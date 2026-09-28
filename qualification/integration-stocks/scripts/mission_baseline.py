"""integration-stocks, fase baseline (C3): STACK_BASELINE.json da missão, antes de qualquer mudança.

Entrada: a saída do coletor versionado `qualification/shared/scripts/collect_stack_baseline_v2.py` (sem mudança),
rodado nesta sessão com --cain-commit/--ecosystem-commit = final_commits da integration-crypto (RAW_LOGS/baseline/).
Este script só compara essa coleta com o STACK_BASELINE_V2.0 e com a attestation QUALIFIED da integration-crypto no
main, e registra o resultado; não coleta nada por conta própria.

Diferenças esperadas e aceitas (declaradas antes): cain e ecosystem-predictor (a integration-crypto os moveu; esta
missão parte dos final_commits dela, D-22 e prompt da sessão 6.4). Qualquer outra diferença = falha.

Uso: python mission_baseline.py --collected <json> --raw-log <log> --common <STACK_BASELINE_V2.0.json>
                                --integration-crypto <QUALIFICATION_ATTESTATION.json> --out <json>
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

EXPECTED_DIFFERENT = {"cain", "ecosystem-predictor"}
# Campos que descrevem o estado REMOTO no instante da coleta (o main de cada repo e as releases publicadas), não a base
# fotografada: diferença neles é registrada como informação, nunca como mudança da base. Separação feita depois da
# primeira execução (RAW_LOGS/baseline/mission_baseline_run1_strict.log, que comparava todos os campos e acusou só o
# cripto-predictor: main 905ab7a e a release v1.2.0rc3 publicados pela integration-crypto).
REMOTE_STATE_FIELDS = {"origin_main", "published_wheels", "ci_runs_at_base"}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--collected", type=Path, required=True)
    ap.add_argument("--raw-log", type=Path, required=True)
    ap.add_argument("--common", type=Path, required=True)
    ap.add_argument("--integration-crypto", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    got = json.loads(a.collected.read_text(encoding="utf-8"))
    common = json.loads(a.common.read_text(encoding="utf-8"))
    ic = json.loads(a.integration_crypto.read_text(encoding="utf-8"))
    ic_commits = {c["repo"]: c["commit_sha"] for c in ic["final_commits"]}
    by_repo = {r["repo"]: r for r in common["repos"]}
    repos, problems = [], []
    for r in got["repos"]:
        c = by_repo[r["repo"]]
        same = {k: r[k] == c[k] for k in r if k not in {"clone"}}
        equal = all(v for k, v in same.items() if k not in REMOTE_STATE_FIELDS)
        entry = {
            "repo": r["repo"],
            "base_commit": r["base"]["commit"],
            "origin_main": r["origin_main"]["commit"],
            "base_is_ancestor_of_main": r["origin_main"]["base_is_ancestor"],
            "commits_main_not_base": r["origin_main"]["commits_main_not_base"],
            "same_tree_as_main": r["origin_main"]["same_tree"],
            "version": r["project"]["version"],
            "uv_lock_sha256": (r.get("uv_lock") or {}).get("sha256"),
            "equal_to_common_baseline": equal,
            "fields_different_from_common": sorted(k for k, v in same.items() if not v and k not in REMOTE_STATE_FIELDS),
            "remote_state_changed_since_common": sorted(k for k, v in same.items() if not v and k in REMOTE_STATE_FIELDS),
        }
        if r["repo"] in EXPECTED_DIFFERENT:
            entry["expected_base"] = ic_commits[r["repo"]]
            entry["base_is_integration_crypto_final_commit"] = r["base"]["commit"] == ic_commits[r["repo"]]
            if not entry["base_is_integration_crypto_final_commit"]:
                problems.append(f"{r['repo']}: base {r['base']['commit']} != final_commit {ic_commits[r['repo']]}")
        elif not equal:
            problems.append(f"{r['repo']}: difere do STACK_BASELINE_V2.0 em {entry['fields_different_from_common']}")
        repos.append(entry)
    wheels_equal = got["final_wheel_verification"] == common["final_wheel_verification"]
    if not wheels_equal:
        problems.append("final_wheel_verification difere do STACK_BASELINE_V2.0")
    if not got["all_final_wheels_match"]:
        problems.append("alguma final_wheel não confere com o asset da release")
    out = {
        "schema": "integration-stocks/STACK_BASELINE/1",
        "phase": "baseline",
        "branch": "integration-stocks",
        "rule": "C3: fotografia de todos os repos antes de qualquer mudança da missão; Etapa B parte do "
                "STACK_BASELINE_V2.0, com cain e ecosystem-predictor nos final_commits da integration-crypto (D-22)",
        "common_baseline": {"id": common["baseline_id"], "sha256": sha(a.common)},
        "integration_crypto": {
            "attestation": {"path": "qualification/integration-crypto/QUALIFICATION_ATTESTATION.json",
                            "sha256": sha(a.integration_crypto), "result": ic["result"]},
            "final_commits": ic_commits,
            "final_wheels": ic["final_wheels"],
            "note": "cripto-predictor ee3d3d1 (1.2.0rc3) é o estado integrado do cripto; o coletor V2 fotografa a base "
                    "da Etapa A (341d270) e não muda nesta missão",
        },
        "collection": {
            "collector": "qualification/shared/scripts/collect_stack_baseline_v2.py (sem mudança)",
            "output": {"path": "qualification/integration-stocks/RAW_LOGS/baseline/stack_baseline_mission_collected.json",
                       "sha256": sha(a.collected)},
            "raw_log": {"path": "qualification/integration-stocks/RAW_LOGS/baseline/collect_stack_baseline_mission.log",
                        "sha256": sha(a.raw_log)},
            "collected_at": got["collected_at"],
            "environment": got["environments"],
        },
        "repos": repos,
        "final_wheels_equal_to_common": wheels_equal,
        "all_final_wheels_match_release_assets": got["all_final_wheels_match"],
        "expected_differences": sorted(EXPECTED_DIFFERENT),
        "problems": problems,
        "ok": not problems,
        "notes": [
            "stocks-predictor: origin/main à frente da base (PRs #99–#106, 23 commits) é só informação (D-24); a base é "
            "61fc017, e nada dessa faixa entra na missão",
        ],
        "capital_permission": False,
        "training_started": False,
    }
    a.out.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"ok": out["ok"], "problems": problems,
                      "repos": {r["repo"]: r["equal_to_common_baseline"] for r in repos}}, indent=1))
    return 0 if out["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
