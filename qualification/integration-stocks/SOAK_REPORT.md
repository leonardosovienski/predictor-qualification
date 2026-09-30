# integration-stocks — SOAK_REPORT

Gate `SOAK` (C10, perfil `QUALIFICATION_PROFILE_INTEGRATION_STOCKS_V1.json`, lido e não alterado). Linux primário, run `run36652132817`, dados reais públicos, runtime só com wheels publicadas. Fonte: `qualification/integration-stocks/RAW_LOGS/runtime/run36652132817/soak/SUMMARY.json` (sha256 `19b3a05a54bc0219…`); comandos brutos em `RAW_LOGS/runtime/run36652132817/soak/commands.log`.

Resultado: **43 conferências OK, 0 falhas**.

| Piso | Mínimo | Obtido |
|---|--:|--:|
| cycles | 20 | 24 |
| duplicates | 5 | 18 |
| domain_restarts | 5 | 6 |
| cain_restarts | 5 | 10 |
| interleaved_cycles_other_domain | 5 | 6 |
| relevant_failure_classes | 3 | 4 |
| runs_per_failure_class | 3 | 4 |
| llm_proposals | 5 | 5 |

Execuções por classe de falha: {"cain_process_death": 10, "delivery_anomaly": 6, "consumer_process_death": 6, "domain_retryable": 4}. Decisões: {"ALLOW": 29, "DUPLICATE": 6, "BLOCK": 6}.

| Conferência (tolerância zero e fim) | Resultado |
|---|---|
| tasks emitted == task files in the spool == distinct requests admitted by the domain | OK |
| one experiment per request in the domain (no duplicated effect) | OK |
| no result lost: every emitted task has a terminal result | OK |
| one domain payload per task | OK |
| one memory fact per terminal task | OK |
| episodes 1..n without gap | OK |
| stocks:REQ-IS-SOAK-004: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-003: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-019: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-005: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-001: payload == authoritative re-read | OK |
| stocks:REQ-LLM-9ae4d056a2e7b32a: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-009: payload == authoritative re-read | OK |
| stocks:REQ-LLM-d516b11929b7a7de: payload == authoritative re-read | OK |
| stocks:REQ-LLM-74964fc17c52c897: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-007: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-011: payload == authoritative re-read | OK |
| stocks:REQ-LLM-d0fe310e5118d78c: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-024: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-021: payload == authoritative re-read | OK |
| stocks:REQ-LLM-07dfb4d65ab14036: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-017: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-016: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-012: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-023: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-013: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-020: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-008: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-015: payload == authoritative re-read | OK |
| soak: canary token absent from CAIN memory | OK |
| soak: canary price absent from CAIN memory | OK |
| soak: post-cutoff instant 2026-10-03 absent from CAIN memory | OK |
| soak: post-cutoff instant 2026-10-04T03:00:00Z absent from CAIN memory | OK |
| no contamination: no fact of another domain | OK |
| no ALLOW for stocks:H1..H22: every emitted task is a frozen soak or LLM hypothesis | OK |
| no capital_permission true anywhere | OK |
| floor cycles >= 20 | OK |
| floor duplicates >= 5 | OK |
| floor domain_restarts >= 5 | OK |
| floor cain_restarts >= 5 | OK |
| floor interleaved_cycles_other_domain >= 5 | OK |
| floor relevant failure classes >= 3 (each >= 3 runs) | OK |
| floor llm_proposals >= 5 | OK |

## Propostas de LLM (auditadas; não são gate, C9)

Modelo local (Ollama no runner). Cada proposta passa pela mesma DecisionPolicy (`cain research propose --proposal`); a decisão e a task vêm da saída desse comando no `commands.log`. Hipóteses só para o LLM (ciclo 4, `FROZEN_PARAMETERS.json` → `stocks_config.llm_hypotheses`): stocks:QUAL-LLM-CTRL-001, stocks:QUAL-LLM-CTRL-002, stocks:QUAL-LLM-CTRL-003, stocks:QUAL-LLM-CTRL-004, stocks:QUAL-LLM-CTRL-005, stocks:QUAL-LLM-CTRL-006, stocks:QUAL-LLM-CTRL-007, stocks:QUAL-LLM-CTRL-008. o mesmo protocolo das hipóteses REAL (backtest 12-1 no painel real do run) com parameters.negative_control SHUFFLED_LABELS de semente própria (9001–9008): um controle negativo real do domínio, nunca uma hipótese científica; cada uma roda no máximo uma vez (a segunda proposta da mesma hipótese é o mesmo experimento → R17).

| Proposta | Hipótese escolhida | Modelo | Digest | Decisão | Task |
|---|---|---|---|---|---|
| `cain:SOAK-LLM-2` | stocks:QUAL-LLM-CTRL-001 | qwen2.5:0.5b | `a8b0c51577010a27` | ALLOW ALLOWED (R14) | {'payload_sha256': 'af08665ba555940aa66cce6c1f4e691a8f0a3fd9ede8d2a8cd489805c91e1511', 'previous_task_id': 'stocks:TASK-a806cf4812695c7f62922f5446ce22c3', 'task_id': 'stocks:TASK-667961d487ea82ab0da24ff47f3fffd2'} |
| `cain:SOAK-LLM-3` | stocks:QUAL-LLM-CTRL-002 | qwen2.5:0.5b | `a8b0c51577010a27` | ALLOW ALLOWED (R14) | {'payload_sha256': '00c8d21f1302b71b2963ed2d06dad2fb01673b166058d4b4ed3cb82123e7cb70', 'previous_task_id': 'stocks:TASK-667961d487ea82ab0da24ff47f3fffd2', 'task_id': 'stocks:TASK-a56965f647638349681afb36d87bab3a'} |
| `cain:SOAK-LLM-4` | stocks:QUAL-LLM-CTRL-003 | qwen2.5:0.5b | `a8b0c51577010a27` | ALLOW ALLOWED (R14) | {'payload_sha256': '4e9a918c235004b224d1f4c55c08f6ab8edef94913e0dbba7611050fd550d28d', 'previous_task_id': 'stocks:TASK-a56965f647638349681afb36d87bab3a', 'task_id': 'stocks:TASK-ae4f7b35f5a024c18fdb6f70356d3bda'} |
| `cain:SOAK-LLM-5` | stocks:QUAL-LLM-CTRL-008 | qwen2.5:0.5b | `a8b0c51577010a27` | ALLOW ALLOWED (R14) | {'payload_sha256': 'df70df18e56a62e53fadd96da6e1611e93ec0eb55768897c80b106df3dd2e1f0', 'previous_task_id': 'stocks:TASK-ae4f7b35f5a024c18fdb6f70356d3bda', 'task_id': 'stocks:TASK-7d9a8b33bc594d27055f739159c9b243'} |
| `cain:SOAK-LLM-6` | stocks:QUAL-LLM-CTRL-007 | qwen2.5:0.5b | `a8b0c51577010a27` | ALLOW ALLOWED (R14) | {'payload_sha256': 'eec4d8eece5560bcf315d8cc70efd1e9572df58d74ee1358238d83c153179d2e', 'previous_task_id': 'stocks:TASK-7d9a8b33bc594d27055f739159c9b243', 'task_id': 'stocks:TASK-30f45661cf4fa21388d4719c3f9f5944'} |
