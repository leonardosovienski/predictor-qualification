# integration-crypto — HOSTED_CI_REPORT

Gate `HOSTED_CI` (C21): só o run de **push** cujo SHA é exatamente o commit vale. Coletado por `scripts/hosted_ci.py`. Para cada workflow vale o run mais recente naquele SHA; os JSON brutos de todos os runs estão em `RAW_LOGS/hosted-ci/`. Core e Ops não mudaram: o CI deles é o da Etapa A (HERDADO).

| Repo | Papel | Commit | Estado | Runs | Jobs não verdes |
|---|---|---|---|---|---|
| cain | baseline | `f343701937a7` | verde | [CI 36220151136](https://github.com/leonardosovienski/cain/actions/runs/36220151136) success |  |
| ecosystem-predictor | baseline | `49ffb16380d2` | VERMELHO | [Full-history security regression 36270444488](https://github.com/leonardosovienski/ecosystem-predictor/actions/runs/36270444488) success; [CI 36350241339](https://github.com/leonardosovienski/ecosystem-predictor/actions/runs/36350241339) failure | {'CI': ['quality (3.13, false)', 'quality (3.14, true)']} |
| cripto-predictor | baseline | `341d270e4d70` | verde | [CI 35925694691](https://github.com/leonardosovienski/cripto-predictor/actions/runs/35925694691) success |  |
| cain | final | `ae00017ab4a2` | verde | [Relock (diagnóstico) 36643289653](https://github.com/leonardosovienski/cain/actions/runs/36643289653) success; [CI 36643289690](https://github.com/leonardosovienski/cain/actions/runs/36643289690) success |  |
| ecosystem-predictor | final | `b0da4fd8d0c4` | verde | [CI 36635412652](https://github.com/leonardosovienski/ecosystem-predictor/actions/runs/36635412652) success; [Full-history security regression 36635412484](https://github.com/leonardosovienski/ecosystem-predictor/actions/runs/36635412484) success |  |
| cripto-predictor | final | `21f8b1822862` | verde | [CI 36642919823](https://github.com/leonardosovienski/cripto-predictor/actions/runs/36642919823) success |  |

Todos os final_commits verdes. O ecosystem-predictor da base (`49ffb16`) teve um run posterior vermelho só pelo IC-F004 (atestados de harness do cripto vencidos em 2026-09-27T02:02Z e ainda `ALIGNED`), anterior a esta missão; a reemissão genuína do harness (`61d3430`) está nos final_commits do ecosystem. Reemissão C14 pela integration-stocks: final_commits cain `deccaaa` (0.4.13rc7) e ecosystem `1304b20` (transporte 0.1.0rc4). Ciclo 2: cain `fb0e1dc` (0.4.13rc10, release única; vale o run mais recente naquele SHA, o do push da tag, e o run do push no main também está verde) e ecosystem `b11494a` (transporte 0.1.0rc5). Ciclo 3: cain `302a5c8` (0.4.13rc12; de novo vale o run da tag, e o do main também está verde). C14 da rc13: cain `960fb25` (0.4.13rc13) e ecosystem `bac1f7b` (transporte 0.1.0rc6), com o run da tag e o do main. A attestation NOT_QUALIFIED registrou o vermelho em `a19655f`.
