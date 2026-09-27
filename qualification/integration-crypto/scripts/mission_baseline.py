"""integration-crypto, fase baseline (C3): STACK_BASELINE.json da missão, antes de qualquer mudança.

Entrada: a saída do coletor versionado `qualification/shared/scripts/collect_stack_baseline_v2.py` (mesmo coletor e
mesmas bases do STACK_BASELINE_V2.0), rodado nesta sessão (RAW_LOGS/baseline/). Este script só compara essa coleta
com o STACK_BASELINE_V2.0 do main e registra o resultado; não coleta nada por conta própria.

Uso: python mission_baseline.py --collected <json> --raw-log <log> --common <STACK_BASELINE_V2.0.json> --out <json>
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

VOLATILE = {"collected_at", "note", "predictor_qualification_commit"}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--collected", type=Path, required=True)
    ap.add_argument("--raw-log", type=Path, required=True)
    ap.add_argument("--common", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    got = json.loads(a.collected.read_text(encoding="utf-8"))
    common = json.loads(a.common.read_text(encoding="utf-8"))
    by_repo = {r["repo"]: r for r in common["repos"]}
    repos = []
    for r in got["repos"]:
        c = by_repo[r["repo"]]
        same = {k: r[k] == c[k] for k in r if k not in {"clone"}}
        repos.append({
            "repo": r["repo"],
            "base_commit": r["base"]["commit"],
            "origin_main": r["origin_main"]["commit"],
            "base_is_ancestor_of_main": r["origin_main"]["base_is_ancestor"],
            "commits_main_not_base": r["origin_main"]["commits_main_not_base"],
            "same_tree_as_main": r["origin_main"]["same_tree"],
            "version": r["project"]["version"],
            "uv_lock_sha256": (r.get("uv_lock") or {}).get("sha256"),
            "equal_to_common_baseline": all(same.values()),
            "fields_different_from_common": sorted(k for k, v in same.items() if not v),
        })
    wheels_equal = got["final_wheel_verification"] == common["final_wheel_verification"]
    out = {
        "schema": "integration-crypto/STACK_BASELINE/1",
        "phase": "baseline",
        "branch": "integration-crypto",
        "rule": "C3: fotografia de todos os repos antes de qualquer mudança da missão; Etapa B parte do STACK_BASELINE_V2.0",
        "common_baseline": {"id": common["baseline_id"], "sha256": sha(a.common)},
        "collection": {
            "collector": "qualification/shared/scripts/collect_stack_baseline_v2.py (sem mudança)",
            "output": {"path": "qualification/integration-crypto/RAW_LOGS/baseline/stack_baseline_mission_collected.json",
                       "sha256": sha(a.collected)},
            "raw_log": {"path": "qualification/integration-crypto/RAW_LOGS/baseline/collect_stack_baseline_mission.log",
                        "sha256": sha(a.raw_log)},
            "collected_at": got["collected_at"],
            "environment": got["environments"],
        },
        "repos": repos,
        "final_wheels_equal_to_common": wheels_equal,
        "all_final_wheels_match_release_assets": got["all_final_wheels_match"],
        "equal_to_common_baseline": wheels_equal and all(r["equal_to_common_baseline"] for r in repos),
        "notes": [
            "cripto-predictor: origin/main à frente da base (PRs #128–#134) é só informação (D-23); a base é 341d270",
            "predictor-ops: origin/main 31d3939 é o squash do PR #26 com a mesma árvore de 9831b0d",
        ],
        "capital_permission": False,
        "training_started": False,
    }
    a.out.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"equal_to_common_baseline": out["equal_to_common_baseline"],
                      "repos": {r["repo"]: r["equal_to_common_baseline"] for r in repos}}, indent=1))
    return 0 if out["equal_to_common_baseline"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
