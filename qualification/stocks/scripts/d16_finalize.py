"""stocks / D-16: fecha os 4 gates bloqueados a partir dos logs brutos de um run do stocks-d16.yml (C20).

Lê só RAW_LOGS/d16/run<id>/stocks-d16-<papel>/ (artefatos baixados sem edição) e aplica os critérios
congelados antes da execução:

  E2E              linux-primary: runtime = final wheels (core_identity), painel = sha256 fixado
                   (SOURCES.json.expected, fontes conferidas), pré-filtro neutro, e2e_runtime --real
                   com todas as checagens ok (processo → término → processo novo relê o mesmo resultado,
                   provenance contra as fontes primárias) e exit 0.
  WINDOWS_SMOKE    windows-latest: o mesmo E2E real + restart em cada ponto de morte do perfil windows
                   (tolerância zero) + conformidade exit 0; painel com o mesmo sha256 do Linux.
  SOAK             linux-primary: veredito de tolerância zero do d16_soak.py e as contagens do perfil
                   congelado QUALIFICATION_PROFILE_STOCKS_V1 contadas linha a linha no soak.jsonl.
  STOCKS_NEGATIVE_CONTROLS  linux-controls: 81 execuções pelo entrypoint (referência + 4 × 20 seeds
                   congeladas) e os critérios congelados (o mesmo all_criteria_ok de scripts/science.py:
                   SHUFFLED ≤ 2/20, FEATURE ≤ 2/20, TEMPORAL ≤ 1,5 × IC inferior da referência quando > 0,
                   UNIVERSE ≥ 16/20 no mesmo estado).

Também calcula as métricas econômicas reais (bruto, líquido, IC95, custos) do resultado do E2E e o
diagnóstico de contaminação por eventos não ajustados (ST-F008) nos períodos de carteira.

Uso: python d16_finalize.py <run_dir> <saída D16_NUMBERS.json>
"""

from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
QC = ROOT / "qualification" / "stocks"
WHEELS = {"predictor-core": "10ef42f34ace8bb2df5f83ff7de2ceec79b035a25ea0a690e8942bd60d2fb4e3",
          "predictor-ops": "0be70bfbb2437dfb080baceb9af41043a09d03b15a358903b8bd7007f5f169b3",
          "stocks-predictor": "92cb1131b4f0ba0b4572d26cb03a1647e239a17f37514c0db1598797119366a8"}
DEATH_POINTS = {"before_admission_commit", "after_admission", "during_materialization", "before_ops", "after_ops",
                "after_domain_effect", "during_result_write", "after_result_write", "after_result_store"}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None


def last_exit(path: Path) -> int | None:
    if not path.is_file():
        return None
    found = re.findall(r"^\[exit (\d+)\]$", path.read_text(encoding="utf-8", errors="replace"), re.M)
    return int(found[-1]) if found else None


def junit(path: Path) -> dict | None:
    if not path.is_file():
        return None
    root = ET.parse(path).getroot()
    suites = [root] if root.tag == "testsuite" else list(root)
    total = {k: sum(int(s.get(k, 0)) for s in suites) for k in ("tests", "failures", "errors", "skipped")}
    total["passed"] = total["tests"] - total["failures"] - total["errors"] - total["skipped"]
    return total


def common(env_dir: Path, expected_panel: str) -> dict:
    env_log = (env_dir / "env.log").read_text(encoding="utf-8", errors="replace") if (env_dir / "env.log").is_file() else ""
    identity = load(env_dir / "core_identity.json") or {}
    installed = {p["name"]: ((p.get("direct_url") or {}).get("archive_info") or {}).get("hashes", {}).get("sha256")
                 for p in identity.get("packages", [])}
    in_site = all(p.get("module_in_site_packages") and not p.get("editable") for p in identity.get("packages", [])
                  if p["name"] in WHEELS)
    manifest = load(env_dir / "BUILD_MANIFEST.json") or {}
    prefilter = load(env_dir / "verify_prefilter.json") or {}
    real_env = load(env_dir / "REAL_ENV.json") or {}
    sources = manifest.get("sources", [])
    out = {
        "setup_ok": "SETUP FAIL" not in env_log and "\ndone " in env_log,
        "d16_lock_ok": "BLOCKED" not in env_log,
        "wheels_installed": {k: installed.get(k) for k in WHEELS},
        "wheels_ok": all(installed.get(k) == v for k, v in WHEELS.items()) and in_site,
        "build_exit": last_exit(env_dir / "build_real_panel.log"),
        "sources_downloaded_in_job": sum(1 for s in sources if s.get("from") == "download"),
        "sources_total": len(sources),
        "panel_sha256": (manifest.get("panel") or {}).get("sha256"),
        "panel_bytes": (manifest.get("panel") or {}).get("bytes"),
        "panel_matches_pin": manifest.get("matches_pin") is True and (manifest.get("panel") or {}).get("sha256") == expected_panel,
        "data_cutoff": manifest.get("data_cutoff"),
        "prefilter_ok": prefilter.get("ok") is True,
        "rebalances": prefilter.get("rebalances"),
        "dataset_object_is_panel": real_env.get("object_hashes", {}).get("dataset") == expected_panel,
    }
    out["ok"] = all(out[k] for k in ("setup_ok", "d16_lock_ok", "wheels_ok", "panel_matches_pin", "prefilter_ok",
                                     "dataset_object_is_panel")) and out["build_exit"] == 0 \
        and out["sources_downloaded_in_job"] == out["sources_total"] > 0
    return out


def e2e(env_dir: Path) -> dict:
    summary = load(env_dir / "e2e" / "E2E_SUMMARY.json") or {}
    outcome = load(env_dir / "e2e" / "outcome_file.json") or {}
    result = outcome.get("result") or {}
    checks = summary.get("checks", [])
    return {"exit": last_exit(env_dir / "e2e.log"), "checks": len(checks), "checks_ok": sum(1 for c in checks if c["ok"]),
            "failed": [c["check"] for c in checks if not c["ok"]], "all_ok": summary.get("all_ok") is True,
            "result_state": result.get("result_state"), "scientific_state": result.get("scientific_state"),
            "economic_state": result.get("economic_state"), "capital_permission": result.get("capital_permission"),
            "metrics": (result.get("domain_facts") or {}).get("metrics"), "costs": (result.get("domain_facts") or {}).get("costs"),
            "baseline_comparison": (result.get("domain_facts") or {}).get("baseline_comparison"),
            "trial_ids": (result.get("core_facts") or {}).get("trial_ids"),
            "temporal_validation": (result.get("core_facts") or {}).get("temporal_validation"),
            "last_period_end": ((result.get("domain_facts") or {}).get("last_universe") or {}).get("session"),
            "rebalances": (result.get("domain_facts") or {}).get("rebalances") or []}


def soak_counts(path: Path) -> dict:
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()] if path.is_file() else []
    proc = [r for r in rows if r["kind"] == "process"]
    rid = lambda r, part: part in r["request_id"]  # noqa: E731
    counts = {
        "process_calls": len(proc),
        "normal_cycles": sum(1 for r in proc if rid(r, "-SOAK-N-") and r["fault"] is None and r["status"] == "RESULT"),
        "duplicates": sum(1 for r in proc if r["status"] == "DUPLICATE" and (r.get("client_ref") or {}).get("dup") is not None),
        "restarts": sum(1 for r in proc if r["fault"] in DEATH_POINTS and r["exit"] == 86),
        "ops_worker_crash": sum(1 for r in proc if r["fault"] == "ops_worker_crash" and r["exit"] == 3
                                and r["scientific_state"] == "NOT_EVALUATED"),
        "before_admission_commit": sum(1 for r in proc if r["fault"] == "before_admission_commit" and r["exit"] == 86),
        "during_result_write": sum(1 for r in proc if r["fault"] == "during_result_write" and r["exit"] == 86),
        "timeouts": sum(1 for r in proc if r["fault"] == "ops_worker_hang" and r["operational_state"] == "TIMEOUT"),
        "family_not_ready": sum(1 for r in proc if r["result_state"] == "NOT_READY"),
        "collection_only_valid": sum(1 for r in proc if r["result_state"] == "COLLECTION_RECORDED"),
    }
    summary = next((r for r in rows if r["kind"] == "summary"), {})
    verdict = next((r for r in rows if r["kind"] == "verdict"), {})
    counts["eligible_trials"] = summary.get("eligible_trials")
    counts["summary"] = {k: summary.get(k) for k in ("requests_with_result", "stored_results", "lost", "unexpected",
                                                     "domain_effects", "ops_jobs", "ops_success_per_job_max",
                                                     "reread_mismatch", "reconcile_exit", "reconcile_findings",
                                                     "violations", "pit_violations", "rebalance_sessions_checked",
                                                     "universe_contamination", "distinct_metrics_for_identical_requests",
                                                     "operator_store_unchanged")}
    counts["zero_tolerance_ok"] = verdict.get("zero_tolerance_ok") is True
    return counts


def contamination(manifest: dict, rebalances: list[dict], last_end: str | None) -> dict:
    """Períodos de carteira/universo com evento corporativo NÃO ajustado dentro de (início, fim].
    `rebalances` traz o início de cada período; o fim do último é a última decisão (last_universe)."""
    events = [(j["security_id"], j["session"], "residual_jump_dismes_changed " + j["especi"])
              for j in manifest.get("residual_jumps", []) if j.get("dismes_changed")]
    for s in manifest.get("corporate_events_skipped", []):
        if s.get("reason", "").startswith("asset issued differs"):
            try:
                prior = date(*map(int, reversed(s["lastDatePrior"].split("/"))))
            except (ValueError, KeyError):
                continue
            events.append((s["security_id"], (prior + timedelta(days=1)).isoformat(), "bonus_in_other_class " + s["label"]))
    hits_port, hits_uni = [], []
    ends = [r["session"] for r in rebalances[1:]] + ([last_end] if last_end else [])
    for start, end in zip(rebalances, ends):
        for sid, day, why in events:
            if start["session"] < day <= end:
                if sid in start["portfolio"]:
                    hits_port.append({"period_start": start["session"], "security_id": sid, "event_session": day, "why": why})
                if sid in start["members"]:
                    hits_uni.append({"period_start": start["session"], "security_id": sid, "event_session": day, "why": why})
    return {"periods": len(ends), "unadjusted_events_considered": len(events),
            "portfolio_hits": hits_port, "universe_hits": hits_uni,
            "portfolio_periods_affected": len({h["period_start"] for h in hits_port}),
            "universe_periods_affected": len({h["period_start"] for h in hits_uni})}


def main() -> int:
    run_dir, out_path = Path(sys.argv[1]), Path(sys.argv[2])
    sources = load(QC / "d16" / "SOURCES.json")
    profile = load(QC / "QUALIFICATION_PROFILE_STOCKS_V1.json")
    expected = sources["expected"]["panel_sha256"]
    lp, lc, wl = (run_dir / f"stocks-d16-{r}" for r in ("linux-primary", "linux-controls", "windows-latest"))
    envs = {name: common(d, expected) for name, d in (("linux-primary", lp), ("linux-controls", lc), ("windows-latest", wl))}
    gates = {}

    e_l = e2e(lp)
    ok = envs["linux-primary"]["ok"] and e_l["exit"] == 0 and e_l["all_ok"] and e_l["checks"] >= 10
    gates["E2E"] = {"status": "PASS" if ok else "FAIL", "linux": e_l | {"rebalances": len(e_l["rebalances"])}}

    e_w = e2e(wl)
    restart = soak_counts(wl / "restart.jsonl")
    conf_w = junit(wl / "conformance.junit.xml")
    same_panel = envs["windows-latest"]["panel_sha256"] == envs["linux-primary"]["panel_sha256"] == expected
    ok = (envs["windows-latest"]["ok"] and e_w["exit"] == 0 and e_w["all_ok"] and restart["zero_tolerance_ok"]
          and restart["restarts"] >= 5 and last_exit(wl / "conformance.log") == 0 and conf_w and conf_w["failures"] == 0
          and conf_w["errors"] == 0 and same_panel)
    gates["WINDOWS_SMOKE"] = {"status": "PASS" if ok else "FAIL", "e2e": e_w | {"rebalances": len(e_w["rebalances"])},
                              "restart": restart, "conformance": conf_w, "panel_same_as_linux": same_panel,
                              "metrics_equal_linux": e_w["metrics"] == e_l["metrics"]}

    soak = soak_counts(lp / "soak.jsonl")
    need = {"normal_cycles": profile["normal_cycles"], "restarts": profile["restarts"], "duplicates": profile["duplicates"],
            "ops_worker_crash": profile["runs_per_relevant_failure_class"],
            "before_admission_commit": profile["runs_per_relevant_failure_class"],
            "during_result_write": profile["runs_per_relevant_failure_class"], "timeouts": profile["timeouts"],
            "family_not_ready": profile["family_not_ready"], "collection_only_valid": profile["collection_only_valid"]}
    short = {k: (soak[k], v) for k, v in need.items() if soak[k] < v}
    ok = (envs["linux-primary"]["ok"] and soak["zero_tolerance_ok"] and not short
          and soak["eligible_trials"] == profile["eligible_trials_while_no_family_ready"]
          and last_exit(lp / "soak.log") == 0)
    gates["SOAK"] = {"status": "PASS" if ok else "FAIL", "counts": soak, "profile_minimums": need, "below_profile": short}

    nc = load(lc / "science" / "NEGATIVE_CONTROLS_SUMMARY.json") or {}
    nc_rows = [json.loads(x) for x in (lc / "science" / "negative_controls.jsonl").read_text(encoding="utf-8").splitlines()
               if x.strip()] if (lc / "science" / "negative_controls.jsonl").is_file() else []
    ok = (envs["linux-controls"]["ok"] and last_exit(lc / "science.log") == 0 and len(nc_rows) == 81
          and not nc.get("failed_runs") and nc.get("all_criteria_ok") is True
          and nc.get("dataset_sha256") == expected)
    gates["STOCKS_NEGATIVE_CONTROLS"] = {"status": "PASS" if ok else "FAIL", "runs": len(nc_rows),
                                         "supported_counts": nc.get("supported_counts"), "criteria": nc.get("criteria"),
                                         "reference": nc.get("reference"), "failed_runs": nc.get("failed_runs"),
                                         "reference_metrics_equal_e2e": (nc.get("reference") or {}).get("excess_gross_ci_bps")
                                         == (e_l["metrics"] or {}).get("excess_gross_ci_bps")}

    manifest = load(lp / "BUILD_MANIFEST.json") or {}
    numbers = {
        "run_dir": (run_dir.resolve().relative_to(ROOT).as_posix() if run_dir.resolve().is_relative_to(ROOT)
                    else run_dir.as_posix()),
        "expected_panel_sha256": expected,
        "environments": envs,
        "gates": gates,
        "economic": {"source": "linux-primary e2e/outcome_file.json (stocks:REQ-D16-E2E-001)",
                     "result_state": e_l["result_state"], "scientific_state": e_l["scientific_state"],
                     "economic_state": e_l["economic_state"], "metrics": e_l["metrics"], "costs": e_l["costs"],
                     "baseline_comparison": e_l["baseline_comparison"], "trial_ids": e_l["trial_ids"],
                     "temporal_validation": e_l["temporal_validation"],
                     "first_rebalance": e_l["rebalances"][0]["session"] if e_l["rebalances"] else None,
                     "last_period_start": e_l["rebalances"][-1]["session"] if e_l["rebalances"] else None,
                     "last_period_end": e_l["last_period_end"],
                     "universe_sizes": sorted({r["universe_size"] for r in e_l["rebalances"]}),
                     "portfolio_sizes": sorted({len(r["portfolio"]) for r in e_l["rebalances"]})},
        "panel": {k: manifest.get(k) for k in ("dataset_version", "data_cutoff", "calendar", "counts", "securities_total",
                                              "securities_kept", "identity_sources")}
        | {"kept_without_identity": (manifest.get("identity") or {}).get("kept_without_identity"),
           "corporate_adjustments": len(manifest.get("corporate_adjustments", [])),
           "residual_jumps_kept": sum(1 for j in manifest.get("residual_jumps", []) if j.get("kept_in_panel"))},
        "contamination": contamination(manifest, e_l["rebalances"], e_l["last_period_end"]),
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(numbers, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({g: v["status"] for g, v in gates.items()}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
