"""stocks / D-16: aplica os vereditos de d16_finalize.py ao GATES.json e gera os relatórios (C20).

Todo número vem de qualification/stocks/D16_EVIDENCE_NUMBERS.json (tirado dos logs brutos por
d16_finalize.py). Atualiza só os 4 gates bloqueados pela D-16 (E2E, WINDOWS_SMOKE, SOAK,
STOCKS_NEGATIVE_CONTROLS), os ambientes, phases_completed (+ "d16"), EVIDENCE_CONSISTENCY
(evidências novas) e o estado terminal; copia a evidência do E2E real para E2E_EVIDENCE/ e escreve
D16_REAL_DATA_REPORT.md. Parciais existentes nunca são tocados (o parcial d16 sai de attest.py).

Uso: python d16_apply.py <run_id>
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
QC = ROOT / "qualification" / "stocks"
REL = "qualification/stocks"


def bps(value) -> str:
    return "—" if value is None else f"{value:+d} bps"


def main() -> int:
    run_id = sys.argv[1]
    numbers = json.loads((QC / "D16_EVIDENCE_NUMBERS.json").read_text(encoding="utf-8"))
    run = f"{REL}/RAW_LOGS/d16/run{run_id}"
    lp, lc, wl = (f"{run}/stocks-d16-{r}" for r in ("linux-primary", "linux-controls", "windows-latest"))
    g = numbers["gates"]
    envs = numbers["environments"]
    econ = numbers["economic"]
    m = econ["metrics"] or {}
    ledger = json.loads((QC / "GATES.json").read_text(encoding="utf-8"))
    common_ev = [f"{REL}/d16/SOURCES.json", f"{REL}/D16_EVIDENCE_NUMBERS.json"]

    # E2E evidence copies (C16 E2E_EVIDENCE/)
    for name, src in (("d16-linux-primary-real", lp), ("d16-windows-latest-real", wl)):
        target = QC / "E2E_EVIDENCE" / name
        target.mkdir(parents=True, exist_ok=True)
        for f in ("E2E_SUMMARY.json", "outcome_file.json", "process_stdout.json", "show_new_process.json"):
            source = ROOT / src / "e2e" / f
            if source.is_file():
                shutil.copyfile(source, target / f)

    e = g["E2E"]["linux"]
    ledger["gates"]["E2E"] = {
        "status": g["E2E"]["status"],
        "evidence": [f"{lp}/e2e/E2E_SUMMARY.json", f"{lp}/e2e/outcome_file.json", f"{lp}/e2e.log", f"{lp}/core_identity.json",
                     f"{lp}/BUILD_MANIFEST.json", f"{lp}/verify_prefilter.json", f"{lp}/REAL_ENV.json",
                     f"{REL}/E2E_EVIDENCE/d16-linux-primary-real/E2E_SUMMARY.json", *common_ev],
        "note": (f"D-16, dado real público (run {run_id}, ubuntu-latest, só final wheels): painel stocks-pit-panel/1 "
                 f"sha256 {(envs['linux-primary']['panel_sha256'] or '?')[:12]}… (fixado em SOURCES.json: "
                 f"{envs['linux-primary']['panel_matches_pin']}), fontes baixadas no job e "
                 f"conferidas ({envs['linux-primary']['sources_downloaded_in_job']}/{envs['linux-primary']['sources_total']}), "
                 f"pré-filtro neutro em {envs['linux-primary']['rebalances']} rebalances; entrypoint stocks-research: "
                 f"{e['checks_ok']}/{e['checks']} checagens (processo → término → processo novo relê o mesmo resultado; "
                 f"provenance contra admission, journal, Core, Ops, efeito); resultado {e['result_state']} "
                 f"({e['scientific_state']}/{e['economic_state']}), capital_permission={e['capital_permission']}."),
    }
    w = g["WINDOWS_SMOKE"]
    ledger["gates"]["WINDOWS_SMOKE"] = {
        "status": w["status"],
        "evidence": [f"{wl}/e2e/E2E_SUMMARY.json", f"{wl}/e2e/outcome_file.json", f"{wl}/restart.jsonl", f"{wl}/core_identity.json",
                     f"{wl}/BUILD_MANIFEST.json", f"{wl}/conformance.junit.xml", f"{wl}/env.log", *common_ev],
        "note": (f"D-16 no windows-latest × py3.13 (run {run_id}, D-1), só final wheels e o mesmo painel real "
                 f"(sha256 igual ao Linux: {w['panel_same_as_linux']}): E2E {w['e2e']['checks_ok']}/{w['e2e']['checks']}; "
                 f"restart em {w['restart']['restarts']} pontos de morte do processo com tolerância zero "
                 f"({'OK' if w['restart']['zero_tolerance_ok'] else 'VIOLADA'}); conformidade "
                 f"{(w['conformance'] or {}).get('passed')}/{(w['conformance'] or {}).get('tests')}; métricas iguais às do Linux: "
                 f"{w['metrics_equal_linux']}."),
    }
    s = g["SOAK"]
    c = s["counts"]
    ledger["gates"]["SOAK"] = {
        "status": s["status"],
        "evidence": [f"{lp}/soak.jsonl", f"{lp}/soak.log", f"{REL}/QUALIFICATION_PROFILE_STOCKS_V1.json", f"{REL}/SOAK_REPORT.md",
                     *common_ev],
        "note": (f"D-16, perfil congelado sobre o painel real (run {run_id}, Linux primário): {c['process_calls']} chamadas; "
                 f"{c['normal_cycles']} ciclos normais, {c['restarts']} restarts, {c['duplicates']} duplicados, "
                 f"{c['ops_worker_crash']}/{c['before_admission_commit']}/{c['during_result_write']} por classe de falha "
                 f"(crash do Ops/admission/gravação), {c['timeouts']} timeouts, {c['family_not_ready']} família-não-pronta, "
                 f"{c['collection_only_valid']} coletas COLLECTION_ONLY (CVM VLMO oficial), {c['eligible_trials']} trial elegível; "
                 f"perdidos {len(c['summary']['lost'] or [])}, inesperados {len(c['summary']['unexpected'] or [])}, "
                 f"violações PIT {len(c['summary']['pit_violations'] or [])}, contaminação de universo "
                 f"{len(c['summary']['universe_contamination'] or [])}, máx. SUCCEEDED por job {c['summary']['ops_success_per_job_max']}; "
                 f"tolerância zero {'OK' if c['zero_tolerance_ok'] else 'VIOLADA'}"
                 + (f"; abaixo do perfil: {s['below_profile']}" if s["below_profile"] else "") + "."),
    }
    n = g["STOCKS_NEGATIVE_CONTROLS"]
    crit = n["criteria"] or {}
    ledger["gates"]["STOCKS_NEGATIVE_CONTROLS"] = {
        "status": n["status"],
        "evidence": [f"{lc}/science/NEGATIVE_CONTROLS_SUMMARY.json", f"{lc}/science/negative_controls.jsonl", f"{lc}/science.log",
                     f"{lc}/BUILD_MANIFEST.json", f"{REL}/NEGATIVE_CONTROLS_REPORT.md", *common_ev],
        "note": (f"D-16, painel real (run {run_id}), {n['runs']} execuções pelo entrypoint (referência + 4 controles × 20 seeds "
                 f"congeladas): SUPPORTED com labels embaralhados {crit.get('SHUFFLED_LABELS', {}).get('supported')}/20 (máx. 2), "
                 f"ranking aleatório {crit.get('FEATURE_ABLATION', {}).get('supported')}/20 (máx. 2), ablação temporal IC inferior "
                 f"máx. {crit.get('TEMPORAL_ABLATION', {}).get('lagged_ci_low_bps_max')} bps × referência "
                 f"{crit.get('TEMPORAL_ABLATION', {}).get('reference_ci_low_bps')} bps, perturbação do universo "
                 f"{crit.get('UNIVERSE_PERTURBATION', {}).get('same_state_as_reference')}/20 no estado da referência (mín. 16); "
                 f"critérios congelados {'atendidos' if n['status'] == 'PASS' else 'NÃO atendidos'}."),
    }
    ev = ledger["gates"]["EVIDENCE_CONSISTENCY"]
    for item in (f"{REL}/D16_EVIDENCE_NUMBERS.json", f"{REL}/scripts/d16_finalize.py", f"{REL}/scripts/d16_apply.py"):
        if item not in ev["evidence"]:
            ev["evidence"].append(item)
    if "D-16" not in ev["note"]:
        ev["note"] += (" D-16: números dos 4 gates e das métricas reais tirados dos logs brutos do run "
                       f"{run_id} por scripts/d16_finalize.py (D16_EVIDENCE_NUMBERS.json).")

    linux_ok = all(g[k]["status"] == "PASS" for k in ("E2E", "SOAK", "STOCKS_NEGATIVE_CONTROLS"))
    ledger["environments"] = [
        {"os": "linux", "python": "3.13", "role": "primary", "where": "github_actions", "result": "PASS" if linux_ok else "FAIL",
         "evidence": [f"{lp}/env.log", f"{lp}/core_identity.json", f"{lp}/e2e/E2E_SUMMARY.json", f"{lp}/soak.jsonl",
                      f"{lc}/science/NEGATIVE_CONTROLS_SUMMARY.json"]},
        {"os": "windows", "python": "3.13", "role": "secondary", "where": "github_actions", "result": w["status"],
         "evidence": [f"{wl}/env.log", f"{wl}/core_identity.json", f"{wl}/e2e/E2E_SUMMARY.json", f"{wl}/restart.jsonl"]},
    ]
    if "d16" not in ledger["phases_completed"]:
        ledger["phases_completed"].append("d16")
    statuses = [v["status"] for v in ledger["gates"].values()]
    findings = json.loads((QC / "FINDINGS.json").read_text(encoding="utf-8"))["findings"]
    blockers = sum(1 for f in findings if f["status"].startswith("OPEN") and f["severity"] in ("P0", "P1"))
    if "FAIL" in statuses or blockers:
        terminal = "NOT_QUALIFIED"
    elif all(x == "PASS" for x in statuses):
        terminal = "QUALIFIED"
    else:
        terminal = "BLOCKED"
    ledger["terminal_state"] = terminal
    if terminal in ("QUALIFIED", "NOT_QUALIFIED"):
        ledger["final_result"] = terminal
    counts = {k: statuses.count(k) for k in ("PASS", "FAIL", "NOT_RUN")}
    ledger["note"] = (f"Estado corrente da missão stocks (STACK_BASELINE_V1.1, Ops 4.2.2rc1, stocks 0.3.0rc2 61fc017) depois da "
                      f"D-16 (run {run_id}, dados reais públicos B3/CVM fixados em qualification/stocks/d16/SOURCES.json): "
                      f"{counts['PASS']} PASS, {counts['FAIL']} FAIL, {counts['NOT_RUN']} NOT_RUN; P0/P1 abertos = {blockers}; "
                      f"estado terminal {terminal}. Parciais nunca reescritos (C8).")
    (QC / "GATES.json").write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")

    cont = numbers["contamination"]
    panel = numbers["panel"]
    cost = econ["costs"] or {}
    lines = [
        "# D-16 — métricas econômicas reais e evidência (missão stocks)",
        "",
        f"Gerado por `scripts/d16_apply.py` a partir de `D16_EVIDENCE_NUMBERS.json` (tirado dos logs brutos do run "
        f"[{run_id}](https://github.com/leonardosovienski/predictor-qualification/actions/runs/{run_id}) por "
        "`scripts/d16_finalize.py`). Nenhum número foi digitado à mão (C20).",
        "",
        "## Gates (critérios congelados)",
        "",
        "| Gate | Estado |",
        "|---|---|",
        *[f"| `{k}` | {g[k]['status']} |" for k in ("E2E", "WINDOWS_SMOKE", "SOAK", "STOCKS_NEGATIVE_CONTROLS")],
        "",
        f"Estado terminal da missão: **{terminal}** ({counts['PASS']} PASS, {counts['FAIL']} FAIL, {counts['NOT_RUN']} NOT_RUN).",
        "",
        "## Painel real",
        "",
        f"* `{panel.get('dataset_version')}`, cutoff `{panel.get('data_cutoff')}`, sha256 fixado `{numbers['expected_panel_sha256']}`; "
        "construído em cada job a partir das fontes baixadas: "
        + ", ".join(f"{name} {'=' if env['panel_matches_pin'] else '≠'} fixado ({env['sources_downloaded_in_job']}/"
                    f"{env['sources_total']} fontes baixadas e conferidas)" for name, env in envs.items()) + ".",
        f"* {panel.get('securities_kept')} ISIN no painel (de {panel.get('securities_total')} ações/units no COTAHIST da janela), "
        f"{(panel.get('counts') or {}).get('bars')} barras com revisões, {panel.get('corporate_adjustments')} eventos acionários "
        f"oficiais da B3 aplicados como revisões PIT; identidade: {panel.get('identity_sources')}; sem CNPJ: "
        f"{panel.get('kept_without_identity')}.",
        "",
        "## Sonda `stocks:QUAL-PIT-MOM-001` (momentum 12-1, quintil superior, top 60 PIT; não é hipótese científica)",
        "",
        f"Estado: **{econ['result_state']}** (científico {econ['scientific_state']}, econômico {econ['economic_state']}); "
        f"{m.get('periods')} períodos de carteira ({econ['first_rebalance']} → {econ['last_period_end']}, rebalance a cada 21 "
        f"pregões — ST-F007); universo de {econ['universe_sizes']} ações e carteira de {econ['portfolio_sizes']} em todo período. "
        f"Validação temporal do Core (`{(econ['temporal_validation'] or {}).get('method')}`): "
        f"{(econ['temporal_validation'] or {}).get('status')} em {(econ['temporal_validation'] or {}).get('records')} registros, "
        f"máx. available_at {(econ['temporal_validation'] or {}).get('max_available_at')} ≤ as_of.",
        "",
        "| Média por período | Bruto | Líquido |",
        "|---|--:|--:|",
        f"| Estratégia | {bps(m.get('strategy_gross_bps'))} | {bps(m.get('strategy_net_bps'))} |",
        f"| Baseline EW do universo | {bps(m.get('baseline_gross_bps'))} | {bps(m.get('baseline_net_bps'))} |",
        f"| Excesso | {bps(m.get('excess_gross_bps'))} | {bps(m.get('excess_net_bps'))} |",
        f"| IC95 do excesso (bootstrap estacionário, bloco {(m.get('ci') or {}).get('block_length')}, "
        f"{(m.get('ci') or {}).get('n_boot')} reamostras, seed {(m.get('ci') or {}).get('seed')}) | "
        f"[{bps((m.get('excess_gross_ci_bps') or [None, None])[0])}, {bps((m.get('excess_gross_ci_bps') or [None, None])[1])}] | "
        f"[{bps((m.get('excess_net_ci_bps') or [None, None])[0])}, {bps((m.get('excess_net_ci_bps') or [None, None])[1])}] |",
        "",
        f"Custos (H1, por lado): emolumentos {cost.get('b3_fee_bps_per_side')} bps + spread/slippage "
        f"{cost.get('slippage_bps_per_side')} bps; custo médio por período: estratégia {bps(cost.get('strategy_mean_cost_bps'))}, "
        f"baseline {bps(cost.get('baseline_mean_cost_bps'))}. Drawdown máximo da estratégia (líquido): "
        f"{bps(m.get('strategy_max_drawdown_bps'))}; acerto do excesso líquido: {m.get('hit_rate_excess_net')}. "
        f"Campo `baseline_comparison.outcome` do resultado: {(econ.get('baseline_comparison') or {}).get('outcome')} "
        "(é só o sinal da média do excesso líquido; não é teste estatístico — o que vale é o IC95 acima).",
        "",
        "Leitura: " + ("o IC95 do excesso bruto contém zero — sem evidência de edge (INCONCLUSIVE); nada disso concede capital "
                       "(capital_permission = false) nem vale fora deste painel, commit e janela (C22)."
                       if econ["scientific_state"] == "INCONCLUSIVE" else
                       f"estado {econ['scientific_state']}/{econ['economic_state']} pelas regras congeladas; nada disso concede "
                       "capital (capital_permission = false) nem vale fora deste painel, commit e janela (C22)."),
        "",
        "## Contaminação por eventos não ajustados (ST-F008, diagnóstico)",
        "",
        f"Eventos corporativos NÃO ajustados considerados (salto > 30% com troca do número de distribuição + bonificação "
        f"em outra classe): {cont['unadjusted_events_considered']}. Períodos com algum deles dentro de (início, fim]: "
        f"carteira {cont['portfolio_periods_affected']} de {cont['periods']}, universe/baseline {cont['universe_periods_affected']} "
        f"de {cont['periods']}.",
        "",
        *[f"* carteira: período {h['period_start']}, {h['security_id']} em {h['event_session']} ({h['why']})"
          for h in cont["portfolio_hits"]],
        *[f"* universo: período {h['period_start']}, {h['security_id']} em {h['event_session']} ({h['why']})"
          for h in cont["universe_hits"]],
        "",
        "Retorno só-preço (proventos em dinheiro não reinvestidos), como a rota (b) da H1: viés declarado.",
        "",
    ]
    (QC / "D16_REAL_DATA_REPORT.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")

    old_state = "**Estado do gate: NOT_RUN — BLOCKED: D-16 pendente.**"
    soak_section = "\n".join([
        "", f"## D-16 — soak sobre o painel real (run {run_id})", "",
        f"Log bruto: `{lp}/soak.jsonl` (d16/d16_soak.py, perfil congelado, runtime suportado, Linux primário).", "",
        "| medida | valor | mínimo do perfil |", "|---|---|---|",
        *[f"| {k} | {c[k]} | {s['profile_minimums'].get(k, '—')} |" for k in (
            "process_calls", "normal_cycles", "restarts", "duplicates", "ops_worker_crash", "before_admission_commit",
            "during_result_write", "timeouts", "family_not_ready", "collection_only_valid", "eligible_trials")],
        *[f"| {k} | {json.dumps(v, ensure_ascii=False)} | |" for k, v in c["summary"].items()],
        f"| tolerância zero | {c['zero_tolerance_ok']} | |", "",
        f"**Gate SOAK: {s['status']}.**", ""])
    nc_section = "\n".join([
        "", f"## D-16 — controles negativos sobre o painel real (run {run_id})", "",
        f"Logs brutos: `{lc}/science/negative_controls.jsonl`, `{lc}/science/NEGATIVE_CONTROLS_SUMMARY.json` "
        "(d16/d16_science.py; mesmas seeds e critérios congelados).", "",
        f"Referência (painel real): {json.dumps(n['reference'], ensure_ascii=False)}", "",
        "| controle | SUPPORTED | critério congelado |", "|---|---|---|",
        *[f"| {k} | {(n['supported_counts'] or {}).get(k)}/20 | {json.dumps(crit.get(k), ensure_ascii=False)} |"
          for k in ("SHUFFLED_LABELS", "TEMPORAL_ABLATION", "FEATURE_ABLATION", "UNIVERSE_PERTURBATION")],
        "", f"**Gate STOCKS_NEGATIVE_CONTROLS: {n['status']}** ({n['runs']} execuções).", ""])
    for name, section, status in (("SOAK_REPORT.md", soak_section, s["status"]),
                                  ("NEGATIVE_CONTROLS_REPORT.md", nc_section, n["status"])):
        path = QC / name
        text = path.read_text(encoding="utf-8")
        text = text.replace(old_state, f"**Estado do gate: {status} (D-16, run {run_id}; seção D-16 no fim).** "
                                       "A execução com a fixture sintética logo abaixo é o diagnóstico anterior à D-16.")
        if section.strip().splitlines()[0] not in text:  # idempotente por run
            text = text.rstrip("\n") + "\n" + section
        path.write_text(text, encoding="utf-8", newline="\n")
    print(json.dumps({"terminal": terminal, "counts": counts, "blockers": blockers}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
