# COLLECTION_ONLY_REPORT — missão stocks (gates STOCKS_COLLECTION_MODE, STOCKS_EXTERNAL_INTELLIGENCE_AXES)

`COLLECTION_ONLY` roda como job real do Ops (`stocks.handlers.external_collection.v1`, JobType MARKET_COLLECTION) e
chama o CLI de domínio `external collect <coletor> --source-file` (sem rede, arquivo oficial provisionado pelo
operador como objeto imutável). Persiste em staging SQLite do circuito, grava recibo e o resultado
`COLLECTION_RECORDED` com `trial_eligible = false` e `feeds = {trial, ranking, portfolio, capital} = false`.

`TRIAL_CONSUMPTION` só consome família com `readiness = READY` **e** PIT efetivo ≥ limiar **e** ligada ao modelo; com a
matriz congelada (0 famílias READY) o resultado é `NOT_READY`, sem trial, com o motivo por família.

## Pelo entrypoint instalado

* `COLLECTION_ONLY collected and never feeds a trial`: **True** (status `SUCCESS`) — `qualification/stocks/RAW_LOGS/cleanroom-final/run35949779357/stocks-runtime-linux-primary/e2e/E2E_SUMMARY.json`
* `NOT_READY family never becomes a trial (3x)`: **True** — motivos: {"B3_LENDING": "FAMILY_NOT_READY (NOT_READY, readiness='NOT_READY')", "CVM_VLMO": "FAMILY_NOT_READY (NOT_READY, readiness='NOT_READY')"}
* soak (diagnóstico): família-não-pronta ['NOT_READY', 'NOT_READY', 'NOT_READY']; coletas ['COLLECTION_RECORDED', 'COLLECTION_RECORDED', 'COLLECTION_RECORDED', 'COLLECTION_RECORDED', 'COLLECTION_RECORDED'];
  trials elegíveis = 0 — `qualification/stocks/RAW_LOGS/cleanroom-final/run35949779357/stocks-runtime-linux-primary/soak.jsonl`

## Vetores congelados

| teste | Linux | windows-latest |
|---|---|---|
| `test_contract_conformance::test_external_intelligence_not_ready_never_becomes_a_signal[matrix-20260921]` | PASS | PASS |
| `test_contract_conformance::test_external_intelligence_not_ready_never_becomes_a_signal[counterfactual-vlmo-ready]` | PASS | PASS |
| `test_contract_conformance::test_collection_only_collects_persists_and_never_feeds_a_trial` | PASS | PASS |
| `test_pit_adversarial::test_pit12_pit15_declared_strict_but_effective_historical_is_never_consumed` | PASS | PASS |

Zero consumo de dado inelegível: `consumed_families = []` e `consumed_observations = 0` em todo resultado.
