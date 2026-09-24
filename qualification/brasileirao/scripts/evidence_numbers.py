"""brasileirao: tira os números dos relatórios dos logs brutos (C20, gate EVIDENCE_CONSISTENCY).

Lê só arquivos em RAW_LOGS/ (resultados `show`, junit, logs de suíte, soak.jsonl, E2E_SUMMARY.json)
e escreve um JSON com cada número e o arquivo de onde saiu. Nenhum número é digitado à mão.

Modos:
  metrics  --results <dir com result_*.json do real_env.py> [--dataset <cópia sqlite> --clv-diagnostic]
  junit    <arquivo.junit.xml>...        contagens tests/failures/errors/skipped
  pytestlog <arquivo.log>...             última linha-resumo do pytest
  soak     <soak.jsonl>                  resumo e veredito
  e2e      <E2E_SUMMARY.json>...         checagens ok/total
Saída: --out <json> (acrescenta/atualiza a chave do modo).
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sqlite3
import xml.etree.ElementTree as ET
from pathlib import Path


def _load(out: Path) -> dict:
    return json.loads(out.read_text(encoding="utf-8")) if out.exists() else {}


def metrics(results_dir: Path, dataset: Path | None, clv: bool) -> dict:
    rows = []
    for path in sorted(results_dir.glob("result_*.json")):
        text = path.read_text(encoding="utf-8").strip()
        if not text:
            rows.append({"file": path.as_posix(), "error": "empty show output"})
            continue
        payload = json.loads(text)
        result = payload.get("result") or {}
        domain = result.get("domain_facts", {})
        ev = domain.get("evaluation") or {}
        eco = domain.get("economics") or {}
        rows.append({
            "file": path.as_posix(),
            "request": path.stem.removeprefix("result_"),
            "result_state": result.get("result_state"),
            "scientific_state": result.get("scientific_state"),
            "economic_state": result.get("economic_state"),
            "n_predictions": len(domain.get("predictions", [])),
            "n_evaluated": ev.get("n_evaluated"),
            "metric": ev.get("metric"),
            "model_score": (ev.get("model") or {}).get(ev.get("metric")),
            "baseline_score": (ev.get("baseline_scores") or {}).get(ev.get("metric")),
            "mean_delta": ev.get("mean_delta"),
            "ci_delta": ev.get("ci_delta"),
            "model_log_loss": (ev.get("model") or {}).get("log_loss"),
            "baseline_log_loss": (ev.get("baseline_scores") or {}).get("log_loss"),
            "n_bets": eco.get("n_bets"),
            "roi_gross": eco.get("roi_gross"),
            "ci_gross_mean": eco.get("ci_gross_mean"),
            "roi_net": eco.get("roi_net"),
            "ci_net_mean": eco.get("ci_net_mean"),
            "net_after_tax_total": eco.get("net_after_tax_total"),
            "hit_rate": eco.get("hit_rate"),
            "clv": eco.get("clv"),
            "data_quality": domain.get("data_quality"),
            "max_used_minus_cutoff_seconds": (result.get("core_facts", {}).get("temporal_validation") or {}).get("max_used_minus_cutoff_seconds"),
        })
    out = {"source_dir": results_dir.as_posix(), "requests": rows}
    if clv and dataset:
        out["clv_diagnostic_open_price"] = clv_diagnostic(results_dir, dataset)
    return out


def _shin(odds: list[float]) -> list[float]:
    from brasileirao_predictor.math_utils import shin_probabilities

    probs, _z, _o = shin_probabilities(odds)
    return [float(p) for p in probs]


def clv_diagnostic(results_dir: Path, dataset: Path) -> dict:
    """DIAGNÓSTICO, fora do resultado: aposta ao preço de ABERTURA (horário desconhecido na base)
    com a previsão feita com informação até kickoff-60min; CLV = odd_abertura x Shin(fechamento) - 1.
    Viés otimista possível: a abertura pode ser anterior a resultados que o modelo já viu."""
    conn = sqlite3.connect(f"file:{dataset.as_posix()}?mode=ro&immutable=1", uri=True)
    odds = {r[0]: r[1:] for r in conn.execute(
        "SELECT s.event_id, s.odds_home, s.odds_draw, s.odds_away, s.odds_home_open, s.odds_draw_open, s.odds_away_open, "
        "l.odd_a, l.odd_b, s.odds_over_open, s.odds_under_open FROM sofascore_matches s "
        "LEFT JOIN odds_lines l ON l.event_id = s.event_id AND l.market = 'ou' AND l.line = 2.5")}
    labels = {r[0]: (r[1], r[2]) for r in conn.execute("SELECT event_id, home_score, away_score FROM matches WHERE home_score IS NOT NULL")}
    out = {}
    for path in sorted(results_dir.glob("result_*-climatology.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        result = payload.get("result") or {}
        target = result.get("domain_facts", {}).get("target")
        bets = []
        for p in result.get("domain_facts", {}).get("predictions", []):
            if p.get("status") != "PREDICTED" or p["event_id"] not in labels or p["event_id"] not in odds:
                continue
            o = odds[p["event_id"]]
            hs, as_ = labels[p["event_id"]]
            if target == "1X2":
                close, opening, probs = list(o[0:3]), list(o[3:6]), [p["p_home"], p["p_draw"], p["p_away"]]
                won = [hs > as_, hs == as_, hs < as_]
            else:
                close, opening, probs = list(o[6:8]), list(o[8:10]), [p["p_over25"], 1 - p["p_over25"]]
                won = [hs + as_ > 2.5, hs + as_ < 2.5]
            if not all(isinstance(x, (int, float)) and x and x > 1 for x in close + opening):
                continue
            shin_close = _shin([float(x) for x in close])
            for i, odd in enumerate(opening):
                edge = probs[i] * odd - 1
                if 0.02 <= edge <= 0.15:
                    bets.append({"clv": odd * shin_close[i] - 1, "net": (odd - 1) * 0.98 if won[i] else -1.0})
        if bets:
            n = len(bets)
            mean_clv = sum(b["clv"] for b in bets) / n
            sd = math.sqrt(sum((b["clv"] - mean_clv) ** 2 for b in bets) / max(n - 1, 1))
            out[path.stem.removeprefix("result_")] = {
                "n_bets_open": n,
                "mean_clv": round(mean_clv, 6),
                "clv_iid_normal_ci95": [round(mean_clv - 1.96 * sd / math.sqrt(n), 6), round(mean_clv + 1.96 * sd / math.sqrt(n), 6)],
                "roi_net_open": round(sum(b["net"] for b in bets) / n, 6),
                "label": "DIAGNÓSTICO: preço de abertura sem carimbo de hora; não entra no resultado nem em gate",
            }
    return out


def junit(paths: list[Path]) -> dict:
    out = {}
    for path in paths:
        root = ET.parse(path).getroot()
        suites = [root] if root.tag == "testsuite" else list(root)
        out[path.as_posix()] = {k: sum(int(s.get(k, 0)) for s in suites) for k in ("tests", "failures", "errors", "skipped")}
    return out


def pytestlog(paths: list[Path]) -> dict:
    out = {}
    pattern = re.compile(r"^=*\s*(.*\b(passed|failed)\b.* in [0-9.]+s.*?)\s*=*$")
    for path in paths:
        lines = [ln for ln in path.read_text(encoding="utf-8", errors="replace").splitlines() if pattern.match(ln.strip())]
        out[path.as_posix()] = pattern.match(lines[-1].strip()).group(1) if lines else None
    return out


def soak(path: Path) -> dict:
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    summary = next((r for r in rows if r["kind"] == "summary"), {})
    verdict = next((r for r in rows if r["kind"] == "verdict"), {})
    processes = [r for r in rows if r["kind"] == "process"]
    return {
        "file": path.as_posix(),
        "process_calls": len(processes),
        "by_fault": {f or "none": sum(1 for r in processes if r.get("fault") == f) for f in sorted({r.get("fault") or "" for r in processes})},
        "summary": {k: summary.get(k) for k in ("requests_with_result", "stored_results", "lost", "unexpected", "domain_effects",
                                                  "ops_success_per_job_max", "ops_jobs", "reread_mismatch", "reconcile_exit", "violations")},
        "zero_tolerance_ok": verdict.get("zero_tolerance_ok"),
    }


def e2e(paths: list[Path]) -> dict:
    out = {}
    for path in paths:
        doc = json.loads(path.read_text(encoding="utf-8"))
        out[path.as_posix()] = {k: doc.get(k) for k in ("mode", "checks_total", "checks_ok", "result_state", "scientific_state", "economic_state")}
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=("metrics", "junit", "pytestlog", "soak", "e2e"))
    ap.add_argument("paths", nargs="*", type=Path)
    ap.add_argument("--results", type=Path)
    ap.add_argument("--dataset", type=Path)
    ap.add_argument("--clv-diagnostic", action="store_true")
    ap.add_argument("--key")
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    doc = _load(args.out)
    if args.mode == "metrics":
        value = metrics(args.results, args.dataset, args.clv_diagnostic)
    elif args.mode == "junit":
        value = junit(args.paths)
    elif args.mode == "pytestlog":
        value = pytestlog(args.paths)
    elif args.mode == "soak":
        value = soak(args.paths[0])
    else:
        value = e2e(args.paths)
    doc.setdefault(args.mode, {})[args.key or "default"] = value
    args.out.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(value, ensure_ascii=False)[:3000])


if __name__ == "__main__":
    main()
