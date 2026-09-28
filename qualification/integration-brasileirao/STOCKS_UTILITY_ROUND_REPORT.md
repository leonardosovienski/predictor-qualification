# Rodada independente CAIN × Stocks — cain 0.4.13rc13 + transporte 0.1.0rc6

> Gerado por `scripts/reissue_rc13.py utility-report` a partir de `RAW_LOGS/runtime/run-20260928T183300Z-br13/stocks-utility-round/SUMMARY.json`
> (sha256 `20326a59d57a127a0ee1b10f91af5cc5f641a9eab28e2b7b7e5c5342aa9d5f5b`). Não é gate da integration-brasileirao. Pedido do dono no chat desta sessão; harness próprio
> (`scripts/stocks_utility_round.py`); critério de aceite combinado com a sessão STOCKS; PC 2 (WSL), modelo local
> phi4-mini; findings do scientific_state do main do stocks fixado em 4c82885 (D-26).

**Resultado: 11 de 11 critérios.**

| Critério | Resultado |
|---|---|
| seed: real backtest ALLOW and executed | PASS |
| 5: guards 12/12 | PASS |
| 5: canary token absent from the CAIN memory | PASS |
| 1: every ALLOW task is a distinct experiment | PASS |
| 2: no LLM proposal reuses the request of a task the domain refused | PASS |
| 3: every LLM proposal has the request type the configuration fixes for its hypothesis | PASS |
| 4: the loop exhausts the LLM-only hypotheses and stops at NO_ELIGIBLE_HYPOTHESIS | PASS |
| 6: memory = authoritative source (payload == show re-read; fact states == payload states) | PASS |
| 7: `momentum 12-1` recognized as closed by findings check | PASS |
| 8: honest report publishable; A0, B, C and E blocked | PASS |
| 9: refusal_mismatches flags every false refusal claim that appeared | PASS |

## Laço com o modelo (10 chamadas)

| Chamada | Hipótese | Tipo de pedido | Decisão | Domínio | Erro |
|---|---|---|---|---|---|
| 1 | stocks:QUAL-LLM-CTRL-001 | BACKTEST_PIT_FACTOR | ALLOW | RESULT |  |
| 2 | stocks:QUAL-LLM-CTRL-002 | BACKTEST_PIT_FACTOR | ALLOW | RESULT |  |
| 3 | stocks:QUAL-LLM-CTRL-003 | BACKTEST_PIT_FACTOR | ALLOW | RESULT |  |
| 4 | stocks:QUAL-LLM-CTRL-004 | BACKTEST_PIT_FACTOR | ALLOW | RESULT |  |
| 5 | stocks:QUAL-LLM-CTRL-005 | BACKTEST_PIT_FACTOR | ALLOW | RESULT |  |
| 6 | stocks:QUAL-LLM-CTRL-006 | BACKTEST_PIT_FACTOR | ALLOW | RESULT |  |
| 7 | stocks:QUAL-LLM-CTRL-008 | BACKTEST_PIT_FACTOR | ALLOW | RESULT |  |
| 8 | stocks:QUAL-LLM-CTRL-007 | BACKTEST_PIT_FACTOR | ALLOW | RESULT |  |
| 9 | — | — | — | — | NO_ELIGIBLE_HYPOTHESIS: the policy holds every proposable hy |
| 10 | — | — | — | — | NO_ELIGIBLE_HYPOTHESIS: the policy holds every proposable hy |

## Guardas (12)

| Caso | Decisão (regra) | Domínio | Resultado |
|---|---|---|---|
| 01 H1 closed | BLOCK HYPOTHESIS_CLOSED (R05) | —  | PASS |
| 02 family momentum_12_1 | BLOCK HYPOTHESIS_CLOSED (R05) | —  | PASS |
| 03 new hypothesis | REQUIRE_HUMAN NEW_HYPOTHESIS (R11) | —  | PASS |
| 04 EI collection | ALLOW ALLOWED (R14) | RESULT COLLECTION_RECORDED | PASS |
| 05 exact duplicate of the seed | DUPLICATE DUPLICATE_REQUEST (R08) | —  | PASS |
| 06 same experiment, other ID (REAL-002) | DUPLICATE EQUIVALENT_REQUEST (R17) | —  | PASS |
| 07 QUAL-PIT-MOM-001 negative control 701 | ALLOW ALLOWED (R14) | REJECTED  | PASS |
| 08 the same hypothesis again, seed 702 | REQUIRE_HUMAN HYPOTHESIS_NOT_ADMITTED_BY_DOMAIN (R15) | —  | PASS |
| 09 future canary | ALLOW ALLOWED (R14) | TEMPORAL_INTEGRITY_VIOLATION  | PASS |
| 10 crypto proposal | BLOCK DOMAIN_MISMATCH (R01) | —  | PASS |
| 11 cost mismatch | BLOCK COST_MODEL_MISMATCH (R06) | —  | PASS |
| 12 priority above cap | BLOCK PRIORITY_ABOVE_CAP (R06) | —  | PASS |

## Linter de relatório

| Relatório | Esperado | Obtido | Violações |
|---|---|---|---|
| A | publishable | publishable | — |
| A0 | blocked | blocked | NOT_IN_CITED_SOURCE, NOT_IN_CITED_SOURCE |
| B | blocked | blocked | NO_PROVENANCE |
| C | blocked | blocked | NOT_IN_CITED_SOURCE |
| E | blocked | blocked | NO_PROVENANCE |

Limites declarados, não decididos: paráfrase sem nome da hipótese (o embedding só lista candidatos). O IS-F009 (envelope
falso do consumidor perdedor) foi resolvido pelo transporte 0.1.0rc6 (um consumidor por domínio): no teste conjunto
deste run, a disputa do stocks deu 20/20.
