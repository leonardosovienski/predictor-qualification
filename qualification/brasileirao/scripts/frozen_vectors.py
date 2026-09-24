"""brasileirao: FROZEN_VECTORS.json = sha256 (e blob git) de cada arquivo da suíte de conformidade num commit.

Uso: python frozen_vectors.py --repo <clone> --commit <sha> --out FROZEN_VECTORS.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess


def git(repo: str, *args: str) -> bytes:
    return subprocess.run(["git", "-C", repo, *args], capture_output=True, check=True).stdout


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--commit", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    items = []
    for line in git(args.repo, "ls-tree", "-r", args.commit, "tests/conformance").decode().splitlines():
        meta, path = line.split("\t", 1)
        if not path.endswith(".py"):
            continue
        raw = git(args.repo, "show", f"{args.commit}:{path}")
        items.append({"path": path, "git_blob": meta.split()[2], "sha256": hashlib.sha256(raw).hexdigest()})
    doc = {
        "schema": "brasileirao/FROZEN_VECTORS/1",
        "repo": "brasileirao-predictor",
        "commit": args.commit,
        "suite": "tests/conformance/",
        "metamorphic_seeds": [11, 23, 37, 41, 53],
        "future_canary": "FUTURE_CANARY_BR_001",
        "files": items,
    }
    with open(args.out, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(doc, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print(args.out, len(items))


if __name__ == "__main__":
    main()
