# OPS_MAPPING_REPORT — missão brasileirao (gates `BR_OPS_REUSE`, `OPS_RUNTIME`)

## 1. Mesmo mecanismo da sombra

| | Sombra (`brasileirao_scripts/sombra_diaria.py`) | Pesquisa (`brasileirao_predictor/research_runtime/execution.py`) |
|---|---|---|
| Como chama o Ops | escreve um jobs file e roda `sys.executable -m predictor_ops run --job <id> --config <arquivo>` em processo filho | **o mesmo**: `_run_ops` escreve o jobs file e roda `[sys.executable, "-m", "predictor_ops", "run", "--job", id, "--config", arquivo]` (`subprocess.run`, `CREATE_NO_WINDOW` no Windows) |
| Validação do jobs file | pelo Ops (`FileJobConfigSource` → `JobsFile`, pydantic) | a mesma (o executor não importa `JobConfig`/`run_job`) |
| Executor paralelo | não | não: nenhum `run_job` importado no circuito (`grep run_job` em `research_runtime/` = 0) |
| Leitura do desfecho | exit code | exit code do CLI + registro terminal do próprio Ops em `<runtime.root>/<job_id>/events.jsonl` (run_id, estado, terminação, provenance) |

## 2. Campo a campo (jobs file `schema_version "3"`)

| Campo | Sombra | Pesquisa | Por quê |
|---|---|---|---|
| `schema_version` | `"3"` | `"3"` | igual |
| `id` | nome da tarefa (`brasileirao-sombra-manha`) | `brasileirao-research-<logical_hash[:24]>` (determinístico) | uma identidade por experimento lógico |
| `command` | `[sys.executable, -X, utf8, -m, brasileirao_scripts.sombra_diaria_payload]` | `[sys.executable, -m, brasileirao_predictor.research_runtime.worker, --request, --effect, --trial-registry]` | módulo da wheel; nunca caminho de checkout; escolhido pelo executor, não pelo pedido |
| `cwd` | padrão (herda) | diretório do experimento | artefatos do job ficam no experimento |
| `environment` | padrão | `{BRASILEIRAO_RESEARCH_FAULT: ""}` | a injeção de falha do processo pai nunca atinge o worker |
| `timeout_seconds` | padrão 3600 | `resource_budget.timeout_seconds` da policy (vetores 1800; teste de timeout 3) | orçamento decidido pela admission |
| `heartbeat_interval_seconds` | padrão 30 | 1 | detecção rápida de lock perdido e heartbeat observável |
| `max_output_bytes` | padrão 10 MiB | 1 MiB | o worker imprime uma linha |
| `expected_artifact` | nenhum | `<experimento>/domain-effect.json` | SUCCEEDED sem efeito vira PARTIAL no próprio Ops |
| `provenance_mode` | padrão `permissive` | `strict` | a wheel do Ops tem de ser verificável (RECORD); editable ou sujo = CONFIGURATION_ERROR |
| `provenance` | metadados do consumidor | domínio, request_id, request_content_hash, admission_id, logical_hash, identidade da wheel do brasileirao-predictor (versão + sha256 do RECORD) | cadeia pedido → job |
| `config_version` | — | `brasileirao-research-ops/1` | versão do mapeamento |
| `input_reference` / `output_reference` | — | sha256 do worker-request.json / caminho do efeito | liga o job às entradas e à saída |
| `retry_count` | 0 | nº da tentativa − 1 | tentativas registradas pelo Ops |
| `scientific_state` | — | `RESEARCH_FORECAST_EVALUATION` | rótulo opaco |
| `job_type` | omitido | `FORECAST_GENERATION` | o job gera previsões e as avalia; não decide sombra e não executa; **nunca** `EXECUTION` |
| `economic_key` | — | `{domain: brasileirao, event_id: <experiment_id>, market: <alvo>, decision_stage: research_forecast, logical_time: <data_cutoff>}` | idempotência do Ops: um SUCCEEDED por experimento; reexecução devolve `SKIPPED economic_operation_already_claimed` |
| `capital_permission` | padrão false | `false` explícito | o modelo do Ops recusa true fora de EXECUTION |
| `exit_statuses` | padrão `{0: SUCCEEDED, 2: PARTIAL}` | `{0: SUCCEEDED}` | só sucesso total conta; recusa do worker (4/5/6) = FAILED + worker-refusal.json |
| `runtime.root` | `runtime_root()/operations` | `<state>/x/o` | dentro do diretório de qualificação |

O job de pesquisa é **pelo menos tão rígido** quanto a sombra em todos os campos (mais rígido em
`provenance_mode`, `expected_artifact`, `economic_key`, `job_type` e `exit_statuses`).

## 3. Prova em runtime

Evidência: preenchida na fase `e2e`/`idempotency-failure` (ver §4).
