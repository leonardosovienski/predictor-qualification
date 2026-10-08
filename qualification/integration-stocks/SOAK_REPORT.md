# integration-stocks — SOAK_REPORT

Gate `SOAK` (C10, perfil `QUALIFICATION_PROFILE_INTEGRATION_STOCKS_V1.json`, lido e não alterado). Linux primário, run `run37704456789`, dados reais públicos, runtime só com wheels publicadas. Fonte: `qualification/integration-stocks/RAW_LOGS/runtime/run37704456789/soak/SUMMARY.json` (sha256 `9762dbcf68bcba02…`); comandos brutos em `RAW_LOGS/runtime/run37704456789/soak/commands.log`.

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
| stocks:REQ-IS-SOAK-001: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-019: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-009: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-008: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-020: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-015: payload == authoritative re-read | OK |
| stocks:REQ-LLM-d516b11929b7a7de: payload == authoritative re-read | OK |
| stocks:REQ-LLM-07dfb4d65ab14036: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-013: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-023: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-024: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-011: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-003: payload == authoritative re-read | OK |
| stocks:REQ-LLM-74964fc17c52c897: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-005: payload == authoritative re-read | OK |
| stocks:REQ-LLM-af16d633be77596f: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-017: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-007: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-021: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-016: payload == authoritative re-read | OK |
| stocks:REQ-LLM-d0fe310e5118d78c: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-012: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-004: payload == authoritative re-read | OK |
| soak: canary token absent from CAIN memory | OK |
| soak: canary price absent from CAIN memory | OK |
| soak: post-cutoff instant 2026-10-11 absent from CAIN memory | OK |
| soak: post-cutoff instant 2026-10-12T03:00:00Z absent from CAIN memory | OK |
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
| `cain:SOAK-LLM-1` | stocks:QUAL-LLM-CTRL-001 | qwen2.5:0.5b | `a8b0c51577010a27` | ALLOW ALLOWED (R14) | {'payload_sha256': 'd117e3326e6df9cdc725d60f9bbe46e1785df996a4373b7279c8c99b60f0772c', 'previous_task_id': 'stocks:TASK-80bb970e0a2d8f71156f2e445a8f6e41', 'task_id': 'stocks:TASK-b554624ac4e683037ae5c79b7745d6cc'} |
| `cain:SOAK-LLM-2` | stocks:QUAL-LLM-CTRL-002 | qwen2.5:0.5b | `a8b0c51577010a27` | ALLOW ALLOWED (R14) | {'payload_sha256': '3d53040e30d36b7f80ee92da5a1544d8ef87b592476937589d455b5ed10a3d6b', 'previous_task_id': 'stocks:TASK-b554624ac4e683037ae5c79b7745d6cc', 'task_id': 'stocks:TASK-367101399f4fbc5ff7f0cd7e4dacfb4c'} |
| `cain:SOAK-LLM-3` | stocks:QUAL-LLM-CTRL-003 | qwen2.5:0.5b | `a8b0c51577010a27` | ALLOW ALLOWED (R14) | {'payload_sha256': '9669b27f564bd1b58a24b7d17da18cfb8e973055e0b685373d0285bd5a10b90b', 'previous_task_id': 'stocks:TASK-367101399f4fbc5ff7f0cd7e4dacfb4c', 'task_id': 'stocks:TASK-d5d52e686bbac42c8fdab4e11cef8890'} |
| `cain:SOAK-LLM-4` | stocks:QUAL-LLM-CTRL-004 | qwen2.5:0.5b | `a8b0c51577010a27` | ALLOW ALLOWED (R14) | {'payload_sha256': 'd228ef577fa3918dbbe9c97be116e19219f732af5c7f1e6ce3c91fe23a6f931c', 'previous_task_id': 'stocks:TASK-d5d52e686bbac42c8fdab4e11cef8890', 'task_id': 'stocks:TASK-45a8c123f377e7981e904f39a8cd89fa'} |
| `cain:SOAK-LLM-5` | stocks:QUAL-LLM-CTRL-005 | qwen2.5:0.5b | `a8b0c51577010a27` | ALLOW ALLOWED (R14) | {'payload_sha256': '8830e0974d23535c4de1abd9a100ba9c802968faf90e5a8b731185462614d06a', 'previous_task_id': 'stocks:TASK-45a8c123f377e7981e904f39a8cd89fa', 'task_id': 'stocks:TASK-98d61b5e6fa9b0c508a81d6924d6a04a'} |
