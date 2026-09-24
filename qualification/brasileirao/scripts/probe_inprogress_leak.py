"""brasileirao / truth-map: o motor de benchmark treina com jogo ainda em andamento?

Reproduz, só lendo a cópia do dataset, a sequência de refits do benchmark_predictor
(evaluator.py e serving_evaluator.py): observações ordenadas por (kickoff, home, away),
primeiro ajuste em MIN_HISTORY=200, refit a cada RETRAIN_EVERY=100; no refit o horizonte é o
kickoff da próxima previsão e entram no ajuste os jogos com `kickoff < horizonte`
(serving_evaluator.py:178, evaluator.py:99). Conta os jogos usados cujo resultado final
ainda NÃO existia no horizonte: kickoff < horizonte < kickoff + duração mínima de um jogo
(105 min = 90 + intervalo de 15, sem acréscimos: limite inferior conservador).

Uso: python probe_inprogress_leak.py <dataset.sqlite3> [--retrain-every 100] [--min-history 200]
Saída: JSON em stdout (refits, refits com jogo em andamento, exemplos).
"""

from __future__ import annotations

import argparse
import json
import sqlite3
from datetime import UTC, datetime, timedelta


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("db")
    ap.add_argument("--retrain-every", type=int, default=100)
    ap.add_argument("--min-history", type=int, default=200)
    ap.add_argument("--min-duration-minutes", type=int, default=105)
    args = ap.parse_args()
    conn = sqlite3.connect(f"file:{args.db}?mode=ro", uri=True)
    rows = conn.execute(
        "SELECT m.date, m.home_team, m.away_team, s.kickoff_at FROM matches m LEFT JOIN sofascore_matches s "
        "ON s.date = m.date AND s.home_team = m.home_team AND s.away_team = m.away_team "
        "WHERE m.home_score IS NOT NULL AND m.away_score IS NOT NULL"
    ).fetchall()
    obs = []
    for d, home, away, kickoff_at in rows:
        if kickoff_at:
            k = datetime.fromisoformat(kickoff_at.replace("Z", "+00:00")).astimezone(UTC)
        else:
            k = datetime.fromisoformat(d).replace(tzinfo=UTC)
        obs.append((k, home, away, kickoff_at is not None))
    obs.sort()
    duration = timedelta(minutes=args.min_duration_minutes)
    refits, leaking, examples = 0, 0, []
    steps = None
    for i in range(args.min_history, len(obs)):
        if steps is None or steps >= args.retrain_every:
            refits += 1
            horizon = obs[i][0]
            in_progress = [o for o in obs[:i] if o[0] < horizon < o[0] + duration]
            if in_progress:
                leaking += 1
                if len(examples) < 15:
                    examples.append({
                        "refit_index": i,
                        "horizon_target": f"{obs[i][1]} x {obs[i][2]} {horizon.isoformat()}",
                        "in_progress_used": [f"{o[1]} x {o[2]} kickoff {o[0].isoformat()}" for o in in_progress],
                    })
            steps = 0
        steps += 1
    print(json.dumps({
        "dataset": args.db,
        "observations": len(obs),
        "with_real_kickoff": sum(1 for o in obs if o[3]),
        "retrain_every": args.retrain_every,
        "min_history": args.min_history,
        "min_duration_minutes": args.min_duration_minutes,
        "refits": refits,
        "refits_using_match_in_progress": leaking,
        "examples": examples,
    }, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
