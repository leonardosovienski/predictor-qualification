# DecisionPolicy (DECISION_POLICY, N_PLUS_1_DETERMINISTIC, NEGATIVE_RESULT_NEUTRALITY)

> Gerado por `scripts/render_reports.py` a partir de `EVIDENCE_NUMBERS.json` (C20). Runtime suportado no PC 2 (owner_linux), run `run-20260928T183300Z-br13`.

Política genérica v2 do cain 0.4.13rc13 (sem mudança nesta missão), com a `rule_order` congelada
no FROZEN_PARAMETERS (ciclo 4):

- R01 BLOCK DOMAIN_MISMATCH
- R02 BLOCK SCHEMA_INVALID
- R03 BLOCK FORBIDDEN_FIELD
- R04 BLOCK REQUEST_TYPE_NOT_ALLOWED (fora da allowlist, ou não o tipo fixado para a hipótese proponível)
- R05 BLOCK HYPOTHESIS_CLOSED
- R16 REQUIRE_HUMAN SEALED_SCOPE
- R06 BLOCK SYMBOL_NOT_ALLOWED / COST_MODEL_MISMATCH / REFERENCE_NOT_ALLOWED / PRIORITY_ABOVE_CAP
- R07 BLOCK REQUEST_ID_CONFLICT
- R08 DUPLICATE
- R09 REQUIRE_HUMAN DOMAIN_RECONCILIATION_PENDING
- R10 REQUIRE_HUMAN CONTRADICTION_UNRESOLVED
- R15 REQUIRE_HUMAN HYPOTHESIS_NOT_ADMITTED_BY_DOMAIN
- R11 REQUIRE_HUMAN NEW_HYPOTHESIS
- R17 DUPLICATE EQUIVALENT_REQUEST
- R12 ABSTAIN OPEN_TASK_PENDING / BUDGET_EXHAUSTED
- R13 COOLDOWN NEGATIVE_STREAK
- R14 ALLOW

- N+1 congelado: 84 passaram, 0 falharam — `qualification/integration-brasileirao/RAW_LOGS/runtime/run-20260928T183300Z-br13/n-plus-1/frozen/SUMMARY.json` (sha256 `b19c600366cc…`)
- N+1 no runtime integrado (resultados V2 reais do cripto e do stocks no mesmo estado): 85 passaram, 0 falharam — `qualification/integration-brasileirao/RAW_LOGS/runtime/run-20260928T183300Z-br13/n-plus-1/integrated/SUMMARY.json` (sha256 `4081ddf450b3…`)
- Holdout 2025 (D-25 (2)), nunca despachado:
  - `01-season-2025`: REQUIRE_HUMAN SEALED_SCOPE (R16)
  - `02-window-into-2025`: REQUIRE_HUMAN SEALED_SCOPE (R16)
  - `03-season-2026`: REQUIRE_HUMAN SEALED_SCOPE (R16)
- IB-F002 (holdout → REQUIRE_HUMAN): FIXED.
