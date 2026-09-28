# Soak (SOAK)

> Gerado por `scripts/render_reports.py` a partir de `EVIDENCE_NUMBERS.json` (C20). Runtime suportado no PC 2 (owner_linux), run `run-20260928T183300Z-br13`.

Perfil congelado `QUALIFICATION_PROFILE_INTEGRATION_BR_V1.json` (ciclo 4), uma hipótese de
qualificação por ciclo (decisão do dono, IB-F007).

- Conferências: 61 passaram, 1 falharam — `qualification/integration-brasileirao/RAW_LOGS/runtime/run-20260928T183300Z-br13/soak/SUMMARY.json` (sha256 `37ac07c77c92…`)
- Contadores: {"cycles": 24, "duplicates": 6, "domain_restarts": 6, "cain_restarts": 6, "interleaved_cycles_other_domain": 6, "failure_runs": {"cain_process_death": 5, "consumer_process_death": 4, "domain_retryable": 3, "delivery_anomaly": 6}, "decisions": {"ALLOW": 23, "BLOCK": 6, "DUPLICATE": 2}, "llm_proposals": 0, "deferred": 0} — `qualification/integration-brasileirao/RAW_LOGS/runtime/run-20260928T183300Z-br13/soak/SUMMARY.json` (sha256 `37ac07c77c92…`)

| Piso | Obtido | Mínimo do perfil |
|---|---|---|
| cycles | 24 | 20 |
| duplicates | 6 | 5 |
| domain_restarts | 6 | 5 |
| cain_restarts | 6 | 5 |
| interleaved_cycles_other_domain | 6 | 5 |
| llm_proposals | 0 | 5 |
| classes de falha com ≥ 3 execuções | 4 | 3 |

- Piso de propostas de LLM: 0 (mínimo 5). **Dispensado pelo dono só para o Brasileirão**
  (IB-F009, "Waiver do piso de LLM (Recommended)"): na cain 0.4.13rc13 o CAIN não
  pergunta ao modelo para um domínio sem `parameters` (todo molde é um experimento já rodado, R17). A conferência que
  falhou continua registrada no SUMMARY.json.
