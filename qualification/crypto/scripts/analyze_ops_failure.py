"""C20: números da fase ops-failure (SHARED-003/004) tirados só dos logs brutos.

Percorre qualification/crypto/RAW_LOGS/ops-failure/<fonte>/<ambiente>/ e produz
qualification/crypto/RAW_LOGS/ops-failure/OPS_FAILURE_SUMMARY.json.
Uso: python analyze_ops_failure.py <dir ops-failure> [<fonte> ...]
"""

from __future__ import annotations

import json
import re
import statistics
import sys
from pathlib import Path

SUMMARY = re.compile(r"^=*\s*(?:(\d+) failed)?(?:, )?(?:(\d+) passed)?(?:, )?(?:(\d+) failed)?.* in [0-9.]+s", re.M)


def pytest_counts(text: str) -> dict:
    line = next((l for l in reversed(text.splitlines()) if re.search(r"\b(passed|failed|error)\b.* in [0-9.]+s", l)), "")
    counts = {k: int(v) for v, k in re.findall(r"(\d+) (passed|failed|errors?|skipped)", line)}
    exit_m = re.search(r"\[exit (\d+)\]", text)
    return {"summary_line": line.strip(), **counts, "exit": int(exit_m.group(1)) if exit_m else None,
            "failed_tests": re.findall(r"^FAILED (\S+)", text, re.M)}


def probes(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            row = json.loads(line)
        except ValueError:
            continue
        if isinstance(row, dict) and "scenario" in row:
            rows.append(row)
    return rows


def env_summary(env_dir: Path) -> dict:
    out: dict = {"env_log_head": (env_dir / "env.log").read_text(encoding="utf-8").splitlines()[:1]}
    env_text = (env_dir / "env.log").read_text(encoding="utf-8")
    m = re.search(r"^predictor_ops (\S+) ", env_text, re.M)
    out["predictor_ops_file"] = m.group(1) if m else None
    out["setup_failed"] = "SETUP FAIL" in env_text or "No module named 'predictor_ops'" in env_text
    for label in ("shared003_test", "shared004_tests", "full_tests_v2"):
        runs = sorted(env_dir.glob(f"{label}_run*.log"))
        parsed = [pytest_counts(p.read_text(encoding="utf-8")) | {"log": p.name} for p in runs]
        out[label] = {
            "executions": len(parsed),
            "executions_all_passed": sum(1 for r in parsed if r["exit"] == 0),
            "executions_with_failure": sum(1 for r in parsed if r["exit"] not in (0, None)),
            "failed_tests_union": sorted({t for r in parsed for t in r["failed_tests"]}),
            "runs": parsed,
        }
    start = [r["first_byte_seconds"] for r in probes(env_dir / "probe_startup.jsonl") if r.get("got_byte")]
    out["probe_startup"] = {
        "n": len(start),
        "min_s": min(start) if start else None,
        "median_s": statistics.median(start) if start else None,
        "max_s": max(start) if start else None,
        "over_0_2s": sum(1 for s in start if s > 0.2),
    }
    for name in ("test_exact", "a_b_delay"):
        rows = probes(env_dir / f"probe_{name}.jsonl")
        out[f"probe_{name}"] = {
            "n": len(rows),
            "assertions_pass": sum(1 for r in rows if r.get("test_assertions_pass")),
            "output_bytes_values": sorted({r.get("output_bytes") for r in rows}),
            "exit_codes": sorted({r.get("exit_code") for r in rows}),
            "termination_methods": sorted({(r.get("termination") or {}).get("method") for r in rows}),
        }
    tree = probes(env_dir / "probe_real_tree.jsonl")
    out["probe_real_tree"] = {
        "n": len(tree),
        "killed_tree_and_truncated": sum(1 for r in tree if r.get("real_job_killed_tree_and_truncated")),
        "child_alive_after": sum(1 for r in tree if r.get("child_alive_after")),
        "grandchild_alive_after": sum(1 for r in tree if r.get("grandchild_alive_after")),
        "termination_methods": sorted({(r.get("termination") or {}).get("method") for r in tree}),
        "exit_codes": sorted({r.get("exit_code") for r in tree}),
    }
    return out


def main() -> None:
    root = Path(sys.argv[1])
    sources = sys.argv[2:] or sorted(p.name for p in root.iterdir() if p.is_dir())
    summary = {"generated_by": "qualification/crypto/scripts/analyze_ops_failure.py", "sources": {}}
    for source in sources:
        src = root / source
        summary["sources"][source] = {}
        for env_dir in sorted(p for p in src.iterdir() if p.is_dir()):
            summary["sources"][source][env_dir.name] = env_summary(env_dir)
    out = root / "OPS_FAILURE_SUMMARY.json"
    out.write_text(json.dumps(summary, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    for source, envs in summary["sources"].items():
        for env, s in envs.items():
            print(f"{source}/{env}: setup_failed={s['setup_failed']} 003={s['shared003_test']['executions_all_passed']}/{s['shared003_test']['executions']} "
                  f"004={s['shared004_tests']['executions_all_passed']}/{s['shared004_tests']['executions']} "
                  f"full={[ (r.get('passed'), r.get('failed')) for r in s['full_tests_v2']['runs']]} "
                  f"startup_med={s['probe_startup']['median_s']} max={s['probe_startup']['max_s']} >0.2s={s['probe_startup']['over_0_2s']} "
                  f"exact={s['probe_test_exact']['assertions_pass']}/{s['probe_test_exact']['n']} ab={s['probe_a_b_delay']['assertions_pass']}/{s['probe_a_b_delay']['n']} "
                  f"tree={s['probe_real_tree']['killed_tree_and_truncated']}/{s['probe_real_tree']['n']} {s['probe_real_tree']['termination_methods']}")


if __name__ == "__main__":
    main()
