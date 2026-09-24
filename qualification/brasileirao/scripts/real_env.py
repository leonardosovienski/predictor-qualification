"""brasileirao: real-data runs through the INSTALLED `brasileirao-research` (Windows local).

Operator provisioning with real inputs, never versioned (D-11): the dataset is captured from the
hash-verified copy of the preserved snapshot (sqlite3.backup, read-only source); the model,
features, baselines, cost model and odds references are JSON objects whose values are copied
from config.yaml of the commit under test (git show, not the working tree). Requests: one per
(season, target, baseline) over the whole season, with data_cutoff = dataset as_of, so every
prediction uses its own cutoff = kickoff - 60 min. The sealed 2025 season is never a target.

Everything the circuit prints is saved raw under --out (outcome lines, `show` payloads); the
numbers of the reports are derived from those files by evidence_numbers.py (C20).

Usage:
  python real_env.py --script <venv>/Scripts/brasileirao-research.exe --repo <clone> --commit <sha>
      --dataset <copy.sqlite3> --dataset-sha256 <hex> --as-of 2026-09-08T19:31:32Z
      --work <short dir> --out <RAW_LOGS dir> [--seasons 2021 2022 2023 2024 2026] [--quick]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import yaml

TARGETS = ("1X2", "OU25")
BASELINES = {"climatology": {"schema": "brasileirao-baseline/1", "kind": "CLIMATOLOGY_PIT"},
             "market": {"schema": "brasileirao-baseline/1", "kind": "MARKET_CLOSE_SHIN"}}
COST = {"schema": "brasileirao-cost-model/1", "edge_window": None, "stake": 1, "slippage_on_winnings": 0.02,
        "tax_on_annual_positive_net": 0.15, "min_bets": 30}
FEATURES = {"schema": "brasileirao-features/1", "features": ["elo_diff_pre_match", "home_advantage"], "xg": False}
ODDS = {"schema": "brasileirao-odds/1", "source": "sofascore_matches", "price": "close", "use": "ex post evaluation only"}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(cmd: list[str], log: Path) -> subprocess.CompletedProcess:
    done = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
    with log.open("a", encoding="utf-8", newline="\n") as fh:
        fh.write(f"$ {' '.join(cmd)}\n[exit {done.returncode}]\n{done.stdout}")
        if done.stderr:
            fh.write(f"[stderr]\n{done.stderr[-4000:]}\n")
    return done


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--script", required=True)
    ap.add_argument("--repo", required=True)
    ap.add_argument("--commit", required=True)
    ap.add_argument("--dataset", required=True, type=Path)
    ap.add_argument("--dataset-sha256", required=True)
    ap.add_argument("--as-of", required=True)
    ap.add_argument("--work", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--seasons", nargs="+", type=int, default=[2021, 2022, 2023, 2024, 2026])
    ap.add_argument("--targets", nargs="+", default=list(TARGETS))
    ap.add_argument("--baselines", nargs="+", default=list(BASELINES))
    args = ap.parse_args()
    if 2025 in args.seasons:
        raise SystemExit("2025 is HOLDOUT_SEALED: never a target")
    if sha(args.dataset) != args.dataset_sha256:
        raise SystemExit("dataset copy hash differs from the recorded sha256")
    args.work.mkdir(parents=True, exist_ok=False)
    args.out.mkdir(parents=True, exist_ok=True)
    log = args.out / "commands.log"
    config = yaml.safe_load(subprocess.run(["git", "-C", args.repo, "show", f"{args.commit}:config.yaml"],
                                           capture_output=True, check=True).stdout.decode("utf-8"))
    model = {
        "schema": "brasileirao-model-config/1",
        "algorithm": "nbdc-normalized-elo-horizon-v2",
        "source": f"config.yaml @ {args.commit} (elo + model); ensemble_xg.enabled={config['ensemble_xg']['enabled']}",
        "config": {"elo": config["elo"], "model": {k: config["model"][k] for k in ("calibration_window_years", "goal_half_life_days", "max_goals")},
                   "algorithm": "nbdc-normalized-elo-horizon-v2"},
    }
    if config["ensemble_xg"]["enabled"]:
        raise SystemExit("ensemble_xg enabled in config.yaml: the compiled handler serves the baseline only")
    cost = COST | {"edge_window": [float(config["backtest"]["min_edge"]), float(config["backtest"]["max_edge"])]}
    objects, registry = args.work / "obj", []
    refs = {("model", "serving-baseline"): model, ("features", "elo-home-advantage"): FEATURES,
            ("cost_model", "close-slippage-tax"): cost, ("odds", "sofascore-close"): ODDS,
            **{("baseline", name): value for name, value in BASELINES.items()}}
    for (kind, name), value in refs.items():
        path = args.work / f"{kind}-{name}.json"
        path.write_text(json.dumps(value, sort_keys=True), encoding="utf-8")
        done = run([args.script, "put-object", "--objects", str(objects), str(path)], log)
        assert done.returncode == 0, done.stderr
        registry.append({"kind": kind, "name": name, "version": "1", "revision_id": f"{name}-r1",
                         "content_hash": json.loads(done.stdout)["object_hash"]})
    done = run([args.script, "put-dataset", "--objects", str(objects), "--source", str(args.dataset),
                "--as-of", args.as_of, "--label", "real-20260908"], log)
    assert done.returncode == 0, done.stderr
    stored = json.loads(done.stdout)
    registry.append({"kind": "dataset", "name": "real-20260908", "version": "1", "revision_id": "real-20260908-r1",
                     "content_hash": stored["manifest_hash"]})
    (args.out / "dataset_capture.json").write_text(json.dumps(stored | {"source_sha256": args.dataset_sha256}, indent=1), encoding="utf-8")
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
    policy = {
        "schema_version": "BrasileiraoResearchAdmissionPolicyV1", "policy_id": "brasileirao-research-real",
        "policy_version": 1, "owner": "BRASILEIRAO_OPERATOR", "requester_trust": "LOCAL_FILE_ONLY",
        "handlers": {"WALKFORWARD_FORECAST_EVALUATION": "brasileirao.handlers.walkforward_forecast_evaluation.v1"},
        "hypotheses": {"brasileirao:HQ-SERVING-BASELINE": {"hypothesis_family": "brasileirao:serving-baseline",
                       "purpose": "walk-forward do modelo de serving congelado contra baseline, sem retunar"}},
        "protected_hypotheses": ["brasileirao:H8", "brasileirao:H9", "brasileirao:H14", "brasileirao:H15", "brasileirao:A1"],
        "season_policy": {"2021": "DEVELOPMENT", "2022": "DEVELOPMENT", "2023": "DEVELOPMENT", "2024": "VALIDATION",
                          "2025": "HOLDOUT_SEALED", "2026": "EXPLORATORY"},
        "allowed_competitions": ["Brasileirão Série A"],
        "registry": registry,
        "limits": {"max_pending_requests": 100, "max_request_bytes": 65536, "max_parameter_bytes": 32768,
                   "max_concurrency": 1, "cpu_seconds": 3600, "memory_mb": 4096, "disk_mb": 4096,
                   "timeout_seconds": 3600, "max_retries": 2, "max_priority": "NORMAL"},
    }
    policy_path = args.work / "policy.json"
    policy_path.write_text(json.dumps(policy, sort_keys=True), encoding="utf-8")
    (args.out / "policy.json").write_text(json.dumps(policy, sort_keys=True, indent=1), encoding="utf-8")
    state = args.work / "s"
    summary = []
    for season in args.seasons:
        for target in args.targets:
            for baseline in args.baselines:
                rid = f"brasileirao:REQ-REAL-{season}-{target}-{baseline}"
                request = {
                    "schema_version": "brasileirao-research-request/1", "request_id": rid,
                    "request_type": "WALKFORWARD_FORECAST_EVALUATION", "research_id": "brasileirao:R-REAL-20260924",
                    "hypothesis_id": "brasileirao:HQ-SERVING-BASELINE", "competition": "Brasileirão Série A",
                    "season": season, "target": target,
                    "events": {"kickoff_from": f"{season}-01-01T00:00:00Z", "kickoff_to": f"{season + 1}-01-01T00:00:00Z"},
                    "data_cutoff": args.as_of, "decision_lead_minutes": 60,
                    "references": {"dataset": {"name": "real-20260908", "version": "1"},
                                   "model": {"name": "serving-baseline", "version": "1"},
                                   "features": {"name": "elo-home-advantage", "version": "1"},
                                   "baseline": {"name": baseline, "version": "1"},
                                   "cost_model": {"name": "close-slippage-tax", "version": "1"},
                                   "odds": {"name": "sofascore-close", "version": "1"}},
                    "priority_hint": "NORMAL",
                }
                if season == 2026:
                    request["events"]["kickoff_to"] = args.as_of
                path = args.work / "req" / f"{season}-{target}-{baseline}.json"
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(json.dumps(request, ensure_ascii=False), encoding="utf-8")
                done = run([args.script, "--state", str(state), "process", "--policy", str(policy_path),
                            "--objects", str(objects), str(path)], log)
                shown = run([args.script, "--state", str(state), "show", rid], log)
                name = f"{season}-{target}-{baseline}"
                (args.out / f"outcome_{name}.jsonl").write_text(done.stdout, encoding="utf-8")
                (args.out / f"result_{name}.json").write_text(shown.stdout, encoding="utf-8")
                summary.append({"request": name, "process_exit": done.returncode, "show_exit": shown.returncode})
                print(name, done.returncode, shown.returncode, flush=True)
    (args.out / "runs.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
