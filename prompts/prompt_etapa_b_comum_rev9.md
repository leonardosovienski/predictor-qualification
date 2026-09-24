# ETAPA B — PARTE COMUM ÀS TRÊS MISSÕES DE INTEGRAÇÃO (Rev 9)

Vale para `integration-crypto`, `integration-stocks` e `integration-brasileirao` (D-22). Cada missão tem um prompt
curto com o cabeçalho de C0.1 e o que é só dela; este arquivo vem junto e vale inteiro. Substitui
`prompt_etapa_b_integracao_rev8.md` (missão única, extinta pela D-22). O núcleo vale inteiro; os prompts só acrescentam.

Objetivo de cada missão: montar e qualificar **a orquestração de pesquisa de um domínio**. O CAIN propõe pesquisas
àquele predictor pelo envelope V2, o predictor decide e executa pelo circuito da Etapa A (admission → Ops → Core),
o resultado volta, o CAIN guarda na memória **daquele domínio** e decide o próximo passo (N+1). Tudo isso **sem quebrar**
nada que a Etapa A provou, sem misturar domínios e sem nunca virar autoridade sobre capital. Um único agente, sem subagentes.

---

## 0. Como trabalhar

* **C0 primeiro.** Falhou → `ABORTED`.
* Só conta o que rodou pelo runtime suportado (C2). Status `PASS | FAIL | NOT_RUN` (`BLOCKED: …` em `note`).
  Números de `RAW_LOGS/` (C20).
* Tudo por branch + PR; nunca merge, push em `main`, rebase ou force-push. Pode publicar releases `rc` de `cain`,
  `ecosystem-predictor` e do adapter do domínio da missão.
* **Pare e pergunte ao dono** quando: regra local conflitar (C19); o domínio precisar mudar fora dos `adapter_paths`
  (C24.4); o protocolo V2 precisar mudar; uma mudança no `cain` ou no `ecosystem-predictor` atingir uma integração
  já `QUALIFIED` de outro domínio (C14: as fases dela que os exercitam são refeitas e ela é reemitida).

---

## 1. Pré-condições comuns (além do C0 e das do prompt da missão)

* As três `QUALIFICATION_ATTESTATION.json` da Etapa A com `result = QUALIFIED` e os três contratos no `main`.
* `qualification/shared/ENVELOPE_V2_FREEZE.json` e `STACK_BASELINE_V2.<n>.json` no `main`.
* Nenhum issue bloqueante em `SHARED_ISSUES.json`.

---

## 2. Arquitetura: três orquestrações sobre um ecossistema

```text
                 ECOSYSTEM (contratos, envelope V2, registry, compatibilidade)
                                      │
          ┌───────────────────────────┼───────────────────────────┐
  integration-crypto          integration-stocks        integration-brasileirao
  CAIN[crypto]                CAIN[stocks]              CAIN[brasileirao]
  → cripto-predictor          → stocks-predictor        → brasileirao-predictor
  → Core + Ops                → Core + Ops              → Core + Ops
```

| Elemento | Compartilhado entre domínios? |
|---|---|
| código do CAIN, composition root, framework da DecisionPolicy | sim (criado em `integration-crypto`) |
| configuração da DecisionPolicy (allowlist, budget, cooldown, regras) | **por domínio** |
| memória / ResearchState (hipóteses, experimentos, evidência negativa, contradições, maturidade) | **por domínio** (namespace obrigatório) |
| envelope V2, contratos, Core, Ops | sim (congelados nesta etapa) |
| dados, hipóteses, features, modelos, custos, baselines, protocolo de avaliação, `capital_permission` | **nunca** |

* **DecisionPolicy em duas camadas:** a lógica genérica (novidade, duplicata, cooldown, incerteza, custo, falsificabilidade)
  fica no `cain`, igual para todos; a **configuração do domínio** diz o que existe naquele domínio (experimentos,
  handlers da `handler_allowlist` do contrato, dados, baselines, custos). Determinística e versionada (id + hash de
  código **e** de configuração), decide `ALLOW | BLOCK | ABSTAIN | REQUIRE_HUMAN | DUPLICATE | COOLDOWN` e emite
  receipt sem LLM (C9, C12).
* **Episódio:** cada ciclo proposta → task → resultado → decisão é um episódio numerado **por domínio**
  (`<domínio>/episode-<n>`), encadeado pelo `research_id`/correlação do envelope e reconstruível do log.
* **Aprendizado entre domínios não é desta etapa.** Nenhum achado de um domínio altera decisão de outro. Memória
  metodológica cross-domain, índice global de experimentos, maturidade L2–L4, loop de engenharia por CapabilityGap,
  prospective, shadow e capital são **fase posterior, com decisão nova do dono**. Nesta etapa, isso pode ser registrado
  como proposta no relatório, nunca implementado nem ligado.

---

## 3. Escopo e circuito

* `cain`, `ecosystem-predictor`: mudam (exceto `packages/research-protocol`, consumido da release congelada).
* O predictor **da missão**: só nos `adapter_paths` do contrato. Os outros dois predictors: **nada muda**.
* `core-predictor`, `predictor-ops`: congelados.

```text
CAIN → proposta → ResearchTaskV2 → TaskOutbox → transporte (ecosystem)
→ adapter do domínio → pedido do contrato → [circuito da Etapa A: admission → Ops → Core]
→ resultado → adapter → ResearchResultV2 → CAIN ResultInbox → memória do domínio
→ restart do CAIN → retrieval → DecisionPolicy → receipt → proposta N+1
```

---

## 4. Ponto de partida do `cain` (24/09; reconfirmar)

| Item | Onde | Observado |
|---|---|---|
| `TaskOutbox` / `ResultInbox` | `cain/src/cain/research_tasks.py`, `research_results.py` | V1, só testes; nenhum entrypoint alcança |
| Memória bitemporal com cubo por domínio (`as_of` obrigatório, log JCS com cadeia de hash) | PR #45 | no `main`; base natural do ResearchState por domínio |
| Aprovação humana durável, fork de runs | PR #48 | no `main` |
| Manifesto por chamada de LLM, record/replay | PR #49 | no `main` |
| **Loop de pesquisa governado** (`cain loop run/status/decide/holdout/verify`) | PR #50 | no `main`. **Executa o avaliador do predictor direto do CAIN**, pulando admission, Ops e Core: conflita com `CAIN_CONTAINMENT` ("o CAIN só propõe") |
| Achados em quarentena, bloqueio de reteste de hipótese encerrada, biblioteca de procedimentos | PR #51 | no `main`. Lê registros dos predictors por `git show` num commit fixado |
| DecisionPolicy, `cain research decision-receipt` | — | não existem |
| Instalação operacional | `C:\CAIN\` (PC 1) | nunca tocar nem usar como prova |

**Conflito do PR #50.** No runtime qualificado, nenhum caminho alcançável dos entrypoints pode executar código de avaliação
do domínio fora do circuito. A missão escolhe e registra uma saída: (a) redirecionar o loop para emitir `ResearchTaskV2`
e consumir `ResearchResultV2` (preferível: o ledger, a cascata, a quarentena e o bloqueio de reteste continuam valendo);
ou (b) cercar o modo de execução direta como ferramenta de laboratório fora do runtime qualificado, com teste provando
que ela não é alcançável. Nos dois casos, `CAIN_CONTAINMENT` prova isso. O PR #51 (leitura de registros versionados por
`git show`) precisa de parecer explícito no `CAIN_CONTAINMENT` ("nunca acessa banco de domínio"): leitura de arquivo
versionado num commit fixado, somente leitura, sem efeito no domínio.

---

## 5. Runtime e dados

* Linux primário: GitHub Actions ou VM na nuvem (D-9); `owner_linux` (PC 2) só onde o dado real do domínio é privado (D-19).
* Windows secundário: D-3 (CAIN local em `C:\QUALIFICACAO\runtime\integration-<domínio>\`); Stocks no `windows-latest` (D-1).
* Memória do CAIN da qualificação = banco novo por missão, nunca `C:\CAIN\dados`.
* Protegidos: o conjunto da Etapa A do domínio da missão, mesmos hashes de blob (`PROTECTED_ARTIFACTS_UNCHANGED`); os dos outros
  dois domínios também não mudam.

---

## 6. O que construir (a parte de cada missão está no prompt dela)

1. **Envelope V2** consumido da release congelada; **adapter** do domínio só nos `adapter_paths`, só pela `adapter_api`:
   V2 → pedido do contrato (com `client_ref`) e resultado → V2 com payload de domínio byte-idêntico.
   Gate `ENVELOPE_V2_CONFORMANCE`; `ENVELOPE_V2_CONFORMANCE_REPORT.md`.
2. **CAIN** com composition root real: `TaskOutbox`, `ResultInbox`, memória do domínio, retrieval e DecisionPolicy
   alcançáveis dos entrypoints.
3. **DecisionPolicy** (seção 2) e o comando `cain research decision-receipt` (sem LLM). Gate `DECISION_POLICY`;
   `DECISION_POLICY_REPORT.md`.

Registre as mudanças em `QUALIFICATION_CHANGELOG.md`.

---

## 7. Garantias

* **`CAIN_INGESTION`**: só schema V2 conhecido, task existente **do mesmo domínio**, correlação e provenance válidas.
* **`CAIN_CONTAINMENT`**: o CAIN só propõe; nunca escolhe handler, budget final, prioridade final ou capital; nunca lê
  banco de domínio; nunca executa código de avaliação do domínio fora do circuito (seção 4); ação fora da allowlist
  bloqueada e registrada.
* **`AUTHORITY_SEPARATION`**: estados operacional, científico e econômico guardados como vieram; nunca promovidos.
* **`CROSS_DOMAIN_ISOLATION`**: resultado de outro domínio nunca satisfaz task deste, e vice-versa. Testado contra os
  **outros dois** domínios: pelo runtime deles, se a integração deles já estiver `QUALIFIED`; senão, por fixtures V2
  congeladas (sha256 no `FROZEN_PARAMETERS`).
* **`DOMAIN_QUALIFIED_IDS`**: `crypto:H9`, `brasileirao:H9`, `stocks:H9` nunca se confundem; ID sem domínio rejeitado.
* **`CONTRADICTION_PRESERVATION`**: contradição fica como contradição, nunca decidida por maioria.
* **`NEGATIVE_RESULT_NEUTRALITY`**: sequência de `NO_EDGE`, `INCONCLUSIVE`, `NOT_READY`, `CLOSED_INSUFFICIENT_SAMPLE`,
  `INCONCLUSIVE_DATA_QUALITY` não aumenta budget, prioridade nem escopo além da policy congelada.
* **`FUTURE_CANARY`**: os canários do domínio nunca aparecem antes do cutoff na memória nem no retrieval.
* **`CAPITAL_FORBIDDEN`**: nenhum caminho concede capital.

---

## 8. E2E, N+1, idempotência, falhas

* **E2E** (`E2E`, `PROVENANCE`): só `final_wheels`, a partir dos entrypoints do CAIN e do consumidor; restart do CAIN e
  do consumidor no meio; ciclos intercalados com outro domínio (C10). `CAIN_ROUNDTRIP_REPORT.md`, `E2E_EVIDENCE/`.
* **N+1** (`N_PLUS_1_DETERMINISTIC`, C9): fixture congelado com resultados do domínio e, para o isolamento, dos outros dois;
  3 processos novos com receipt idêntico byte a byte.
* **Idempotência** (`IDEMPOTENCY`): retry, restart, entrega duplicada → nenhum segundo experimento, efeito ou resultado.
  IDs: research_id, task_id, request_id, admission_id, experiment_id, attempt_id, ops_run_id, result_id.
* **Falhas** (`FAILURE_INJECTION`, `RESTART_RECOVERY`): `FAILURE_MATRIX.json` congelada antes: antes do envio; entre envio
  e ACK; durante e depois da ingestão; durante a decisão; CAIN fora; consumidor fora; resultado duplicado ou fora de ordem;
  versão de schema errada; mesmo ID com payload diferente; envelope válido com task errada. Fail closed.

---

## 9. Revalidação do contrato (C24.3; `DOMAIN_CONTRACTS_PRESERVED`)

Do domínio da missão, nos `final_commits` desta missão, itens (a)–(f) de C24.3. `CONTRACT_REVALIDATION_REPORT.md` +
`domain_attestations[0].revalidation`. Falhou → pare; a Etapa A do domínio reabre (C24.4).

---

## 10. Soak, Windows, CI, segredos

* **Perfil** `QUALIFICATION_PROFILE_INTEGRATION_<CÓDIGO>_V1.json` (pisos C10, Etapa B) + ≥ 5 propostas via
  `cain research explain` (LLM, auditadas; não são gate). Tolerância zero: resultado de outro domínio aceito, ID ambíguo
  aceito, contradição decidida por maioria. Soak no Linux primário (`SOAK`).
* **Windows** (`WINDOWS_SMOKE`): E2E + restart no secundário do domínio.
* **CI** (`HOSTED_CI`): push/PR dos repos tocados + workflows de integração V2 criados aqui; os V1 aposentados (HYG-015) não entram.
* **Segredos** (`SECRETS_CLEAN`): zero achados.

---

## 11. Fases (C8)

```text
freeze-parameters → baseline → truth-map → cleanroom-baseline → envelope-v2
→ domain-adapter → cain-wiring-decision-policy → publish-candidates
→ cleanroom-final → contract-revalidation → e2e → n-plus-1
→ isolation-ids-contradiction → idempotency-failure → windows-smoke
→ hosted-ci → soak → attestation
```

---

## 12. Resultado

Gates exigidos (núcleo C7.2):

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

Origem dos que não têm seção própria: `BLOCKERS_ZERO` ← `FINDINGS.json`; `STACK_BASELINE_FROZEN` ← fase `baseline`;
`LOCK_INTEGRITY`/`CORE_IDENTITY` ← `CORE_IDENTITY_REPORT.md`; `CLEANROOM_FINAL` ← fase `cleanroom-final`;
`SHARED_DEPENDENCY_CLEAR` ← vereditos das SHARED; `EVIDENCE_CONSISTENCY` ← script versionado que tira todos os números
de `RAW_LOGS/`.

`QUALIFIED` pelas regras C7.1: todos os gates em `PASS`, uma `domain_attestations` (a do domínio) com revalidação
`PASS`, `P0 = P1 = 0`, `capital_permission = false`, `training_started = false`.

**Não iniciar treinamento. Não mover capital.**
