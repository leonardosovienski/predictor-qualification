"""integration-brasileirao, fase baseline (C3): STACK_BASELINE.json da missão, antes de qualquer mudança.

Entrada: a saída do coletor versionado `qualification/shared/scripts/collect_stack_baseline_v2.py` (sem mudança),
rodado nesta sessão com --cain-commit/--ecosystem-commit = final_commits da integration-stocks QUALIFIED
(RAW_LOGS/baseline/). Este script só compara essa coleta com o STACK_BASELINE_V2.0 e com a attestation QUALIFIED da
integration-stocks no main, e registra o resultado; não coleta nada por conta própria.

Diferenças esperadas e aceitas (declaradas antes): cain e ecosystem-predictor (as integrações anteriores os moveram;
esta missão parte dos final_commits da integration-stocks, prompt da sessão 7.4). Qualquer outra diferença = falha.
Campos de estado REMOTO (main de cada repo, releases publicadas, runs de CI) são informação, nunca mudança da base
(mesma separação da integration-stocks).

Uso: python mission_baseline.py --collected <json> --raw-log <log> --common <STACK_BASELINE_V2.0.json>
                                --integration-stocks <QUALIFICATION_ATTESTATION.json> --out <json>
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

EXPECTED_DIFFERENT = {"cain", "ecosystem-predictor"}
REMOTE_STATE_FIELDS = {"origin_main", "published_wheels", "ci_runs_at_base"}
M = "qualification/integration-brasileirao"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--collected", type=Path, required=True)
    ap.add_argument("--raw-log", type=Path, required=True)
    ap.add_argument("--common", type=Path, required=True)
    ap.add_argument("--integration-stocks", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    got = json.loads(a.collected.read_text(encoding="utf-8"))
    common = json.loads(a.common.read_text(encoding="utf-8"))
    ist = json.loads(a.integration_stocks.read_text(encoding="utf-8"))
    ist_commits = {c["repo"]: c["commit_sha"] for c in ist["final_commits"]}
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
            entry["expected_base"] = ist_commits[r["repo"]]
            entry["base_is_integration_stocks_final_commit"] = r["base"]["commit"] == ist_commits[r["repo"]]
            if not entry["base_is_integration_stocks_final_commit"]:
                problems.append(f"{r['repo']}: base {r['base']['commit']} != final_commit {ist_commits[r['repo']]}")
        elif not equal:
            problems.append(f"{r['repo']}: difere do STACK_BASELINE_V2.0 em {entry['fields_different_from_common']}")
        repos.append(entry)
    wheels_equal = got["final_wheel_verification"] == common["final_wheel_verification"]
    if not wheels_equal:
        problems.append("final_wheel_verification difere do STACK_BASELINE_V2.0")
    if not got["all_final_wheels_match"]:
        problems.append("alguma final_wheel não confere com o asset da release")
    br = next(r for r in repos if r["repo"] == "brasileirao-predictor")
    if br["base_commit"] != "25cdf4d9bb309d33f066fbc6a379f5d98c69f08a":
        problems.append(f"brasileirao-predictor: base {br['base_commit']} != runtime_target 25cdf4d")
    out = {
        "schema": "integration-brasileirao/STACK_BASELINE/1",
        "phase": "baseline",
        "branch": "integration-brasileirao",
        "rule": "C3: fotografia de todos os repos antes de qualquer mudança da missão; Etapa B parte do "
                "STACK_BASELINE_V2.0, com cain e ecosystem-predictor nos final_commits da integration-stocks "
                "QUALIFIED (D-22; prompt da sessão 7.4)",
        "common_baseline": {"id": common["baseline_id"], "sha256": sha(a.common)},
        "integration_stocks": {
            "attestation": {"path": "qualification/integration-stocks/QUALIFICATION_ATTESTATION.json",
                            "sha256": sha(a.integration_stocks), "result": ist["result"]},
            "final_commits": ist_commits,
            "final_wheels": ist["final_wheels"],
            "note": "cripto-predictor ee3d3d1 e stocks-predictor 6f857b2 são os estados integrados dos outros "
                    "domínios (runtimes integrados desta missão); o coletor V2 fotografa as bases da Etapa A, que não "
                    "mudam nesta missão",
        },
        "collection": {
            "collector": "qualification/shared/scripts/collect_stack_baseline_v2.py (sem mudança)",
            "output": {"path": f"{M}/RAW_LOGS/baseline/stack_baseline_mission_collected.json", "sha256": sha(a.collected)},
            # O log bruto do coletor (ls-tree de todos os repos + JSON da API) fica no diretório privado do runtime: o
            # no_data_rows_check acusa nele um falso positivo dentro de um hash de blob (IB-F003) e não é alterado.
            "raw_log": {"path": "~/predictors/runtime/integration-brasileirao/priv/baseline/"
                                "collect_stack_baseline_mission.log", "sha256": sha(a.raw_log),
                        "published": False, "why": "IB-F003 (falso positivo do no_data_rows_check num hash de blob)"},
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
            "brasileirao-predictor: base 25cdf4d = runtime_target rc3; origin/main d80a4ed tem a mesma árvore (D-25 (1))",
            "cain: origin/main à frente de deccaaa (#59 política v2, #60, #61 versão 0.4.13rc8 não publicada, #62 "
            "correções IS-F002/IS-F003): só informação (IB-F001); nada dessa faixa entra na missão",
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
