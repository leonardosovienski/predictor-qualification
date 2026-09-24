"""stocks / fase e2e: circuito inteiro pelo entrypoint instalado, com prova de provenance.

pedido em arquivo → `stocks-research process` (processo 1, termina) → `stocks-research show`
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

    from stocks_predictor.research_contract import canonical

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
        request_id = "stocks:REQ-E2E-RUNTIME-001"
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
    events = [json.loads(line) for events_file in ops_runtime(env).glob("stocks-research-*/events.jsonl")
              for line in events_file.read_text(encoding="utf-8").splitlines() if line.strip()]
    ops = [e for e in events if e.get("run_id") == result["ops_facts"]["ops_run_id"]]
    check("Ops terminal event produced by predictor_ops", len(ops) == 1 and ops[0]["run_status"] == "SUCCEEDED"
          and ops[0]["service"] == "predictor_ops" and ops[0]["economic_lock_id"] == result["ops_facts"]["economic_lock_id"]
          and ops[0].get("heartbeat_at") is not None, ops_event_keys=sorted(ops[0]) if ops else None)
    check("identities of installed wheels in the result", all(result[b]["identity"]["version"] for b in
          ("core_facts", "ops_facts", "domain_facts")),
          identities={b: result[b]["identity"] for b in ("core_facts", "ops_facts", "domain_facts")})
    check("capital_permission false and domain-qualified ids", result["capital_permission"] is False and all(
        str(result[f]).startswith("stocks:") for f in ("request_id", "admission_id", "experiment_id", "result_id",
                                                        "research_id", "hypothesis_id")))
    if not args.real:
        check("client_ref echoed unchanged", outcome.get("client_ref") == {"e2e": 1})

    cases = []
    if not args.real:
        for k in range(3):
            for case, dataset in (("A", "case_a"), ("B", "case_b")):
                rid = f"stocks:REQ-E2E-CASE{case}-{k}"
                code, lines = cli(env, "process", str(write_request(env, f"case{case}{k}", request(rid, dataset=dataset))))
                o = lines[0]
                cases.append({"case": case, "cycle": k, "exit": code, "operational": o.get("operational_state"),
                              "scientific": o.get("scientific_state"), "economic": o.get("economic_state"),
                              "result_state": o.get("result_state")})
            rid = f"stocks:REQ-E2E-CASEC-{k}"
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
    domain = {}
    if not args.real:
        from conformance.fixtures import collection_request

        # STOCKS_UNIVERSE_IDENTITY through the entrypoint: same request, three fresh state roots
        hashes = []
        for k in range(3):
            fresh = build(args.work / f"u{k}")
            rid = "stocks:REQ-E2E-UNIVERSE-001"
            code, lines = cli(fresh, "process", str(write_request(fresh, "u", request(rid))))
            stored = json.loads(Path(lines[0]["outcome_file"]).read_text(encoding="utf-8"))["result"]
            hashes.append([r["universe_identity_hash"] for r in stored["domain_facts"]["rebalances"]])
        check("universe identical across three fresh processes/state roots", len({json.dumps(h) for h in hashes}) == 1
              and len(hashes[0]) > 0, rebalances=len(hashes[0]))
        domain["universe_hashes_first_run"] = hashes[0]
        # External Intelligence: TRIAL_CONSUMPTION of NOT_READY families, 3x
        ei_cases = []
        for k in range(3):
            value = request(f"stocks:REQ-E2E-EI-{k}")
            value["parameters"]["external_intelligence"] = {"mode": "TRIAL_CONSUMPTION", "families": ["CVM_VLMO", "B3_LENDING"]}
            code, lines = cli(env, "process", str(write_request(env, f"ei{k}", value)))
            stored = json.loads(Path(lines[0]["outcome_file"]).read_text(encoding="utf-8"))["result"]
            ei = stored["domain_facts"]["external_intelligence"]
            ei_cases.append({"exit": code, "result_state": stored["result_state"], "trial_ids": stored["core_facts"]["trial_ids"],
                             "consumed": ei["consumed_families"],
                             "reasons": {f: v["reason"] for f, v in ei["decisions"].items()}})
        check("NOT_READY family never becomes a trial (3x)", all(c["result_state"] == "NOT_READY" and not c["trial_ids"]
              and not c["consumed"] for c in ei_cases), cases=ei_cases)
        # COLLECTION_ONLY through the entrypoint
        code, lines = cli(env, "process", str(write_request(env, "col", collection_request("stocks:REQ-E2E-COLLECT-001"))))
        stored = json.loads(Path(lines[0]["outcome_file"]).read_text(encoding="utf-8"))["result"]
        check("COLLECTION_ONLY collected and never feeds a trial", code == 0 and stored["result_state"] == "COLLECTION_RECORDED"
              and stored["domain_facts"]["collection_status"] == "SUCCESS" and stored["trial_eligible"] is False
              and not any(stored["domain_facts"]["feeds"].values()), collection_status=stored["domain_facts"]["collection_status"])
        # FUTURE_CANARY through the entrypoint
        code, lines = cli(env, "process", str(write_request(env, "canary", request("stocks:REQ-E2E-CANARY-001", dataset="future_canary"))))
        check("future canary fails closed (exit 4, LookaheadError)", code == 4 and "LookaheadError" in lines[0].get("reason", ""))
        domain["main_result_metrics"] = result["domain_facts"].get("metrics")
    summary = {"request_id": request_id, "checks": checks, "cases": cases, "domain": domain,
               "all_ok": all(c["ok"] for c in checks)}
    (args.out / "E2E_SUMMARY.json").write_text(json.dumps(summary, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"all_ok": summary["all_ok"], "failed": [c["check"] for c in checks if not c["ok"]]}))
    return 0 if summary["all_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
