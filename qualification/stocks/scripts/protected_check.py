"""stocks / PROTECTED_ARTIFACTS_UNCHANGED: compara o conjunto protegido do truth-map com o final_commit.

Git: hash do blob de cada item de PROTECTED_SET.json no commit final (git rev-parse <commit>:<path>)
e busca de itens novos pelos mesmos padrões (o conjunto só cresce). Fora do git: sha256 de cada
arquivo de dados imutável, recalculado somente leitura (arquivo sha256sum passado por --data-now).
Saída: JSON em stdout (vai para RAW_LOGS como log bruto).

Uso: python protected_check.py --repo <clone> --commit <final> --data-now <sha256sum.txt>
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parent))
from truth_map import DECLARED, PROMPT_GLOBS, match, tree  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--commit", required=True)
    ap.add_argument("--data-now", required=True, type=Path)
    args = ap.parse_args()
    protected = json.loads((HERE.parents[1] / "PROTECTED_SET.json").read_text(encoding="utf-8"))
    final_tree = tree(args.repo, args.commit)
    changed, missing = [], []
    for item in protected["items"]:
        blob = final_tree.get(item["path"])
        if blob is None:
            missing.append(item["path"])
        elif blob != item["git_blob"]:
            changed.append({"path": item["path"], "truth_map": item["git_blob"], "final": blob})
    patterns = PROMPT_GLOBS + [p for p, _ in DECLARED]
    known = {item["path"] for item in protected["items"]}
    new_items = sorted(p for p in final_tree if p not in known and any(match(p, pat) for pat in patterns))
    before = {i["path"]: i["sha256"] for i in protected["immutable_data"]["items"]}
    now = {}
    for line in args.data_now.read_text(encoding="utf-8").splitlines():
        digest, path = line.split(" ", 1)
        now["C:/STOCKS/" + path.lstrip("*")] = digest
    data_changed = sorted(p for p in before if now.get(p) != before[p])
    data_new = sorted(p for p in now if p not in before)
    report = {
        "truth_map_commit": protected["commit"], "final_commit": args.commit,
        "git_items": len(protected["items"]), "git_changed": changed, "git_missing": missing,
        "git_new_items_matching_patterns": new_items,
        "data_items": len(before), "data_rehashed": len(now), "data_changed": data_changed, "data_new_files": data_new,
        "unchanged": not changed and not missing and not data_changed,
        "diff_names_truth_map_to_final": subprocess.run(
            ["git", "-C", args.repo, "diff", "--name-only", protected["commit"], args.commit],
            capture_output=True, text=True, check=True).stdout.splitlines(),
    }
    print(json.dumps(report, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
