"""crypto / fase science: controles negativos e métricas econômicas com dados reais (Windows).

Tudo pelo `cripto-research` instalado, um processo por chamada, com os limiares de
FROZEN_PARAMETERS.json (negative_controls, costs_methodology):
  * injeção de futuro (dataset real com linhas pós-cutoff) → 0 resultados aceitos
  * ablação temporal (ordem trocada; disponível antes de observado) → 0 resultados aceitos
  * labels embaralhados (direção sorteada, seeds 0..99) → SUPPORTED em ≤ 10 de 100
  * métricas econômicas do pedido real: bruto e líquido separados, cada um com IC
  * canário: FUTURE_CANARY_CRYPTO_001 e as datas pós-cutoff não aparecem em nada que
    um pedido legítimo produz (resultado, efeito, trial do Core, outcome)

Uso: python science_real.py --tests <tests/> --real <dir do real_env> --state <dir> --out <dir>
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

CUTOFF = "2026-08-31T00:00:00Z"
CANARY_MARKER = "FUTURE_CANARY_CRYPTO_001"
POST_CUTOFF_DATES = ("2026-09-07", "2026-09-14", "2026-09-21")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tests", type=Path, required=True)
    ap.add_argument("--real", type=Path, required=True)
    ap.add_argument("--state", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    sys.path.insert(0, str(args.tests))
    from conformance.fixtures import cli, experiments

    args.out.mkdir(parents=True, exist_ok=True)
    env = {"root": args.real, "policy": args.real / "policy.json", "objects": args.real / "objects",
           "state": args.state, "requests": args.real / "requests"}
    rows = []

    def run(name: str) -> dict:
        code, lines = cli(env, "process", str(args.real / "requests" / f"{name}.json"))
        o = lines[0]
        row = {"vector": name, "exit": code, "status": o.get("status"), "reason": o.get("reason"),
               "result_id": o.get("result_id"), "operational": o.get("operational_state"),
               "scientific": o.get("scientific_state"), "economic": o.get("economic_state"),
               "result_state": o.get("result_state")}
        if o.get("outcome_file"):
            row["result"] = json.loads(Path(o["outcome_file"]).read_text(encoding="utf-8")).get("result")
        rows.append(row)
        return row

    e2e = run("e2e")
    future = run("canary")
    ablation = [run("ablation-order"), run("ablation-availability")]
    placebo = [run(f"placebo-{seed:03d}") for seed in range(100)]

    metrics = (e2e.get("result") or {}).get("domain_facts", {}).get("metrics", {})
    costs = (e2e.get("result") or {}).get("domain_facts", {}).get("costs", {})
    economic = {
        "request": "crypto:REQ-REAL-E2E-001",
        "gross_return_bps": metrics.get("gross_return_bps"),
        "gross_ci_bps": [metrics.get("gross_ci_low_bps"), metrics.get("gross_ci_high_bps")],
        "net_return_bps": metrics.get("net_return_bps"),
        "net_ci_bps": [metrics.get("net_ci_low_bps"), metrics.get("net_ci_high_bps")],
        "ci": metrics.get("ci"),
        "costs": costs,
        "sample_size": metrics.get("sample_size"),
        "scientific_state": e2e.get("scientific"),
        "economic_state": e2e.get("economic"),
        "separated_with_ci": all(v is not None for v in (metrics.get("gross_ci_low_bps"), metrics.get("net_ci_low_bps"))),
        "note": "descritivo; não é edge nem autorização de capital",
    }
    supported = sum(1 for p in placebo if p["scientific"] == "SUPPORTED")
    controls = {
        "future_injection": {"accepted_results": int(future["status"] == "RESULT"), "status": future["status"],
                             "reason": future["reason"], "pass": future["status"] == "TEMPORAL_INTEGRITY_VIOLATION"},
        "temporal_ablation": {"accepted_results": sum(1 for a in ablation if a["status"] == "RESULT"),
                              "statuses": [a["status"] for a in ablation],
                              "pass": all(a["status"] == "TEMPORAL_INTEGRITY_VIOLATION" for a in ablation)},
        "shuffled_labels": {"runs": len(placebo), "supported": supported, "threshold": 10,
                            "states": {s: sum(1 for p in placebo if p["scientific"] == s)
                                       for s in sorted({p["scientific"] for p in placebo})},
                            "pass": len(placebo) == 100 and supported <= 10},
    }
    # canário: nada produzido por pedidos legítimos pode carregar o token nem datas pós-cutoff
    leak = []
    for work in experiments(env).iterdir():
        result_file = work / "research-result.json"
        if not result_file.exists():
            continue
        for artifact in ("research-result.json", "domain-effect.json", "trials-v2.json", "worker-request.json"):
            path = work / artifact
            if path.exists():
                text = path.read_text(encoding="utf-8")
                if CANARY_MARKER in text or any(d in text for d in POST_CUTOFF_DATES):
                    leak.append(str(path))
    for outcome in (args.state / "outcomes").glob("*.json"):
        data = json.loads(outcome.read_text(encoding="utf-8"))
        if data.get("status") in {"RESULT", "DUPLICATE"}:
            text = json.dumps(data)
            if CANARY_MARKER in text or any(d in text for d in POST_CUTOFF_DATES):
                leak.append(str(outcome))
    canary = {"token": CANARY_MARKER, "post_cutoff_dates": POST_CUTOFF_DATES, "leaks": leak, "pass": not leak}
    report = {"economic_metrics": economic, "negative_controls": controls, "future_canary": canary,
              "vectors": [{k: v for k, v in r.items() if k != "result"} for r in rows]}
    (args.out / "SCIENCE_REAL.json").write_text(json.dumps(report, indent=1, ensure_ascii=False), encoding="utf-8")
    ok = economic["separated_with_ci"] and all(c["pass"] for c in controls.values()) and canary["pass"]
    print(json.dumps({"ok": ok, "supported_placebo": supported, "leaks": len(leak)}))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
