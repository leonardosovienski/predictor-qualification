# OPS_MAPPING_REPORT — missão brasileirao (gates `BR_OPS_REUSE`, `OPS_RUNTIME`)

> **Requalificação rc3 (C14 do BR-F018, 2026-09-24):** final_commit `25cdf4d` / wheel 0.3.0rc3 `403e6a02…`. Mesmo mecanismo e mesma wheel do Ops (4.2.2rc1); E2E real 25/25 no Linux primário do PC 2 e no Windows local (jobs file v3, `strict`, `FORECAST_GENERATION`, heartbeat, lock econômico, 1 SUCCEEDED). Detalhes: `BR_F018_REQUALIFICATION_REPORT.md`; saída bruta: `RAW_LOGS/c14-rc3-20260924/`. O texto abaixo descreve a rc2 (Etapa A).

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

## 3. Prova em runtime (Ops da wheel congelada 4.2.2rc1)

| O que | Veio do Ops? | Evidência |
|---|---|---|
| jobs file v3 aceito pelo `FileJobConfigSource` do Ops e executado por `python -m predictor_ops run` | sim (o executor só escreve o arquivo e chama o CLI) | `RAW_LOGS/ops-mapping/windows_local_real_e2e/ops-job.1.json` (comando = módulo da wheel, `provenance_mode strict`, `job_type FORECAST_GENERATION`, `capital_permission false`, `runtime.root` no estado de qualificação) |
| `ops_run_id`, estado terminal, exit code, início/fim | sim: registro terminal escrito pelo `run_job` do Ops em `events.jsonl` | `…/events.jsonl` (`SUCCEEDED`, exit 0, `run_id`); o resultado autoritativo cita o mesmo `ops_run_id` (E2E real: check `ops_run_id_matches`) |
| provenance da biblioteca | sim: `collect_provenance(strict=True)` verificou o RECORD da wheel instalada | `events.jsonl` → `library_provenance {kind: wheel, mode: strict, identity_status: VALIDATED}` |
| heartbeat | sim | `…/heartbeat.json`, `heartbeat_at` no registro |
| lock e idempotência econômica | sim: `economic_lock_id` = sha256 do `economic_key`; registro de idempotência `SUCCEEDED` | `…/idempotency_record.json`; reexecução do mesmo pedido: `SKIPPED economic_operation_already_claimed` (conformidade F05 `after_ops`) |
| lock ocupado | sim: `SKIPPED lock_not_acquired` | conformidade F14 |
| timeout | sim: o Ops mata a árvore do worker, `exit 124`, `termination.reason = timeout`, `run_status FAILED` | conformidade F11 (`test_ops_timeout_kills_the_worker_and_is_not_a_result`), Linux primário, windows-latest e Windows local |
| crash do worker | sim: estado terminal FAILED | conformidade F10 |

As mesmas checagens rodaram no E2E sintético do Linux primário e do windows-latest
(`RAW_LOGS/cleanroom-final/run35963501898/*/e2e/E2E_SUMMARY.json`: 26/26 cada) e no E2E real do
Windows local (`RAW_LOGS/windows-smoke/rc2/e2e_real/E2E_SUMMARY.json`: 25/25): `ops_single_success`,
`ops_run_id_matches`, `ops_job_type_forecast_generation`, `ops_strict_wheel_provenance`,
`ops_heartbeat_recorded`, `ops_economic_lock`, `jobs_file_v3_module_command`,
`jobs_file_strict_no_capital`.

Importar classe do Ops sem rodar o mecanismo não conta: o circuito não importa `JobConfig` nem
`run_job` (só os testes usam `EconomicJobKey`/`economic_lock_id` para calcular onde fica o lock).
