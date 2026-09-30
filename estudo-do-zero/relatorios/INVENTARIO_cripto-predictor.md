# Inventário — cripto-predictor



Raiz: `C:\CRIPTO\pesquisa-20260909`. HEAD `88158f25ab067ed34a845a52f3816e215addf486`, branch `main`. Data UTC `2026-09-30T14:38:44.054796+00:00`; fuso usuário America/Sao_Paulo. Identidade e consultas remotas em `evidencias/cripto-predictor/baseline.json` e `remote-refs.txt`. Estado remoto: confirmado-remotamente; remoto main `74113effcec7c0cf8deb8a8a46d413b6942368ce` difere do HEAD local. Nenhum pull/fetch nos originais.



Versão fonte `1.1.1rc4`; Python `>=3.13,<3.15`. A instalação efetiva e serviço ativo não foram sondados. Releases/artefatos: consultar investigação central em release-identity.json, mantendo escopo por tag/SHA.



Árvore preexistente:

```

(limpa no baseline)

```



## Espaço e método



3313 caminhos rastreados (git ls-files). Distribuição por raiz:



| Raiz | Caminhos |

|---|---:|

| `.ci` | 3 |

| `.dockerignore` | 1 |

| `.env.example` | 1 |

| `.gitattributes` | 1 |

| `.github` | 3 |

| `.gitignore` | 1 |

| `.pre-commit-config.yaml` | 1 |

| `ARCHITECTURE_IMPLEMENTATION.md` | 1 |

| `BASELINE_REPORT.md` | 1 |

| `CONTINUAR_AQUI.md` | 1 |

| `CR_FREEZE_INDEX.md` | 1 |

| `CR_RESEARCH_FREEZE.md` | 1 |

| `Dockerfile` | 1 |

| `GarimpoInvestimentos` | 198 |

| `HANDOFF-2026-07-02.md` | 1 |

| `HANDOFF-2026-08-14.md` | 1 |

| `HANDOFF.md` | 1 |

| `HANDOFF_HISTORICO_ATE_20260917.md` | 1 |

| `PUBLICATION_STATUS_20260912.md` | 1 |

| `README.md` | 1 |

| `charters` | 5 |

| `compose.yaml` | 1 |

| `coverage-runtime.ini` | 1 |

| `cripto.cmd` | 1 |

| `docs` | 2807 |

| `global-coverage.txt` | 1 |

| `observation_plans` | 4 |

| `observation_reports` | 2 |

| `packages` | 12 |

| `pyproject.toml` | 1 |

| `pyrightconfig.json` | 1 |

| `requirements.txt` | 1 |

| `run_garimpo_fase1.bat` | 1 |

| `run_sinal_diario.bat` | 1 |

| `scripts` | 76 |

| `tests` | 170 |

| `typings` | 6 |

| `uv.lock` | 1 |



1743 arquivos de código/config/CI/locks/contratos lidos mecanicamente; classificação primária 450 arquivos/67258 linhas. 1366 definições Python de funções test_* identificadas, não casos coletados nem aprovação. Arquivos .NET não entram nesta contagem de funções Python. Índice AST em code-index.json. Documentos históricos/terceiros sob docs foram varridos mecanicamente e não certificados como código próprio atual.



Leitura estrutural integral bytes + AST não é revisão semântica integral. Caminhos centrais aprofundados são discriminados em coverage.json, com pendências explícitas. Arquivos não rastreados relevantes em Brasileirão foram incluídos separadamente e hashes estão em untracked-hashes.json. Bancos originais não abertos, credenciais privadas não lidas, modelos não treinados, APIs externas não consultadas por estes subestudos.



## Classificação



- Pacotes executáveis, scripts e testes: itens abaixo; não tratar testes como runtime.

- `docs/`, relatórios e evidências datadas: declarações/arquivos históricos; catálogo completo tracked-files.txt, aprofundamento só fontes que sustentam conflito.

- `data/`, modelos serializados e bases: inventário de caminhos, sem conteúdo privado ou afirmação de funcionamento atual.

- Workflows e Docker/Compose: configuração executável declarada, sem levantar serviços.

- `.venv`, caches ignorados e instalação principal: fora do catálogo rastreado e não sondados.



## Índice de código/configuração analisado



| Caminho | Linhas | Tipo |

|---|---:|---|

| `.ci/integration-audit/e2e_crypto.py` | 244 | fonte/teste/config; ver coverage.json |

| `.ci/integration-audit/validate.py` | 391 | fonte/teste/config; ver coverage.json |

| `.github/workflows/ci.yml` | 112 | fonte/teste/config; ver coverage.json |

| `.github/workflows/integration-audit.yml` | 39 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/__init__.py` | 18 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/analyzers/__init__.py` | 0 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/analyzers/ai_insights.py` | 370 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/analyzers/backtest.py` | 973 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/analyzers/equivalence.py` | 146 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/analyzers/factor_dsl.py` | 310 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/analyzers/gate_power.py` | 184 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/analyzers/ground_truth_harness.py` | 295 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/analyzers/hypothesis_loop.py` | 319 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/analyzers/hypothesis_loop_runner.py` | 255 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/analyzers/indicators.py` | 127 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/analyzers/judge_calibration.py` | 160 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/analyzers/opportunity_detector.py` | 309 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/analyzers/pbo.py` | 172 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/analyzers/prefilter.py` | 50 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/analyzers/score_engine.py` | 80 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/analyzers/trials.py` | 170 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/arguments.py` | 66 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/cli.py` | 91 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/collectors/__init__.py` | 0 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/collectors/coingecko_api.py` | 60 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/collectors/discovery.py` | 184 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/collectors/news.py` | 298 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/collectors/serpapi_news.py` | 34 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/config.py` | 164 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/contracts.py` | 105 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/core/__init__.py` | 0 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/core/api_guard.py` | 90 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/core/cache.py` | 108 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/core/collection_policy.py` | 33 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/core/history.py` | 132 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/core/logger.py` | 63 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/core/paths.py` | 28 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/dpl/__init__.py` | 55 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/dpl/aggregation.py` | 9 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/dpl/alignment.py` | 105 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/dpl/business_days.py` | 42 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/dpl/circuit_breaker.py` | 17 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/dpl/contracts.py` | 24 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/dpl/derivatives.py` | 127 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/dpl/entity_mapper.py` | 119 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/dpl/events.py` | 98 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/dpl/facade.py` | 99 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/dpl/feature_engineering.py` | 114 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/dpl/feature_store.py` | 849 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/dpl/hash_chain.py` | 194 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/dpl/ingest.py` | 243 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/dpl/macro_calendar.py` | 124 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/dpl/migrations/_0005_fix_raw_signals.py` | 33 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/dpl/migrations/_0006_predictions.py` | 28 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/dpl/migrations/_0007_feature_version.py` | 30 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/dpl/migrations/_0008_predictions_degraded.py` | 17 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/dpl/migrations/_0009_predictions_llm_fallback.py` | 18 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/dpl/migrations/_0010_predictions_news_provenance.py` | 8 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/dpl/migrations/_0011_predictions_collection_policy.py` | 4 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/dpl/migrations/_0012_provenance_content_hash.py` | 17 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/dpl/migrations/_0013_enriched_signals.py` | 16 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/dpl/migrations/_0014_source_quality_scorecards.py` | 16 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/dpl/migrations/_0015_observation_scorecards.py` | 19 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/dpl/migrations/_0016_predictions_append_only.py` | 96 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/dpl/migrations/_0017_archive_hash_chain.py` | 11 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/dpl/migrations/_0018_archive_immutable.py` | 29 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/dpl/migrations/_0019_input_snapshots.py` | 50 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/dpl/migrations/__init__.py` | 43 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/dpl/providers/__init__.py` | 1 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/dpl/providers/_validation.py` | 28 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/dpl/providers/bcb.py` | 106 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/dpl/providers/binance.py` | 9 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/dpl/providers/ccxt_base.py` | 139 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/dpl/providers/coingecko.py` | 128 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/dpl/providers/cotahist.py` | 162 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/dpl/providers/dxy.py` | 99 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/dpl/providers/fear_greed.py` | 73 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/dpl/providers/football_stubs.py` | 51 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/dpl/providers/kraken.py` | 13 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/dpl/providers/martj42.py` | 68 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/dpl/router.py` | 9 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/dpl/signals.py` | 7 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/dpl/snapshots.py` | 124 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/dpl/stocks.py` | 80 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/durable_io.py` | 99 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/external_intelligence/__init__.py` | 17 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/external_intelligence/__main__.py` | 144 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/external_intelligence/audit.py` | 115 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/external_intelligence/collection.py` | 50 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/external_intelligence/conditional.py` | 56 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/external_intelligence/context.py` | 63 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/external_intelligence/contracts.py` | 372 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/external_intelligence/features.py` | 60 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/external_intelligence/ledger.py` | 36 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/external_intelligence/providers/__init__.py` | 7 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/external_intelligence/providers/coinmetrics.py` | 138 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/external_intelligence/providers/common.py` | 22 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/external_intelligence/providers/nansen.py` | 123 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/external_intelligence/providers/santiment.py` | 132 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/external_intelligence/shadow.py` | 28 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/external_intelligence/store.py` | 471 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/feature_store_health.py` | 62 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/governance.py` | 321 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/health_io.py` | 25 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/history_cli.py` | 28 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/ingest_cli.py` | 23 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/ingestion.py` | 107 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/jobs.py` | 234 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/local_runtime.py` | 169 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/main.py` | 347 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/migrate_history.py` | 24 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/observation_collect.py` | 84 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/observation_quality.py` | 272 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/observation_reporting.py` | 195 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/observation_resilience.py` | 121 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/observation_watchdog.py` | 114 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/operational/__init__.py` | 1 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/operational/attest_harness.py` | 242 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/operational/feature_store_backup.py` | 227 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/opportunity_monitor.py` | 247 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/output/__init__.py` | 0 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/output/reporter.py` | 141 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/persistence.py` | 19 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/phase1.py` | 408 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/phase1_watchdog.py` | 162 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/pipeline_results.py` | 38 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/plugin.py` | 63 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/profit_recovery_v1.py` | 1582 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/profit_research.py` | 357 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/providers/__init__.py` | 3 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/providers/contracts.py` | 31 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/quality_scorecard.py` | 129 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/quality_snapshot.py` | 693 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/renewal_research.py` | 252 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/research/__init__.py` | 1 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/research/__main__.py` | 203 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/research/factors.py` | 103 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/research/registry.py` | 112 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/research/simulation.py` | 204 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/research/universe.py` | 98 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/research/validation.py` | 53 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/research_admission.py` | 484 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/research_execution.py` | 527 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/research_recovery.py` | 145 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/research_results.py` | 236 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/research_worker.py` | 211 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/runtime_mode.py` | 19 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/security/__init__.py` | 3 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/security/redaction.py` | 75 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/services/__init__.py` | 1 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/services/backtest.py` | 3 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/services/features.py` | 3 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/services/inference.py` | 8 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/services/ingestion.py` | 3 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/services/reporting.py` | 3 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/trading/__init__.py` | 7 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/trading/binance_spot_collector.py` | 413 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/trading/contracts.py` | 367 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/trading/cost_policy.py` | 69 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/trading/costs.py` | 90 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/trading/execution.py` | 287 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/trading/microstructure.py` | 350 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/trading/microstructure_quality.py` | 153 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/trading/portfolio.py` | 227 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/trading/report.py` | 74 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/trading/signal_adapter.py` | 148 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/trading/store.py` | 724 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/v3/__init__.py` | 4 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/v3/backtest_v3.py` | 1720 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/v3/circuit_breaker.py` | 9 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/v3/collectors/__init__.py` | 0 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/v3/collectors/binance_vision.py` | 255 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/v3/collectors/funding_collector.py` | 220 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/v3/collectors/oi_collector.py` | 233 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/v3/collectors/record_io.py` | 80 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/v3/collectors/spot_collector.py` | 198 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/v3/costs.py` | 84 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/v3/crowding_features.py` | 60 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/v3/daily.py` | 36 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/v3/economic_gate.py` | 130 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/v3/feature_builder.py` | 365 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/v3/macro_features.py` | 217 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/v3/paper_report.py` | 236 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/v3/paper_trader.py` | 266 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/v3/pipeline.py` | 464 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/v3/regime_engine.py` | 578 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/v3/signal_engine.py` | 411 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/v3/timeindex.py` | 71 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/v3/vision_ingest.py` | 110 | fonte/teste/config; ver coverage.json |

| `GarimpoInvestimentos/watchdog.py` | 282 | fonte/teste/config; ver coverage.json |

| `compose.yaml` | 16 | fonte/teste/config; ver coverage.json |

| `cripto.cmd` | 9 | fonte/teste/config; ver coverage.json |

| `packages/research-export/pyproject.toml` | 18 | fonte/teste/config; ver coverage.json |

| `packages/research-export/src/crypto_research_export/__init__.py` | 205 | fonte/teste/config; ver coverage.json |

| `packages/research-export/src/crypto_research_export/bundle.py` | 174 | fonte/teste/config; ver coverage.json |

| `packages/research-export/src/crypto_research_export/external.py` | 94 | fonte/teste/config; ver coverage.json |

| `packages/research-export/tests/conftest.py` | 23 | fonte/teste/config; ver coverage.json |

| `packages/research-export/tests/test_bundle.py` | 162 | fonte/teste/config; ver coverage.json |

| `packages/research-export/tests/test_export.py` | 99 | fonte/teste/config; ver coverage.json |

| `packages/research-export/tests/test_external.py` | 98 | fonte/teste/config; ver coverage.json |

| `packages/research-export/tests/test_publication.py` | 26 | fonte/teste/config; ver coverage.json |

| `pyproject.toml` | 73 | fonte/teste/config; ver coverage.json |

| `run_garimpo_fase1.bat` | 67 | fonte/teste/config; ver coverage.json |

| `run_sinal_diario.bat` | 61 | fonte/teste/config; ver coverage.json |

| `scripts/__init__.py` | 1 | fonte/teste/config; ver coverage.json |

| `scripts/attest_harness.py` | 15 | fonte/teste/config; ver coverage.json |

| `scripts/audit_absolute_research.py` | 320 | fonte/teste/config; ver coverage.json |

| `scripts/audit_altcoin_analogs.py` | 176 | fonte/teste/config; ver coverage.json |

| `scripts/audit_altcoin_retro.py` | 191 | fonte/teste/config; ver coverage.json |

| `scripts/audit_basis_sources.py` | 173 | fonte/teste/config; ver coverage.json |

| `scripts/audit_btc_basis.py` | 231 | fonte/teste/config; ver coverage.json |

| `scripts/audit_immediate_decimal.py` | 356 | fonte/teste/config; ver coverage.json |

| `scripts/audit_market_calendar.py` | 100 | fonte/teste/config; ver coverage.json |

| `scripts/backtest_absolute_carry.py` | 472 | fonte/teste/config; ver coverage.json |

| `scripts/backtest_absolute_spot.py` | 178 | fonte/teste/config; ver coverage.json |

| `scripts/backtest_altcoin_payoff.py` | 398 | fonte/teste/config; ver coverage.json |

| `scripts/backtest_btc_basis.py` | 436 | fonte/teste/config; ver coverage.json |

| `scripts/basis_data.py` | 411 | fonte/teste/config; ver coverage.json |

| `scripts/carry_forward_math.py` | 197 | fonte/teste/config; ver coverage.json |

| `scripts/carry_forward_registration.py` | 154 | fonte/teste/config; ver coverage.json |

| `scripts/carry_public.py` | 246 | fonte/teste/config; ver coverage.json |

| `scripts/check_altcoin_forward_design.py` | 118 | fonte/teste/config; ver coverage.json |

| `scripts/check_predictor_core_imports.py` | 11 | fonte/teste/config; ver coverage.json |

| `scripts/check_reopen_dossier.py` | 103 | fonte/teste/config; ver coverage.json |

| `scripts/ci_check.py` | 121 | fonte/teste/config; ver coverage.json |

| `scripts/collect_absolute_carry.py` | 199 | fonte/teste/config; ver coverage.json |

| `scripts/collect_altcoin_analogs.py` | 286 | fonte/teste/config; ver coverage.json |

| `scripts/collect_altcoin_retro.py` | 114 | fonte/teste/config; ver coverage.json |

| `scripts/compare_absolute_profit.py` | 156 | fonte/teste/config; ver coverage.json |

| `scripts/diagnose_ar2_renewals.py` | 126 | fonte/teste/config; ver coverage.json |

| `scripts/diagnose_btc_execution.py` | 219 | fonte/teste/config; ver coverage.json |

| `scripts/diagnose_h6_mechanism.py` | 138 | fonte/teste/config; ver coverage.json |

| `scripts/feature_store_backup.py` | 10 | fonte/teste/config; ver coverage.json |

| `scripts/fix_task_logon.ps1` | 35 | fonte/teste/config; ver coverage.json |

| `scripts/fix_task_power.ps1` | 48 | fonte/teste/config; ver coverage.json |

| `scripts/fix_task_power_watchdog.ps1` | 44 | fonte/teste/config; ver coverage.json |

| `scripts/fix_task_watchdog_trigger.ps1` | 26 | fonte/teste/config; ver coverage.json |

| `scripts/forense/check_all_tables.py` | 13 | fonte/teste/config; ver coverage.json |

| `scripts/forense/check_backup.py` | 6 | fonte/teste/config; ver coverage.json |

| `scripts/forense/check_db.py` | 3 | fonte/teste/config; ver coverage.json |

| `scripts/forense/check_db2.py` | 9 | fonte/teste/config; ver coverage.json |

| `scripts/forense/check_failed_runs.py` | 18 | fonte/teste/config; ver coverage.json |

| `scripts/freeze_h6_definition.py` | 170 | fonte/teste/config; ver coverage.json |

| `scripts/garimpo_fase1.py` | 10 | fonte/teste/config; ver coverage.json |

| `scripts/immediate_public.py` | 258 | fonte/teste/config; ver coverage.json |

| `scripts/integration_audit_receipt.py` | 108 | fonte/teste/config; ver coverage.json |

| `scripts/migrate_trials_schema_preview.py` | 115 | fonte/teste/config; ver coverage.json |

| `scripts/observe_altcoin_forward.py` | 840 | fonte/teste/config; ver coverage.json |

| `scripts/observe_carry_forward.py` | 317 | fonte/teste/config; ver coverage.json |

| `scripts/paired_llm.py` | 514 | fonte/teste/config; ver coverage.json |

| `scripts/paired_llm_source.py` | 274 | fonte/teste/config; ver coverage.json |

| `scripts/plan_absolute_profit.py` | 44 | fonte/teste/config; ver coverage.json |

| `scripts/plan_btc_hedge.py` | 129 | fonte/teste/config; ver coverage.json |

| `scripts/plan_btc_hedge_v2.py` | 132 | fonte/teste/config; ver coverage.json |

| `scripts/plan_btc_hedge_v3.py` | 150 | fonte/teste/config; ver coverage.json |

| `scripts/prepare_altcoin_payoff.py` | 389 | fonte/teste/config; ver coverage.json |

| `scripts/psr_nonoverlap.py` | 84 | fonte/teste/config; ver coverage.json |

| `scripts/recover_aave_history.py` | 359 | fonte/teste/config; ver coverage.json |

| `scripts/register_task_attest_renew.ps1` | 90 | fonte/teste/config; ver coverage.json |

| `scripts/register_task_backup.ps1` | 92 | fonte/teste/config; ver coverage.json |

| `scripts/reproduce_absolute_research.py` | 108 | fonte/teste/config; ver coverage.json |

| `scripts/reproduce_btc_basis.py` | 50 | fonte/teste/config; ver coverage.json |

| `scripts/research_altcoin_analogs.py` | 532 | fonte/teste/config; ver coverage.json |

| `scripts/research_io.py` | 125 | fonte/teste/config; ver coverage.json |

| `scripts/research_migration.py` | 337 | fonte/teste/config; ver coverage.json |

| `scripts/review_carry_absolute_profit.py` | 169 | fonte/teste/config; ver coverage.json |

| `scripts/run_absolute_research.py` | 75 | fonte/teste/config; ver coverage.json |

| `scripts/run_btc_basis.py` | 80 | fonte/teste/config; ver coverage.json |

| `scripts/run_daily.ps1` | 33 | fonte/teste/config; ver coverage.json |

| `scripts/run_daily_v3.ps1` | 8 | fonte/teste/config; ver coverage.json |

| `scripts/run_daily_v3_payload.ps1` | 7 | fonte/teste/config; ver coverage.json |

| `scripts/run_immediate_audit.py` | 294 | fonte/teste/config; ver coverage.json |

| `scripts/run_observation_resilience.py` | 3 | fonte/teste/config; ver coverage.json |

| `scripts/safe_pull.ps1` | 53 | fonte/teste/config; ver coverage.json |

| `scripts/scan_secrets.py` | 103 | fonte/teste/config; ver coverage.json |

| `scripts/simulate_prefilter.py` | 107 | fonte/teste/config; ver coverage.json |

| `scripts/verify_installed_wheels.py` | 72 | fonte/teste/config; ver coverage.json |

| `scripts/verify_research_runtime.py` | 80 | fonte/teste/config; ver coverage.json |

| `scripts/watchdog_coleta.py` | 7 | fonte/teste/config; ver coverage.json |

| `tests/conftest.py` | 81 | fonte/teste/config; ver coverage.json |

| `tests/test_aave_economic_evidence.py` | 81 | fonte/teste/config; ver coverage.json |

| `tests/test_absolute_research.py` | 199 | fonte/teste/config; ver coverage.json |

| `tests/test_adversarial_hardening.py` | 66 | fonte/teste/config; ver coverage.json |

| `tests/test_ai_insights_ensemble.py` | 148 | fonte/teste/config; ver coverage.json |

| `tests/test_ai_insights_retry.py` | 186 | fonte/teste/config; ver coverage.json |

| `tests/test_altcoin_analogs.py` | 132 | fonte/teste/config; ver coverage.json |

| `tests/test_altcoin_forward.py` | 320 | fonte/teste/config; ver coverage.json |

| `tests/test_altcoin_observer_review.py` | 130 | fonte/teste/config; ver coverage.json |

| `tests/test_altcoin_payoff.py` | 102 | fonte/teste/config; ver coverage.json |

| `tests/test_altcoin_retro.py` | 186 | fonte/teste/config; ver coverage.json |

| `tests/test_api_guard.py` | 101 | fonte/teste/config; ver coverage.json |

| `tests/test_architecture_boundaries.py` | 27 | fonte/teste/config; ver coverage.json |

| `tests/test_architecture_contracts.py` | 30 | fonte/teste/config; ver coverage.json |

| `tests/test_audit_economic_accounting.py` | 63 | fonte/teste/config; ver coverage.json |

| `tests/test_audit_expansion_regressions.py` | 316 | fonte/teste/config; ver coverage.json |

| `tests/test_audit_final_boundaries.py` | 129 | fonte/teste/config; ver coverage.json |

| `tests/test_audit_model_integrity.py` | 96 | fonte/teste/config; ver coverage.json |

| `tests/test_audit_persistence_safety.py` | 169 | fonte/teste/config; ver coverage.json |

| `tests/test_audit_public_anchor.py` | 56 | fonte/teste/config; ver coverage.json |

| `tests/test_audit_release_guards.py` | 115 | fonte/teste/config; ver coverage.json |

| `tests/test_audit_source_integrity.py` | 113 | fonte/teste/config; ver coverage.json |

| `tests/test_backtest_bootstrap.py` | 40 | fonte/teste/config; ver coverage.json |

| `tests/test_binance_spot_collector.py` | 261 | fonte/teste/config; ver coverage.json |

| `tests/test_btc_basis.py` | 248 | fonte/teste/config; ver coverage.json |

| `tests/test_btc_execution_plan.py` | 35 | fonte/teste/config; ver coverage.json |

| `tests/test_btc_execution_validation.py` | 75 | fonte/teste/config; ver coverage.json |

| `tests/test_cache.py` | 145 | fonte/teste/config; ver coverage.json |

| `tests/test_carry_forward.py` | 258 | fonte/teste/config; ver coverage.json |

| `tests/test_carry_public.py` | 96 | fonte/teste/config; ver coverage.json |

| `tests/test_check_reopen_dossier.py` | 64 | fonte/teste/config; ver coverage.json |

| `tests/test_config_news_providers.py` | 45 | fonte/teste/config; ver coverage.json |

| `tests/test_config_secrets_resolution.py` | 74 | fonte/teste/config; ver coverage.json |

| `tests/test_continuity_recovery.py` | 118 | fonte/teste/config; ver coverage.json |

| `tests/test_core_integrity.py` | 57 | fonte/teste/config; ver coverage.json |

| `tests/test_dependency_execution_manifest.py` | 15 | fonte/teste/config; ver coverage.json |

| `tests/test_diagnose_h6_mechanism_pit.py` | 87 | fonte/teste/config; ver coverage.json |

| `tests/test_discovery.py` | 101 | fonte/teste/config; ver coverage.json |

| `tests/test_distribution_security.py` | 60 | fonte/teste/config; ver coverage.json |

| `tests/test_divergence.py` | 53 | fonte/teste/config; ver coverage.json |

| `tests/test_dpl.py` | 176 | fonte/teste/config; ver coverage.json |

| `tests/test_dpl_aggregation.py` | 167 | fonte/teste/config; ver coverage.json |

| `tests/test_dpl_business_days.py` | 65 | fonte/teste/config; ver coverage.json |

| `tests/test_dpl_dxy.py` | 163 | fonte/teste/config; ver coverage.json |

| `tests/test_dpl_feature_store.py` | 161 | fonte/teste/config; ver coverage.json |

| `tests/test_dpl_features.py` | 93 | fonte/teste/config; ver coverage.json |

| `tests/test_dpl_football.py` | 113 | fonte/teste/config; ver coverage.json |

| `tests/test_dpl_macro_calendar.py` | 145 | fonte/teste/config; ver coverage.json |

| `tests/test_dpl_migrations.py` | 117 | fonte/teste/config; ver coverage.json |

| `tests/test_dpl_stocks.py` | 232 | fonte/teste/config; ver coverage.json |

| `tests/test_dsr_provenance.py` | 44 | fonte/teste/config; ver coverage.json |

| `tests/test_ecosystem_plugin_state.py` | 12 | fonte/teste/config; ver coverage.json |

| `tests/test_equivalence.py` | 36 | fonte/teste/config; ver coverage.json |

| `tests/test_experiment_registry.py` | 662 | fonte/teste/config; ver coverage.json |

| `tests/test_external_intelligence.py` | 271 | fonte/teste/config; ver coverage.json |

| `tests/test_factor_dsl.py` | 168 | fonte/teste/config; ver coverage.json |

| `tests/test_failure_replay.py` | 188 | fonte/teste/config; ver coverage.json |

| `tests/test_feature_store_backup.py` | 96 | fonte/teste/config; ver coverage.json |

| `tests/test_feature_store_backup_agendado.py` | 56 | fonte/teste/config; ver coverage.json |

| `tests/test_feature_store_guards.py` | 111 | fonte/teste/config; ver coverage.json |

| `tests/test_feature_store_health.py` | 68 | fonte/teste/config; ver coverage.json |

| `tests/test_football_stubs.py` | 89 | fonte/teste/config; ver coverage.json |

| `tests/test_freeze_h6_definition.py` | 68 | fonte/teste/config; ver coverage.json |

| `tests/test_gate_power.py` | 97 | fonte/teste/config; ver coverage.json |

| `tests/test_golden_science.py` | 38 | fonte/teste/config; ver coverage.json |

| `tests/test_governance_charter.py` | 35 | fonte/teste/config; ver coverage.json |

| `tests/test_governance_wheel_assets.py` | 15 | fonte/teste/config; ver coverage.json |

| `tests/test_ground_truth_harness.py` | 146 | fonte/teste/config; ver coverage.json |

| `tests/test_h6_power_context.py` | 82 | fonte/teste/config; ver coverage.json |

| `tests/test_h6_spearman_verdict_eligibility.py` | 104 | fonte/teste/config; ver coverage.json |

| `tests/test_hash_chain.py` | 159 | fonte/teste/config; ver coverage.json |

| `tests/test_hypothesis_loop.py` | 247 | fonte/teste/config; ver coverage.json |

| `tests/test_hypothesis_loop_runner.py` | 162 | fonte/teste/config; ver coverage.json |

| `tests/test_immediate_audit.py` | 123 | fonte/teste/config; ver coverage.json |

| `tests/test_integration_audit_receipt.py` | 107 | fonte/teste/config; ver coverage.json |

| `tests/test_jobs_operations.py` | 284 | fonte/teste/config; ver coverage.json |

| `tests/test_judge.py` | 106 | fonte/teste/config; ver coverage.json |

| `tests/test_judge_calibration.py` | 80 | fonte/teste/config; ver coverage.json |

| `tests/test_kelly_sweep_cli.py` | 79 | fonte/teste/config; ver coverage.json |

| `tests/test_local_runtime.py` | 153 | fonte/teste/config; ver coverage.json |

| `tests/test_manual_dependencies.py` | 152 | fonte/teste/config; ver coverage.json |

| `tests/test_measurement_quality.py` | 188 | fonte/teste/config; ver coverage.json |

| `tests/test_merge_fonte.py` | 106 | fonte/teste/config; ver coverage.json |

| `tests/test_mode_composition.py` | 70 | fonte/teste/config; ver coverage.json |

| `tests/test_news_providers.py` | 287 | fonte/teste/config; ver coverage.json |

| `tests/test_observation_governance.py` | 67 | fonte/teste/config; ver coverage.json |

| `tests/test_observation_quality.py` | 129 | fonte/teste/config; ver coverage.json |

| `tests/test_observation_reporting.py` | 35 | fonte/teste/config; ver coverage.json |

| `tests/test_observation_watchdog.py` | 46 | fonte/teste/config; ver coverage.json |

| `tests/test_opportunity_detector.py` | 133 | fonte/teste/config; ver coverage.json |

| `tests/test_opportunity_monitor.py` | 137 | fonte/teste/config; ver coverage.json |

| `tests/test_ops_hardening.py` | 362 | fonte/teste/config; ver coverage.json |

| `tests/test_order_book_reconstruction.py` | 77 | fonte/teste/config; ver coverage.json |

| `tests/test_output_dir_bootstrap.py` | 42 | fonte/teste/config; ver coverage.json |

| `tests/test_paired_llm.py` | 336 | fonte/teste/config; ver coverage.json |

| `tests/test_paper_idempotency.py` | 44 | fonte/teste/config; ver coverage.json |

| `tests/test_pbo.py` | 108 | fonte/teste/config; ver coverage.json |

| `tests/test_permutation_placebo_control.py` | 100 | fonte/teste/config; ver coverage.json |

| `tests/test_phase1_watchdog.py` | 126 | fonte/teste/config; ver coverage.json |

| `tests/test_plugin_persistence.py` | 27 | fonte/teste/config; ver coverage.json |

| `tests/test_positive_control.py` | 93 | fonte/teste/config; ver coverage.json |

| `tests/test_predictions_append_only.py` | 205 | fonte/teste/config; ver coverage.json |

| `tests/test_prefilter.py` | 35 | fonte/teste/config; ver coverage.json |

| `tests/test_profit_recovery_v1.py` | 365 | fonte/teste/config; ver coverage.json |

| `tests/test_profit_research.py` | 369 | fonte/teste/config; ver coverage.json |

| `tests/test_provider_runtime_config.py` | 84 | fonte/teste/config; ver coverage.json |

| `tests/test_provider_validation.py` | 34 | fonte/teste/config; ver coverage.json |

| `tests/test_quality_snapshot.py` | 645 | fonte/teste/config; ver coverage.json |

| `tests/test_readme_reflete_charter.py` | 77 | fonte/teste/config; ver coverage.json |

| `tests/test_recover_aave_history.py` | 106 | fonte/teste/config; ver coverage.json |

| `tests/test_registry_e_scripts_encoding.py` | 107 | fonte/teste/config; ver coverage.json |

| `tests/test_renewal_research.py` | 223 | fonte/teste/config; ver coverage.json |

| `tests/test_repo_hygiene.py` | 95 | fonte/teste/config; ver coverage.json |

| `tests/test_report_harness.py` | 68 | fonte/teste/config; ver coverage.json |

| `tests/test_repository_research_freezes.py` | 24 | fonte/teste/config; ver coverage.json |

| `tests/test_research_admission.py` | 258 | fonte/teste/config; ver coverage.json |

| `tests/test_research_capabilities.py` | 330 | fonte/teste/config; ver coverage.json |

| `tests/test_research_corrections.py` | 163 | fonte/teste/config; ver coverage.json |

| `tests/test_research_execution.py` | 292 | fonte/teste/config; ver coverage.json |

| `tests/test_research_migration.py` | 85 | fonte/teste/config; ver coverage.json |

| `tests/test_research_recovery.py` | 67 | fonte/teste/config; ver coverage.json |

| `tests/test_research_results.py` | 144 | fonte/teste/config; ver coverage.json |

| `tests/test_review_data_contracts.py` | 122 | fonte/teste/config; ver coverage.json |

| `tests/test_review_failure_boundaries.py` | 156 | fonte/teste/config; ver coverage.json |

| `tests/test_review_input_snapshots.py` | 150 | fonte/teste/config; ver coverage.json |

| `tests/test_rolling_flip.py` | 71 | fonte/teste/config; ver coverage.json |

| `tests/test_run_redoma.py` | 121 | fonte/teste/config; ver coverage.json |

| `tests/test_scientific_state_charter.py` | 106 | fonte/teste/config; ver coverage.json |

| `tests/test_secret_assignment_boundaries.py` | 19 | fonte/teste/config; ver coverage.json |

| `tests/test_secrets_telemetry.py` | 26 | fonte/teste/config; ver coverage.json |

| `tests/test_security_redaction.py` | 77 | fonte/teste/config; ver coverage.json |

| `tests/test_settings.py` | 41 | fonte/teste/config; ver coverage.json |

| `tests/test_shared_wheel_download_hashes.py` | 94 | fonte/teste/config; ver coverage.json |

| `tests/test_stats.py` | 62 | fonte/teste/config; ver coverage.json |

| `tests/test_store_history.py` | 220 | fonte/teste/config; ver coverage.json |

| `tests/test_strategy_draft_governance.py` | 17 | fonte/teste/config; ver coverage.json |

| `tests/test_test_environment_isolation.py` | 60 | fonte/teste/config; ver coverage.json |

| `tests/test_threshold_grid_registry.py` | 49 | fonte/teste/config; ver coverage.json |

| `tests/test_timeindex.py` | 40 | fonte/teste/config; ver coverage.json |

| `tests/test_trading_contracts.py` | 379 | fonte/teste/config; ver coverage.json |

| `tests/test_trading_costs.py` | 76 | fonte/teste/config; ver coverage.json |

| `tests/test_trading_execution.py` | 172 | fonte/teste/config; ver coverage.json |

| `tests/test_trading_microstructure.py` | 222 | fonte/teste/config; ver coverage.json |

| `tests/test_trading_portfolio.py` | 223 | fonte/teste/config; ver coverage.json |

| `tests/test_trading_recovery_lifecycle.py` | 76 | fonte/teste/config; ver coverage.json |

| `tests/test_trading_report_and_cost_policy.py` | 130 | fonte/teste/config; ver coverage.json |

| `tests/test_trading_signal_adapter.py` | 178 | fonte/teste/config; ver coverage.json |

| `tests/test_trading_store.py` | 105 | fonte/teste/config; ver coverage.json |

| `tests/test_trials.py` | 196 | fonte/teste/config; ver coverage.json |

| `tests/test_v3_backtest_barriers.py` | 95 | fonte/teste/config; ver coverage.json |

| `tests/test_v3_circuit_breaker.py` | 72 | fonte/teste/config; ver coverage.json |

| `tests/test_v3_costs.py` | 46 | fonte/teste/config; ver coverage.json |

| `tests/test_v3_crowding_features.py` | 92 | fonte/teste/config; ver coverage.json |

| `tests/test_v3_derivatives_dpl.py` | 63 | fonte/teste/config; ver coverage.json |

| `tests/test_v3_economic_gate.py` | 74 | fonte/teste/config; ver coverage.json |

| `tests/test_v3_feature_prefix_regression.py` | 80 | fonte/teste/config; ver coverage.json |

| `tests/test_v3_hmm_no_lookahead.py` | 123 | fonte/teste/config; ver coverage.json |

| `tests/test_v3_macro_dxy_integration.py` | 146 | fonte/teste/config; ver coverage.json |

| `tests/test_v3_macro_features.py` | 226 | fonte/teste/config; ver coverage.json |

| `tests/test_v3_paper_report.py` | 150 | fonte/teste/config; ver coverage.json |

| `tests/test_v3_paper_trader.py` | 109 | fonte/teste/config; ver coverage.json |

| `tests/test_v3_portfolio_equity.py` | 141 | fonte/teste/config; ver coverage.json |

| `tests/test_v3_production_paths.py` | 12 | fonte/teste/config; ver coverage.json |

| `tests/test_v3_regime_engine_extra_covariates.py` | 321 | fonte/teste/config; ver coverage.json |

| `tests/test_v3_regime_staleness.py` | 75 | fonte/teste/config; ver coverage.json |

| `tests/test_v3_signal_engine.py` | 164 | fonte/teste/config; ver coverage.json |

| `tests/test_v3_wfa_actual_slicing.py` | 120 | fonte/teste/config; ver coverage.json |

| `tests/test_v3_wfa_purge_contract.py` | 87 | fonte/teste/config; ver coverage.json |

| `tests/test_watchdog_coleta.py` | 100 | fonte/teste/config; ver coverage.json |

| `tests/test_watchdog_paths.py` | 162 | fonte/teste/config; ver coverage.json |

| `uv.lock` | 1856 | fonte/teste/config; ver coverage.json |



## Épocas remotas observadas

Os manifests do main remoto e os assets do Anexo foram verificados separadamente, por SHA/versão. Veja [confronto do Anexo](CONFRONTO_ANEXO_REMOTO.md). Essas identidades não ampliam automaticamente a cobertura semântica da raiz primária nem provam integração runtime.
