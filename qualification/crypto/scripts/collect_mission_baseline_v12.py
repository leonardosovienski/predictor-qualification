"""crypto / reabertura V1.2 (D-27, C24.4): STACK_BASELINE da missão reaberta (C3, C8 "HEAD diferente
do registrado → novo baseline").

Reaproveita collect_mission_baseline.py / collect_stack_baseline.py, com duas adaptações do host
Linux que conduz a reabertura (sessão de 2026-09-29): os clones ficam em <clone-root>/<repo> (em vez
dos caminhos Windows de C:\\QUALIFICACAO), e `gh api` é atendido por scripts/gh_api_shim.sh (curl
anônimo à api.github.com), colocado no PATH pelo próprio script. Só leitura; tudo vai ao log bruto.

Uso:
  python collect_mission_baseline_v12.py --clone-root /home/user \
      --raw-log qualification/crypto/RAW_LOGS/v1.2/baseline/collect.log \
      --out qualification/crypto/STACK_BASELINE_V1.2.json
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[2] / "shared" / "scripts"))
import collect_stack_baseline as shared  # noqa: E402

MISSION_REPOS = ("cripto-predictor", "core-predictor", "predictor-ops")
# commits congelados da Etapa A que continuam sendo os final_commits de Core e Ops (wheels inalteradas)
FROZEN = {"core-predictor": "5a0841509f091ea0aa95bde0d3d65e2a1a9e984d",
          "predictor-ops": "9831b0d5e727972b1d85ff48be14ffa58677898b"}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--clone-root", required=True, type=Path)
    ap.add_argument("--raw-log", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()
    shim_dir = HERE.parent
    os.environ["PATH"] = f"{shim_dir / 'ghbin'}{os.pathsep}{os.environ['PATH']}"
    (shim_dir / "ghbin").mkdir(exist_ok=True)
    gh = shim_dir / "ghbin" / "gh"
    if not gh.exists():
        gh.symlink_to(shim_dir / "gh_api_shim.sh")
    args.raw_log.parent.mkdir(parents=True, exist_ok=True)
    r = shared.Runner(args.raw_log)
    specs = [(repo, str(args.clone_root / repo), dirs) for repo, _clone, dirs in shared.REPOS if repo in MISSION_REPOS]
    repos = [shared.collect_repo(r, *spec) for spec in specs]
    for entry in repos:
        entry["git_status_porcelain"] = r.git(entry["clone"], "status", "--porcelain", "--untracked-files=all").splitlines()
        entry["local_branches"] = r.git(entry["clone"], "branch", "--format=%(refname:short)").split()
        entry["remote_branches"] = r.git(entry["clone"], "branch", "-r", "--format=%(refname:short)").split()
        frozen = FROZEN.get(entry["repo"])
        if frozen:
            changed = r.git(entry["clone"], "diff", "--name-only", frozen, entry["head"], "--",
                            "src", "pyproject.toml", "uv.lock").split()
            entry["frozen_final_commit"] = {"commit": frozen, "package_files_changed_to_head": changed,
                                            "wheel_source_unchanged": not changed}
    uv_version = r.run(["uv", "--version"]).strip()
    shared_dir = HERE.parents[2] / "shared"
    v11 = json.loads((shared_dir / "STACK_BASELINE_V1.1.json").read_text(encoding="utf-8"))
    v11_heads = {x["repo"]: x["head"] for x in v11["repos"]}
    prev = json.loads((HERE.parents[1] / "runtime_target.json").read_text(encoding="utf-8"))
    baseline = {
        "baseline_id": "crypto/STACK_BASELINE_V1.2",
        "stage": "A",
        "branch": "crypto",
        "cycle": "V1.2 (reabertura D-27, C24.4)",
        "common_baseline": "STACK_BASELINE_V1.2",
        "common_core_sha256": shared.sha256_bytes((HERE.parents[2] / "COMMON_QUALIFICATION_CORE.md").read_bytes()),
        "mission_prompt": "prompts/prompt_etapa_a_cripto_rev8.md",
        "collected_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "collector": "qualification/crypto/scripts/collect_mission_baseline_v12.py (gh api via gh_api_shim.sh)",
        "environment_collector": {
            "role": "coletor (Linux na nuvem da sessão de 2026-09-29; só git e API pública do GitHub; nada dos repos é executado aqui como prova)",
            "os": platform.platform(), "python_collector": sys.version.split()[0], "uv": uv_version,
        },
        "runtime_target": {k: prev[k] for k in ("commit", "version", "wheel_url", "wheel_sha256", "sdist_sha256", "previous")},
        "repos": repos,
        "head_vs_stack_baseline_v1_1": {
            x["repo"]: {"v1_1_head": v11_heads.get(x["repo"]), "head": x["head"], "equal": v11_heads.get(x["repo"]) == x["head"]}
            for x in repos
        },
        "stack_wheel_verification": shared.verify_stack_wheels(r, repos),
        "capital_permission": False,
        "training_started": False,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(baseline, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"{args.out}: {len(repos)} repos")


if __name__ == "__main__":
    main()
