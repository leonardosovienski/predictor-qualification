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
