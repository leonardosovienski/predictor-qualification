"""stocks / EVIDENCE_CONSISTENCY (C20): todo número dos relatórios sai dos logs brutos em RAW_LOGS/.

Lê junit XML (testes), pytest.log (linha final), soak.jsonl (resumo), E2E_SUMMARY.json,
NEGATIVE_CONTROLS_SUMMARY.json, external_intelligence_readiness.json e core_identity.json,
sem editar nada, e escreve EVIDENCE_NUMBERS.json. Os relatórios .md citam só estes números.

Uso: python evidence_numbers.py   (a partir de qualquer diretório)
"""

from __future__ import annotations

import hashlib
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

QC = Path(__file__).resolve().parents[1]
RAW = QC / "RAW_LOGS"


def rel(path: Path) -> str:
    return path.relative_to(QC.parents[1]).as_posix()


def junit(path: Path) -> dict:
    root = ET.parse(path).getroot()
    suites = [root] if root.tag == "testsuite" else list(root)
    totals = {"tests": 0, "failures": 0, "errors": 0, "skipped": 0}
    for suite in suites:
        for key in totals:
            totals[key] += int(suite.get(key, 0))
    totals["passed"] = totals["tests"] - totals["failures"] - totals["errors"] - totals["skipped"]
    return {"file": rel(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), **totals}


def pytest_tail(path: Path) -> dict:
    lines = [line for line in path.read_text(encoding="utf-8", errors="replace").splitlines() if line.strip()]
    summary = next((line for line in reversed(lines) if re.search(r"\d+ (passed|failed|errors?)", line)), None)
    exit_line = next((line for line in reversed(lines) if line.startswith("[exit ")), None)
    return {"file": rel(path), "summary": summary, "exit": exit_line}


def main() -> None:
    out: dict = {"generated_by": "qualification/stocks/scripts/evidence_numbers.py", "suites": {}, "runtime": {}}
    for phase_dir in sorted(p for p in RAW.iterdir() if p.is_dir()):
        for log in sorted(phase_dir.rglob("pytest.log")):
            out["suites"][rel(log)] = pytest_tail(log)
        for xml in sorted(phase_dir.rglob("*.xml")):
            out["suites"][rel(xml)] = junit(xml)
        for log in sorted(phase_dir.rglob("full_suite.log")) + sorted(phase_dir.rglob("conformance.log")):
            out["suites"][rel(log)] = pytest_tail(log)
    for run in sorted((RAW / "cleanroom-final").glob("run*/stocks-runtime-*")):
        entry: dict = {}
        e2e = run / "e2e" / "E2E_SUMMARY.json"
        if e2e.exists():
            summary = json.loads(e2e.read_text(encoding="utf-8"))
            entry["e2e"] = {"file": rel(e2e), "checks": len(summary["checks"]),
                            "checks_ok": sum(1 for c in summary["checks"] if c["ok"]), "all_ok": summary["all_ok"],
                            "authority_cases": len(summary["cases"])}
        soak = run / "soak.jsonl"
        if soak.exists():
            rows = [json.loads(line) for line in soak.read_text(encoding="utf-8").splitlines() if line.strip()]
            final = next(r for r in rows if r["kind"] == "summary")
            verdict = next(r for r in rows if r["kind"] == "verdict")
            entry["soak"] = {"file": rel(soak), "process_calls": sum(1 for r in rows if r["kind"] == "process"),
                             "faults_injected": sum(1 for r in rows if r["kind"] == "process" and r.get("fault")),
                             **{k: final[k] for k in ("requests_with_result", "stored_results", "domain_effects",
                                                      "ops_jobs", "ops_success_per_job_max", "eligible_trials")},
                             "lost": len(final["lost"]), "unexpected": len(final["unexpected"]),
                             "reread_mismatch": len(final["reread_mismatch"]), "violations": len(final["violations"]),
                             "pit_violations": len(final["pit_violations"]),
                             "zero_tolerance_ok": verdict["zero_tolerance_ok"]}
        science = run / "science" / "NEGATIVE_CONTROLS_SUMMARY.json"
        if science.exists():
            summary = json.loads(science.read_text(encoding="utf-8"))
            entry["negative_controls"] = {"file": rel(science), "supported_counts": summary["supported_counts"],
                                          "criteria_ok": {k: v["ok"] for k, v in summary["criteria"].items()},
                                          "reference": {k: summary["reference"][k] for k in (
                                              "scientific_state", "economic_state", "excess_gross_bps",
                                              "excess_gross_ci_bps", "excess_net_ci_bps", "periods")}}
        readiness = run / "science" / "external_intelligence_readiness.json"
        if readiness.exists():
            doc = json.loads(readiness.read_text(encoding="utf-8"))
            entry["external_intelligence"] = {"file": rel(readiness), "ready_families": doc["ready_families"],
                                              "families": len(doc["families"]),
                                              "consumption_allowed": [f for f, v in doc["families"].items()
                                                                      if v["consumption_for_trial"]["allowed"]]}
        identity = run / "core_identity.json"
        if identity.exists():
            doc = json.loads(identity.read_text(encoding="utf-8"))
            entry["identity"] = {p["name"]: {"version": p["version"],
                                             "sha256": ((p.get("direct_url") or {}).get("archive_info") or {}).get("hash"),
                                             "in_site_packages": p["module_in_site_packages"], "editable": p["editable"]}
                                 for p in doc["packages"]}
            entry["lock_chain"] = {c["name"]: {"spec": c["pyproject_spec"], "lock_version": c["lock_version"],
                                               "lock_sha256": c["lock_wheel_sha256"]} for c in doc["lock_chain"]}
        out["runtime"][rel(run)] = entry
    target = QC / "EVIDENCE_NUMBERS.json"
    target.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"{rel(target)}: {len(out['suites'])} suites, {len(out['runtime'])} runtimes")


if __name__ == "__main__":
    main()
