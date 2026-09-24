# QUALIFICATION_CHANGELOG — missão stocks (Etapa A)

O que a missão mudou, onde, por quê, com commit e PR. `core-predictor` e `predictor-ops` **não** foram alterados
(congelados na Etapa A; Ops consumido pela release v4.2.2rc1, D-17). Nenhuma hipótese foi promovida ou reaberta
(H7–H19 como estão); nenhum treinamento; nenhum capital.

## stocks-predictor (branch `qualification/stocks-stage-a`, PR #95)

| Commit | O quê | Por quê | Teste que prova |
|---|---|---|---|
| `3e5045a` | `research_contract.py`: schemas `stocks-research-request/1` e `stocks-research-result/1`, IDs `stocks:`, estados operacional/científico/econômico separados, invariantes de autoridade | §8/§9; C18; C24.1 | `tests/conformance/test_contract_conformance.py`, `tests/test_research_units.py` |
| `3e5045a` | `research_admission.py`: policy do operador (`LOCAL_FILE_ONLY`), allowlist compilada de 2 handlers, H1–H22/`stocks:H<n>` nunca admitidas, cota de pendentes | §7.2 (ADMISSION) | `test_admission_rejects_before_any_execution` (21 vetores), `test_collector_outside_policy_is_rejected` |
| `3e5045a` | `research_execution.py`: handler como **job real do predictor_ops** (lock, heartbeat, timeout, attempt, idempotência econômica); estado científico relido do `TrialRegistryV2` do Core; resultado determinístico com hash no journal antes da escrita; falha fechada em corrupção | §7.3 (OPS_RUNTIME), §9 | `tests/conformance/test_failure_recovery.py`, `test_failure_extra.py` |
| `3e5045a` | `research_pit.py`: visão PIT do painel (`available_at`, revisões, listagem/deslistagem conhecidas, identidade por `security_id` e CNPJ), universo de liquidez com as regras de `universe.rank_universe` + correções PIT | §10 (universo, PIT) | `tests/conformance/test_pit_adversarial.py` (PIT-01..15) |
| `3e5045a` | `research_worker.py`: walk-forward com `factor.signals`, `portfolio.select_portfolio`, custos de `execution` para estratégia e baseline EW; `replay`, `bootstrap_ci`, `max_drawdown`, `dataset_fingerprint` e `TrialRegistryV2` do Core; controles negativos | §9, §10 | conformidade + `test_worker_in_process_writes_effect_and_core_trial` |
| `3e5045a` | `research_readiness.py` + `research_collect_worker.py`: eixos de External Intelligence (elegibilidade só por `readiness`, PIT efetivo da matriz); coleta COLLECTION_ONLY como job do Ops pelo CLI de domínio | §10 (AXES, COLLECTION_MODE) | `test_external_intelligence_not_ready_never_becomes_a_signal`, `test_collection_only_collects_persists_and_never_feeds_a_trial` |
| `3e5045a` | `research_results.py`, `research_recovery.py`, `research_runner.py` + `[project.scripts] stocks-research` | C24.1 entrypoint, authoritative_result_source | `test_e2e_result_is_reread_identically_after_restart`, `test_import_closure.py` |
| `3e5045a` | `stocks_predictor/adapters/` reservado (vazio) | C24.1 `adapter_paths` | `test_no_entrypoint_reaches_envelope_cain_or_adapter_paths`, `test_nothing_outside_adapter_paths_imports_them` |
| `3e5045a` | `pyproject.toml`/`uv.lock`: `predictor-ops==4.2.2rc1` pela release (sha256 `0be70bfb…`), `tzdata>=2025.2`, versão `0.3.0rc1` | §7.1; **ST-F001** (P1: `ZoneInfo('America/Sao_Paulo')` quebrava import de `external_intelligence`/`operations` no Windows) | `tests/test_timezone_runtime.py`; suíte coleta tudo no windows-latest (antes: 2 erros de coleta) |
| `a02e00e`, `84c8761` | fixtures de conformidade: painel curto sem evento fora do calendário; custo do vetor `case_b` que zera o excesso líquido | vetores do caso B congelado | conformidade |
| `57c6f7e` | tipos Optional | pyright do CI | CI |
| `a2339cf`, `9820418`, `9a6c09a` | recibos R8 (carga real COTAHIST_A2026 55.986 linhas + capacidade 250 mil) e ressela de `docs/engineering/current-operational-evidence.json` | regra local R8 (AGENTS.md), **D-18** | `tools/verify_operational_evidence.py`, `tests/test_operational_evidence.py` |
| `9820418` | `tests/test_research_units.py`: testes em processo do circuito | cobertura medida (piso 77% mantido, não afrouxado) | CI Quality 3.13/3.14 |
| `9a6c09a` | `ecosystem_plugin.py` informa a versão instalada | **ST-F005** (P2: versão `0.2.0` fixa) | `test_ecosystem_plugin_reports_the_installed_version` |

**final_commit:** `9a6c09ae92991c8490be624f5693865bcbaeca26`. Pré-release
[`v0.3.0rc1`](https://github.com/leonardosovienski/stocks-predictor/releases/tag/v0.3.0rc1): wheel
`3cc4e04a04967efb11e16000815b8c632cf9659e2703b097a1277dabf5639467`, sdist
`d8d6f610100d9caa5f86ec2c6a063a02a3c4c6dd86465d01e1201200e22e5f98` (build reprodutível no Actions, run 35948598904).

## predictor-qualification (branch `stocks/qualification`)

| O quê | Por quê |
|---|---|
| `qualification/stocks/` (parâmetros congelados, baseline, truth-map, relatórios, contrato, parciais, RAW_LOGS) | C16 |
| `.github/workflows/stocks-suite.yml`, `stocks-runtime.yml`, `stocks-build-rc.yml`, `stocks-secrets.yml`, `stocks-evidence-check.yml` | todo Python do Stocks roda no Actions (D-1/D-9): suíte antes/depois, runtime limpo, build da rc, segredos, validação das attestations |
| `qualification/stocks/scripts/*` | coletor de baseline, truth-map, identidade, runtime limpo, E2E, soak, ciência, números dos logs, relatórios, gates |
| `qualification/DECISIONS.json`: **D-18** | C19: regra R8 × Python local/D-16 (autorização do dono) |
| `.gitattributes`: `qualification/stocks/RAW_LOGS/** -text` | logs brutos byte a byte (C20) |

## C14 — rc2 (ST-F006)

| Commit | O quê | Por quê | Teste que prova |
|---|---|---|---|
| `61fc017` (branch `qualification/stocks-rc2`, PR #96) | versão `0.3.0rc2`; ressela de `docs/engineering/current-operational-evidence.json` sobre o main (inclui hatchling 1.32.3 e checkout v7 dos #93/#94) | **ST-F006**: CI do main vermelho em `2a18513` (selo R8); o main divergia do final_commit `9a6c09a` | `tools/verify_operational_evidence.py`; CI dispatch 35953418753; suíte Linux/windows-latest (run 35953426762) |

Pré-release [`v0.3.0rc2`](https://github.com/leonardosovienski/stocks-predictor/releases/tag/v0.3.0rc2): wheel
`92cb1131b4f0ba0b4572d26cb03a1647e239a17f37514c0db1598797119366a8`, sdist
`b7a98bfedfd8e57d223e5e641cb2068e82c967aadf0798f6b74924e6e443a365` (build reprodutível, run 35953426669).
Refeitos (C14): publish-candidates, cleanroom-final/e2e/conformidade/ciência/soak (run 35954279991), CI hospedado,
segredos (run 35955382714), conjunto protegido. **final_commit:** `61fc017256ffea815ae96bbe02b847dccdb395cc`.

## D-16 (2026-09-24, sessão da noite no PC 2) — branch `stocks/d16-20260924` do predictor-qualification

Nenhum código do `stocks-predictor`, `core-predictor` ou `predictor-ops` mudou: alvo continua `61fc017` /
`v0.3.0rc2` (`92cb1131…`), Core 3.2.1, Ops 4.2.2rc1. Nenhum parâmetro, vetor, perfil, seed ou critério congelado mudou (C15).

| Commit | O quê | Por quê |
|---|---|---|
| `a7be0cf` | `d16/verify_stage_a.py` + `RAW_LOGS/d16/stage-a/verify_stage_a.json` | passo 0: a Etapa A se sustenta (62/62: evidências dos 22 parciais no commit de emissão — número corrigido: o changelog dizia 23, o log bruto diz 22, 27 PASS, wheels baixadas com sha256 conferido) |
| `1b8b885` | `d16/build_real_panel.py`, `d16/SOURCES.json`, `d16/PROTOCOL_REAL.json`, `d16/verify_prefilter.py`, `d16/real_env.py`, `d16/d16_soak.py`, `d16/d16_science.py`, `d16/d16_run.sh`, `.github/workflows/stocks-d16.yml`; `D16_RUNBOOK.md` §4; FINDINGS ST-F007/ST-F008; `RAW_LOGS/d16/suite-run35978266234` | construtor `dados reais públicos → stocks-pit-panel/1` e fixação de URL + sha256 das fontes antes da execução (D-16); suíte no alvo 61fc017 (1049 passed Linux e windows-latest) |
| `5d1944c` | `build_real_panel.fetch`: download com retomada (Range/If-Range) | run 35981568362 parou no setup (falha fechada): a B3 cortava a transferência para o runner (`IncompleteRead`); defeito de kit |
| `4f138da` | `RAW_LOGS/d16/run35983568296/`, `D16_EVIDENCE_NUMBERS.json`, `D16_REAL_DATA_REPORT.md`, `E2E_EVIDENCE/d16-*`, `GATES.json`, seções D-16 de `SOAK_REPORT.md` e `NEGATIVE_CONTROLS_REPORT.md`; `scripts/d16_finalize.py`, `scripts/d16_apply.py` | fechamento dos 4 gates pelos critérios congelados, números tirados dos logs brutos (C20) |
| (este) | `RAW_LOGS/secrets/run35986948802/`, `SECRETS_CLEAN` no `GATES.json` (nota corrigida: o log diz 10 commits varridos, não 7); `FROZEN_VECTORS.json` + `scripts/frozen_vectors.py`; `ATTESTATION_PARTIAL_d16.json`, `QUALIFICATION_ATTESTATION.json` | varredura de segredos sobre a árvore com os logs novos; o schema exige `frozen_vectors_sha256` numa attestation final e a missão stocks não tinha o manifesto: ele só registra a identidade (blob git + sha256) dos vetores de conformidade no final_commit 61fc017 — idênticos aos do final_commit da rc1 9a6c09a — e dos vetores reais da D-16; nenhum vetor mudou |

Resultado: E2E, WINDOWS_SMOKE, SOAK e STOCKS_NEGATIVE_CONTROLS em PASS (run 35983568296); 31/31 gates PASS, P0 = P1 = 0 →
`QUALIFIED` (vale com o merge do dono). Sonda `stocks:QUAL-PIT-MOM-001` no painel real: INCONCLUSIVE / NO_EDGE (ver
`D16_REAL_DATA_REPORT.md`). Pendências P2 para o dono: ST-F007 (rebalance a cada 21 pregões × "fim de mês"), ST-F008
(limitações do painel público).

### D-16, depois do merge (branch `stocks/d16-dispatch-only-20260924`)

| O quê | Por quê |
|---|---|
| `.github/workflows/stocks-d16.yml`: só `workflow_dispatch` (sem gatilho de push) | o push do merge refez a D-16 no main com o pin antigo; a resposta da B3 para ALOS tinha mudado e o build falhou fechado (run 36001349055). Fontes mutáveis exigem pin novo antes de cada execução, como no crypto-d16.yml |
| `RAW_LOGS/d16/run36001349055-main/` | preservar a evidência do run que falhou (C20; não é evidência de gate) |
| `D16_RUNBOOK.md` §6 | como rodar de novo (pin + dispatch) |

## C14 "Núcleo (versão)" v2.0 → v2.1 (D-19, 2026-09-24)

Núcleo v2.1 (PR #22) e schema com `common_core_version` 2.0|2.1 (PR #26). Nenhum requisito do stocks mudou (a D-19 só
admite `owner_linux` para dado privado). Sem refazer fases:

| Arquivo | O quê | Por quê | Prova |
|---|---|---|---|
| `scripts/attest.py` | `CORE_SHA` da v2.1 (`a3b4b7bb…`), `common_core_version` 2.1; `check()` confere também `environments[*].evidence`, `shared_dependency_verdicts[*].verdict_sha256` e `findings_file` | C7.1 regras 3 e 6; mesmo buraco do CR-F021 do crypto | `RAW_LOGS/c14-nucleo-v2.1/cr-f021_check.log`: cópias adulteradas nos 3 campos são acusadas |
| `QUALIFICATION_ATTESTATION.json` | reemitida: `QUALIFIED`, 31/31 PASS (mesmos estados), P0=P1=0, P2=5 | C7.1 regra 8 | `attest.py check` OK |
| `QUALIFICATION_ATTESTATION_superseded_c95145a78a46.json` | a anterior (v2.0), preservada byte a byte | C7.1 regra 8 | `supersedes_sha256` da nova |

`d16/verify_stage_a.py` continua conferindo o núcleo v2.0: é a verificação do passo 0 da D-16, feita no HEAD 3983de1, e fica como registro.

## C14 "Núcleo (versão)" v2.1 → v2.2 (D-20, 2026-09-24)

Núcleo v2.2 (PR #30): o C0.2 passa a conferir o schema pelo `MANIFEST.sha256`. Nenhum requisito do stocks mudou; nenhuma fase refeita.
`scripts/attest.py` com o sha256 da v2.2 (`d681e423…`) e `common_core_version` 2.2. O modo `--schema-only` (parciais históricos, CI) aceita os núcleos v2.0 e v2.1 em que eles foram emitidos.
`QUALIFICATION_ATTESTATION.json` reemitida: **QUALIFIED**, 31/31 PASS (mesmos estados), P0=0 P1=0 P2=5; a anterior foi preservada como
`QUALIFICATION_ATTESTATION_superseded_f7923a88b7be.json` (`supersedes_sha256`). `attest.py check` OK.

### Verificação da attestation reemitida no núcleo v2.2 (branch `stocks/verify-attestation-v22-20260924`)

| O quê | Por quê |
|---|---|
| `d16/verify_attestation.py`: regra 6 contra o sha256 do núcleo no próprio commit (não mais v2.0 fixo) + C0.2 (`MANIFEST.sha256` confere, com schema e núcleo) | a attestation foi reemitida na v2.1 (D-19) e na v2.2 (D-20); o verificador precisa seguir o núcleo do commit |
| `RAW_LOGS/d16/recheck-20260924/verify_attestation_main_v22.json` | no main `d301aba`: `QUALIFICATION_ATTESTATION.json` `4896575f…` (v2.2, supersedes `f7923a88…` ← `c95145a7…`) passa schema, C7.1 (1)…(8) e C0.2 |
