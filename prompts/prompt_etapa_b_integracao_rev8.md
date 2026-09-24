> **SUBSTITUÍDO pela D-22 (núcleo v2.3).** A Etapa B virou três missões, uma por domínio: use
> `prompt_etapa_b_comum_rev9.md` + `prompt_etapa_b_{crypto,stocks,brasileirao}_rev9.md`. Este arquivo fica como registro.

# MISSÃO — ETAPA B: INTEGRAÇÃO CAIN × ECOSYSTEM × CRIPTO × BRASILEIRÃO × STOCKS (Rev 8 — enxuto)

```text
stage  = B
branch = integration
núcleo = qualification/COMMON_QUALIFICATION_CORE.md v2.2
sha256 = d681e423499e202c735ee1f110311a9721019ef11e21ae824f4791bada7c7d2c
```

Objetivo: o CAIN propõe pesquisas aos três domínios pelo envelope V2, recebe
os resultados, guarda memória e decide o próximo passo (N+1) — **sem quebrar**
nada que a Etapa A provou, sem misturar domínios e sem nunca virar autoridade
sobre capital. Você é o único agente; não use subagentes. O núcleo vale
inteiro; este prompt só acrescenta.

---

## 0. Como trabalhar

* **C0 primeiro.** Falhou → `ABORTED`.
* Só conta o que rodou pelo runtime suportado (C2). Status `PASS | FAIL |
  NOT_RUN` (`BLOCKED: …` em `note`). Números de `RAW_LOGS/` (C20).
* Tudo por branch + PR; nunca merge, push em `main`, rebase ou force-push.
  Você pode publicar releases `rc` de `cain` e dos adapters.
* **Pare e pergunte ao dono** quando: regra local conflitar (C19); um domínio
  precisar mudar fora dos `adapter_paths` (C24.4); o protocolo V2 precisar mudar.

---

## 1. Pré-condições (além do C0)

* As três `QUALIFICATION_ATTESTATION.json` da Etapa A com `result = QUALIFIED`
  e os três contratos no `main`.
* `qualification/shared/ENVELOPE_V2_FREEZE.json` e `STACK_BASELINE_V2.<n>.json`
  no `main`.
* Nenhum issue bloqueante em `SHARED_ISSUES.json`.

---

## 2. Escopo e circuito

* `cain`, `ecosystem-predictor`: mudam (exceto `packages/research-protocol`,
  consumido da release congelada).
* `cripto-predictor`, `brasileirao-predictor`, `stocks-predictor`: **só** nos
  `adapter_paths` do contrato.
* `core-predictor`, `predictor-ops`: congelados.

Para cada domínio, intercalando os três:

```text
CAIN → proposta → ResearchTaskV2 → TaskOutbox → transporte (ecosystem)
→ adapter do domínio → pedido do contrato → [circuito da Etapa A: admission → Ops → Core]
→ resultado → adapter → ResearchResultV2 → CAIN ResultInbox → persistência
→ restart do CAIN → retrieval → DecisionPolicy → receipt → proposta N+1
```

---

## 3. Ponto de partida (22/09 — reconfirmar)

| Item | Onde | Observado |
|---|---|---|
| `TaskOutbox` | `cain/src/cain/research_tasks.py` | existe; só testes; V1 |
| `ResultInbox` | `cain/src/cain/research_results.py` | existe; só testes; V1 |
| `ResultEgressPolicy` | `cain/src/cain/research_egress.py` | egress (não é DecisionPolicy) |
| `cain research explain` | `cain/src/cain/research/cli.py` | usa LLM — só soak (C9) |
| DecisionPolicy, `cain research decision-receipt` | — | não existem |
| Entrypoints | `cain`, `cain-mcp`, `cain-stream` | — |
| Instalação operacional | `C:\CAIN\.venv`, serviço 8877, `C:\CAIN\dados` | nunca tocar nem usar como prova |

---

## 4. Runtime e dados

* Linux (D-9): os três domínios + CAIN no mesmo runtime de qualificação.
* Windows (D-3): CAIN e Brasileirão em `C:\QUALIFICACAO\runtime\integration\`,
  Cripto em `C:\Cripto\qualificacao\runtime\integration\`; parte Stocks em
  `windows-latest` no GitHub Actions (D-1).
* Memória do CAIN da qualificação = banco novo, nunca `C:\CAIN\dados`.
* Protegidos: união dos três conjuntos da Etapa A, mesmos hashes de blob (gate
  `PROTECTED_ARTIFACTS_UNCHANGED`).

---

## 5. O que construir

1. **Envelope V2** consumido da release congelada; **adapters** nos três
   domínios só nos `adapter_paths`, só pela `adapter_api`: V2 → pedido do
   contrato (com `client_ref`) e resultado → V2 com payload de domínio
   byte-idêntico. Gate `ENVELOPE_V2_CONFORMANCE` (validação contra o V2,
   serialização canônica, rejeição fail closed);
   `ENVELOPE_V2_CONFORMANCE_REPORT.md`.
2. **CAIN** com composition root real: `TaskOutbox`, `ResultInbox`,
   memória/retrieval e DecisionPolicy alcançáveis dos entrypoints.
3. **DecisionPolicy** (C12) determinística e versionada, decisões
   `ALLOW | BLOCK | ABSTAIN | REQUIRE_HUMAN | DUPLICATE | COOLDOWN`, e o comando
   `cain research decision-receipt` (sem LLM). Gate `DECISION_POLICY`;
   `DECISION_POLICY_REPORT.md`.

Registre as mudanças em `QUALIFICATION_CHANGELOG.md`.

---

## 6. Garantias

* **`CAIN_INGESTION`** — só schema V2 conhecido, task existente **do mesmo
  domínio**, correlação e provenance válidas.
* **`CAIN_CONTAINMENT`** — CAIN só propõe; nunca escolhe handler, budget
  final, prioridade final ou capital; nunca lê banco de domínio; ação fora da
  allowlist bloqueada e registrada.
* **`AUTHORITY_SEPARATION`** — o CAIN guarda os estados operacional, científico
  e econômico como vieram; nunca promove um a outro.
* **`CROSS_DOMAIN_ISOLATION`** — resultado de um domínio nunca satisfaz task de
  outro (todas as combinações dos três).
* **`DOMAIN_QUALIFIED_IDS`** — `crypto:H9`, `brasileirao:H9`, `stocks:H9` nunca
  se confundem; ID sem domínio rejeitado.
* **`CONTRADICTION_PRESERVATION`** — resultados contraditórios ficam como
  contradição, nunca decididos por maioria.
* **`NEGATIVE_RESULT_NEUTRALITY`** — sequência de `NO_EDGE`, `INCONCLUSIVE`,
  `NOT_READY`, `CLOSED_INSUFFICIENT_SAMPLE`, `INCONCLUSIVE_DATA_QUALITY` não
  aumenta budget, prioridade nem escopo além da policy congelada.
* **`FUTURE_CANARY`** — os canários dos três domínios nunca aparecem antes do
  cutoff na memória nem no retrieval do CAIN.
* **`CAPITAL_FORBIDDEN`** — nenhum caminho concede capital.

---

## 7. E2E, N+1, idempotência, falhas

* **E2E** (gates `E2E`, `PROVENANCE`): só `final_wheels`, a partir dos
  entrypoints do CAIN e dos consumidores; três domínios intercalados; restart
  do CAIN e de cada consumidor no meio. `CAIN_ROUNDTRIP_REPORT.md`, `E2E_EVIDENCE/`.
* **N+1** (gate `N_PLUS_1_DETERMINISTIC`, C9): fixture congelado com resultados
  dos três; 3 processos novos com receipt idêntico byte a byte.
* **Idempotência** (gate `IDEMPOTENCY`): retry, restart, entrega duplicada →
  nenhum segundo experimento, efeito ou resultado. IDs: research_id, task_id,
  request_id, admission_id, experiment_id, attempt_id, ops_run_id, result_id.
* **Falhas** (gates `FAILURE_INJECTION`, `RESTART_RECOVERY`),
  `FAILURE_MATRIX.json` congelada antes, por domínio: antes do envio; entre
  envio e ACK; durante e depois da ingestão; durante a decisão; CAIN fora;
  consumidor fora; resultado duplicado ou fora de ordem; versão de schema
  errada; mesmo ID com payload diferente; envelope válido com task errada.
  Fail closed.

---

## 8. Revalidação dos contratos (C24.3; gate `DOMAIN_CONTRACTS_PRESERVED`)

Para cada domínio, nos `final_commits` desta missão, itens (a)–(f) de C24.3.
`CONTRACT_REVALIDATION_REPORT.md` + `domain_attestations[*].revalidation`.
Falhou → pare; a Etapa A daquele domínio reabre (C24.4).

---

## 9. Soak, Windows, CI, segredos

* **Perfil** `QUALIFICATION_PROFILE_INTEGRATION_V1.json` (pisos C10, Etapa B) +
  ≥ 5 propostas via `cain research explain` (LLM, auditadas; não são gate).
  Tolerância zero: resultado de outro domínio aceito, ID ambíguo aceito,
  contradição decidida por maioria. Soak no Linux (gate `SOAK`).
* **Windows** (gate `WINDOWS_SMOKE`): E2E + restart local para CAIN + Cripto +
  Brasileirão e job `windows-latest` para Stocks — as duas partes precisam passar.
* **CI** (gate `HOSTED_CI`): push/PR dos 7 repos + workflows de integração V2
  criados aqui; os V1 aposentados (HYG-015) não entram.
* **Segredos** (gate `SECRETS_CLEAN`): zero achados.

---

## 10. Fases (C8)

```text
freeze-parameters → baseline → truth-map → cleanroom-baseline → envelope-v2
→ domain-adapters → cain-wiring-decision-policy → publish-candidates
→ cleanroom-final → contract-revalidation → e2e → n-plus-1
→ isolation-ids-contradiction → idempotency-failure → windows-smoke
→ hosted-ci → soak → attestation
```

---

## 11. Resultado

Gates comuns exigidos (núcleo C7.2):

```text
BLOCKERS_ZERO | STACK_BASELINE_FROZEN | LOCK_INTEGRITY | CORE_IDENTITY |
CLEANROOM_FINAL | HOSTED_CI | E2E | IDEMPOTENCY | RESTART_RECOVERY |
FAILURE_INJECTION | PROVENANCE | AUTHORITY_SEPARATION | FUTURE_CANARY |
PROTECTED_ARTIFACTS_UNCHANGED | SOAK | WINDOWS_SMOKE | SHARED_DEPENDENCY_CLEAR
| EVIDENCE_CONSISTENCY | SECRETS_CLEAN | CAPITAL_FORBIDDEN |
ENVELOPE_V2_CONFORMANCE | CAIN_INGESTION | CAIN_CONTAINMENT | DECISION_POLICY
| N_PLUS_1_DETERMINISTIC | NEGATIVE_RESULT_NEUTRALITY | CROSS_DOMAIN_ISOLATION
| DOMAIN_QUALIFIED_IDS | CONTRADICTION_PRESERVATION |
DOMAIN_CONTRACTS_PRESERVED
```

De onde vêm os que não têm seção própria: `BLOCKERS_ZERO` ← `FINDINGS.json`;
`STACK_BASELINE_FROZEN` ← fase `baseline`; `LOCK_INTEGRITY`/`CORE_IDENTITY` ←
`CORE_IDENTITY_REPORT.md`; `CLEANROOM_FINAL` ← fase `cleanroom-final`;
`SHARED_DEPENDENCY_CLEAR` ← veredito da SHARED-003; `EVIDENCE_CONSISTENCY` ←
script versionado que tira todos os números de `RAW_LOGS/`.

`QUALIFIED` pelas regras C7.1: gates do núcleo (todas as missões + Etapa B) em
`PASS`, `domain_attestations` com os três domínios e revalidação `PASS`,
`P0 = P1 = 0`, `capital_permission = false`, `training_started = false`.

Com isso e com as três da Etapa A, o stack está qualificado para o próximo
passo (decisão do dono). **Não iniciar treinamento. Não mover capital.**
