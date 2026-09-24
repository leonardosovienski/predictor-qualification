# TEMPORAL_INTEGRITY_REPORT — missão brasileirao (gate `TEMPORAL_INTEGRITY`)

> **Requalificação rc3 (C14 do BR-F018, 2026-09-24):** final_commit `25cdf4d` / wheel 0.3.0rc3 `403e6a02…`. Testes temporais verdes nos 4 ambientes (`temporal-suite/gate_tests_rc3.json`); corroboração com o dado real pela rc3: 7/7 checagens (resumo sem dado); gap máximo −1800 s nos 20 pedidos reais; prova do revert do `a51a68d` refeita no `25cdf4d`. Detalhes: `BR_F018_REQUALIFICATION_REPORT.md`; saída bruta: `RAW_LOGS/c14-rc3-20260924/`. O texto abaixo descreve a rc2 (Etapa A).

Regra (igual no contrato e em `FROZEN_PARAMETERS.json`):

```text
∀ informação i usada na previsão t: available_at(i) < cutoff(t)
cutoff(t) = min(kickoff(t) − decision_lead_minutes, data_cutoff)
available_at(resultado) = kickoff + 180 min   (sem kickoff: dia UTC seguinte 03:00Z)
```

## 1. Como a regra é imposta (código em `brasileirao_predictor/research_runtime/worker.py`, wheel v0.3.0rc2)

| Estado que afeta a previsão | Como fica no passado estrito |
|---|---|
| Resultados (Elo, calibração, climatologia) | um único fluxo de eventos (informação em `available_at`, decisão em `cutoff`) percorrido por `predictor_core.measurement.replay`; o handler recebe só a `PastView`; na mesma marca de tempo a decisão vem antes (desigualdade estrita); verificação defensiva dentro do handler |
| Elo | recalculado de zero em cada cutoff com a `PastView`; janela `window_years` relativa ao cutoff (não ao último jogo do banco) |
| Refit mensal (a, b, α, ρ) | `refit_at` = 1º instante UTC do mês do cutoff; só resultados com `available_at < refit_at`; memo em processo chaveado pelo fingerprint da informação usada (nada persistido) |
| Janela móvel / calibração | relativa a `refit_at` |
| Caches do banco (`current_elo`, `model_parameters`, `xg_model_parameters`) | nunca lidos (estado do momento da captura) |
| Dataset | snapshot `sqlite3.backup` com sha256, aberto `mode=ro&immutable=1`; o banco de origem nunca é lido pelo handler |
| Rótulos e odds de fechamento | só entram na avaliação, depois de todas as previsões existirem |
| Payload/resultado | `core_facts.temporal_validation`: nº de eventos, maior `available_at` usado − cutoff (< 0), caches lidos = `[]` |
| Timestamps | fuso explícito obrigatório; sem fuso → `TEMPORAL_INTEGRITY_VIOLATION` (nunca adivinha) |

## 2. Provas (suíte de conformidade pela wheel publicada, vetores congelados)

Contagens tiradas do junit bruto por `scripts/gate_tests.py` → `RAW_LOGS/temporal-suite/gate_tests_rc2_actions.json`
(e `…_windows_local.json`, ver §4).

| Teste | O que mostra |
|---|---|
| `test_every_prediction_uses_only_information_available_before_its_cutoff` | para cada previsão, o nº de informações usadas = nº de resultados com `kickoff + 180 min < cutoff`, calculado independentemente a partir dos vetores; `max_used_minus_cutoff_seconds < 0` |
| `test_handler_reads_only_the_captured_snapshot_not_the_live_database` | captura → **escrita no banco de origem** (placares +3, odds, linhas apagadas) → mesmo pedido de novo: resultado idêntico; nova captura do banco alterado: resultado diferente (o teste enxerga mudança) |
| `test_data_cutoff_after_the_snapshot_as_of_is_refused` | `data_cutoff` > `as_of` do dataset → recusa |
| BR_* e FUTURE_CANARY | relatórios próprios: `SAME_KICKOFF_REPORT.md`, `METAMORPHIC_REPORT.md`, `FUTURE_CANARY_REPORT.md`, `CACHE_STATE_REPORT.md` |

## 3. Correção de vazamento fora do circuito (BR-F004, P0)

Os motores de benchmark existentes (`evaluator.py`, `serving_evaluator.py` serving e H9,
`elo_baseline.py`) e o `backtest_walkforward.py` cortavam o histórico por `kickoff < horizonte`
(ou por data UTC): jogo em andamento entrava no ajuste com o placar final. Snapshot real: 2 de 20
refits na cadência do benchmark, 381 de 1956 com refit a cada jogo
(`RAW_LOGS/truth-map/probe_inprogress_leak_real.json`). Corrigido com a regra única
`brasileirao_predictor/pit.py`; regressões falham antes e passam depois
(`RAW_LOGS/contract-admission/BR-F004/`). Os relatórios protegidos em `reports/` foram gerados
com o motor antigo e ficam como estão (C15.1).

## 4. Dado real (Windows local, runtime D-3, wheel v0.3.0rc2)

Todo resultado real traz `max_used_minus_cutoff_seconds` negativo (−1800 s nos 20 pedidos,
`EVIDENCE_NUMBERS.json` → `metrics.real_windows_rc2_04b42c9`). Corroboração das variantes no
dado real (canário, permutação, caches envenenados, mesmo kickoff):
`RAW_LOGS/temporal-suite/real_corroboration/REAL_CORROBORATION.json`.

## 5. Limites

* A disponibilidade do resultado é uma regra conservadora (180 min), não a hora observada de
  publicação: `result_observed_at` do snapshot é carimbo de backfill (2026-09-07) para todo o histórico.
* Odds de abertura não têm horário na base histórica; não entram em resultado (CLV só como diagnóstico).
