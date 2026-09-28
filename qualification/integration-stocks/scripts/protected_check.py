"""integration-stocks (C15.1, PROTECTED_ARTIFACTS_UNCHANGED): o conjunto protegido de truth-map continua igual.

Recalcula cada item de PROTECTED_SET.json:
  * stocks: hash do blob no final_commit desta missão (o domínio que mudou, só em adapter_paths e D-24 (4));
  * crypto e brasileirao: hash do blob no commit base do truth-map (repos que esta missão não altera);
  * artefatos compartilhados do predictor-qualification: sha256 no checkout atual.
  Um QUALIFICATION_ATTESTATION.json alterado ganha, só como registro, o arquivo _superseded_ com os bytes esperados
  e o supersedes_sha256 da attestation atual (o item continua contado como alterado).
Ciclo 2 (IS-F008, decisão do dono de 2026-09-28, opção (a) "Encadeada"): os quatro itens trocados pelo ciclo 2
(congelados desta missão e da integration-crypto, attestation da integration-crypto) contam como alterados pela letra
(all_unchanged) e como encadeados só se a cadeia de ponteiros, salto a salto, chegar ao sha256 protegido com cada
arquivo preservado nos bytes que o ponteiro diz (all_unchanged_or_chained, o que o gate usa). Todo outro item
alterado continua FAIL.
Cadeia sem limite fixo de saltos (pedido do dono de 2026-09-28, "Resolve"): até o ciclo 4 a cadeia parava em 5
saltos, e a attestation da integration-crypto já estava em 5 depois da C14 na rc13. A cadeia agora segue até o sha256
protegido, até um documento sem ponteiro, até um arquivo com bytes diferentes do ponteiro ou até um arquivo já
visitado (ciclo, sempre FAIL). O teto CHAIN_GUARD só impede laço sem fim e nunca é atingido por uma cadeia real. Cada
cadeia diz por que parou (stop). A regra do IS-F008 não muda.
Adaptado de qualification/integration-crypto/scripts/protected_check.py (mesma lógica; missão integration-stocks).
Uso: python protected_check.py <checkout do predictor-qualification> <clones> <final_commit do stocks> <out.json>
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

CHAINED_ITEMS = {  # IS-F008 (a)
    "qualification/integration-stocks/FROZEN_PARAMETERS.json",
    "qualification/integration-stocks/FROZEN_VECTORS.json",
    "qualification/integration-crypto/FROZEN_PARAMETERS.json",
    "qualification/integration-crypto/QUALIFICATION_ATTESTATION.json",
}
CHAIN_GUARD = 1000  # só contra laço sem fim; uma cadeia real para antes (ciclo, sha256 protegido ou fim)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pointer(path: Path) -> tuple[str, str] | None:
    """(arquivo preservado, sha256) para onde o documento aponta: cycle.supersedes nos congelados, supersedes_sha256
    + QUALIFICATION_ATTESTATION_superseded_<sha12>.json nas attestations."""
    doc = json.loads(path.read_text(encoding="utf-8"))
    supersedes = doc.get("cycle", {}).get("supersedes") if isinstance(doc.get("cycle"), dict) else None
    if supersedes:
        return supersedes["file"], supersedes["sha256"]
    if doc.get("supersedes_sha256"):
        return f"QUALIFICATION_ATTESTATION_superseded_{doc['supersedes_sha256'][:12]}.json", doc["supersedes_sha256"]
    return None


def chain(path: Path, expected: str) -> dict:
    hops, current, ok, stop = [], path, False, "guard"
    seen = {path.name}
    for _ in range(CHAIN_GUARD):
        target = pointer(current)
        if target is None:
            stop = "no_pointer"
            break
        kept = current.with_name(target[0])
        if kept.name in seen:
            stop = "cycle"
            break
        seen.add(kept.name)
        kept_sha = sha(kept) if kept.is_file() else None
        hops.append({"file": kept.name, "pointer_sha256": target[1], "file_sha256": kept_sha})
        if kept_sha != target[1]:
            stop = "bytes_differ" if kept_sha else "missing"
            break
        if kept_sha == expected:
            ok, stop = True, "protected_sha256"
            break
        current = kept
    return {"hops": hops, "ok": ok, "stop": stop,
            "decision": "IS-F008 (dono, 2026-09-28: \"(a) Encadeada (Recomendado)\")"}


def ls_tree(repo: Path, commit: str) -> dict[str, str]:
    out = subprocess.run(["git", "-C", str(repo), "ls-tree", "-r", commit], capture_output=True, text=True,
                         check=True).stdout
    return {line.split("\t", 1)[1]: line.split()[2] for line in out.splitlines()}


def main() -> int:
    qual, repos, stocks_final, out = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3], Path(sys.argv[4])
    protected = json.loads((qual / "qualification/integration-stocks/PROTECTED_SET.json").read_text(encoding="utf-8"))
    report = {"schema": "integration-stocks/PROTECTED_CHECK/1", "domains": {}, "shared": []}
    ok = True
    chained_ok = True
    for domain, entry in protected["domains"].items():
        commit = stocks_final if domain == "stocks" else entry["commit"]
        tree = ls_tree(repos / entry["repo"], commit)
        changed = [e["path"] for e in entry["entries"] if tree.get(e["path"]) != e["git_blob"]]
        report["domains"][domain] = {"repo": entry["repo"], "commit": commit, "items": len(entry["entries"]),
                                     "changed": changed}
        ok &= not changed
        chained_ok &= not changed
    for item in protected["shared"]:
        path = qual / item["path"]
        current = hashlib.sha256(path.read_bytes()).hexdigest()
        row = {"path": item["path"], "expected": item["sha256"], "current": current, "ok": current == item["sha256"]}
        if not row["ok"] and path.name == "QUALIFICATION_ATTESTATION.json":
            # só registro (não muda o ok): attestation reemitida (C7.1 regra 8) com os bytes esperados preservados
            kept = path.with_name(f"QUALIFICATION_ATTESTATION_superseded_{item['sha256'][:12]}.json")
            row["supersession"] = {
                "superseded_file": kept.relative_to(qual).as_posix(),
                "superseded_file_sha256": hashlib.sha256(kept.read_bytes()).hexdigest() if kept.is_file() else None,
                "current_supersedes_sha256": json.loads(path.read_text(encoding="utf-8")).get("supersedes_sha256")}
        if not row["ok"] and item["path"] in CHAINED_ITEMS:
            row["chain"] = chain(path, item["sha256"])
        report["shared"].append(row)
        ok &= row["ok"]
        chained_ok &= row["ok"] or row.get("chain", {}).get("ok", False)
    report["all_unchanged"] = ok
    report["all_unchanged_or_chained"] = chained_ok
    report["chained_items"] = [s["path"] for s in report["shared"] if s.get("chain", {}).get("ok")]
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
