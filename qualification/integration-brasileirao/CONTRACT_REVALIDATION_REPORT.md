# Revalidação do contrato do domínio (C24.3, DOMAIN_CONTRACTS_PRESERVED)

> Gerado por `scripts/render_reports.py` a partir de `EVIDENCE_NUMBERS.json` (C20). Runtime suportado no PC 2 (owner_linux), run `run-20260928T145525Z-br12`.

- (a)(b)(e)(f) estáticas: 10 passaram, 0 falharam —
  `qualification/integration-brasileirao/RAW_LOGS/runtime/run-20260928T145525Z-br12/contract-revalidation/static.json` (sha256 `baafb856bb32…`)
- (f) pelo caminho aceito pelo dono (IB-F005, "Aceitar precedente (Recommended)"): aceito =
  True — `qualification/integration-brasileirao/RAW_LOGS/runtime/run-20260928T145525Z-br12/contract-revalidation/ib_f005_acceptance.json` (sha256 `6952b4276faf…`); runs: https://github.com/leonardosovienski/brasileirao-predictor/actions/runs/36373479101, https://github.com/leonardosovienski/brasileirao-predictor/actions/runs/36375025850
- (c) conformidade no cleanroom-final: 89 testes, 0 falhas, 0 erros, 0 pulados — `qualification/integration-brasileirao/RAW_LOGS/runtime/run-20260928T145525Z-br12/cleanroom-final/conformance.junit.xml` (sha256 `12129428c6ba…`)
- (d) pelo runtime suportado: 11 passaram, 0 falharam — `qualification/integration-brasileirao/RAW_LOGS/runtime/run-20260928T145525Z-br12/contract-revalidation/SUMMARY.json` (sha256 `b02d2d3a0ea4…`)
- Registro: a primeira execução estática, sem o arquivo de aceite, deu (f) FAIL; o arquivo de aceite confere a
  decisão do dono e os dois runs pelo `gh` (`scripts/ib_f005_acceptance.py`).
