"""brasileirao / fase e2e: circuito inteiro pelo entrypoint instalado, com prova de provenance.

pedido em arquivo → `brasileirao-research process` (processo 1, termina) → `brasileirao-research show`
(processo 2, novo) → mesmo resultado byte a byte; depois a cadeia de provenance é conferida contra
as fontes primárias: recibo da admission (SQLite), journal, registro de trials do Core, eventos do
Ops (jobs file v3 + CLI), efeito de domínio e ResultStore.

Sintético (--tests): laboratório da suíte de conformidade (diagnóstico no Linux enquanto D-16 pende).
Real (--real): a instalação do real_env.py (state, policy e objects do dado real).

Uso: python e2e_runtime.py --tests <árvore tests/> --work <dir> --out <dir de evidência>
     [--real-state S --real-policy P --real-objects O --real-request R]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import subprocess
import sys
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tests", type=Path, required=True)
    ap.add_argument("--work", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--real-state", type=Path)
    ap.add_argument("--real-policy", type=Path)
    ap.add_argument("--real-objects", type=Path)
    ap.add_argument("--real-request", type=Path)
    args = ap.parse_args()
    sys.path.insert(0, str(args.tests))
    from conformance import fixtures
    from conformance.harness import SCRIPT, Lab, cli, outcomes, standard_lab

    args.out.mkdir(parents=True, exist_ok=True)
    checks: list[dict] = []

    def check(name: str, ok: bool, **detail) -> None:
        checks.append({"check": name, "ok": bool(ok), **detail})

    if args.real_request:
        lab = Lab(args.work)
        state, policy, objects, request_path = args.real_state, args.real_policy, args.real_objects, args.real_request
        request_id = json.loads(request_path.read_text(encoding="utf-8"))["request_id"]
        mode = "real"
    else:
        args.work.mkdir(parents=True, exist_ok=True)
        lab = standard_lab()
        state, policy, objects = lab.state, lab.policy_path, lab.objects
        request_id = "brasileirao:REQ-E2E-RUNTIME-001"
        request_path = lab.request_file(fixtures.request(request_id, client_ref={"e2e": 1}))
        mode = "synthetic"

    done = cli("--state", str(state), "process", "--policy", str(policy), "--objects", str(objects), str(request_path))
    (args.out / "process_1.stdout.jsonl").write_text(done.stdout, encoding="utf-8")
    (args.out / "process_1.stderr.log").write_text(done.stderr, encoding="utf-8")
    first = outcomes(done)[-1]
    check("process_1_exit_0", done.returncode == 0, exit=done.returncode, status=first.get("status"))
    shown = cli("--state", str(state), "show", request_id)
    (args.out / "show_2.stdout.json").write_text(shown.stdout, encoding="utf-8")
    payload = json.loads(shown.stdout)
    result = payload.get("result") or {}
    check("restart_reread_exit_0", shown.returncode == 0, exit=shown.returncode)
    check("reread_is_authoritative_store", payload.get("source") == "authoritative_result_store")
    check("reread_same_result_id", result.get("result_id") == first.get("result_id"))
    again = cli("--state", str(state), "show", request_id)
    check("reread_byte_identical", json.loads(again.stdout).get("result_sha256") == payload.get("result_sha256"))
    duplicate = cli("--state", str(state), "process", "--policy", str(policy), "--objects", str(objects), str(request_path))
    dup = outcomes(duplicate)[-1]
    check("duplicate_returns_same_result", dup.get("status") == "DUPLICATE" and dup.get("result_id") == first.get("result_id"))

    # --- provenance chain against primary sources
    with sqlite3.connect(state / "admission.sqlite") as db:
        receipt = db.execute(
            "SELECT admission_id, decision, policy_hash, content_hash FROM admissions WHERE request_id=? AND decision='ACCEPTED'",
            (request_id,),
        ).fetchone()
    check("admission_receipt", receipt is not None and receipt[0] == result.get("admission_id") and receipt[2] == result["provenance"]["admission_policy_hash"])
    check("request_content_hash", receipt is not None and receipt[3] == result["provenance"]["request_content_hash"])
    with sqlite3.connect(state / "x" / "journal.sqlite") as db:
        exp = db.execute("SELECT experiment_id, state, effect_hash, result_hash, ops_run_id, logical_hash FROM experiments WHERE request_id=?", (request_id,)).fetchone()
        transitions = [r[0] for r in db.execute("SELECT state FROM transitions WHERE experiment_id=? ORDER BY sequence", (exp[0],))]
    check("journal_completed", exp is not None and exp[1] == "COMPLETED", transitions=transitions)
    check("journal_experiment_matches_result", exp[0] == result.get("experiment_id"))
    work = state / "x" / "e" / exp[5][:16]
    effect = work / "domain-effect.json"
    effect_sha = hashlib.sha256(effect.read_bytes()).hexdigest()
    check("effect_hash_journal_result", effect_sha == exp[2] == result["domain_facts"]["effect_sha256"])
    result_file = work / "research-result.json"
    check("result_file_hash", hashlib.sha256(result_file.read_bytes()).hexdigest() == exp[3] == payload.get("result_sha256"))
    trials = json.loads((work / "trials-v2.json").read_text(encoding="utf-8"))
    check("core_trial_registered_once", len(trials) == 1 and trials[0]["trial_id"] == result["core_facts"]["trial_ids"][0])
    check("core_trial_state_is_result_state", trials[0]["status"] == result["scientific_state"])
    events = [json.loads(x) for p in (state / "x" / "o").glob("*/events.jsonl") for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]
    mine = [e for e in events if (e.get("provenance") or {}).get("request_id") == request_id]
    successes = [e for e in mine if e.get("run_status") == "SUCCEEDED"]
    check("ops_single_success", len(successes) == 1, ops_records=len(mine))
    ok_ops = successes[0] if successes else {}
    check("ops_run_id_matches", ok_ops.get("run_id") == result["ops_facts"]["ops_run_id"] == exp[4])
    check("ops_job_type_forecast_generation", ok_ops.get("job_type") == "FORECAST_GENERATION")
    check("ops_strict_wheel_provenance", (ok_ops.get("library_provenance") or {}).get("mode") == "strict" and ok_ops["library_provenance"].get("kind") == "wheel")
    check("ops_heartbeat_recorded", bool(ok_ops.get("heartbeat_at")) or (state / "x" / "o" / ok_ops.get("job_id", "?") / "heartbeat.json").exists())
    check("ops_economic_lock", bool(ok_ops.get("economic_lock_id")))
    jobs = sorted(work.glob("ops-job.*.json"))
    job = json.loads(jobs[-1].read_text(encoding="utf-8"))["jobs"][0] if jobs else {}
    check("jobs_file_v3_module_command", job.get("command", [None, None, None])[1:3] == ["-m", "brasileirao_predictor.research_runtime.worker"])
    check("jobs_file_strict_no_capital", job.get("provenance_mode") == "strict" and job.get("capital_permission") is False and job.get("job_type") == "FORECAST_GENERATION")
    check("capital_permission_false", result.get("capital_permission") is False)
    check("ids_qualified", all(str(result.get(k, "")).startswith("brasileirao:") for k in ("result_id", "request_id", "admission_id", "experiment_id")))
    audit = result["core_facts"]["temporal_validation"]
    check("temporal_replay_strict", audit["engine"] == "predictor_core.measurement.replay" and audit["max_used_minus_cutoff_seconds"] < 0 and audit["db_caches_read"] == [])
    if mode == "synthetic":
        check("client_ref_echoed", first.get("client_ref") == {"e2e": 1})
    summary = {
        "mode": mode,
        "request_id": request_id,
        "result_id": result.get("result_id"),
        "result_state": result.get("result_state"),
        "scientific_state": result.get("scientific_state"),
        "economic_state": result.get("economic_state"),
        "script": str(SCRIPT),
        "checks_total": len(checks),
        "checks_ok": sum(1 for c in checks if c["ok"]),
        "checks": checks,
    }
    (args.out / "E2E_SUMMARY.json").write_text(json.dumps(summary, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: summary[k] for k in ("mode", "checks_total", "checks_ok", "result_state")}))
    if mode == "synthetic":
        lab.cleanup()
    return 0 if summary["checks_ok"] == summary["checks_total"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
