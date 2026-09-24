# PIT_ADVERSARIAL_REPORT — missão stocks (gates STOCKS_PIT_ADVERSARIAL, TEMPORAL_INTEGRITY, FUTURE_CANARY)

Casos congelados em `FROZEN_PARAMETERS.pit_adversarial_vectors` antes da execução; cada caso quebra de propósito o
painel sintético e é conferido na visão PIT que o handler de produção usa, pela wheel publicada, no Linux primário e no
windows-latest (`qualification/stocks/RAW_LOGS/cleanroom-final/run35954279991/stocks-runtime-linux-primary/conformance.junit.xml`, `qualification/stocks/RAW_LOGS/cleanroom-final/run35954279991/stocks-runtime-windows-latest/conformance.junit.xml`).
Uma violação bastaria para FAIL.

| caso | ataque | esperado | teste(s) | Linux + windows |
|---|---|---|---|---|
| PIT-01 | constituinte do futuro (listing_available_at > t) | fora do universo em t | `test_pit01_future_constituent_is_absent_until_its_listing_is_known` | PASS |
| PIT-02 | ticker do futuro (evento de ticker efetivo ≤ t, available_at > t) | em t vale o ticker anterior; identidade (security_id) inalterada | `test_pit02_future_ticker_does_not_relabel_before_it_is_known` | PASS |
| PIT-03 | delistado omitido | presente no universo enquanto existia e a saída não era conhecida; retorno até a última barra e depois caixa | `test_pit03_delisted_security_is_present_while_it_existed` | PASS |
| PIT-04 | IPO antes da listagem (barras antes de listed_on) | barras anteriores à listagem ignoradas; fora do universo antes da listagem conhecida | `test_pit04_bars_before_the_listing_are_ignored` | PASS |
| PIT-05 | CNPJ/ticker futuro (evento de identidade com available_at > t) | em t vale a identidade anterior | `test_pit05_pit06_future_cnpj_document_is_ignored_until_available` | PASS |
| PIT-06 | documento CVM (identidade) com available_at posterior | ignorado até available_at | `test_pit05_pit06_future_cnpj_document_is_ignored_until_available` | PASS |
| PIT-07 | entrega atrasada (barra da sessão d disponível só em d+k) | não usada em t < d+k | `test_pit07_pit08_late_delivery_and_backfill_are_invisible_before_they_arrive` | PASS |
| PIT-08 | backfill (barra antiga inserida depois) | não usada antes de available_at | `test_pit07_pit08_late_delivery_and_backfill_are_invisible_before_they_arrive` | PASS |
| PIT-09 | republicação (mesma sessão, nova revisão) | em t vale a última revisão com available_at ≤ t | `test_pit09_pit10_republication_uses_the_revision_known_at_decision` | PASS |
| PIT-10 | revisão da fonte (valor corrigido depois) | decisão em t usa o valor conhecido em t | `test_pit09_pit10_republication_uses_the_revision_known_at_decision` | PASS |
| PIT-11 | first_seen/available_at corrompido (available_at antes do fato, ausente ou inválido) | TEMPORAL_INTEGRITY_VIOLATION, sem trial | `test_pit11_corrupted_availability_is_a_temporal_violation[<lambda>0]`, `test_pit11_corrupted_availability_is_a_temporal_violation[<lambda>1]`, `test_pit11_corrupted_availability_is_a_temporal_violation[<lambda>2]`, `test_pit11_corrupted_availability_is_a_temporal_violation[<lambda>3]` | PASS |
| PIT-12 | HISTORICAL_ONLY promovido a PIT_STRICT (declarado × efetivo) | vale o estado efetivo; nunca consumido para trial | `test_pit12_pit15_declared_strict_but_effective_historical_is_never_consumed` | PASS |
| PIT-13 | registro oficial duplicado | idêntico: deduplicado sem efeito; divergente: INCONCLUSIVE_DATA_QUALITY | `test_pit13_duplicate_official_record_identical_collapses_divergent_fails` | PASS |
| PIT-14 | conflito de identidade (mesmo security_id com dois CNPJ no mesmo instante; mesmo ticker em dois security_id) | INCONCLUSIVE_DATA_QUALITY | `test_pit14_identity_conflicts_are_data_quality_problems[one_ticker_two_securities]`, `test_pit14_identity_conflicts_are_data_quality_problems[two_issuers_same_instant]`, `test_pit14_identity_conflicts_are_data_quality_problems[unknown_security]` | PASS |
| PIT-15 | caso obrigatório: família com PIT_STRICT declarado e HISTORICAL_ONLY efetivo na matriz | pipeline usa HISTORICAL_ONLY; TRIAL_CONSUMPTION → NOT_READY | `test_pit12_pit15_declared_strict_but_effective_historical_is_never_consumed` | PASS |

## Integridade temporal pelo circuito inteiro (entrypoint)

| teste | Linux | windows-latest |
|---|---|---|
| `test_contract_conformance::test_future_canary_fails_closed_and_never_leaks` | PASS | PASS |
| `test_contract_conformance::test_temporal_integrity_as_of_mismatch_fails_closed` | PASS | PASS |
| `test_pit_adversarial::test_data_quality_problem_is_an_inconclusive_result_through_the_entrypoint` | PASS | PASS |
| `test_pit_adversarial::test_decision_never_uses_data_available_after_it` | PASS | PASS |

A desigualdade PIT é imposta em dois níveis: `research_pit.Panel` (cada decisão só vê `available_at` ≤ decisão) e
`predictor_core.measurement.replay` no worker (`LookaheadError` se qualquer registro do snapshot estiver disponível
depois do `as_of`; decisões monotônicas; `max_available_used` ≤ `decision_at` em cada rebalance).
Canário `FUTURE_CANARY_STOCKS_001`: dataset com o canário → `TEMPORAL_INTEGRITY_VIOLATION` (exit 4), sem efeito, trial
nem resultado; o token não aparece em efeito, trial, resultado, `results.sqlite` nem outcomes de pedidos legítimos.
