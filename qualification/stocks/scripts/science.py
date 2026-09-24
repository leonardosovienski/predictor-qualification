"""stocks / fase pit-universe-canary-negative: controles negativos e prontidão de External Intelligence.

Roda no runtime suportado (wheel instalada), pelo entrypoint `stocks-research`, com os
vetores congelados da suíte de conformidade do final_commit (--tests). Até a D-16, o
painel é a fixture sintética congelada: o resultado é DIAGNÓSTICO (FROZEN_PARAMETERS
d16_dependency_rule), nunca PASS de STOCKS_NEGATIVE_CONTROLS.

Saídas (em --out): negative_controls.jsonl (uma linha por execução, bruta),
NEGATIVE_CONTROLS_SUMMARY.json, external_intelligence_readiness.json (classificação da
matriz congelada pelo research_readiness da wheel instalada).

Uso: python science.py --tests <árvore tests/> --work <dir> --out <dir> --matrix <matriz.json>
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SEEDS = [101, 202, 303, 404, 505, 606, 707, 808, 909, 1010, 1111, 1212, 1313, 1414, 1515, 1616, 1717, 1818, 1919, 2020]
KINDS = ("SHUFFLED_LABELS", "TEMPORAL_ABLATION", "FEATURE_ABLATION", "UNIVERSE_PERTURBATION")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tests", type=Path, required=True)
    ap.add_argument("--work", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--matrix", type=Path, required=True)
    args = ap.parse_args()
    sys.path.insert(0, str(args.tests))
    from conformance.fixtures import build, cli, request, write_request

    from stocks_predictor.research_readiness import AXES, classify, consumption_decision

    args.out.mkdir(parents=True, exist_ok=True)
    matrix = json.loads(args.matrix.read_text(encoding="utf-8"))
    axes = classify(matrix)
    readiness = {
        "source": str(args.matrix.name),
        "classifier": "stocks_predictor.research_readiness.classify (wheel instalada)",
        "axes_order": list(AXES),
        "ready_families": axes["ready_families"],
        "families": {
            family: {**entry, "consumption_for_trial": dict(zip(("allowed", "reason"),
                                                              consumption_decision(axes, family)))}
            for family, entry in axes["families"].items()
        },
    }
    (args.out / "external_intelligence_readiness.json").write_text(
        json.dumps(readiness, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

    env = build(args.work)
    log = (args.out / "negative_controls.jsonl").open("w", encoding="utf-8")

    def run(rid: str, control: dict | None) -> dict:
        value = request(rid)
        if control is not None:
            value["parameters"]["negative_control"] = control
        code, lines = cli(env, "process", str(write_request(env, rid.split(":")[1], value)))
        outcome = lines[0]
        result = json.loads(Path(outcome["outcome_file"]).read_text(encoding="utf-8")).get("result") or {}
        metrics = (result.get("domain_facts") or {}).get("metrics") or {}
        row = {"request_id": rid, "control": control, "exit": code, "status": outcome.get("status"),
               "result_state": outcome.get("result_state"), "scientific_state": outcome.get("scientific_state"),
               "economic_state": outcome.get("economic_state"),
               "excess_gross_bps": metrics.get("excess_gross_bps"),
               "excess_gross_ci_bps": metrics.get("excess_gross_ci_bps"),
               "excess_net_ci_bps": metrics.get("excess_net_ci_bps"), "periods": metrics.get("periods")}
        log.write(json.dumps(row, sort_keys=True) + "\n")
        log.flush()
        return row

    reference = run("stocks:REQ-NC-REFERENCE", None)
    rows = {kind: [run(f"stocks:REQ-NC-{kind[:4]}-{seed}", {"kind": kind, "seed": seed}) for seed in SEEDS]
            for kind in KINDS}
    supported = {kind: sum(1 for r in rows[kind] if r["scientific_state"] == "SUPPORTED") for kind in KINDS}
    same_state = sum(1 for r in rows["UNIVERSE_PERTURBATION"] if r["scientific_state"] == reference["scientific_state"])
    ref_low = (reference["excess_gross_ci_bps"] or [None])[0]
    lag_lows = [r["excess_gross_ci_bps"][0] for r in rows["TEMPORAL_ABLATION"] if r["excess_gross_ci_bps"]]
    criteria = {
        "SHUFFLED_LABELS": {"supported": supported["SHUFFLED_LABELS"], "max_allowed": 2,
                            "ok": supported["SHUFFLED_LABELS"] <= 2},
        "FEATURE_ABLATION": {"supported": supported["FEATURE_ABLATION"], "max_allowed": 2,
                             "ok": supported["FEATURE_ABLATION"] <= 2},
        "TEMPORAL_ABLATION": {"reference_ci_low_bps": ref_low, "lagged_ci_low_bps_max": max(lag_lows) if lag_lows else None,
                              "ok": ref_low is None or not lag_lows or ref_low <= 0
                              or max(lag_lows) <= ref_low * 1.5},
        "UNIVERSE_PERTURBATION": {"same_state_as_reference": same_state, "min_required": 16, "ok": same_state >= 16},
    }
    summary = {"data": "FIXTURE SINTÉTICA CONGELADA (diagnóstico; D-16 pendente)", "reference": reference,
               "supported_counts": supported, "criteria": criteria,
               "all_criteria_ok": all(c["ok"] for c in criteria.values()), "seeds": SEEDS}
    (args.out / "NEGATIVE_CONTROLS_SUMMARY.json").write_text(json.dumps(summary, indent=1, ensure_ascii=False) + "\n",
                                                            encoding="utf-8")
    print(json.dumps({"supported_counts": supported, "all_criteria_ok": summary["all_criteria_ok"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
