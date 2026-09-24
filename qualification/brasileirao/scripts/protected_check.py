"""brasileirao: PROTECTED_ARTIFACTS_UNCHANGED — blob git de cada item do PROTECTED_SET.json no commit final.

Uso: python protected_check.py --repo <clone> --commit <sha> --set PROTECTED_SET.json --out <json>
Item ausente ou com blob diferente = alterado (P0).
"""

from __future__ import annotations

import argparse
import json
import subprocess


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--commit", required=True)
    ap.add_argument("--set", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    protected = json.load(open(args.set, encoding="utf-8"))
    tree = {}
    for line in subprocess.run(["git", "-C", args.repo, "ls-tree", "-r", args.commit], capture_output=True, text=True,
                               encoding="utf-8", check=True).stdout.splitlines():
        meta, path = line.split("\t", 1)
        tree[path] = meta.split()[2]
    changed = [{"path": i["path"], "truth_map_blob": i["git_blob"], "final_blob": tree.get(i["path"])}
               for i in protected["items"] if tree.get(i["path"]) != i["git_blob"]]
    doc = {"schema": "brasileirao/PROTECTED_CHECK/1", "truth_map_commit": protected["commit"], "final_commit": args.commit,
           "items": protected["count"], "unchanged": protected["count"] - len(changed), "changed": changed}
    with open(args.out, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(doc, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print(f"{doc['unchanged']}/{doc['items']} iguais; alterados: {len(changed)}")


if __name__ == "__main__":
    main()
