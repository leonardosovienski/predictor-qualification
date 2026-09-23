"""crypto / fase `baseline` (C3): STACK_BASELINE.json da missão.

Reaproveita o coletor do STACK_BASELINE_V1 (qualification/shared/scripts/
collect_stack_baseline.py) restrito aos três repos da missão: cripto-predictor,
core-predictor e predictor-ops. Só leitura (git + gh api); todo comando e saída
vão sem edição para o log bruto; o JSON deriva dessas saídas.

Uso:
  python collect_mission_baseline.py --raw-log <RAW_LOGS/baseline/collect.log> --out <STACK_BASELINE.json>
"""

from __future__ import annotations

import argparse
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[2] / "shared" / "scripts"))

import collect_stack_baseline as shared  # noqa: E402

MISSION_REPOS = ("cripto-predictor", "core-predictor", "predictor-ops")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw-log", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()
    args.raw_log.parent.mkdir(parents=True, exist_ok=True)
    r = shared.Runner(args.raw_log)
    specs = [spec for spec in shared.REPOS if spec[0] in MISSION_REPOS]
    repos = [shared.collect_repo(r, *spec) for spec in specs]
    for entry in repos:
        entry["git_status_porcelain"] = r.git(
            entry["clone"], "status", "--porcelain", "--untracked-files=all"
        ).splitlines()
        entry["local_branches"] = r.git(entry["clone"], "branch", "--format=%(refname:short)").split()
    uv_version = r.run(["uv", "--version"]).strip()
    v1 = json.loads((HERE.parents[2] / "shared" / "STACK_BASELINE_V1.json").read_text(encoding="utf-8"))
    v1_heads = {x["repo"]: x["head"] for x in v1["repos"]}
    baseline = {
        "baseline_id": "crypto/STACK_BASELINE",
        "stage": "A",
        "branch": "crypto",
        "common_baseline": "STACK_BASELINE_V1",
        "common_core_sha256": "50e8f49859daae6dcdf17164781d1837d8b656796924c35060f8d35855ee36e1",
        "mission_prompt": "prompts/prompt_etapa_a_cripto_rev8.md",
        "collected_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "collector": "qualification/crypto/scripts/collect_mission_baseline.py",
        "environment_collector": {
            "role": "secondary (Windows local, D-3)",
            "os": platform.platform(),
            "python_collector": sys.version.split()[0],
            "uv": uv_version,
        },
        "repos": repos,
        "head_vs_stack_baseline_v1": {
            x["repo"]: {"v1_head": v1_heads.get(x["repo"]), "head": x["head"],
                        "equal": v1_heads.get(x["repo"]) == x["head"]}
            for x in repos
        },
        "stack_wheel_verification": shared.verify_stack_wheels(r, repos),
        "capital_permission": False,
        "training_started": False,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(baseline, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8", newline="\n")
    print(f"{args.out}: {len(repos)} repos")


if __name__ == "__main__":
    main()
