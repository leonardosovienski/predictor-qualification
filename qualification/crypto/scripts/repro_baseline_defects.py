"""Reprodução, no commit de baseline 5fd4e1b, dos defeitos do domínio achados no truth-map.

Roda no venv do clone (checkout em 5fd4e1b) — diagnóstico, para preservar a prova antes da
correção (princípios §6). Cada caso imprime OBSERVED/EXPECTED e DEFECT_REPRODUCED true|false.

D1 AdmissionStore: max_pending_tasks conta todo ACCEPTED para sempre.
D2 research_worker.evaluate: net_return_bps ≠ média do CostModel.net_return (2 pernas + funding);
   nenhum IC do líquido.
"""

from __future__ import annotations

import json
import sys
import tempfile
from datetime import UTC, datetime, timedelta
from pathlib import Path

from predictor_core.contracts.trial_v2 import dataset_fingerprint
from research_protocol import sign_task

from GarimpoInvestimentos.research_admission import AdmissionStore
from GarimpoInvestimentos.research_worker import evaluate
from GarimpoInvestimentos.v3.costs import CostModel

SECRET = bytes.fromhex("42" * 32)
SCOPE = "crypto.research.propose"


def d1(tmp: Path) -> dict:
    registry = [{"kind": k, "name": k, "version": "v1", "revision_id": f"{k}:r1",
                 "content_hash": f"{i + 1:064x}", "scopes": [SCOPE]}
                for i, k in enumerate(["protocol", "dataset", "baseline", "cost_model", "evidence"])]
    policy = {
        "schema_version": "CryptoResearchAdmissionPolicyV1", "policy_id": "p", "policy_version": 1,
        "owner": "CRIPTO_OPERATOR",
        "publishers": [{"publisher_identity": "cain-qa", "key_id": "k", "scopes": [SCOPE], "revoked": False}],
        "handlers": {"BACKTEST_EXISTING_HYPOTHESIS": "crypto.handlers.backtest_existing_hypothesis.v1"},
        "registry": registry,
        "limits": {"max_pending_tasks": 2, "max_task_bytes": 16384, "max_refs": 8, "max_parameter_bytes": 1024,
                   "rate_limit_per_minute": 100, "max_concurrency": 1, "cpu_seconds": 60, "memory_mb": 512,
                   "disk_mb": 128, "timeout_seconds": 60, "max_retries": 2, "dead_letter_threshold": 3,
                   "max_age_seconds": 86400, "per_publisher_pending": 100, "max_priority": "NORMAL"},
        "allowed_symbols": ["BTCUSDT"],
    }
    path = tmp / "policy.json"
    path.write_text(json.dumps(policy), encoding="utf-8")
    store = AdmissionStore(tmp / "admission.db", path, keys={("cain-qa", "k"): SECRET})
    now = datetime.now(UTC)
    decisions = []
    for n in range(3):
        ref = lambda kind: {"kind": kind, "name": kind, "version": "v1"}
        task = {
            "schema_version": "ResearchTaskV1", "task_id": f"TASK-{n}", "research_id": "R", "parent_task_id": None,
            "hypothesis_id": "HX", "domain": "crypto", "request_type": "BACKTEST_EXISTING_HYPOTHESIS",
            "protocol_ref": ref("protocol"), "dataset_constraint_ref": ref("dataset"), "baseline_refs": [ref("baseline")],
            "cost_model_ref": ref("cost_model"), "evidence_refs": [ref("evidence")],
            "bounded_parameters": {"symbol": "BTCUSDT", "horizon_days": 7, "max_observations": 100, "fee_bps": 10, "slippage_bps": 5},
            "priority_hint": "NORMAL", "created_at": now.isoformat().replace("+00:00", "Z"),
            "expires_at": (now + timedelta(hours=1)).isoformat().replace("+00:00", "Z"), "requested_by": "repro",
            "provenance": {"cain_source_sha": "1" * 40, "retrieval_receipt_ids": ["r"], "proposal_model": "fixture"},
        }
        env = sign_task(task, producer="CAIN", publisher_identity="cain-qa", consumer="CRIPTO", scope=SCOPE, key_id="k", secret=SECRET)
        receipt = store.submit(env)
        decisions.append((receipt["decision"], receipt["reason_code"]))
    has_release_api = any(hasattr(store, name) for name in ("complete", "mark_terminal", "release"))
    return {"case": "D1", "decisions": decisions, "admission_store_has_completion_api": has_release_api,
            "DEFECT_REPRODUCED": decisions[2] == ("REJECTED", "GLOBAL_PENDING_QUOTA") and not has_release_api,
            "note": "sem API de conclusão, os 2 primeiros ACCEPTED ocupam a cota para sempre"}


def d2(tmp: Path) -> dict:
    cutoff = datetime(2026, 8, 31, tzinfo=UTC)
    rows = []
    for i in range(30):
        observed = cutoff - timedelta(days=7 * (30 - i))
        rows.append({"observed_at": observed.isoformat().replace("+00:00", "Z"),
                     "available_at": (observed + timedelta(minutes=1)).isoformat().replace("+00:00", "Z"),
                     "gross_return": 0.002 if i % 2 else 0.001, "funding_rate": 0.0001})
    objects = {
        "protocol": {"handler": "crypto.handlers.backtest_existing_hypothesis.v1", "minimum_sample": 20, "turnover_bps": 100,
                     "hypothesis_family": "f", "feature_version": "fv", "model_version": "mv",
                     "selection_path": {"family": "f", "candidate_set": ["mv"], "selection_metric": "predeclared", "selected_candidate": "mv"}},
        "dataset": {"dataset_version": "d", "data_cutoff": cutoff.isoformat().replace("+00:00", "Z"),
                    "label_start": rows[0]["observed_at"], "label_end": rows[-1]["available_at"],
                    "row_fingerprint": dataset_fingerprint(rows, fields=("observed_at", "available_at", "gross_return", "funding_rate")), "rows": rows},
        "baseline": {"baseline_id": "B", "gross_return_bps": 0, "net_return_bps": 0},
        "cost_model": {"fee_bps": 10, "slippage_bps": 5},
        "evidence": {"receipt_id": "E"},
    }
    refs = []
    for kind, value in objects.items():
        p = tmp / f"{kind}.json"
        p.write_text(json.dumps(value), encoding="utf-8")
        refs.append({"kind": kind, "path": str(p)})
    params = {"symbol": "BTCUSDT", "horizon_days": 7, "max_observations": 100, "fee_bps": 10, "slippage_bps": 5}
    request = {"schema": "crypto-admitted-backtest/1", "experiment_id": "EXP-X", "trial_id": "TRIAL-X",
               "task": {"request_type": "BACKTEST_EXISTING_HYPOTHESIS", "hypothesis_id": "HX", "bounded_parameters": params},
               "references": refs, "identities": {k: "0" * 64 for k in objects}, "registered_at": "2026-09-01T00:00:00Z",
               "code_version": "crypto:repro"}
    effect = evaluate(request)
    costs = CostModel(10.0, 5.0)
    net = [costs.net_return(r["gross_return"], 1.0, r["funding_rate"], 7 * 24.0) for r in rows]
    expected_net_bps = round(sum(net) / len(net) * 10_000)
    observed = effect["metrics"]["net_return_bps"]
    return {"case": "D2", "gross_return_bps": effect["metrics"]["gross_return_bps"],
            "reported_net_return_bps": observed, "costmodel_net_return_bps": expected_net_bps,
            "reported_total_cost_bps": effect["costs"]["total_cost_bps"],
            "metrics_keys": sorted(effect["metrics"]),
            "net_ci_present": any(k.startswith("net_ci") for k in effect["metrics"]),
            "DEFECT_REPRODUCED": observed != expected_net_bps}


def main() -> None:
    out = []
    with tempfile.TemporaryDirectory(dir=sys.argv[1] if len(sys.argv) > 1 else None) as raw:
        tmp = Path(raw)
        (tmp / "d1").mkdir()
        (tmp / "d2").mkdir()
        out.append(d1(tmp / "d1"))
        out.append(d2(tmp / "d2"))
    for item in out:
        print(json.dumps(item, sort_keys=True))


if __name__ == "__main__":
    main()
