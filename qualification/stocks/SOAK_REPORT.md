# SOAK_REPORT — missão stocks (C10; gate SOAK)

**Estado do gate: PASS (D-16, run 35983568296; seção D-16 no fim).** A execução com a fixture sintética logo abaixo é o diagnóstico anterior à D-16. A regra congelada (`FROZEN_PARAMETERS.d16_dependency_rule`)
exige dado real no Linux primário para o SOAK; a execução abaixo usa a fixture sintética congelada e é
**diagnóstico**.

Perfil: `QUALIFICATION_PROFILE_STOCKS_V1.json` (números congelados em `FROZEN_PARAMETERS.soak_profile` antes da
execução). Runtime suportado (wheels publicadas), GitHub Actions ubuntu-latest, cada chamada ao `stocks-research` num
processo novo. Log bruto: `qualification/stocks/RAW_LOGS/cleanroom-final/run35954279991/stocks-runtime-linux-primary/soak.jsonl`.

| medida | valor |
|---|---|
| chamadas ao entrypoint | 73 |
| falhas injetadas | 17 |
| pedidos com resultado esperado | 48 |
| resultados armazenados | 48 |
| efeitos de domínio | 48 |
| jobs do Ops / máximo de SUCCEEDED por job | 48 / 1 |
| resultados perdidos / inesperados | 0 / 0 |
| releitura divergente | 0 |
| violações (duplicata, autoridade, IDs) | 0 |
| violações PIT | 0 |
| trials elegíveis de External Intelligence | 0 (nenhuma família READY) |
| tolerância zero | True |

## D-16 — soak sobre o painel real (run 35983568296)

Log bruto: `qualification/stocks/RAW_LOGS/d16/run35983568296/stocks-d16-linux-primary/soak.jsonl` (d16/d16_soak.py, perfil congelado, runtime suportado, Linux primário).

| medida | valor | mínimo do perfil |
|---|---|---|
| process_calls | 67 | — |
| normal_cycles | 20 | 20 |
| restarts | 11 | 5 |
| duplicates | 5 | 5 |
| ops_worker_crash | 3 | 3 |
| before_admission_commit | 4 | 3 |
| during_result_write | 3 | 3 |
| timeouts | 3 | 3 |
| family_not_ready | 3 | 3 |
| collection_only_valid | 5 | 5 |
| eligible_trials | 0 | — |
| requests_with_result | 42 | |
| stored_results | 42 | |
| lost | [] | |
| unexpected | [] | |
| domain_effects | 42 | |
| ops_jobs | 42 | |
| ops_success_per_job_max | 1 | |
| reread_mismatch | [] | |
| reconcile_exit | 0 | |
| reconcile_findings | [] | |
| violations | [] | |
| pit_violations | [] | |
| rebalance_sessions_checked | 49 | |
| universe_contamination | [] | |
| distinct_metrics_for_identical_requests | 1 | |
| operator_store_unchanged | true | |
| tolerância zero | True | |

**Gate SOAK: PASS.**
