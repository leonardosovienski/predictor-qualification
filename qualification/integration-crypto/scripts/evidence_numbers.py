"""integration-crypto (C20, EVIDENCE_CONSISTENCY): todos os números dos relatórios saem de RAW_LOGS/ por este script.

Percorre qualification/integration-crypto/RAW_LOGS/ (nunca edita nada lá) e grava EVIDENCE_NUMBERS.json com, para
cada número, o arquivo de origem e o sha256 dele:
  * SUMMARY.json dos cenários (conferências passadas/falhas, contadores do soak, receipts do N+1);
  * *.junit.xml (testes, falhas, erros, pulados);
  * FAILURE_MATRIX_RESULTS.json; static_checks.json (C24.3); HOSTED_CI_SUMMARY.json;
  * logs de publicação (RELEASE_VERIFIED: url e sha256) e o RESUMO do C0.
Uso: python evidence_numbers.py <qualification/integration-crypto>
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
        for extra in ("counters", "receipts", "decisions"):
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
    for path in sorted(raw.rglob("publish_*.log")):
        text = path.read_text(encoding="utf-8")
        verified = re.findall(r"RELEASE_VERIFIED=YES url=(\S+) sha256=([0-9a-f]{64})", text)
        put(f"{path.relative_to(raw).as_posix()}:release", path,
            {"reproducible": "REPRODUCIBLE=YES" in text, "verified": [{"url": u, "sha256": s} for u, s in verified]})
    c0 = raw / "c0" / "c0_preflight.log"
    if c0.is_file():
        match = re.search(r"RESUMO checks=(\d+) ok=(\d+)", c0.read_text(encoding="utf-8"))
        put("c0:checks", c0, {"checks": int(match.group(1)), "ok": int(match.group(2))} if match else None)
    out = mission / "EVIDENCE_NUMBERS.json"
    out.write_text(json.dumps({"schema": "integration-crypto/EVIDENCE_NUMBERS/1",
                               "generator": "qualification/integration-crypto/scripts/evidence_numbers.py",
                               "numbers": numbers}, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(out, len(numbers), "números")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
