"""integration-crypto, fase soak (SOAK; QUALIFICATION_PROFILE_INTEGRATION_CRYPTO_V1.json, lido e nunca alterado).

Ciclos do domínio crypto pelo runtime suportado, com dados reais, no mesmo estado, intercalados com duplicatas,
reinícios do CAIN e do consumidor, fixtures V2 dos outros domínios e falhas de 4 classes; depois as propostas de LLM
(`cain research explain` no modo de proposta; auditadas; não são gate) quando o modelo local existe. Todos os números
do relatório saem do log bruto (commands.log) e do SUMMARY.json deste script.

Uso (com o env.sh do runtime_env.sh): python soak.py <qualification/integration-crypto> <work> <out>
"""

from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

from harness import Harness, now

NEGATIVE_STATES = {"NO_EDGE", "INCONCLUSIVE", "REFUTED", "CLOSED_INSUFFICIENT_SAMPLE", "INCONCLUSIVE_DATA_QUALITY"}


def main() -> int:
    mission, work, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    profile = json.loads((mission / "QUALIFICATION_PROFILE_INTEGRATION_CRYPTO_V1.json").read_text(encoding="utf-8"))
    gen = json.loads((mission / "FROZEN_VECTORS.json").read_text(encoding="utf-8"))["soak_generator"]
    h = Harness(out, work, mission, "soak")
    props = work / "proposals"
    props.mkdir(parents=True, exist_ok=True)
    base = json.loads((mission / "fixtures/proposals/e2e/01-allow.json").read_text(encoding="utf-8"))
    counters = {"cycles": 0, "duplicates": 0, "domain_restarts": 0, "cain_restarts": 0,
                "interleaved_cycles_other_domain": 0, "failure_runs": {}, "decisions": {}, "llm_proposals": 0}
    minimums = profile["minimums"]

    def proposal(n: int, hypothesis: str) -> Path:
        value = json.loads(json.dumps(base))
        value["proposal_id"] = f"cain:SOAK-{n:03d}"
        value["request"].update(request_id=f"crypto:REQ-IC-SOAK-{n:03d}", hypothesis_id=hypothesis)
        value["request"]["parameters"]["placebo_seed"] = 1000 + n
        path = props / f"{n:03d}.json"
        path.write_text(json.dumps(value), encoding="utf-8")
        return path

    def decide(label: str, path: Path, **kw) -> dict:
        code, lines, _ = h.propose(label, path, **kw)
        line = lines[0] if lines else {}
        counters["decisions"][line.get("decision")] = counters["decisions"].get(line.get("decision"), 0) + 1
        return line

    def fail_class(name: str) -> None:
        counters["failure_runs"][name] = counters["failure_runs"].get(name, 0) + 1

    hyps = gen["hypotheses"]
    n = 0
    cain_faults = ["after_outbox_commit", "after_spool_write_before_ack", "after_inbox_commit_before_memory",
                   "after_memory_commit", "after_decision_before_episode_commit"]
    while counters["cycles"] < gen["cycles"]:
        n += 1
        path = proposal(n, hyps[(n - 1) % len(hyps)])
        k = counters["cycles"]
        as_of = now()
        # CAIN process death at one of the named points, in rotation (restarts of the CAIN)
        fault = cain_faults[k % len(cain_faults)] if k < 2 * len(cain_faults) else None
        if fault == "after_decision_before_episode_commit":
            code, _, _ = h.propose(f"propose {n} (fault)", path, as_of=as_of, fault=fault)
            counters["cain_restarts"] += code == 86
            fail_class("cain_process_death")
        line = decide(f"propose {n}", path, as_of=as_of) if fault != "after_outbox_commit" else {}
        if fault == "after_outbox_commit":
            code, lines, _ = h.propose(f"propose {n} (fault)", path, as_of=as_of, fault=fault)
            counters["cain_restarts"] += code == 86
            fail_class("cain_process_death")
            line = decide(f"propose {n} (after restart)", path, as_of=as_of)
        if line.get("decision") != "ALLOW":
            continue  # COOLDOWN/ABSTAIN episodes are recorded; the cycle count only counts full roundtrips
        if fault == "after_spool_write_before_ack":
            code, _, _ = h.dispatch(f"dispatch {n} (fault)", fault=fault)
            counters["cain_restarts"] += code == 86
            fail_class("cain_process_death")
        h.dispatch(f"dispatch {n}")
        if k % 4 == 1:  # consumer dies after the domain, before the V2 result (domain restart)
            code, _, _ = h.consumer(f"consumer {n} (fault)", fault="after_domain_before_result_write")
            counters["domain_restarts"] += code == 86
            fail_class("consumer_process_death")
        if k % 6 == 3:  # domain retryable failure, then the CAIN asks for a resend
            _c, lines, _ = h.consumer(f"consumer {n} (Ops crash)", domain_fault="ops_worker_crash")
            fail_class("domain_retryable")
            h.ingest(f"ingest {n} retryable")
            h.cain(f"retry {n}", "retry", "--domain", "crypto", "--state", h.state, "--spool", h.spool,
                   "--task-id", line["task"]["task_id"])
        h.consumer(f"consumer {n}")
        if fault in ("after_inbox_commit_before_memory", "after_memory_commit"):
            code, _, _ = h.ingest(f"ingest {n} (fault)", fault=fault)
            counters["cain_restarts"] += code == 86
            fail_class("cain_process_death")
        h.ingest(f"ingest {n}")
        counters["cycles"] += 1
        # duplicates: re-delivery of the task and of the result, and a re-proposal of the same content
        if k % 4 == 0:
            h.dispatch(f"resend {n}", resend=True)
            h.consumer(f"consumer resend {n}")
            results = [p for p, r in h.results() if r["task_id"] == line["task"]["task_id"]]
            shutil.copy(results[0], results[0].with_name(f"redelivered-{n:03d}-" + results[0].name))
            h.ingest(f"ingest redelivered {n}")
            dup = json.loads(path.read_text(encoding="utf-8"))
            dup["proposal_id"] = f"cain:SOAK-{n:03d}-again"
            dup_path = props / f"{n:03d}-again.json"
            dup_path.write_text(json.dumps(dup), encoding="utf-8")
            again = decide(f"propose duplicate {n}", dup_path)
            counters["duplicates"] += 3 if again.get("decision") == "DUPLICATE" else 2
            fail_class("delivery_anomaly")
        # interleaved cycles with the other two domains (frozen V2 fixtures): must be refused without effect
        if k % 4 == 2:
            other = ("stocks", "brasileirao")[(k // 4) % 2]
            target = h.spool / "crypto" / "results" / f"interleaved-{n:03d}-{other}.json"
            shutil.copy(mission / f"fixtures/v2/{other}/result-h9.json", target)
            _c, lines, _ = h.ingest(f"ingest interleaved {other} {n}")
            rejected = [l for l in lines if l.get("file") == target.name and l.get("code") == "DOMAIN_MISMATCH"]
            prop = decide(f"propose {other} H9 into crypto {n}", mission / "fixtures/proposals/e2e/06-stocks-h9.json")
            if rejected and prop.get("decision") in ("BLOCK", None):
                counters["interleaved_cycles_other_domain"] += 1
    # ------------------------------------------------------------------ LLM proposals (audited; not a gate, C9)
    llm_url = os.environ.get("SOAK_OLLAMA_URL")
    llm_model = os.environ.get("SOAK_OLLAMA_MODEL")
    if llm_url and llm_model:
        cfg = work / "cain-llm.toml"
        cfg.write_text("\n".join(["[llm]", 'provider = "ollama"', f'model = "{llm_model}"', f'base_url = "{llm_url}"',
                                  "temperature = 0.0", "seed = 42", "timeout = 600.0", "num_ctx = 8192",
                                  "num_predict = 256", "max_input_bytes = 16000", "think = false", ""]),
                       encoding="utf-8")
        for i in range(1, minimums["llm_proposals"] + 2):
            out_file = props / f"llm-{i}.json"
            code, lines, _ = h.cain(f"llm proposal {i}", "explain", f"proximo experimento {i}", "--propose-for-domain",
                                    "crypto", "--state", h.state, "--proposal-out", out_file, "--proposal-id",
                                    f"cain:SOAK-LLM-{i}", "--config", cfg)
            if code != 0 or not out_file.exists():
                continue
            line = decide(f"propose llm {i}", out_file)
            if line.get("decision"):
                counters["llm_proposals"] += 1
                shutil.copy(out_file, out / out_file.name)
                shutil.copy(out_file.with_suffix(".audit.json"), out / out_file.with_suffix(".audit.json").name)
            if line.get("decision") == "ALLOW":
                h.dispatch(f"dispatch llm {i}"); h.consumer(f"consumer llm {i}"); h.ingest(f"ingest llm {i}")
    # ------------------------------------------------------------------ zero tolerance and end checks
    episodes = h.episodes("episodes final")
    emitted = [e for e in episodes["episodes"] if e["task_id"]]
    task_files = list((h.spool / "crypto" / "tasks").glob("TASK-*.json"))
    with h.ro(h.dstate / "admission.sqlite") as db:
        accepted = db.execute("SELECT count(DISTINCT request_id) FROM admissions WHERE decision='ACCEPTED'").fetchone()[0]
    with h.ro(h.dstate / "x" / "journal.sqlite") as db:
        experiments = db.execute("SELECT count(*) FROM experiments").fetchone()[0]
        per_request = db.execute("SELECT max(c) FROM (SELECT count(*) c FROM experiments GROUP BY request_id)").fetchone()[0]
    h.check("tasks emitted == task files in the spool == distinct requests admitted by the domain",
            len(emitted) == len(task_files) == accepted, emitted=len(emitted), spool=len(task_files), admitted=accepted)
    h.check("one experiment per request in the domain (no duplicated effect)", per_request == 1 and
            experiments == accepted, experiments=experiments)
    terminal = {r["task_id"] for r in episodes["inbox"] if r["class"] == "TERMINAL_RESULT"}
    h.check("no result lost: every emitted task has a terminal result", {e["task_id"] for e in emitted} <= terminal,
            missing=sorted({e["task_id"] for e in emitted} - terminal))
    payloads = {}
    for r in episodes["inbox"]:
        if r["payload_sha256"]:
            payloads.setdefault(r["task_id"], set()).add(r["payload_sha256"])
    h.check("one domain payload per task", all(len(v) == 1 for v in payloads.values()))
    h.check("one memory fact per terminal task", sum(1 for r in episodes["inbox"] if r["fact_id"])
            >= len(terminal) and episodes["memory"]["status"] == "intact", memory=episodes["memory"])
    h.check("episodes 1..n without gap", [e["number"] for e in episodes["episodes"]]
            == list(range(1, len(episodes["episodes"]) + 1)))
    for _p, result in h.results():
        if result["result"] is not None and result["outcome"]["status"] == "RESULT":
            code, shown = h.show(f"show {result['request_id']}", result["request_id"])
            h.check(f"{result['request_id']}: payload == authoritative re-read",
                    code == 0 and shown.get("result_sha256") == result["result"]["payload_sha256"])
    h.no_canary("soak")
    mem = (h.state / "memory.sqlite").read_bytes()
    h.check("no contamination: no fact of another domain", b'"cube":"stocks"' not in mem
            and b'"cube":"brasileirao"' not in mem)
    h.check("no ALLOW for crypto:H1..H9", all("crypto:H" not in e.get("proposal_id", "") for e in emitted))
    h.check("no capital_permission true anywhere", all(
        b'"capital_permission":true' not in p.read_bytes().replace(b" ", b"")
        for p in list(h.state.iterdir()) + list(h.spool.rglob("*.json"))))
    # ------------------------------------------------------------------ floors of the frozen profile
    classes = {k: v for k, v in counters["failure_runs"].items() if v >= minimums["runs_per_failure_class"]}
    for key in ("cycles", "duplicates", "domain_restarts", "cain_restarts", "interleaved_cycles_other_domain"):
        h.check(f"floor {key} >= {minimums[key]}", counters[key] >= minimums[key], got=counters[key])
    h.check(f"floor relevant failure classes >= {minimums['relevant_failure_classes']} "
            f"(each >= {minimums['runs_per_failure_class']} runs)",
            len(classes) >= minimums["relevant_failure_classes"], got=counters["failure_runs"])
    h.check(f"floor llm_proposals >= {minimums['llm_proposals']}", counters["llm_proposals"] >= minimums["llm_proposals"],
            got=counters["llm_proposals"], model=llm_model, url=llm_url)
    return h.finish({"counters": counters})


if __name__ == "__main__":
    raise SystemExit(main())
