# integration-stocks — SOAK_REPORT

Gate `SOAK` (C10, perfil `QUALIFICATION_PROFILE_INTEGRATION_STOCKS_V1.json`, lido e não alterado). Linux primário, run `run37698400981`, dados reais públicos, runtime só com wheels publicadas. Fonte: `qualification/integration-stocks/RAW_LOGS/runtime/run37698400981/soak/SUMMARY.json` (sha256 `897f1c6cc517a853…`); comandos brutos em `RAW_LOGS/runtime/run37698400981/soak/commands.log`.

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
| stocks:REQ-IS-SOAK-005: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-017: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-015: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-001: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-004: payload == authoritative re-read | OK |
| stocks:REQ-LLM-74964fc17c52c897: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-011: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-024: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-019: payload == authoritative re-read | OK |
| stocks:REQ-LLM-07dfb4d65ab14036: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-016: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-008: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-020: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-012: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-003: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-007: payload == authoritative re-read | OK |
| stocks:REQ-LLM-d0fe310e5118d78c: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-023: payload == authoritative re-read | OK |
| stocks:REQ-LLM-d516b11929b7a7de: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-021: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-009: payload == authoritative re-read | OK |
| stocks:REQ-LLM-9ae4d056a2e7b32a: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-013: payload == authoritative re-read | OK |
| soak: canary token absent from CAIN memory | OK |
| soak: canary price absent from CAIN memory | OK |
| soak: post-cutoff instant 2026-10-10 absent from CAIN memory | OK |
| soak: post-cutoff instant 2026-10-11T03:00:00Z absent from CAIN memory | OK |
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
| `cain:SOAK-LLM-2` | stocks:QUAL-LLM-CTRL-001 | qwen2.5:0.5b | `a8b0c51577010a27` | ALLOW ALLOWED (R14) | {'payload_sha256': '2215eac58b1ea889aa5825c4f5f86b08cf3169b9b4789eda5041fc726462c2f0', 'previous_task_id': 'stocks:TASK-623c0183548e1fdbe795218cadb3e284', 'task_id': 'stocks:TASK-abe640c2003e53e8dbce344061d7bb92'} |
| `cain:SOAK-LLM-3` | stocks:QUAL-LLM-CTRL-002 | qwen2.5:0.5b | `a8b0c51577010a27` | ALLOW ALLOWED (R14) | {'payload_sha256': '95473fa797802a8b0321e83d22bbb056792183677ac7992ccc8534098dddefac', 'previous_task_id': 'stocks:TASK-abe640c2003e53e8dbce344061d7bb92', 'task_id': 'stocks:TASK-9edb1c6f85cb328e05e2d0890e0ba3de'} |
| `cain:SOAK-LLM-4` | stocks:QUAL-LLM-CTRL-003 | qwen2.5:0.5b | `a8b0c51577010a27` | ALLOW ALLOWED (R14) | {'payload_sha256': '4564182cd054532e11ec92ccd8e6011e2c56115990fd6b05daafd177ac658888', 'previous_task_id': 'stocks:TASK-9edb1c6f85cb328e05e2d0890e0ba3de', 'task_id': 'stocks:TASK-79b46e8816baed72200663b93a4b5d1b'} |
| `cain:SOAK-LLM-5` | stocks:QUAL-LLM-CTRL-008 | qwen2.5:0.5b | `a8b0c51577010a27` | ALLOW ALLOWED (R14) | {'payload_sha256': 'bdbf5ae9f0302e88924c4734e093a4ed6552d0cf8fa1ff504c7020e3d62479fa', 'previous_task_id': 'stocks:TASK-79b46e8816baed72200663b93a4b5d1b', 'task_id': 'stocks:TASK-551749605d7f65947cdee90c4fa1341e'} |
| `cain:SOAK-LLM-6` | stocks:QUAL-LLM-CTRL-007 | qwen2.5:0.5b | `a8b0c51577010a27` | ALLOW ALLOWED (R14) | {'payload_sha256': 'cec4a5a091db839a258b94a7b033384ab65ce9cb40ec0d7fcc0695b0daab3837', 'previous_task_id': 'stocks:TASK-551749605d7f65947cdee90c4fa1341e', 'task_id': 'stocks:TASK-faffedf73272042ef7ce9ec367c25a76'} |
