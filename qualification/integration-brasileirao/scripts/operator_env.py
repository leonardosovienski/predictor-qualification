"""integration-brasileirao: ambiente de OPERADOR do Brasileirão (fronteira do domínio, não do CAIN), no runtime privado.

Mesma fronteira da Etapa A (qualification/brasileirao/scripts/real_env.py), sem os pedidos: objetos de referência JSON
cujos valores vêm do config.yaml do commit final (git show, não da árvore de trabalho), provisionados pelo
`brasileirao-research put-object` INSTALADO; dois datasets capturados pelo `brasileirao-research put-dataset`
(sqlite3.backup da fonte só leitura) com o mesmo as_of; e a policy de admissão da missão (FROZEN_PARAMETERS →
operator_env). O holdout 2025 continua HOLDOUT_SEALED na policy (contrato).

Dataset canário (FROZEN_PARAMETERS → data.future_canary): cópia privada da cópia conferida do dado, com DUAS partidas a
mais nas tabelas e na forma do vetor FUTURE_CANARY_BR_001 da conformidade (token × um time do próprio dado,
competição/temporada 2024, kickoffs 2024-10-20T22:00:00Z e 2024-10-27T22:00:00Z, placares 17×0 e 0×17), depois do
data_cutoff 2024-10-01T00:00:00Z do pedido 03-canary e antes do as_of do dataset.

Tudo fica no diretório privado <work>. A saída (stdout e REAL_ENV.json) tem só referências, hashes, contagens e o
token; nenhum valor do dado (time, event_id, placar, odd) é impresso ou gravado fora do diretório privado.

Uso: python operator_env.py --script <venv>/bin/brasileirao-research --repo <clone brasileirao-predictor>
         --commit <final_commit> --dataset <cópia conferida> --dataset-sha256 <hex> --work <dir privado vazio>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sqlite3
import subprocess
from pathlib import Path

import yaml

AS_OF = "2026-09-08T19:31:32Z"
CANARY = "FUTURE_CANARY_BR_INTEGRATION_001"
CANARY_KICKOFFS = ("2024-10-20T22:00:00+00:00", "2024-10-27T22:00:00+00:00")
BASELINES = {"climatology": {"schema": "brasileirao-baseline/1", "kind": "CLIMATOLOGY_PIT"},
             "market": {"schema": "brasileirao-baseline/1", "kind": "MARKET_CLOSE_SHIN"}}
COST = {"schema": "brasileirao-cost-model/1", "edge_window": None, "stake": 1, "slippage_on_winnings": 0.02,
        "tax_on_annual_positive_net": 0.15, "min_bets": 30}
FEATURES = {"schema": "brasileirao-features/1", "features": ["elo_diff_pre_match", "home_advantage"], "xg": False}
ODDS = {"schema": "brasileirao-odds/1", "source": "sofascore_matches (1X2) + odds_lines ou 2.5 (O/U)", "price": "close",
        "use": "ex post evaluation only"}
HYPOTHESES = ("brasileirao:HQ-SERVING-BASELINE", "brasileirao:QUAL-SERVING-REAL-001",
              "brasileirao:QUAL-SERVING-REAL-002", "brasileirao:QUAL-SERVING-REAL-003",
              # ciclo 4 (decisão do dono): uma hipótese de qualificação por ciclo do soak (FROZEN_PARAMETERS → operator_env)
              *(f"brasileirao:QUAL-SOAK-{n:03d}" for n in range(1, 25)))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(cmd: list[str], log: Path) -> subprocess.CompletedProcess:
    done = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
    with log.open("a", encoding="utf-8", newline="\n") as fh:  # log privado: pode conter caminhos, nunca vai a RAW_LOGS
        fh.write(f"$ {' '.join(cmd)}\n[exit {done.returncode}]\n{done.stdout}\n[stderr]\n{done.stderr[-4000:]}\n")
    if done.returncode != 0:
        raise SystemExit(f"{cmd[1]} falhou (exit {done.returncode}); ver o log privado")
    return done


def build_canary(source: Path, target: Path) -> dict:
    """Cópia privada + duas partidas canário (token × um time do dado), fora de qualquer impressão."""
    shutil.copyfile(source, target)
    db = sqlite3.connect(target)
    try:
        row = db.execute("SELECT competition, home_team FROM sofascore_matches WHERE season='2024' "
                         "AND home_team IS NOT NULL ORDER BY event_id LIMIT 1").fetchone()
        competition, team = row
        base = db.execute("SELECT MAX(event_id) FROM sofascore_matches").fetchone()[0]
        for offset, ((home, away, hs, as_), kickoff) in enumerate(
                zip(((CANARY, team, 17, 0), (team, CANARY, 0, 17)), CANARY_KICKOFFS, strict=True), 1):
            event_id = base + offset
            day = kickoff[:10]
            db.execute("INSERT INTO sofascore_matches (event_id, competition, season, date, kickoff_at, home_team, "
                       "away_team, home_score, away_score, odds_home, odds_draw, odds_away) "
                       "VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                       (event_id, competition, "2024", day, kickoff, home, away, hs, as_, 1.5, 4.0, 6.0))
            db.execute("INSERT INTO odds_lines (event_id, market, line, odd_a, odd_b) VALUES (?, 'ou', 2.5, 1.9, 1.9)",
                       (event_id,))
            db.execute("INSERT INTO matches (event_id, date, home_team, away_team, home_score, away_score, tournament, "
                       "city, country, neutral) VALUES (?,?,?,?,?,?,?,?,?,?)",
                       (event_id, day, home, away, hs, as_, "Brasileirão Série A", None, "Brazil", 0))
        db.commit()
        counts = {t: db.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
                  for t in ("sofascore_matches", "matches", "odds_lines")}
    finally:
        db.close()
    return {"token": CANARY, "kickoffs_utc": [k.replace("+00:00", "Z") for k in CANARY_KICKOFFS],
            "rows_added": 2, "counts_after": counts, "sha256": sha(target)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--script", required=True)
    ap.add_argument("--repo", required=True)
    ap.add_argument("--commit", required=True)
    ap.add_argument("--dataset", required=True, type=Path)
    ap.add_argument("--dataset-sha256", required=True)
    ap.add_argument("--work", required=True, type=Path)
    a = ap.parse_args()
    if sha(a.dataset) != a.dataset_sha256:
        raise SystemExit("cópia do dado com sha256 diferente do registrado")
    a.work.mkdir(parents=True, exist_ok=False)
    log = a.work / "operator_commands.log"
    config = yaml.safe_load(subprocess.run(["git", "-C", a.repo, "show", f"{a.commit}:config.yaml"],
                                           capture_output=True, check=True).stdout.decode("utf-8"))
    if config["ensemble_xg"]["enabled"]:
        raise SystemExit("ensemble_xg ligado no config.yaml: o handler compilado serve só a baseline")
    model = {"schema": "brasileirao-model-config/1", "algorithm": "nbdc-normalized-elo-horizon-v2",
             "source": f"config.yaml @ {a.commit} (elo + model); ensemble_xg.enabled=False",
             "config": {"elo": config["elo"],
                        "model": {k: config["model"][k] for k in ("calibration_window_years", "goal_half_life_days",
                                                                   "max_goals")},
                        "algorithm": "nbdc-normalized-elo-horizon-v2"}}
    cost = COST | {"edge_window": [float(config["backtest"]["min_edge"]), float(config["backtest"]["max_edge"])]}
    objects, registry = a.work / "obj", []
    refs = {("model", "serving-baseline"): model, ("features", "elo-home-advantage"): FEATURES,
            ("cost_model", "close-slippage-tax"): cost, ("odds", "sofascore-close"): ODDS,
            **{("baseline", name): value for name, value in BASELINES.items()}}
    for (kind, name), value in refs.items():
        path = a.work / f"{kind}-{name}.json"
        path.write_text(json.dumps(value, sort_keys=True), encoding="utf-8")
        done = run([a.script, "put-object", "--objects", str(objects), str(path)], log)
        registry.append({"kind": kind, "name": name, "version": "1", "revision_id": f"{name}-r1",
                         "content_hash": json.loads(done.stdout)["object_hash"]})
    canary_db = a.work / "canary-source.sqlite3"
    canary = build_canary(a.dataset, canary_db)
    datasets = {}
    for label, source in (("real-20260908", a.dataset), ("real-canary-20260908", canary_db)):
        done = run([a.script, "put-dataset", "--objects", str(objects), "--source", str(source), "--as-of", AS_OF,
                    "--label", label], log)
        stored = json.loads(done.stdout)
        registry.append({"kind": "dataset", "name": label, "version": "1", "revision_id": f"{label}-r1",
                         "content_hash": stored["manifest_hash"]})
        datasets[label] = {"manifest_hash": stored["manifest_hash"], "source_sha256": sha(source)}
    if sha(a.dataset) != a.dataset_sha256:
        raise SystemExit("cópia do dado mudou durante a captura")
    policy = {
        "schema_version": "BrasileiraoResearchAdmissionPolicyV1", "policy_id": "brasileirao-integration-qualification",
        "policy_version": 1, "owner": "BRASILEIRAO_OPERATOR", "requester_trust": "LOCAL_FILE_ONLY",
        "handlers": {"WALKFORWARD_FORECAST_EVALUATION": "brasileirao.handlers.walkforward_forecast_evaluation.v1"},
        "hypotheses": {h: {"hypothesis_family": "brasileirao:serving-baseline",
                           "purpose": "walk-forward do modelo de serving congelado contra baseline, sem retunar "
                                      "(qualificação da integração)"} for h in HYPOTHESES},
        "protected_hypotheses": ["brasileirao:H8", "brasileirao:H9", "brasileirao:H14", "brasileirao:H15",
                                 "brasileirao:A1"],
        "season_policy": {"2021": "DEVELOPMENT", "2022": "DEVELOPMENT", "2023": "DEVELOPMENT", "2024": "VALIDATION",
                          "2025": "HOLDOUT_SEALED", "2026": "EXPLORATORY"},
        "allowed_competitions": ["Brasileirão Série A"],
        "registry": registry,
        "limits": {"max_pending_requests": 100, "max_request_bytes": 65536, "max_parameter_bytes": 32768,
                   "max_concurrency": 1, "cpu_seconds": 3600, "memory_mb": 4096, "disk_mb": 4096,
                   "timeout_seconds": 3600, "max_retries": 2, "max_priority": "NORMAL"},
    }
    policy_path = a.work / "policy.json"
    policy_path.write_text(json.dumps(policy, sort_keys=True), encoding="utf-8")
    env = {"schema": "integration-brasileirao/REAL_ENV/1", "as_of": AS_OF, "commit": a.commit,
           "dataset_source_sha256": a.dataset_sha256, "datasets": datasets,
           "canary": {k: v for k, v in canary.items() if k != "sha256"} | {"canary_source_sha256": canary["sha256"]},
           "canary_markers": [CANARY, *canary["kickoffs_utc"], *(k[:16] for k in CANARY_KICKOFFS)],
           "policy": {"policy_id": policy["policy_id"], "sha256": sha(policy_path)},
           "registry": [{k: r[k] for k in ("kind", "name", "version", "content_hash")} for r in registry],
           "paths": {"policy": str(policy_path), "objects": str(objects)}}
    (a.work / "REAL_ENV.json").write_text(json.dumps(env, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({k: env[k] for k in ("datasets", "policy")} | {"canary_sha256": canary["sha256"],
                                                                   "registry": len(registry)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
