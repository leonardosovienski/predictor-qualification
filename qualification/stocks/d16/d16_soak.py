"""stocks / D-16: soak do perfil congelado QUALIFICATION_PROFILE_STOCKS_V1 sobre o painel REAL.

Mesmo desenho do scripts/soak.py (diagnóstico com fixture), trocando os vetores sintéticos pelo
ambiente de operador real (real_env.py): cada chamada ao entrypoint instalado `stocks-research`
é um processo novo; uma linha JSON por chamada no log bruto; no fim, as checagens de tolerância zero.

Perfil (congelado): 20 ciclos normais, 5 restarts, 5 duplicados, 3 por classe de falha relevante
(crash do job do Ops, crash da admission, crash na gravação do resultado), 3 timeouts, 3
família-não-pronta, 5 coletas válidas em COLLECTION_ONLY (fonte oficial CVM VLMO), 0 trial
elegível enquanto nenhuma família estiver READY.

--profile windows: o subconjunto do WINDOWS_SMOKE (restart em cada ponto de morte do processo,
em rodízio, + duplicata), com as mesmas checagens de perda/duplicata/releitura.

Uso: python d16_soak.py --tests <tests/> --build <dir do build> --protocol <PROTOCOL_REAL.json>
       --matrix <matriz.json> --work <dir> --log <soak.jsonl> [--profile full|windows]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tests", type=Path, required=True)
    ap.add_argument("--build", type=Path, required=True)
    ap.add_argument("--protocol", type=Path, required=True)
    ap.add_argument("--matrix", type=Path, required=True)
    ap.add_argument("--work", type=Path, required=True)
    ap.add_argument("--log", type=Path, required=True)
    ap.add_argument("--profile", choices=("full", "windows"), default="full")
    args = ap.parse_args()
    sys.path.insert(0, str(args.tests))
    sys.path.insert(0, str(HERE))
    from conformance.fixtures import cli, experiments, ops_runtime, write_request
    from real_env import backtest_request, collection_request, provision

    from stocks_predictor.research_contract import canonical
    from stocks_predictor.research_faults import PROCESS_DEATH_POINTS

    protocol = json.loads(args.protocol.read_text(encoding="utf-8"))
    matrix = json.loads(args.matrix.read_text(encoding="utf-8"))
    manifest = json.loads((args.build / "BUILD_MANIFEST.json").read_text(encoding="utf-8"))
    log = args.log.open("a", encoding="utf-8")

    def record(kind: str, **fields) -> dict:
        row = {"at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "kind": kind, **fields}
        log.write(json.dumps(row, sort_keys=True) + "\n")
        log.flush()
        return row

    env = provision(args.work / "main", args.build, protocol, matrix)
    as_of = env["as_of"]
    record("environment", profile=args.profile, real_env=env["env"], panel_sha256=manifest["panel"]["sha256"])
    expected_results: dict[str, str] = {}
    violations: list[str] = []

    def run(e, name: str, value: dict, *, fault: str | None = None) -> tuple[int, dict]:
        path = write_request(e, name, value)
        code, lines = cli(e, "process", str(path), fault=fault)
        outcome = lines[0] if lines else {}
        record("process", request_id=value["request_id"], fault=fault, exit=code,
               status=outcome.get("status"), result_id=outcome.get("result_id"),
               result_state=outcome.get("result_state"), operational_state=outcome.get("operational_state"),
               scientific_state=outcome.get("scientific_state"), economic_state=outcome.get("economic_state"),
               client_ref=outcome.get("client_ref"))
        return code, outcome

    normal = 20 if args.profile == "full" else 5
    for i in range(normal):
        rid = f"stocks:REQ-D16-SOAK-N-{i:03d}"
        code, outcome = run(env, f"n{i}", backtest_request(protocol, rid, as_of))
        if code != 0 or outcome.get("status") != "RESULT":
            violations.append(f"normal {rid}: {code} {outcome.get('status')}")
        expected_results[rid] = outcome.get("result_id")
        if i % 4 == 0 and i // 4 < 5:  # duplicatas (mesma chave, client_ref próprio devolvido)
            code, outcome = run(env, f"d{i}", backtest_request(protocol, rid, as_of, client_ref={"dup": i}))
            if code != 0 or outcome.get("status") != "DUPLICATE" or outcome.get("client_ref") != {"dup": i}:
                violations.append(f"duplicate {rid}: {code} {outcome.get('status')}")
        if args.profile == "windows" or (i % 4 == 1 and i // 4 < 5):  # restarts nos pontos de morte, em rodízio
            k = i if args.profile == "windows" else i // 4
            point = PROCESS_DEATH_POINTS[k % len(PROCESS_DEATH_POINTS)]
            rrid = f"stocks:REQ-D16-SOAK-R-{i:03d}"
            code, _ = run(env, f"r{i}", backtest_request(protocol, rrid, as_of), fault=point)
            code2, outcome = run(env, f"r{i}", backtest_request(protocol, rrid, as_of))
            if code != 86 or code2 != 0 or outcome.get("status") not in {"RESULT", "DUPLICATE"}:
                violations.append(f"restart {point}: {code}/{code2} {outcome.get('status')}")
            expected_results[rrid] = outcome.get("result_id")

    not_ready, collections = [], []
    if args.profile == "full":
        hang_env = provision(args.work / "hang", args.build, protocol, matrix,
                             timeout=protocol["policy"]["hang_env_timeout_seconds"])
        record("hang_environment", real_env=hang_env["env"])
        for k in range(3):  # classes de falha relevantes, 3 execuções cada
            rid = f"stocks:REQ-D16-SOAK-CRASH-{k}"
            code, outcome = run(env, f"c{k}", backtest_request(protocol, rid, as_of), fault="ops_worker_crash")
            if code != 3 or outcome.get("scientific_state") != "NOT_EVALUATED":
                violations.append(f"crash {rid}: {code}")
            code, outcome = run(env, f"c{k}", backtest_request(protocol, rid, as_of))
            expected_results[rid] = outcome.get("result_id")
            rid = f"stocks:REQ-D16-SOAK-HANG-{k}"
            code, outcome = run(hang_env, f"h{k}", backtest_request(protocol, rid, as_of), fault="ops_worker_hang")
            if code != 3 or outcome.get("operational_state") != "TIMEOUT":
                violations.append(f"hang {rid}: {code} {outcome.get('operational_state')}")
            code, outcome = run(hang_env, f"h{k}", backtest_request(protocol, rid, as_of))
            if code != 0:
                violations.append(f"hang retry {rid}: {code}")
            rid = f"stocks:REQ-D16-SOAK-ADM-{k}"
            code, _ = run(env, f"a{k}", backtest_request(protocol, rid, as_of), fault="before_admission_commit")
            code2, outcome = run(env, f"a{k}", backtest_request(protocol, rid, as_of))
            if code != 86 or code2 != 0:
                violations.append(f"before_admission_commit {rid}: {code}/{code2}")
            expected_results[rid] = outcome.get("result_id")
            rid = f"stocks:REQ-D16-SOAK-WRITE-{k}"
            code, _ = run(env, f"w{k}", backtest_request(protocol, rid, as_of), fault="during_result_write")
            code2, outcome = run(env, f"w{k}", backtest_request(protocol, rid, as_of))
            if code != 86 or code2 != 0:
                violations.append(f"during_result_write {rid}: {code}/{code2}")
            expected_results[rid] = outcome.get("result_id")
        for k in range(3):  # família não pronta: 0 trial
            rid = f"stocks:REQ-D16-SOAK-EI-{k}"
            value = backtest_request(protocol, rid, as_of, ei={"mode": "TRIAL_CONSUMPTION", "families": ["CVM_VLMO"]})
            code, outcome = run(env, f"ei{k}", value)
            not_ready.append(outcome.get("result_state"))
            if code != 0 or outcome.get("result_state") != "NOT_READY":
                violations.append(f"family-not-ready {rid}: {code} {outcome.get('result_state')}")
            expected_results[rid] = outcome.get("result_id")
        vlmo = next(s for s in manifest["sources"] if s["name"].startswith("vlmo_cia_aberta_"))
        observed_at = (vlmo.get("at") or manifest["data_cutoff"]).replace("+00:00", "Z")  # instante do download
        for k in range(5):  # coletas COLLECTION_ONLY com a fonte oficial
            rid = f"stocks:REQ-D16-SOAK-COLLECT-{k}"
            code, outcome = run(env, f"col{k}", collection_request(protocol, rid, observed_at))
            collections.append(outcome.get("result_state"))
            if code != 0 or outcome.get("result_state") != "COLLECTION_RECORDED":
                violations.append(f"collection {rid}: {code} {outcome.get('result_state')}")
            expected_results[rid] = outcome.get("result_id")
    record("stocks_profile", family_not_ready=not_ready, collections=collections)

    # checagens de tolerância zero
    results_db = env["state"] / "results.sqlite"
    with sqlite3.connect(results_db) as db:
        rows = db.execute("SELECT request_id,result_id FROM results").fetchall()
    stored = dict(rows)
    lost = [r for r, res in expected_results.items() if stored.get(r) != res]
    extra = [r for r in stored if r not in expected_results]
    effects = list(experiments(env).rglob("domain-effect.json"))
    per_job_success = {}
    for events in ops_runtime(env).glob("stocks-research-*/events.jsonl"):
        per_job_success[events.parent.name] = sum(
            1 for line in events.read_text(encoding="utf-8").splitlines()
            if line.strip() and json.loads(line).get("run_status") == "SUCCEEDED")
    reread_mismatch, eligible_trials, pit_violations = [], 0, []
    universe_by_session: dict[str, set[str]] = {}
    metrics_seen = set()
    for rid in expected_results:
        code, lines = cli(env, "show", rid)
        result = lines[0].get("result") if lines else None
        with sqlite3.connect(results_db) as db:
            row = db.execute("SELECT result FROM results WHERE request_id=?", (rid,)).fetchone()
        blob = bytes(row[0]) if row else None
        if code != 0 or result is None or blob is None or canonical(result) != blob:
            reread_mismatch.append(rid)
            continue
        if result.get("capital_permission") is not False or not all(
                str(result.get(f, "")).startswith("stocks:") for f in ("request_id", "result_id", "experiment_id", "admission_id")):
            violations.append(f"authority/ids {rid}")
        eligible_trials += int(bool(result.get("trial_eligible")))
        domain = result.get("domain_facts") or {}
        for reb in domain.get("rebalances") or []:
            if reb["decision_at"] > reb["session"] + "T12:00:00Z":
                pit_violations.append(rid)
            universe_by_session.setdefault(reb["session"], set()).add(reb["universe_identity_hash"])
        if domain.get("metrics") and domain.get("negative_control") is None and domain["metrics"].get("excess_gross_bps") is not None:
            metrics_seen.add(json.dumps(domain["metrics"], sort_keys=True))
    universe_contamination = sorted(s for s, hashes in universe_by_session.items() if len(hashes) != 1)
    code, lines = cli(env, "reconcile")
    store_ok = all(hashlib.sha256(p.read_bytes()).hexdigest() == p.name
                   for p in (env["objects"]).rglob("*") if p.is_file())
    summary = record(
        "summary",
        profile=args.profile,
        requests_with_result=len(expected_results),
        stored_results=len(stored),
        lost=lost,
        unexpected=extra,
        domain_effects=len(effects),
        ops_success_per_job_max=max(per_job_success.values()) if per_job_success else 0,
        ops_jobs=len(per_job_success),
        reread_mismatch=reread_mismatch,
        reconcile_exit=code,
        reconcile_findings=(lines[0].get("findings") if lines else None),
        violations=violations,
        eligible_trials=eligible_trials,
        pit_violations=pit_violations,
        rebalance_sessions_checked=len(universe_by_session),
        universe_contamination=universe_contamination,
        distinct_metrics_for_identical_requests=len(metrics_seen),
        operator_store_unchanged=store_ok,
    )
    ok = (not lost and not extra and not reread_mismatch and not violations and code == 0
          and eligible_trials == 0 and not pit_violations and not universe_contamination
          and summary["ops_success_per_job_max"] == 1 and len(effects) == len(stored)
          and len(metrics_seen) <= 1 and store_ok)
    record("verdict", zero_tolerance_ok=ok)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
