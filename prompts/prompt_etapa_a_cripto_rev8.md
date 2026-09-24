# MISSÃO — ETAPA A: CRIPTO × CORE × OPS (Rev 8 — enxuto)

```text
stage  = A
branch = crypto        (nome do braço no schema, não é branch Git)
núcleo = qualification/COMMON_QUALIFICATION_CORE.md v2.2
sha256 = d681e423499e202c735ee1f110311a9721019ef11e21ae824f4791bada7c7d2c
```

Objetivo: provar que o Cripto roda pesquisa **de verdade** por Core e Ops,
ponta a ponta, e que o resultado é **confiável para decidir dinheiro**: sem
vazamento de futuro, sem resultado duplicado ou perdido, sem hipótese
congelada mexida, com custos reais separando lucro bruto de líquido. Sem CAIN e
sem envelope (Etapa B). Você é o único agente; não use subagentes. O núcleo
vale inteiro; este prompt só acrescenta.

---

## 0. Como trabalhar

* **C0 primeiro** (núcleo C0). Falhou → `ABORTED`, sem rodar fase nenhuma.
* **Só conta o que rodou**: PROVEN pelo runtime suportado (C2). Código que
  "parece certo", teste que monta os componentes à mão, relatório antigo e CI
  de outro commit não fecham gate. Sem evidência → `FAIL` ou `NOT_RUN`, nunca
  `PASS`.
* Status de gate: `PASS | FAIL | NOT_RUN`. Algo externo impede (CI fora do ar,
  ambiente indisponível, veredito pendente) → `NOT_RUN` com `note:
  "BLOCKED: …"`.
* Todo número vem de log bruto em `RAW_LOGS/` (C20).
* Tudo por branch + PR; nunca merge, push em `main`, rebase ou force-push. Você
  pode publicar releases pré-release (`rc`) do `cripto-predictor`.
* **Pare e pergunte ao dono** quando: uma regra local conflitar com o núcleo
  (C19); algo congelado precisar mudar; Core ou Ops precisarem de correção; a
  ação for irreversível fora dos clones de qualificação.
* Se a arquitetura real contradisser este prompt, registre a divergência em
  `FINDINGS.json` e siga o código real. Não force o código a parecer com o texto.

---

## 1. Escopo e circuito

```text
cripto-predictor   muda nesta missão
core-predictor     congelado (só a wheel publicada)
predictor-ops      congelado (só a wheel publicada)
```

Circuito a provar pelo runtime suportado (C3.1), só com wheels publicadas:

```text
pedido em arquivo (conforme o contrato) → entrypoint instalado ([project.scripts])
→ admission do Cripto → referências com hash → handler da allowlist
→ job real no Predictor Ops → Predictor Core → resultado com fatos separados
→ persistência → processo termina → restart → releitura do MESMO resultado
```

Entrega central: `qualification/crypto/DOMAIN_RESEARCH_CONTRACT.json` (C24).

---

## 2. Pré-condições (além do C0)

* `qualification/HYGIENE.json` com tudo `DONE` — em especial **HYG-003**
  (`predictor-research-protocol` com URL da release em `tool.uv.sources` e no
  `uv.lock`; sem `cain-research`; `tests/test_research_execution.py` em
  `legacy/v1_integration/`, fora da coleta) e **HYG-015** (`integration-audit.yml`
  só `workflow_dispatch`).
* `qualification/shared/STACK_BASELINE_V1.json`,
  `qualification/shared/SHARED-002/CLEANROOM_REPORT.md` e
  `qualification/shared/SHARED_ISSUES.json` (com a SHARED-003 da HYG-008).

---

## 3. Ponto de partida (hipóteses — reconfirmar no baseline)

Observado em 22/09/2026 no `main` (`acdf289`):

| Item | Onde | Estado observado |
|---|---|---|
| `AdmissionStore` | `GarimpoInvestimentos/research_admission.py` | existe; só usado em testes; importa `research_protocol` (`verify_task`, linhas 15 e 256) |
| `ReferenceStore`, `ResearchExecutor` | `GarimpoInvestimentos/research_execution.py` | idem; importam `research_protocol` (`validate_result`, linhas 20 e 326) |
| armazenamento de resultado / `ResultOutbox` | `GarimpoInvestimentos/research_results.py` | acoplado a `ResearchResultV1` e `sign_result` |
| handler | `GarimpoInvestimentos/research_worker.py` (`main`, linha 178) | fora de `[project.scripts]` |
| recuperação | `GarimpoInvestimentos/research_recovery.py` | existe |
| entrypoints | `cripto-predictor`, `cripto-predictor-job` | reconfirmar |
| dependências | Core 3.2.1 e Ops 4.2.1 por release; `predictor-research-protocol==1.0.3rc1` declarado **sem** fonte nem lock (HYG-003 corrige) | reconfirmar |

Achados antigos úteis para orientar (não valem como prova): E2E antigo era
montado em fixture; contagens divergentes para o mesmo commit (`1614 passed, 1
skipped` × `1580 passed, 7 skipped`) — descubra qual é a real.

---

## 4. Runtime e dados

* Linux × Python 3.13 (D-9): GitHub Actions `ubuntu-latest`; VM na nuvem para o soak.
* Windows × Python 3.13 (D-3): `C:\Cripto\qualificacao\runtime\`.
* Clone de trabalho: `C:\Cripto\qualificacao\cripto-predictor`.
* Dados: só cópias com sha256 registrado (origem → cópia). A execução final não
  depende de conteúdo da rede que possa mudar.
* **Não tocar:** `C:\Cripto\operacao`, `C:\Cripto\pesquisa-20260909`,
  `C:\Cripto\restaurado-20260908`, `C:\Cripto\configuracao\pipeline.env`
  (nunca ler nem copiar segredos).
* Regras locais: `C:\Cripto\AGENTS.md`, `LEIA_PRIMEIRO.md`, `RETOMAR_NO_CODEX.md`
  e os arquivos de regra do repo (C19).

---

## 5. Hipóteses e artefatos congelados (C15.1)

Lista inicial em `FROZEN_PARAMETERS.json`; lista completa em `PROTECTED_SET.json`
ao fim de `truth-map` (hash de blob git):

```text
charters/**   observation_plans/**   observation_reports/**
CR_RESEARCH_FREEZE.md   CR_FREEZE_INDEX.md   docs/EVIDENCE_REGISTRY.md
docs/HYPOTHESES.md   docs/case_studies/**   docs/evidence/**/*freeze*.json
+ tudo que esses documentos declarem congelado
```

Estado científico esperado (`charters/scientific_state.json`):

```text
crypto:H1 H2 H3 H5 CLOSED_NO_GO | crypto:H4 H6 H9 CLOSED_INSUFFICIENT_SAMPLE
crypto:H7 H8 REGISTERED_NOT_ACTIVATED | frozen: crypto:funding_oi_hmm_v3
capital_authorized: false
```

Nenhuma hipótese encerrada é reaberta (`scripts/check_reopen_dossier.py`
continua sendo o portão). Mudou algo protegido = P0. Gate
`PROTECTED_ARTIFACTS_UNCHANGED`.

---

## 6. SHARED-003 — falha do Ops no Windows (comece cedo)

Esta missão dá o veredito; Brasileirão e Stocks esperam por ele (C13).

Falha: `predictor-ops` `tests_v2/test_runner.py::test_timeout_and_truncation`
(Windows local `86 passed / 1 failed`; CI Linux e `windows-latest` verdes em
`7266a20`). Importa para dinheiro porque é o **timeout do Ops no Windows** —
um job travado que não morre.

Matriz congelada (fase `ops-failure`), um log por execução:

```text
Linux × py3.13 × source          10×
Linux × py3.13 × wheel 4.2.1     10×
Windows × py3.13 × source        10×   (local)
Windows × py3.13 × wheel 4.2.1   10×   (local)
windows-latest × py3.13          1×    (workflow do repo de evidência)
suíte tests_v2 completa          1× por combinação local
```

Hipóteses a testar: término do filho × árvore de processos no Windows;
antivírus atrasando o spawn além de 0,2 s; `exit_code 124` dependente de
plataforma; leitura bloqueante de stdout/stderr depois do timeout; contagem de
bytes com `\r\n`.

Classificação (C13): `environmental | test_only | flaky | regression |
bad_install | unresolved`, com causa demonstrada por intervenção A/B ou trace —
"no CI passa" não é causa. Diga explicitamente se o **job real** do Ops (não só
o teste) mata o processo e trunca a saída no Windows; é isso que decide se
bloqueia.

Proibido: aumentar timeout, `skip`, `xfail`, afrouxar assert. Se o Ops precisar
de correção: pare e pergunte ao dono (vira release nova + `STACK_BASELINE_V1.<n>`).

Saídas: `OPS_FAILURE_REPORT.md`,
`qualification/shared/SHARED-003/SHARED_DEPENDENCY_VERDICT.json`,
`SHARED_ISSUES.json` atualizado. Gate `CRYPTO_OPS_FAILURE_VERDICT`.

---

## 7. Baseline e mapa real

* **baseline:** `STACK_BASELINE.json` (C3) + `git status` antes de qualquer
  mudança. Gate `STACK_BASELINE_FROZEN`.
* **truth-map:** busca no código **e** trace em runtime de cada componente do §3
  e do circuito. `ARCHITECTURE_TRUTH_MAP.json` (nível C2 de cada um, onde é
  instanciado, quem chama), `PROTECTED_SET.json`, `CORE_IDENTITY_REPORT.md`
  (C4; gates `LOCK_INTEGRITY`, `CORE_IDENTITY`).

---

## 8. Domínio sem envelope + composição real

Admission, handler, persistência e recuperação **não podem depender do
envelope**: remover `research_protocol.verify_task`, `validate_result`,
`sign_result`, `ResearchTaskV1`, `ResearchResultV1` desses módulos. Os schemas
de pedido e resultado são do Cripto (não alias do V1). Conversão para envelope,
se existir, vai para `adapter_paths`.

Teste automático: a closure **transitiva** de imports de tudo que o
`entrypoint` alcança não chega em `research_protocol`, `cain`, envelope do
ecosystem nem em `adapter_paths`.

Composition root real, a partir de um entrypoint novo em `[project.scripts]`
que lê pedidos em arquivo, instanciando `AdmissionStore`, `ReferenceStore`,
`ResearchExecutor`, handler, armazenamento de resultado e recuperação. Use o
que já existe; não crie segunda implementação. Gate `CRYPTO_RUNTIME_WIRING`
(instanciado → alcançável → exercitado → PROVEN pela wheel instalada).

Registre cada mudança em `QUALIFICATION_CHANGELOG.md`.

---

## 9. Contrato (C24)

`qualification/crypto/DOMAIN_RESEARCH_CONTRACT.json` com todos os campos de
C24.1, `domain_prefix = crypto`. Congelar também: nome do entrypoint, formato e
pasta do pedido, exit codes, comportamento para pedido inválido, duplicata e
conflito. Após restart, o resultado é **relido** do
`authoritative_result_source`, nunca recalculado. Gate `DOMAIN_CONTRACT` (o dono
aprova com o merge do PR do contrato, fase `contract-sign-off`).

---

## 10. Admission e referências

A policy é do Cripto e decide: tipo de pedido, handler, budget, prioridade,
referências aceitas, cutoff. O pedido declara intenção (hipótese, dataset,
cutoff, parâmetros permitidos pelo schema) e nunca escolhe comando, módulo,
path, URL, handler fora da allowlist ou capital. Pedidos válidos e inválidos
pelo entrypoint real. Gate `ADMISSION`.

Referência aceita tem digest esperado e digest materializado. Falha fechada
para: hash diferente, objeto ausente, referência de outro pedido, conteúdo
alterado depois de materializado.

---

## 11. Ops, Core e estados separados

* **Ops** (gate `OPS_RUNTIME`): o job roda de fato pelo Ops da wheel congelada;
  registrar `ops_run_id`, attempt, lock, timeout, heartbeat, estado terminal,
  reconciliação — produzidos pelo Ops, não recriados pelo Cripto.
* **Core** (gate `CORE_PARTICIPATION`): trial/evaluation identity, validação
  temporal e estado científico vêm do Core real; correlacionar
  `request_id → experiment_id → trial → core facts → result_id`.
* **Estados separados** (gates `AUTHORITY_SEPARATION`,
  `CRYPTO_UNCOMFORTABLE_CASES`). Antes dos testes, congele
  `AUTHORITY_STATE_MATRIX.json` (combinações permitidas e proibidas). Pelo
  runtime final, ≥ 3 ciclos de cada:

```text
CASO A  Ops SUCCEEDED / Core INCONCLUSIVE / Cripto NO_EDGE
CASO B  retorno bruto > 0 / retorno líquido < 0
CASO C  Ops FAILED ou TIMEOUT → nenhum estado científico nem econômico favorável
```

Nunca: Ops ok ⇒ ciência ok ⇒ edge ⇒ capital. `capital_permission = false`
(gate `CAPITAL_FORBIDDEN`).

---

## 12. E2E, idempotência, falhas e corrupção

* **E2E** (gates `E2E`, `PROVENANCE`): só `final_wheels`; entra pelo entrypoint
  instalado com pedido em arquivo; sem editable, `PYTHONPATH`, mocks ou teste
  montando o pipeline. Processo termina, reinicia em processo novo e relê o
  mesmo resultado (mesmo pedido, experimento, resultado e provenance).
  Evidência em `E2E_EVIDENCE/`.
* **Idempotência** (gate `IDEMPOTENCY`): mesma key + mesmo conteúdo (retry,
  restart, duplicata) → 1 experimento e 1 resultado (attempts podem variar);
  mesma key + conteúdo diferente → conflito, nunca sobrescreve; crash entre
  efeito e dedupe → efeito lógico único por transação ou journal + reconciliação.
* **Falhas** (gates `FAILURE_INJECTION`, `RESTART_RECOVERY`): congele
  `FAILURE_MATRIX.json` antes; injete na borda (sem mock de Core/Ops) antes e
  depois do commit da admission, durante a materialização, antes/durante/depois
  do Ops, timeout e crash do Ops, durante e depois da gravação do resultado.
  Em cada uma: falha detectada, recuperação segura, nada perdido, nada duplicado.
* **Corrupção** (gate `CRYPTO_SPLIT_BRAIN_CORRUPTION`): DB diz que existe / FS
  não, e vice-versa; artefato modificado; hash errado; referência de outra
  pesquisa; resultado com metadata inconsistente → falha fechada, sem reparo
  silencioso.

---

## 13. Validade científica e dinheiro

* **Temporal** (gate `TEMPORAL_INTEGRITY`): PIT, cutoff, oracle separado,
  previsão só depois do sinal válido. Reexecutar no runtime suportado:
  `tests/test_dpl*.py`, `tests/test_v3_wfa_purge_contract.py`,
  `tests/test_permutation_placebo_control.py`, `tests/test_pbo.py`,
  `tests/test_gate_power.py`.
* **Future canary** (gate `FUTURE_CANARY`): `FUTURE_CANARY_CRYPTO_001` só em
  dado posterior ao cutoff; procurar antes do cutoff no dataset, referências,
  features, estado do modelo, entradas do Core e resultado. Apareceu = P0.
* **Métricas econômicas** (gate `CRYPTO_ECONOMIC_METRICS`): taxas, slippage,
  turnover e metodologia de custos **congelados antes**; bruto e líquido
  separados, com intervalo de confiança.
* **Controles negativos** (gate `CRYPTO_NEGATIVE_CONTROLS`): injeção de dado
  futuro, ablação temporal, labels embaralhados; resultado esperado e
  thresholds congelados antes. Sinal que sobrevive a labels embaralhados é
  investigado, nunca comemorado.

Saída `SCIENTIFIC_INTEGRITY_REPORT.md`.

---

## 14. Soak, Windows, CI, segredos

* **Perfil** `QUALIFICATION_PROFILE_CRYPTO_V1.json` (congelado antes): 20 ciclos
  normais, 5 restarts, 5 duplicados, 3 por classe de falha relevante, 3 de cada
  caso do §11. Soak no Linux (gate `SOAK`, `SOAK_REPORT.md`).
* **Windows** (gate `WINDOWS_SMOKE`): E2E + restart + releitura com as final
  wheels em `C:\Cripto\qualificacao\runtime\`.
* **CI** (gate `HOSTED_CI`): workflows de push/PR dos três repos verdes no
  baseline e nos `final_commits` (C21).
* **Segredos** (gate `SECRETS_CLEAN`): varredura (ex.: `gitleaks` ou busca por
  padrões de chave) nos commits da missão, nos logs e nos relatórios; zero
  achados.

---

## 15. Fases (C8)

```text
freeze-parameters → baseline → truth-map → cleanroom-baseline → ops-failure
→ contract-wiring → publish-candidates → cleanroom-final → e2e
→ idempotency-failure → science → windows-smoke → hosted-ci → soak
→ contract-sign-off → attestation
```

* `freeze-parameters`: mostre o `FROZEN_PARAMETERS.json` ao dono antes de congelar.
* `publish-candidates`: releases `rc` novas do `cripto-predictor` (nunca
  sobrescrever), sha256 registrado.
* Mudou código depois de `cleanroom-final` → C14.
* Cada fase grava `ATTESTATION_PARTIAL_<phase>.json`.

---

## 16. Artefatos

C16 do núcleo, mais: `OPS_FAILURE_REPORT.md`, `AUTHORITY_STATE_MATRIX.json`,
`SCIENTIFIC_INTEGRITY_REPORT.md`, `DOMAIN_RESEARCH_CONTRACT.json`,
`qualification/shared/SHARED-003/SHARED_DEPENDENCY_VERDICT.json`.

---

## 17. Resultado

`QUALIFIED` só pelas regras C7.1: todos os gates do núcleo (todas as missões +
Etapa A) e os do braço em `PASS`:

```text
CRYPTO_RUNTIME_WIRING | CRYPTO_OPS_FAILURE_VERDICT | CRYPTO_UNCOMFORTABLE_CASES
| CRYPTO_ECONOMIC_METRICS | CRYPTO_NEGATIVE_CONTROLS | CRYPTO_SPLIT_BRAIN_CORRUPTION
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
Estados terminais: C7.3. Nunca escreva no texto algo mais forte que a attestation.

Resposta final, curta:

```text
estado terminal | result da attestation (ou "nenhuma")
cripto final_commit + wheel (url, sha256) | core e ops (versão, sha256)
SHARED-003: classificação + bloqueia?
gates: PASS / FAIL / NOT_RUN (lista dos que não passaram, com motivo)
P0 / P1 abertos | o que falta o dono fazer
```

**Não iniciar treinamento. Não mover capital.**
