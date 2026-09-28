# integration-stocks — SOAK_REPORT

Gate `SOAK` (C10, perfil `QUALIFICATION_PROFILE_INTEGRATION_STOCKS_V1.json`, lido e não alterado). Linux primário, run `run36365355063`, dados reais públicos, runtime só com wheels publicadas. Fonte: `qualification/integration-stocks/RAW_LOGS/runtime/run36365355063/soak/SUMMARY.json` (sha256 `eba2bd1bf154c38d…`); comandos brutos em `RAW_LOGS/runtime/run36365355063/soak/commands.log`.

Resultado: **38 conferências OK, 0 falhas**.

| Piso | Mínimo | Obtido |
|---|--:|--:|
| cycles | 20 | 24 |
| duplicates | 5 | 18 |
| domain_restarts | 5 | 6 |
| cain_restarts | 5 | 10 |
| interleaved_cycles_other_domain | 5 | 6 |
| relevant_failure_classes | 3 | 4 |
| runs_per_failure_class | 3 | 4 |
| llm_proposals | 5 | 6 |

Execuções por classe de falha: {"cain_process_death": 10, "delivery_anomaly": 6, "consumer_process_death": 6, "domain_retryable": 4}. Decisões: {"ALLOW": 24, "DUPLICATE": 6, "BLOCK": 12}.

| Conferência (tolerância zero e fim) | Resultado |
|---|---|
| tasks emitted == task files in the spool == distinct requests admitted by the domain | OK |
| one experiment per request in the domain (no duplicated effect) | OK |
| no result lost: every emitted task has a terminal result | OK |
| one domain payload per task | OK |
| one memory fact per terminal task | OK |
| episodes 1..n without gap | OK |
| stocks:REQ-IS-SOAK-004: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-021: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-024: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-015: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-023: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-019: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-001: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-008: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-020: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-009: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-003: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-005: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-013: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-011: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-012: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-016: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-007: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-017: payload == authoritative re-read | OK |
| soak: canary token absent from CAIN memory | OK |
| soak: canary price absent from CAIN memory | OK |
| soak: post-cutoff instant 2026-10-01 absent from CAIN memory | OK |
| soak: post-cutoff instant 2026-10-02T03:00:00Z absent from CAIN memory | OK |
| no contamination: no fact of another domain | OK |
| no ALLOW for stocks:H1..H22: every emitted task is a frozen soak hypothesis | OK |
| no capital_permission true anywhere | OK |
| floor cycles >= 20 | OK |
| floor duplicates >= 5 | OK |
| floor domain_restarts >= 5 | OK |
| floor cain_restarts >= 5 | OK |
| floor interleaved_cycles_other_domain >= 5 | OK |
| floor relevant failure classes >= 3 (each >= 3 runs) | OK |
| floor llm_proposals >= 5 | OK |

## Propostas de LLM (auditadas; não são gate, C9)

Modelo local (Ollama no runner). Cada proposta passa pela mesma DecisionPolicy (`cain research propose --proposal`); a decisão e a task vêm da saída desse comando no `commands.log`. Limite conhecido antes do congelamento (IS-F003): o framework grava `parameters.placebo_seed`, que o `request_schema` do Stocks recusa.

| Proposta | Hipótese escolhida | Modelo | Digest | Decisão | Task |
|---|---|---|---|---|---|
| `cain:SOAK-LLM-1` | stocks:QUAL-PIT-MOM-REAL-001 | qwen2.5:0.5b | `a8b0c51577010a27` | BLOCK SCHEMA_INVALID (R02) | nenhuma |
| `cain:SOAK-LLM-2` | stocks:QUAL-PIT-MOM-REAL-001 | qwen2.5:0.5b | `a8b0c51577010a27` | BLOCK SCHEMA_INVALID (R02) | nenhuma |
| `cain:SOAK-LLM-3` | stocks:QUAL-PIT-MOM-REAL-001 | qwen2.5:0.5b | `a8b0c51577010a27` | BLOCK SCHEMA_INVALID (R02) | nenhuma |
| `cain:SOAK-LLM-4` | stocks:QUAL-PIT-MOM-REAL-001 | qwen2.5:0.5b | `a8b0c51577010a27` | BLOCK SCHEMA_INVALID (R02) | nenhuma |
| `cain:SOAK-LLM-5` | stocks:QUAL-PIT-MOM-REAL-001 | qwen2.5:0.5b | `a8b0c51577010a27` | BLOCK SCHEMA_INVALID (R02) | nenhuma |
| `cain:SOAK-LLM-6` | stocks:QUAL-PIT-MOM-REAL-001 | qwen2.5:0.5b | `a8b0c51577010a27` | BLOCK SCHEMA_INVALID (R02) | nenhuma |
