"""brasileirao: renderiza as tabelas de REAL_DATA_METRICS.md a partir de EVIDENCE_NUMBERS.json (C20)."""
import json
import sys

d = json.load(open(sys.argv[1], encoding="utf-8"))["metrics"][sys.argv[2]]
f = lambda x, p=4: "—" if x is None else f"{x:+.{p}f}"
ci = lambda c: "—" if not c or c[0] is None else f"[{c[0]:+.4f}, {c[1]:+.4f}]"
print("| Pedido (temporada-alvo-baseline) | Estado | n | Score modelo | Score baseline | Δ médio [IC95] | Apostas | ROI bruto/aposta [IC95] | ROI líquido/aposta [IC95] | Líquido após imposto (u) |")
print("|---|---|---|---|---|---|---|---|---|---|")
for r in d["requests"]:
    print(f"| {r['request']} | {r['result_state']} | {r['n_evaluated']} | {f(r['model_score'])} | {f(r['baseline_score'])} | {f(r['mean_delta'])} {ci(r['ci_delta'])} | {r['n_bets'] if r['n_bets'] is not None else '—'} | {f(r['roi_gross'])} {ci(r['ci_gross_mean'])} | {f(r['roi_net'])} {ci(r['ci_net_mean'])} | {f(r['net_after_tax_total'], 2)} |")
print()
print("| Diagnóstico abertura (temporada-alvo) | Apostas na abertura | CLV médio | IC95 (normal iid) | ROI líquido na abertura |")
print("|---|---|---|---|---|")
for k, v in d["clv_diagnostic_open_price"].items():
    print(f"| {k} | {v['n_bets_open']} | {v['mean_clv']:+.4f} | [{v['clv_iid_normal_ci95'][0]:+.4f}, {v['clv_iid_normal_ci95'][1]:+.4f}] | {v['roi_net_open']:+.4f} |")
