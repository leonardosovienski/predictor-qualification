# CACHE_STATE_REPORT — missão brasileirao (gate `BR_CACHE_STATE`)

Exigência: previsão histórica em processo novo ≡ previsão histórica depois de rodar uma data futura
(no mesmo processo e entre processos que compartilham estado).

## Estado que poderia vazar

| Estado | Onde | Tratamento |
|---|---|---|
| `current_elo`, `model_parameters`, `xg_model_parameters` | tabelas do snapshot, gravadas pelo cron no momento da captura (= futuro de qualquer previsão histórica) | nunca lidas pelo handler (`temporal_validation.db_caches_read = []`) |
| memo de refit | em processo (`GoalModelCache`), chave = fingerprint exato da informação usada + `refit_at` | uma data futura não serve parâmetros a uma data passada: a chave muda com a informação |
| estado do circuito compartilhado entre processos | `--state` (admission, journal, resultados, runtime do Ops) | nenhum dado de modelo persiste entre pedidos; cada pedido roda num worker novo |

## Provas (vetores congelados, pela wheel publicada)

| Teste | Mostra |
|---|---|
| `test_capture_time_caches_are_never_read` | snapshot com caches envenenados (Elo 9999/1, parâmetros absurdos) ≡ snapshot com caches limpos |
| `test_historical_prediction_is_the_same_after_running_a_future_date` | laboratório A: só o pedido histórico; laboratório B: primeiro o futuro, depois o histórico, **no mesmo `--state`** (processos novos) → iguais |
| `test_same_process_memo_does_not_leak_a_future_refit` | no mesmo processo Python: `walkforward` futuro e depois histórico com o **mesmo** memo ≡ histórico com memo novo (JSON idêntico) |

Dado real (Windows local): caches do snapshot real multiplicados/envenenados numa cópia →
`REAL_CORROBORATION.json` → `poisoned_caches_identical`.
