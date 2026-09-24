"""brasileirao / BR-F018: DIAGNÓSTICO (não fecha gate) — nos refits reais, o ótimo do método NOVO (rc3: gradiente
analítico + polimento até a raiz do gradiente) é pelo menos tão bom quanto o do método ANTIGO (rc2: L-BFGS-B com
diferenças finitas), na MESMA negll?

Monta à mão, com a wheel rc3 instalada, o mesmo caminho do worker que `fit_sensitivity.py` (refit mensal, só
informação com `available_at < refit_at`). O método antigo é reproduzido exatamente sobre a mesma wheel: `minimize`
sem `jac` e sem polimento (a negll da rc3 é a da rc2 sem mudança). Para cada refit compara, na mesma negll e nos
mesmos dados, o valor nos dois pontos de parada e a norma do gradiente projetado (KKT nos bounds). Só contagens e
diferenças numéricas vão para a saída; nenhum registro do dado.

Uso (python do runtime da wheel rc3):
  python optimum_check.py --dataset <cópia> --repo <clone> --commit <sha> --as-of <T> --out <json>
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import yaml
from brasileirao_predictor import model
from brasileirao_predictor.research_runtime import worker

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fit_sensitivity

_captured: dict = {}
_objective, _polish, _minimize = model._goal_model_objective, model._polish_gradient_root, model.minimize


def _capture_objective(*args):
    negll, gradient = _objective(*args)
    _captured["negll"], _captured["gradient"] = negll, gradient
    return negll, gradient


def _polish_new(theta, negll, gradient, bounds):
    solution = _polish(theta, negll, gradient, bounds)
    _captured["theta"], _captured["bounds"] = np.array(solution), bounds
    return solution


def _polish_old(theta, negll, gradient, bounds):
    _captured["theta"], _captured["bounds"] = np.array(theta), bounds
    return theta


def _minimize_without_jac(fun, x0, *args, jac=None, **kwargs):
    return _minimize(fun, x0, *args, **kwargs)


def fit(new: bool, history, weights):
    model.minimize = _minimize if new else _minimize_without_jac
    model._polish_gradient_root = _polish_new if new else _polish_old
    model.fit_goal_model(history, sample_weights=weights)
    return _captured["theta"].copy(), _captured["negll"], _captured["gradient"], _captured["bounds"]


def projected_gradient_norm(theta, gradient, bounds) -> float:
    lower = np.array([-np.inf if lo is None else lo for lo, _ in bounds])
    upper = np.array([np.inf if hi is None else hi for _, hi in bounds])
    grad = gradient(theta)
    free = model._projected_free(theta, grad, lower, upper)
    return float(np.max(np.abs(grad[free]), initial=0.0))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", type=Path, required=True)
    ap.add_argument("--repo", required=True)
    ap.add_argument("--commit", required=True)
    ap.add_argument("--as-of", required=True)
    ap.add_argument("--from", dest="start", default="2021-05")
    ap.add_argument("--to", dest="end", default="2026-09")
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    model._goal_model_objective = _capture_objective
    config = yaml.safe_load(subprocess.run(["git", "-C", args.repo, "show", f"{args.commit}:config.yaml"],
                                           capture_output=True, check=True).stdout.decode("utf-8"))
    cfg = {"elo": config["elo"], "model": {k: config["model"][k] for k in ("calibration_window_years", "goal_half_life_days", "max_goals")}}
    conn = sqlite3.connect(f"{args.dataset.resolve().as_uri()}?mode=ro&immutable=1", uri=True)
    info = worker._information(conn, datetime.fromisoformat(args.as_of.replace("Z", "+00:00")))
    conn.close()
    rows = []
    for refit_at in fit_sensitivity.months(args.start, args.end):
        prepared = fit_sensitivity.pairs_and_weights([r for r in info if r["available_at"] < refit_at], refit_at, cfg)
        if prepared is None:
            continue
        history, weights = prepared
        theta_new, negll, gradient, bounds = fit(True, history, weights)
        theta_old, _negll, _gradient, _bounds = fit(False, history, weights)
        f_new, f_old = negll(theta_new), negll(theta_old)  # mesma negll, mesmos dados, dois pontos
        rows.append({"refit_at": refit_at.strftime("%Y-%m"), "negll_new_minus_old": f_new - f_old,
                     "relative": (f_new - f_old) / abs(f_old),
                     "projected_gradient_new": projected_gradient_norm(theta_new, gradient, bounds),
                     "projected_gradient_old": projected_gradient_norm(theta_old, gradient, bounds),
                     "max_abs_theta_diff": float(np.max(np.abs(theta_new - theta_old)))})
    gaps = [r["negll_new_minus_old"] for r in rows]
    summary = {
        "schema": "brasileirao/OPTIMUM_CHECK/1",
        "label": "DIAGNÓSTICO: montagem manual do caminho do worker com a wheel instalada; não fecha gate",
        "refits": len(rows),
        "new_better": sum(g < 0 for g in gaps), "equal": sum(g == 0 for g in gaps), "new_worse": sum(g > 0 for g in gaps),
        "max_new_minus_old": max(gaps), "min_new_minus_old": min(gaps),
        "max_relative_new_minus_old": max(r["relative"] for r in rows),
        "max_projected_gradient_new": max(r["projected_gradient_new"] for r in rows),
        "median_projected_gradient_old": float(np.median([r["projected_gradient_old"] for r in rows])),
        "max_projected_gradient_old": max(r["projected_gradient_old"] for r in rows),
        "max_abs_theta_diff": max(r["max_abs_theta_diff"] for r in rows),
    }
    args.out.write_text(json.dumps({**summary, "rows": rows}, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(summary, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
