# integration-stocks — DECISION_POLICY_REPORT

Gate `DECISION_POLICY` (C12). Política `cain-decision-policy` versão 2 do `cain-research` 0.4.13rc15 (`src/cain/orchestration/policy.py`, sha256 `aff2f5fc6198eb49…`, conferido em `fb0e1dcb9003`), receipt `cain-decision-receipt/1`; configuração do Stocks empacotada em `src/cain/orchestration/data/stocks.json`.

## Regras, na ordem de avaliação (FROZEN_PARAMETERS.json → decision_policy.rule_order)

1. R01 BLOCK DOMAIN_MISMATCH: proposta, pedido ou evidência de outro domínio, ou ID sem domínio (C18)
2. R02 BLOCK SCHEMA_INVALID: forma da proposta ou pedido fora do request_schema congelado do Stocks
3. R03 BLOCK FORBIDDEN_FIELD: campo fora de cain-proposal/1 (handler, comando, módulo, caminho, URL, budget, prioridade final, capital …) ou client_ref que o envelope controla
4. R04 BLOCK REQUEST_TYPE_NOT_ALLOWED: request_type fora da handler_allowlist do contrato, ou diferente do tipo que a configuração fixa para a hipótese proponível (proposable_request_types, cain#67; no Stocks as fixtures de proposta congeladas decidem: coleta nunca vai como backtest)
5. R05 BLOCK HYPOTHESIS_CLOSED: hipótese encerrada do estado científico (stocks:H1..H22) ou família congelada
6. R16 REQUIRE_HUMAN SEALED_SCOPE: pedido que tocaria um escopo lacrado da configuração (sealed_scopes); Stocks: nenhum lacre (lista vazia)
7. R06 BLOCK SYMBOL_NOT_ALLOWED / COST_MODEL_MISMATCH / REFERENCE_NOT_ALLOWED / PRIORITY_ABOVE_CAP: custos comparados só quando a variante de parameters do request_schema declara fee_bps/slippage_bps (cain#62, IS-F002): o backtest declara, a coleta não
8. R07 BLOCK REQUEST_ID_CONFLICT: request_id já emitido com outro conteúdo
9. R08 DUPLICATE DUPLICATE_REQUEST: o mesmo conteúdo já emitido no domínio
10. R09 REQUIRE_HUMAN DOMAIN_RECONCILIATION_PENDING: desfecho REQUIRES_HUMAN do domínio sem resolução
11. R10 REQUIRE_HUMAN CONTRADICTION_UNRESOLVED: estados científicos em conflito para a hipótese (nunca por maioria)
12. R15 REQUIRE_HUMAN HYPOTHESIS_NOT_ADMITTED_BY_DOMAIN: o domínio já recusou a hipótese com HYPOTHESIS_NOT_ADMITTED
13. R11 REQUIRE_HUMAN NEW_HYPOTHESIS: hipótese fora da lista proponível
14. R17 DUPLICATE EQUIVALENT_REQUEST: o mesmo experimento (o pedido sem request_id, hypothesis_id, research_id e client_ref) já rodou ou está aberto no domínio com outro ID (cain#68); tarefa recusada pelo domínio não conta
15. R12 ABSTAIN OPEN_TASK_PENDING / BUDGET_EXHAUSTED
16. R13 COOLDOWN NEGATIVE_STREAK: N resultados negativos seguidos da hipótese → K episódios sem task nova
17. R14 ALLOW

## Configuração do Stocks (FROZEN_PARAMETERS.json → decision_policy.stocks_config)

Fonte: `qualification/integration-stocks/FROZEN_PARAMETERS.json` (sha256 `40d740cb257bbc1a…`), chave `decision_policy.stocks_config`.

- fontes: stocks-predictor `61fc017256ffea815ae96bbe02b847dccdb395cc` (SHA completo): `stocks_predictor/research_admission.py`, `trials_v2.json`, `trials.json`, `config.yaml`, `EXTERNAL_INTELLIGENCE_TRIAL_READINESS_MATRIX.json`; contrato `qualification/stocks/DOMAIN_RESEARCH_CONTRACT.json` (`76fa8227dd83eb9a…`);
- tipos de pedido: BACKTEST_PIT_FACTOR, COLLECT_EXTERNAL_INTELLIGENCE;
- hipóteses que a política nunca reabre (22, H1..H22): CLOSED_JUDGED H1, H2, H3, H4, H5, H6, H8, H11, H14, H15, H16; CLOSED_EMBARGO_ORIGINAL H7, H9, H10, H12, H13; PAUSED_INCONCLUSIVE_DATA_QUALITY H17; PAUSED H18, H19; CLOSED_HISTORICAL H20; CLOSED_HISTORICAL_CONDITIONAL H21; CLOSED_REJECTED H22;
- famílias congeladas (17): low_vol_252, momentum_12_1, momentum_12_1_total_return, momentum_6_1, momentum_lowvol_intersection, near_52w_high, net_margin, quality_leverage, quality_net_margin, quality_roe, quality_roe_leverage_double_filter, quality_roe_leverage_intersection, revenue_growth_yoy, reversal_21d, turn_of_month, vol_target_sizing, volume_surge;
- famílias acrescentadas pela D-26: quality_net_margin, quality_roe_leverage_double_filter, da lista `frozen_families` de `research/scientific_state.json` em `4c82885eddab233f2b57442046875fdc2c8f0932` (sha256 `1f7eeff798a1ac37…`); nenhuma família sai;
- hipóteses propostas pela missão: stocks:QUAL-EI-COLLECTION-001, stocks:QUAL-LLM-CTRL-001, stocks:QUAL-LLM-CTRL-002, stocks:QUAL-LLM-CTRL-003, stocks:QUAL-LLM-CTRL-004, stocks:QUAL-LLM-CTRL-005, stocks:QUAL-LLM-CTRL-006, stocks:QUAL-LLM-CTRL-007, stocks:QUAL-LLM-CTRL-008, stocks:QUAL-PIT-MOM-001, stocks:QUAL-PIT-MOM-REAL-001, stocks:QUAL-PIT-MOM-REAL-002, stocks:QUAL-PIT-MOM-REAL-003;
- sobreposição de parâmetros no molde do LLM (`proposal_overlays`): stocks:QUAL-LLM-CTRL-001 {"negative_control": {"kind": "SHUFFLED_LABELS", "seed": 9001}}; stocks:QUAL-LLM-CTRL-002 {"negative_control": {"kind": "SHUFFLED_LABELS", "seed": 9002}}; stocks:QUAL-LLM-CTRL-003 {"negative_control": {"kind": "SHUFFLED_LABELS", "seed": 9003}}; stocks:QUAL-LLM-CTRL-004 {"negative_control": {"kind": "SHUFFLED_LABELS", "seed": 9004}}; stocks:QUAL-LLM-CTRL-005 {"negative_control": {"kind": "SHUFFLED_LABELS", "seed": 9005}}; stocks:QUAL-LLM-CTRL-006 {"negative_control": {"kind": "SHUFFLED_LABELS", "seed": 9006}}; stocks:QUAL-LLM-CTRL-007 {"negative_control": {"kind": "SHUFFLED_LABELS", "seed": 9007}}; stocks:QUAL-LLM-CTRL-008 {"negative_control": {"kind": "SHUFFLED_LABELS", "seed": 9008}};
- custos: fee 3 bps + slippage 15 bps (config.yaml [H1-FROZEN] execution.b3_fee_pct 0.0003 e spread_slippage_pct 0.0015 em 61fc017 (os mesmos do cost_model h1-frozen do contrato));
- prioridade máxima NORMAL; budget {"max_open_tasks": 1, "max_tasks_per_research": 64, "max_tasks_total": 512}; cooldown {"after_consecutive_negative": 3, "episodes": 2};
- ST-F007: rebalance a cada 21 pregões (universe.rebalance_every_sessions = 21, o que o handler compilado aceita), nunca 'fim de mês' (D-21)
- ST-F008: painel público só-preço com lacunas de eventos (D-21): a DecisionPolicy não lê métrica nenhuma; estados científico/econômico só entram como registro e nunca aumentam budget, prioridade ou escopo
- C22: QUALIFIED da Etapa A não é edge econômico; WATCH/WATCH_NO_CAPITAL nunca viram sinal nem capital

## Decisões do N+1 (receipt em 3 processos novos, byte a byte)

Fonte: `qualification/integration-stocks/RAW_LOGS/runtime/run36649880023/n-plus-1/frozen/SUMMARY.json` (sha256 `a178d67ed2e8e953…`).

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
| 17-collection | ALLOW | ALLOWED | R14 |
| 18-llm-shape | BLOCK | SCHEMA_INVALID | R02 |
| 19-unqualified-id | BLOCK | DOMAIN_MISMATCH | R01 |
| 20-reference-not-allowed | BLOCK | REFERENCE_NOT_ALLOWED | R06 |

## Limites do framework achados antes dos congelados (FROZEN_PARAMETERS.json → stocks_config)

- R06-custos-em-todo-pedido: policy.decide compara config.costs com parameters de todo pedido; COLLECT_EXTERNAL_INTELLIGENCE não tem fee_bps/slippage_bps ⇒ sempre BLOCK COST_MODEL_MISMATCH (n1/17-collection) Estado: ciclo 2: corrigido no cain#62 (d8b8061, IS-F002), na release única rc10; n1/17-collection passa a ALLOW
- llm-placebo-seed: cain.orchestration.llm grava parameters.placebo_seed (parâmetro do cripto); o request_schema do Stocks recusa campo extra ⇒ proposta de LLM do Stocks = BLOCK SCHEMA_INVALID (n1/18-llm-shape) Estado: ciclo 2: corrigido no cain#62 (d8b8061, IS-F003), na release única rc10: a semente do LLM só entra onde a variante do contrato a declara
- R17-llm-floor: no cain rc10 (R17 + molde por hipótese, cain#67/#68), depois do primeiro ciclo nenhuma hipótese proponível tem molde que não repita um experimento emitido: o LLM não é chamado e o piso llm_proposals da C10 não é atingível (diagnóstico local na rc10; não é gate) Decisão: dono, 2026-09-28: "Hipóteses para o LLM" (proposal_overlays no cain → rc11; C14 das três integrações)
