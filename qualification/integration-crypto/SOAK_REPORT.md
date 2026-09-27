# integration-crypto — SOAK_REPORT

Gate `SOAK` (C10, perfil `QUALIFICATION_PROFILE_INTEGRATION_CRYPTO_V1.json`, lido e não alterado). Linux primário, run `run36357575208`, dados reais públicos, runtime só com wheels publicadas. Fonte: `qualification/integration-crypto/RAW_LOGS/runtime/run36357575208/soak/SUMMARY.json` (sha256 `1c666f2f7b00f2d6…`); comandos brutos em `RAW_LOGS/runtime/run36357575208/soak/commands.log`.

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
| llm_proposals | 5 | 6 |

Execuções por classe de falha: {"cain_process_death": 10, "delivery_anomaly": 6, "consumer_process_death": 6, "domain_retryable": 4}. Decisões: {"ALLOW": 26, "DUPLICATE": 6, "BLOCK": 6, "COOLDOWN": 4}.

| Conferência (tolerância zero e fim) | Resultado |
|---|---|
| tasks emitted == task files in the spool == distinct requests admitted by the domain | OK |
| one experiment per request in the domain (no duplicated effect) | OK |
| no result lost: every emitted task has a terminal result | OK |
| one domain payload per task | OK |
| one memory fact per terminal task | OK |
| episodes 1..n without gap | OK |
| crypto:REQ-IC-SOAK-008: payload == authoritative re-read | OK |
| crypto:REQ-IC-SOAK-024: payload == authoritative re-read | OK |
| crypto:REQ-IC-SOAK-011: payload == authoritative re-read | OK |
| crypto:REQ-IC-SOAK-016: payload == authoritative re-read | OK |
| crypto:REQ-IC-SOAK-019: payload == authoritative re-read | OK |
| crypto:REQ-IC-SOAK-005: payload == authoritative re-read | OK |
| crypto:REQ-IC-SOAK-015: payload == authoritative re-read | OK |
| crypto:REQ-IC-SOAK-023: payload == authoritative re-read | OK |
| crypto:REQ-IC-SOAK-001: payload == authoritative re-read | OK |
| crypto:REQ-LLM-af16d633be77596f: payload == authoritative re-read | OK |
| crypto:REQ-IC-SOAK-017: payload == authoritative re-read | OK |
| crypto:REQ-IC-SOAK-012: payload == authoritative re-read | OK |
| crypto:REQ-IC-SOAK-009: payload == authoritative re-read | OK |
| crypto:REQ-IC-SOAK-021: payload == authoritative re-read | OK |
| crypto:REQ-IC-SOAK-013: payload == authoritative re-read | OK |
| crypto:REQ-IC-SOAK-003: payload == authoritative re-read | OK |
| crypto:REQ-LLM-07dfb4d65ab14036: payload == authoritative re-read | OK |
| crypto:REQ-IC-SOAK-004: payload == authoritative re-read | OK |
| crypto:REQ-IC-SOAK-020: payload == authoritative re-read | OK |
| crypto:REQ-IC-SOAK-007: payload == authoritative re-read | OK |
| soak: canary token absent from CAIN memory | OK |
| soak: post-cutoff instant 2026, 9, 7 absent from CAIN memory | OK |
| soak: post-cutoff instant 2026-09-07 absent from CAIN memory | OK |
| soak: post-cutoff instant 2026, 9, 14 absent from CAIN memory | OK |
| soak: post-cutoff instant 2026-09-14 absent from CAIN memory | OK |
| soak: post-cutoff instant 2026, 9, 21 absent from CAIN memory | OK |
| soak: post-cutoff instant 2026-09-21 absent from CAIN memory | OK |
| no contamination: no fact of another domain | OK |
| no ALLOW for crypto:H1..H9 | OK |
| no capital_permission true anywhere | OK |
| floor cycles >= 20 | OK |
| floor duplicates >= 5 | OK |
| floor domain_restarts >= 5 | OK |
| floor cain_restarts >= 5 | OK |
| floor interleaved_cycles_other_domain >= 5 | OK |
| floor relevant failure classes >= 3 (each >= 3 runs) | OK |
| floor llm_proposals >= 5 | OK |

Execuções anteriores do soak, mantidas como evidência (não descartadas):

- `run36357313578`: 40 OK, 1 falhas — `floor llm_proposals >= 5` (obtido: 0). Fonte: `qualification/integration-crypto/RAW_LOGS/runtime/run36357313578/soak/SUMMARY.json` (sha256 `0a89a8a02ae4ad14…`). Recusas do cliente LLM no `qualification/integration-crypto/RAW_LOGS/runtime/run36357313578/soak/commands.log` (sha256 `62402be054cae991…`) (bytes de entrada, limite): [(4487, 3584)].

A falha anterior foi de configuração do harness, não do produto: o `cain-llm.toml` do soak declarava `num_ctx = 4096`, e o orçamento de entrada do cliente LLM do cain é `min(max_input_bytes, num_ctx - num_predict - 256)` = min(6500, 4096 - 256 - 256), menor que o pedido de proposta com contexto (números da recusa acima, lidos do log). Cada proposta saiu `LLM_PROPOSAL_FAILED` (fail closed, nenhuma task emitida). O harness passou a declarar `num_ctx = 8192` e `max_input_bytes = 16000` (`scripts/soak.py`, commit `2319ed0`, cuja mensagem atribui o 3584 ao padrão do cain por engano: o padrão de `max_input_bytes` é 6500, e o limite vinha do `num_ctx` do harness). Perfil, pisos, parâmetros congelados e vetores não mudaram.

As propostas de LLM usam um modelo local (Ollama no runner; modelo e digest nos arquivos `*.audit.json` do artefato). São auditadas e passam pela mesma DecisionPolicy; não servem de prova de gate (C9).
