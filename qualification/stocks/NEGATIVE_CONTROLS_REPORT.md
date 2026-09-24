# NEGATIVE_CONTROLS_REPORT — missão stocks (gate STOCKS_NEGATIVE_CONTROLS)

**Estado do gate: PASS (D-16, run 35983568296; seção D-16 no fim).** A execução com a fixture sintética logo abaixo é o diagnóstico anterior à D-16. Controles negativos só significam algo sobre o dado real
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

## D-16 — controles negativos sobre o painel real (run 35983568296)

Logs brutos: `qualification/stocks/RAW_LOGS/d16/run35983568296/stocks-d16-linux-controls/science/negative_controls.jsonl`, `qualification/stocks/RAW_LOGS/d16/run35983568296/stocks-d16-linux-controls/science/NEGATIVE_CONTROLS_SUMMARY.json` (d16/d16_science.py; mesmas seeds e critérios congelados).

Referência (painel real): {"request_id": "stocks:REQ-D16-NC-REFERENCE", "control": null, "exit": 0, "status": "RESULT", "result_state": "INCONCLUSIVE", "scientific_state": "INCONCLUSIVE", "economic_state": "NO_EDGE", "excess_gross_bps": 38, "excess_gross_ci_bps": [-33, 104], "excess_net_bps": 29, "excess_net_ci_bps": [-43, 95], "periods": 49}

| controle | SUPPORTED | critério congelado |
|---|---|---|
| SHUFFLED_LABELS | 0/20 | {"supported": 0, "max_allowed": 2, "ok": true} |
| TEMPORAL_ABLATION | 0/20 | {"reference_ci_low_bps": -33, "lagged_ci_low_bps_max": -38, "rule": "reportado; nunca melhora o IC inferior do excesso bruto em mais de 50% sem investigação", "ok": true} |
| FEATURE_ABLATION | 1/20 | {"supported": 1, "max_allowed": 2, "ok": true} |
| UNIVERSE_PERTURBATION | 0/20 | {"same_state_as_reference": 20, "min_required": 16, "ok": true, "rule": "estado igual ao não perturbado em ≥ 16 de 20; senão resultado frágil (reportado)"} |

**Gate STOCKS_NEGATIVE_CONTROLS: PASS** (81 execuções).
