"""integration-brasileirao, fase e2e (E2E, PROVENANCE, FUTURE_CANARY, CAIN_INGESTION, CAIN_CONTAINMENT, AUTHORITY_SEPARATION).

Adaptado de qualification/integration-stocks/scripts/e2e.py. Circuito inteiro pelo runtime suportado no owner_linux
(PC 2), a partir dos entrypoints do CAIN e do consumidor, com o dado REAL privado (dataset real-20260908 capturado da
cópia conferida; canário real-canary-20260908):
    cain research propose → dispatch → predictor-research-consumer (adapter → adapter_api → admission → Ops → Core)
    → cain research ingest → memória do domínio brasileirao → próxima decisão (N+1)
Plano congelado em FROZEN_VECTORS.json → e2e_plan: restart do consumidor e do CAIN no meio (02), entrega intercalada
de resultados V2 dos outros dois domínios (fixtures congeladas da integration-crypto), canário depois do data_cutoff (03)
com o controle sem canário (04), duplicata (05), hipótese protegida (06), H9 do cripto e do stocks (07, 08), família
congelada do loop do PR #50 (09), N+1 depois dos resultados (10). Só temporadas 2021–2024; nada de 2025+ é despachado.

A comparação canário × controle (previsões, avaliação, economia e qualidade) é feita no diretório privado; a evidência
pública tem só o booleano e os sha256 do conteúdo comparável. Nenhum valor do dado vai para a saída pública.

Uso (com o env.sh do runtime_env.sh): python e2e.py <qualification/integration-brasileirao> <work privado> <out>
"""

from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

from harness import Harness, sha


def comparable(result: dict) -> dict:
    """Conteúdo que tem de ser igual entre duas execuções da mesma pergunta (sem identidades do run)."""
    domain = result["domain_facts"]
    return {
        "result_state": result["result_state"], "scientific_state": result["scientific_state"],
        "economic_state": result["economic_state"],
        "predictions": [{k: v for k, v in p.items() if k != "information_fingerprint"} for p in domain["predictions"]],
        "evaluation": domain["evaluation"], "economics": domain["economics"], "data_quality": domain["data_quality"],
    }


def canon(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def main() -> int:
    mission, work, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    h = Harness(out, work, mission, "e2e")
    vectors = json.loads((mission / "FROZEN_VECTORS.json").read_text(encoding="utf-8"))
    plan = {Path(item["proposal"]).stem: item for item in vectors["e2e_plan"]}
    fixtures = mission.parent / "integration-crypto" / "fixtures" / "v2"

    def propose(name: str, **kw) -> dict:
        code, lines, _ = h.propose(f"propose {name}", plan[name]["proposal"], **kw)
        line = lines[0] if lines else {}
        expected = plan[name]
        ok = code == 0 and line.get("decision") == expected["expected_decision"] and (
            "expected_reason" not in expected or line.get("reason_code") == expected["expected_reason"])
        h.check(f"{name}: decision {expected['expected_decision']} {expected.get('expected_reason', '')}".strip(), ok,
                got={k: line.get(k) for k in ("decision", "reason_code", "rule")})
        return line

    def roundtrip(name: str) -> dict:
        h.dispatch(f"dispatch {name}")
        h.consumer(f"consumer {name}")
        _code, lines, _ = h.ingest(f"ingest {name}")
        return {"ingest": lines}

    first = propose("01-allow")
    roundtrip("01-allow")
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
            got=[l.get("action") for l in lines])
    results_dir = h.spool / "brasileirao" / "results"
    for domain in ("crypto", "stocks", "brasileirao"):
        shutil.copy(fixtures / domain / "result-h9.json", results_dir / f"interleaved-{domain}-result-h9.json")
    code, lines, _ = h.ingest("ingest interleaved other domains")
    rejected = {l["file"]: l.get("code") for l in lines if l.get("action") == "rejected"}
    h.check("interleaved: crypto and stocks results rejected (DOMAIN_MISMATCH), brasileirao H9 of a task never "
            "emitted rejected (TASK_NOT_FOUND)", rejected == {
                "interleaved-crypto-result-h9.json": "DOMAIN_MISMATCH",
                "interleaved-stocks-result-h9.json": "DOMAIN_MISMATCH",
                "interleaved-brasileirao-result-h9.json": "TASK_NOT_FOUND"}, got=rejected)
    canary = propose("03-canary")
    roundtrip("03-canary")
    control = propose("04-canary-control")
    roundtrip("04-canary-control")
    for name in ("05-duplicate", "06-h9-protected", "07-crypto-h9", "08-stocks-h9", "09-frozen-family"):
        line = propose(name)
        h.check(f"{name}: no task emitted", line.get("task") is None)
    nxt = propose("10-next")
    roundtrip("10-next")

    tasks = {first["task"]["task_id"]: "01", second["task"]["task_id"]: "02", canary["task"]["task_id"]: "03",
             control["task"]["task_id"]: "04", nxt["task"]["task_id"]: "10"}
    by_task: dict[str, list] = {}
    for _path, result in h.results():
        by_task.setdefault(result["task_id"], []).append(result)
    h.check("every emitted task has a V2 result; no result for any other task", set(by_task) == set(tasks),
            tasks=sorted(tasks), results=sorted(by_task))
    states, bodies = {}, {}
    for task_id, results in sorted(by_task.items()):
        task = h.task(task_id)
        statuses = sorted(r["outcome"]["status"] for r in results)
        h.check(f"{tasks[task_id]}: terminal RESULT/DUPLICATE with one domain payload",
                set(statuses) <= {"RESULT", "DUPLICATE"}
                and len({r["result"]["payload_sha256"] for r in results if r["result"]}) == 1, got=statuses)
        body = results[0]["result"]
        states[tasks[task_id]] = {k: body[k] for k in ("result_state", "scientific_state", "economic_state",
                                                       "operational_state")}
        bodies[tasks[task_id]] = json.loads(body["payload_canonical"])
        for result in results:
            h.provenance(result, task)
    same = canon(comparable(bodies["03"])) == canon(comparable(bodies["04"]))
    h.check("03 × 04: the canary (rows after the data_cutoff) never changed a prediction, metric, economic figure, data "
            "quality count or state (compared in the private directory)", same,
            canary_comparable_sha256=sha(canon(comparable(bodies["03"]))),
            control_comparable_sha256=sha(canon(comparable(bodies["04"]))))
    h.check("03: the canary dataset is the canary reference, the control the real one (only references differ)",
            bodies["03"]["domain_facts"]["references"]["dataset"]["name"] == "real-canary-20260908"
            and bodies["04"]["domain_facts"]["references"]["dataset"]["name"] == "real-20260908")
    h.check("03/04: every prediction cutoff is at or before the request data_cutoff (no information after it)",
            all(p["cutoff"] <= "2024-10-01T00:00:00Z" for n in ("03", "04") for p in bodies[n]["domain_facts"]["predictions"]),
            predictions={n: len(bodies[n]["domain_facts"]["predictions"]) for n in ("03", "04")})
    h.check("no request of season 2025 or later reached the domain (holdout sealed)",
            all(h.task(t)["payload"]["season"] <= 2024 for t in tasks), seasons=sorted({h.task(t)["payload"]["season"]
                                                                                        for t in tasks}))
    episodes = h.episodes("episodes final")
    decisions = [e["decision"] for e in episodes["episodes"]]
    h.check("episodes numbered 1..n without gap", [e["number"] for e in episodes["episodes"]]
            == list(range(1, len(decisions) + 1)), decisions=decisions)
    h.check("one inbox row per result file, memory hash chain intact",
            len(episodes["inbox"]) == sum(len(v) for v in by_task.values())
            and episodes["memory"]["status"] == "intact", inbox=len(episodes["inbox"]), memory=episodes["memory"])
    emitted = [e["task_id"] for e in episodes["episodes"] if e["task_id"]]
    h.check("tasks emitted == ALLOW decisions == task files in the spool",
            len(emitted) == decisions.count("ALLOW") == len(list((h.spool / "brasileirao" / "tasks").glob("*.json"))),
            emitted=len(emitted))
    chain = [h.task(t) for t in emitted]
    h.check("previous_task_id chains the domain's tasks",
            [t["previous_task_id"] for t in chain] == [None] + [t["task_id"] for t in chain[:-1]])
    h.check("episode IDs are brasileirao/episode-<n> and every ID is brasileirao:-qualified",
            all(t["episode_id"].startswith("brasileirao:episode-") and t["task_id"].startswith("brasileirao:TASK-")
                and t["request_id"].startswith("brasileirao:") and t["hypothesis_id"].startswith("brasileirao:")
                for t in chain))
    h.no_canary("e2e")
    mem = (h.state / "memory.sqlite").read_bytes()
    h.check("no fact of another domain in the CAIN memory", b'"cube":"crypto"' not in mem
            and b'"cube":"stocks"' not in mem)
    h.check("no capital_permission true in CAIN state or spool", all(
        b'"capital_permission":true' not in p.read_bytes().replace(b" ", b"")
        for p in list(h.state.iterdir()) + list(h.spool.rglob("*.json"))))
    env = json.loads(Path(os.environ["REAL_ENV"]).read_text(encoding="utf-8"))
    return h.finish({"decisions": decisions, "domain_states": states,
                     "real_env": {"datasets": env["datasets"], "policy": env["policy"],
                                  "dataset_source_sha256": env["dataset_source_sha256"]}})


if __name__ == "__main__":
    raise SystemExit(main())
