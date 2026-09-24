"""stocks / D-16: controles negativos sobre o painel REAL (STOCKS_NEGATIVE_CONTROLS) e métricas.

Mesmo desenho e mesmos critérios congelados do scripts/science.py (FROZEN_PARAMETERS
negative_controls), trocando a fixture pelo ambiente de operador real (real_env.py). Cada execução
é um processo novo do entrypoint instalado `stocks-research`, pela wheel publicada.

  referência   o pedido do protocolo real, sem controle (o mesmo conteúdo do E2E)
  controles    SHUFFLED_LABELS, TEMPORAL_ABLATION, FEATURE_ABLATION, UNIVERSE_PERTURBATION × 20 seeds

Saídas (em --out): negative_controls.jsonl (uma linha por execução, bruta) e
NEGATIVE_CONTROLS_SUMMARY.json (contagens e critérios congelados, calculados do jsonl).

Uso: python d16_science.py --tests <tests/> --build <dir do build> --protocol <PROTOCOL_REAL.json>
       --matrix <matriz.json> --work <dir> --out <dir>
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SEEDS = [101, 202, 303, 404, 505, 606, 707, 808, 909, 1010, 1111, 1212, 1313, 1414, 1515, 1616, 1717, 1818, 1919, 2020]
KINDS = ("SHUFFLED_LABELS", "TEMPORAL_ABLATION", "FEATURE_ABLATION", "UNIVERSE_PERTURBATION")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tests", type=Path, required=True)
    ap.add_argument("--build", type=Path, required=True)
    ap.add_argument("--protocol", type=Path, required=True)
    ap.add_argument("--matrix", type=Path, required=True)
    ap.add_argument("--work", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    sys.path.insert(0, str(args.tests))
    sys.path.insert(0, str(HERE))
    from conformance.fixtures import cli, write_request
    from real_env import backtest_request, provision

    protocol = json.loads(args.protocol.read_text(encoding="utf-8"))
    if protocol["negative_controls"]["seeds"] != SEEDS or list(protocol["negative_controls"]["kinds"]) != list(KINDS):
        raise SystemExit("negative-control seeds/kinds differ from the frozen ones")
    matrix = json.loads(args.matrix.read_text(encoding="utf-8"))
    args.out.mkdir(parents=True, exist_ok=True)
    env = provision(args.work, args.build, protocol, matrix)
    log = (args.out / "negative_controls.jsonl").open("w", encoding="utf-8")

    def run(rid: str, control: dict | None) -> dict:
        value = backtest_request(protocol, rid, env["as_of"], control=control)
        code, lines = cli(env, "process", str(write_request(env, rid.split(":")[1], value)))
        outcome = lines[0] if lines else {}
        result = json.loads(Path(outcome["outcome_file"]).read_text(encoding="utf-8")).get("result") or {} \
            if outcome.get("outcome_file") else {}
        metrics = (result.get("domain_facts") or {}).get("metrics") or {}
        row = {"request_id": rid, "control": control, "exit": code, "status": outcome.get("status"),
               "result_state": outcome.get("result_state"), "scientific_state": outcome.get("scientific_state"),
               "economic_state": outcome.get("economic_state"),
               "excess_gross_bps": metrics.get("excess_gross_bps"),
               "excess_gross_ci_bps": metrics.get("excess_gross_ci_bps"),
               "excess_net_bps": metrics.get("excess_net_bps"),
               "excess_net_ci_bps": metrics.get("excess_net_ci_bps"), "periods": metrics.get("periods")}
        log.write(json.dumps(row, sort_keys=True) + "\n")
        log.flush()
        return row

    reference = run("stocks:REQ-D16-NC-REFERENCE", None)
    rows = {kind: [run(f"stocks:REQ-D16-NC-{kind[:4]}-{seed}", {"kind": kind, "seed": seed}) for seed in SEEDS]
            for kind in KINDS}
    failed_runs = [r["request_id"] for kind in KINDS for r in rows[kind] if r["exit"] != 0 or r["status"] != "RESULT"]
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
                              "rule": "reportado; nunca melhora o IC inferior do excesso bruto em mais de 50% sem investigação",
                              "ok": ref_low is None or not lag_lows or ref_low <= 0 or max(lag_lows) <= ref_low * 1.5},
        "UNIVERSE_PERTURBATION": {"same_state_as_reference": same_state, "min_required": 16, "ok": same_state >= 16,
                                  "rule": "estado igual ao não perturbado em ≥ 16 de 20; senão resultado frágil (reportado)"},
    }
    summary = {"data": "PAINEL REAL B3/CVM (D-16)", "dataset_version": env["env"]["dataset_version"],
               "dataset_sha256": env["env"]["object_hashes"]["dataset"], "reference": reference,
               "runs": 1 + sum(len(v) for v in rows.values()), "failed_runs": failed_runs,
               "supported_counts": supported, "criteria": criteria,
               "all_criteria_ok": all(c["ok"] for c in criteria.values()) and not failed_runs, "seeds": SEEDS}
    (args.out / "NEGATIVE_CONTROLS_SUMMARY.json").write_text(json.dumps(summary, indent=1, ensure_ascii=False) + "\n",
                                                            encoding="utf-8")
    print(json.dumps({"supported_counts": supported, "all_criteria_ok": summary["all_criteria_ok"],
                      "failed_runs": len(failed_runs)}))
    return 0 if not failed_runs else 1


if __name__ == "__main__":
    raise SystemExit(main())
