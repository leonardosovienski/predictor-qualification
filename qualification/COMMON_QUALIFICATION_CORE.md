# COMMON_QUALIFICATION_CORE — NÚCLEO COMUM DE QUALIFICAÇÃO (v2.1 — enxuto)

**v2.1 (2026-09-24, D-19):** C11 e C7.1 admitem o Linux do dono (`owner_linux`) como
ambiente primário **só** para dado real privado, sem direito de redistribuição. Nenhum
outro requisito mudou. C14 "Núcleo (versão)": as attestations revalidam no novo schema
e são reemitidas com o novo `common_core_sha256`, sem refazer fases.

**Supersedes (v2.0):** v1.3. Nenhuma missão foi qualificada sob a v1.3 (a única
execução terminou `ABORTED` no C0), então não há nada a revalidar.

**Foco desta versão:** provar que o stack **funciona** e que os resultados são
**confiáveis para ganhar dinheiro** — sem vazamento de futuro, sem ação
duplicada ou perdida, sem holdout contaminado, rodando as versões certas.
Saiu tudo que era cerimônia: assinaturas por chave, conta bot, revisores,
proteção de branch, reprodução independente, testes de ataque hostil,
reconciliação de evidência antiga e review assinado de mudanças.

Projeto de um dono só. **Aprovar = o dono fazer merge do PR no `main`.**

```text
Etapa A — domínio × Core × Ops (três missões, sem CAIN e sem envelope)
    crypto        cripto-predictor      + core-predictor + predictor-ops
    brasileirao   brasileirao-predictor + core-predictor + predictor-ops
    stocks        stocks-predictor      + core-predictor + predictor-ops
    → cada uma entrega um DOMAIN_RESEARCH_CONTRACT.json (C24)

Preparação — envelope V2 desenhado a partir dos três contratos

Etapa B — integração (uma missão)
    integration   cain + ecosystem-predictor + os três domínios + Core + Ops
```

---

## C0. PRÉ-VERIFICAÇÃO (antes de tudo)

1. **Hash do núcleo:** sha256 de `qualification/COMMON_QUALIFICATION_CORE.md`
   igual ao do prompt da missão (64 caracteres). Diferente = aborta. Se a única
   diferença for CRLF, corrigir o checkout (`.gitattributes` com
   `qualification/** text eol=lf`) e recalcular.
2. **Schema:** sha256 de `qualification/ATTESTATION_SCHEMA.json` =
   `3594e35044626264a18270ee4e079e653e3b940f1e7a72d36f2b70972f5bf970`.
3. **Arquivos no `main` do repositório de evidência:**
   `qualification/DECISIONS.json` e `qualification/HYGIENE.json`. Para as
   missões das Etapas A e B, todos os itens de `HYGIENE.json` em `DONE` e o
   baseline comum existente (C3).
4. **Pré-condições do prompt** da missão.

Qualquer falha → estado `ABORTED`, motivo em `qualification/<branch>/FINDINGS.json`
(se o repositório de evidência não existir, só na resposta — nada é gravado em
repositório de produto). Nenhuma fase roda depois de um C0 com falha.

O que está no `main` do repositório de evidência vale como aprovado pelo dono.
O agente **nunca** faz merge, push em `main`, rebase ou force-push; toda
mudança entra por branch + PR. O agente pode marcar item de higiene como
`DONE` no PR quando o critério de aceite tiver evidência — vale quando o dono
fizer merge.

### Layout do repositório de evidência (`predictor-qualification`, público)

```text
qualification/COMMON_QUALIFICATION_CORE.md
qualification/ATTESTATION_SCHEMA.json
qualification/DECISIONS.json
qualification/HYGIENE.json
qualification/shared/HYGIENE/<HYG-0xx>.md          (evidência da Fase 0)
qualification/shared/STACK_BASELINE_V1.json        (e V1.<n>)
qualification/shared/STACK_BASELINE_V2.<n>.json
qualification/shared/SHARED-002/CLEANROOM_REPORT.md
qualification/shared/SHARED_ISSUES.json            (C13)
qualification/shared/<issue_id>/SHARED_DEPENDENCY_VERDICT.json
qualification/shared/ENVELOPE_V2_FREEZE.json
qualification/<branch>/...                          (artefatos da missão, C16)
```

`<branch>` ∈ {`crypto`, `brasileirao`, `stocks`, `integration`}.

**Repositórios públicos:** nada de segredo (chaves de API, de exchange, de
casas de aposta, tokens, `.env`, `pipeline.env`, HMAC) em arquivo, log, commit,
relatório ou saída de CI. Dados grandes ou comprados não são versionados:
entram por caminho local + sha256.

## C1. REGRAS ABSOLUTAS

Não:

* treinar CAIN nem iniciar treinamento;
* mover capital, criar ordens, aprovar apostas — `capital_permission = false`;
* alterar hipótese congelada, thresholds, cutoff, vetores ou parâmetros
  **depois** de ver resultado (isso é overfitting disfarçado);
* tratar sucesso operacional como resultado científico, resultado científico
  como edge, ou edge como autorização de capital;
* aceitar comando/shell/módulo arbitrário vindo de pedido de pesquisa (a
  admission resolve para handler da allowlist);
* usar mocks/stubs de Core, Ops ou CAIN na prova E2E final (fault injection na
  borda é permitido e exigido);
* alterar instalação operacional, bancos operacionais, dados canônicos ou
  artefatos protegidos (C3.1, C15.1);
* escrever segredo em qualquer lugar (C0);
* violar regra local de repositório (C19).

Parâmetros, vetores de teste, perfil de soak e thresholds são congelados
**antes** da execução (C15). Ambiguidade de identidade, schema ou cutoff →
rejeitar (fail closed).

## C2. MATURIDADE

```text
NOT_PRESENT < DECLARED < IMPLEMENTED < INSTANTIATED < REACHABLE < EXERCISED < PROVEN
```

* **DECLARED** — documento diz que existe. **IMPLEMENTED** — o código existe.
* **INSTANTIATED** — criado em código de produção. **REACHABLE** — alcançável
  de um entrypoint de `[project.scripts]` ou serviço.
* **EXERCISED** — rodou em teste que monta os componentes à mão.
* **PROVEN** — rodou pelo runtime suportado (C3.1), a partir do entrypoint,
  sem montagem manual, com evidência.

Só PROVEN conta para gate. PASS de relatório antigo, de outra missão ou de
outro commit não conta — pode orientar investigação, nunca substitui execução.

## C3. BASELINE

**Baseline da missão** (fase `baseline`, antes de qualquer mudança): para cada
repo, HEAD, branch, limpo/sujo, versão, sha256 do `uv.lock`, wheels consumidas e
seus sha256, Python, SO, schemas, migrations, configuração relevante (sem
segredos). Saída `qualification/<branch>/STACK_BASELINE.json`.

**Baselines comuns:**

```text
STACK_BASELINE_V1    todos os repos depois da Fase 0. Base da Etapa A.
STACK_BASELINE_V1.n  se core-predictor ou predictor-ops mudar durante a Etapa A
                     (decisão do dono), ou numa reabertura de domínio (C24.4).
STACK_BASELINE_V2.0  no congelamento do envelope V2: final_commits das três
                     missões da Etapa A + release do protocolo V2. Base da Etapa B.
```

Durante a Etapa A, `core-predictor` e `predictor-ops` ficam **congelados**; a
missão só muda o próprio repo de domínio. Na Etapa B, `cain` e
`ecosystem-predictor` mudam livremente e os domínios **só** nos
`adapter_paths` (C24).

### C3.1 Runtime suportado × instalação operacional

* **Runtime suportado** = instalação limpa **só** com as wheels publicadas (C5)
  dos commits finais, num diretório de qualificação (D-3 Windows, D-9 Linux),
  executada pelos entrypoints de `[project.scripts]`.
* **Instalação operacional** (ex.: `C:\CAIN\`, `C:\Cripto\operacao`,
  `C:\STOCKS\data`, bancos do Brasileirão) nunca é usada como prova, nunca é
  escrita, nunca é atualizada pela qualificação.
* Rodar do checkout, com `PYTHONPATH` ou editable = diagnóstico, nunca PROVEN.

## C4. VERSÕES CERTAS (gates `LOCK_INTEGRITY`, `CORE_IDENTITY`)

Todo repo do stack tem `uv.lock` versionado; `uv lock --check` passa e
`uv sync --locked` instala sem resolver nada novo. Dependência declarada fora
do lock = bloqueio.

Para cada dependência entre repos do stack (Core, Ops, `predictor-research-*`,
`cain-research`, Ecosystem), a cadeia

```text
pyproject range ↔ tool.uv.sources (URL da release) ↔ uv.lock ↔ instalação do CI
↔ hash da wheel ↔ metadata instalado ↔ caminho do módulo em runtime
```

aponta para a mesma wheel. Pacote do stack não vem de índice público, `vendor/`
ou checkout de outro repo. Exceção: smoke da própria wheel recém-construída e
requirements exportados do lock com `--require-hashes`. Saída
`CORE_IDENTITY_REPORT.md`.

## C5. WHEELS PUBLICADAS E CLEANROOM

**Wheel publicada** = asset de uma release do GitHub do repo dono (tag +
asset), sha256 registrado. O agente **pode** publicar releases pré-release
(`rc`) dos repos que a missão altera; nunca sobrescreve asset existente (versão
nova sempre).

* **cleanroom-baseline** — diagnóstico do estado inicial.
* **cleanroom-final** — depois da última mudança de código, só com as wheels
  publicadas (fase `publish-candidates`). Gate `CLEANROOM_FINAL`. Mudança
  posterior invalida (C14).

Saída `CLEANROOM_REPORT.md`.

## C6. SEVERIDADE

```text
P0  quebra o que dá dinheiro ou faz perder: vazamento de futuro, resultado
    errado/duplicado/perdido, holdout ou artefato protegido alterado,
    versão errada rodando, segredo exposto
P1  defeito real que afeta resultado ou operação, sem violação observada
    (ex.: teste exigido ausente, evidência incompleta)
P2  defeito sem efeito em resultado ou operação
```

Gate `BLOCKERS_ZERO`: `P0 = 0` e `P1 = 0` abertos. Achados em
`FINDINGS.json` (id, severidade, descrição, evidência, status).

`QUALIFICATION_CHANGELOG.md`: o que o agente mudou, onde, por quê, commit e PR.
Toda afirmação de gate cita arquivo de evidência + sha256.

## C7. ATTESTATION

`qualification/<branch>/QUALIFICATION_ATTESTATION.json`, validada contra
`qualification/ATTESTATION_SCHEMA.json` (JSON Schema 2020-12). Status de gate:
`PASS | FAIL | NOT_RUN` (dependência externa que impede a execução: `NOT_RUN`
com `note` começando por `BLOCKED:`). Resultado: `QUALIFIED | NOT_QUALIFIED |
IN_PROGRESS` (este só em parciais).

### C7.1 Regras além do schema (conferidas por script)

1. `QUALIFIED` ⇔ todos os gates exigidos em `PASS`, `P0 = P1 = 0`, nenhum
   veredito compartilhado bloqueante.
2. `counts` bate com `FINDINGS.json` (status aberto).
3. Todo arquivo de evidência existe e o sha256 confere no commit da attestation.
4. Todo `final_wheels[*].sha256` confere com o asset da `url`, e as
   `final_wheels` cobrem todo pacote do stack instalado no runtime.
5. `environments`: um Linux `primary` e um Windows `secondary` (C11). `where =
   owner_linux` só com a D-19 e só na missão cujo dado real é privado.
6. `common_core_sha256` = sha256 desta versão.
7. Etapa A: `domain_contract_sha256` = sha256 do contrato no `main`.
   Etapa B: uma `domain_attestations` por domínio, cada uma de uma attestation
   da Etapa A `QUALIFIED`, com revalidação C24.3 em `PASS`.
8. Attestation reemitida depois de C14 aponta `supersedes_sha256` para a
   anterior, que nunca é apagada.

### C7.2 Gates (IDs fixos)

**Todas as missões:**

| Gate | O que prova |
|---|---|
| `BLOCKERS_ZERO` | nenhum P0/P1 aberto |
| `STACK_BASELINE_FROZEN` | baseline antes de qualquer mudança (C3) |
| `LOCK_INTEGRITY` / `CORE_IDENTITY` | versões certas (C4) |
| `CLEANROOM_FINAL` | instala e roda só com as wheels publicadas (C5) |
| `HOSTED_CI` | CI do GitHub verde nos commits do baseline e finais (C21) |
| `E2E` | circuito inteiro pelo runtime suportado, sem mocks nem montagem manual |
| `IDEMPOTENCY` | retry/restart/duplicata não geram segundo efeito |
| `RESTART_RECOVERY` | restart em cada ponto crítico recupera certo |
| `FAILURE_INJECTION` | a matriz de falhas da missão, injetada na borda |
| `PROVENANCE` | cada resultado diz de qual pedido, dado, wheel e commit veio |
| `AUTHORITY_SEPARATION` | falha do Ops não vira resultado válido; resultado científico não vira edge; edge não vira capital |
| `FUTURE_CANARY` | dado do futuro nunca aparece antes do cutoff |
| `PROTECTED_ARTIFACTS_UNCHANGED` | holdouts e artefatos congelados intactos (C15.1) |
| `SOAK` | C10 |
| `WINDOWS_SMOKE` | E2E + restart no Windows (C11) |
| `SHARED_DEPENDENCY_CLEAR` | nenhuma falha compartilhada bloqueante (C13) |
| `EVIDENCE_CONSISTENCY` | todo número vem de log bruto (C20) |
| `SECRETS_CLEAN` | nenhum segredo em repo, log, relatório ou CI (varredura + revisão) |
| `CAPITAL_FORBIDDEN` | nenhum caminho concede capital |

**Etapa A:** `DOMAIN_CONTRACT` (contrato completo, aprovado, conformidade verde,
C24) · `ADMISSION` (pedido resolve só para handler da allowlist) ·
`OPS_RUNTIME` (roda de fato pelo Ops: lock, timeout, heartbeat, attempt,
reconciliação) · `CORE_PARTICIPATION` (Core usado de fato) ·
`TEMPORAL_INTEGRITY` (cutoff/PIT respeitado em todo estado que afeta a previsão).

**Etapa B:** `ENVELOPE_V2_CONFORMANCE` · `CAIN_INGESTION` · `CAIN_CONTAINMENT`
(CAIN só propõe; nunca acessa banco de domínio nem executa fora da allowlist) ·
`DECISION_POLICY` · `N_PLUS_1_DETERMINISTIC` (C9) · `NEGATIVE_RESULT_NEUTRALITY`
(resultados negativos não inflam budget/escopo) · `CROSS_DOMAIN_ISOLATION` ·
`DOMAIN_QUALIFIED_IDS` (C18) · `CONTRADICTION_PRESERVATION` ·
`DOMAIN_CONTRACTS_PRESERVED` (C24.3).

**Gates de braço da Etapa A** (significado no prompt da missão):

```text
crypto:       CRYPTO_RUNTIME_WIRING, CRYPTO_OPS_FAILURE_VERDICT,
              CRYPTO_UNCOMFORTABLE_CASES, CRYPTO_ECONOMIC_METRICS,
              CRYPTO_NEGATIVE_CONTROLS, CRYPTO_SPLIT_BRAIN_CORRUPTION
brasileirao:  BR_OPS_REUSE, BR_KICKOFF_ORDERING, BR_TIMEZONE_INTEGRITY,
              BR_SAME_KICKOFF_ISOLATION, BR_METAMORPHIC, BR_CACHE_STATE,
              BR_FUTURE_INJECTION
stocks:       STOCKS_CORE_PIN, STOCKS_EXTERNAL_INTELLIGENCE_AXES, STOCKS_COLLECTION_MODE,
              STOCKS_UNIVERSE_IDENTITY, STOCKS_PIT_ADVERSARIAL, STOCKS_NEGATIVE_CONTROLS
```

### C7.3 Estados terminais

| Estado | Quando | Attestation |
|---|---|---|
| `QUALIFIED` | C7.1 regra 1 | final, `result = QUALIFIED` |
| `NOT_QUALIFIED` | algum gate `FAIL` ou P0/P1 aberto | final, `result = NOT_QUALIFIED` |
| `BLOCKED` | nenhum `FAIL`, mas algo externo impede (CI fora, ambiente, falha compartilhada sem veredito) | só o último parcial (`IN_PROGRESS`) com os bloqueios em `note` |
| `ABORTED` | C0 falhou | nenhuma; motivo em `FINDINGS.json` |

Sempre `capital_permission = false` e `training_started = false`.

## C8. CHECKPOINT

Cada fase grava seus artefatos + `ATTESTATION_PARTIAL_<phase>.json`
(`result = IN_PROGRESS`), sem sobrescrever os anteriores. Retomada continua de
`phases_completed`, sem mudar nada congelado. HEAD diferente do registrado →
novo baseline + C14.

## C9. N+1 DETERMINÍSTICO (Etapa B)

O gate usa a DecisionPolicy (C12) sobre um conjunto congelado de resultados dos
três domínios, com receipt de comando **sem LLM**: mesmo fixture + mesma policy
+ mesmo estado = mesmo receipt byte a byte em 3 processos novos. Caminho com LLM
só entra no soak, nunca como prova.

## C10. SOAK

Perfil congelado antes (`QUALIFICATION_PROFILE_<CODE>_V1.json`), no runtime
suportado, no ambiente primário. Pisos (a missão pode aumentar):

```text
Etapa A:  ciclos normais ≥ 20 | restarts ≥ 5 | pedidos duplicados ≥ 5
          | execuções por classe de falha relevante ≥ 3
Etapa B:  por domínio: ciclos ≥ 20 | duplicatas ≥ 5 | restarts do domínio ≥ 5
          | restarts do CAIN ≥ 5 | ciclos intercalados entre domínios ≥ 5
          | classes de falha relevantes ≥ 3 | propostas de LLM ≥ 5
```

Tolerância zero: efeito duplicado; resultado perdido; provenance quebrada;
ação não autorizada; contaminação entre domínios; corrupção silenciosa;
vazamento de futuro. Saída `SOAK_REPORT.md`.

## C11. AMBIENTES

**Primário:** Linux × Python 3.13 (GitHub Actions ou VM na nuvem, D-9; para
dado real privado sem direito de redistribuição, também o Linux do dono,
`owner_linux`, provisionado por `provision_linux_vm.sh`, D-19) —
qualificação completa e soak. **Secundário:** Windows × Python 3.13 — E2E +
restart. Crypto e Brasileirão: no Windows local (D-3). Stocks: job
`windows-latest` no GitHub Actions (D-1; o Windows local do Stocks não recebe
instalação). Não existe isenção: `WINDOWS_SMOKE` é `PASS`, `FAIL` ou `NOT_RUN`.

## C12. CAIN COMO CONSUMIDOR (Etapa B)

* **Admission:** schema conhecido, task existente do mesmo domínio, correlação e
  provenance válidas.
* **Memória:** guarda referências, resumos e contradições; nunca altera trial,
  dataset, baseline ou resultado do domínio.
* **DecisionPolicy:** determinística e versionada (id + hash); decide
  `ALLOW | BLOCK | ABSTAIN | REQUIRE_HUMAN | DUPLICATE | COOLDOWN` e emite receipt
  (C9). Se não existir, é criada no `cain` pela missão `integration`.
* **Contenção:** ação fora da allowlist do domínio = bloqueada e registrada.

## C13. FALHAS EM DEPENDÊNCIA COMPARTILHADA

Falha reproduzida em Core/Ops vai para `qualification/shared/SHARED_ISSUES.json`
(issue_id, dependência, wheel_sha256, missão dona, status). Bloqueia
`SHARED_DEPENDENCY_CLEAR` de todas as missões que usam a mesma wheel até o
veredito da missão dona em `qualification/shared/<issue_id>/SHARED_DEPENDENCY_VERDICT.json`:

```text
reproduções (ambiente × source/wheel, com contagem) | classificação:
environmental | test_only | flaky | regression | bad_install | unresolved
| causa raiz com evidência | caminhos de código afetados | missões afetadas | blocking
```

* `unresolved` e `regression` bloqueiam sempre.
* `flaky` bloqueia se o comportamento instável estiver em caminho que as
  missões usam em runtime; `test_only` (defeito só do teste, com causa
  demonstrada) e `environmental`/`bad_install` com causa demonstrada não
  bloqueiam.
* Proibido: aumentar timeout, pular teste ou marcar xfail sem causa raiz.
* Correção em Core/Ops durante a Etapa A: decisão do dono → `STACK_BASELINE_V1.<n>` + C14.

## C14. O QUE REFAZER QUANDO ALGO MUDA

| Mudança | Refazer |
|---|---|
| Wheel de Core ou Ops | nas missões afetadas: baseline, C4, cleanroom-final, E2E, restart, falhas que tocam Core/Ops, soak, Windows |
| Código do domínio X depois de `cleanroom-final` | publish-candidates, cleanroom-final e as fases que exercitam o código |
| Domínio X fora dos `adapter_paths` durante a Etapa B | reabre a Etapa A de X (C24.4) |
| Domínio X dentro dos `adapter_paths` na Etapa B | só C24.3 de X + fases da integração que usam X |
| Contrato de domínio | `DOMAIN_CONTRACT` de X + fases dependentes; congelamento do V2 revisto |
| `cain`, `ecosystem-predictor` ou envelope V2 | fases da integração que os exercitam + C24.3 |
| Núcleo (versão) | revalidar attestation no novo schema; refazer o que mudou de requisito |
| Ambiente (SO/Python) | novo baseline + tudo naquele ambiente |
| Parâmetro/vetor/perfil congelado | a fase inteira, como novo ciclo |

## C15. PARÂMETROS CONGELADOS

Primeira fase de toda missão: `freeze-parameters`. Grava
`qualification/<branch>/FROZEN_PARAMETERS.json` com todos os números e listas
do prompt (contagens, tolerâncias, janelas de falha, cutoff, decisões citadas,
lista inicial do conjunto protegido). Vetores gerados têm hash próprio.
**O agente mostra o arquivo ao dono antes de congelar.**

### C15.1 Conjunto protegido

* Lista inicial do prompt em `FROZEN_PARAMETERS.json`; lista completa em
  `PROTECTED_SET.json` ao fim de `truth-map`, antes de qualquer mudança.
* Identidade por **hash do blob git** (arquivo versionado) ou sha256 (não versionado).
* O conjunto só cresce. Item descoberto depois já alterado = P0.
* `PROTECTED_ARTIFACTS_UNCHANGED`: hashes iguais de `truth-map` até a
  attestation. Saída `PROTECTED_ARTIFACT_REPORT.md`.

## C16. ARTEFATOS MÍNIMOS

Em `qualification/<branch>/`:

```text
STACK_BASELINE.json            ARCHITECTURE_TRUTH_MAP.json
CORE_IDENTITY_REPORT.md        CLEANROOM_REPORT.md
PROTECTED_SET.json             PROTECTED_ARTIFACT_REPORT.md
FAILURE_MATRIX.json            E2E_EVIDENCE/
SOAK_REPORT.md                 HOSTED_CI_REPORT.md
FROZEN_PARAMETERS.json         FINDINGS.json
QUALIFICATION_CHANGELOG.md     QUALIFICATION_PROFILE_<CODE>_V1.json
RAW_LOGS/                      ATTESTATION_PARTIAL_<phase>.json
QUALIFICATION_ATTESTATION.json
```

Etapa A: + `DOMAIN_RESEARCH_CONTRACT.json`. Etapa B: +
`ENVELOPE_V2_CONFORMANCE_REPORT.md`, `DECISION_POLICY_REPORT.md`,
`CAIN_ROUNDTRIP_REPORT.md`, `CONTRACT_REVALIDATION_REPORT.md`.

## C17. (removida na v2.0 — evidência antiga só orienta, ver C2)

## C18. IDs COM DOMÍNIO

IDs de hipótese, trial e artefato circulam entre repos como `<domínio>:<id>`
(`crypto:H9`, `brasileirao:H9`, `stocks:H9`). Etapa A: o contrato declara o
prefixo e o resultado já sai com IDs qualificados (os repos não renomeiam IDs
internos). Etapa B: ID sem domínio = rejeitar; teste com o mesmo `H9` nos três.

## C19. REGRAS LOCAIS

`AGENTS.md`, `CLAUDE.md`, `LEIA_PRIMEIRO.md`, `COMECE_AQUI.md`, `RETOMAR_*.md` e
equivalentes dos repos e das pastas locais são obedecidos. Conflito com o
núcleo ou o prompt: o agente **para a fase e pergunta ao dono**; nunca escolhe
sozinho. A resposta vira uma entrada em `DECISIONS.json` (por PR).

## C20. NÚMEROS VÊM DOS LOGS (gate `EVIDENCE_CONSISTENCY`)

Todo número de relatório (testes, ciclos, contagens, métricas) sai de log bruto
em `RAW_LOGS/` por script versionado. Raw log nunca é editado.

## C21. CI HOSPEDADO (gate `HOSTED_CI`)

Workflows de `push`/`pull_request` dos repos da missão verdes no GitHub
Actions nos commits do baseline e nos `final_commits`, instalando com
`uv sync --locked`. Link do run + commit + `success`. Job pulado sem motivo =
falha; CI de outro SHA não vale. Saída `HOSTED_CI_REPORT.md`.

## C22. O QUE UM `QUALIFIED` GARANTE

Nos `final_commits` e `final_wheels` declarados, nos ambientes declarados, com
os vetores e perfis congelados, cada gate passou com evidência. **Não** garante
edge, lucro, ausência de defeitos fora dos vetores, nem comportamento em outros
commits ou dados. Relatório que afirme mais que isso = P1.

## C23. NOMES

| Missão (`branch`) | `stage` | Código | `envelope_version` | Baseline |
|---|---|---|---|---|
| `crypto` | A | `CRYPTO` | `NONE` | `STACK_BASELINE_V1[.n]` |
| `brasileirao` | A | `BR` | `NONE` | `STACK_BASELINE_V1[.n]` |
| `stocks` | A | `STOCKS` | `NONE` | `STACK_BASELINE_V1[.n]` |
| `integration` | B | `INTEGRATION` | `V2` | `STACK_BASELINE_V2.n` |

Fases: `^[a-z0-9_-]+$`.

## C24. CONTRATO DE PESQUISA DO DOMÍNIO

### C24.1 Conteúdo

`qualification/<branch>/DOMAIN_RESEARCH_CONTRACT.json`, aprovado pelo dono
(merge) ao fim da missão:

```text
domain_prefix         "crypto" | "brasileirao" | "stocks"
request_schema        JSON Schema do pedido — sem nada de CAIN, envelope ou transporte
requester_trust       "LOCAL_FILE_ONLY" na Etapa A
client_ref            campo opaco devolvido sem alteração; fora do idempotency_key
admission_policy      id, versão, sha256; decisões e motivos
handler_allowlist     request type → handler
entrypoint            script de [project.scripts] que lê pedidos em arquivo
adapter_api           função pública: pedido → resultado, pelo mesmo caminho do entrypoint
result_schema         core_facts / ops_facts / domain_facts separados; estados operacional,
                      científico e econômico distintos; IDs com domínio
result_states         enum fechado, com os negativos (NO_EDGE, INCONCLUSIVE, NOT_READY,
                      CLOSED_INSUFFICIENT_SAMPLE, INCONCLUSIVE_DATA_QUALITY + do domínio)
id_fields             request, admission, experiment, attempt, ops_run, result
temporal_contract     cutoff/as_of e a desigualdade PIT
idempotency_key       o que faz dois pedidos serem o mesmo (sem client_ref)
authoritative_result_source   de onde o resultado é relido após restart
adapter_paths         diretório(s) reservado(s) ao adapter da Etapa B; nunca vazio
adapter_entrypoints   scripts que a Etapa B pode criar, dentro de adapter_paths
conformance_suite     suíte com os vetores congelados de E2E, IDEMPOTENCY,
                      FUTURE_CANARY e TEMPORAL_INTEGRITY da missão
```

Regras de `adapter_paths`: (1) disjuntos do conjunto protegido, da suíte de
conformidade e de tudo alcançável do `entrypoint`; (2) nada fora deles importa
algo de dentro (grafo de imports); (3) o adapter só chama o domínio pela
`adapter_api`.

### C24.2 Na Etapa A

E2E entra pelo `entrypoint` com pedidos em arquivo (fixtures congeladas).
`DOMAIN_CONTRACT` = contrato completo + regras de `adapter_paths` + suíte verde
no runtime suportado + merge do dono.

### C24.3 Na Etapa B (revalidação por domínio)

(a) diff do domínio desde os `final_commits` da Etapa A só dentro dos
`adapter_paths` (exceto versão patch/pré-release, `adapter_entrypoints` e
dependências `predictor-research-*`/`cain-research` no `pyproject`/`uv.lock`);
(b) regras de `adapter_paths` valendo; (c) suíte de conformidade verde com as
wheels da integração; (d) o pedido que o adapter gera tem o mesmo hash canônico
do vetor da Etapa A (sem `client_ref`), o `client_ref` volta igual e o payload
de domínio no resultado V2 é byte-idêntico ao da `adapter_api`; (e) conjunto
protegido intacto; (f) CI do domínio verde. Falha → C24.4.

### C24.4 Reabertura

A integração para; o dono aprova `STACK_BASELINE_V1.<n>` com uma branch de
reabertura a partir dos `final_commits` da Etapa A; a missão do domínio refaz o
que C14 manda, emite nova attestation (`supersedes_sha256`); a branch entra em
`main` por merge; a integração retoma.
