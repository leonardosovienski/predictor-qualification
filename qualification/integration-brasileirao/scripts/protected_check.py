"""integration-brasileirao (C15.1, PROTECTED_ARTIFACTS_UNCHANGED): o conjunto protegido do truth-map continua igual.

Adaptado de qualification/integration-stocks/scripts/protected_check.py. Recalcula cada item de PROTECTED_SET.json:
  * brasileirao: hash do blob no final_commit desta missão (o domínio mudou só em brasileirao_predictor/adapters/ e
    na versão; nenhum item protegido pode ter mudado);
  * crypto e stocks: cada item dos arquivos-fonte da Etapa A (PROTECTED_SET.json e FROZEN_VECTORS.json, com o sha256
    registrado no truth-map) pelo hash do blob no commit base (repos que esta missão não altera);
  * artefatos compartilhados do predictor-qualification: sha256 no checkout atual.
Regra da cadeia preservada (decisão do dono, 2026-09-28, "Cadeia preservada", mesmo critério do IS-F006 (a) da
integration-stocks): um artefato compartilhado com sha256 diferente do truth-map conta como inalterado SÓ se os bytes do
truth-map estão, byte a byte (sha256 conferido), num arquivo <nome>_cycle<N>_<sha12>.json ou
QUALIFICATION_ATTESTATION_superseded_<sha12>.json do mesmo diretório. Qualquer outra diferença é FAIL.
Uso: python protected_check.py <checkout do predictor-qualification> <clones> <final_commit do brasileirao> <out.json>
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

M = "qualification/integration-brasileirao"


def ls_tree(repo: Path, commit: str) -> dict[str, str]:
    out = subprocess.run(["git", "-C", str(repo), "ls-tree", "-r", commit], capture_output=True, text=True,
                         check=True).stdout
    return {line.split("\t", 1)[1]: line.split()[2] for line in out.splitlines()}


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def preserved(path: Path, expected: str) -> Path | None:
    """The file in the same directory that keeps the truth-map bytes (cycle or superseded), if any."""
    stem = re.escape(path.stem)
    pattern = re.compile(rf"({stem}_cycle\d+|{stem}_superseded)_{expected[:12]}\.json\Z")
    for candidate in sorted(path.parent.iterdir()):
        if pattern.match(candidate.name) and sha(candidate.read_bytes()) == expected:
            return candidate
    return None


def main() -> int:
    qual, repos, br_final, out = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3], Path(sys.argv[4])
    protected = json.loads((qual / M / "PROTECTED_SET.json").read_text(encoding="utf-8"))
    report = {"schema": "integration-brasileirao/PROTECTED_CHECK/1",
              "rule": "cadeia preservada (decisão do dono 2026-09-28; IS-F006 (a))", "domains": {}, "shared": []}
    ok = True
    for domain, entry in protected["domains"].items():
        commit = br_final if domain == "brasileirao" else entry["commit"]
        tree = ls_tree(repos / entry["repo"], commit)
        if "entries" in entry:
            items = entry["entries"]
            sources_ok = True
        else:
            items, sources_ok = [], True
            for source, expected in entry["sources"].items():
                raw = (qual / f"qualification/{domain}/{source}").read_bytes()
                sources_ok &= sha(raw) == expected
                doc = json.loads(raw)
                items += doc.get("items") if source == "PROTECTED_SET.json" else doc.get("files")
        changed = [i["path"] for i in items if tree.get(i["path"]) != i["git_blob"]]
        report["domains"][domain] = {"repo": entry["repo"], "commit": commit, "items": len(items),
                                     "expected_items": entry["items"], "sources_unchanged": sources_ok,
                                     "changed": changed}
        ok &= not changed and sources_ok and len(items) == entry["items"]
    for item in protected["shared"]:
        path = qual / item["path"]
        current = sha(path.read_bytes())
        row = {"path": item["path"], "expected": item["sha256"], "current": current,
               "unchanged": current == item["sha256"]}
        if not row["unchanged"]:
            kept = preserved(path, item["sha256"])
            row["preserved_in"] = kept.relative_to(qual).as_posix() if kept else None
        row["ok"] = row["unchanged"] or bool(row.get("preserved_in"))
        report["shared"].append(row)
        ok &= row["ok"]
    report["all_unchanged"] = ok
    report["items_total"] = sum(d["items"] for d in report["domains"].values()) + len(report["shared"])
    report["shared_changed_preserved"] = [s["path"] for s in report["shared"] if not s["unchanged"] and s["ok"]]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"all_unchanged": ok, "items_total": report["items_total"],
                      "changed": {d: v["changed"] for d, v in report["domains"].items()},
                      "shared_changed_preserved": report["shared_changed_preserved"],
                      "shared_failed": [s["path"] for s in report["shared"] if not s["ok"]]}))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
