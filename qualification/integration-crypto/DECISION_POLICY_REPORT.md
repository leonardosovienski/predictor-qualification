# integration-crypto — DECISION_POLICY_REPORT

Gate `DECISION_POLICY` (C12, prompt comum §2 e §6.3, prompt do cripto §3). Os números de execução estão em
`EVIDENCE_NUMBERS.json`, que um script tira de `RAW_LOGS/`. Este texto só cita as chaves de lá (C20).

## 1. O que foi construído (cain)

| Peça | Onde | O que faz |
|---|---|---|
| DecisionPolicy genérica | `cain/orchestration/policy.py` | É uma função pura, sem LLM e sem relógio. Decide `ALLOW \| BLOCK \| ABSTAIN \| REQUIRE_HUMAN \| DUPLICATE \| COOLDOWN` pelas regras R01–R14 (tabela abaixo) e devolve a regra que disparou. |
| Receipt | `policy.receipt` + `policy.dumps` | JSON canônico (`cain-decision-receipt/1`). Traz: id e versão da política, sha256 do código (`policy.py`), sha256 da configuração, domínio, episódio, `as_of`, sha256 da proposta, digest do estado lido, decisão, regra e a task (se houver). Sempre leva `capital_permission=false`. |
| Configuração do domínio | `cain/orchestration/data/crypto.json` | É gerada por `tools/build_domain_config.py` a partir de três fontes, cada uma com sha256: `341d270e4d709150c581c3cd93f4518d483009eb` (SHA completo), o contrato no `main` do predictor-qualification e o `FROZEN_PARAMETERS.json`. |
| `cain research decision-receipt` | `cain/orchestration/cli.py` | Imprime só os bytes canônicos do receipt. Não grava nada. |
| Composition root | `cain research propose/dispatch/retry/ingest/episodes` | Liga TaskOutbox V2, spool, ResultInbox V2, memória do domínio (cubo), retrieval e DecisionPolicy. Tudo é alcançável do entrypoint `cain` (`tests/unit/test_loop_fenced.py::test_orchestration_is_reachable_from_the_cain_console_script`). |

## 2. Regras (primeira que casar vence)

| Regra | Decisão | Motivo |
|---|---|---|
| R01 | BLOCK `DOMAIN_MISMATCH` | proposta, pedido ou evidência de outro domínio, ou ID sem domínio (C18) |
| R02 | BLOCK `SCHEMA_INVALID` | formato `cain-proposal/1` ou pedido inválido contra o `request_schema` (validador do protocolo congelado) |
| R03 | BLOCK `FORBIDDEN_FIELD` | campo fora do formato (handler, comando, módulo, caminho, URL, budget, prioridade final, capital) ou `client_ref` |
| R04 | BLOCK `REQUEST_TYPE_NOT_ALLOWED` | tipo fora das chaves da `handler_allowlist` do contrato. O CAIN nunca nomeia handler. |
| R05 | BLOCK `HYPOTHESIS_CLOSED` | `crypto:H1..H9` do estado científico em 341d270 (inclusive H7/H8 `REGISTERED_NOT_ACTIVATED`) ou a família `funding_oi_hmm_v3` |
| R06 | BLOCK `SYMBOL_NOT_ALLOWED` / `COST_MODEL_MISMATCH` / `REFERENCE_NOT_ALLOWED` / `PRIORITY_ABOVE_CAP` | custos 10/5 bps de `v3/costs.py` em 341d270, referências e teto de prioridade da configuração |
| R07 | BLOCK `REQUEST_ID_CONFLICT` | o mesmo `request_id` já foi emitido com outro conteúdo |
| R08 | DUPLICATE | o mesmo conteúdo de pedido já foi emitido no domínio |
| R09 | REQUIRE_HUMAN `DOMAIN_RECONCILIATION_PENDING` | há um resultado `REQUIRES_HUMAN` do domínio sem resolução |
| R10 | REQUIRE_HUMAN `CONTRADICTION_UNRESOLVED` | há `SUPPORTED` × `REFUTED` para a mesma hipótese; a decisão é de uma pessoa, nunca por maioria |
| R11 | REQUIRE_HUMAN `NEW_HYPOTHESIS` | a hipótese está fora de `proposable_hypotheses` |
| R12 | ABSTAIN `OPEN_TASK_PENDING` / `BUDGET_EXHAUSTED` | budget constante: 1 task aberta, 64 por pesquisa, 512 no total |
| R13 | COOLDOWN `NEGATIVE_STREAK` | 3 resultados negativos seguidos da hipótese: 2 episódios sem task nova dela |
| R14 | ALLOW | nenhuma regra acima casou |

Por construção, nenhum resultado aumenta budget, prioridade ou escopo, e nenhum estado econômico
(`WATCH`/`WATCH_NO_CAPITAL`) é lido como sinal. `QUALIFIED` da Etapa A não é edge (prompt do cripto §5). Não existe caminho de
capital.

## 3. Interface da configuração de domínio (`cain-domain-config/1`)

Para acrescentar stocks ou brasileirão basta:

1. um `data/<domínio>.json`, gerado das fontes fixadas do domínio;
2. o adapter do domínio nos `adapter_paths` dele;
3. a entrada do adapter na allowlist do transporte.

O framework não muda. Os campos são estes:

| Campo | Significado |
|---|---|
| `domain`, `config_version`, `source`, `contract`, `frozen_parameters` | identidade e proveniência (SHA completo e sha256 de cada fonte) |
| `allowed_request_types` | as chaves da `handler_allowlist` do contrato |
| `closed_hypotheses`, `frozen_families` | nunca são reabertas |
| `proposable_hypotheses` | o que pode ser proposto sem o dono |
| `allowed_symbols`, `costs`, `allowed_references`, `max_priority_hint` | o que o pedido pode conter |
| `budget`, `cooldown`, `negative_result_states`, `contradiction_pairs` | constantes da política |

## 4. Conflito do PR #50: escolha e motivo (vale para as três missões)

Escolha: opção **(b)** do prompt comum §4.

- O `cain loop` executava o avaliador do predictor direto do CAIN (`cain/loop/evaluator.py::run_stage`), fora de admission → Ops → Core.
- Ele saiu do console script `cain` e ficou como ferramenta de laboratório (`python -m cain.loop`, mesmos argumentos e saídas).
- As medidas de similaridade usadas por `cain review`/`cain findings` foram para `cain/loop/similarity.py`.
- `tests/unit/test_loop_fenced.py` prova, pelo fecho estático de imports (inclusive imports dentro de funções), que nenhum console script alcança `cain.loop.engine`/`cain.loop.evaluator` nem um pacote de domínio.

Motivo para não usar a opção (a):

- O loop propõe mudanças de código de features/modelo e roda uma cascata de avaliação própria.
- O contrato do cripto só tem `BACKTEST_EXISTING_HYPOTHESIS`.
- Redirecionar o loop exigiria tipos de pedido novos no contrato ou no protocolo, o que é C24.4/C14.

A orquestração nova é o caminho qualificado: proposta → política → task V2 → domínio → resultado → memória → N+1.

## 5. Evidência de execução

Wheels publicadas, Linux primário (GitHub Actions). Chaves de `EVIDENCE_NUMBERS.json`:

- testes da política contra a wheel publicada: `runtime/run36360075557/cleanroom-final/cain.junit.xml:junit`;
- N+1 (receipts byte a byte iguais em processos novos): `runtime/run36360075557/n-plus-1:checks_passed`,
  `:checks_failed`, `:receipts`;
- decisões do E2E: `runtime/run36360075557/e2e:decisions`;
- isolamento, IDs com domínio e contradição: `runtime/run36360075557/isolation:checks_passed` e `:checks_failed`;
- soak com propostas do LLM local pela mesma política: `runtime/run36360088636/soak:counters` (`decisions`,
  `llm_proposals`).

Tabelas por conferência em `CAIN_ROUNDTRIP_REPORT.md` e `SOAK_REPORT.md`, geradas por `scripts/render_reports.py`.
