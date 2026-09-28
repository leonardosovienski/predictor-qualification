"""integration-crypto (C15.1, PROTECTED_ARTIFACTS_UNCHANGED): o conjunto protegido de truth-map continua igual.

Recalcula cada item de PROTECTED_SET.json:
  * crypto: hash do blob no final_commit desta missão (o domínio que mudou, só em adapter_paths);
  * stocks e brasileirao: hash do blob no commit base (repos que esta missão não altera) e confirmação de que
    nenhum commit desta missão existe neles (as branches da missão estão só em cain, ecosystem, cripto e
    predictor-qualification);
  * artefatos compartilhados do predictor-qualification: sha256 no checkout atual.
Ciclos 2 e 3 (IC-F011, decisões do dono de 2026-09-28): o FROZEN_PARAMETERS.json desta missão reemitido como novo
ciclo conta como alterado pela letra da C15.1; fica registrado como encadeado só se a cadeia do atual (cycle.supersedes
e cycle.chain, do mais novo ao mais antigo) chegar a um arquivo guardado (FROZEN_PARAMETERS_cycle<n>_<sha12>.json)
com os bytes protegidos, e se cada elo for um arquivo guardado com o sha256 que declara. ``all_unchanged`` continua sendo a letra; ``all_unchanged_or_chained`` é o que o gate usa, pela decisão.
Uso: python protected_check.py <checkout do predictor-qualification> <clones> <final_commit do cripto> <out.json>
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


CHAINED_ITEM = "qualification/integration-crypto/FROZEN_PARAMETERS.json"


def chain(path: Path, expected: str) -> dict:
    """The reissued frozen parameters reach, through cycle.supersedes and cycle.chain (newest first), a kept file with
    exactly the protected bytes; every link on the way must be a kept file with the sha256 it declares."""
    cycle = json.loads(path.read_text(encoding="utf-8")).get("cycle", {})
    checked = []
    for link in [cycle.get("supersedes", {}), *cycle.get("chain", [])]:
        kept = path.with_name(link.get("file", "")) if link.get("file") else None
        sha = hashlib.sha256(kept.read_bytes()).hexdigest() if kept and kept.is_file() else None
        checked.append({"file": kept.name if kept else None, "declared_sha256": link.get("sha256"),
                        "file_sha256": sha, "ok": sha is not None and sha == link.get("sha256")})
    hit = next((c for c in checked if c["declared_sha256"] == expected), None)
    return {"superseded_file": hit["file"] if hit else None,
            "superseded_file_sha256": hit["file_sha256"] if hit else None,
            "current_supersedes_sha256": cycle.get("supersedes", {}).get("sha256"), "links": checked,
            "ok": hit is not None and hit["file_sha256"] == expected and all(c["ok"] for c in checked),
            "decision": "IC-F011 (dono, 2026-09-28: \"Aprovo; reemissão encadeada\"); ciclo 3: \"Aprovo\""}


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
    chained_ok = ok
    for item in protected["shared"]:
        path = qual / item["path"]
        current = hashlib.sha256(path.read_bytes()).hexdigest()
        entry = {"path": item["path"], "expected": item["sha256"], "current": current, "ok": current == item["sha256"]}
        if not entry["ok"] and item["path"] == CHAINED_ITEM:
            entry["chain"] = chain(path, item["sha256"])
        report["shared"].append(entry)
        ok &= entry["ok"]
        chained_ok &= entry["ok"] or entry.get("chain", {}).get("ok", False)
    report["all_unchanged"] = ok
    report["all_unchanged_or_chained"] = chained_ok
    report["chained_items"] = [s["path"] for s in report["shared"] if "chain" in s]
    report["items_total"] = sum(d["items"] for d in report["domains"].values()) + len(report["shared"])
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"all_unchanged": ok, "all_unchanged_or_chained": chained_ok,
                      "chained_items": report["chained_items"], "items_total": report["items_total"],
                      "changed": {d: v["changed"] for d, v in report["domains"].items()},
                      "shared_changed": [s["path"] for s in report["shared"] if not s["ok"]]}))
    return 0 if chained_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
