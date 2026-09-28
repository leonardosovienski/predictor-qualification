"""integration-brasileirao (C20, EVIDENCE_CONSISTENCY): todos os números dos relatórios saem de RAW_LOGS/ por este script.

Adaptado de qualification/integration-stocks/scripts/evidence_numbers.py (mesma lógica; sem as partes só do stocks, R8
e suíte do domínio). Percorre qualification/integration-brasileirao/RAW_LOGS/ (nunca edita nada lá) e grava
EVIDENCE_NUMBERS.json com, para cada número, o arquivo de origem e o sha256 dele:
  * SUMMARY.json dos cenários (conferências passadas/falhas, contadores e eventos do soak, receipts, cubos de memória);
  * *.junit.xml (testes, falhas, erros, pulados);
  * FAILURE_MATRIX_RESULTS.json; static_checks.json (C24.3); HOSTED_CI_SUMMARY.json; core_identity.json;
    protected_check.json; secrets_scan.json; final_wheels_check*.json;
  * logs de publicação (RELEASE_VERIFIED: url e sha256; REPRODUCIBLE);
  * windows-smoke: data_copy.tsv (sha256 antes/depois) e transfer_back.tsv (arquivos devolvidos ao WSL);
  * pré-voos C0 de todos os diretórios c0* (linhas CHECK, c0_falhas e ref).
Uso: python evidence_numbers.py <qualification/integration-brasileirao>
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    mission = Path(sys.argv[1])
    raw = mission / "RAW_LOGS"
    root = mission.parent.parent
    numbers: dict[str, dict] = {}

    def put(key: str, path: Path, value) -> None:
        numbers[key] = {"value": value, "source": path.relative_to(root).as_posix(), "sha256": sha(path)}

    for path in sorted(raw.rglob("SUMMARY.json")):
        doc = json.loads(path.read_text(encoding="utf-8"))
        rel = path.parent.relative_to(raw).as_posix()
        put(f"{rel}:checks_passed", path, doc.get("passed"))
        put(f"{rel}:checks_failed", path, doc.get("failed"))
        for extra in ("counters", "events", "receipts", "decisions", "domain_states", "real_env", "memory_cubes"):
            if extra in doc:
                put(f"{rel}:{extra}", path, doc[extra])
    for path in sorted(raw.rglob("*.junit.xml")):
        tree = ET.parse(path).getroot()
        suites = [tree] if tree.tag == "testsuite" else list(tree.iter("testsuite"))
        totals = {k: sum(int(s.get(k, 0)) for s in suites) for k in ("tests", "failures", "errors", "skipped")}
        put(f"{path.relative_to(raw).as_posix()}:junit", path, totals)
    for path in sorted(raw.rglob("FAILURE_MATRIX_RESULTS.json")):
        put(f"{path.relative_to(raw).as_posix()}:points", path, json.loads(path.read_text(encoding="utf-8"))["points"])
    for path in sorted(raw.rglob("static_checks.json")):
        doc = json.loads(path.read_text(encoding="utf-8"))
        put(f"{path.relative_to(raw).as_posix()}:c24_3", path, {"passed": doc["passed"], "failed": doc["failed"]})
    for path in sorted(raw.rglob("HOSTED_CI_SUMMARY.json")):
        doc = json.loads(path.read_text(encoding="utf-8"))
        put(f"{path.relative_to(raw).as_posix()}:hosted_ci", path,
            [{k: s[k] for k in ("repo", "commit", "role", "ok", "runs", "non_success_jobs")} for s in doc])
    for name in ("static.json", "release_check.json", "cycle3_check.json", "cycle4_check.json"):
        for path in sorted(raw.rglob(name)):
            doc = json.loads(path.read_text(encoding="utf-8"))
            put(f"{path.relative_to(raw).as_posix()}:checks", path, {"passed": doc["passed"], "failed": doc["failed"]})
    for path in sorted(raw.rglob("ib_f005_acceptance.json")):
        doc = json.loads(path.read_text(encoding="utf-8"))
        put(f"{path.relative_to(raw).as_posix()}:accepted", path, {"accepted": doc["accepted"], "runs": doc["runs"]})
    for name in ("core_identity.json", "final_wheels_check*.json"):
        for path in sorted(raw.rglob(name)):
            doc = json.loads(path.read_text(encoding="utf-8"))
            put(f"{path.relative_to(raw).as_posix()}:checks", path, {"passed": doc["passed"], "failed": doc["failed"]})
    for path in sorted(raw.rglob("protected_check.json")):
        doc = json.loads(path.read_text(encoding="utf-8"))
        put(f"{path.relative_to(raw).as_posix()}:protected", path,
            {"all_unchanged": doc["all_unchanged"], "items_total": doc["items_total"]})
    for path in sorted(raw.rglob("secrets_scan.json")):
        doc = json.loads(path.read_text(encoding="utf-8"))
        put(f"{path.relative_to(raw).as_posix()}:secrets", path, {"clean": doc["clean"], "findings": len(doc["findings"]),
                                                                 "scanned": doc["scanned"]})
    for path in sorted(raw.rglob("publish_*.log")):
        text = path.read_text(encoding="utf-8")
        verified = re.findall(r"RELEASE_VERIFIED=YES url=(\S+) sha256=([0-9a-f]{64})", text)
        put(f"{path.relative_to(raw).as_posix()}:release", path,
            {"reproducible": "REPRODUCIBLE=YES" in text or '"status": "PASS"' in text,
             "verified": [{"url": u, "sha256": s} for u, s in verified]})
    for path in sorted(raw.rglob("data_copy.tsv")):
        rows = [line.split("\t") for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
        put(f"{path.relative_to(raw).as_posix()}:data_copy", path,
            [{"file": r[0], "expected": r[1], "all_equal": len(set(r[1:])) == 1} for r in rows])
    for path in sorted(raw.rglob("transfer_back.tsv")):
        rows = [line.split("\t") for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
        put(f"{path.relative_to(raw).as_posix()}:transfer_back", path,
            {"files": len(rows), "bytes": sum(int(r[1]) for r in rows)})
    for path in sorted(raw.glob("c0*/c0_preflight*.log")):
        text = path.read_text(encoding="utf-8")
        match = re.search(r"^c0_falhas (\d+)$", text, re.M)
        ref = re.search(r"^ref \S+ (\w+)", text, re.M)
        put(f"{path.relative_to(raw).as_posix()}:checks", path, {"checks": len(re.findall(r"^CHECK ", text, re.M)),
                                                                "failed": int(match.group(1)) if match else None,
                                                                "ref": ref.group(1) if ref else None})
    out = mission / "EVIDENCE_NUMBERS.json"
    out.write_text(json.dumps({"schema": "integration-brasileirao/EVIDENCE_NUMBERS/1",
                               "generator": "qualification/integration-brasileirao/scripts/evidence_numbers.py",
                               "numbers": numbers}, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(out, len(numbers), "números")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
