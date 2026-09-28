"""integration-stocks (C20, EVIDENCE_CONSISTENCY): todos os números dos relatórios saem de RAW_LOGS/ por este script.

Adaptado de qualification/integration-crypto/scripts/evidence_numbers.py (mesma lógica). Percorre
qualification/integration-stocks/RAW_LOGS/ (nunca edita nada lá) e grava EVIDENCE_NUMBERS.json com, para cada número,
o arquivo de origem e o sha256 dele:
  * SUMMARY.json dos cenários (conferências passadas/falhas, contadores do soak, receipts do N+1, decisões);
  * *.junit.xml (testes, falhas, erros, pulados);
  * FAILURE_MATRIX_RESULTS.json; static_checks.json (C24.3); HOSTED_CI_SUMMARY.json; core_identity.json;
    protected_check.json; secrets_scan.json; final_wheels_check*.json;
  * logs de publicação (RELEASE_VERIFIED: url e sha256), do procedimento R8, da suíte local do Stocks e das
    reexecuções de passo dela (stocks_*_rerun_*.log);
  * pré-voos C0 (linhas CHECK e c0_falhas).
Uso: python evidence_numbers.py <qualification/integration-stocks>
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
        for extra in ("counters", "receipts", "decisions", "domain_states", "real_env", "memory_cubes"):
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
    r8 = raw / "domain-adapter" / "r8_procedure.log"
    if r8.is_file():
        text = r8.read_text(encoding="utf-8")
        put("domain-adapter:r8", r8, {
            "source_sha256_before": re.search(r"source_sha256_before (\w+)", text).group(1),
            "source_sha256_after": re.search(r"source_sha256_after (\w+)", text).group(1),
            "real": re.search(r"^real (\w+) (\d+) ", text, re.M).groups(),
            "capacity": re.search(r"^capacity (\w+) (\d+)", text, re.M).groups(),
            "seal_code_files": int(re.search(r'"code_files": (\d+)', text).group(1)),
            "verify": re.search(r'"current_revision_status": "(\w+)"', text).group(1)})
    suite = raw / "domain-adapter" / "stocks_suite_6f857b2.log"
    if suite.is_file():
        text = suite.read_text(encoding="utf-8")
        put("domain-adapter:stocks_suite", suite, {
            "steps": dict(re.findall(r"^\[(\w+) exit (\d+)\]", text, re.M)),
            "tests": re.search(r"(\d+) passed, (\d+) subtests passed", text).groups(),
            "coverage_total": re.search(r"^TOTAL\s.*?(\d+)%$", text, re.M).group(1),
            "dirty_before": re.search(r"dirty_before (\d+)", text).group(1),
            "dirty_after": re.search(r"dirty_after (\d+)", text).group(1)})
    for rerun in sorted((raw / "domain-adapter").glob("stocks_*_rerun_*.log")):
        text = rerun.read_text(encoding="utf-8")
        put(f"domain-adapter:{rerun.stem}", rerun, {
            "steps": dict(re.findall(r"^\[(\w+) exit (\d+)\]", text, re.M)),
            "head": re.search(r" head (\w+)", text).group(1),
            "dirty_after": re.search(r"dirty_after (\d+)", text).group(1)})
    for path in sorted((raw / "c0").glob("*.log")):
        text = path.read_text(encoding="utf-8")
        match = re.search(r"^c0_falhas (\d+)$", text, re.M)
        put(f"c0/{path.name}:checks", path, {"checks": len(re.findall(r"^CHECK ", text, re.M)),
                                             "failed": int(match.group(1)) if match else None,
                                             "ref": re.search(r"^ref \S+ (\w+)", text, re.M).group(1)})
    out = mission / "EVIDENCE_NUMBERS.json"
    out.write_text(json.dumps({"schema": "integration-stocks/EVIDENCE_NUMBERS/1",
                               "generator": "qualification/integration-stocks/scripts/evidence_numbers.py",
                               "numbers": numbers}, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(out, len(numbers), "números")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
