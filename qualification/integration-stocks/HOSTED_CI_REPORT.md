# integration-stocks — HOSTED_CI_REPORT

Gate `HOSTED_CI` (C21; prompt da sessão 9.3: só o run de **push** cujo SHA é exatamente o commit vale). Coletado por `scripts/hosted_ci.py` (`qualification/integration-stocks/RAW_LOGS/hosted-ci/final-rc15/HOSTED_CI_SUMMARY.json` (sha256 `9950921cebc09f65…`)). Core e Ops não mudaram (CI da Etapa A, HERDADO).

| Repo | Papel | Commit | Estado | Runs de push | Jobs não verdes |
|---|---|---|---|---|---|
| cain | baseline | `10744a9f1496` | verde | [CI 36359969690](https://github.com/leonardosovienski/cain/actions/runs/36359969690) success |  |
| ecosystem-predictor | baseline | `61f3ac421604` | verde | [CI 36359189276](https://github.com/leonardosovienski/ecosystem-predictor/actions/runs/36359189276) success |  |
| stocks-predictor | baseline | `61fc017256ff` | SEM PUSH VERDE | nenhum run de push |  |
| cain | final | `ae00017ab4a2` | verde | [Relock (diagnóstico) 36643289653](https://github.com/leonardosovienski/cain/actions/runs/36643289653) success; [CI 36643289690](https://github.com/leonardosovienski/cain/actions/runs/36643289690) success |  |
| ecosystem-predictor | final | `b0da4fd8d0c4` | verde | [CI 36635412652](https://github.com/leonardosovienski/ecosystem-predictor/actions/runs/36635412652) success; [Full-history security regression 36635412484](https://github.com/leonardosovienski/ecosystem-predictor/actions/runs/36635412484) success |  |
| stocks-predictor | final | `6f857b232eaa` | SEM PUSH VERDE | nenhum run de push |  |

## stocks-predictor

O `ci.yml` do stocks-predictor dispara `push` só em `main` (intocável pela D-24 (4c)): nem a base `61fc017` nem o final_commit `6f857b2` têm run de push (IS-F004). No SHA exato do final_commit há o run `workflow_dispatch` [36363108348](https://github.com/leonardosovienski/stocks-predictor/actions/runs/36363108348): failure — secrets=failure, Quality / Python 3.14=success, Quality / Python 3.13=success (`qualification/integration-stocks/RAW_LOGS/hosted-ci/stocks-predictor_6f857b2_run36363108348.json` (sha256 `43f10ba3a7b5565a…`)). O job `secrets` falha por um falso positivo pré-existente fora desta branch (`qualification/integration-stocks/RAW_LOGS/hosted-ci/stocks-predictor_6f857b2_run36363108348_secrets_job.log` (sha256 `6e3bf10e3799a223…`); IS-F005). Decisão do dono pendente; o gate fica `NOT_RUN` com BLOCKED e não é relaxado pelo agente.
