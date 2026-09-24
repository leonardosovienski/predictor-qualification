# SAME_KICKOFF_REPORT — missão brasileirao (gate `BR_SAME_KICKOFF_ISOLATION`)

> **Requalificação rc3 (C14 do BR-F018, 2026-09-24):** final_commit `25cdf4d` / wheel 0.3.0rc3 `403e6a02…`. Teste verde nos 4 ambientes; soak com o dado real: 5 ciclos de mesmo kickoff com a mesma informação; corroboração real: jogo irmão idêntico e mudança vista só depois. Detalhes: `BR_F018_REQUALIFICATION_REPORT.md`; saída bruta: `RAW_LOGS/c14-rc3-20260924/`. O texto abaixo descreve a rc2 (Etapa A).

Pergunta: o resultado do jogo A afeta a previsão do jogo B que começa no mesmo instante — por dado
explícito ou por estado (Elo, refit, climatologia, cache)?

## Mecanismo

* O resultado de A fica disponível em `kickoff + 180 min`; o cutoff de B é `kickoff − 60 min`. No
  fluxo do `replay` do Core, a informação de A vem depois da decisão de B.
* Elo recalculado de zero por cutoff com a `PastView`; refit mensal com `available_at < refit_at`;
  climatologia com a mesma `PastView`; nenhum cache persistente entre previsões.
* O mesmo vale para o jogo **ainda em andamento** de kickoff anterior (21:30Z × 23:00Z na mesma
  rodada): no cutoff 22:00Z o jogo das 21:30Z não terminou.

## Provas (vetores congelados, pela wheel publicada)

| Teste | Vetor | Resultado exigido |
|---|---|---|
| `test_result_of_game_a_does_not_affect_game_b_with_the_same_kickoff` | 2023 rodada 12, slots 0 e 1 (mesmo kickoff 19:00Z); o placar de A vira 9×0 numa nova captura | previsão de B byte-idêntica (inclui o fingerprint da informação); um jogo da rodada seguinte **muda** (o teste enxerga o vazamento se houvesse) |
| `test_match_still_in_progress_is_not_information_for_the_next_kickoff` | slots 21:30Z e 23:00Z da mesma rodada; o placar do jogo das 21:30Z vira 9×0 | previsão do jogo das 23:00Z byte-idêntica; rodada seguinte muda |
| soak (Linux, diagnóstico) | 5 ciclos com pares de mesmo kickoff listados | os dois jogos do par usam exatamente o mesmo conjunto de informação |

Contagens: `RAW_LOGS/temporal-suite/gate_tests_rc2_actions.json` (Linux primário e windows-latest) e
`…_windows_local.json`. Dado real: `REAL_CORROBORATION.json` (`same_kickoff_sibling_identical`,
`same_kickoff_change_seen_later`).
