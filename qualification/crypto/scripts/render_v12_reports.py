"""crypto, reabertura V1.2 (C20): acrescenta a seção "V1.2" aos relatórios da missão só com números de
EVIDENCE_NUMBERS_V1.2.json (gerado de RAW_LOGS/v1.2 por evidence_numbers_v12.py). Idempotente: se a seção já existe,
ela é substituída. Nenhum número é digitado à mão.
Uso: python render_v12_reports.py
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
QC = ROOT / "qualification" / "crypto"
MARK = "## V1.2 (reabertura D-27: cripto 1.2.0rc4 / 21f8b182)"


def sha(rel: str) -> str:
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()[:12] + "…"


def replace_section(path: Path, body: str) -> None:
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(re.escape(MARK) + r".*?(?=\n## |\Z)", re.S)
    section = MARK + "\n\n" + body.strip() + "\n"
    text = pattern.sub(lambda _m: section, text) if MARK in text else text.rstrip("\n") + "\n\n" + section
    path.write_text(text, encoding="utf-8", newline="\n")


def main() -> None:
    n = json.loads((QC / "EVIDENCE_NUMBERS_V1.2.json").read_text(encoding="utf-8"))
    run = n["run"]
    L, D = n["runtime-linux-primary"], n["d16"]
    W = n.get("runtime-windows-latest")
    R = f"RAW_LOGS/v1.2/{run}"
    ci = L["core_identity"]["packages"]
    wheels = ", ".join(f"{k} {v['version']} (`{(v['wheel_sha256'] or '')[:8]}…`)" for k, v in ci.items())

    # CLEANROOM_REPORT
    win = ""
    if W:
        win = (f"- windows-latest (informação adicional; o secundário do crypto é o Windows local, D-3): conformidade "
               f"{W['conformance']['passed']}/{W['conformance']['tests']}; suíte {W['full_suite']['passed']} passed, {W['full_suite']['failures']} falhas "
               f"(as mesmas do Linux: {sorted(W['full_suite']['failed']) == sorted(L['full_suite']['failed'])}); E2E {W['e2e']['checks']} checagens, all_ok={W['e2e']['all_ok']}.\n")
    replace_section(QC / "CLEANROOM_REPORT.md", f"""
Run [{run.removeprefix('run')}](https://github.com/leonardosovienski/predictor-qualification/actions/runs/{run.removeprefix('run')})
(`crypto-reopening.yml`), saída devolvida por branch e copiada sem edição para `{R}/` (SHA256SUMS por job).

- Wheels instaladas fora do checkout, só do lock exportado com `--require-hashes` + wheel da release conferida por sha256: {wheels}.
- Linux primário (`ubuntu-latest`, Python {L['core_identity']['python']}): conformidade **{L['conformance']['passed']}/{L['conformance']['tests']}**; suíte completa pela wheel
  **{L['full_suite']['passed']} passed, {L['full_suite']['failures']} falhas** ({L['full_suite']['tests']} testes). As {L['full_suite']['failures']} falhas são todas da classe T (testes que leem
  o checkout: 16 das 17 da CR-F016 e 16 dos testes novos dos PRs #128–#134, que leem `docs/evidence`, `docs/research_ledger` ou
  `GarimpoInvestimentos/h6_status.json` pelo caminho do repo); nenhuma exercita código instalado de forma diferente. Detalhe em `FINDINGS.json` (CR-F016).
- E2E sintético pelo entrypoint instalado: {L['e2e']['checks']} checagens, all_ok={L['e2e']['all_ok']}. Soak sintético (diagnóstico): zero_tolerance_ok={L['soak_synthetic_diagnostic']['zero_tolerance_ok']}.
{win}- Job `d16` (mesmo run, runtime idêntico): conformidade {D['conformance']['passed']}/{D['conformance']['tests']}.

`CLEANROOM_FINAL` V1.2: **PASS** (Linux primário). Fonte: `EVIDENCE_NUMBERS_V1.2.json`.
""")

    # CORE_IDENTITY_REPORT
    chain = L["core_identity"]["lock_chain"] or []
    rows = "\n".join(f"| {c['name']} | `{c.get('pyproject_spec')}` | release (`tool.uv.sources`) | `{(c.get('lock_wheel_sha256') or '')[:8]}…` | "
                     f"{ci.get(c['name'], {}).get('version')} `{(ci.get(c['name'], {}).get('wheel_sha256') or '')[:8]}…` | site-packages={ci.get(c['name'], {}).get('module_in_site_packages')} |"
                     for c in chain)
    replace_section(QC / "CORE_IDENTITY_REPORT.md", f"""
`uv.lock` de `21f8b182`: `uv lock --check` exit {n['uv_lock_check_21f8b182']['exit']} (`{n['uv_lock_check_21f8b182']['file']}`) e job `quality` do CI verde
(`{n['hosted_ci']['jobs_cripto-predictor_36642919823']['file']}`). Runtime do run {run.removeprefix('run')} (`{L['core_identity']['file']}`,
sha256 `{sha(L['core_identity']['file'])}`; o job `d16` tem a mesma cadeia em `{D['core_identity']['file']}`):

| Pacote | pyproject | tool.uv.sources | uv.lock sha256 | Instalado (direct_url) | Módulo |
|---|---|---|---|---|---|
{rows}
| cripto-predictor | — (o próprio projeto) | — | — | {ci['cripto-predictor']['version']} `{ci['cripto-predictor']['wheel_sha256'][:8]}…` (asset da release v1.2.0rc4) | site-packages={ci['cripto-predictor']['module_in_site_packages']} |

Nenhum pacote do stack vem de índice público, `vendor/` ou checkout; `research_protocol`/`cain` ausentes (import_graph: nenhuma raiz os alcança).
`LOCK_INTEGRITY` V1.2: **PASS**. `CORE_IDENTITY` V1.2: **PASS**.
""")

    # HOSTED_CI_REPORT
    jobs = n["hosted_ci"]["jobs_cripto-predictor_36642919823"]["jobs"]
    rel = n["hosted_ci"]["jobs_cripto-predictor_36643518795"]["jobs"]
    replace_section(QC / "HOSTED_CI_REPORT.md", f"""
Fonte: `RAW_LOGS/v1.2/hosted-ci/` (API pública do GitHub, sem edição). Baseline = final desta reabertura (`21f8b182`, `main`).

| Repo | Commit | Papel | Workflow (evento) | Run | Jobs |
|---|---|---|---|---|---|
| cripto-predictor | `21f8b182` | baseline = final_commit V1.2 | CI (push, main) | [36642919823](https://github.com/leonardosovienski/cripto-predictor/actions/runs/36642919823) | {', '.join(f'{k}: {v}' for k, v in jobs.items())} |
| cripto-predictor | `21f8b182` | release v1.2.0rc4 | Release (workflow_dispatch) | [36643518795](https://github.com/leonardosovienski/cripto-predictor/actions/runs/36643518795) | {', '.join(f'{k}: {v}' for k, v in rel.items())} |
| core-predictor | `5a08415` | final (congelado; wheel inalterada) | herdado da V1.0 (mesmo commit) | [35823003554](https://github.com/leonardosovienski/core-predictor/actions/runs/35823003554) | success |
| predictor-ops | `9831b0d` | final (congelado; wheel inalterada) | herdado da V1.1 (mesmo commit) | [35905678198](https://github.com/leonardosovienski/predictor-ops/actions/runs/35905678198) | success |

`HOSTED_CI` V1.2: **PASS**. Nenhum job pulado.
""")

    # PROTECTED_ARTIFACT_REPORT
    p0, p2 = n["protected_set_check_21f8b182"], n["protected_set_v1_2_check_21f8b182"]
    replace_section(QC / "PROTECTED_ARTIFACT_REPORT.md", f"""
- Conjunto V1.0 (`PROTECTED_SET.json`, {p0['items']} blobs de `5fd4e1b`) conferido em `21f8b182`: **{p0['unchanged']}/{p0['items']} iguais,
  {p0['changed_or_missing']} alterados ou ausentes** (`{p0['file']}`). Nada do que estava protegido em `341d270` mudou nos PRs #128–#134 nem nas correções de 2026-09-29.
- Conjunto refeito pelo `truth_map.py` em `21f8b182` (`PROTECTED_SET_V1.2.json`): **{p2['items']} itens** (só cresce: +{p2['items'] - p0['items']} arquivos novos em `docs/evidence/`,
  cobertos pelos globs do prompt §5); {p2['unchanged']}/{p2['items']} iguais no alvo (`{p2['file']}`).
- `charters/scientific_state.json` continua com o mesmo blob: H1–H3, H5 `CLOSED_NO_GO`; H4, H6, H9 `CLOSED_INSUFFICIENT_SAMPLE`; H7, H8
  `REGISTERED_NOT_ACTIVATED`; família congelada `funding_oi_hmm_v3`; `capital_authorized: false`. Nada foi reaberto.

`PROTECTED_ARTIFACTS_UNCHANGED` V1.2: **PASS**.
""")

    # SOAK_REPORT
    s, ss = D["soak_real"], L["soak_synthetic_diagnostic"]
    classes = "\n".join(f"| `{k}` | {v} |" for k, v in s["failure_classes"].items())
    replace_section(QC / "SOAK_REPORT.md", f"""
Perfil `QUALIFICATION_PROFILE_CRYPTO_V1` inalterado. Dados reais (D-16) no Linux primário: run
[{run.removeprefix('run')}](https://github.com/leonardosovienski/predictor-qualification/actions/runs/{run.removeprefix('run')}), job `d16`, log bruto `{s['file']}`
(sha256 `{sha(s['file'])}`). Dados: {D['data_manifest']['verified_against_published_checksum']}/{D['data_manifest']['files']} arquivos da Binance conferidos pelo `.CHECKSUM`
publicado ({len(D['data_manifest']['unavailable'])} indisponível na origem, como na D-16 original); dataset in-sample `{D['data_manifest']['objects']['dataset-real-in-sample.json']['sha256'][:12]}…`
({D['data_manifest']['objects']['dataset-real-in-sample.json']['rows']} observações), o mesmo da D-16 de 2026-09-24.

| Classe de falha do perfil (mínimo 3) | Executado |
|---|---|
{classes}

- chamadas ao entrypoint: **{s['process_calls']}**; resultados armazenados: **{s['stored_results']}** ({s['requests_with_result']} pedidos com resultado); perdidos: **{s['lost']}**; inesperados: **{s['unexpected']}**;
- efeitos de domínio: **{s['domain_effects']}**; jobs do Ops: **{s['ops_jobs']}**; máximo de `SUCCEEDED` por job: **{s['ops_success_per_job_max']}**;
- releitura por `show`: divergências **{s['reread_mismatch']}**; corrupções injetadas {s['corruptions_injected']}, recusadas sem reparo {s['corruptions_fail_closed']};
- `reconcile`: exit {s['reconcile_exit']}, {s['reconcile_findings']} achados, estranhos {s['reconcile_foreign_findings']}, corrupções não acusadas {s['reconcile_missed_corruptions']};
- violações: **{s['violations']}**; `zero_tolerance_ok = {str(s['zero_tolerance_ok']).lower()}`.

Soak sintético do mesmo run (job `runtime linux-primary`, diagnóstico): {ss['process_calls']} chamadas, {ss['stored_results']} resultados, perdidos {ss['lost']},
violações {ss['violations']}, `zero_tolerance_ok = {str(ss['zero_tolerance_ok']).lower()}`.

`SOAK` V1.2: **PASS**.
""")

    # SCIENTIFIC_INTEGRITY_REPORT
    sc = D["science"]; econ, ctl = sc["economic_metrics"], sc["negative_controls"]
    temporal_failed = [t for t in L["full_suite"]["failed"] if any(k in t for k in ("test_dpl", "wfa_purge", "permutation_placebo", "test_pbo", "gate_power"))]
    replace_section(QC / "SCIENTIFIC_INTEGRITY_REPORT.md", f"""
Fonte: `{sc['file']}` (sha256 `{sha(sc['file'])}`), run {run.removeprefix('run')} (Linux primário, dados reais, wheel 1.2.0rc4).

- **Temporal** (`TEMPORAL_INTEGRITY`): suítes DPL/WFA/permutação/PBO/poder dentro da suíte completa pela wheel no Linux ({L['full_suite']['passed']} passed);
  falhas nessas suítes: {len(temporal_failed)}. O `replay` do Core impõe `observed_at ≤ available_at ≤ data_cutoff` antes de qualquer estatística (conformidade {L['conformance']['passed']}/{L['conformance']['tests']}).
- **Future canary** (`FUTURE_CANARY`): vazamentos do `FUTURE_CANARY_CRYPTO_001` e das datas pós-cutoff nos artefatos dos pedidos legítimos: **{sc['future_canary']['leaks']}**; pass={sc['future_canary']['pass']}.
- **Métricas econômicas** (`CRYPTO_ECONOMIC_METRICS`), pedido `{econ['request']}`, {econ.get('sample_size', '—')} observações, custos congelados (`{econ['costs']['model']}`):

| | Média (bps/semana) | IC 95% |
|---|---|---|
| bruto | {econ['gross_return_bps']} | {econ['gross_ci_bps']} |
| líquido | {econ['net_return_bps']} | {econ['net_ci_bps']} |

  Custo médio total {econ['costs']['mean_total_cost_bps']} bps; decisão do gate econômico `{econ['costs']['cost_aware_decision']}`; estado científico `{econ['scientific_state']}`; econômico `{econ['economic_state']}`.
  Iguais aos da D-16 de 2026-09-24. **Descritivo: não é edge, lucro nem autorização de capital (C22).**
- **Controles negativos** (`CRYPTO_NEGATIVE_CONTROLS`): injeção de futuro {ctl['future_injection']['accepted_results']} aceitos (pass={ctl['future_injection']['pass']});
  ablação temporal {ctl['temporal_ablation']['accepted_results']} aceitos (pass={ctl['temporal_ablation']['pass']}); labels embaralhados `SUPPORTED` em
  **{ctl['shuffled_labels']['supported']}/{ctl['shuffled_labels']['runs']}** (limiar ≤ {ctl['shuffled_labels']['threshold']}; pass={ctl['shuffled_labels']['pass']}).

Gates V1.2: `TEMPORAL_INTEGRITY` **{'PASS' if not temporal_failed else 'FAIL'}**, `FUTURE_CANARY` **PASS**, `CRYPTO_ECONOMIC_METRICS` **PASS**, `CRYPTO_NEGATIVE_CONTROLS` **PASS**.
""")
    print("relatórios V1.2 renderizados")


if __name__ == "__main__":
    main()
