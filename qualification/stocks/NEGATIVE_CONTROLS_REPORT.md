# NEGATIVE_CONTROLS_REPORT — missão stocks (gate STOCKS_NEGATIVE_CONTROLS)

**Estado do gate: NOT_RUN — BLOCKED: D-16 pendente.** Controles negativos só significam algo sobre o dado real
(`FROZEN_PARAMETERS.d16_dependency_rule`). A execução abaixo, sobre a fixture sintética congelada, é **diagnóstico**:
prova que os controles estão implementados no handler de produção e rodam pelo entrypoint instalado.

Seeds, critérios e aplicabilidade congelados antes (`FROZEN_PARAMETERS.negative_controls`). Log bruto por execução:
`qualification/stocks/RAW_LOGS/cleanroom-final/run35954279991/stocks-runtime-linux-primary/science/negative_controls.jsonl`; resumo `qualification/stocks/RAW_LOGS/cleanroom-final/run35954279991/stocks-runtime-linux-primary/science/NEGATIVE_CONTROLS_SUMMARY.json`.

Referência (painel sintético `positive`, tendência plantada de propósito): científico SUPPORTED, econômico
WATCH, excesso bruto 427 bps/período, IC95 bruto [305, 551],
IC95 líquido [291, 541], 29 períodos. **Isto não é métrica econômica:** a fixture tem
edge plantado para exercitar o caminho SUPPORTED.

| controle | SUPPORTED | critério congelado |
|---|---|---|
| SHUFFLED_LABELS | 0/20 | {"supported": 0, "max_allowed": 2, "ok": true} |
| TEMPORAL_ABLATION | 20/20 | {"reference_ci_low_bps": 305, "lagged_ci_low_bps_max": 348, "ok": true} |
| FEATURE_ABLATION | 2/20 | {"supported": 2, "max_allowed": 2, "ok": true} |
| UNIVERSE_PERTURBATION | 20/20 | {"same_state_as_reference": 20, "min_required": 16, "ok": true} |

Leitura: labels embaralhados nunca SUPPORTED (0/20); ranking aleatório no limite congelado (2/20). A ablação
temporal (sinal defasado 1 rebalance) continua SUPPORTED porque a fixture tem tendência persistente — é esperado na
fixture e seria investigado no dado real. A perturbação de universo mantém o estado em 20/20.
