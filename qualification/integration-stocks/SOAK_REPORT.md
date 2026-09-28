# integration-stocks — SOAK_REPORT

Gate `SOAK` (C10, perfil `QUALIFICATION_PROFILE_INTEGRATION_STOCKS_V1.json`, lido e não alterado). Linux primário, run `run36440479456`, dados reais públicos, runtime só com wheels publicadas. Fonte: `qualification/integration-stocks/RAW_LOGS/runtime/run36440479456/soak/SUMMARY.json` (sha256 `7a52a2f68a87836f…`); comandos brutos em `RAW_LOGS/runtime/run36440479456/soak/commands.log`.

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
| stocks:REQ-IS-SOAK-021: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-007: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-009: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-003: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-012: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-024: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-013: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-001: payload == authoritative re-read | OK |
| stocks:REQ-LLM-d0fe310e5118d78c: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-016: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-017: payload == authoritative re-read | OK |
| stocks:REQ-LLM-d516b11929b7a7de: payload == authoritative re-read | OK |
| stocks:REQ-LLM-af16d633be77596f: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-005: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-023: payload == authoritative re-read | OK |
| stocks:REQ-LLM-07dfb4d65ab14036: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-019: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-015: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-011: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-020: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-004: payload == authoritative re-read | OK |
| stocks:REQ-LLM-74964fc17c52c897: payload == authoritative re-read | OK |
| stocks:REQ-IS-SOAK-008: payload == authoritative re-read | OK |
| soak: canary token absent from CAIN memory | OK |
| soak: canary price absent from CAIN memory | OK |
| soak: post-cutoff instant 2026-10-01 absent from CAIN memory | OK |
| soak: post-cutoff instant 2026-10-02T03:00:00Z absent from CAIN memory | OK |
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

Modelo local (Ollama no runner). Cada proposta passa pela mesma DecisionPolicy (`cain research propose --proposal`); a decisão e a task vêm da saída desse comando no `commands.log`. Hipóteses só para o LLM (ciclo 2, `FROZEN_PARAMETERS.json` → `stocks_config.llm_hypotheses`): stocks:QUAL-LLM-CTRL-001, stocks:QUAL-LLM-CTRL-002, stocks:QUAL-LLM-CTRL-003, stocks:QUAL-LLM-CTRL-004, stocks:QUAL-LLM-CTRL-005. o mesmo protocolo das hipóteses REAL (backtest 12-1 no painel real do run) com parameters.negative_control SHUFFLED_LABELS de semente própria (9001–9005): um controle negativo real do domínio, nunca uma hipótese científica; cada uma roda no máximo uma vez (a segunda proposta da mesma hipótese é o mesmo experimento → R17).

| Proposta | Hipótese escolhida | Modelo | Digest | Decisão | Task |
|---|---|---|---|---|---|
| `cain:SOAK-LLM-1` | stocks:QUAL-LLM-CTRL-001 | qwen2.5:0.5b | `a8b0c51577010a27` | ALLOW ALLOWED (R14) | {'payload_sha256': '86a003c73384cd1de45bab3118a5604a72cdbf3dec557a3d2348dd5d585cf4e5', 'previous_task_id': 'stocks:TASK-63b0601b27d886c88faf33fd313e0b78', 'task_id': 'stocks:TASK-bf421b4f73e02178d3f4c951e152d4df'} |
| `cain:SOAK-LLM-2` | stocks:QUAL-LLM-CTRL-002 | qwen2.5:0.5b | `a8b0c51577010a27` | ALLOW ALLOWED (R14) | {'payload_sha256': '81c32c5471add586ae691acd4600e5bb4239624b7b9283a209bca5a34bf9f9fd', 'previous_task_id': 'stocks:TASK-bf421b4f73e02178d3f4c951e152d4df', 'task_id': 'stocks:TASK-b84ef64dc457be44314e0745e473db24'} |
| `cain:SOAK-LLM-3` | stocks:QUAL-LLM-CTRL-003 | qwen2.5:0.5b | `a8b0c51577010a27` | ALLOW ALLOWED (R14) | {'payload_sha256': '1a0507e9c150c92336a5af26e32f9116c9e93768a3a5f6b0d73a3941a9f3324b', 'previous_task_id': 'stocks:TASK-b84ef64dc457be44314e0745e473db24', 'task_id': 'stocks:TASK-987992bcf6c32a084ec5de6c31763262'} |
| `cain:SOAK-LLM-4` | stocks:QUAL-LLM-CTRL-004 | qwen2.5:0.5b | `a8b0c51577010a27` | ALLOW ALLOWED (R14) | {'payload_sha256': '24d6d22b5ad39ba0088440c7b7ae57265cca21cab2569675937442df4140f695', 'previous_task_id': 'stocks:TASK-987992bcf6c32a084ec5de6c31763262', 'task_id': 'stocks:TASK-d458239b8cd950edb2121fdfe7d0472d'} |
| `cain:SOAK-LLM-5` | stocks:QUAL-LLM-CTRL-005 | qwen2.5:0.5b | `a8b0c51577010a27` | ALLOW ALLOWED (R14) | {'payload_sha256': '2e51ccacc6db1224610942226212bf9d5019a682551dc851096d5dfea4709cc2', 'previous_task_id': 'stocks:TASK-d458239b8cd950edb2121fdfe7d0472d', 'task_id': 'stocks:TASK-f50ed9073aa5a01c17f83737aa967c44'} |
