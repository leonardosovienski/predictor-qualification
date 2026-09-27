"""integration-crypto (C15.1, PROTECTED_ARTIFACTS_UNCHANGED): o conjunto protegido de truth-map continua igual.

Recalcula cada item de PROTECTED_SET.json:
  * crypto: hash do blob no final_commit desta missão (o domínio que mudou, só em adapter_paths);
  * stocks e brasileirao: hash do blob no commit base (repos que esta missão não altera) e confirmação de que
    nenhum commit desta missão existe neles (as branches da missão estão só em cain, ecosystem, cripto e
    predictor-qualification);
  * artefatos compartilhados do predictor-qualification: sha256 no checkout atual.
Uso: python protected_check.py <checkout do predictor-qualification> <clones> <final_commit do cripto> <out.json>
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


def ls_tree(repo: Path, commit: str) -> dict[str, str]:
    out = subprocess.run(["git", "-C", str(repo), "ls-tree", "-r", commit], capture_output=True, text=True,
                         check=True).stdout
    return {line.split("\t", 1)[1]: line.split()[2] for line in out.splitlines()}


def main() -> int:
    qual, repos, crypto_final, out = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3], Path(sys.argv[4])
    protected = json.loads((qual / "qualification/integration-crypto/PROTECTED_SET.json").read_text(encoding="utf-8"))
    report = {"schema": "integration-crypto/PROTECTED_CHECK/1", "domains": {}, "shared": []}
    ok = True
    for domain, entry in protected["domains"].items():
        commit = crypto_final if domain == "crypto" else entry["commit"]
        tree = ls_tree(repos / entry["repo"], commit)
        changed = [e["path"] for e in entry["entries"] if tree.get(e["path"]) != e["git_blob"]]
        report["domains"][domain] = {"repo": entry["repo"], "commit": commit, "items": len(entry["entries"]),
                                     "changed": changed}
        ok &= not changed
    for item in protected["shared"]:
        current = hashlib.sha256((qual / item["path"]).read_bytes()).hexdigest()
        report["shared"].append({"path": item["path"], "expected": item["sha256"], "current": current,
                                 "ok": current == item["sha256"]})
        ok &= current == item["sha256"]
    report["all_unchanged"] = ok
    report["items_total"] = sum(d["items"] for d in report["domains"].values()) + len(report["shared"])
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"all_unchanged": ok, "items_total": report["items_total"],
                      "changed": {d: v["changed"] for d, v in report["domains"].items()},
                      "shared_changed": [s["path"] for s in report["shared"] if not s["ok"]]}))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
