"""crypto / fase e2e: circuito inteiro pelo entrypoint instalado, com prova de provenance.

pedido em arquivo → `cripto-research process` (processo 1, termina) → `cripto-research show`
(processo 2, novo) → mesmo resultado byte a byte; depois, a cadeia de provenance é conferida
contra as fontes primárias: recibo da admission (SQLite), journal, registro de trials do Core,
eventos do Ops, efeito de domínio e ResultStore. Casos A/B/C 3× cada (AUTHORITY_STATE_MATRIX).

Uso: python e2e_runtime.py --tests <árvore tests/> --work <dir> --out <dir de evidência>
     [--real <dir com policy.json/objects/requests do real_env.py>]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import sys
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tests", type=Path, required=True)
    ap.add_argument("--work", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--real", type=Path)
    args = ap.parse_args()
    sys.path.insert(0, str(args.tests))
    from conformance.fixtures import build, cli, experiments, ops_runtime, request, write_request

    from GarimpoInvestimentos.research_contract import canonical

    args.out.mkdir(parents=True, exist_ok=True)
    checks: list[dict] = []

    def check(name: str, ok: bool, **detail) -> None:
        checks.append({"check": name, "ok": bool(ok), **detail})

    if args.real:
        env = {"root": args.real, "policy": args.real / "policy.json", "objects": args.real / "objects",
               "state": args.work / "s", "requests": args.real / "requests"}
        main_request = args.real / "requests" / "e2e.json"
        request_id = json.loads(main_request.read_text(encoding="utf-8"))["request_id"]
    else:
        env = build(args.work)
        request_id = "crypto:REQ-E2E-RUNTIME-001"
        main_request = write_request(env, "e2e", request(request_id, client_ref={"e2e": 1}))

    code1, lines1 = cli(env, "process", str(main_request))
    outcome = lines1[0]
    (args.out / "process_stdout.json").write_text(json.dumps(outcome, indent=1, ensure_ascii=False), encoding="utf-8")
    written = json.loads(Path(outcome["outcome_file"]).read_text(encoding="utf-8"))
    (args.out / "outcome_file.json").write_text(json.dumps(written, indent=1, ensure_ascii=False), encoding="utf-8")
    check("process exit 0 and RESULT", code1 == 0 and outcome["status"] == "RESULT", exit=code1, status=outcome["status"])
    result = written["result"]
    code2, lines2 = cli(env, "show", request_id)
    shown = lines2[0]
    (args.out / "show_new_process.json").write_text(json.dumps(shown, indent=1, ensure_ascii=False), encoding="utf-8")
    check("new process rereads the same result byte-for-byte",
          code2 == 0 and canonical(shown["result"]) == canonical(result),
          sha256=hashlib.sha256(canonical(result)).hexdigest())

    state = env["state"]
    with sqlite3.connect(state / "admission.sqlite") as db:
        adm = db.execute("SELECT admission_id,decision,policy_hash,content_hash FROM admissions WHERE request_id=? "
                         "AND decision='ACCEPTED'", (request_id,)).fetchone()
    check("admission receipt matches result", adm is not None and adm[0] == result["admission_id"]
          and adm[2] == result["provenance"]["admission_policy_hash"]
          and adm[3] == result["provenance"]["request_content_hash"], admission=adm)
    with sqlite3.connect(state / "x" / "journal.sqlite") as db:
        exp = db.execute("SELECT experiment_id,state,effect_hash,result_hash,ops_run_id FROM experiments WHERE request_id=?",
                         (request_id,)).fetchone()
        attempts = db.execute("SELECT attempt_id,ops_run_id,state FROM attempts WHERE experiment_id=?",
                              (exp[0],)).fetchall()
    check("journal experiment completed and linked", exp is not None and exp[0] == result["experiment_id"]
          and exp[1] == "COMPLETED" and exp[4] == result["ops_facts"]["ops_run_id"], journal=exp)
    check("attempt ids match", sorted(a[0] for a in attempts) == sorted(result["ops_facts"]["attempt_ids"]))
    work = next(p for p in experiments(env).iterdir() if (p / "research-result.json").exists()
                and json.loads((p / "research-result.json").read_text(encoding="utf-8"))["request_id"] == request_id)
    effect_sha = hashlib.sha256((work / "domain-effect.json").read_bytes()).hexdigest()
    check("effect bytes match journal and result", effect_sha == exp[2] == result["domain_facts"]["effect_sha256"])
    trials = json.loads((work / "trials-v2.json").read_text(encoding="utf-8")) if (work / "trials-v2.json").exists() else []
    trial = next((t for t in trials if t["trial_id"] in result["core_facts"]["trial_ids"]), None)
    check("Core trial registry holds the trial and the scientific state", trial is not None
          and trial["status"] == result["scientific_state"] and trial["experiment_id"] == result["experiment_id"])
    events = [json.loads(line) for events_file in ops_runtime(env).glob("crypto-research-*/events.jsonl")
              for line in events_file.read_text(encoding="utf-8").splitlines() if line.strip()]
    ops = [e for e in events if e.get("run_id") == result["ops_facts"]["ops_run_id"]]
    check("Ops terminal event produced by predictor_ops", len(ops) == 1 and ops[0]["run_status"] == "SUCCEEDED"
          and ops[0]["service"] == "predictor_ops" and ops[0]["economic_lock_id"] == result["ops_facts"]["economic_lock_id"]
          and ops[0].get("heartbeat_at") is not None, ops_event_keys=sorted(ops[0]) if ops else None)
    check("identities of installed wheels in the result", all(result[b]["identity"]["version"] for b in
          ("core_facts", "ops_facts", "domain_facts")),
          identities={b: result[b]["identity"] for b in ("core_facts", "ops_facts", "domain_facts")})
    check("capital_permission false and domain-qualified ids", result["capital_permission"] is False and all(
        str(result[f]).startswith("crypto:") for f in ("request_id", "admission_id", "experiment_id", "result_id",
                                                        "research_id", "hypothesis_id")))
    if not args.real:
        check("client_ref echoed unchanged", outcome.get("client_ref") == {"e2e": 1})

    cases = []
    if not args.real:
        for k in range(3):
            for case, dataset in (("A", "case_a"), ("B", "case_b")):
                rid = f"crypto:REQ-E2E-CASE{case}-{k}"
                code, lines = cli(env, "process", str(write_request(env, f"case{case}{k}", request(rid, dataset=dataset))))
                o = lines[0]
                cases.append({"case": case, "cycle": k, "exit": code, "operational": o.get("operational_state"),
                              "scientific": o.get("scientific_state"), "economic": o.get("economic_state"),
                              "result_state": o.get("result_state")})
            rid = f"crypto:REQ-E2E-CASEC-{k}"
            path = write_request(env, f"caseC{k}", request(rid))
            code, lines = cli(env, "process", str(path), fault="ops_worker_crash")
            o = lines[0]
            cases.append({"case": "C", "cycle": k, "exit": code, "operational": o.get("operational_state"),
                          "scientific": o.get("scientific_state"), "economic": o.get("economic_state"),
                          "status": o.get("status")})
        want = {"A": ("SUCCEEDED", "INCONCLUSIVE", "NO_EDGE"), "B": ("SUCCEEDED", "SUPPORTED", "NO_EDGE"),
                "C": ("FAILED", "NOT_EVALUATED", "NOT_EVALUATED")}
        for c in cases:
            check(f"case {c['case']} cycle {c['cycle']}", (c["operational"], c["scientific"], c["economic"]) == want[c["case"]], **c)
    summary = {"request_id": request_id, "checks": checks, "cases": cases,
               "all_ok": all(c["ok"] for c in checks)}
    (args.out / "E2E_SUMMARY.json").write_text(json.dumps(summary, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"all_ok": summary["all_ok"], "failed": [c["check"] for c in checks if not c["ok"]]}))
    return 0 if summary["all_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
