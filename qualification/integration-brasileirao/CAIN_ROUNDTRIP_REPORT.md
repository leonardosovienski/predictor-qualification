# Roundtrip CAIN ↔ Brasileirão (E2E, CAIN_INGESTION, PROVENANCE, FUTURE_CANARY, CROSS_DOMAIN_ISOLATION)

> Gerado por `scripts/render_reports.py` a partir de `EVIDENCE_NUMBERS.json` (C20). Runtime suportado no PC 2 (owner_linux), run `run-20260928T183300Z-br13`.

- E2E no Linux primário: 79 passaram, 0 falharam — `qualification/integration-brasileirao/RAW_LOGS/runtime/run-20260928T183300Z-br13/e2e/SUMMARY.json` (sha256 `48ad99e81eab…`); decisões: ALLOW, ALLOW, ALLOW, ALLOW, DUPLICATE, BLOCK, BLOCK, BLOCK, BLOCK, ALLOW
- E2E no Windows secundário (PC 2): 79 passaram, 0 falharam — `qualification/integration-brasileirao/RAW_LOGS/runtime/run-20260928T183300Z-br13-windows/e2e/SUMMARY.json` (sha256 `4a1984ac5599…`)
- Isolamento, IDs e contradição: 30 passaram, 0 falharam — `qualification/integration-brasileirao/RAW_LOGS/runtime/run-20260928T183300Z-br13/isolation/SUMMARY.json` (sha256 `4ab4c34fbb6a…`); contradição: 9 passaram, 0 falharam — `qualification/integration-brasileirao/RAW_LOGS/runtime/run-20260928T183300Z-br13/isolation/contradiction/SUMMARY.json` (sha256 `47cccfc324fb…`)
- Matriz de falhas F01–F16: F01 3/3, F02 3/3, F03 3/3, F04 3/3, F05 4/4, F06 2/2, F07 2/2, F08 10/10, F09 2/2, F10 3/3, F11 3/3, F12 3/3, F13 6/6, F14 3/3, F15 4/4, F16 11/11
  — `qualification/integration-brasileirao/RAW_LOGS/runtime/run-20260928T183300Z-br13/failure-matrix/FAILURE_MATRIX_RESULTS.json` (sha256 `37ed26931a28…`)
- Memória do CAIN: só referências, estados e hashes (nenhuma linha do dado real; no_data_rows_check em toda saída
  pública de cada cenário).
