# MISSÃO — ETAPA A: STOCKS × CORE × OPS (Rev 8 — enxuto)

```text
stage  = A
branch = stocks        (nome do braço no schema, não é branch Git)
núcleo = qualification/COMMON_QUALIFICATION_CORE.md v2.2
sha256 = d681e423499e202c735ee1f110311a9721019ef11e21ae824f4791bada7c7d2c
```

Objetivo: provar que o Stocks roda pesquisa **de verdade** por Core e Ops,
ponta a ponta, e que o resultado é **confiável para investir**: universo sem
viés de sobrevivência nem ativo do futuro, nenhum dado posterior ao `as_of`,
dado ainda não pronto nunca vira sinal, nada duplicado ou perdido, artefatos
congelados intactos. Sem CAIN e sem envelope (Etapa B). Você é o único agente;
não use subagentes. O núcleo vale inteiro; este prompt só acrescenta.

---

## 0. Como trabalhar

* **C0 primeiro** (núcleo C0). Falhou → `ABORTED`, sem rodar fase nenhuma.
* **Só conta o que rodou**: PROVEN pelo runtime suportado (C2). Código que
  "parece certo", teste que monta os componentes à mão, relatório antigo e CI
  de outro commit não fecham gate. Sem evidência → `FAIL` ou `NOT_RUN`, nunca `PASS`.
* Status: `PASS | FAIL | NOT_RUN` (`NOT_RUN` + `note: "BLOCKED: …"` quando algo
  externo impede). Todo número vem de `RAW_LOGS/` (C20).
* Tudo por branch + PR; nunca merge, push em `main`, rebase ou force-push. Você
  pode publicar releases pré-release (`rc`) do `stocks-predictor`.
* **Neste Windows não se instala nada**: não criar venv, não instalar Core,
  Ops nem dependências no Python local (regra do repo; D-1). Tudo que roda
  Python roda no GitHub Actions ou na VM Linux.
* **Pare e pergunte ao dono** quando: regra local conflitar (C19); algo
  congelado precisar mudar; Core ou Ops precisarem de correção.
* Se o código real contradisser este prompt, registre em `FINDINGS.json` e siga o código.

---

## 1. Escopo e circuito

```text
stocks-predictor   muda nesta missão
core-predictor     congelado (só a wheel publicada)
predictor-ops      congelado (só a wheel publicada)
```

```text
pedido em arquivo (conforme o contrato) → entrypoint instalado ([project.scripts])
→ admission do Stocks → handler da allowlist → job real no Predictor Ops
→ experimento do Stocks → Predictor Core → resultado (core/ops/domain facts)
→ persistência → processo termina → restart → releitura do MESMO resultado
```

Entrega central: `qualification/stocks/DOMAIN_RESEARCH_CONTRACT.json` (C24).

---

## 2. Pré-condições (além do C0)

* `qualification/HYGIENE.json` com tudo `DONE` — em especial **HYG-009**
  (`predictor-core>=3.2.1,<4`; em 22/09 estava `>=3.2,<4`) e **HYG-015**
  (`cain-export.yml` só `workflow_dispatch`).
* `STACK_BASELINE_V1.json`, `SHARED-002/CLEANROOM_REPORT.md`, `SHARED_ISSUES.json`.
* **SHARED-003** (timeout do Ops no Windows) é da missão `crypto`; você avança,
  mas `SHARED_DEPENDENCY_CLEAR` espera o veredito não bloqueante.

---

## 3. Ponto de partida (hipóteses — reconfirmar no baseline)

| Item | Observado em 22/09 |
|---|---|
| Core | `predictor-core` por release 3.2.1 (`tool.uv.sources` + `uv.lock`) |
| Ops | **não** é dependência; nenhum import de `predictor_ops` |
| `predictor-research-*` / `cain-research` | nenhum |
| Entrypoints | nenhum `[project.scripts]`; só o plugin `predictor.plugins` |
| CI | `.github/workflows/ci.yml` |
| External Intelligence | `EXTERNAL_INTELLIGENCE_TRIAL_READINESS_MATRIX.json` (21/09): B3_LENDING, CVM_VLMO, CVM_BUYBACK, CVM_CDA — todas `readiness: NOT_READY`, mesmo listadas sob `eligible_families`; CVM_ENTREGA e CVM_FCA_IDENTITY = suporte; CVM_IPE_METADATA = inelegível |
| Hipóteses | `stocks:H7 H9 H10 H12 H13` (embargo original); `stocks:H17 H18 H19` (pausadas); `stocks:H17 → INCONCLUSIVE_DATA_QUALITY` — não promover nada |

Elegibilidade vem **só** do campo `readiness`; o nome da chave não concede nada.

---

## 4. Runtime e dados

* Linux × Python 3.13 (D-9): GitHub Actions `ubuntu-latest`; VM na nuvem para o soak.
* Windows (D-1): job `windows-latest` × py3.13 no GitHub Actions.
* Clone de trabalho e cópia local da evidência em
  `C:\STOCKS\work\qualification\` (D-10); entregas em `C:\STOCKS\outputs`.
* **Dados imutáveis — nunca alterar:** `C:\STOCKS\DADOS_STOCKS.zip*`,
  `C:\STOCKS\data\`, `C:\STOCKS\data\CATALOG.json`. Trabalhar em cópias com
  sha256 (origem → cópia executada). Dado comprado/grande não vai para repo
  público: no CI entra por armazenamento com URL + sha256 em
  `FROZEN_PARAMETERS.json`, ou por fixture sintética congelada.
* Regras locais: `AGENTS.md`, `CLAUDE.md`, `C:\STOCKS\COMECE_AQUI.md` (C19).

---

## 5. Artefatos congelados (C15.1)

Lista inicial em `FROZEN_PARAMETERS.json`; completa em `PROTECTED_SET.json` ao
fim de `truth-map` (blob git; fora do git, sha256):

```text
RESEARCH_FREEZE.md   experiments/BIG_WINNER_*/frozen_signals/**
experiments/BIG_WINNER_IMPROVEMENT_PROGRAM_V1/V2_FINAL_FREEZE.json
experiments/BIG_WINNER_IMPROVEMENT_PROGRAM_V1/V2_SELECTION_FREEZE.yaml
trials.json   trials_v2.json   trials.harness_attestation.json
EXTERNAL_INTELLIGENCE_TRIAL_READINESS_MATRIX.json
EXTERNAL_INTELLIGENCE_TRIAL_READINESS_PROTOCOL.json
research/session-20260907/deliverables/historical-protected-integrity.json
research/session-20260907/deliverables/real-integration-protected-integrity.json
research/session-20260907/scripts/verify_history_protected.py
research/session-20260907/scripts/verify_real_protected.py
+ os dados imutáveis do §4
```

Rodar também `verify_history_protected.py` e `verify_real_protected.py` como
checagem extra. Mudou algo protegido = P0. Gate `PROTECTED_ARTIFACTS_UNCHANGED`.

---

## 6. Baseline, mapa real e versões

* **baseline:** `STACK_BASELINE.json` (C3). Gate `STACK_BASELINE_FROZEN`.
* **truth-map:** código **e** runtime de: construção do universo, fatores,
  ranking, BIG_WINNER, frozen V2, prospectivo/sombra, Trial Registry, External
  Intelligence, Core, qualquer uso de Ops, plugin. `ARCHITECTURE_TRUTH_MAP.json`,
  `PROTECTED_SET.json`.
* **Versões** (C4): medir antes da mudança (Core declarado/lock/wheel; Ops
  ausente) e de novo depois de adicionar o Ops, antes do E2E. Gates
  `LOCK_INTEGRITY`, `CORE_IDENTITY`, **`STOCKS_CORE_PIN`** (range, fonte, lock e
  wheel batem em `predictor-core 3.2.1`). `CORE_IDENTITY_REPORT.md`.

---

## 7. O que construir

1. **Predictor Ops** como dependência pela wheel publicada: declarado,
   `tool.uv.sources` com a URL da release, `uv.lock` atualizado.
2. **Admission** do Stocks: decide tipo, handler, budget, prioridade e
   referências. O pedido nunca escolhe handler, shell, import, SQL, path, URL,
   budget final, prioridade final ou capital. Gate `ADMISSION`.
3. **Handler** da allowlist rodando como **job real do Ops** (gate `OPS_RUNTIME`:
   lock, timeout, heartbeat, retry, reconciliação vindos do Ops).
4. **Entrypoint** em `[project.scripts]` que lê pedido em arquivo.
5. Diretório reservado de `adapter_paths` para a Etapa B.

Registre cada mudança em `QUALIFICATION_CHANGELOG.md`.

---

## 8. Contrato (C24)

Todos os campos de C24.1, `domain_prefix = stocks`. O `request_schema` cobre,
sem transporte: identidade do universo, `as_of`, snapshot do dataset,
fatores/features, ranking/modelo, alvo/horizonte, protocolo de seleção,
baseline, custos, trial, metadados PIT. `result_states` inclui
`INCONCLUSIVE, NO_EDGE, NOT_READY, CLOSED_INSUFFICIENT_SAMPLE,
INCONCLUSIVE_DATA_QUALITY` — nenhum vira sucesso. Teste automático de imports:
nada que o entrypoint alcança importa `cain`, `research_protocol`, envelope ou
`adapter_paths`. Gate `DOMAIN_CONTRACT` (o dono aprova com o merge do
contrato, fase `contract-sign-off`).

---

## 9. Core e separação

Core real (gate `CORE_PARTICIPATION`): trial/evaluation identity, validação
temporal, estado científico. O Core não decide universo, ranking nem capital;
falha do Ops nunca vira resultado científico (gate `AUTHORITY_SEPARATION`).
`capital_permission = false` (gate `CAPITAL_FORBIDDEN`).

---

## 10. Garantias do domínio

* **`STOCKS_EXTERNAL_INTELLIGENCE_AXES`** — classificar cada família em eixos
  independentes: ingestão, armazenamento PIT, QA, capacidade, coleta contínua,
  elegibilidade para trial, uso no modelo, uso no contrato. Um eixo pronto não
  promove outro ("coletado" ≠ PIT_STRICT ≠ elegível). Não exige família READY.
  `EXTERNAL_INTELLIGENCE_READINESS.json`.
* **`STOCKS_COLLECTION_MODE`** — `COLLECTION_ONLY` pode coletar, validar,
  persistir e monitorar; nunca alimenta trial, ranking, portfólio ou capital.
  `TRIAL_CONSUMPTION` só por família com todos os requisitos congelados
  satisfeitos. Se 0 famílias `READY`: soak em `COLLECTION_ONLY` e 0 trials
  elegíveis — isso é o certo, não falha. Zero consumo de dado inelegível.
  `COLLECTION_ONLY_REPORT.md`.
* **`STOCKS_UNIVERSE_IDENTITY`** — mesma entrada + mesmo `as_of` = mesma lista
  e mesmo hash do universo; entradas/saídas só por eventos com
  `available_at ≤ as_of`; delistados presentes quando existiam; troca de ticker
  e CNPJ preserva a identidade. `UNIVERSE_IDENTITY_REPORT.md`.
* **`STOCKS_PIT_ADVERSARIAL`** + **`TEMPORAL_INTEGRITY`** — tentar quebrar de
  propósito: constituinte do futuro, ticker do futuro, delistado omitido, IPO
  antes da listagem, CNPJ/ticker futuro, documento CVM com `available_at`
  posterior, entrega atrasada, backfill, republicação, revisão da fonte,
  `first_seen`/`available_at` corrompidos, `HISTORICAL_ONLY` promovido a
  `PIT_STRICT`, registro oficial duplicado, conflito de identidade. Caso
  obrigatório: onde a matriz rebaixou `PIT_STRICT` para `HISTORICAL_ONLY`, o
  pipeline respeita o estado **efetivo**. Uma violação basta para falhar.
  `PIT_ADVERSARIAL_REPORT.md`.
* **`FUTURE_CANARY`** — `FUTURE_CANARY_STOCKS_001` só depois do cutoff;
  procurar em snapshot, features, universo, ranking, entrada do modelo, trial,
  artefato e resultado. Apareceu antes = P0.
* **`STOCKS_NEGATIVE_CONTROLS`** — labels embaralhados, ablação temporal,
  ablação de feature, perturbação do universo; seeds, critérios e
  aplicabilidade congelados antes. Resultado estável com labels embaralhados é
  investigado, nunca comemorado. `NEGATIVE_CONTROLS_REPORT.md`.

---

## 11. E2E, idempotência e falhas

* **E2E** (gates `E2E`, `PROVENANCE`): só `final_wheels`; entra pelo
  entrypoint com pedido em arquivo; não importa componentes internos nem monta
  o pipeline; persiste, reinicia, relê o mesmo resultado (identidade + hash).
  `E2E_EVIDENCE/`.
* **Idempotência** (gate `IDEMPOTENCY`): retry, restart, duplicata e reentrega
  do mesmo pedido lógico (pela `idempotency_key`, sem `client_ref`) não criam
  segundo experimento nem resultado; contagens antes/depois.
* **Falhas** (gates `FAILURE_INJECTION`, `RESTART_RECOVERY`):
  `FAILURE_MATRIX.json` congelada antes; injeção na borda: crash da admission,
  da materialização e do Ops, timeout do Ops, crash na gravação do artefato e
  do resultado, pedido duplicado e fora de ordem, versão de schema errada,
  artefato corrompido, DB lock, falha de escrita em disco. Zero duplicata, zero
  perda, zero mudança em congelado.

---

## 12. Soak, Windows, CI, segredos

* **Perfil** `QUALIFICATION_PROFILE_STOCKS_V1.json` (congelado antes): 20
  ciclos normais, 5 restarts, 5 duplicados, 3 por classe de falha relevante, 3
  timeouts, 3 família-não-pronta, 5 coletas válidas em `COLLECTION_ONLY`; 0
  trial elegível enquanto nenhuma família estiver READY (com o motivo). Soak na
  VM Linux; tolerância zero para violação PIT, contaminação do universo e
  mudança em congelado (gate `SOAK`).
* **Windows** (gate `WINDOWS_SMOKE`): E2E + restart + releitura com as final
  wheels num job `windows-latest` × py3.13 do GitHub Actions (D-1). Vale como
  PASS/FAIL normal.
* **CI** (gate `HOSTED_CI`): workflows de push/PR de Stocks, Core e Ops verdes
  no baseline e nos `final_commits`.
* **Segredos** (gate `SECRETS_CLEAN`): varredura nos commits, logs e relatórios;
  zero achados.

---

## 13. Fases (C8)

```text
freeze-parameters → baseline → truth-map → dependency-identity-baseline
→ cleanroom-baseline → contract-admission-ops-entrypoint → dependency-identity-final
→ publish-candidates → cleanroom-final → e2e → pit-universe-canary-negative
→ idempotency-failure → windows-smoke → hosted-ci → soak → contract-sign-off
→ attestation
```

* `freeze-parameters`: mostre ao dono o `FROZEN_PARAMETERS.json` antes de congelar.
* `publish-candidates`: releases `rc` novas, sha256 registrado.
* Mudou código depois de `cleanroom-final` → C14.

---

## 14. Artefatos

C16 do núcleo, mais: `DOMAIN_RESEARCH_CONTRACT.json`, `EXTERNAL_INTELLIGENCE_READINESS.json`,
`COLLECTION_ONLY_REPORT.md`, `UNIVERSE_IDENTITY_REPORT.md`, `PIT_ADVERSARIAL_REPORT.md`,
`NEGATIVE_CONTROLS_REPORT.md`.

---

## 15. Resultado

`QUALIFIED` só pelas regras C7.1: todos os gates do núcleo (todas as missões +
Etapa A) e os do braço em `PASS`:

```text
STOCKS_CORE_PIN | STOCKS_EXTERNAL_INTELLIGENCE_AXES | STOCKS_COLLECTION_MODE
| STOCKS_UNIVERSE_IDENTITY | STOCKS_PIT_ADVERSARIAL | STOCKS_NEGATIVE_CONTROLS
```

Gates comuns exigidos (núcleo C7.2):

```text
BLOCKERS_ZERO | STACK_BASELINE_FROZEN | LOCK_INTEGRITY | CORE_IDENTITY |
CLEANROOM_FINAL | HOSTED_CI | E2E | IDEMPOTENCY | RESTART_RECOVERY |
FAILURE_INJECTION | PROVENANCE | AUTHORITY_SEPARATION | FUTURE_CANARY |
PROTECTED_ARTIFACTS_UNCHANGED | SOAK | WINDOWS_SMOKE | SHARED_DEPENDENCY_CLEAR
| EVIDENCE_CONSISTENCY | SECRETS_CLEAN | CAPITAL_FORBIDDEN | DOMAIN_CONTRACT |
ADMISSION | OPS_RUNTIME | CORE_PARTICIPATION | TEMPORAL_INTEGRITY
```

De onde vêm os que não têm seção própria: `BLOCKERS_ZERO` ← `FINDINGS.json`;
`STACK_BASELINE_FROZEN` ← fase `baseline`; `LOCK_INTEGRITY`/`CORE_IDENTITY` ←
`CORE_IDENTITY_REPORT.md`; `CLEANROOM_FINAL` ← fase `cleanroom-final`;
`SHARED_DEPENDENCY_CLEAR` ← veredito da SHARED-003; `EVIDENCE_CONSISTENCY` ←
script versionado que tira todos os números de `RAW_LOGS/`.

`P0 = P1 = 0`, `capital_permission = false`, `training_started = false`.
Estados terminais: C7.3.

Resposta final, curta:

```text
estado terminal | result da attestation (ou "nenhuma")
stocks final_commit + wheel (url, sha256) | core e ops (versão, sha256)
gates: PASS / FAIL / NOT_RUN (os que não passaram, com motivo)
famílias READY: n (e quais) | violações PIT: nenhuma | encontradas (onde)
P0 / P1 abertos | o que falta o dono fazer
```

**Não iniciar treinamento. Não mover capital.**
