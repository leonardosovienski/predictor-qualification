"""brasileirao: DIAGNÓSTICO (não é prova de gate) — o refit mensal do modelo de gols é sensível ao último bit?

Explica por que o mesmo pedido real, com a mesma wheel e o mesmo snapshot (sha256 igual) e o mesmo
conjunto de informação (information_fingerprint igual), dá parâmetros diferentes no Windows e no Linux.
Monta à mão, com a wheel instalada, o mesmo caminho do worker (_information -> _windowed -> ratings ->
model.fit_goal_model com os pesos de recência) para cada refit_at mensal, e compara:
  * repetição: o mesmo ajuste duas vezes no mesmo processo (determinismo no mesmo SO);
  * perturbação de 1 ULP: pesos multiplicados por (1 + 2**-52), diferença que duas libm/BLAS produzem.
Só números de parâmetros vão para a saída; nenhum registro do dado.

Uso (python do runtime da wheel): python fit_sensitivity.py --dataset <cópia> --repo <clone> --commit <sha>
          --as-of <T> --from 2021-05 --to 2026-09 --out <json>
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import statistics
import subprocess
from datetime import UTC, datetime, timedelta
from pathlib import Path

import yaml

from brasileirao_predictor import model, ratings
from brasileirao_predictor.research_runtime import worker


def months(start: str, end: str) -> list[datetime]:
    y, m = map(int, start.split("-"))
    ey, em = map(int, end.split("-"))
    out = []
    while (y, m) <= (ey, em):
        out.append(datetime(y, m, 1, tzinfo=UTC))
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


def pairs_and_weights(info: list[dict], refit_at: datetime, cfg: dict):
    """O mesmo que worker._fit_goal_model até a chamada do otimizador."""
    rows = worker._windowed(info, refit_at, cfg["elo"].get("window_years"))
    if not rows:
        return None
    _elo, history = ratings.compute_ratings(worker._elo_rows(rows), cfg["elo"], asof=refit_at.date())
    keys = ratings.temporal_keys(worker._elo_rows(rows))
    ordered = [row for _key, row in sorted(zip(keys, rows, strict=True), key=lambda item: item[0])]
    cal_start = (refit_at.date() - timedelta(days=int(float(cfg["model"]["calibration_window_years"]) * 365.25))).isoformat()
    pairs = [(h, r) for h, r in zip(history, ordered, strict=True) if r["date"] >= cal_start]
    if len(pairs) < worker.MIN_CALIBRATION:
        return None
    weights = model.exponential_recency_weights([r["date"] for _h, r in pairs], refit_at.date().isoformat(),
                                                cfg["model"]["goal_half_life_days"])
    return [h for h, _r in pairs], weights


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", type=Path, required=True)
    ap.add_argument("--repo", required=True)
    ap.add_argument("--commit", required=True)
    ap.add_argument("--as-of", required=True)
    ap.add_argument("--from", dest="start", required=True)
    ap.add_argument("--to", dest="end", required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--tight", nargs=2, type=float, metavar=("FTOL", "GTOL"),
                    help="contraprova: L-BFGS-B com ftol/gtol dados (só neste processo; a wheel não muda)")
    args = ap.parse_args()
    if args.tight:
        original = model.minimize

        def tight_minimize(fun, x0, *a, method=None, options=None, **kw):
            if method == "L-BFGS-B":
                options = {"ftol": args.tight[0], "gtol": args.tight[1], "maxiter": 15000, "maxfun": 150000} | (options or {})
            return original(fun, x0, *a, method=method, options=options, **kw)

        model.minimize = tight_minimize
    config = yaml.safe_load(subprocess.run(["git", "-C", args.repo, "show", f"{args.commit}:config.yaml"],
                                           capture_output=True, check=True).stdout.decode("utf-8"))
    cfg = {"elo": config["elo"], "model": {k: config["model"][k] for k in ("calibration_window_years", "goal_half_life_days", "max_goals")}}
    as_of = datetime.fromisoformat(args.as_of.replace("Z", "+00:00"))
    conn = sqlite3.connect(f"{args.dataset.resolve().as_uri()}?mode=ro&immutable=1", uri=True)
    info = worker._information(conn, as_of)
    conn.close()
    rows = []
    failures = 0
    for refit_at in months(args.start, args.end):
        # como no walkforward: só informação com available_at < refit_at entra no refit (ordem canônica do worker)
        fit_info = [r for r in info if r["available_at"] < refit_at]
        prepared = pairs_and_weights(fit_info, refit_at, cfg)
        if prepared is None:
            continue
        history, weights = prepared
        try:
            p0 = model.fit_goal_model(history, sample_weights=weights)
            p_repeat = model.fit_goal_model(history, sample_weights=weights)
            p_ulp = model.fit_goal_model(history, sample_weights=[w * (1 + 2**-52) for w in weights])
        except model.OptimizationFailedError:
            failures += 1
            continue
        rows.append({
            "refit_at": refit_at.strftime("%Y-%m-%d"),
            "n_calibration": len(history),
            "repeat_identical": list(p0) == list(p_repeat),
            "ulp_max_abs_param_diff": max(abs(a - b) for a, b in zip(p0, p_ulp)),
        })
    diffs = [r["ulp_max_abs_param_diff"] for r in rows]
    doc = {
        "schema": "brasileirao/FIT_SENSITIVITY/1",
        "label": "DIAGNÓSTICO: montagem manual do caminho do worker com a wheel instalada; não fecha gate",
        "optimizer": f"L-BFGS-B ftol={args.tight[0]} gtol={args.tight[1]} (contraprova --tight)" if args.tight else "como na wheel (L-BFGS-B, tolerâncias padrão)",
        "optimizer_failures": failures,
        "refits": len(rows),
        "repeat_identical_all": all(r["repeat_identical"] for r in rows),
        "ulp_changed_refits": sum(1 for d in diffs if d > 0),
        "ulp_max_abs_param_diff": {"max": max(diffs), "median": statistics.median(diffs),
                                   "over_1e-6": sum(1 for d in diffs if d > 1e-6), "over_1e-3": sum(1 for d in diffs if d > 1e-3)},
        "rows": rows,
    }
    args.out.write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: doc[k] for k in ("refits", "repeat_identical_all", "ulp_changed_refits", "ulp_max_abs_param_diff")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
