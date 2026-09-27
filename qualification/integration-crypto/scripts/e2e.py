"""integration-crypto, fase e2e (E2E, PROVENANCE, FUTURE_CANARY, CAIN_INGESTION, CAIN_CONTAINMENT, AUTHORITY_SEPARATION).

Circuito inteiro pelo runtime suportado, a partir dos entrypoints do CAIN e do consumidor, com os dados públicos reais:
    cain research propose → dispatch → predictor-research-consumer (adapter → adapter_api → admission → Ops → Core)
    → cain research ingest → memória do domínio → próxima decisão (N+1)
Plano congelado em FROZEN_VECTORS.json → e2e_plan. Restart do consumidor e do CAIN no meio (episódio 02),
entrega intercalada de resultados V2 dos outros dois domínios (fixtures congeladas), canário pós-cutoff (03),
duplicata (04), hipótese encerrada (05), outro domínio (06), N+1 depois dos resultados (07).

Uso (com o env.sh do runtime_env.sh): python e2e.py <qualification/integration-crypto> <work> <out>
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

from harness import Harness


def main() -> int:
    mission, work, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    h = Harness(out, work, mission, "e2e")
    vectors = json.loads((mission / "FROZEN_VECTORS.json").read_text(encoding="utf-8"))
    plan = {Path(item["proposal"]).stem: item for item in vectors["e2e_plan"]}

    def propose(name: str, **kw) -> dict:
        code, lines, _ = h.propose(f"propose {name}", plan[name]["proposal"], **kw)
        line = lines[0] if lines else {}
        h.check(f"{name}: decision {plan[name]['expected_decision']}", code == 0
                and line.get("decision") == plan[name]["expected_decision"], got=line)
        return line

    def roundtrip(name: str) -> dict:
        h.dispatch(f"dispatch {name}")
        h.consumer(f"consumer {name}")
        _code, lines, _ = h.ingest(f"ingest {name}")
        return {"ingest": lines}

    # 01: first episode, full roundtrip
    first = propose("01-allow")
    roundtrip("01-allow")
    # 02: consumer dies after the domain and before the V2 result; CAIN dies during ingestion
    second = propose("02-allow-restarts")
    h.dispatch("dispatch 02")
    code, _, _ = h.consumer("consumer 02 (fault)", fault="after_domain_before_result_write")
    h.check("02: consumer died at after_domain_before_result_write (exit 86)", code == 86, exit=code)
    h.check("02: no V2 result written before the restart",
            not any(r["task_id"] == second["task"]["task_id"] for _p, r in h.results()))
    h.consumer("consumer 02 (restart)")
    code, _, _ = h.ingest("ingest 02 (fault)", fault="after_inbox_commit_before_memory")
    h.check("02: CAIN died at after_inbox_commit_before_memory (exit 86)", code == 86, exit=code)
    _code, lines, _ = h.ingest("ingest 02 (restart)")
    h.check("02: restarted ingestion completed the memory", any(l.get("action") == "remembered" for l in lines),
            got=lines)
    # interleaved: V2 results of the other two domains land in the crypto spool
    results_dir = h.spool / "crypto" / "results"
    for rel in ("fixtures/v2/stocks/result-h9.json", "fixtures/v2/brasileirao/result-h9.json",
                "fixtures/v2/crypto/result-h9.json"):
        shutil.copy(mission / rel, results_dir / ("interleaved-" + rel.replace("/", "-")))
    code, lines, _ = h.ingest("ingest interleaved other domains")
    rejected = {l["file"]: l.get("code") for l in lines if l.get("action") == "rejected"}
    h.check("interleaved: stocks and brasileirao results rejected (DOMAIN_MISMATCH), crypto H9 of a task never "
            "emitted rejected (TASK_NOT_FOUND)", rejected == {
                "interleaved-fixtures-v2-stocks-result-h9.json": "DOMAIN_MISMATCH",
                "interleaved-fixtures-v2-brasileirao-result-h9.json": "DOMAIN_MISMATCH",
                "interleaved-fixtures-v2-crypto-result-h9.json": "TASK_NOT_FOUND"}, got=rejected)
    # 03: canary after the cutoff
    canary = propose("03-canary")
    roundtrip("03-canary")
    # 04..06: duplicate, closed hypothesis, other domain: no task
    for name in ("04-duplicate", "05-h9-closed", "06-stocks-h9"):
        line = propose(name)
        h.check(f"{name}: no task emitted", line.get("task") is None)
    # 07: next step after the results (N+1)
    nxt = propose("07-next")
    roundtrip("07-next")

    # ------------------------------------------------------------------ verification
    tasks = {first["task"]["task_id"]: "01", second["task"]["task_id"]: "02", canary["task"]["task_id"]: "03",
             nxt["task"]["task_id"]: "07"}
    by_task: dict[str, list] = {}
    for _path, result in h.results():
        by_task.setdefault(result["task_id"], []).append(result)
    h.check("every emitted task has a V2 result; no result for any other task", set(by_task) == set(tasks),
            tasks=sorted(tasks), results=sorted(by_task))
    for task_id, results in sorted(by_task.items()):
        task = h.task(task_id)
        statuses = sorted(r["outcome"]["status"] for r in results)
        if tasks[task_id] == "03":
            h.check("03: the domain refused the canary (TEMPORAL_INTEGRITY_VIOLATION), no domain result",
                    statuses == ["TEMPORAL_INTEGRITY_VIOLATION"] and results[0]["result"] is None, got=statuses)
            continue
        h.check(f"{tasks[task_id]}: terminal RESULT/DUPLICATE with one domain payload",
                set(statuses) <= {"RESULT", "DUPLICATE"}
                and len({r["result"]["payload_sha256"] for r in results}) == 1, got=statuses)
        for result in results:
            h.provenance(result, task)
    code, shown = h.show("show canary", "crypto:REQ-IC-E2E-003")
    h.check("03: the domain has no authoritative result for the canary", code != 0, exit=code, got=shown)
    with h.ro(h.dstate / "results.sqlite") as db:
        tables = [r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")]
    h.check("domain result store readable", bool(tables), tables=tables)
    episodes = h.episodes("episodes final")
    decisions = [e["decision"] for e in episodes["episodes"]]
    h.check("episodes numbered 1..n without gap", [e["number"] for e in episodes["episodes"]]
            == list(range(1, len(decisions) + 1)), decisions=decisions)
    h.check("one inbox row per result file, memory hash chain intact",
            len(episodes["inbox"]) == sum(len(v) for v in by_task.values())
            and episodes["memory"]["status"] == "intact", inbox=len(episodes["inbox"]), memory=episodes["memory"])
    emitted = [e["task_id"] for e in episodes["episodes"] if e["task_id"]]
    h.check("tasks emitted == ALLOW decisions == task files in the spool",
            len(emitted) == decisions.count("ALLOW") == len(list((h.spool / "crypto" / "tasks").glob("*.json"))),
            emitted=len(emitted))
    chain = [h.task(t) for t in emitted]
    h.check("previous_task_id chains the domain's tasks",
            [t["previous_task_id"] for t in chain] == [None] + [t["task_id"] for t in chain[:-1]])
    h.no_canary("e2e")
    mem = (h.state / "memory.sqlite").read_bytes()
    h.check("no fact of another domain in the CAIN memory", b'"cube":"stocks"' not in mem
            and b'"cube":"brasileirao"' not in mem)
    h.check("no capital_permission true in CAIN state or spool", all(
        b'"capital_permission":true' not in p.read_bytes().replace(b" ", b"")
        for p in list(h.state.iterdir()) + list(h.spool.rglob("*.json"))))
    return h.finish({"decisions": decisions})


if __name__ == "__main__":
    raise SystemExit(main())
