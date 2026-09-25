"""brasileirao: DIAGNÓSTICO (não fecha gate) — os outros ajustes com L-BFGS-B sem gradiente analítico são sensíveis
ao último bit, como o fit_goal_model antes do BR-F018?

Pista da revisão final (BR_F018_REQUALIFICATION_REPORT.md §9): `xg_model.fit`, `dixon_coles.fit_dixon_coles_parameters`
e `event_models.fit_event_model` usam L-BFGS-B com diferenças finitas. Pela wheel instalada, para cada um:
  * determinismo: a mesma entrada duas vezes no mesmo processo;
  * 1 ULP: uma entrada contínua movida para o float vizinho (`math.nextafter`) em todos os registros — a ordem de
    grandeza das diferenças que duas libm/BLAS produzem (Elo do mandante no `fit_event_model`, `days_ago` no
    `fit_dixon_coles_parameters`, xG no `xg_model.fit`).
Controle: `model.fit_goal_model` (corrigido no BR-F018) com os pesos × (1 + 2**-52).
Dados sintéticos com seed fixa. Com --dataset, também `fit_event_model` no dado real (escanteios e cartões amarelos,
Elo de `current_elo`), do mesmo jeito que o `display.compute_event` do `brasileirao-predict` o chama.
A saída tem só diferenças numéricas de parâmetros e probabilidades; nenhum registro do dado.

Uso (python do runtime da wheel): python other_optimizers_sensitivity.py [--dataset <cópia>] --out <json>
"""

from __future__ import annotations

import argparse
import json
import math
import sqlite3
from pathlib import Path

import numpy as np
from brasileirao_predictor import dixon_coles, event_models, model, xg_model

SEED = 20260925
N_TEAMS = 12


def up(x: float) -> float:
    return math.nextafter(float(x), math.inf)


def max_abs(a, b) -> float:
    """Maior |Δ| entre dois resultados com a mesma estrutura (dicts, listas e números)."""
    if isinstance(a, dict):
        return max((max_abs(a[k], b[k]) for k in a), default=0.0)
    if isinstance(a, (list, tuple)):
        return max((max_abs(x, y) for x, y in zip(a, b, strict=True)), default=0.0)
    if isinstance(a, (int, float)) and not isinstance(a, bool) and a is not None and b is not None:
        return abs(float(a) - float(b))
    return 0.0 if a == b else math.inf


def numeric(params: dict, keys) -> dict:
    return {k: params[k] for k in keys if k in params}


def league(seed: int):
    """Liga sintética: turno e returno, gols Poisson pela força, eventos Poisson pelo Elo."""
    rng = np.random.default_rng(seed)
    teams = [f"T{i:02d}" for i in range(N_TEAMS)]
    strength = {t: float(rng.normal(0.0, 0.35)) for t in teams}
    elo = {t: 1500.0 + 250.0 * strength[t] + float(rng.normal(0.0, 1.0)) for t in teams}
    games = []
    day = 0
    for home in teams:
        for away in teams:
            if home == away:
                continue
            day += 1
            lam_h = math.exp(0.25 + strength[home] - strength[away])
            lam_a = math.exp(strength[away] - strength[home])
            diff = (elo[home] - elo[away]) / 400.0
            games.append({
                "date": f"2025-{1 + (day // 28) % 12:02d}-{1 + day % 28:02d}",
                "home": home, "away": away,
                "home_goals": int(rng.poisson(lam_h)), "away_goals": int(rng.poisson(lam_a)),
                "home_xg": float(rng.gamma(4.0, lam_h / 4.0)), "away_xg": float(rng.gamma(4.0, lam_a / 4.0)),
                "home_event": int(rng.poisson(math.exp(1.6 + 0.3 * diff))),
                "away_event": int(rng.poisson(math.exp(1.4 - 0.3 * diff))),
                "days_ago": float(len(teams) * (len(teams) - 1) - day) + float(rng.uniform(0.0, 0.999)),
            })
    return teams, elo, games


def check_event_model(history, distribution: str, elo_pair) -> dict:
    fit = lambda h: event_models.fit_event_model(h, "diag", distribution=distribution)
    base, again = fit(history), fit(history)
    # só o Elo do mandante: mover os dois pelo mesmo ULP (mesma faixa binária) deixaria a diferença idêntica
    moved = fit([{**r, "home_elo": up(r["home_elo"])} for r in history])
    keys = ("a", "b", "alpha")

    def pred(p):
        lh, la, probs = event_models.predict_event(*elo_pair, p)
        return {"lh": lh, "la": la, **{k: v for k, v in probs.items() if isinstance(v, float)}}

    return {"fit_status": [base["fit_status"], moved["fit_status"]],
            "repeat_identical": numeric(base, keys) == numeric(again, keys),
            "ulp_max_abs_param_diff": max_abs(numeric(base, keys), numeric(moved, keys)),
            "ulp_max_abs_prob_diff": max_abs(pred(base), pred(moved))}


def check_dixon_coles(games) -> dict:
    fit = lambda g: dixon_coles.fit_dixon_coles_parameters(g, 0.0065)
    base, again = fit(games), fit(games)
    moved = fit([{**g, "days_ago": up(g["days_ago"])} for g in games])
    keys = ("attack", "defense", "home_advantage", "rho")
    return {"converged": [base["converged"], moved["converged"]],
            "repeat_identical": numeric(base, keys) == numeric(again, keys),
            "ulp_max_abs_param_diff": max_abs(numeric(base, keys), numeric(moved, keys))}


def check_xg_model(games) -> dict:
    matches = [(g["date"], g["home"], g["away"], g["home_goals"], g["away_goals"]) for g in games]
    xg_map = {(g["date"], g["home"], g["away"]): (g["home_xg"], g["away_xg"]) for g in games}
    moved_map = {k: (up(v[0]), up(v[1])) for k, v in xg_map.items()}
    cfg = {"half_life_years": 0.75, "w_xg": 0.85, "ridge_reg": 1.0}
    fit = lambda m: xg_model.fit(matches, m, "2026-01-01", cfg)
    base, again, moved = fit(xg_map), fit(xg_map), fit(moved_map)
    return {"repeat_identical": base == again, "ulp_max_abs_param_diff": max_abs(base, moved)}


def check_goal_model_control() -> dict:
    rng = np.random.default_rng(SEED)
    history = []
    for _ in range(1200):
        diff = float(rng.normal(0.0, 250.0))
        history.append((diff, int(rng.poisson(math.exp(0.15 + 0.6 * diff / 400.0))),
                        int(rng.poisson(math.exp(0.15 - 0.6 * diff / 400.0)))))
    weights = [math.exp(-math.log(2.0) * (1200 - i) / 730.0) for i in range(1200)]
    base = model.fit_goal_model(history, sample_weights=weights)
    moved = model.fit_goal_model(history, sample_weights=[w * (1 + 2**-52) for w in weights])
    return {"ulp_max_abs_param_diff": max_abs(list(base), list(moved))}


def real_event_histories(dataset: Path):
    conn = sqlite3.connect(f"{dataset.resolve().as_uri()}?mode=ro&immutable=1", uri=True)
    elo = dict(conn.execute("SELECT team, elo FROM current_elo").fetchall())
    out = {}
    for stat in ("Corner kicks", "Yellow cards"):
        rows = conn.execute(
            """SELECT sm.home_team, sm.away_team, h.value, a.value FROM sofascore_matches sm
               JOIN match_statistics h ON h.event_id=sm.event_id AND h.period='ALL' AND h.stat_name=? AND h.team='home'
               JOIN match_statistics a ON a.event_id=sm.event_id AND a.period='ALL' AND a.stat_name=? AND a.team='away'
               WHERE sm.home_score IS NOT NULL""", (stat, stat)).fetchall()
        out[stat] = [{"home_team": h, "away_team": aw, "home_elo": float(elo.get(h, 1500)), "away_elo": float(elo.get(aw, 1500)),
                      "home_event": hv, "away_event": av} for h, aw, hv, av in rows]
    conn.close()
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    teams, elo, games = league(SEED)
    history = [{"home_team": g["home"], "away_team": g["away"], "home_elo": elo[g["home"]], "away_elo": elo[g["away"]],
                "home_event": g["home_event"], "away_event": g["away_event"]} for g in games]
    pair = (elo[teams[0]], elo[teams[1]])
    doc = {
        "schema": "brasileirao/OTHER_OPTIMIZERS_SENSITIVITY/1",
        "label": "DIAGNÓSTICO: pela wheel instalada; não fecha gate",
        "synthetic": {"seed": SEED, "teams": N_TEAMS, "games": len(games),
                      "control_model.fit_goal_model": check_goal_model_control(),
                      "event_models.fit_event_model(poisson)": check_event_model(history, "poisson", pair),
                      "event_models.fit_event_model(nbinom)": check_event_model(history, "nbinom", pair),
                      "dixon_coles.fit_dixon_coles_parameters": check_dixon_coles(games),
                      "xg_model.fit": check_xg_model(games)},
    }
    if args.dataset:
        real = {}
        for stat, hist in real_event_histories(args.dataset).items():
            elos = sorted({r["home_elo"] for r in hist})
            real[stat] = {"n": len(hist), **check_event_model(hist, "poisson", (elos[-1], elos[0]))}
        doc["real_event_model_as_display"] = real
    args.out.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(doc, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
