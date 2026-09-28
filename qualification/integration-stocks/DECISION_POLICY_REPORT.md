# integration-stocks — DECISION_POLICY_REPORT

Gate `DECISION_POLICY` (C12). Framework da integration-crypto **sem mudança** (regras R01–R14, receipt `cain-decision-receipt/1`, ver `qualification/integration-crypto/DECISION_POLICY_REPORT.md`); esta missão acrescenta só a configuração do Stocks, empacotada no `cain-research` 0.4.13rc7 (`src/cain/orchestration/data/stocks.json`).

## Configuração do Stocks (FROZEN_PARAMETERS.json → decision_policy.stocks_config)

Fonte: `qualification/integration-stocks/FROZEN_PARAMETERS.json` (sha256 `771b8a23e9b9bde7…`), chave `decision_policy.stocks_config`.

- fontes: stocks-predictor `61fc017256ffea815ae96bbe02b847dccdb395cc` (SHA completo): `stocks_predictor/research_admission.py`, `trials_v2.json`, `trials.json`, `config.yaml`, `EXTERNAL_INTELLIGENCE_TRIAL_READINESS_MATRIX.json`; contrato `qualification/stocks/DOMAIN_RESEARCH_CONTRACT.json` (`76fa8227dd83eb9a…`);
- tipos de pedido: BACKTEST_PIT_FACTOR, COLLECT_EXTERNAL_INTELLIGENCE;
- hipóteses que a política nunca reabre (22, H1..H22): CLOSED_JUDGED H1, H2, H3, H4, H5, H6, H8, H11, H14, H15, H16; CLOSED_EMBARGO_ORIGINAL H7, H9, H10, H12, H13; PAUSED_INCONCLUSIVE_DATA_QUALITY H17; PAUSED H18, H19; CLOSED_HISTORICAL H20; CLOSED_HISTORICAL_CONDITIONAL H21; CLOSED_REJECTED H22;
- famílias congeladas (15): low_vol_252, momentum_12_1, momentum_12_1_total_return, momentum_6_1, momentum_lowvol_intersection, near_52w_high, net_margin, quality_leverage, quality_roe, quality_roe_leverage_intersection, revenue_growth_yoy, reversal_21d, turn_of_month, vol_target_sizing, volume_surge;
- hipóteses propostas pela missão: stocks:QUAL-EI-COLLECTION-001, stocks:QUAL-PIT-MOM-001, stocks:QUAL-PIT-MOM-REAL-001, stocks:QUAL-PIT-MOM-REAL-002, stocks:QUAL-PIT-MOM-REAL-003;
- custos: fee 3 bps + slippage 15 bps (config.yaml [H1-FROZEN] execution.b3_fee_pct 0.0003 e spread_slippage_pct 0.0015 em 61fc017 (os mesmos do cost_model h1-frozen do contrato));
- prioridade máxima NORMAL; budget {"max_open_tasks": 1, "max_tasks_per_research": 64, "max_tasks_total": 512}; cooldown {"after_consecutive_negative": 3, "episodes": 2};
- ST-F007: rebalance a cada 21 pregões (universe.rebalance_every_sessions = 21, o que o handler compilado aceita), nunca 'fim de mês' (D-21)
- ST-F008: painel público só-preço com lacunas de eventos (D-21): a DecisionPolicy não lê métrica nenhuma; estados científico/econômico só entram como registro e nunca aumentam budget, prioridade ou escopo
- C22: QUALIFIED da Etapa A não é edge econômico; WATCH/WATCH_NO_CAPITAL nunca viram sinal nem capital

## Decisões do N+1 (receipt em 3 processos novos, byte a byte)

Fonte: `qualification/integration-stocks/RAW_LOGS/runtime/run36365355063/n-plus-1/frozen/SUMMARY.json` (sha256 `70e38fb48fd64d10…`).

| Candidata | Decisão | Motivo | Regra |
|---|---|---|---|
| 01-next | ALLOW | ALLOWED | R14 |
| 02-duplicate | DUPLICATE | DUPLICATE_REQUEST | R08 |
| 03-crypto-h9 | BLOCK | DOMAIN_MISMATCH | R01 |
| 04-stocks-h9 | BLOCK | HYPOTHESIS_CLOSED | R05 |
| 05-brasileirao-h9 | BLOCK | DOMAIN_MISMATCH | R01 |
| 06-new-hypothesis | REQUIRE_HUMAN | NEW_HYPOTHESIS | R11 |
| 07-h1-momentum | BLOCK | HYPOTHESIS_CLOSED | R05 |
| 08-h2-low-vol | BLOCK | HYPOTHESIS_CLOSED | R05 |
| 09-h14-52w-high | BLOCK | HYPOTHESIS_CLOSED | R05 |
| 10-h15-volume | BLOCK | HYPOTHESIS_CLOSED | R05 |
| 11-family-momentum | BLOCK | HYPOTHESIS_CLOSED | R05 |
| 12-family-low-vol | BLOCK | HYPOTHESIS_CLOSED | R05 |
| 13-family-52w-high | BLOCK | HYPOTHESIS_CLOSED | R05 |
| 14-family-volume | BLOCK | HYPOTHESIS_CLOSED | R05 |
| 15-watch-high-priority | BLOCK | PRIORITY_ABOVE_CAP | R06 |
| 16-cost-mismatch | BLOCK | COST_MODEL_MISMATCH | R06 |
| 17-collection | BLOCK | COST_MODEL_MISMATCH | R06 |
| 18-llm-shape | BLOCK | SCHEMA_INVALID | R02 |
| 19-unqualified-id | BLOCK | DOMAIN_MISMATCH | R01 |
| 20-reference-not-allowed | BLOCK | REFERENCE_NOT_ALLOWED | R06 |

## Limites do framework genérico para o Stocks (achados antes do congelamento; framework não mudado)

- IS-F002: R06 compara custos em todo pedido; a coleta não tem custos ⇒ `BLOCK COST_MODEL_MISMATCH` (candidata 17-collection). O CAIN desta missão não propõe coleta.
- IS-F003: o caminho de LLM grava `placebo_seed` (parâmetro do cripto) ⇒ `BLOCK SCHEMA_INVALID` (candidata 18-llm-shape e propostas do soak).
