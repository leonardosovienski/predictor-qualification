# HOSTED_CI_REPORT — missão brasileirao (gate `HOSTED_CI`, C21)

Workflows de `push`/`pull_request` verdes no GitHub Actions nos commits do baseline e nos
`final_commits`, instalando com `uv sync --locked`. Nenhum job pulado (todos `success`).

## brasileirao-predictor

| Commit | Workflow | Run | Evento | Jobs | Evidência |
|---|---|---|---|---|---|
| `e14f339` (baseline) | CI Pipeline (`ci.yml`) | [35824710652](https://github.com/leonardosovienski/brasileirao-predictor/actions/runs/35824710652) | push main | Python 3.13, 3.14, .NET 10, Compose: success | `RAW_LOGS/baseline/hosted_ci/run_35824710652.json`, `.log` |
| `e14f339` (baseline) | Scoped synthetic publication validation | [35824710697](https://github.com/leonardosovienski/brasileirao-predictor/actions/runs/35824710697) | push main | 4/4 success | `RAW_LOGS/baseline/hosted_ci/run_35824710697.json` |
| `04b42c9` (final) | CI Pipeline | [35965123063](https://github.com/leonardosovienski/brasileirao-predictor/actions/runs/35965123063) | pull_request #78 | 4/4 success; pytest 2305 passed, 2 skipped (3.13 e 3.14), integração 30 passed | `RAW_LOGS/hosted-ci/br_final_35965123063.json`, `.log` |
| `04b42c9` (final) | Scoped synthetic publication validation | [35963505773](https://github.com/leonardosovienski/brasileirao-predictor/actions/runs/35963505773) | push (branch `publication-validation-brasileirao-qualification`, gatilho do próprio workflow) | 4/4 success | `RAW_LOGS/hosted-ci/br_final_35963505773.json`, `.log` |

Os 2 `skipped` do pytest: `test_run_passive_process_tree` (só Windows, por desenho) e
`test_registro_conforma_ao_schema_do_core` (atestado de poder vencido — BR-F010, P2, arquivo protegido).
O pyright do CI cobre `brasileirao_predictor/research_runtime` (código novo): 0 erros.

## core-predictor e predictor-ops (congelados)

| Repo | Commit | Run | Resultado | Evidência |
|---|---|---|---|---|
| core-predictor | `5a08415` (baseline = final) | [35823003554](https://github.com/leonardosovienski/core-predictor/actions/runs/35823003554) | success (4 jobs) | `RAW_LOGS/baseline/hosted_ci/run_35823003554.json` |
| predictor-ops | `9831b0d` (release 4.2.2rc1 = final) | [35905678198](https://github.com/leonardosovienski/predictor-ops/actions/runs/35905678198) (push da tag) e [35905393899](https://github.com/leonardosovienski/predictor-ops/actions/runs/35905393899) (PR #26) | success (ubuntu 3.13/3.14, windows-latest 3.13, container) | `RAW_LOGS/baseline/hosted_ci/run_35905678198.json`, `run_35905393899.json` |
| predictor-ops | `31d3939` (main, árvore = 9831b0d) | [35936257309](https://github.com/leonardosovienski/predictor-ops/actions/runs/35936257309) | success | `RAW_LOGS/baseline/hosted_ci/run_35936257309.json` |

## Runtime da qualificação (repo de evidência)

`brasileirao-runtime.yml` (Linux primário + windows-latest, só wheels publicadas):
run [35963501898](https://github.com/leonardosovienski/predictor-qualification/actions/runs/35963501898)
sobre v0.3.0rc2 — `RAW_LOGS/cleanroom-final/run35963501898/` (ver `CLEANROOM_REPORT.md` §2).
