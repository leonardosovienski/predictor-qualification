# integration-crypto — HOSTED_CI_REPORT

Gate `HOSTED_CI` (C21): só o run de **push** cujo SHA é exatamente o commit vale. Coletado por `scripts/hosted_ci.py`. Para cada workflow vale o run mais recente naquele SHA; os JSON brutos de todos os runs estão em `RAW_LOGS/hosted-ci/`. Core e Ops não mudaram: o CI deles é o da Etapa A (HERDADO).

| Repo | Papel | Commit | Estado | Runs | Jobs não verdes |
|---|---|---|---|---|---|
| cain | baseline | `f343701937a7` | verde | [CI 36220151136](https://github.com/leonardosovienski/cain/actions/runs/36220151136) success |  |
| ecosystem-predictor | baseline | `49ffb16380d2` | VERMELHO | [Full-history security regression 36270444488](https://github.com/leonardosovienski/ecosystem-predictor/actions/runs/36270444488) success; [CI 36350241339](https://github.com/leonardosovienski/ecosystem-predictor/actions/runs/36350241339) failure | {'CI': ['quality (3.13, false)', 'quality (3.14, true)']} |
| cripto-predictor | baseline | `341d270e4d70` | verde | [CI 35925694691](https://github.com/leonardosovienski/cripto-predictor/actions/runs/35925694691) success |  |
| cain | final | `6b460afd5f19` | verde | [CI 36357069397](https://github.com/leonardosovienski/cain/actions/runs/36357069397) success |  |
| ecosystem-predictor | final | `a19655f45f84` | VERMELHO | [CI 36356527291](https://github.com/leonardosovienski/ecosystem-predictor/actions/runs/36356527291) failure | {'CI': ['quality (3.13, false)', 'quality (3.14, true)']} |
| cripto-predictor | final | `ee3d3d17de0b` | verde | [CI 36355995378](https://github.com/leonardosovienski/cripto-predictor/actions/runs/36355995378) success |  |

**ecosystem-predictor vermelho só pelo IC-F004.** O job `quality` falha em `test_real_registry_has_current_hash_verified_target_harness`: dois atestados de harness do cripto venceram em 2026-09-27T02:02Z e continuam `ALIGNED`. É anterior a esta missão. No commit base, o run de push do main de 2026-09-26 foi verde; um run posterior no mesmo SHA (tag do protocolo, 2026-09-27T21:02Z) já saiu vermelho. Depende de decisão do dono (FINDINGS IC-F004).
