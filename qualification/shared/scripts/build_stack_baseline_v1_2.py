"""STACK_BASELINE_V1.2 (C3, C24.4, D-27): base da reabertura da Etapa A do crypto.

Deriva de qualification/crypto/STACK_BASELINE_V1.2.json (coletado por collect_mission_baseline_v12.py, só git +
API pública) e do STACK_BASELINE_V1.1.json: os três repos da missão (cripto-predictor, core-predictor, predictor-ops)
com HEAD, versão, lock e wheels; os demais repos ficam como no V1.1 (informação, não base desta reabertura).
Uso: python build_stack_baseline_v1_2.py   (grava qualification/shared/STACK_BASELINE_V1.2.json)
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SHARED = ROOT / "qualification" / "shared"


def main() -> None:
    mission = json.loads((ROOT / "qualification" / "crypto" / "STACK_BASELINE_V1.2.json").read_text(encoding="utf-8"))
    v11 = json.loads((SHARED / "STACK_BASELINE_V1.1.json").read_text(encoding="utf-8"))
    core = ROOT / "qualification" / "COMMON_QUALIFICATION_CORE.md"
    repos = {r["repo"]: r for r in mission["repos"]}
    doc = {
        "baseline_id": "STACK_BASELINE_V1.2",
        "note": ("D-27 (C24.4): reabertura da Etapa A do crypto. cripto-predictor no main 21f8b182 (1.2.0rc4, pré-release "
                 "v1.2.0rc4 publicada pelo workflow Release com build duplo); core-predictor e predictor-ops com as MESMAS wheels "
                 "do V1.1 (3.2.1 e 4.2.2rc1; final_commits 5a08415 e 9831b0d), embora o main dos dois tenha avançado só em "
                 "CI/README/Dockerfile (nenhum arquivo de src/, pyproject.toml ou uv.lock mudou desde o commit da wheel). "
                 "Os demais repos (cain, ecosystem-predictor, brasileirao-predictor, stocks-predictor) não fazem parte desta "
                 "base e ficam registrados só como no V1.1 (a base da Etapa B continua sendo STACK_BASELINE_V2.0 até revisão)."),
        "supersedes": "STACK_BASELINE_V1.1",
        "common_core_version": "2.3",
        "common_core_sha256": hashlib.sha256(core.read_bytes()).hexdigest(),
        "decisions": ["D-9", "D-16", "D-17", "D-27"],
        "mission_prompt": "prompts/prompt_etapa_a_cripto_rev8.md",
        "collected_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "collector": "qualification/shared/scripts/build_stack_baseline_v1_2.py sobre qualification/crypto/STACK_BASELINE_V1.2.json",
        "environments": {
            "collector_host": mission["environment_collector"],
            "linux_primary": {"role": "primary (GitHub Actions, D-9/D-16)", "source": "crypto-reopening.yml"},
            "windows_secondary": {"role": "secondary (Windows local, D-3)", "status": "pendente nesta reabertura"},
        },
        "repos": [
            {k: repos[r][k] for k in ("repo", "remote", "branch", "head", "origin_main", "head_equals_origin_main", "clean",
                                      "project", "uv_lock", "stack_wheels_consumed", "published_wheels", "ci_runs_at_head")}
            | ({"frozen_final_commit": repos[r]["frozen_final_commit"]} if "frozen_final_commit" in repos[r] else {})
            for r in ("cripto-predictor", "core-predictor", "predictor-ops")
        ],
        "final_commits_stage_a_crypto": [
            {"repo": "cripto-predictor", "commit_sha": repos["cripto-predictor"]["head"]},
            {"repo": "core-predictor", "commit_sha": "5a0841509f091ea0aa95bde0d3d65e2a1a9e984d"},
            {"repo": "predictor-ops", "commit_sha": "9831b0d5e727972b1d85ff48be14ffa58677898b"},
        ],
        "stack_wheel_verification": mission["stack_wheel_verification"],
        "other_repos_as_in_v1_1": [{k: x[k] for k in ("repo", "head")} for x in v11["repos"]
                                   if x["repo"] not in ("cripto-predictor", "core-predictor", "predictor-ops")],
        "capital_permission": False,
        "training_started": False,
    }
    out = SHARED / "STACK_BASELINE_V1.2.json"
    out.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(out, len(doc["repos"]), "repos")


if __name__ == "__main__":
    main()
