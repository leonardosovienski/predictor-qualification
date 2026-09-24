"""brasileirao / fase soak: executa QUALIFICATION_PROFILE_BR_V1 pelo entrypoint instalado.

Roda no runtime suportado (venv limpo só com as final_wheels). Usa os vetores congelados da suíte
de conformidade do final_commit (tests/conformance/fixtures.py, passado por --tests); cada chamada
ao `brasileirao-research` é um processo novo. Um JSON por linha no log bruto; ao fim, as checagens
de tolerância zero. Com vetores sintéticos é DIAGNÓSTICO enquanto a D-16 não for decidida.

Uso: python soak.py --tests <árvore tests/ do final_commit> --work <dir> --log <soak.jsonl>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
from contextlib import closing
import sys
import time
from pathlib import Path

PROFILE = {
    "normal_cycles": 20,
    "restarts": 5,
    "duplicate_requests": 5,
    "runs_per_relevant_failure_class": 3,
    "same_kickoff_cycles": 5,
    "out_of_order_dataset_cycles": 5,
    "future_canary_cycles": 5,
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tests", type=Path, required=True)
    ap.add_argument("--work", type=Path, required=True)
    ap.add_argument("--log", type=Path, required=True)
    args = ap.parse_args()
    sys.path.insert(0, str(args.tests))
    from conformance import fixtures
    from conformance.harness import cli, comparable, outcomes, standard_lab

    from brasileirao_predictor.research_runtime.contract import canonical
    from brasileirao_predictor.research_runtime.faults import FAULT_ENV, FAULT_EXIT, PROCESS_DEATH_POINTS

    args.work.mkdir(parents=True, exist_ok=True)
    log = args.log.open("a", encoding="utf-8")

    def record(kind: str, **fields) -> dict:
        row = {"at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "kind": kind, **fields}
        log.write(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n")
        log.flush()
        return row

    record("profile", **PROFILE)
    seeds = (11, 23, 37, 41, 53)
    lab = standard_lab(
        {"synthetic": {}, "canary": {"canary": True}, **{f"perm-{s}": {"permutation_seed": s} for s in seeds}}
    )
    hang = standard_lab(timeout_seconds=3)
    expected: dict[str, str] = {}
    violations: list[str] = []

    def run(target_lab, value: dict, *, fault: str | None = None) -> tuple[int, dict]:
        env = {FAULT_ENV: fault} if fault else None
        code, lines, _stderr = target_lab.process(target_lab.request_file(value), env=env)
        outcome = lines[-1] if lines else {}
        record("process", request_id=value["request_id"], fault=fault, exit=code, status=outcome.get("status"),
               result_id=outcome.get("result_id"), operational_state=outcome.get("operational_state"),
               scientific_state=outcome.get("scientific_state"), economic_state=outcome.get("economic_state"),
               reason=outcome.get("reason"))
        return code, outcome

    def shown(target_lab, rid: str) -> dict:
        code, payload = target_lab.show(rid)
        return payload.get("result") if code == 0 else {}

    windows = [("2023-06-01T00:00:00Z", "2023-07-01T00:00:00Z"), ("2023-07-01T00:00:00Z", "2023-08-01T00:00:00Z"),
               ("2023-08-01T00:00:00Z", fixtures.DATA_CUTOFF), ("2023-06-01T00:00:00Z", fixtures.DATA_CUTOFF)]
    # normal cycles, with duplicates and restarts interleaved
    for i in range(PROFILE["normal_cycles"]):
        rid = f"brasileirao:REQ-SOAK-N-{i:03d}"
        start, end = windows[i % len(windows)]
        target = "1X2" if i % 2 == 0 else "OU25"
        value = fixtures.request(rid, target=target, kickoff_from=start, kickoff_to=end)
        code, outcome = run(lab, value)
        if code != 0 or outcome.get("status") != "RESULT":
            violations.append(f"normal {rid}: {code} {outcome.get('status')}")
        expected[rid] = outcome.get("result_id")
        if i % 4 == 0 and i // 4 < PROFILE["duplicate_requests"]:
            code, dup = run(lab, value | {"client_ref": {"dup": i}})
            if code != 0 or dup.get("status") != "DUPLICATE" or dup.get("client_ref") != {"dup": i} or dup.get("result_id") != expected[rid]:
                violations.append(f"duplicate {rid}: {code} {dup.get('status')}")
        if i % 4 == 1 and i // 4 < PROFILE["restarts"]:
            point = PROCESS_DEATH_POINTS[(i // 4) * 2 % len(PROCESS_DEATH_POINTS)]
            rrid = f"brasileirao:REQ-SOAK-R-{i:03d}"
            restart = fixtures.request(rrid, target=target, kickoff_from=start, kickoff_to=end)
            code, _ = run(lab, restart, fault=point)
            code2, outcome = run(lab, restart)
            if code != FAULT_EXIT or code2 != 0 or outcome.get("status") not in {"RESULT", "DUPLICATE"}:
                violations.append(f"restart {point}: {code}/{code2} {outcome.get('status')}")
            expected[rrid] = outcome.get("result_id")

    # relevant failure classes, 3 runs each: worker crash, Ops timeout, death before the admission
    # commit, death during the result write
    for k in range(PROFILE["runs_per_relevant_failure_class"]):
        rid = f"brasileirao:REQ-SOAK-CRASH-{k}"
        code, outcome = run(lab, fixtures.request(rid), fault="ops_worker_crash")
        if code != 3 or outcome.get("scientific_state") != "NOT_EVALUATED" or outcome.get("operational_state") != "FAILED":
            violations.append(f"crash {rid}: {code}")
        code, outcome = run(lab, fixtures.request(rid))
        expected[rid] = outcome.get("result_id")
        if code != 0:
            violations.append(f"crash retry {rid}: {code}")
        rid = f"brasileirao:REQ-SOAK-HANG-{k}"
        code, outcome = run(hang, fixtures.request(rid), fault="ops_worker_hang")
        if code != 3 or outcome.get("operational_state") != "TIMEOUT" or outcome.get("scientific_state") != "NOT_EVALUATED":
            violations.append(f"hang {rid}: {code} {outcome.get('operational_state')}")
        rid = f"brasileirao:REQ-SOAK-ADM-{k}"
        code, _ = run(lab, fixtures.request(rid), fault="before_admission_commit")
        code2, outcome = run(lab, fixtures.request(rid))
        if code != FAULT_EXIT or code2 != 0:
            violations.append(f"before_admission_commit {rid}: {code}/{code2}")
        expected[rid] = outcome.get("result_id")
        rid = f"brasileirao:REQ-SOAK-WRITE-{k}"
        code, _ = run(lab, fixtures.request(rid), fault="during_result_write")
        code2, outcome = run(lab, fixtures.request(rid))
        if code != FAULT_EXIT or code2 != 0:
            violations.append(f"during_result_write {rid}: {code}/{code2}")
        expected[rid] = outcome.get("result_id")

    base = comparable(shown(lab, "brasileirao:REQ-SOAK-N-003"))  # 2023-06-01 → cutoff, 1X2? (i=3: OU25)
    # same-kickoff cycles: listed pairs of games that share a kickoff
    pairs = {}
    for e in fixtures.fixtures():
        if e["season"] == 2023 and 6 <= e["kickoff"].month <= 9 and e["superseded_by"] is None and e["slot"] in (0, 1):
            pairs.setdefault(e["kickoff"], []).append(e)
    same = [v for v in pairs.values() if len(v) == 2][: PROFILE["same_kickoff_cycles"]]
    for k, (a, b) in enumerate(same):
        listed = [{"event_id": x["event_id"], "kickoff_at": x["kickoff"].strftime("%Y-%m-%dT%H:%M:%SZ")} for x in (a, b)]
        rid = f"brasileirao:REQ-SOAK-SAMEKO-{k}"
        code, outcome = run(lab, fixtures.request(rid, fixtures_list=listed, odds=False))
        result = shown(lab, rid)
        preds = result.get("domain_facts", {}).get("predictions", [])
        if code != 0 or len(preds) != 2 or preds[0]["information_fingerprint"] != preds[1]["information_fingerprint"]:
            violations.append(f"same kickoff {rid}: information sets differ or missing")
        expected[rid] = outcome.get("result_id")
    # out-of-order dataset cycles: 5 insertion-order permutations must give the same result
    reference = comparable(shown(lab, "brasileirao:REQ-SOAK-N-003"))
    for seed in seeds[: PROFILE["out_of_order_dataset_cycles"]]:
        rid = f"brasileirao:REQ-SOAK-PERM-{seed}"
        start, end = windows[3]
        code, outcome = run(lab, fixtures.request(rid, target="OU25", kickoff_from=start, kickoff_to=end, dataset=f"perm-{seed}"))
        if code != 0 or comparable(shown(lab, rid)) != reference:
            violations.append(f"permutation {seed}: result differs")
        expected[rid] = outcome.get("result_id")
    # future canary cycles
    for k in range(PROFILE["future_canary_cycles"]):
        rid = f"brasileirao:REQ-SOAK-CANARY-{k}"
        start, end = windows[3]
        code, outcome = run(lab, fixtures.request(rid, target="OU25", kickoff_from=start, kickoff_to=end, dataset="canary"))
        if code != 0 or comparable(shown(lab, rid)) != reference:
            violations.append(f"canary {rid}: result differs from the canary-free reference")
        expected[rid] = outcome.get("result_id")
    del base
    leaked = [str(p) for p in lab.state.rglob("*") if p.is_file() and p.suffix in {".json", ".jsonl", ".sqlite"}
              and fixtures.CANARY.encode() in p.read_bytes()]
    if leaked:
        violations.append(f"FUTURE_CANARY found in {leaked[:5]}")

    # zero-tolerance checks
    with closing(sqlite3.connect(lab.state / "results.sqlite")) as db, db:
        rows = db.execute("SELECT request_id,result_id,content_hash,result FROM results").fetchall()
    stored = {r: res for r, res, _h, _b in rows}
    lost = [r for r, res in expected.items() if stored.get(r) != res]
    extra = [r for r in stored if r not in expected]
    effects = list((lab.state / "x" / "e").rglob("domain-effect.json"))
    per_job_success = {}
    for events in (lab.state / "x" / "o").glob("brasileirao-research-*/events.jsonl"):
        per_job_success[events.parent.name] = sum(
            1 for line in events.read_text(encoding="utf-8").splitlines() if line.strip() and json.loads(line).get("run_status") == "SUCCEEDED"
        )
    reread_mismatch = []
    blobs = {r: bytes(b) for r, _res, _h, b in rows}
    for rid in expected:
        result = shown(lab, rid)
        if not result or canonical(result) != blobs.get(rid):
            reread_mismatch.append(rid)
        if result and (result.get("capital_permission") is not False or not all(
            str(result.get(f, "")).startswith("brasileirao:") for f in ("request_id", "result_id", "experiment_id", "admission_id"))):
            violations.append(f"authority/ids {rid}")
    reconcile = cli("--state", str(lab.state), "reconcile")
    summary = record(
        "summary",
        requests_with_result=len(expected),
        stored_results=len(stored),
        lost=lost,
        unexpected=extra,
        domain_effects=len(effects),
        ops_success_per_job_max=max(per_job_success.values()) if per_job_success else 0,
        ops_jobs=len(per_job_success),
        reread_mismatch=reread_mismatch,
        reconcile_exit=reconcile.returncode,
        reconcile_findings=json.loads(reconcile.stdout).get("findings") if reconcile.stdout.startswith("{") else reconcile.stdout[-500:],
        violations=violations,
        effects_sha256=sorted(hashlib.sha256(p.read_bytes()).hexdigest()[:16] for p in effects)[:5],
    )
    ok = (not lost and not extra and not reread_mismatch and not violations and reconcile.returncode == 0
          and summary["ops_success_per_job_max"] == 1 and len(effects) == len(stored))
    record("verdict", zero_tolerance_ok=ok)
    del outcomes
    lab.cleanup()
    hang.cleanup()
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
