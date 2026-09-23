# MISSÃO — ETAPA A: BRASILEIRÃO × CORE × OPS (Rev 8 — enxuto)

```text
stage  = A
branch = brasileirao   (nome do braço no schema, não é branch Git)
núcleo = qualification/COMMON_QUALIFICATION_CORE.md v2.0
sha256 = 50e8f49859daae6dcdf17164781d1837d8b656796924c35060f8d35855ee36e1
```

Objetivo: provar que o Brasileirão roda pesquisa **de verdade** por Core e
Ops, ponta a ponta, e que as previsões são **confiáveis para apostar**: nenhuma
informação posterior ao cutoff entra na previsão (ordem de jogos, fuso,
mesmo horário, cache, refit), nada duplicado ou perdido, holdouts intactos.
Sem CAIN e sem envelope (Etapa B). Você é o único agente; não use subagentes.
O núcleo vale inteiro; este prompt só acrescenta.

---

## 0. Como trabalhar

* **C0 primeiro** (núcleo C0). Falhou → `ABORTED`, sem rodar fase nenhuma.
* **Só conta o que rodou**: PROVEN pelo runtime suportado (C2). Código que
  "parece certo", teste que monta os componentes à mão, relatório antigo e CI
  de outro commit não fecham gate. Sem evidência → `FAIL` ou `NOT_RUN`, nunca
  `PASS`.
* Status: `PASS | FAIL | NOT_RUN` (`NOT_RUN` + `note: "BLOCKED: …"` quando algo
  externo impede). Todo número vem de `RAW_LOGS/` (C20).
* Tudo por branch + PR; nunca merge, push em `main`, rebase ou force-push. Você
  pode publicar releases pré-release (`rc`) do `brasileirao-predictor`.
* **Pare e pergunte ao dono** quando: regra local conflitar (C19); algo
  congelado precisar mudar; Core ou Ops precisarem de correção.
* Se o código real contradisser este prompt, registre em `FINDINGS.json` e siga o código.

---

## 1. Escopo e circuito

```text
brasileirao-predictor   muda nesta missão
core-predictor          congelado (só a wheel publicada)
predictor-ops           congelado (só a wheel publicada)
```

```text
pedido em arquivo (conforme o contrato) → entrypoint instalado
→ admission do Brasileirão → handler da allowlist → job real no Predictor Ops
→ runtime científico existente → Predictor Core → resultado (core/ops/domain facts)
→ persistência → processo termina → restart → releitura do MESMO resultado
```

Entrega central: `qualification/brasileirao/DOMAIN_RESEARCH_CONTRACT.json` (C24).

---

## 2. Pré-condições (além do C0)

* `qualification/HYGIENE.json` com tudo `DONE` — em especial **HYG-015**
  (`cain-export.yml` só `workflow_dispatch`; em 22/09 ainda rodava em push/PR).
* `STACK_BASELINE_V1.json`, `SHARED-002/CLEANROOM_REPORT.md`, `SHARED_ISSUES.json`.
* **SHARED-003** (timeout do Ops no Windows) é da missão `crypto`. Você avança,
  mas `SHARED_DEPENDENCY_CLEAR` só passa com o veredito não bloqueante — e ele
  afeta seu `WINDOWS_SMOKE` e a falha "timeout do Ops" no Windows.

---

## 3. Ponto de partida (verificado no código em 22/09 — reconfirmar)

`brasileirao-predictor` `main` = `34d73e2`; `predictor-ops` 4.2.1 (`b19e695`).

| Item | Observado |
|---|---|
| Pacote | 0.2.0; `requires-python >=3.13,<3.15`; a wheel leva `brasileirao_predictor` e `brasileirao_scripts` |
| Dependências | `predictor-core>=3.2.1,<4`, `predictor-ops>=4.2.0,<5`, por release (Core 3.2.1, Ops 4.2.1) |
| CI | `ci.yml` (ubuntu, 3.13/3.14, pyright), `publication-validation.yml` (instala a wheel com `--require-hashes`) |
| Entrypoints | `brasileirao-predict`, `brasileirao-kernel`, `brasileirao-shadow`, plugin `predictor.plugins`; **nenhum lê pedido de pesquisa** |
| Ops hoje — sombra | `brasileirao_scripts/sombra_diaria.py` escreve um jobs file (`schema_version "3"`: `id`, `command`, `provenance`, `runtime.root`) e roda `sys.executable -m predictor_ops run --job <id> --config <arquivo>`. `JobConfig`/`run_job` rodam **dentro** do Ops. Timeout, heartbeat, `expected_artifact`, `provenance_mode` e `job_type` ficam no padrão (3600 s, 30 s, nenhum, `permissive`, nenhum) |
| Ops hoje — coleta | `jobs.market-research.example.json` (`schema_version "1"`) roda `.venv/Scripts/python.exe brasileirao_scripts/<script>.py` — caminho de checkout, não de wheel |
| Sombra × dados | fora de um checkout git exige `BRASILEIRAO_PROJECT_ROOT`; copia o banco por `sqlite3.backup`, mas declara que o payload "may observe later commits" (lê o banco vivo depois da cópia) |
| Ops 4.2.1 | tipos de job: `SPORTS_COLLECTION, MARKET_COLLECTION, FORECAST_GENERATION, SHADOW_DECISION, EXECUTION, SETTLEMENT, RECONCILIATION, RISK_MONITORING` (não há "RESEARCH"); jobs file v3 não exige `job_type`; `capital_permission` só em `EXECUTION` |
| Kickoff | correção `a51a68d`: `backtest_walkforward.py` (+3/−1) e `tests/test_walkforward_row_contract.py` (+41) |
| Fuso | `prediction_protocol.py` exige datetime com fuso e normaliza para UTC; `bet_log.py` rejeita timestamp sem fuso; demais pontos: desconhecido |
| Protegidos | `docs/open_source_research/OSR-20260911-01/PROTECTED_PATHS.txt` (172 linhas: H9, H14, H15, A1, coleta de odds), `contracts/h8-ou25-frozen-candidate.json`, `reports/**/frozen_candidate.json`, `reports/benchmark_h9_frozen_*.json` — recontar |
| IDs | `H9` existe também no Cripto e no Stocks → prefixo `brasileirao:` (C18) |

---

## 4. Runtime e dados

* Linux × Python 3.13 (D-9): GitHub Actions; VM na nuvem para o soak.
* Windows × Python 3.13 (D-3): `C:\QUALIFICACAO\runtime\brasileirao\` (venv
  nova, só final wheels com `--require-hashes`).
* Clone de trabalho: `C:\QUALIFICACAO\repos\brasileirao-predictor`.
* Dados: só cópias com sha256 (snapshot SQLite + arquivos).
* **Não tocar:** instalação e bancos operacionais do Brasileirão, agendador
  operacional, chaves de API de odds.
* Regras locais: `C:\BRASILEIRAO\LEIA_PRIMEIRO.md`, `C:\BRASILEIRAO\INSTRUCOES\`
  e os arquivos de regra do repo (C19).

---

## 5. Holdouts e artefatos congelados (C15.1)

`brasileirao:H8`, `H9`, `H14`, `H15`, `A1`, holdouts, frozen trials, artefatos
de avaliação, calendários protegidos. Lista inicial = protegidos do §3 em
`FROZEN_PARAMETERS.json`; lista completa em `PROTECTED_SET.json` ao fim de
`truth-map` (blob git). Proibido: retunar, mudar threshold, reler holdout ou
resultado protegido para escolher configuração, mexer em frozen candidate.
Mudou algo protegido = P0 (guarde a evidência; não "conserte" com checkout).
Gate `PROTECTED_ARTIFACTS_UNCHANGED`.

---

## 6. Baseline e mapa real

* **baseline:** `STACK_BASELINE.json` (C3). Gate `STACK_BASELINE_FROZEN`.
* **truth-map:** com código **e** runtime: prediction, formal prediction, model
  update, sombra, settlement, coleta, scheduler
  (`scheduler.prospective.example.json`, `jobs.market-research.example.json`),
  Redis/kernel, Core, Ops, evaluator, walk-forward, xG, Elo, pacote research,
  plugin. Para cada um: entrypoint, cadeia de chamadas, estado, persistência,
  participação de Core/Ops, fronteira temporal, se roda de wheel ou de checkout.
  Saídas: `ARCHITECTURE_TRUTH_MAP.json`, `PROTECTED_SET.json`,
  `CORE_IDENTITY_REPORT.md` (C4 com a versão **executada**; gates
  `LOCK_INTEGRITY`, `CORE_IDENTITY`).

---

## 7. O que construir (três peças + reserva)

1. **Entrypoint** novo em `[project.scripts]` que lê pedido em arquivo e
   funciona **só com a wheel instalada** (sem `.git`, sem source root): a raiz
   de dados vem de configuração declarada no contrato; a provenance da própria
   distribuição vem do metadata instalado (versão, RECORD, sha256 da wheel).
2. **Admission** do Brasileirão: decide tipo, handler, budget, prioridade,
   referências e cutoff aceitável. O pedido nunca escolhe comando, módulo,
   path, URL, SQL ou handler fora da allowlist. Gate `ADMISSION`.
3. **Handler** rodando como **job real do Ops** (§8).
4. Módulo reservado de `adapter_paths` para a Etapa B (vazio ou esqueleto).

Registre cada mudança em `QUALIFICATION_CHANGELOG.md`.

---

## 8. Reusar o Ops como a sombra usa (gates `BR_OPS_REUSE`, `OPS_RUNTIME`)

Nada de executor paralelo. Mesmo mecanismo real da sombra: jobs file validado
pelo Ops → `sys.executable -m predictor_ops run --job <id> --config <arquivo>`.
O job de pesquisa é **pelo menos tão rígido** quanto a sombra e declara,
congelado em `FROZEN_PARAMETERS.json`:

```text
schema_version "3" | job id determinístico
| command = [sys.executable, "-m", <módulo da wheel>]   (nunca caminho de checkout)
| timeout_seconds | heartbeat_interval_seconds | max_output_bytes | expected_artifact
| provenance_mode = "strict" | provenance (domínio, pedido, wheel)
| job_type: omitido ou FORECAST_GENERATION, com justificativa; nunca EXECUTION
| capital_permission = false | runtime.root dentro do diretório de qualificação
```

`OPS_MAPPING_REPORT.md`: campo a campo sombra → pesquisa, com o motivo de cada
diferença, e prova em runtime de que `ops_run_id`, lock, heartbeat, timeout e
estado terminal vieram do Ops da wheel congelada. Importar classe do Ops sem
rodar o mecanismo não conta.

---

## 9. Contrato (C24)

Todos os campos de C24.1, `domain_prefix = brasileirao`. O `request_schema`
cobre, sem transporte: competição, temporada, event_id(s), kickoff, cutoff,
alvo, snapshot do dataset, identidade de modelo e features, baseline e
referência de odds quando houver. Teste automático: a closure transitiva de
imports do que o entrypoint alcança não chega em `cain`, `research_protocol`,
envelope nem `adapter_paths`. Gate `DOMAIN_CONTRACT` (o dono aprova com o merge
do contrato, fase `contract-sign-off`).

---

## 10. Suíte temporal (fase `temporal-suite`; roda com as final wheels)

A regra de tudo: `∀ informação i usada na previsão t: available_at(i) < cutoff(t)`,
escrita igual no contrato e no `FROZEN_PARAMETERS.json`. Vale para features,
Elo, xG, estado ataque/defesa, janelas móveis, refit mensal, cache, artefatos do
modelo, baseline, odds, payload e estado persistido. O handler lê **só** o
snapshot com hash: teste que escreve no banco de origem depois da captura e
mostra que o resultado não muda. Gate `TEMPORAL_INTEGRITY`;
`TEMPORAL_INTEGRITY_REPORT.md`.

* **`BR_KICKOFF_ORDERING`** — jogos fora de ordem no arquivo, mesma data, mesmo
  kickoff, rodadas inconsistentes, fixtures duplicadas, jogo adiado e
  remarcado. Prova de que o teste pega o bug: num **worktree descartável** do
  `final_commit`, reverter só o trecho de `backtest_walkforward.py` do
  `a51a68d` (mantendo o teste) → falha; restaurar → passa; apagar o worktree e
  mostrar que a final wheel não mudou.
* **`BR_TIMEZONE_INTEGRITY`** — sedes em `America/Sao_Paulo`, `Manaus`, `Cuiaba`,
  `Rio_Branco`; horário de verão nas temporadas **antes de 2019** (a hora que
  se repete e a que não existe); offsets diferentes; timestamp sem fuso →
  normaliza por regra do contrato ou rejeita, nunca adivinha. Mapear todos os
  pontos que leem datas.
* **`BR_METAMORPHIC`** — ≥ 5 permutações congeladas (seed + sha256) da ordem
  das linhas: mesmo resultado nos aspectos invariantes, com comparadores
  congelados. Diferença sem explicação = não passa. `METAMORPHIC_REPORT.md`.
* **`BR_SAME_KICKOFF_ISOLATION`** — o resultado do jogo A não afeta a previsão
  do jogo B de mesmo kickoff, nem por dado explícito nem por estado (Elo, xG,
  cache). `SAME_KICKOFF_REPORT.md`.
* **`FUTURE_CANARY`** — `FUTURE_CANARY_BR_001` só depois do cutoff; procurar em
  linhas de treino, Elo, xG, features, cache, refit, artefato do modelo,
  payload, resultado — inclusive transformado (número derivado, hash,
  agregado). Apareceu antes = P0. `FUTURE_CANARY_REPORT.md`.
* **`BR_CACHE_STATE`** — previsão histórica em processo novo ≡ previsão
  histórica depois de rodar uma data futura (mesmo processo e entre processos
  que compartilham estado). `CACHE_STATE_REPORT.md`.
* **`BR_FUTURE_INJECTION`** — dado impossível antes do cutoff injetado no banco:
  rejeita, exclui ou falha fechado; nunca usa "porque está no banco". Pelo
  caminho real (entrypoint → Ops → handler).

---

## 11. Core e separação (gates `CORE_PARTICIPATION`, `AUTHORITY_SEPARATION`, `CAPITAL_FORBIDDEN`)

Core real: trial/evaluation identity, validação temporal, estatística, estado
científico; correlacionar `request_id → experiment_id → trial → core facts →
result_id`. O Core não decide mercado, odds nem capital. Previsão válida ≠
edge de aposta; edge ≠ capital permitido. Falha do Ops nunca vira resultado
válido. O código de decisão econômica existente (`research/economic_decision.py`,
`shadow_portfolio.py` e afins) não é alcançável com permissão de capital.
`capital_permission = false`.

---

## 12. E2E, idempotência e falhas

* **E2E** (gates `E2E`, `PROVENANCE`): só `final_wheels`, entra pelo entrypoint
  do §7 com pedido em arquivo; sem editable, `PYTHONPATH`, mocks, sem chamar
  handler ou `run_job` direto. Termina, reinicia em processo novo, relê o mesmo
  resultado. `E2E_EVIDENCE/`.
* **Idempotência** (gate `IDEMPOTENCY`): mesma key + mesmo conteúdo (retry,
  restart, duplicata, fora de ordem, concorrência se possível) → 1 experimento,
  1 resultado; mesma key + conteúdo diferente → conflito; crash entre efeito e
  dedupe → efeito único por transação ou journal + reconciliação.
* **Falhas** (gates `FAILURE_INJECTION`, `RESTART_RECOVERY`): `FAILURE_MATRIX.json`
  congelada antes; injeção na borda: crash da admission, crash e timeout do Ops
  (Linux **e** Windows), falha no artefato de previsão, na composição e na
  gravação do resultado, pedido duplicado e fora de ordem, DB lock, DB × FS
  divergentes, artefato ausente ou corrompido. Nada perdido, nada duplicado,
  resultado incompleto nunca vira resultado válido.

---

## 13. Soak, Windows, CI, segredos

* **Perfil** `QUALIFICATION_PROFILE_BR_V1.json` (congelado antes): 20 ciclos
  normais, 5 restarts, 5 duplicados, 3 por classe de falha relevante, 5 ciclos
  de mesmo kickoff, 5 com dataset fora de ordem, 5 com future canary. Soak no
  Linux; tolerância zero para vazamento de futuro e mudança em protegido
  (gate `SOAK`).
* **Windows** (gate `WINDOWS_SMOKE`): E2E + restart + releitura em
  `C:\QUALIFICACAO\runtime\brasileirao\`, registrando as wheels instaladas.
* **CI** (gate `HOSTED_CI`): `ci.yml`, `publication-validation.yml` e os
  workflows de push/PR de Core e Ops verdes no baseline e nos `final_commits`.
* **Segredos** (gate `SECRETS_CLEAN`): varredura nos commits, logs e relatórios
  da missão (chaves de odds e afins); zero achados.
* **Typecheck:** o `pyright` do CI deve cobrir o código novo (admission,
  handler, entrypoint). Erros antigos em `brasileirao_predictor/research` não
  bloqueiam; erro no código novo é P1.

---

## 14. Fases (C8)

```text
freeze-parameters → baseline → truth-map → cleanroom-baseline → contract-admission
→ ops-mapping → publish-candidates → cleanroom-final → temporal-suite → e2e
→ idempotency-failure → windows-smoke → hosted-ci → soak → contract-sign-off
→ attestation
```

* `freeze-parameters`: mostre ao dono o `FROZEN_PARAMETERS.json` (com os
  parâmetros do job Ops do §8) antes de congelar.
* `publish-candidates`: releases `rc` novas, sha256 registrado.
* Mudou código depois de `cleanroom-final` → C14.

---

## 15. Artefatos

C16 do núcleo, mais: `DOMAIN_RESEARCH_CONTRACT.json`, `OPS_MAPPING_REPORT.md`,
`TEMPORAL_INTEGRITY_REPORT.md`, `SAME_KICKOFF_REPORT.md`, `METAMORPHIC_REPORT.md`,
`FUTURE_CANARY_REPORT.md`, `CACHE_STATE_REPORT.md`.

---

## 16. Resultado

`QUALIFIED` só pelas regras C7.1: todos os gates do núcleo (todas as missões +
Etapa A) e os do braço em `PASS`:

```text
BR_OPS_REUSE | BR_KICKOFF_ORDERING | BR_TIMEZONE_INTEGRITY | BR_SAME_KICKOFF_ISOLATION
| BR_METAMORPHIC | BR_CACHE_STATE | BR_FUTURE_INJECTION
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
brasileirao final_commit + wheel (url, sha256) | core e ops (versão, sha256)
gates: PASS / FAIL / NOT_RUN (os que não passaram, com motivo)
vazamento de futuro: nenhum detectado | encontrado (onde)
P0 / P1 abertos | o que falta o dono fazer
```

**Não iniciar treinamento. Não mover capital.**
