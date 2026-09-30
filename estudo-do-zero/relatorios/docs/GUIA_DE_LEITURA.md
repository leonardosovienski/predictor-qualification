# Guia de leitura

Comece por LINHA_DE_BASE.md e RELATORIO_GERAL.md; depois PRELIMINAR, INVENTARIO e COMO_FUNCIONA de um projeto. Cada path abaixo deve ser confirmado no source-index/source-catalog: alguns itens agrupam nomes para orientar módulos, não são comandos. A cobertura informa onde há aprofundamento pendente.

## cain

1. pyproject.toml e settings.py
2. runtime.py → orchestrator/routing.py → agents/
3. workspace.py e persistence/adapters/sqlite.py
4. research/service.py → bundles.py → objects.py
5. research/grounding.py → historian.py → analysis.py → workflows.py
6. api.py/research/api.py e web/app.js; mcp.py
7. llm/ e providers.py; evaluation/ e testes correspondentes

## cripto-predictor

1. pyproject.toml → uv.lock → plugin.py
2. GarimpoInvestimentos/config.py e governance.py
3. dpl/feature_store.py e ingestion.py
4. research_admission.py → research_execution.py → research_worker.py → research_results.py
5. core/economic_gate.py; trials.py e v3/pipeline.py
6. packages/research-export/; workflows CI e tests

## brasileirao-predictor

1. pyproject.toml → uv.lock → plugin.py
2. CLI e config apontados source-index
3. data/ e temporal/ bitemporal/prospective_shadow
4. backtest_event.py e event_models.py
5. economic_decision.py → recommendation.py/calibration_gate.py
6. tools/export_cain_* e testes; suplemento research_runtime da outra época

## stocks-predictor

1. pyproject.toml → uv.lock → main.py
2. db.py → ingest_cotahist.py / ingest_cvm.py
3. cvm_pit.py → factors.py / factor.py
4. backtest.py → simulation.py → profit_validation.py
5. rj_episodes.py → rj_judge.py; etf_hold.py; discovery/
6. external_intelligence.py → diagnostics.py → tools/verify_operational_evidence.py
7. tests por responsabilidade; CI e export_cain ferramentas

## core-predictor

1. pyproject.toml e __init__.py
2. contracts/scientific.py e data/contracts.py
3. measurement/replay.py → metrics.py → bootstrap.py
4. measurement/trials.py e contracts/trial_v2.py
5. data/router.py → circuit_breaker.py → source_quality.py
6. kernel/ persistência/net e testes leaf/contratos; tools/check_installed_wheel.py

## predictor-ops

1. pyproject.toml → src/predictor_ops/cli.py
2. runner.py e callbacks do runner
3. lock/heartbeat/mutation_guard e timeout
4. provenance.py e receipt schema
5. tests runner/recovery/concurrency; CI installedwheel; suplemento Windows4.2.2rc1

## ecosystem-predictor

1. pyproject.toml → src/ecosystem_predictor/contracts.py e registry.py
2. packages/research-snapshot contrato+validador
3. packages/research-bundle contrato+files
4. packages/research-protocol messages/auth
5. registries arquitetura/compat; compat/locks e CI
6. scripts/check_ecosystem_drift.py e tests; versões V2/transport do AnexoNV

## predictor-qualification

1. qualification/COMMON_QUALIFICATION_CORE.md como DD e regras
2. shared/scripts/collect_stack_baseline.py → cleanroom_baseline.py
3. crypto/scripts/attest.py → evidence_numbers.py
4. GATES/FINDINGS/schema e atestados de época
5. crypto/scripts/e2e_runtime.py → science_real.py → soak.py
6. workflows e RAW_LOGS somente correspondentes ao SHA/gate investigado

Na primeira passagem, ignore caches, wheels, ambientes e datasetsbrutos; catalogue relatóriosdatados/RAW_LOGS sem lê-los como verdade atual. Volte a eles somente para o gate ou conclusão em disputa. Não execute exemplos/doctor/verificadores no original: diversos inicializam bancos ou gravam recibos. Leia o preflight e a saída de ET-RUN antes usar os resultados.
