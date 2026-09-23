"""crypto / fase soak: executa QUALIFICATION_PROFILE_CRYPTO_V1 pelo entrypoint instalado.

Roda no runtime suportado (venv limpo só com as final_wheels). Usa os vetores congelados
da suíte de conformidade do final_commit (tests/conformance/fixtures.py, passado por
--tests), cada chamada ao `cripto-research` num processo novo. Um JSON por linha no log
bruto; ao fim, as checagens de tolerância zero.

Uso: python soak.py --tests <árvore tests/ do final_commit> --work <dir> --log <soak.jsonl>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import sys
import time
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tests", type=Path, required=True)
    ap.add_argument("--work", type=Path, required=True)
    ap.add_argument("--log", type=Path, required=True)
    args = ap.parse_args()
    sys.path.insert(0, str(args.tests))
    from conformance.fixtures import build, cli, experiments, ops_runtime, request, write_request

    from GarimpoInvestimentos.research_faults import PROCESS_DEATH_POINTS

    log = args.log.open("a", encoding="utf-8")

    def record(kind: str, **fields) -> dict:
        row = {"at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "kind": kind, **fields}
        log.write(json.dumps(row, sort_keys=True) + "\n")
        log.flush()
        return row

    env = build(args.work / "main")
    hang_env = build(args.work / "hang", timeout_seconds=5)
    expected_results: dict[str, str] = {}  # request_id -> result_id
    violations: list[str] = []

    def run(e, name: str, value: dict, *, fault: str | None = None) -> tuple[int, dict]:
        path = write_request(e, name, value)
        code, lines = cli(e, "process", str(path), fault=fault)
        outcome = lines[0] if lines else {}
        record("process", request_id=value["request_id"], fault=fault, exit=code,
               status=outcome.get("status"), result_id=outcome.get("result_id"),
               operational_state=outcome.get("operational_state"),
               scientific_state=outcome.get("scientific_state"), economic_state=outcome.get("economic_state"))
        return code, outcome

    # 20 ciclos normais, intercalados com duplicatas, restarts e falhas
    for i in range(20):
        rid = f"crypto:REQ-SOAK-N-{i:03d}"
        code, outcome = run(env, f"n{i}", request(rid))
        if code != 0 or outcome.get("status") != "RESULT":
            violations.append(f"normal {rid}: {code} {outcome.get('status')}")
        expected_results[rid] = outcome.get("result_id")
        if i % 4 == 0 and i // 4 < 5:  # 5 duplicatas
            dup = request(f"crypto:REQ-SOAK-N-{i:03d}", client_ref={"dup": i})
            code, outcome = run(env, f"d{i}", dup)
            if code != 0 or outcome.get("status") != "DUPLICATE" or outcome.get("client_ref") != {"dup": i}:
                violations.append(f"duplicate {rid}: {code} {outcome.get('status')}")
        if i % 4 == 1 and i // 4 < 5:  # 5 restarts em pontos de morte do processo, em rodízio
            point = PROCESS_DEATH_POINTS[(i // 4) % len(PROCESS_DEATH_POINTS)]
            rrid = f"crypto:REQ-SOAK-R-{i:03d}"
            code, _ = run(env, f"r{i}", request(rrid), fault=point)
            code2, outcome = run(env, f"r{i}", request(rrid))
            if code != 86 or code2 != 0 or outcome.get("status") not in {"RESULT", "DUPLICATE"}:
                violations.append(f"restart {point}: {code}/{code2} {outcome.get('status')}")
            expected_results[rrid] = outcome.get("result_id")

    # classes de falha relevantes, 3 execuções cada
    for k in range(3):
        rid = f"crypto:REQ-SOAK-CRASH-{k}"
        code, outcome = run(env, f"c{k}", request(rid), fault="ops_worker_crash")
        if code != 3 or outcome.get("scientific_state") != "NOT_EVALUATED":
            violations.append(f"crash {rid}: {code}")
        code, outcome = run(env, f"c{k}", request(rid))
        expected_results[rid] = outcome.get("result_id")
        rid = f"crypto:REQ-SOAK-HANG-{k}"
        code, outcome = run(hang_env, f"h{k}", request(rid), fault="ops_worker_hang")
        if code != 3 or outcome.get("operational_state") != "TIMEOUT":
            violations.append(f"hang {rid}: {code} {outcome.get('operational_state')}")
        code, outcome = run(hang_env, f"h{k}", request(rid))
        if code != 0:
            violations.append(f"hang retry {rid}: {code}")
        rid = f"crypto:REQ-SOAK-ADM-{k}"
        code, _ = run(env, f"a{k}", request(rid), fault="before_admission_commit")
        code2, outcome = run(env, f"a{k}", request(rid))
        if code != 86 or code2 != 0:
            violations.append(f"before_admission_commit {rid}: {code}/{code2}")
        expected_results[rid] = outcome.get("result_id")
        rid = f"crypto:REQ-SOAK-WRITE-{k}"
        code, _ = run(env, f"w{k}", request(rid), fault="during_result_write")
        code2, outcome = run(env, f"w{k}", request(rid))
        if code != 86 or code2 != 0:
            violations.append(f"during_result_write {rid}: {code}/{code2}")
        expected_results[rid] = outcome.get("result_id")

    # casos A, B e C (C = crash/hang acima), 3 ciclos cada
    for k in range(3):
        for case, dataset, want in (("A", "case_a", ("INCONCLUSIVE", "NO_EDGE")), ("B", "case_b", ("SUPPORTED", "NO_EDGE"))):
            rid = f"crypto:REQ-SOAK-CASE{case}-{k}"
            code, outcome = run(env, f"k{case}{k}", request(rid, dataset=dataset))
            if (outcome.get("scientific_state"), outcome.get("economic_state")) != want:
                violations.append(f"case {case} {rid}: {outcome.get('scientific_state')}/{outcome.get('economic_state')}")
            expected_results[rid] = outcome.get("result_id")

    # checagens de tolerância zero
    results_db = env["state"] / "results.sqlite"
    with sqlite3.connect(results_db) as db:
        rows = db.execute("SELECT request_id,result_id,content_hash FROM results").fetchall()
    stored = {r: res for r, res, _ in rows}
    lost = [r for r, res in expected_results.items() if stored.get(r) != res]
    extra = [r for r in stored if r not in expected_results]
    effects = list(experiments(env).rglob("domain-effect.json"))
    per_experiment_success = {}
    for events in ops_runtime(env).glob("crypto-research-*/events.jsonl"):
        n = sum(1 for line in events.read_text(encoding="utf-8").splitlines()
                if line.strip() and json.loads(line).get("run_status") == "SUCCEEDED")
        per_experiment_success[events.parent.name] = n
    reread_mismatch = []
    for rid in expected_results:
        code, lines = cli(env, "show", rid)
        result = lines[0].get("result") if lines else None
        blob = None
        with sqlite3.connect(results_db) as db:
            row = db.execute("SELECT result FROM results WHERE request_id=?", (rid,)).fetchone()
            blob = bytes(row[0]) if row else None
        from GarimpoInvestimentos.research_contract import canonical

        if code != 0 or result is None or blob is None or canonical(result) != blob:
            reread_mismatch.append(rid)
        if result is not None and (result.get("capital_permission") is not False
                                   or not all(str(result.get(f, "")).startswith("crypto:")
                                              for f in ("request_id", "result_id", "experiment_id", "admission_id"))):
            violations.append(f"authority/ids {rid}")
    code, lines = cli(env, "reconcile")
    summary = record(
        "summary",
        requests_with_result=len(expected_results),
        stored_results=len(stored),
        lost=lost,
        unexpected=extra,
        domain_effects=len(effects),
        ops_success_per_job_max=max(per_experiment_success.values()) if per_experiment_success else 0,
        ops_jobs=len(per_experiment_success),
        reread_mismatch=reread_mismatch,
        reconcile_exit=code,
        reconcile_findings=(lines[0].get("findings") if lines else None),
        violations=violations,
        effects_sha256=sorted(hashlib.sha256(p.read_bytes()).hexdigest()[:16] for p in effects)[:5],
    )
    ok = (not lost and not extra and not reread_mismatch and not violations and code == 0
          and summary["ops_success_per_job_max"] == 1 and len(effects) == len(stored))
    record("verdict", zero_tolerance_ok=ok)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
