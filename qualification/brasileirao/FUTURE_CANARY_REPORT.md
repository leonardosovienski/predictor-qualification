# FUTURE_CANARY_REPORT — missão brasileirao (gates `FUTURE_CANARY`, `BR_FUTURE_INJECTION`)

## Canário `FUTURE_CANARY_BR_001`

Vetor congelado (`tests/conformance/fixtures.py`, `canary=True`): dois jogos **depois** do
`data_cutoff` (2023-10-20 e 2023-10-27; cutoff 2023-10-01; as_of do snapshot 2024-01-01) com o time
`FUTURE_CANARY_BR_001` e placares 17×0 / 0×17 contra times reais; os caches do snapshot também
recebem o canário (`current_elo` do canário e `xg_model_parameters` com o token).

Procura (`test_future_canary_never_reaches_any_artifact`):

1. **transformado** (número derivado, agregado): o resultado com canário é idêntico ao resultado sem
   canário (previsões, Elo, parâmetros do refit, climatologia, métricas, IC, economia);
2. **literal**: o token não aparece em nenhum arquivo `.json`, `.jsonl` ou `.sqlite` escrito pelo
   circuito (efeitos, trials do Core, resultados, outcomes, jobs files, eventos e idempotência do Ops,
   admission, journal);
3. auditoria: `excluded_after_data_cutoff` aumenta (as linhas existem no snapshot e ficam fora).

Soak (Linux, diagnóstico): 5 ciclos com canário iguais à referência sem canário.
Dado real (Windows local): canário inserido numa cópia do snapshot real depois do cutoff
(`REAL_CORROBORATION.json` → `canary_identical`, `canary_token_absent`).

Apareceu antes do cutoff = P0. Não apareceu.

## Injeção de dado impossível (`BR_FUTURE_INJECTION`)

| Vetor | Resultado exigido |
|---|---|
| placar final de jogo com kickoff **depois** do `as_of` do snapshot (`future_result=True`) | `TEMPORAL_INTEGRITY_VIOLATION` (exit 4) pelo caminho real entrypoint → Ops → handler; nenhum resultado (`show` = NOT_FOUND) |
| jogo com kickoff sem fuso | `TEMPORAL_INTEGRITY_VIOLATION`; nunca adivinhado (`BR_TIMEZONE_INTEGRITY`) |
| `data_cutoff` depois do `as_of` | recusa `DATA_CUTOFF_AFTER_DATASET_AS_OF` |
| jogo que começou antes do cutoff mas não terminou | excluído (`available_at` ≥ cutoff) — `SAME_KICKOFF_REPORT.md` |

O handler nunca usa um dado "porque está no banco": cada linha tem `available_at` e passa pelo
`replay` do Core.
