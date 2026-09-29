"""crypto (C15.1, gate PROTECTED_ARTIFACTS_UNCHANGED): confere um PROTECTED_SET*.json contra um commit.
Só leitura (git ls-tree). Saída: JSON com items, unchanged e changed_or_missing (mesmo formato de
RAW_LOGS/v1.1/protected_set_check_341d270.json).
Uso: python protected_set_check.py --set PROTECTED_SET.json --repo <clone> --commit <sha> --out <json>
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", required=True, type=Path)
    ap.add_argument("--repo", required=True)
    ap.add_argument("--commit", required=True)
    ap.add_argument("--out", required=True, type=Path)
    a = ap.parse_args()
    doc = json.loads(a.set.read_text(encoding="utf-8"))
    items = doc["items"]
    tree = subprocess.run(["git", "-C", a.repo, "ls-tree", "-r", a.commit], capture_output=True, text=True, check=True).stdout
    current = {line.split("\t", 1)[1]: line.split("\t", 1)[0].split()[2] for line in tree.splitlines()}
    changed = [{"path": i["path"], "expected": i["git_blob"], "actual": current.get(i["path"])}
               for i in items if current.get(i["path"]) != i["git_blob"]]
    out = {"schema": "crypto/PROTECTED_ARTIFACT_CHECK/1", "truth_map_commit": doc.get("commit"),
           "final_commit": a.commit, "protected_set": a.set.name,
           "protected_set_sha256": hashlib.sha256(a.set.read_bytes()).hexdigest(),
           "items": len(items), "unchanged": len(items) - len(changed), "changed_or_missing": changed}
    a.out.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"{a.out}: {out['unchanged']}/{out['items']} iguais, {len(changed)} alterados/ausentes")


if __name__ == "__main__":
    main()
