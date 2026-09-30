# Inventário — brasileirao-predictor



Raiz: `C:\BRASILEIRAO\brasileirao-predictor`. HEAD `f87806900d2aa3c5e267259a67f27ce56e18dc03`, branch `main`. Data UTC `2026-09-30T14:38:46.171938+00:00`; fuso usuário America/Sao_Paulo. Identidade e consultas remotas em `evidencias/brasileirao-predictor/baseline.json` e `remote-refs.txt`. Estado remoto: confirmado-remotamente; remoto main `1e0c6f0b31e7cdc514190f08d5d2ff9689bd905d` difere do HEAD local. Nenhum pull/fetch nos originais.



Versão fonte `0.2.0`; Python `>=3.13,<3.15`. A instalação efetiva e serviço ativo não foram sondados. Releases/artefatos: consultar investigação central em release-identity.json, mantendo escopo por tag/SHA.



Árvore preexistente:

```

M brasileirao_scripts/backtest_walkforward.py

 M brasileirao_scripts/evaluate_h14_prospective.py

 M brasileirao_scripts/evaluate_h15_prospective.py

 M tests/test_evaluate_h14_prospective.py

 M tests/test_evaluate_h15_prospective.py

 M tests/test_prospective_evaluation_guard.py

?? brasileirao_scripts/prospective_metrics.py

?? brasileirao_scripts/prospective_protocol_v2.py

?? docs/research/prospective_repair_v2_20260915.json

?? docs/research/prospective_repair_v2_20260915.md

?? tests/test_audit_hardening.py

?? tests/test_prospective_metrics.py

?? tests/test_prospective_protocol_compatibility.py

?? tests/test_prospective_protocol_v2.py

?? tests/test_walkforward_row_contract.py

```



## Espaço e método



2537 caminhos rastreados (git ls-files). Distribuição por raiz:



| Raiz | Caminhos |

|---|---:|

| `.ci` | 1 |

| `.dockerignore` | 1 |

| `.env.example` | 1 |

| `.gitattributes` | 1 |

| `.github` | 4 |

| `.gitignore` | 1 |

| `ARCHITECTURE_IMPLEMENTATION.md` | 1 |

| `Dockerfile.cli` | 1 |

| `Dockerfile.kernel` | 1 |

| `Dockerfile.worker` | 1 |

| `HANDOFF.md` | 1 |

| `PUBLICATION_STATUS_20260912.md` | 1 |

| `README.md` | 1 |

| `brasileirao_predictor` | 117 |

| `brasileirao_scripts` | 120 |

| `compose.yaml` | 1 |

| `config.yaml` | 1 |

| `constraints` | 1 |

| `contracts` | 13 |

| `data` | 6 |

| `docker` | 2 |

| `docs` | 1884 |

| `dotnet` | 38 |

| `global.json` | 1 |

| `jobs.market-research.example.json` | 1 |

| `poc_oddspapi.py` | 1 |

| `pyproject.toml` | 1 |

| `pytest.ini` | 1 |

| `reports` | 92 |

| `research` | 14 |

| `scheduler.prospective.example.json` | 1 |

| `schemas` | 1 |

| `scripts` | 2 |

| `tests` | 205 |

| `tools` | 17 |

| `uv.lock` | 1 |



1049 arquivos de código/config/CI/locks/contratos lidos mecanicamente; classificação primária 524 arquivos/73288 linhas. 1448 definições Python de funções test_* identificadas, não casos coletados nem aprovação. Arquivos .NET não entram nesta contagem de funções Python. Índice AST em code-index.json. Documentos históricos/terceiros sob docs foram varridos mecanicamente e não certificados como código próprio atual.



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

| `.github/workflows/cain-export.yml` | 44 | fonte/teste/config; ver coverage.json |

| `.github/workflows/ci.yml` | 188 | fonte/teste/config; ver coverage.json |

| `.github/workflows/publication-validation.yml` | 189 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/__init__.py` | 13 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/a1_phase0.py` | 163 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/a1_recommendation.py` | 107 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/backtest.py` | 594 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/backtest_event.py` | 363 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/backup_restore.py` | 204 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/bet_log.py` | 1024 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/bootstrap.py` | 195 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/check_coverage.py` | 117 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/collector_a1.py` | 537 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/cron_update_models.py` | 117 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/data/api_football_provider.py` | 179 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/data/bitemporal_store.py` | 140 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/data/bookmaker_odds.py` | 190 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/data/bookmaker_stability.py` | 158 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/data/collection_only_archive.py` | 176 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/data/historical_expansion.py` | 141 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/data/lineup_archive.py` | 29 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/data/lineup_envelopes.py` | 154 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/data/market_anchor.py` | 105 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/data/missingness_audit.py` | 82 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/data/odds_api_snapshot.py` | 208 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/data/pit_backfill.py` | 662 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/data/promotions.py` | 131 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/data/prospective_shadow.py` | 103 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/data/sportmonks_provider.py` | 155 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/data/the_odds_api_provider.py` | 242 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/data/xg_quality.py` | 31 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/db.py` | 646 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/diagnose_event_data.py` | 116 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/display.py` | 634 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/dixon_coles.py` | 242 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/dynamic_strength.py` | 60 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/ecosystem_plugin.py` | 44 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/elo_baseline.py` | 138 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/evaluator.py` | 169 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/event_models.py` | 275 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/feature_builder.py` | 129 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/formal_prediction.py` | 46 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/identity.py` | 107 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/ingest.py` | 115 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/ingest_fbref.py` | 166 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/ingest_sofascore.py` | 597 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/kernel_cli.py` | 44 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/kernel_daemon.py` | 548 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/kernel_message.py` | 60 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/kernel_redis_v2.py` | 284 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/market_pricer.py` | 154 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/math_utils.py` | 45 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/model.py` | 421 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/net.py` | 49 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/obs.py` | 42 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/operational_readiness.py` | 103 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/paths.py` | 25 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/predict.py` | 384 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/prediction_log.py` | 192 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/prediction_protocol.py` | 166 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/ratings.py` | 129 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/research/__init__.py` | 0 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/research/calibration_gate.py` | 53 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/research/contextual_ensemble.py` | 169 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/research/economic_decision.py` | 119 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/research/h9_shadow.py` | 153 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/research/market_0b_resolution.py` | 291 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/research/market_edge_ordering.py` | 292 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/research/market_residual.py` | 305 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/research/ou25_nested_replay.py` | 629 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/research/pit_features/__init__.py` | 17 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/research/pit_features/absences.py` | 17 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/research/pit_features/contextual.py` | 98 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/research/pit_features/contracts.py` | 102 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/research/pit_features/hierarchical_home_advantage.py` | 17 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/research/pit_features/isolated_xg.py` | 24 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/research/pit_features/lineup.py` | 18 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/research/price_strength/__init__.py` | 3 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/research/price_strength/__main__.py` | 111 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/research/price_strength/artifacts.py` | 212 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/research/price_strength/capture_decision.py` | 252 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/research/price_strength/closing_scenario.py` | 192 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/research/price_strength/demo.py` | 93 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/research/price_strength/dynamic_xg.py` | 389 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/research/price_strength/economic_search.py` | 555 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/research/price_strength/historical_admission.py` | 150 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/research/price_strength/live_capture_admission.py` | 155 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/research/price_strength/price_hurdle.py` | 227 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/research/price_strength/quotes.py` | 431 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/research/price_strength/study.py` | 355 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/research/price_strength_reliability.py` | 151 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/research/promoted_cold_start.py` | 270 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/research/prospective_validation/__init__.py` | 10 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/research/prospective_validation/contracts.py` | 72 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/research/prospective_validation/ledger.py` | 34 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/research/prospective_validation/metrics.py` | 125 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/research/residual_dataset.py` | 220 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/research/residual_features.py` | 87 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/research/residual_gate.py` | 141 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/research/residual_walkforward.py` | 221 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/research/rho_stability.py` | 94 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/research/score_metrics.py` | 83 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/research/season_2026_split.py` | 94 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/research/shadow_portfolio.py` | 148 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/research/sofascore_probe.py` | 168 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/research/structural_edge.py` | 193 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/research/survival_test.py` | 438 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/research/temporal_replay.py` | 34 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/research/test_combinations.py` | 185 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/research/verify_calibration.py` | 237 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/research/vorp_ridge.py` | 278 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/serving_evaluator.py` | 314 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/settings.py` | 51 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/settle.py` | 271 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/simulator.py` | 245 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/sofascore.py` | 174 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/status.py` | 104 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/temporal_policy.py` | 82 | fonte/teste/config; ver coverage.json |

| `brasileirao_predictor/xg_model.py` | 200 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/__init__.py` | 1 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/_attest_only.py` | 48 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/_prospective_evaluation_guard.py` | 128 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/a1_phase0.py` | 72 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/audit_missingness.py` | 21 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/auditoria.py` | 141 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/backfill_bookmaker_smokes.py` | 67 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/backfill_player_comp_stats_from_sofascore.py` | 152 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/backtest_close.py` | 100 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/backtest_walkforward.py` | 423 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/backup_h9_runtime.py` | 24 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/benchmark_predictor.py` | 924 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/bootstrap_calibration_window.py` | 110 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/bundle_h9_evidence.py` | 72 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/calib_empate.py` | 86 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/calib_ou.py` | 112 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/capture_sofascore_event.py` | 230 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/check_prediction_readiness.py` | 22 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/ci_check.py` | 286 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/collect_collection_only.py` | 28 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/collect_market_research.py` | 88 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/collect_odds_a1.py` | 236 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/collector_daily_metrics.py` | 55 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/compare_hypothesis_errors.py` | 158 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/confound.py` | 220 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/cosh_free.py` | 114 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/coverage_report.py` | 192 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/diag_zebra.py` | 94 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/elasticidade.py` | 65 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/emit_h9_shadow.py` | 324 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/eval_walkforward.py` | 148 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/evaluate_contextual_ensemble.py` | 29 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/evaluate_gate_a1.py` | 92 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/evaluate_h14_prospective.py` | 276 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/evaluate_h15_prospective.py` | 266 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/evaluate_market_residual.py` | 53 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/evaluate_promoted_cold_start.py` | 63 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/evaluate_rho_stability.py` | 25 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/evaluate_shadow_cohort.py` | 206 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/exp001_coverage_audit.py` | 130 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/exp001_data_pilot.py` | 130 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/exp_a_calib.py` | 60 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/exp_f_rho.py` | 116 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/experimentos_causa.py` | 137 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/export_version_losses.py` | 70 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/gen_teams_json.py` | 63 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/governanca.py` | 207 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/h10_fadiga_walkforward.py` | 284 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/h4_verdict_bootstrap.py` | 200 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/hotpath_smoke.py` | 151 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/import_ou25_historical_backfill.py` | 253 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/ingest_api_football_history.py` | 48 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/init_compose_data.py` | 42 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/install_closing_snapshot_task.ps1` | 41 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/install_collector_a1_task.ps1` | 36 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/install_windows_scheduler.ps1` | 109 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/inventario_dados.py` | 185 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/investigate_calibration_window.py` | 185 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/investigate_half_life.py` | 139 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/lineup_inbox.py` | 28 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/maher.py` | 192 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/maher_verif.py` | 161 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/monitor_h8_gate.py` | 58 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/monitor_shadow_cohort.py` | 66 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/odds_shop.py` | 438 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/operational_readiness.py` | 16 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/p1_cost_probe.py` | 259 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/permutation_test.py` | 240 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/persist_h14_prospective.py` | 247 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/persist_h15_prospective.py` | 260 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/playoff_clv.py` | 96 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/poc_fadiga.py` | 148 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/predict_first18_2026.py` | 69 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/predict_first18_ou_dc.py` | 97 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/predict_first18_teams.py` | 131 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/predict_walkforward_ev.py` | 169 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/prereg_serving_vs_climatologia.py` | 191 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/prever.py` | 217 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/prospective_readiness.py` | 62 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/prova_mecanismo.py` | 111 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/record_closing_snapshots.py` | 129 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/record_h9_closing_snapshots.py` | 91 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/record_odds_smoke.py` | 81 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/register_h9_prospective.py` | 47 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/register_retest_2023_2026.py` | 84 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/registrar_h5.py` | 70 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/renew_core3_harness.py` | 52 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/replay_round_2026_08_22.py` | 183 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/report_h9_execution_quality.py` | 103 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/report_h9_missed_windows.py` | 151 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/report_shadow_mode.py` | 333 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/research_01a_refit_cadence.py` | 386 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/research_dynamic_strength.py` | 100 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/research_market02_1x2.py` | 178 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/research_market_0b_resolution.py` | 94 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/research_market_edge_ordering.py` | 92 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/research_ou25_annual_2021_2026.py` | 184 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/research_ou25_certainty.py` | 61 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/research_ou25_factorial.py` | 58 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/research_ou25_market_anchor.py` | 47 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/research_ou25_nested_replay.py` | 175 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/research_residual_diagnostics.py` | 293 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/research_xg_ensemble.py` | 316 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/run_h4_sweep.py` | 247 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/run_passive_task.py` | 192 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/seed_test_fixtures.py` | 63 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/settle_h9_shadow.py` | 129 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/settle_live_prediction.py` | 168 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/shadow_dashboard.py` | 131 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/sim_2025_2026.py` | 212 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/sim_melhorias.py` | 362 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/smoke_odds_source.py` | 68 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/sombra.py` | 549 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/sombra_diaria.py` | 156 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/sombra_diaria_payload.py` | 129 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/sync_matches_from_sofascore.py` | 129 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/temporal_replay_manifest.py` | 27 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/trial_draw_calibration_a10.py` | 129 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/update_h9_fixtures.py` | 32 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/validate_env_example.py` | 18 | fonte/teste/config; ver coverage.json |

| `compose.yaml` | 80 | fonte/teste/config; ver coverage.json |

| `config.yaml` | 137 | fonte/teste/config; ver coverage.json |

| `contracts/a1-ou25-phase0-policy.json` | 35 | fonte/teste/config; ver coverage.json |

| `contracts/brasileirao-api-football-fixtures-v1.json` | 24 | fonte/teste/config; ver coverage.json |

| `contracts/h8-ou25-frozen-candidate.json` | 37 | fonte/teste/config; ver coverage.json |

| `contracts/h9-ou25-prospective.json` | 28 | fonte/teste/config; ver coverage.json |

| `contracts/ou25-nested-future-candidate.json` | 24 | fonte/teste/config; ver coverage.json |

| `contracts/ou25-paper-capital-round-2026-08-29.json` | 73 | fonte/teste/config; ver coverage.json |

| `contracts/ou25-recommendation-v2.json` | 54 | fonte/teste/config; ver coverage.json |

| `contracts/ou25-under-high-ev-prospective-2026.json` | 57 | fonte/teste/config; ver coverage.json |

| `contracts/redis-fair-odds-v2.schema.json` | 21 | fonte/teste/config; ver coverage.json |

| `contracts/redis-protocol-v1.schema.json` | 18 | fonte/teste/config; ver coverage.json |

| `contracts/redis-protocol-v2.md` | 166 | fonte/teste/config; ver coverage.json |

| `contracts/redis-protocol-v2.schema.json` | 26 | fonte/teste/config; ver coverage.json |

| `contracts/season-2026-turn-split-paper.json` | 94 | fonte/teste/config; ver coverage.json |

| `dotnet/LineupWorker.Tests/CompletionContractTests.cs` | 38 | fonte/teste/config; ver coverage.json |

| `dotnet/LineupWorker.Tests/FairOddsCorrelationTests.cs` | 172 | fonte/teste/config; ver coverage.json |

| `dotnet/LineupWorker.Tests/FairOddsRecoveryTests.cs` | 192 | fonte/teste/config; ver coverage.json |

| `dotnet/LineupWorker.Tests/KellyMathTests.cs` | 14 | fonte/teste/config; ver coverage.json |

| `dotnet/LineupWorker.Tests/KernelCrossProcessTests.cs` | 215 | fonte/teste/config; ver coverage.json |

| `dotnet/LineupWorker.Tests/KernelInvocationIdentityTests.cs` | 117 | fonte/teste/config; ver coverage.json |

| `dotnet/LineupWorker.Tests/LatencyAuditIntegrityTests.cs` | 98 | fonte/teste/config; ver coverage.json |

| `dotnet/LineupWorker.Tests/LatencyOrderingTests.cs` | 47 | fonte/teste/config; ver coverage.json |

| `dotnet/LineupWorker.Tests/LineupStreamTests.cs` | 169 | fonte/teste/config; ver coverage.json |

| `dotnet/LineupWorker.Tests/LineupWorker.Tests.csproj` | 18 | fonte/teste/config; ver coverage.json |

| `dotnet/LineupWorker.Tests/MarketFeedContractTests.cs` | 163 | fonte/teste/config; ver coverage.json |

| `dotnet/LineupWorker.Tests/ModelBranchTests.cs` | 86 | fonte/teste/config; ver coverage.json |

| `dotnet/LineupWorker.Tests/OperationalSettingsTests.cs` | 84 | fonte/teste/config; ver coverage.json |

| `dotnet/LineupWorker.Tests/RedisEndpointTests.cs` | 32 | fonte/teste/config; ver coverage.json |

| `dotnet/LineupWorker.Tests/RedisProtocolTests.cs` | 113 | fonte/teste/config; ver coverage.json |

| `dotnet/LineupWorker.Tests/WatchdogRecoveryTests.cs` | 115 | fonte/teste/config; ver coverage.json |

| `dotnet/LineupWorker.Tests/WorkerHealthTests.cs` | 121 | fonte/teste/config; ver coverage.json |

| `dotnet/LineupWorker.Tests/WorkerInputContractTests.cs` | 70 | fonte/teste/config; ver coverage.json |

| `dotnet/LineupWorker.Tests/WorkerRuntimeFencingTests.cs` | 307 | fonte/teste/config; ver coverage.json |

| `dotnet/LineupWorker.Tests/WorkerRuntimeTests.cs` | 479 | fonte/teste/config; ver coverage.json |

| `dotnet/LineupWorker/LineupWorker.csproj` | 16 | fonte/teste/config; ver coverage.json |

| `dotnet/LineupWorker/Models/KernelContracts.cs` | 146 | fonte/teste/config; ver coverage.json |

| `dotnet/LineupWorker/Models/LatencyRecord.cs` | 81 | fonte/teste/config; ver coverage.json |

| `dotnet/LineupWorker/Models/LineupEvent.cs` | 51 | fonte/teste/config; ver coverage.json |

| `dotnet/LineupWorker/Models/LineupModelInputs.cs` | 41 | fonte/teste/config; ver coverage.json |

| `dotnet/LineupWorker/OperationalSettings.cs` | 65 | fonte/teste/config; ver coverage.json |

| `dotnet/LineupWorker/Program.cs` | 93 | fonte/teste/config; ver coverage.json |

| `dotnet/LineupWorker/Services/KernelRedisProtocolV2.cs` | 264 | fonte/teste/config; ver coverage.json |

| `dotnet/LineupWorker/Services/LatencyAuditService.cs` | 155 | fonte/teste/config; ver coverage.json |

| `dotnet/LineupWorker/Services/LineupStreamConsumer.cs` | 142 | fonte/teste/config; ver coverage.json |

| `dotnet/LineupWorker/Services/MarketOddsCache.cs` | 211 | fonte/teste/config; ver coverage.json |

| `dotnet/LineupWorker/Services/MarketStateEngine.cs` | 407 | fonte/teste/config; ver coverage.json |

| `dotnet/LineupWorker/Services/VorpStateService.cs` | 110 | fonte/teste/config; ver coverage.json |

| `dotnet/LineupWorker/Services/WatchdogStateStore.cs` | 56 | fonte/teste/config; ver coverage.json |

| `dotnet/LineupWorker/Services/WorkerHealth.cs` | 70 | fonte/teste/config; ver coverage.json |

| `dotnet/LineupWorker/Worker.cs` | 437 | fonte/teste/config; ver coverage.json |

| `global.json` | 1 | fonte/teste/config; ver coverage.json |

| `poc_oddspapi.py` | 139 | fonte/teste/config; ver coverage.json |

| `pyproject.toml` | 63 | fonte/teste/config; ver coverage.json |

| `pytest.ini` | 9 | fonte/teste/config; ver coverage.json |

| `schemas/odds_snapshot_v1.json` | 40 | fonte/teste/config; ver coverage.json |

| `scripts/migration/build_data_archive.py` | 627 | fonte/teste/config; ver coverage.json |

| `scripts/migration/verify_archive.py` | 112 | fonte/teste/config; ver coverage.json |

| `tests/conftest.py` | 11 | fonte/teste/config; ver coverage.json |

| `tests/test_a1_phase0.py` | 104 | fonte/teste/config; ver coverage.json |

| `tests/test_a1_recommendation.py` | 76 | fonte/teste/config; ver coverage.json |

| `tests/test_api_football_provider.py` | 118 | fonte/teste/config; ver coverage.json |

| `tests/test_audit_fixes.py` | 349 | fonte/teste/config; ver coverage.json |

| `tests/test_backtest_extended.py` | 178 | fonte/teste/config; ver coverage.json |

| `tests/test_backtest_odds.py` | 237 | fonte/teste/config; ver coverage.json |

| `tests/test_backup_restore.py` | 88 | fonte/teste/config; ver coverage.json |

| `tests/test_benchmark_panel_fixes.py` | 389 | fonte/teste/config; ver coverage.json |

| `tests/test_bet_id.py` | 59 | fonte/teste/config; ver coverage.json |

| `tests/test_bet_log.py` | 331 | fonte/teste/config; ver coverage.json |

| `tests/test_bitemporal_store.py` | 44 | fonte/teste/config; ver coverage.json |

| `tests/test_bookmaker_odds.py` | 228 | fonte/teste/config; ver coverage.json |

| `tests/test_bookmaker_stability.py` | 62 | fonte/teste/config; ver coverage.json |

| `tests/test_bootstrap.py` | 66 | fonte/teste/config; ver coverage.json |

| `tests/test_brasileirao_domain.py` | 230 | fonte/teste/config; ver coverage.json |

| `tests/test_build_data_archive.py` | 286 | fonte/teste/config; ver coverage.json |

| `tests/test_bundle_h9_evidence.py` | 19 | fonte/teste/config; ver coverage.json |

| `tests/test_calibration_gate.py` | 51 | fonte/teste/config; ver coverage.json |

| `tests/test_capture_decision.py` | 212 | fonte/teste/config; ver coverage.json |

| `tests/test_capture_sofascore_event.py` | 109 | fonte/teste/config; ver coverage.json |

| `tests/test_ci_current_elo_containment.py` | 45 | fonte/teste/config; ver coverage.json |

| `tests/test_ci_dependency_pins.py` | 16 | fonte/teste/config; ver coverage.json |

| `tests/test_ci_nao_suja_a_arvore.py` | 55 | fonte/teste/config; ver coverage.json |

| `tests/test_closeout_coverage.py` | 35 | fonte/teste/config; ver coverage.json |

| `tests/test_closeout_integrity.py` | 169 | fonte/teste/config; ver coverage.json |

| `tests/test_closeout_research_inputs.py` | 75 | fonte/teste/config; ver coverage.json |

| `tests/test_closeout_status.py` | 30 | fonte/teste/config; ver coverage.json |

| `tests/test_closing_scenario.py` | 89 | fonte/teste/config; ver coverage.json |

| `tests/test_collection_only_archive.py` | 56 | fonte/teste/config; ver coverage.json |

| `tests/test_collector_contract.py` | 323 | fonte/teste/config; ver coverage.json |

| `tests/test_compare_hypothesis_errors.py` | 12 | fonte/teste/config; ver coverage.json |

| `tests/test_completion_anchor.py` | 41 | fonte/teste/config; ver coverage.json |

| `tests/test_completion_compose_init.py` | 48 | fonte/teste/config; ver coverage.json |

| `tests/test_completion_event_inputs.py` | 39 | fonte/teste/config; ver coverage.json |

| `tests/test_completion_ledger.py` | 67 | fonte/teste/config; ver coverage.json |

| `tests/test_completion_math_consumer.py` | 73 | fonte/teste/config; ver coverage.json |

| `tests/test_completion_pit_contracts.py` | 90 | fonte/teste/config; ver coverage.json |

| `tests/test_completion_regressions.py` | 94 | fonte/teste/config; ver coverage.json |

| `tests/test_completion_serving_storage.py` | 29 | fonte/teste/config; ver coverage.json |

| `tests/test_completion_source_budget.py` | 65 | fonte/teste/config; ver coverage.json |

| `tests/test_contextual_ensemble.py` | 39 | fonte/teste/config; ver coverage.json |

| `tests/test_core3_harness_contract.py` | 37 | fonte/teste/config; ver coverage.json |

| `tests/test_core_integrity.py` | 21 | fonte/teste/config; ver coverage.json |

| `tests/test_db.py` | 172 | fonte/teste/config; ver coverage.json |

| `tests/test_db_extended_odds.py` | 189 | fonte/teste/config; ver coverage.json |

| `tests/test_db_readonly.py` | 33 | fonte/teste/config; ver coverage.json |

| `tests/test_dixon_coles.py` | 98 | fonte/teste/config; ver coverage.json |

| `tests/test_dixon_coles_fit.py` | 117 | fonte/teste/config; ver coverage.json |

| `tests/test_draw_diagnostics.py` | 30 | fonte/teste/config; ver coverage.json |

| `tests/test_dynamic_strength.py` | 37 | fonte/teste/config; ver coverage.json |

| `tests/test_economic_search.py` | 118 | fonte/teste/config; ver coverage.json |

| `tests/test_ecosystem_plugin.py` | 19 | fonte/teste/config; ver coverage.json |

| `tests/test_elo_baseline.py` | 62 | fonte/teste/config; ver coverage.json |

| `tests/test_elo_baseline_block_guard.py` | 90 | fonte/teste/config; ver coverage.json |

| `tests/test_emit_h9_shadow.py` | 266 | fonte/teste/config; ver coverage.json |

| `tests/test_evaluate_h14_prospective.py` | 130 | fonte/teste/config; ver coverage.json |

| `tests/test_evaluate_h15_prospective.py` | 125 | fonte/teste/config; ver coverage.json |

| `tests/test_exp001_coverage_audit.py` | 12 | fonte/teste/config; ver coverage.json |

| `tests/test_exp001_cutoff_state_regression.py` | 108 | fonte/teste/config; ver coverage.json |

| `tests/test_exp001_data_pilot.py` | 26 | fonte/teste/config; ver coverage.json |

| `tests/test_feature_builder.py` | 119 | fonte/teste/config; ver coverage.json |

| `tests/test_find_odds.py` | 120 | fonte/teste/config; ver coverage.json |

| `tests/test_followup_capture_contract.py` | 263 | fonte/teste/config; ver coverage.json |

| `tests/test_formal_prediction.py` | 82 | fonte/teste/config; ver coverage.json |

| `tests/test_h10_fadiga_walkforward.py` | 133 | fonte/teste/config; ver coverage.json |

| `tests/test_h9_missed_window_exit.py` | 17 | fonte/teste/config; ver coverage.json |

| `tests/test_h9_shadow.py` | 75 | fonte/teste/config; ver coverage.json |

| `tests/test_historical_admission.py` | 132 | fonte/teste/config; ver coverage.json |

| `tests/test_historical_expansion.py` | 63 | fonte/teste/config; ver coverage.json |

| `tests/test_historical_numeric_boundary.py` | 14 | fonte/teste/config; ver coverage.json |

| `tests/test_hostil_2026_07_18.py` | 240 | fonte/teste/config; ver coverage.json |

| `tests/test_hotpath_cold_start.py` | 30 | fonte/teste/config; ver coverage.json |

| `tests/test_hotpath_smoke.py` | 152 | fonte/teste/config; ver coverage.json |

| `tests/test_identity.py` | 42 | fonte/teste/config; ver coverage.json |

| `tests/test_info_stake_cap.py` | 38 | fonte/teste/config; ver coverage.json |

| `tests/test_ingest_typing_boundaries.py` | 54 | fonte/teste/config; ver coverage.json |

| `tests/test_integral_review_admission.py` | 76 | fonte/teste/config; ver coverage.json |

| `tests/test_integral_review_domain.py` | 18 | fonte/teste/config; ver coverage.json |

| `tests/test_integral_review_event_backtest.py` | 84 | fonte/teste/config; ver coverage.json |

| `tests/test_inventario_dados.py` | 163 | fonte/teste/config; ver coverage.json |

| `tests/test_kernel_cli_redis.py` | 100 | fonte/teste/config; ver coverage.json |

| `tests/test_kernel_protocol.py` | 191 | fonte/teste/config; ver coverage.json |

| `tests/test_kernel_runtime.py` | 256 | fonte/teste/config; ver coverage.json |

| `tests/test_kernel_v2_runtime.py` | 200 | fonte/teste/config; ver coverage.json |

| `tests/test_kickoff_block_guard.py` | 123 | fonte/teste/config; ver coverage.json |

| `tests/test_ledger_consistency.py` | 171 | fonte/teste/config; ver coverage.json |

| `tests/test_lineup_archive.py` | 18 | fonte/teste/config; ver coverage.json |

| `tests/test_lineup_inbox.py` | 23 | fonte/teste/config; ver coverage.json |

| `tests/test_lineup_inbox_redis.py` | 108 | fonte/teste/config; ver coverage.json |

| `tests/test_live_capture_admission.py` | 103 | fonte/teste/config; ver coverage.json |

| `tests/test_logic_registry.py` | 42 | fonte/teste/config; ver coverage.json |

| `tests/test_market_0b_resolution.py` | 79 | fonte/teste/config; ver coverage.json |

| `tests/test_market_anchor.py` | 86 | fonte/teste/config; ver coverage.json |

| `tests/test_market_edge_ordering.py` | 122 | fonte/teste/config; ver coverage.json |

| `tests/test_market_pricer.py` | 141 | fonte/teste/config; ver coverage.json |

| `tests/test_market_probs_date.py` | 69 | fonte/teste/config; ver coverage.json |

| `tests/test_market_research_jobs_manifest.py` | 14 | fonte/teste/config; ver coverage.json |

| `tests/test_market_residual.py` | 135 | fonte/teste/config; ver coverage.json |

| `tests/test_math.py` | 150 | fonte/teste/config; ver coverage.json |

| `tests/test_missingness_audit.py` | 27 | fonte/teste/config; ver coverage.json |

| `tests/test_model.py` | 113 | fonte/teste/config; ver coverage.json |

| `tests/test_model_xg.py` | 141 | fonte/teste/config; ver coverage.json |

| `tests/test_odds_api_snapshot.py` | 113 | fonte/teste/config; ver coverage.json |

| `tests/test_odds_shop_stale.py` | 63 | fonte/teste/config; ver coverage.json |

| `tests/test_odds_source_smoke.py` | 28 | fonte/teste/config; ver coverage.json |

| `tests/test_operational_provenance.py` | 56 | fonte/teste/config; ver coverage.json |

| `tests/test_operational_readiness.py` | 61 | fonte/teste/config; ver coverage.json |

| `tests/test_ou25_annual.py` | 33 | fonte/teste/config; ver coverage.json |

| `tests/test_ou25_certainty.py` | 11 | fonte/teste/config; ver coverage.json |

| `tests/test_ou25_market_anchor.py` | 56 | fonte/teste/config; ver coverage.json |

| `tests/test_ou25_nested_replay.py` | 161 | fonte/teste/config; ver coverage.json |

| `tests/test_parse_all_odds.py` | 175 | fonte/teste/config; ver coverage.json |

| `tests/test_parse_ou_scope_regression.py` | 126 | fonte/teste/config; ver coverage.json |

| `tests/test_parsers_sofascore.py` | 286 | fonte/teste/config; ver coverage.json |

| `tests/test_permutation_test.py` | 131 | fonte/teste/config; ver coverage.json |

| `tests/test_persist_h14_prospective.py` | 179 | fonte/teste/config; ver coverage.json |

| `tests/test_persist_h15_prospective.py` | 224 | fonte/teste/config; ver coverage.json |

| `tests/test_pit_backfill.py` | 220 | fonte/teste/config; ver coverage.json |

| `tests/test_pit_contextual_features.py` | 63 | fonte/teste/config; ver coverage.json |

| `tests/test_pit_features_scaffold.py` | 79 | fonte/teste/config; ver coverage.json |

| `tests/test_player_comp_stats_sofascore.py` | 44 | fonte/teste/config; ver coverage.json |

| `tests/test_predict_cache_freshness.py` | 57 | fonte/teste/config; ver coverage.json |

| `tests/test_prediction_log.py` | 201 | fonte/teste/config; ver coverage.json |

| `tests/test_prediction_protocol.py` | 120 | fonte/teste/config; ver coverage.json |

| `tests/test_prereg_serving_vs_climatologia.py` | 127 | fonte/teste/config; ver coverage.json |

| `tests/test_price_hurdle.py` | 121 | fonte/teste/config; ver coverage.json |

| `tests/test_price_strength_artifacts.py` | 242 | fonte/teste/config; ver coverage.json |

| `tests/test_price_strength_dynamic_xg.py` | 296 | fonte/teste/config; ver coverage.json |

| `tests/test_price_strength_quotes.py` | 361 | fonte/teste/config; ver coverage.json |

| `tests/test_price_strength_reliability.py` | 185 | fonte/teste/config; ver coverage.json |

| `tests/test_price_strength_review_regressions.py` | 187 | fonte/teste/config; ver coverage.json |

| `tests/test_price_strength_study.py` | 160 | fonte/teste/config; ver coverage.json |

| `tests/test_promoted_cold_start.py` | 87 | fonte/teste/config; ver coverage.json |

| `tests/test_promotions_dataset.py` | 38 | fonte/teste/config; ver coverage.json |

| `tests/test_prospective_evaluation_guard.py` | 301 | fonte/teste/config; ver coverage.json |

| `tests/test_prospective_readiness.py` | 24 | fonte/teste/config; ver coverage.json |

| `tests/test_prospective_validation_scaffold.py` | 172 | fonte/teste/config; ver coverage.json |

| `tests/test_ratings.py` | 151 | fonte/teste/config; ver coverage.json |

| `tests/test_reconciliation_gate_contracts.py` | 124 | fonte/teste/config; ver coverage.json |

| `tests/test_record_h9_closing_snapshots.py` | 90 | fonte/teste/config; ver coverage.json |

| `tests/test_redis_contract.py` | 17 | fonte/teste/config; ver coverage.json |

| `tests/test_redis_integration.py` | 511 | fonte/teste/config; ver coverage.json |

| `tests/test_repo_hygiene.py` | 40 | fonte/teste/config; ver coverage.json |

| `tests/test_report_h9_execution_quality.py` | 102 | fonte/teste/config; ver coverage.json |

| `tests/test_report_shadow_mode.py` | 147 | fonte/teste/config; ver coverage.json |

| `tests/test_research_01a_refit_cadence.py` | 303 | fonte/teste/config; ver coverage.json |

| `tests/test_research_xg_ensemble.py` | 155 | fonte/teste/config; ver coverage.json |

| `tests/test_residual_artifact_integrity.py` | 144 | fonte/teste/config; ver coverage.json |

| `tests/test_residual_dataset.py` | 74 | fonte/teste/config; ver coverage.json |

| `tests/test_residual_diagnostics.py` | 27 | fonte/teste/config; ver coverage.json |

| `tests/test_residual_features.py` | 53 | fonte/teste/config; ver coverage.json |

| `tests/test_residual_gate.py` | 22 | fonte/teste/config; ver coverage.json |

| `tests/test_residual_walkforward.py` | 57 | fonte/teste/config; ver coverage.json |

| `tests/test_resolution_bank.py` | 83 | fonte/teste/config; ver coverage.json |

| `tests/test_resolution_coverage.py` | 86 | fonte/teste/config; ver coverage.json |

| `tests/test_resolution_curated_versions.py` | 138 | fonte/teste/config; ver coverage.json |

| `tests/test_resolution_gate_dependence.py` | 28 | fonte/teste/config; ver coverage.json |

| `tests/test_resolution_historical_import.py` | 84 | fonte/teste/config; ver coverage.json |

| `tests/test_resolution_kernel_lifecycle.py` | 132 | fonte/teste/config; ver coverage.json |

| `tests/test_resolution_kernel_params.py` | 26 | fonte/teste/config; ver coverage.json |

| `tests/test_resolution_lineup_envelopes.py` | 82 | fonte/teste/config; ver coverage.json |

| `tests/test_resolution_live_settlement.py` | 103 | fonte/teste/config; ver coverage.json |

| `tests/test_resolution_odds_shop.py` | 79 | fonte/teste/config; ver coverage.json |

| `tests/test_resolution_player_stats.py` | 42 | fonte/teste/config; ver coverage.json |

| `tests/test_resolution_promotions.py` | 47 | fonte/teste/config; ver coverage.json |

| `tests/test_resolution_residual_dataset.py` | 101 | fonte/teste/config; ver coverage.json |

| `tests/test_resolution_restore.py` | 84 | fonte/teste/config; ver coverage.json |

| `tests/test_resolution_structural_edge.py` | 69 | fonte/teste/config; ver coverage.json |

| `tests/test_resolution_walkforward.py` | 122 | fonte/teste/config; ver coverage.json |

| `tests/test_rho_stability.py` | 27 | fonte/teste/config; ver coverage.json |

| `tests/test_run_passive_process_tree.py` | 156 | fonte/teste/config; ver coverage.json |

| `tests/test_run_passive_task.py` | 154 | fonte/teste/config; ver coverage.json |

| `tests/test_season_2026_split.py` | 131 | fonte/teste/config; ver coverage.json |

| `tests/test_secrets_telemetry.py` | 22 | fonte/teste/config; ver coverage.json |

| `tests/test_serving_evaluator.py` | 271 | fonte/teste/config; ver coverage.json |

| `tests/test_settings.py` | 36 | fonte/teste/config; ver coverage.json |

| `tests/test_settle.py` | 78 | fonte/teste/config; ver coverage.json |

| `tests/test_settle_h9_shadow.py` | 124 | fonte/teste/config; ver coverage.json |

| `tests/test_settle_live_prediction.py` | 53 | fonte/teste/config; ver coverage.json |

| `tests/test_settlement_input_integrity.py` | 26 | fonte/teste/config; ver coverage.json |

| `tests/test_shadow_cohort_evaluator.py` | 178 | fonte/teste/config; ver coverage.json |

| `tests/test_shared_dependencies.py` | 65 | fonte/teste/config; ver coverage.json |

| `tests/test_simulator.py` | 63 | fonte/teste/config; ver coverage.json |

| `tests/test_simulator_fixes.py` | 44 | fonte/teste/config; ver coverage.json |

| `tests/test_sofascore_cache.py` | 107 | fonte/teste/config; ver coverage.json |

| `tests/test_sofascore_probe.py` | 121 | fonte/teste/config; ver coverage.json |

| `tests/test_sombra_h5.py` | 219 | fonte/teste/config; ver coverage.json |

| `tests/test_sombra_runtime_paths.py` | 31 | fonte/teste/config; ver coverage.json |

| `tests/test_source_temporal_regressions.py` | 89 | fonte/teste/config; ver coverage.json |

| `tests/test_sportmonks_provider.py` | 98 | fonte/teste/config; ver coverage.json |

| `tests/test_statistics_parser.py` | 69 | fonte/teste/config; ver coverage.json |

| `tests/test_structural_edge.py` | 103 | fonte/teste/config; ver coverage.json |

| `tests/test_sync_competition_filter.py` | 57 | fonte/teste/config; ver coverage.json |

| `tests/test_telemetry.py` | 23 | fonte/teste/config; ver coverage.json |

| `tests/test_temporal_policy.py` | 55 | fonte/teste/config; ver coverage.json |

| `tests/test_temporal_replay.py` | 32 | fonte/teste/config; ver coverage.json |

| `tests/test_the_odds_api_provider.py` | 182 | fonte/teste/config; ver coverage.json |

| `tests/test_trial_provenance_enforcement.py` | 146 | fonte/teste/config; ver coverage.json |

| `tests/test_trials_registry_schema.py` | 80 | fonte/teste/config; ver coverage.json |

| `tests/test_update_h9_fixtures.py` | 25 | fonte/teste/config; ver coverage.json |

| `tests/test_walkforward_temporal_blocks.py` | 15 | fonte/teste/config; ver coverage.json |

| `tests/test_windows_scheduler_contract.py` | 64 | fonte/teste/config; ver coverage.json |

| `tests/test_xg_input_quality.py` | 98 | fonte/teste/config; ver coverage.json |

| `tests/test_xg_model.py` | 213 | fonte/teste/config; ver coverage.json |

| `tools/export_cain_bundle.py` | 133 | fonte/teste/config; ver coverage.json |

| `tools/export_cain_status.py` | 166 | fonte/teste/config; ver coverage.json |

| `tools/integration_validation/run.py` | 241 | fonte/teste/config; ver coverage.json |

| `tools/publication_validation/compose_config.py` | 58 | fonte/teste/config; ver coverage.json |

| `tools/publication_validation/guard_probes.py` | 67 | fonte/teste/config; ver coverage.json |

| `tools/publication_validation/installed_shadow.py` | 57 | fonte/teste/config; ver coverage.json |

| `tools/publication_validation/run.py` | 155 | fonte/teste/config; ver coverage.json |

| `tools/runtime_lab/kernel_synthetic.py` | 60 | fonte/teste/config; ver coverage.json |

| `tools/runtime_lab/lab_guard.py` | 78 | fonte/teste/config; ver coverage.json |

| `tools/runtime_lab/python_tests.py` | 40 | fonte/teste/config; ver coverage.json |

| `tools/runtime_lab/run.py` | 272 | fonte/teste/config; ver coverage.json |

| `tools/runtime_lab/sitecustomize.py` | 8 | fonte/teste/config; ver coverage.json |

| `tools/test_export_cain_bundle.py` | 139 | fonte/teste/config; ver coverage.json |

| `tools/test_export_cain_status.py` | 57 | fonte/teste/config; ver coverage.json |

| `uv.lock` | 1260 | fonte/teste/config; ver coverage.json |

| `brasileirao_scripts/prospective_metrics.py` | 50 | não rastreado local |

| `brasileirao_scripts/prospective_protocol_v2.py` | 336 | não rastreado local |

| `tests/test_audit_hardening.py` | 46 | não rastreado local |

| `tests/test_prospective_metrics.py` | 36 | não rastreado local |

| `tests/test_prospective_protocol_compatibility.py` | 102 | não rastreado local |

| `tests/test_prospective_protocol_v2.py` | 243 | não rastreado local |

| `tests/test_walkforward_row_contract.py` | 38 | não rastreado local |

