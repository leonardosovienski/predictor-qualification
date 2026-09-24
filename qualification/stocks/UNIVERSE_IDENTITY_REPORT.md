# UNIVERSE_IDENTITY_REPORT — missão stocks (gate STOCKS_UNIVERSE_IDENTITY)

Código: `stocks_predictor/research_pit.py` (`Panel.universe`), chamado pelo worker do handler
`stocks.handlers.pit_factor_backtest.v1`. Identidade = `security_id`; ticker e CNPJ são rótulos com validade no tempo;
dedup por emissor usa o CNPJ conhecido na decisão (não o prefixo de 4 letras do ticker).

## Pelo entrypoint instalado (wheel publicada)

`universe identical across three fresh processes/state roots`: **True** (30 rebalances; mesmo pedido em 3 raízes de estado novas,
3 processos) — `qualification/stocks/RAW_LOGS/cleanroom-final/run35949779357/stocks-runtime-linux-primary/e2e/E2E_SUMMARY.json`; idem no windows-latest
(`qualification/stocks/RAW_LOGS/cleanroom-final/run35949779357/stocks-runtime-windows-latest/e2e/E2E_SUMMARY.json`).

## Vetores congelados (suíte de conformidade pela wheel)

| teste | Linux | windows-latest |
|---|---|---|
| `test_pit_adversarial::test_pit03_delisted_security_is_present_while_it_existed` | PASS | PASS |
| `test_pit_adversarial::test_universe_is_deterministic_across_three_fresh_processes` | PASS | PASS |
| `test_pit_adversarial::test_universe_changes_only_through_events_available_at_decision` | PASS | PASS |
| `test_pit_adversarial::test_ticker_and_cnpj_changes_preserve_security_identity` | PASS | PASS |

Propriedades: mesma entrada + mesmo `as_of` = mesma lista e mesmo hash; entradas e saídas só por eventos com
`available_at` ≤ decisão; deslistado presente enquanto existia e sua saída não era conhecida; troca de ticker e de CNPJ
preserva a identidade. Vetores sintéticos (prompt §4); com dado real = D-16.
