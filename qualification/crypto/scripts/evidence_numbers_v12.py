"""C20 (EVIDENCE_CONSISTENCY), reabertura V1.2 (D-27): todos os números dos relatórios da V1.2 saem só dos logs
brutos de qualification/crypto/RAW_LOGS/v1.2/ (junit XML, jsonl, logs, JSONs gerados por scripts). Nada digitado.
Uso: python evidence_numbers_v12.py --run run36646241688 [--out EVIDENCE_NUMBERS_V1.2.json]
"""
from __future__ import annotations

import argparse
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "qualification" / "crypto" / "RAW_LOGS" / "v1.2"
SOAK_FIELDS = ("requests_with_result", "stored_results", "domain_effects", "ops_jobs", "ops_success_per_job_max",
               "lost", "unexpected", "reread_mismatch", "violations", "reconcile_exit")
SOAK_FAILURE_CLASSES = ("ops_worker_crash", "ops_worker_hang", "host_killed_during_ops_job",
                        "before_admission_commit", "during_result_write", "result_file_corruption")


def rel(p: Path) -> str:
    return p.relative_to(ROOT).as_posix()


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
    return {"file": rel(path), **total, "failed": sorted(failed)}


def soak(path: Path) -> dict:
    rows = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    summary = next(r for r in rows if r["kind"] == "summary")
    verdict = next(r for r in rows if r["kind"] == "verdict")
    process = [r for r in rows if r["kind"] == "process"]
    corruptions = [r for r in rows if r["kind"] == "corruption"]
    faults: dict[str, int] = {}
    for r in process:
        faults[r.get("fault") or "none"] = faults.get(r.get("fault") or "none", 0) + 1
    classes = {c: (len(corruptions) if c == "result_file_corruption" else faults.get(c, 0)) for c in SOAK_FAILURE_CLASSES}
    count = lambda v: len(v) if isinstance(v, list) else v  # noqa: E731  (listas do log viram contagens)
    return {"file": rel(path), "process_calls": len(process), "faults": dict(sorted(faults.items())),
            "failure_classes": classes, **{k: count(summary[k]) for k in SOAK_FIELDS},
            "reconcile_findings": count(summary.get("reconcile_findings")),
            "reconcile_foreign_findings": count(summary.get("reconcile_foreign_findings")),
            "reconcile_missed_corruptions": count(summary.get("reconcile_missed_corruptions")),
            "corruptions_injected": len(corruptions),
            "corruptions_fail_closed": sum(1 for r in corruptions if r["show_exit"] == 5 and r["retry_exit"] == 5
                                           and r["file_not_repaired"]),
            "zero_tolerance_ok": verdict["zero_tolerance_ok"]}


def e2e(path: Path) -> dict:
    d = json.loads(path.read_text(encoding="utf-8"))
    return {"file": rel(path), "all_ok": d["all_ok"], "checks": len(d["checks"]),
            "failed": [c["check"] for c in d["checks"] if not c["ok"]]}


def env_head(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    first = text.splitlines()[0] if text.strip() else ""
    return {"file": rel(path), **dict(re.findall(r"(\w+)=(\S+)", first)),
            "done": re.search(r"^done ", text, re.M) is not None,
            "setup_fail": "SETUP FAIL" in text, "blocked": "BLOCKED" in text}


def exits(d: Path, steps: tuple[str, ...]) -> dict:
    out = {}
    for step in steps:
        p = d / f"{step}.log"
        found = re.findall(r"\[exit (\d+)\]", p.read_text(encoding="utf-8", errors="replace")) if p.exists() else []
        out[step] = int(found[-1]) if found else None
    return out


def core_identity(path: Path) -> dict | None:
    if not path.exists():
        return None
    d = json.loads(path.read_text(encoding="utf-8"))
    return {"file": rel(path), "python": d.get("python"),
            "packages": {p["name"]: {"version": p["version"], "editable": p.get("editable"), "installer": p.get("installer"),
                                     "wheel_sha256": ((p.get("direct_url") or {}).get("archive_info") or {}).get("hashes", {}).get("sha256"),
                                     "module_in_site_packages": p.get("module_in_site_packages"), "import_error": p.get("import_error")}
                         for p in d.get("packages", [])},
            "lock_chain": d.get("lock_chain")}


def runtime(d: Path) -> dict:
    n = {"env": env_head(d / "env.log"), "step_exits": exits(d, ("conformance", "full_suite", "e2e", "soak")),
         "conformance": junit(d / "conformance.junit.xml"), "full_suite": junit(d / "full_suite.junit.xml"),
         "e2e": e2e(d / "e2e" / "E2E_SUMMARY.json"),
         "core_identity": core_identity(d / "core_identity.json")}
    if (d / "soak.jsonl").exists():
        n["soak_synthetic_diagnostic"] = soak(d / "soak.jsonl")
    return n


def d16(d: Path) -> dict:
    manifest = json.loads((d / "data_MANIFEST.json").read_text(encoding="utf-8"))
    files = [f for f in manifest["files"] if "copy_sha256" in f]
    science = json.loads((d / "science" / "SCIENCE_REAL.json").read_text(encoding="utf-8"))
    return {"env": env_head(d / "env.log"),
            "step_exits": exits(d, ("e2e_real", "e2e_cases", "science", "soak_real", "conformance")),
            "data_manifest": {"file": rel(d / "data_MANIFEST.json"), "files": len(manifest["files"]),
                              "verified_against_published_checksum": sum(1 for f in files if f["published_sha256"] == f["copy_sha256"]),
                              "unavailable": [f["url"] for f in manifest["files"] if "unavailable" in f],
                              "objects": manifest["objects"]},
            "e2e_real": e2e(d / "e2e_real" / "E2E_SUMMARY.json"),
            "e2e_cases": e2e(d / "e2e_cases" / "E2E_SUMMARY.json"),
            "conformance": junit(d / "conformance.junit.xml"),
            "soak_real": soak(d / "soak_real.jsonl"),
            "science": {"file": rel(d / "science" / "SCIENCE_REAL.json"),
                        "economic_metrics": science["economic_metrics"],
                        "negative_controls": science["negative_controls"],
                        "future_canary": {"leaks": len(science["future_canary"]["leaks"]),
                                          "pass": science["future_canary"]["pass"]}}}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--out", default="EVIDENCE_NUMBERS_V1.2.json")
    a = ap.parse_args()
    run = RAW / a.run
    n: dict = {"run": a.run}
    for label in ("runtime-linux-primary", "runtime-windows-latest"):
        if (run / label).is_dir():
            n[label] = runtime(run / label)
    if (run / "d16").is_dir():
        n["d16"] = d16(run / "d16")
        n["d16"]["core_identity"] = core_identity(run / "d16" / "core_identity.json")
    for name in ("protected_set_check_21f8b182", "protected_set_v1_2_check_21f8b182"):
        p = RAW / "protected" / f"{name}.json"
        d = json.loads(p.read_text(encoding="utf-8"))
        n[name] = {"file": rel(p), "items": d["items"], "unchanged": d["unchanged"], "changed_or_missing": len(d["changed_or_missing"])}
    lock = RAW / "lock" / "uv_lock_check_21f8b182.log"
    m = re.search(r"\[exit (\d+)\]", lock.read_text(encoding="utf-8"))
    n["uv_lock_check_21f8b182"] = {"file": rel(lock), "exit": int(m.group(1)) if m else None}
    ci = {}
    for p in sorted((RAW / "hosted-ci").glob("jobs_*.json")):
        d = json.loads(p.read_text(encoding="utf-8"))
        ci[p.stem] = {"file": rel(p), "jobs": {j["name"]: j["conclusion"] for j in d["jobs"]},
                      "head_sha": sorted({j["head_sha"] for j in d["jobs"]})}
    n["hosted_ci"] = ci
    sec = RAW / "secrets" / "scan_secrets_21f8b182.log"
    n["secrets"] = {"scan_secrets": {"file": rel(sec), "findings": len(json.loads(re.search(r"\{.*\}", sec.read_text(encoding="utf-8"), re.S).group(0))["findings"])},
                    "diff_patterns": {"file": rel(RAW / "secrets" / "diff_patterns_341d270_21f8b182.log"),
                                      "pattern_hits": 0 if "[exit 1/1]" in (RAW / "secrets" / "diff_patterns_341d270_21f8b182.log").read_text(encoding="utf-8") else None}}
    graph = json.loads((RAW / "truth-map" / "import_graph_21f8b182.json").read_text(encoding="utf-8"))
    n["import_graph"] = {"file": rel(RAW / "truth-map" / "import_graph_21f8b182.json"),
                         "roots": {k: {"closure_size": v["closure_size"], "forbidden_reached": v["forbidden_reached"],
                                       "adapter_paths_reached": v["adapter_paths_reached"]} for k, v in graph["roots"].items()}}
    out = ROOT / "qualification" / "crypto" / a.out
    out.write_text(json.dumps(n, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    brief = {k: (v if not isinstance(v, dict) else {kk: vv for kk, vv in v.items() if not isinstance(vv, (dict, list))}) for k, v in n.items()}
    print(json.dumps(brief, ensure_ascii=False)[:1500])


if __name__ == "__main__":
    main()
