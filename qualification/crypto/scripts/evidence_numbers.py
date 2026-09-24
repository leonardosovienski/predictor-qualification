"""C20 (EVIDENCE_CONSISTENCY): todos os números dos relatórios da missão crypto, tirados só
de logs brutos em qualification/crypto/RAW_LOGS (junit XML, jsonl, logs de pytest, JSONs
gerados por scripts). Nenhum número é digitado à mão.

Uso: python evidence_numbers.py   → escreve qualification/crypto/EVIDENCE_NUMBERS.json
     --d16 d16/<run_id>          → acrescenta a seção "d16" (saída bruta de d16_linux.sh)
"""

from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "qualification" / "crypto" / "RAW_LOGS"
import argparse

_ap = argparse.ArgumentParser()
_ap.add_argument("--runtime-run", default="run35885023422")
_ap.add_argument("--local", default="windows-smoke/local")
_ap.add_argument("--protected", default="final/protected_set_check_2bc63eb.json")
_ap.add_argument("--ops-summary", default="ops-failure/OPS_FAILURE_SUMMARY.json")
_ap.add_argument("--out", default="EVIDENCE_NUMBERS.json")
_ap.add_argument("--d16", help="pasta da execução D-16 dentro de RAW_LOGS (ex.: d16/<run_id>)")
ARGS = _ap.parse_args()
RUNTIME_RUN = ARGS.runtime_run


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


SOAK_FIELDS = ("requests_with_result", "stored_results", "domain_effects", "ops_jobs", "ops_success_per_job_max",
               "lost", "unexpected", "reread_mismatch", "violations", "reconcile_exit")


def d16(d: Path) -> dict:
    """Números da execução D-16 (d16_linux.sh), só dos arquivos brutos da pasta."""
    env = (d / "env.log").read_text(encoding="utf-8", errors="replace")
    head = dict(re.findall(r"(\w+)=(\S+)", env.splitlines()[0])) if env.strip() else {}
    exits = {}
    for step in ("e2e_real", "e2e_cases", "science", "soak_real", "conformance"):
        found = re.findall(r"\[exit (\d+)\]", (d / f"{step}.log").read_text(encoding="utf-8", errors="replace"))
        exits[step] = int(found[-1]) if found else None
    manifest = json.loads((d / "data_MANIFEST.json").read_text(encoding="utf-8"))
    files = [f for f in manifest["files"] if "copy_sha256" in f]
    e2e = json.loads((d / "e2e_real" / "E2E_SUMMARY.json").read_text(encoding="utf-8"))
    cases = json.loads((d / "e2e_cases" / "E2E_SUMMARY.json").read_text(encoding="utf-8"))
    science = json.loads((d / "science" / "SCIENCE_REAL.json").read_text(encoding="utf-8"))
    soak = d / "soak_real.jsonl"
    rows = [json.loads(l) for l in soak.read_text(encoding="utf-8").splitlines() if l.strip()]
    summary = next(r for r in rows if r["kind"] == "summary")
    verdict = next(r for r in rows if r["kind"] == "verdict")
    process = [r for r in rows if r["kind"] == "process"]
    corruptions = [r for r in rows if r["kind"] == "corruption"]
    faults: dict[str, int] = {}
    for r in process:
        faults[r.get("fault") or "none"] = faults.get(r.get("fault") or "none", 0) + 1
    return {
        "dir": str(d.relative_to(ROOT)).replace("\\", "/"),
        "env": {"where": head.get("where"), "commit": head.get("commit"), "wheel_sha256": head.get("sha256"),
                "done": re.search(r"^done ", env, re.M) is not None,
                "setup_fail": "SETUP FAIL" in env, "blocked": "BLOCKED" in env},
        "step_exits": exits,
        "data_manifest": {"files": len(files),
                          "checksum_ok": sum(1 for f in files if f["published_sha256"] == f["copy_sha256"]),
                          "unavailable": [f["url"] for f in manifest["files"] if "unavailable" in f],
                          "objects": manifest["objects"]},
        "e2e_real": {"all_ok": e2e["all_ok"], "checks": len(e2e["checks"])},
        "e2e_cases": {"all_ok": cases["all_ok"], "checks": len(cases["checks"])},
        "conformance": junit(d / "conformance.junit.xml"),
        "soak": {"process_calls": len(process), "faults": dict(sorted(faults.items())),
                 **{k: summary[k] for k in SOAK_FIELDS},
                 "reconcile_findings": len(summary.get("reconcile_findings") or []),
                 "corruptions_injected": len(corruptions),
                 "corruptions_fail_closed": sum(1 for r in corruptions if r["show_exit"] == 5 and r["retry_exit"] == 5
                                                and r["file_not_repaired"]),
                 "reconcile_foreign_findings": len(summary.get("reconcile_foreign_findings") or []),
                 "reconcile_missed_corruptions": len(summary.get("reconcile_missed_corruptions") or []),
                 "zero_tolerance_ok": verdict["zero_tolerance_ok"]},
        "science": {"economic_metrics": science["economic_metrics"],
                    "negative_controls": science["negative_controls"],
                    "future_canary": {"leaks": len(science["future_canary"]["leaks"]),
                                      "pass": science["future_canary"]["pass"]}},
    }


def main() -> None:
    n: dict = {}
    n["baseline_windows_suite"] = pytest_line(RAW / "baseline" / "windows_pytest_5fd4e1b_run2.log")
    n["baseline_windows_suite_method_error"] = pytest_line(RAW / "baseline" / "windows_pytest_5fd4e1b.log")
    for h in ("9844976", "6f73051", "2bafad9", "2bc63eb"):
        p = RAW / "contract-wiring" / f"windows_pytest_{h}.log"
        if p.exists():
            n[f"checkout_windows_suite_{h}"] = pytest_line(p)
    if ARGS.out != "EVIDENCE_NUMBERS.json":
        for p in sorted((RAW / "v1.1").glob("windows_pytest_*.log")):
            n[f"checkout_windows_suite_{p.stem.removeprefix('windows_pytest_')}"] = pytest_line(p)
    ops = json.loads((RAW / ARGS.ops_summary).read_text(encoding="utf-8"))["sources"]
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
    local = RAW / ARGS.local
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
    protected = json.loads((RAW / ARGS.protected).read_text(encoding="utf-8"))
    n["protected_set"] = {"items": protected["items"], "unchanged": protected["unchanged"],
                          "changed_or_missing": len(protected["changed_or_missing"])}
    if ARGS.d16:
        n["d16"] = d16(RAW / ARGS.d16)
    out = ROOT / "qualification" / "crypto" / ARGS.out
    out.write_text(json.dumps(n, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: (v if not isinstance(v, dict) else {kk: vv for kk, vv in v.items()
                                                            if not isinstance(vv, (dict, list))})
                      for k, v in n.items()}, ensure_ascii=False)[:3000])


if __name__ == "__main__":
    main()
