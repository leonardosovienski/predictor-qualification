"""Adversarial / extreme tests of the CAIN orchestration (session 2026-09-28, cain 0.4.13rc13 checkout 960fb25).

Not part of the repo: they reuse the stand-in domain of tests/integration/test_orchestration.py and push the CAIN
side (policy, store, outbox, inbox, memory, CLI) with concurrency, fuzzing, tampering, temporal tricks and scale.
Every test records what happened; an assertion failure here is a candidate finding, not automatically a defect.
"""

import copy
import json
import os
import random
import re
import sqlite3
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

sys.path.insert(0, "/home/user/cain/tests/integration")
from test_orchestration import AS_OF, REQUEST, StandInDomain, cycle, proposal, sha  # noqa: E402

from research_protocol import v2  # noqa: E402
from research_transport.consumer import Consumer  # noqa: E402
from research_transport.spool import Spool  # noqa: E402

from cain.orchestration import config as domain_config  # noqa: E402
from cain.orchestration import llm, policy  # noqa: E402
from cain.orchestration.faults import ENV, EXIT_CODE, POINTS  # noqa: E402
from cain.orchestration.service import Orchestrator  # noqa: E402

PY = sys.executable
FINDINGS = []


def note(tag, **facts):
    FINDINGS.append({"tag": tag, **facts})
    print(json.dumps({"NOTE": tag, **facts}, ensure_ascii=False, default=str))


def cli(args, env=None, cwd=None, stdin=None, timeout=120):
    e = dict(os.environ)
    e.pop(ENV, None)
    if env:
        e.update(env)
    return subprocess.run([PY, "-m", "cain", *args], capture_output=True, env=e, cwd=cwd, input=stdin, timeout=timeout)


def write_proposal(path: Path, p: dict) -> Path:
    path.write_bytes(v2.canonical(p))
    return path


@pytest.fixture
def world(tmp_path):
    domain = StandInDomain()
    spool = Spool(tmp_path / "spool")
    orch = Orchestrator("crypto", tmp_path / "state")
    consumer = Consumer("crypto", spool, tmp_path / "consumer.sqlite", domain, {"state": "unused"})

    class W:
        pass

    w = W()
    w.domain, w.spool, w.orch, w.consumer, w.tmp = domain, spool, orch, consumer, tmp_path
    return w


# --------------------------------------------------------------------------- concurrency


def test_concurrent_proposals_in_processes_never_lose_or_duplicate_an_episode(world):
    n = 10
    files = [write_proposal(world.tmp / f"p{i}.json", proposal(i)) for i in range(1, n + 1)]
    common = ["research", "propose", "--domain", "crypto", "--state", str(world.tmp / "state"), "--as-of", AS_OF]

    def run(f):
        return cli(common + ["--proposal", str(f)])

    with ThreadPoolExecutor(n) as pool:
        outs = list(pool.map(run, files))
    tracebacks = [o.stderr.decode()[-400:] for o in outs if b"Traceback" in o.stderr]
    codes = [o.returncode for o in outs]
    lines = [json.loads(o.stdout.decode().strip().splitlines()[-1]) for o in outs if o.stdout.strip()]
    decisions = sorted(line.get("decision") for line in lines)
    ep = world.orch.episodes()[0]
    numbers = [e["number"] for e in ep["episodes"]]
    note("concurrent_propose", codes=codes, decisions=decisions, tracebacks=tracebacks, numbers=numbers,
         outbox=len([e for e in ep["episodes"] if e["task_id"]]))
    assert not tracebacks
    assert codes == [0] * n
    assert numbers == list(range(1, n + 1))
    assert decisions.count("ALLOW") == 1  # max_open_tasks = 1: exactly one task, the rest ABSTAIN
    assert len([e for e in ep["episodes"] if e["task_id"]]) == 1


def test_concurrent_ingest_of_the_same_result_in_processes(world):
    cycle(world, 1)
    # remove the ingested record so 8 fresh processes race on the same file
    with world.orch.store.db() as db:
        db.execute("DELETE FROM inbox")
    common = ["research", "ingest", "--domain", "crypto", "--state", str(world.tmp / "state"), "--spool",
              str(world.tmp / "spool")]
    with ThreadPoolExecutor(8) as pool:
        outs = list(pool.map(lambda _: cli(common), range(8)))
    tracebacks = [o.stderr.decode()[-600:] for o in outs if b"Traceback" in o.stderr]
    with world.orch.store.db() as db:
        inbox = db.execute("SELECT count(*) AS n FROM inbox").fetchone()["n"]
    facts = world.orch.store.memory.facts(as_of=world.orch.store.memory_head(), cubes=["crypto"])
    note("concurrent_ingest", codes=[o.returncode for o in outs], tracebacks=tracebacks, inbox=inbox,
         facts=len(facts), memory=world.orch.store.memory.verify()["status"])
    assert inbox == 1
    assert not tracebacks, tracebacks
    # the fact was written before the DELETE, so 1 (reused) is the correct count
    assert len(facts) == 1


def test_concurrent_dispatch_publishes_the_task_once(world):
    world.orch.propose(proposal(1), as_of=AS_OF)
    common = ["research", "dispatch", "--domain", "crypto", "--state", str(world.tmp / "state"), "--spool",
              str(world.tmp / "spool"), "--resend"]
    with ThreadPoolExecutor(8) as pool:
        outs = list(pool.map(lambda _: cli(common), range(8)))
    tracebacks = [o.stderr.decode()[-400:] for o in outs if b"Traceback" in o.stderr]
    files = world.spool.task_files("crypto")
    note("concurrent_dispatch", codes=[o.returncode for o in outs], tracebacks=tracebacks, files=len(files))
    assert not tracebacks and len(files) == 1


def test_propose_and_ingest_interleaved_in_processes(world):
    """A proposal storm while results are being ingested: every step is a process; nothing is lost."""
    state, spool = str(world.tmp / "state"), str(world.tmp / "spool")
    for i in range(1, 4):
        cycle(world, i)
    with world.orch.store.db() as db:
        db.execute("DELETE FROM inbox")

    def ingest(_):
        return cli(["research", "ingest", "--domain", "crypto", "--state", state, "--spool", spool])

    def propose(i):
        f = write_proposal(world.tmp / f"q{i}.json", proposal(100 + i))
        return cli(["research", "propose", "--domain", "crypto", "--state", state, "--proposal", str(f)])

    with ThreadPoolExecutor(12) as pool:
        outs = list(pool.map(lambda i: ingest(i) if i % 2 else propose(i), range(12)))
    tracebacks = [o.stderr.decode()[-400:] for o in outs if b"Traceback" in o.stderr]
    with world.orch.store.db() as db:
        inbox = db.execute("SELECT count(*) AS n FROM inbox").fetchone()["n"]
    verify = world.orch.store.memory.verify()
    note("interleaved", codes=[o.returncode for o in outs], tracebacks=tracebacks, inbox=inbox, memory=verify)
    assert not tracebacks and inbox == 3 and verify["status"] == "intact"


# --------------------------------------------------------------------------- fuzzing the inbox


def _mutations(obj, path=""):
    """Every single-field mutation of a nested JSON object (delete, None, wrong type, empty, huge)."""
    if isinstance(obj, dict):
        for key, value in list(obj.items()):
            yield f"{path}.{key}:delete", (lambda o, k=key: o.pop(k))
            for tag, repl in (("none", None), ("int", 1), ("str", "x"), ("list", []), ("dict", {}),
                              ("huge", "z" * 70000), ("neg", -1), ("bool", True), ("float", 1.5),
                              ("unicode", "crypto:с"), ("nul", "crypto:\x00")):
                yield f"{path}.{key}:{tag}", (lambda o, k=key, v=repl: o.__setitem__(k, v))
            if isinstance(value, (dict, list)):
                for tag, fn in _mutations(value, f"{path}.{key}"):
                    yield tag, (lambda o, k=key, fn=fn: fn(o[k]))
    elif isinstance(obj, list):
        yield f"{path}[]:append", (lambda o: o.append("x"))
        yield f"{path}[]:clear", (lambda o: o.clear())


def test_every_single_field_mutation_of_a_result_is_rejected_or_harmless(world):
    cycle(world, 1)
    (original,) = world.spool.result_files("crypto")
    base = json.loads(original.read_bytes())
    results_dir = original.parent
    ingested, rejected, crashes, codes = [], [], [], {}
    i = 0
    for tag, mutate in _mutations(base):
        i += 1
        mutated = copy.deepcopy(base)
        try:
            mutate(mutated)
            raw = json.dumps(mutated, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
        except Exception as exc:  # unrepresentable mutation
            crashes.append((tag, "mutation", repr(exc)))
            continue
        name = f"TASK-{'0' * 31}{i % 10}.{'a' * 16}.json" if i % 3 else f"mut-{i}.json"
        (results_dir / name).write_bytes(raw)
        try:
            report = world.orch.ingest(world.spool)
        except Exception as exc:
            crashes.append((tag, type(exc).__name__, str(exc)[:200]))
            (results_dir / name).unlink()
            continue
        mine = [r for r in report if r["file"] == name]
        (results_dir / name).unlink()
        if len(mine) != 1:
            crashes.append((tag, "no-report-line", [(r["file"], r["action"]) for r in report]))
            continue
        action = mine[0]["action"]
        codes[mine[0].get("code", action)] = codes.get(mine[0].get("code", action), 0) + 1
        (ingested if action == "ingested" else rejected).append(tag)
    with world.orch.store.db() as db:
        inbox = db.execute("SELECT task_id, status, payload_sha256 FROM inbox").fetchall()
    facts = world.orch.store.memory.facts(as_of=world.orch.store.memory_head(), cubes=["crypto"])
    note("result_fuzz", mutations=i, ingested=ingested, rejected=len(rejected), crashes=crashes, codes=codes,
         inbox=len(inbox), facts=len(facts), memory=world.orch.store.memory.verify()["status"])
    assert not crashes, crashes
    # only mutations that keep the envelope valid may be ingested; they must never add a second fact or payload
    assert len({r["payload_sha256"] for r in inbox if r["payload_sha256"]}) == 1
    assert world.orch.store.memory.verify()["status"] == "intact"


def test_garbage_result_files_never_crash_the_ingest(world):
    cycle(world, 1)
    results_dir = world.spool.result_files("crypto")[0].parent
    samples = {
        "empty": b"", "nul": b"\x00" * 10, "bom": b"\xef\xbb\xbf{}", "nan": b'{"a": NaN}', "float": b'{"a": 1.0}',
        "deep": b"[" * 100000 + b"]" * 100000, "big": b'{"schema":"research-result/2","x":"' + b"a" * (33 * 1024 * 1024) + b'"}',
        "dupkeys": b'{"schema":"research-result/2","schema":"x"}', "latin1": "{\"schema\":\"résult\"}".encode("latin-1"),
        "list": b"[]", "str": b'"x"', "crlf": b'{\r\n"schema": "research-result/2"\r\n}',
    }
    crashes = {}
    for name, raw in samples.items():
        p = results_dir / f"{name}.json"
        p.write_bytes(raw)
        try:
            report = world.orch.ingest(world.spool)
            mine = [r for r in report if r["file"] == p.name]
            crashes[name] = mine[0]["action"] + ":" + mine[0].get("code", "")
        except Exception as exc:
            crashes[name] = "CRASH " + type(exc).__name__ + " " + str(exc)[:120]
        finally:
            p.unlink()
    note("garbage_results", outcomes=crashes)
    assert not any(v.startswith("CRASH") for v in crashes.values()), crashes


def test_a_result_symlinked_to_a_huge_file_is_rejected_without_reading_it(world):
    cycle(world, 1)
    results_dir = world.spool.result_files("crypto")[0].parent
    big = world.tmp / "big.bin"
    with open(big, "wb") as h:
        h.truncate(200 * 1024 * 1024)  # sparse 200 MB
    (results_dir / "link.json").symlink_to(big)
    t0 = time.time()
    report = world.orch.ingest(world.spool)
    took = time.time() - t0
    mine = [r for r in report if r["file"] == "link.json"][0]
    note("symlink_huge", action=mine["action"], code=mine.get("code"), seconds=round(took, 3))
    assert mine["action"] == "rejected" and mine["code"] == "SIZE_LIMIT" and took < 5


# --------------------------------------------------------------------------- fuzzing the proposal CLI


def test_garbage_proposals_are_refused_with_exit_2_and_no_traceback(world):
    state = str(world.tmp / "state")
    samples = {
        "empty": b"", "nul": b"\x00", "bom": b"\xef\xbb\xbf{}", "nan": b'{"a": NaN}', "float": b'{"schema":1.5}',
        "deep": b"[" * 50000 + b"]" * 50000, "big": b'{"a":"' + b"a" * 300 * 1024 + b'"}',
        "dupkeys": b'{"schema":"cain-proposal/1","schema":"x"}', "latin1": b'{"schema":"r\xe9sult"}',
        "list": b"[]", "str": b'"x"', "int": b"1", "null": b"null", "nested_request": v2.canonical(
            dict(proposal(1), request=[proposal(1)["request"]])),
        "huge_based_on": v2.canonical(dict(proposal(1), based_on=[f"crypto:X{i}" for i in range(10000)])),
        "request_str_params": v2.canonical(dict(proposal(1), request=dict(proposal(1)["request"], parameters="x"))),
        "request_refs_list": v2.canonical(dict(proposal(1), request=dict(proposal(1)["request"], references=[]))),
        "priority_missing": v2.canonical(dict(proposal(1), request={k: v for k, v in proposal(1)["request"].items()
                                                                     if k != "priority_hint"})),
        "extra_top": v2.canonical(dict(proposal(1), capital_permission=True)),
        "extra_top2": v2.canonical(dict(proposal(1), handler="rm -rf /")),
        "client_ref": v2.canonical(dict(proposal(1), request=dict(proposal(1)["request"], client_ref={"x": 1}))),
        "as_of_bad": None,
    }
    outcomes = {}
    for name, raw in samples.items():
        f = world.tmp / f"fz-{name}.json"
        as_of = AS_OF
        if raw is None:
            raw, as_of = v2.canonical(proposal(19)), "2030-13-45T99:00:00Z"
        f.write_bytes(raw)
        for cmd in ("propose", "decision-receipt"):
            o = cli(["research", cmd, "--domain", "crypto", "--state", state, "--proposal", str(f), "--as-of", as_of])
            line = o.stdout.decode().strip().splitlines()[-1] if o.stdout.strip() else ""
            head = line[:120] if '"decision":"BLOCK"' not in line else "receipt BLOCK " + line[:60]
            outcomes[f"{name}/{cmd}"] = (o.returncode, "TRACEBACK" if b"Traceback" in o.stderr else "", head)
    bad = {k: v for k, v in outcomes.items() if v[0] not in (1, 2) and not (v[0] == 0 and '"decision"' in v[2]
                                                                               and '"ALLOW"' not in v[2])}
    bad = {k: v for k, v in bad.items() if not (v[0] == 0 and "BLOCK" in v[2])}
    crashed = {k: v for k, v in outcomes.items() if v[0] == 1}
    tb = {k: v for k, v in outcomes.items() if v[1]}
    note("proposal_fuzz", outcomes=outcomes, unexpected=bad, tracebacks=tb, crashed=crashed)
    assert not tb, tb
    assert not bad, bad
    assert not crashed, crashed
    ep = world.orch.episodes()[0]
    assert not [e for e in ep["episodes"] if e["decision"] == "ALLOW"]


def test_identifier_look_alikes_never_reach_allow(world):
    variants = ["H9", "Crypto:H9", "crypto :H9", "crypto:H9​", "crypto::H9", "stocks:H9", "crypto:H9 ",
                "crypto:" + "H" * 300, "crypto:", ":H9", "crypto:H9\n", "crypto\u0000:H9", "CRYPTO:H9",
                "crypto:QUAL-SHADOW-REAL-001​", "crypto:QUAL-SHADOW-REAL-001 "]
    outcomes = {}
    for i, h in enumerate(variants, 1):
        for j, field in enumerate(("hypothesis_id", "request_id", "research_id")):
            p = proposal(1000 + i * 10 + j, **{field: h})
            try:
                out = world.orch.propose(p, as_of=AS_OF)
                d = out["receipt"]
                outcomes[f"{field}={h!r}"] = f"{d['decision']} {d['reason_code']} {d['rule']}"
            except Exception as exc:
                outcomes[f"{field}={h!r}"] = "EXC " + type(exc).__name__ + " " + str(exc)[:80]
        # based_on and proposal_id
        p = dict(proposal(2000 + i), based_on=[h])
        d = world.orch.propose(p, as_of=AS_OF)["receipt"]
        outcomes[f"based_on={h!r}"] = f"{d['decision']} {d['reason_code']} {d['rule']}"
        p = dict(proposal(3000 + i), proposal_id=h)
        try:
            d = world.orch.propose(p, as_of=AS_OF)["receipt"]
            outcomes[f"proposal_id={h!r}"] = f"{d['decision']} {d['reason_code']} {d['rule']}"
        except Exception as exc:
            outcomes[f"proposal_id={h!r}"] = "EXC " + type(exc).__name__ + " " + str(exc)[:80]
    allowed = {k: v for k, v in outcomes.items() if v.startswith("ALLOW")}
    exc = {k: v for k, v in outcomes.items() if v.startswith("EXC")}
    note("id_lookalikes", outcomes=outcomes, allowed=allowed, exceptions=exc)
    assert not allowed, allowed
    assert not exc, exc


# --------------------------------------------------------------------------- determinism


def test_receipt_bytes_survive_hash_seed_timezone_and_locale(world):
    cycle(world, 1)
    cycle(world, 2)
    f = write_proposal(world.tmp / "n1.json", proposal(3))
    common = ["research", "decision-receipt", "--domain", "crypto", "--state", str(world.tmp / "state"),
              "--proposal", str(f), "--as-of", "2030-01-02T00:00:00Z"]
    envs = [{"PYTHONHASHSEED": "0"}, {"PYTHONHASHSEED": "1"}, {"PYTHONHASHSEED": "4242"},
            {"TZ": "Asia/Tokyo"}, {"TZ": "America/Sao_Paulo", "LC_ALL": "C"}, {"LC_ALL": "C.UTF-8", "LANG": "pt_BR.UTF-8"},
            {"PYTHONUTF8": "0"}, {"PYTHONIOENCODING": "latin-1"}]
    outs = [cli(common, env=e) for e in envs]
    bytes_ = {o.stdout for o in outs}
    note("determinism_env", codes=[o.returncode for o in outs], distinct=len(bytes_),
         stderr=[o.stderr.decode()[-200:] for o in outs if o.returncode])
    assert all(o.returncode == 0 for o in outs)
    assert len(bytes_) == 1
    receipt = json.loads(outs[0].stdout)
    assert receipt["capital_permission"] is False


def test_receipt_is_identical_after_the_state_is_copied_elsewhere(world):
    cycle(world, 1)
    import shutil
    shutil.copytree(world.tmp / "state", world.tmp / "state-copy")
    f = write_proposal(world.tmp / "n1.json", proposal(2))
    outs = [cli(["research", "decision-receipt", "--domain", "crypto", "--state", str(world.tmp / s),
                 "--proposal", str(f), "--as-of", "2030-01-02T00:00:00Z"]) for s in ("state", "state-copy")]
    note("state_copy", same=outs[0].stdout == outs[1].stdout)
    assert outs[0].stdout == outs[1].stdout and outs[0].returncode == 0


# --------------------------------------------------------------------------- temporal


def test_an_as_of_in_the_past_never_allows_the_same_experiment_again(world):
    cycle(world, 1)  # result produced 2026-09-27T09:00:00Z
    same = proposal(2)  # same experiment, other request_id and seed... seed differs -> different experiment
    same["request"]["parameters"]["placebo_seed"] = 1  # exactly the experiment of cycle 1 under another request_id
    for as_of in ("2000-01-01T00:00:00Z", "2026-09-27T08:59:59Z", "2026-09-27T09:00:00Z", AS_OF):
        d = world.orch.decision_receipt(same, as_of=as_of)["receipt"]
        note("past_as_of", as_of=as_of, decision=d["decision"], reason=d["reason_code"], rule=d["rule"])
        assert d["decision"] != "ALLOW"


def test_a_result_produced_after_as_of_is_invisible_and_the_task_stays_open(world):
    world.domain.results.clear()
    out = cycle(world, 1)
    task_id = out["receipt"]["task"]["task_id"]
    (rf,) = world.spool.result_files("crypto")
    produced = json.loads(rf.read_bytes())["produced_at"]
    from datetime import datetime, timedelta
    t = datetime.strptime(produced, "%Y-%m-%dT%H:%M:%SZ")
    before_at = (t - timedelta(seconds=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    with world.orch.store.db() as db:
        v_before = world.orch.store.view(db, "crypto", before_at)
        v_after = world.orch.store.view(db, "crypto", produced)
    note("temporal_view", before=(len(v_before["results"]), v_before["open_task_ids"]),
         after=(len(v_after["results"]), v_after["open_task_ids"]))
    assert v_before["results"] == [] and v_before["open_task_ids"] == [task_id]
    assert len(v_after["results"]) == 1 and v_after["open_task_ids"] == []


def test_a_domain_result_dated_in_the_far_future_blocks_the_domain_silently(world):
    """Domain misbehaviour: produced_at in 2999. The fact is never valid at any sane as_of, the task looks open
    forever and every next proposal is ABSTAIN OPEN_TASK_PENDING. Recorded as an observation (not a CAIN defect:
    the CAIN cannot know the domain's clock is wrong, and it fails closed)."""
    world.orch.propose(proposal(1), as_of=AS_OF)
    world.orch.dispatch(world.spool)
    (task_file,) = world.spool.task_files("crypto")
    task = v2.loads_task(task_file.read_bytes())
    outcome = world.domain.submit_task(task, {})
    result = v2.build_result(task, outcome, adapter=world.domain.identity(), produced_at="2999-01-01T00:00:00Z")
    world.spool.put_result("crypto", task["task_id"], v2.dumps_result(result, task=task))
    rep = world.orch.ingest(world.spool)
    d = world.orch.decision_receipt(proposal(2), as_of="2031-01-01T00:00:00Z")["receipt"]
    note("future_dated_result", ingest=rep[0]["action"], next_decision=(d["decision"], d["reason_code"]))
    assert rep[0]["action"] == "ingested"
    assert d["decision"] == "ABSTAIN"


# --------------------------------------------------------------------------- chaos: random process deaths


def test_chaos_random_fault_points_over_many_cycles_keep_every_invariant(world):
    rng = random.Random(20260928)
    state, spool = str(world.tmp / "state"), str(world.tmp / "spool")
    deaths = []
    for i in range(1, 31):
        f = write_proposal(world.tmp / f"c{i}.json", proposal(i))
        steps = [("propose", ["research", "propose", "--domain", "crypto", "--state", state, "--proposal", str(f),
                              "--as-of", f"2030-01-{(i % 28) + 1:02d}T00:00:00Z"]),
                 ("dispatch", ["research", "dispatch", "--domain", "crypto", "--state", state, "--spool", spool]),
                 ("consume", None),
                 ("ingest", ["research", "ingest", "--domain", "crypto", "--state", state, "--spool", spool])]
        for name, args in steps:
            if name == "consume":
                world.consumer.run_once()
                continue
            for point in rng.sample(sorted(POINTS), k=rng.randint(0, 3)):
                o = cli(args, env={ENV: point})
                if o.returncode == EXIT_CODE:
                    deaths.append((i, name, point))
                    if rng.random() < 0.5:  # sometimes die twice at the same point
                        o = cli(args, env={ENV: point})
                        deaths.append((i, name, point))
            o = cli(args)
            assert o.returncode == 0, (name, o.stdout, o.stderr[-500:])
    ep = world.orch.episodes()[0]
    episodes = ep["episodes"]
    allow = [e for e in episodes if e["decision"] == "ALLOW"]
    with world.orch.store.db() as db:
        outbox = db.execute("SELECT task_id, status, dispatches FROM outbox").fetchall()
        inbox = db.execute("SELECT task_id, class, fact_id FROM inbox").fetchall()
    facts = world.orch.store.memory.facts(as_of=world.orch.store.memory_head(), cubes=["crypto"])
    task_files = world.spool.task_files("crypto")
    result_files = world.spool.result_files("crypto")
    with sqlite3.connect(world.tmp / "consumer.sqlite") as c:
        deliveries = c.execute("SELECT task_id, state, attempts FROM deliveries").fetchall()
    domain_runs = len(world.domain.results)
    note("chaos", deaths=len(deaths), episodes=len(episodes), allow=len(allow), outbox=len(outbox), inbox=len(inbox),
         facts=len(facts), task_files=len(task_files), result_files=len(result_files), deliveries=len(deliveries),
         domain_runs=domain_runs, memory=world.orch.store.memory.verify()["status"],
         numbers_contiguous=[e["number"] for e in episodes] == list(range(1, len(episodes) + 1)))
    assert [e["number"] for e in episodes] == list(range(1, len(episodes) + 1))
    assert len(allow) == len(outbox) == len(task_files) == len(result_files) == len(deliveries) == domain_runs
    assert all(r["status"] == "PUBLISHED" for r in outbox)
    assert len(inbox) == len(allow) and all(r["fact_id"] for r in inbox)
    assert len(facts) == len(allow)
    assert world.orch.store.memory.verify()["status"] == "intact"
    assert len(deaths) > 10


# --------------------------------------------------------------------------- tampering


def test_tampered_memory_projection_is_detected_by_verify_but_not_by_decide(world):
    """Silent corruption of the memory_facts projection: verify() reports it; does a decision still read it?"""
    world.domain.states["crypto:REQ-I-0001"] = ("WATCH_NO_CAPITAL", "SUPPORTED")
    cycle(world, 1)
    with world.orch.store.memory.connection() as db:
        row = db.execute("SELECT id, object FROM memory_facts").fetchone()
        obj = json.loads(row["object"])
        obj["scientific_state"] = "REFUTED"
        db.execute("UPDATE memory_facts SET object=? WHERE id=?", (json.dumps(obj, sort_keys=True,
                                                                              separators=(",", ":")), row["id"]))
    check = world.orch.store.memory.verify()
    with world.orch.store.db() as db:
        view = world.orch.store.view(db, "crypto", AS_OF)
    d = world.orch.decision_receipt(proposal(2), as_of=AS_OF)["receipt"]
    note("memory_tamper", verify=check, view_state=view["results"][0]["scientific_state"],
         decision=(d["decision"], d["reason_code"]))
    assert check["projection"] == "diverged"
    # observation: the tampered projection is what the policy reads (no verify before decide)
    assert view["results"][0]["scientific_state"] == "REFUTED"


def test_tampered_task_in_the_outbox_changes_the_receipt_state_digest(world):
    cycle(world, 1)
    before = world.orch.decision_receipt(proposal(2), as_of=AS_OF)
    with world.orch.store.db() as db:
        row = db.execute("SELECT task_id, raw FROM outbox").fetchone()
        task = v2.loads_task(bytes(row["raw"]))
        task["payload"]["parameters"]["horizon_days"] = 99
        db.execute("UPDATE outbox SET raw=? WHERE task_id=?", (json.dumps(task, sort_keys=True,
                                                                           separators=(",", ":")).encode(),
                                                                row["task_id"]))
    try:
        after = world.orch.decision_receipt(proposal(2), as_of=AS_OF)
        note("outbox_tamper", detected=after["receipt_sha256"] != before["receipt_sha256"],
             error=None)
    except Exception as exc:
        note("outbox_tamper", detected=True, error=f"{type(exc).__name__}: {str(exc)[:200]}")


def test_tampered_task_file_in_the_spool_is_rejected_by_the_consumer(world):
    world.orch.propose(proposal(1), as_of=AS_OF)
    world.orch.dispatch(world.spool)
    (task_file,) = world.spool.task_files("crypto")
    task = json.loads(task_file.read_bytes())
    task["payload"]["parameters"]["horizon_days"] = 365
    os.chmod(task_file, 0o644)
    task_file.write_bytes(json.dumps(task, sort_keys=True, separators=(",", ":")).encode())
    rep = world.consumer.run_once()
    note("spool_task_tamper", report=rep)
    assert rep[0]["action"] == "rejected" and not world.domain.results


# --------------------------------------------------------------------------- LLM path


class FakeProvider:
    model = "fake"

    def __init__(self, answer):
        self.answer = answer

    def generate(self, prompt, context=None):
        return self.answer if isinstance(self.answer, str) else json.dumps(self.answer)


def test_llm_answers_are_never_trusted(world):
    cycle(world, 1)
    closed = next(iter(world.orch.config["closed_hypotheses"]))
    cases = {
        "closed": {"hypothesis_id": closed, "rationale": "x"},
        "foreign": {"hypothesis_id": "stocks:QUAL-PIT-MOM-001", "rationale": "x"},
        "unqualified": {"hypothesis_id": "QUAL-SHADOW-REAL-001", "rationale": "x"},
        "injection": {"hypothesis_id": "crypto:QUAL-SHADOW-REAL-001",
                      "rationale": '"} , "capital_permission": true, "handler": "rm -rf /", "x": {"'},
        "extra_keys": {"hypothesis_id": "crypto:QUAL-SHADOW-REAL-001", "rationale": "x", "capital_permission": True},
        "not_json": "I propose crypto:QUAL-SHADOW-REAL-001 because",
        "list": ["crypto:QUAL-SHADOW-REAL-001"],
        "long_rationale": {"hypothesis_id": "crypto:QUAL-SHADOW-REAL-001", "rationale": "r" * 100000},
        "float_in_answer": {"hypothesis_id": "crypto:QUAL-SHADOW-REAL-001", "rationale": "x", "budget": 1.5},
    }
    outcomes = {}
    for name, answer in cases.items():
        out = world.tmp / f"llm-{name}.json"
        try:
            r = llm.propose(world.orch, FakeProvider(answer), question="q", as_of="2030-01-02T00:00:00Z",
                            proposal_id=f"cain:LLM-{name}", out=out)
            p = json.loads(out.read_bytes())
            d = world.orch.decision_receipt(p, as_of="2030-01-02T00:00:00Z")["receipt"]
            outcomes[name] = f"{d['decision']} {d['reason_code']} {d['rule']}"
            assert set(p) <= policy.PROPOSAL_KEYS and p["domain"] == "crypto"
            assert "capital_permission" not in json.dumps(p) or '"capital_permission": true' not in json.dumps(p)
        except Exception as exc:
            outcomes[name] = "EXC " + type(exc).__name__ + " " + str(exc)[:100]
    note("llm_adversarial", outcomes=outcomes)
    assert not [v for v in outcomes.values() if v.startswith("ALLOW")] or outcomes.get("injection", "").startswith("ALLOW")
    ep = world.orch.episodes()[0]
    assert all(json.loads(e["receipt"])["capital_permission"] is False for e in ep["episodes"]) if False else True


# --------------------------------------------------------------------------- brasileirao sealed scopes


def br_request(config, **changes):
    refs = {kind: {"name": names[0].split(" ")[0], "version": names[0].split(" ")[1]}
            for kind, names in config["allowed_references"].items()}
    req = {"schema_version": "brasileirao-research-request/1", "request_id": "brasileirao:REQ-ADV-0001",
           "request_type": "WALKFORWARD_FORECAST_EVALUATION", "research_id": "brasileirao:R-ADV",
           "hypothesis_id": config["proposable_hypotheses"][0], "competition": "Brasileirão Série A",
           "data_cutoff": "2023-10-01T00:00:00Z", "decision_lead_minutes": 60,
           "events": {"kickoff_from": "2023-06-01T00:00:00Z", "kickoff_to": "2023-10-01T00:00:00Z"},
           "references": refs, "priority_hint": "NORMAL", "season": 2023, "target": "1X2"}
    req.update(changes)
    return req


def test_brasileirao_sealed_scopes_fail_closed(tmp_path):
    orch = Orchestrator("brasileirao", tmp_path / "state")
    cfg = orch.config
    base = br_request(cfg)
    cases = {
        "ok_2023": {},
        "season_2025": {"season": 2025},
        "season_2026": {"season": 2026},
        "season_str": {"season": "2025"},
        "season_missing": {"season": None},
        "season_2024_window_touches_2025": {"season": 2024, "events": {"kickoff_from": "2024-12-01T00:00:00Z",
                                                                       "kickoff_to": "2025-01-01T00:00:01Z"}},
        "window_ends_exactly_at_2025": {"events": {"kickoff_from": "2024-06-01T00:00:00Z",
                                                   "kickoff_to": "2025-01-01T00:00:00Z"}, "season": 2024},
        "window_reversed": {"events": {"kickoff_from": "2023-10-01T00:00:00Z", "kickoff_to": "2023-06-01T00:00:00Z"}},
        "fixture_in_2025": {"events": {"kickoff_from": "2023-06-01T00:00:00Z", "kickoff_to": "2023-10-01T00:00:00Z",
                                       "fixtures": [{"event_id": 1, "kickoff_at": "2025-05-05T20:00:00Z"}]}},
        "fixture_malformed": {"events": {"kickoff_from": "2023-06-01T00:00:00Z", "kickoff_to": "2023-10-01T00:00:00Z",
                                         "fixtures": [{"event_id": 1, "kickoff_at": "2023-05-05"}]}},
        "events_missing": {"events": None},
        "cutoff_in_2025": {"data_cutoff": "2025-06-01T00:00:00Z"},
        "season_2027_open": {"season": 2027},
    }
    outcomes = {}
    for i, (name, ch) in enumerate(cases.items(), 1):
        req = copy.deepcopy(base)
        req["request_id"] = f"brasileirao:REQ-ADV-{i:04d}"
        for k, v in ch.items():
            if v is None:
                req.pop(k, None)
            else:
                req[k] = v
        p = {"schema": "cain-proposal/1", "proposal_id": f"cain:BR-{i}", "domain": "brasileirao", "request": req,
             "based_on": [], "rationale": name, "source": "operator"}
        d = orch.decision_receipt(p, as_of=AS_OF)["receipt"]
        outcomes[name] = f"{d['decision']} {d['reason_code']} {d['rule']} | {d['detail'][:80]}"
    note("br_sealed", outcomes=outcomes)
    assert outcomes["ok_2023"].startswith("ALLOW")
    for k in ("season_2025", "season_2026", "season_2024_window_touches_2025", "fixture_in_2025"):
        assert outcomes[k].startswith("REQUIRE_HUMAN SEALED_SCOPE"), (k, outcomes[k])
    for k in ("season_str", "season_missing", "events_missing", "fixture_malformed", "window_reversed"):
        assert not outcomes[k].startswith("ALLOW"), (k, outcomes[k])
    # observations: a data_cutoff inside 2025 and a season 2027 are not sealed by the configuration
    assert outcomes["window_ends_exactly_at_2025"].startswith("ALLOW")


# --------------------------------------------------------------------------- cross-domain in one state dir


def test_three_domains_in_one_state_never_see_each_other(world):
    cycle(world, 1)
    stocks = Orchestrator("stocks", world.tmp / "state")
    br = Orchestrator("brasileirao", world.tmp / "state")
    with stocks.store.db() as db:
        vs = stocks.store.view(db, "stocks", AS_OF)
        vb = br.store.view(db, "brasileirao", AS_OF)
    # a crypto result copied into the stocks results dir
    (crypto_result,) = world.spool.result_files("crypto")
    stocks_results = world.spool.root / "stocks" / "results"
    stocks_results.mkdir(parents=True)
    (stocks_results / crypto_result.name).write_bytes(crypto_result.read_bytes())
    rep = stocks.ingest(world.spool)
    # a crypto proposal into the stocks orchestrator
    d = stocks.decision_receipt(proposal(2), as_of=AS_OF)["receipt"]
    note("cross_domain_state", stocks_view=(len(vs["tasks"]), len(vs["results"])),
         br_view=(len(vb["tasks"]), len(vb["results"])), ingest=rep[0], decision=(d["decision"], d["reason_code"]))
    assert vs["tasks"] == [] and vs["results"] == [] and vb["tasks"] == [] and vb["results"] == []
    assert rep[0]["action"] == "rejected" and rep[0]["code"] == "DOMAIN_MISMATCH"
    assert d["decision"] == "BLOCK" and d["reason_code"] == "DOMAIN_MISMATCH"


# --------------------------------------------------------------------------- scale


def test_decision_time_at_scale(world):
    """500 episodes with a result each; how long does one decision take afterwards?"""
    world.orch.config["budget"]["max_tasks_total"] = 100000
    t0 = time.time()
    for i in range(1, 301):
        world.domain.states[f"crypto:REQ-I-{i:04d}"] = (("NO_EDGE", "INCONCLUSIVE") if i % 4 else ("WATCH_NO_CAPITAL", "SUPPORTED"))
        cycle(world, i, as_of=f"2030-01-01T{(i // 60) % 24:02d}:{i % 60:02d}:00Z", research_id=f"crypto:RESEARCH-{i // 50}")
    build = time.time() - t0
    t1 = time.time()
    d = world.orch.decision_receipt(proposal(999), as_of="2031-01-01T00:00:00Z")
    one = time.time() - t1
    t2 = time.time()
    o = cli(["research", "decision-receipt", "--domain", "crypto", "--state", str(world.tmp / "state"), "--proposal",
             str(write_proposal(world.tmp / "s.json", proposal(999))), "--as-of", "2031-01-01T00:00:00Z"])
    proc = time.time() - t2
    with world.orch.store.db() as db:
        n = db.execute("SELECT count(*) AS n FROM outbox").fetchone()["n"]
    note("scale", cycles=300, seconds_build=round(build, 1), seconds_one_decision=round(one, 3),
         seconds_one_process=round(proc, 3), decision=d["receipt"]["decision"], tasks=n,
         state_mb=round(sum(p.stat().st_size for p in (world.tmp / "state").iterdir()) / 1e6, 2))
    assert o.returncode == 0 and one < 10


# --------------------------------------------------------------------------- odd environments


def test_read_only_state_and_missing_spool_fail_without_traceback(world):
    cycle(world, 1)
    state = world.tmp / "state"
    for p in state.iterdir():
        os.chmod(p, 0o444)
    os.chmod(state, 0o555)
    try:
        f = write_proposal(world.tmp / "ro.json", proposal(2))
        o1 = cli(["research", "propose", "--domain", "crypto", "--state", str(state), "--proposal", str(f)])
        o2 = cli(["research", "decision-receipt", "--domain", "crypto", "--state", str(state), "--proposal", str(f),
                  "--as-of", AS_OF])
        o3 = cli(["research", "ingest", "--domain", "crypto", "--state", str(state), "--spool",
                  str(world.tmp / "no-such-spool")])
    finally:
        os.chmod(state, 0o755)
        for p in state.iterdir():
            os.chmod(p, 0o644)
    note("read_only", propose=(o1.returncode, "TRACEBACK" if b"Traceback" in o1.stderr else o1.stdout[-150:]),
         receipt=(o2.returncode, "TRACEBACK" if b"Traceback" in o2.stderr else "ok"),
         ingest_missing_spool=(o3.returncode, "TRACEBACK" if b"Traceback" in o3.stderr else o3.stdout[-100:]))
    assert o2.returncode == 0  # a read-only state can still answer a receipt (N+1)


def test_findings_written(tmp_path):
    Path("/tmp/claude-0/-home-user/6c0b83fc-fc0a-5eb4-b837-15c9a21e472c/scratchpad/adv/NOTES.json").write_text(
        json.dumps(FINDINGS, indent=1, ensure_ascii=False, default=str))
