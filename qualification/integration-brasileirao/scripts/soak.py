"""integration-brasileirao, fase soak (SOAK; QUALIFICATION_PROFILE_INTEGRATION_BR_V1.json, lido e nunca alterado).

Adaptado de qualification/integration-stocks/scripts/soak.py. Os 24 ciclos do domínio brasileirao seguem o
FROZEN_VECTORS.json → soak_generator (hipóteses QUAL-SERVING-REAL-001..003 em rodízio, temporada × alvo × baseline ×
janela, dataset real-20260908 v1, só 2021–2024), pelo runtime suportado, com o dado real privado, no mesmo estado do
CAIN. Em ciclos nomeados (plano do perfil): reinícios do CAIN F01–F06 (uma vez cada), do consumidor F08 × 2, F16 × 2 e
F07 × 2, falha retryable do domínio F14 × 3, duplicatas (2 reentregas de task, 2 de resultado, 2 repropostas do mesmo
conteúdo) e 6 ciclos intercalados REAIS de outro domínio pelos runtimes integrados (3 cripto, 3 stocks), cada um
seguido da entrega cruzada do resultado real e da proposta desse domínio ao brasileirao (têm de ser recusados sem
efeito). Depois, as propostas de LLM (`cain research explain` no modo de proposta, Ollama local do PC 2; auditadas;
não são gate, C9). Um pedido que a política não deixa passar (COOLDOWN/ABSTAIN) fica registrado e é proposto de novo
mais tarde (no máximo 4 vezes); o ciclo só conta quando o roundtrip completa.
Todos os números do relatório saem do log bruto (commands.log) e do SUMMARY.json deste script.

Uso (com o env.sh do runtime_env.sh, INTEGRATED=1; SOAK_OLLAMA_URL e SOAK_OLLAMA_MODEL para as propostas de LLM):
python soak.py <qualification/integration-brasileirao> <work> <out>
"""

from __future__ import annotations

import copy
import json
import os
import re
import shutil
import sys
from pathlib import Path

from harness import Harness, now
from isolation import CUBES

CAIN_FAULTS = {0: "after_outbox_commit", 1: "after_spool_write_before_ack", 2: "after_inbox_commit_before_memory",
               3: "after_memory_commit", 4: "after_decision_before_episode_commit", 5: "cain_stopped"}
CONSUMER_FAULTS = {6: "F08", 10: "F08", 7: "F16", 11: "F16", 8: "F07", 12: "F07"}
RETRYABLE = {9, 13, 17}
DUPLICATES = {14: "task", 18: "task", 15: "result", 19: "result", 16: "repropose", 20: "repropose"}
INTERLEAVED = {1: "crypto", 3: "stocks", 5: "crypto", 7: "stocks", 9: "crypto", 11: "stocks"}
MAX_ATTEMPTS = 4


def main() -> int:
    mission, work, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    profile = json.loads((mission / "QUALIFICATION_PROFILE_INTEGRATION_BR_V1.json").read_text(encoding="utf-8"))
    gen = json.loads((mission / "FROZEN_VECTORS.json").read_text(encoding="utf-8"))["soak_generator"]
    frozen = json.loads((mission / "FROZEN_PARAMETERS.json").read_text(encoding="utf-8"))
    proposable = set(frozen["decision_policy"]["brasileirao_config"]["proposable_hypotheses"])
    template = "fixtures/proposals/e2e/01-allow.json"
    base_refs = json.loads((mission / template).read_text(encoding="utf-8"))["request"]["references"]
    h = Harness(out, work, mission, "soak")
    side = {"crypto": h.for_domain("crypto"), "stocks": h.for_domain("stocks")}
    props = work / "proposals"
    props.mkdir(parents=True, exist_ok=True)
    counters = {"cycles": 0, "duplicates": 0, "domain_restarts": 0, "cain_restarts": 0,
                "interleaved_cycles_other_domain": 0, "failure_runs": {}, "decisions": {}, "llm_proposals": 0,
                "deferred": 0}
    minimums = profile["minimums"]
    events_log = []

    def proposal(n: int) -> Path:
        s = gen["schedule"][n - 1]
        season = s["season"]
        start = f"{season}-01-01T00:00:00Z" if s["window"] == "season" else f"{season}-07-01T00:00:00Z"
        refs = copy.deepcopy(base_refs)
        refs["baseline"]["name"] = s["baseline"]
        path = h.proposal_path(template, props / f"{n:03d}.json",
                               request_id=gen["request_id"].replace("<nnn>", f"{n:03d}"),
                               hypothesis_id=gen["hypotheses"][(n - 1) % len(gen["hypotheses"])], season=season,
                               target=s["target"], references=refs,
                               events={"kickoff_from": start, "kickoff_to": f"{season + 1}-01-01T00:00:00Z"})
        value = json.loads(path.read_text(encoding="utf-8"))
        value["proposal_id"] = f"cain:IB-SOAK-{n:03d}"
        path.write_text(json.dumps(value, ensure_ascii=False, indent=1), encoding="utf-8")
        return path

    def decide(label: str, path: Path, harness: Harness = h, **kw) -> dict:
        _code, lines, _ = harness.propose(label, path, **kw)
        line = lines[0] if lines else {}
        if harness is h:
            counters["decisions"][line.get("decision")] = counters["decisions"].get(line.get("decision"), 0) + 1
        return line

    def fail_class(name: str) -> None:
        counters["failure_runs"][name] = counters["failure_runs"].get(name, 0) + 1

    def restart(kind: str, code: int, label: str) -> None:
        ok = code == 86
        counters[kind] += ok
        events_log.append({"event": label, "exit": code, "counted": ok})

    def interleave(i: int, domain: str) -> None:
        """A real cycle of another domain by its integrated runtime, then its result and proposal to the brasileirao."""
        x = side[domain]
        rel = "fixtures/proposals/e2e/01-allow.json"
        other = json.loads((mission.parent / f"integration-{domain}" / rel).read_text(encoding="utf-8"))["request"]
        params = dict(other["parameters"])
        # another experiment each time (R17 EQUIVALENT_REQUEST): crypto by its placebo seed (as its own soak), stocks
        # by the securities cap
        if domain == "crypto":
            params["placebo_seed"] = 2000 + i
            hyp = f"crypto:QUAL-SHADOW-REAL-00{(i - 1) % 3 + 1}"
            rid = f"crypto:REQ-IB-SOAK-X{i:02d}"
        else:
            params["max_securities"] = int(params["max_securities"]) - i
            hyp = f"stocks:QUAL-PIT-MOM-REAL-00{(i - 1) % 3 + 1}"
            rid = f"stocks:REQ-IB-SOAK-X{i:02d}"
        path = h.integrated_proposal(domain, rel, props / f"x{i:02d}-{domain}.json", f"cain:IB-SOAK-X{i:02d}-{domain}",
                                     request_id=rid, hypothesis_id=hyp, parameters=params)
        line = decide(f"{domain} {i}: propose real (integrated)", path, x)
        seen = {p.name for p, _r in x.results(domain)}
        if line.get("decision") == "ALLOW":
            x.dispatch(f"{domain} {i}: dispatch"); x.consumer(f"{domain} {i}: consumer"); x.ingest(f"{domain} {i}: ingest")
        new = [(p, r) for p, r in x.results(domain) if p.name not in seen]
        real = len(new) == 1 and new[0][1]["outcome"]["status"] == "RESULT"
        h.check(f"interleaved {i}: real {domain} cycle completed in its own orchestration", real,
                decision=line.get("decision"), statuses=[r["outcome"]["status"] for _p, r in new])
        rejected = False
        if real:
            target = h.spool / "brasileirao" / "results" / f"interleaved-{i:02d}-{domain}.json"
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(new[0][0], target)
            _c, lines, _ = h.ingest(f"brasileirao: ingest the real {domain} result {i}")
            rejected = any(l.get("file") == target.name and l.get("code") == "DOMAIN_MISMATCH" for l in lines)
        cross = decide(f"brasileirao: the {domain} proposal {i}", path)
        blocked = cross.get("decision") == "BLOCK" and cross.get("reason_code") == "DOMAIN_MISMATCH" \
            and not cross.get("task")
        h.check(f"interleaved {i}: {domain} result and proposal refused by the brasileirao without effect",
                rejected and blocked, rejected=rejected, cross={k: cross.get(k) for k in ("decision", "reason_code")})
        counters["interleaved_cycles_other_domain"] += real and rejected and blocked

    queue = [(n, 1) for n in range(1, len(gen["schedule"]) + 1)]
    interleaved_done = 0
    while queue:
        n, attempt = queue.pop(0)
        k = counters["cycles"]
        path = proposal(n)
        as_of = now()
        fault = CAIN_FAULTS.get(k)
        if fault == "after_decision_before_episode_commit":
            code, _, _ = h.propose(f"propose {n} (fault)", path, as_of=as_of, fault=fault)
            restart("cain_restarts", code, f"F05 cycle {n}")
            fail_class("cain_process_death")
        if fault == "after_outbox_commit":
            code, _, _ = h.propose(f"propose {n} (fault)", path, as_of=as_of, fault=fault)
            restart("cain_restarts", code, f"F01 cycle {n}")
            fail_class("cain_process_death")
            last = h.episodes(f"episodes after F01 {n}")["episodes"][-1]
            line = {"decision": last["decision"], "task": {"task_id": last["task_id"]}}
        else:
            line = decide(f"propose {n}", path, as_of=as_of)
        if line.get("decision") != "ALLOW":
            counters["deferred"] += 1
            events_log.append({"event": f"cycle {n} deferred", "decision": line.get("decision"),
                               "reason_code": line.get("reason_code"), "attempt": attempt})
            if attempt < MAX_ATTEMPTS:
                queue.append((n, attempt + 1))
            continue
        task_id = line["task"]["task_id"]
        if fault == "after_spool_write_before_ack":
            code, _, _ = h.dispatch(f"dispatch {n} (fault)", fault=fault)
            restart("cain_restarts", code, f"F02 cycle {n}")
            fail_class("cain_process_death")
        h.dispatch(f"dispatch {n}")
        cf = CONSUMER_FAULTS.get(k)
        if cf == "F08":
            code, _, _ = h.consumer(f"consumer {n} (F08)", fault="after_domain_before_result_write")
            restart("domain_restarts", code, f"F08 cycle {n}")
            fail_class("consumer_process_death")
        elif cf == "F16":
            code, _, _ = h.consumer(f"consumer {n} (F16)", domain_fault="after_ops")
            restart("domain_restarts", code, f"F16 cycle {n}")
            fail_class("consumer_process_death")
        elif cf == "F07":
            h.ingest(f"ingest {n} while the consumer is stopped")
            waiting = (h.spool / "brasileirao" / "tasks" / (task_id.split(":", 1)[1] + ".json")).exists()
            ok = waiting and not [r for _p, r in h.results() if r["task_id"] == task_id]
            counters["domain_restarts"] += ok
            events_log.append({"event": f"F07 cycle {n}", "task_waits_in_spool": waiting, "counted": ok})
        if k in RETRYABLE:
            _c, lines, _ = h.consumer(f"consumer {n} (F14 Ops crash)", domain_fault="ops_worker_crash")
            # the consumer lists every task of the spool (earlier ones as skipped): read this task's line
            retryable = any(l.get("task_id") == task_id and l.get("status") == "OPS_FAILED_RETRYABLE" for l in lines)
            h.ingest(f"ingest {n} retryable")
            h.cain(f"retry {n}", "retry", "--domain", "brasileirao", "--state", h.state, "--spool", h.spool,
                   "--task-id", task_id)
            if retryable:
                fail_class("domain_retryable")
            events_log.append({"event": f"F14 cycle {n}", "retryable": retryable})
        h.consumer(f"consumer {n}")
        if fault == "cain_stopped":
            waits = bool([r for _p, r in h.results() if r["task_id"] == task_id])
            inbox = [r for r in h.episodes(f"episodes {n} (CAIN out)")["inbox"] if r["task_id"] == task_id]
            ok = waits and not inbox
            counters["cain_restarts"] += ok
            events_log.append({"event": f"F06 cycle {n}", "result_waits_in_spool": waits, "counted": ok})
        if fault in ("after_inbox_commit_before_memory", "after_memory_commit"):
            code, _, _ = h.ingest(f"ingest {n} (fault)", fault=fault)
            restart("cain_restarts", code, f"{'F03' if 'inbox' in fault else 'F04'} cycle {n}")
            fail_class("cain_process_death")
        h.ingest(f"ingest {n}")
        counters["cycles"] += 1
        dup = DUPLICATES.get(k)
        if dup == "task":
            h.dispatch(f"resend {n}", resend=True)
            _c, lines, _ = h.consumer(f"consumer resend {n}")
            h.ingest(f"ingest after resend {n}")
            # this task's line only: the re-delivered task is not executed again (skipped or domain DUPLICATE)
            ok = any(l.get("task_id") == task_id and (l.get("status") == "DUPLICATE"
                                                      or l.get("action") in ("skipped", "duplicate")) for l in lines)
        elif dup == "result":
            mine = [p for p, r in h.results() if r["task_id"] == task_id]
            shutil.copy(mine[0], mine[0].with_name(f"redelivered-{n:03d}-" + mine[0].name))
            _c, lines, _ = h.ingest(f"ingest redelivered {n}")
            ok = any(l.get("action") == "duplicate" and l.get("file", "").startswith("redelivered-") for l in lines)
        elif dup == "repropose":
            again = json.loads(path.read_text(encoding="utf-8"))
            again["proposal_id"] = f"cain:IB-SOAK-{n:03d}-again"
            again_path = props / f"{n:03d}-again.json"
            again_path.write_text(json.dumps(again, ensure_ascii=False), encoding="utf-8")
            ok = decide(f"propose duplicate {n}", again_path).get("decision") == "DUPLICATE"
        if dup:
            counters["duplicates"] += ok
            fail_class("delivery_anomaly")
            events_log.append({"event": f"duplicate {dup} cycle {n}", "no_second_effect": ok})
        if k in INTERLEAVED and interleaved_done < len(INTERLEAVED):
            interleaved_done += 1
            interleave(interleaved_done, INTERLEAVED[k])
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
            code, _lines, _ = h.cain(f"llm proposal {i}", "explain", f"proximo experimento {i}",
                                     "--propose-for-domain", "brasileirao", "--state", h.state, "--proposal-out",
                                     out_file, "--proposal-id", f"cain:IB-SOAK-LLM-{i}", "--config", cfg)
            if code != 0 or not out_file.exists():
                continue
            line = decide(f"propose llm {i}", out_file)
            if line.get("decision"):
                counters["llm_proposals"] += 1
                shutil.copy(out_file, out / out_file.name)
                audit = out_file.with_suffix(".audit.json")
                if audit.exists():
                    shutil.copy(audit, out / audit.name)
            if line.get("decision") == "ALLOW":
                h.dispatch(f"dispatch llm {i}"); h.consumer(f"consumer llm {i}"); h.ingest(f"ingest llm {i}")
    # ------------------------------------------------------------------ zero tolerance and end checks
    episodes = h.episodes("episodes final")
    emitted = [e for e in episodes["episodes"] if e["task_id"]]
    task_files = list((h.spool / "brasileirao" / "tasks").glob("TASK-*.json"))
    with h.ro(h.dstate / "admission.sqlite") as db:
        accepted = db.execute("SELECT count(DISTINCT request_id) FROM admissions WHERE decision='ACCEPTED'").fetchone()[0]
    with h.ro(h.dstate / "x" / "journal.sqlite") as db:
        experiments = db.execute("SELECT count(*) FROM experiments").fetchone()[0]
        per_request = db.execute("SELECT max(c) FROM (SELECT count(*) c FROM experiments GROUP BY request_id)").fetchone()[0]
    with h.ro(h.dstate / "results.sqlite") as db:
        per_result = db.execute("SELECT max(c) FROM (SELECT count(*) c FROM results GROUP BY request_id)").fetchone()[0]
    h.check("tasks emitted == task files in the spool == distinct requests admitted by the domain",
            len(emitted) == len(task_files) == accepted, emitted=len(emitted), spool=len(task_files), admitted=accepted)
    h.check("one experiment and one authoritative result per request in the domain (no duplicated effect)",
            per_request == 1 and per_result == 1 and experiments == accepted, experiments=experiments)
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
    emitted_tasks = [h.task(e["task_id"]) for e in emitted]
    chain = [t.get("previous_task_id") for t in emitted_tasks]
    h.check("previous_task_id points to the previous emitted task",
            chain == [None] + [t["task_id"] for t in emitted_tasks[:-1]], chain_length=len(chain))
    for _p, result in h.results():
        if result["result"] is not None and result["outcome"]["status"] in ("RESULT", "DUPLICATE"):
            code, shown = h.show(f"show {result['request_id']}", result["request_id"])
            h.check(f"{result['request_id']}: payload == authoritative re-read",
                    code == 0 and shown.get("result_sha256") == result["result"]["payload_sha256"])
    h.no_canary("soak")
    cubes = work / "cubes.py"
    cubes.write_text(CUBES, encoding="utf-8")
    _c, lines, _ = h.run("memory cubes", [os.environ["CAIN_PY"], "-I", cubes, h.state], public_stdout="full")
    mem = lines[0]
    h.check("no contamination: each domain's facts only in its own cube (the other domains never see brasileirao)",
            mem["verify"] == "intact" and all(all(s.startswith(f"{d}:") for s in mem[d])
                                              for d in ("brasileirao", "crypto", "stocks")), got=mem)
    closed = re.compile(r"brasileirao:(H[0-9]+|A[0-9]+)\Z")
    h.check("no ALLOW for a closed/protected hypothesis or frozen family: every emitted task is proposable",
            all(not closed.match(t["hypothesis_id"]) and t["hypothesis_id"] in proposable for t in emitted_tasks),
            hypotheses=sorted({t["hypothesis_id"] for t in emitted_tasks}))
    h.check("no request of season 2025 or later dispatched, no window into 2025 (holdout sealed)",
            all(t["payload"]["season"] <= 2024 and t["payload"]["events"]["kickoff_to"] <= "2025-01-01T00:00:00Z"
                for t in emitted_tasks), seasons=sorted({t["payload"]["season"] for t in emitted_tasks}))
    h.check("NEGATIVE_RESULT_NEUTRALITY: every emitted task NORMAL priority; budget constants unchanged",
            all(t["payload"]["priority_hint"] == "NORMAL" for t in emitted_tasks)
            and len(emitted) <= frozen["decision_policy"]["brasileirao_config"]["budget"]["max_tasks_total"])
    h.check("no capital_permission true anywhere", all(
        b'"capital_permission":true' not in p.read_bytes().replace(b" ", b"")
        for p in [q for q in h.state.iterdir() if q.is_file()] + list(h.spool.rglob("*.json"))))
    # ------------------------------------------------------------------ floors of the frozen profile
    classes = {k: v for k, v in counters["failure_runs"].items() if v >= minimums["runs_per_failure_class"]}
    for key in ("cycles", "duplicates", "domain_restarts", "cain_restarts", "interleaved_cycles_other_domain"):
        h.check(f"floor {key} >= {minimums[key]}", counters[key] >= minimums[key], got=counters[key])
    h.check(f"floor relevant failure classes >= {minimums['relevant_failure_classes']} "
            f"(each >= {minimums['runs_per_failure_class']} runs)",
            len(classes) >= minimums["relevant_failure_classes"], got=counters["failure_runs"])
    h.check(f"floor llm_proposals >= {minimums['llm_proposals']}", counters["llm_proposals"] >= minimums["llm_proposals"],
            got=counters["llm_proposals"], model=llm_model, url=llm_url)
    return h.finish({"counters": counters, "events": events_log, "memory_cubes": mem})


if __name__ == "__main__":
    raise SystemExit(main())
