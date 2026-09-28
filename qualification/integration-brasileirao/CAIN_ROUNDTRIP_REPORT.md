# Roundtrip CAIN ↔ Brasileirão (E2E, CAIN_INGESTION, PROVENANCE, FUTURE_CANARY, CROSS_DOMAIN_ISOLATION)

> Gerado por `scripts/render_reports.py` a partir de `EVIDENCE_NUMBERS.json` (C20). Runtime suportado no PC 2 (owner_linux), run `run-20260928T145525Z-br12`.

- E2E no Linux primário: 79 passaram, 0 falharam — `qualification/integration-brasileirao/RAW_LOGS/runtime/run-20260928T145525Z-br12/e2e/SUMMARY.json` (sha256 `fd4d64951ada…`); decisões: ALLOW, ALLOW, ALLOW, ALLOW, DUPLICATE, BLOCK, BLOCK, BLOCK, BLOCK, ALLOW
- E2E no Windows secundário (PC 2): 79 passaram, 0 falharam — `qualification/integration-brasileirao/RAW_LOGS/runtime/run-20260928T145525Z-br12-windows/e2e/SUMMARY.json` (sha256 `6f9d7b59873e…`)
- Isolamento, IDs e contradição: 30 passaram, 0 falharam — `qualification/integration-brasileirao/RAW_LOGS/runtime/run-20260928T145525Z-br12/isolation/SUMMARY.json` (sha256 `3d78a1959d34…`); contradição: 9 passaram, 0 falharam — `qualification/integration-brasileirao/RAW_LOGS/runtime/run-20260928T145525Z-br12/isolation/contradiction/SUMMARY.json` (sha256 `e3ec926a4df6…`)
- Matriz de falhas F01–F16: F01 3/3, F02 3/3, F03 3/3, F04 3/3, F05 4/4, F06 2/2, F07 2/2, F08 10/10, F09 2/2, F10 3/3, F11 3/3, F12 3/3, F13 6/6, F14 3/3, F15 4/4, F16 11/11
  — `qualification/integration-brasileirao/RAW_LOGS/runtime/run-20260928T145525Z-br12/failure-matrix/FAILURE_MATRIX_RESULTS.json` (sha256 `37ed26931a28…`)
- Memória do CAIN: só referências, estados e hashes (nenhuma linha do dado real; no_data_rows_check em toda saída
  pública de cada cenário).
