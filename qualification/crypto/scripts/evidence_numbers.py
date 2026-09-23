"""C20 (EVIDENCE_CONSISTENCY): todos os números dos relatórios da missão crypto, tirados só
de logs brutos em qualification/crypto/RAW_LOGS (junit XML, jsonl, logs de pytest, JSONs
gerados por scripts). Nenhum número é digitado à mão.

Uso: python evidence_numbers.py   → escreve qualification/crypto/EVIDENCE_NUMBERS.json
"""

from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "qualification" / "crypto" / "RAW_LOGS"
RUNTIME_RUN = "run35885023422"


def junit(path: Path) -> dict:
    tree = ET.parse(path)
    suites = [tree.getroot()] if tree.getroot().tag == "testsuite" else list(tree.getroot())
    total = {"tests": 0, "failures": 0, "errors": 0, "skipped": 0}
    failed = []
    for suite in suites:
        for key in total:
            total[key] += int(suite.get(key, 0))
        for case in suite.iter("testcase"):
            if case.find("failure") is not None or case.find("error") is not None:
                failed.append(f"{case.get('classname')}::{case.get('name')}")
    total["passed"] = total["tests"] - total["failures"] - total["errors"] - total["skipped"]
    return {"file": str(path.relative_to(ROOT)).replace("\\", "/"), **total, "failed": failed}


def pytest_line(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    line = next((l for l in reversed(text.splitlines()) if re.search(r"\d+ (passed|failed)", l)), "")
    counts = {k: int(v) for v, k in re.findall(r"(\d+) (passed|failed|errors?|skipped)", line)}
    exit_m = re.search(r"(?:pytest exit=|\[exit )(\d+)", text)
    return {"file": str(path.relative_to(ROOT)).replace("\\", "/"), "summary": line.strip(), **counts,
            "exit": int(exit_m.group(1)) if exit_m else None}


def jsonl_kind(path: Path, kind: str) -> dict | None:
    for line in path.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        if row.get("kind") == kind:
            return row
    return None


def main() -> None:
    n: dict = {}
    n["baseline_windows_suite"] = pytest_line(RAW / "baseline" / "windows_pytest_5fd4e1b_run2.log")
    n["baseline_windows_suite_method_error"] = pytest_line(RAW / "baseline" / "windows_pytest_5fd4e1b.log")
    for h in ("9844976", "6f73051", "2bafad9", "2bc63eb"):
        p = RAW / "contract-wiring" / f"windows_pytest_{h}.log"
        if p.exists():
            n[f"checkout_windows_suite_{h}"] = pytest_line(p)
    ops = json.loads((RAW / "ops-failure" / "OPS_FAILURE_SUMMARY.json").read_text(encoding="utf-8"))["sources"]
    iso = [0, 0]
    for envs in ops.values():
        for d in envs.values():
            if d["setup_failed"]:
                continue
            iso[0] += d["shared003_test"]["executions_all_passed"]
            iso[1] += d["shared003_test"]["executions"]
    n["shared003_isolated_test_executions"] = {"passed": iso[0], "total": iso[1]}
    lockrace = sorted((RAW / "ops-failure" / "windows-local-lockrace").glob("*_run*.log"))
    n["shared005_lockrace_isolated"] = {
        variant: {"runs": sum(1 for p in lockrace if p.name.startswith(variant)),
                  "failed": sum(1 for p in lockrace if p.name.startswith(variant)
                                and "[exit 0]" not in p.read_text(encoding="utf-8", errors="replace"))}
        for variant in ("source", "wheel")}
    guard = [json.loads(l) for l in (RAW / "ops-failure" / "windows-local-lockrace" / "guard_ab_wheel.jsonl")
             .read_text(encoding="utf-8").splitlines() if l.strip()]
    n["shared005_guard_ab"] = {c: {"runs": sum(1 for g in guard if g["case"] == c),
                                   "permission_error": sum(1 for g in guard if g["case"] == c and "PermissionError" in g.get("exception", "")),
                                   "entered": sum(1 for g in guard if g["case"] == c and g.get("entered"))}
                               for c in ("A_empty_guard", "B_initialized_guard")}
    rt = RAW / "cleanroom-final" / RUNTIME_RUN
    for env in ("linux-primary", "windows-latest"):
        p = rt / f"crypto-runtime-{env}"
        n[f"runtime_{env}"] = {
            "conformance": junit(p / "conformance.junit.xml"),
            "full_suite": junit(p / "full_suite.junit.xml"),
            "e2e": json.loads((p / "e2e" / "E2E_SUMMARY.json").read_text(encoding="utf-8"))["all_ok"],
            "e2e_checks": len(json.loads((p / "e2e" / "E2E_SUMMARY.json").read_text(encoding="utf-8"))["checks"]),
        }
        if (p / "soak.jsonl").exists():
            summary = jsonl_kind(p / "soak.jsonl", "summary")
            verdict = jsonl_kind(p / "soak.jsonl", "verdict")
            calls = sum(1 for l in (p / "soak.jsonl").read_text(encoding="utf-8").splitlines()
                        if json.loads(l).get("kind") == "process")
            n[f"runtime_{env}"]["soak"] = {"process_calls": calls, **{k: summary[k] for k in (
                "requests_with_result", "stored_results", "domain_effects", "ops_jobs", "ops_success_per_job_max",
                "lost", "unexpected", "reread_mismatch", "violations", "reconcile_exit")},
                "zero_tolerance_ok": verdict["zero_tolerance_ok"]}
    local = RAW / "windows-smoke" / "local"
    n["runtime_windows_local"] = {
        "conformance": junit(local / "conformance.junit.xml"),
        "temporal_suites": junit(local / "temporal_suites.junit.xml"),
        "e2e_real": json.loads((local / "e2e_real" / "E2E_SUMMARY.json").read_text(encoding="utf-8"))["all_ok"],
        "e2e_real_checks": len(json.loads((local / "e2e_real" / "E2E_SUMMARY.json").read_text(encoding="utf-8"))["checks"]),
    }
    science = json.loads((local / "science" / "SCIENCE_REAL.json").read_text(encoding="utf-8"))
    n["science_real"] = {"economic_metrics": science["economic_metrics"],
                         "negative_controls": science["negative_controls"],
                         "future_canary": {"leaks": len(science["future_canary"]["leaks"])}}
    protected = json.loads((RAW / "final" / "protected_set_check_2bc63eb.json").read_text(encoding="utf-8"))
    n["protected_set"] = {"items": protected["items"], "unchanged": protected["unchanged"],
                          "changed_or_missing": len(protected["changed_or_missing"])}
    out = ROOT / "qualification" / "crypto" / "EVIDENCE_NUMBERS.json"
    out.write_text(json.dumps(n, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: (v if not isinstance(v, dict) else {kk: vv for kk, vv in v.items()
                                                            if not isinstance(vv, (dict, list))})
                      for k, v in n.items()}, ensure_ascii=False)[:3000])


if __name__ == "__main__":
    main()
