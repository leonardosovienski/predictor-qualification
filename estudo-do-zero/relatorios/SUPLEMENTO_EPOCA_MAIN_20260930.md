# Suplemento — época `main` remoto (2026-09-30)

Complementa a [linha de base da época main](LINHA_DE_BASE_EPOCA_MAIN.md). Tudo aqui se refere aos HEADs do `main` remoto listados lá (cain `abeb1e60`, brasileirão `1e0c6f0b`, core `956891ea`, cripto `74113eff`, ecosystem `0b0a09c8`, ops `21cfcea5`, qualificação `3ed750c5`, stocks `3ec7e413`), lidos no clone Linux de execução. Nada aqui altera as conclusões da época original (raízes Windows), que continuam válidas só para os SHAs da [linha de base](LINHA_DE_BASE.md). Evidência: `../evidencias/epoca-main-20260930/` (índice das execuções em `runs/INDEX.txt`); cada leitura e execução tem linha própria em `../evidencias/REGISTRO.log` (projeto `EPOCA-MAIN` ou o projeto lido, ação com prefixo "época main").

Legenda de certeza: OD observação direta; ET-RUN executado nesta sessão; ET-SRC lido no código; ET-HIST registrado por outra sessão; DD declaração documental; INF inferência; NV não verificado.

## 1. Confronto com os documentos de estado (Anexo A3/A4)

Os seis `docs/ESTADO_2026-09-30.md` (cain, core, ops, cripto, brasileirão, stocks), `ecosystem-predictor/CURRENT_STATE.md`, `ETAPA_B_INTEGRATED_STACK_20260928.md` e `predictor-qualification/qualification/shared/CICLO_D27_20260930.md` foram lidos integralmente no `main`. Cada afirmação verificável foi confrontada com evidência primária desta sessão.

| Afirmação (DD) | Onde | Verificação | Resultado |
|---|---|---|---|
| "o `README.md` entra na METADATA da wheel e só muda com versão nova" | os seis ESTADO | METADATA das 11 wheels publicadas comparada com o README do commit da tag e do `main` (`wheel-readme-metadata-check.json`) | **Confirmado para as 7 wheels principais** (core 3.2.1, ops 4.2.2rc1, cain 0.4.13rc15, cripto 1.2.0rc4, brasileirão 0.3.0rc5, stocks 0.3.0rc3, ecosystem 0.2.1): corpo da METADATA == README da tag, `Description-Content-Type: text/markdown`. **Não vale para as 4 subdistribuições do ecosystem** (protocol 2.0.0rc2, transport 0.1.0rc7, snapshot 1.0.2rc1, bundle 1.0.1rc1): METADATA sem long description (0 bytes), logo README não entra nelas. OD/ET-RUN |
| "o `main` passou a declarar versão nova não publicada; nenhuma linha de código mudou" (core 3.2.2, ops 4.2.2rc2, cripto 1.2.0rc5, brasileirão 0.3.0rc6) | ESTADO de core, ops, cripto, brasileirão | `uv build --wheel --offline` no `main` e comparação membro a membro com a wheel publicada (`built-vs-published-wheels.json`) | **Confirmado com uma ressalva**: além de METADATA, as wheels do `main` diferem das publicadas em `licenses/LICENSE` (arquivo novo, entra na wheel) e, no core, também em `WHEEL` (versão do hatchling); no cain e no cripto difere ainda o `__init__.py` que carrega a string de versão. Nenhum outro membro de código difere. A frase do ESTADO do cain "mudança de licença (`c1f89d7`), **fora da wheel**" está errada: o `LICENSE` entra na wheel em `licenses/`. ET-RUN |
| ops: "A wheel construída do `main` é a mesma da release" (linha 14) e, mais abaixo, "o `main` passou a declarar 4.2.2rc2 não publicada" (linha 19) | ESTADO do ops | mesma comparação | As duas frases coexistem no mesmo arquivo; a segunda supera a primeira. Construída do `main` = 4.2.2rc2 ≠ 4.2.2rc1 (METADATA, `licenses/LICENSE`). Código `src/predictor_ops` idêntico. ET-RUN |
| stocks: "`main` à frente da wheel: `pyproject.toml` declara 0.3.0rc4 (não publicada)" e "CI do `main` vermelho (só o lacre R8): `97979d5` mudou `pyproject.toml`" | ESTADO do stocks | `tools/verify_operational_evidence.py` (para no primeiro divergente) + comparação completa dos 263 caminhos lacrados com `canonical_sha` do próprio verificador (`runs/stocks-r8-seal-full-compare.log`) | **Parcialmente confirmado**: o lacre está quebrado, mas por **3 arquivos**, não só o `pyproject.toml`: `.github/workflows/ci.yml` (bump `setup-uv` 6→7, `3db4978`), `pyproject.toml` (`97979d5` licença e `68a2647` hatchling) e `tools/build-requirements.txt` (`68a2647`, `07f5c7f` trove-classifiers). População lacrada = população atual (263/263). A wheel construída do `main` (rc4) tem 25 membros a mais que a rc3 publicada (24 módulos, sobretudo `stocks_predictor/v2/`, e `licenses/LICENSE`). ET-RUN |
| ecosystem: "Wheels publicadas: core 3.2.1, ops 4.2.2rc1, ecosystem 0.2.1, … stocks 0.3.0rc3 (`registries/released_architecture.json`)" | `CURRENT_STATE.md` | `released_architecture.json` (7 wheels com sha256) contra os assets baixados (`released-architecture-vs-assets.json`) | **Confirmado**: 7/7 sha256 batem com os assets do GitHub. O registro não lista as 4 subdistribuições (protocol, transport, snapshot, bundle); elas estão só no texto. OD |
| ecosystem: "Pilha qualificada vigente: cain 0.4.13rc13 + transporte 0.1.0rc6; candidata (D-27): cain rc15 + transporte rc7 + cripto rc4"; "teste conjunto dos três domínios 58/58 no PC 2" | `ETAPA_B_INTEGRATED_STACK_20260928.md` | leitura; attestations no `main` da qualificação | As três attestations de integração no `main` (`integration-crypto` `c9e7330e`, `integration-stocks` `59deb091`, `integration-brasileirao` `4a14f6cb`) validam no seu commit de emissão (ver §3). O teste conjunto 58/58 é ET-HIST (PC 2, WSL); não reexecutado. DD/ET-HIST |
| cain: "`integration-crypto` rc15: todas as fases do Linux primário verdes (run 36648103793)"; cripto: "Etapa A `crypto` reaberta como V1.2 … 30/31 gates PASS … só parciais; a attestation vigente continua a V1.1" | ESTADO de cain e cripto | `attest.py check` no `main` atual | Coerente com o observado: a attestation `QUALIFIED` de `crypto` no `main` é a V1.1 e **não valida mais** contra a árvore atual (§3), porque a reabertura V1.2 regravou relatórios no mesmo diretório. Os runs do GitHub Actions citados são ET-HIST, não reabertos aqui. OD |
| qualificação: "o dono delegou as decisões 1–3 ao agente, mas a escrita em `DECISIONS.json` foi bloqueada … D-29, D-30, D-31 ficaram propostas" | `CICLO_D27_20260930.md` | `DECISIONS.json` no `main` `3ed750c5` | Confirmado: 28 decisões registradas; D-29/D-30/D-31 não constam. OD |
| cain: "`cain doctor`" como verificador | ESTADO do cain (Anexo A6) | `.venv/bin/cain doctor` | Falha por `connection refused` (sem Ollama no container); com `CAIN_PROVIDER=fake` sai 0 e avisa "sem inferência real". Não prova inferência nem o provedor real. ET-RUN |

## 2. Verificadores do Anexo A6 (ET-RUN)

| Projeto | Comando | Saída | Limite |
|---|---|---|---|
| stocks | `main.py doctor --check` | 0 | `.venv` de sessão anterior |
| stocks | `tools/check_project_files.py` | 0 | idem |
| stocks | `tools/verify_operational_evidence.py` | 1 — `current operational code changed: .github/workflows/ci.yml` | aborta no primeiro; comparação completa em §1 |
| core | `tools/check_installed_wheel.py --wheel predictor_core-3.2.1…whl` (`python -I`) | 1 no `.venv` do core (editable 3.2.2); **0 no `.venv` do cripto** (wheel 3.2.1 instalada) | o script exige a wheel instalada; o venv do core não é cleanroom |
| ops | `predictor-ops provenance` | 3 `CONFIGURATION_ERROR` no `.venv` do ops (editable); **0 `VALIDATED` no `.venv` do cripto** (wheel 4.2.2rc1) | idem |
| ecosystem | `scripts/check_ecosystem_drift.py --offline-check` | 0, sem drift | só offline |
| ecosystem | `build_v2_domain_registry.py --check` | 1 contra `3ed750c` ("out of date"); **0 contra `ec02315a`**, o commit-fonte gravado em `domains.json` | os três `DOMAIN_RESEARCH_CONTRACT.json` são byte-idênticos entre `ec02315a` e `3ed750c5`; a ferramenta compara metadados do commit, não o conteúdo |
| ecosystem | `render_v2_mapping.py` | 0 | renderização |
| cripto | `scripts/check_release_identity.py --strict` | 1 — falha de TLS no `urllib` via proxy do container | substituído pela comparação manual de membros (`built-vs-published-wheels.json`); o gate em si ficou NV aqui |
| cain | `cain doctor` | 1 (Ollama ausente); 0 com `CAIN_PROVIDER=fake` | sem inferência real |
| qualificação | `attest.py check` (6 missões) | ver §3 | precisa de `jsonschema` (Python auxiliar do estudo) |
| todos | `uv build --wheel --offline` | 0 em cain, brasileirão, core, cripto, ops, stocks | cache do container; ecosystem não construído (workspace de 5 pacotes) |

Não executados (Windows-only ou ambiente do dono): `preservation.py`, verificadores que dependem de `C:\…`, suítes completas de cada projeto, harness econômicos, jobs de GitHub Actions.

## 3. Attestations da qualificação: válidas na emissão, três não validam mais no `main`

Para cada `qualification/<missão>/QUALIFICATION_ATTESTATION.json` no `main` `3ed750c5`, o commit de emissão foi obtido por `git log -1`, a árvore inteira extraída nesse commit e o `scripts/attest.py check` **da própria missão** executado (`attestation-issuance-commits.json`, `runs/attest-check-at-issuance-*.log`, `runs/attest-check-current-*.log`).

| Missão | Emissão | `check` na emissão | `check` no `main` atual |
|---|---|---|---|
| crypto | `96da7d08` | OK | **9 problemas** (C7.1(2) counts; sha256 divergente em FINDINGS.json, CORE_IDENTITY_REPORT.md, CLEANROOM_REPORT.md, HOSTED_CI_REPORT.md, SCIENTIFIC_INTEGRITY_REPORT.md, PROTECTED_ARTIFACT_REPORT.md) |
| brasileirao | `5430a6f1` | OK | 0 |
| stocks | `6206b7b2` | OK | 0 |
| integration-crypto | `c9e7330e` | OK | **11 problemas** (CORE_IDENTITY, CLEANROOM, HOSTED_CI, CAIN_ROUNDTRIP, PROTECTED_ARTIFACT, SOAK, EVIDENCE_NUMBERS.json, scripts/render_reports.py, CONTRACT_REVALIDATION divergentes) |
| integration-stocks | `59deb091` | OK | **18 problemas** (FINDINGS.json e os relatórios acima, mais DECISION_POLICY e ENVELOPE_V2_CONFORMANCE) |
| integration-brasileirao | `4a14f6cb` | OK | 0 |

Leitura: o núcleo (C7.1 regra 3) exige que o sha256 confira **no commit da attestation**, e confere. Mas no `main` atual os arquivos que as três attestations citam foram regravados pelo ciclo D-27 (reabertura V1.2 do crypto e ciclos rc15/c5 das integrações escrevem no mesmo diretório da missão) sem nova attestation com `supersedes_sha256`. Quem ler o `main` não consegue reproduzir a evidência da attestation vigente sem voltar ao commit de emissão. Achado `EPOCA-QUAL-1` (P1, OD) em [PROBLEMAS_PRIORIZADOS](PROBLEMAS_PRIORIZADOS.md). Rodar o `attest.py` de uma missão sobre a attestation de outra dá um falso "counts não bate" (o script lê o FINDINGS.json da própria missão); esse erro de método foi cometido e corrigido nesta sessão (registrado).

## 4. Wheels publicadas × `main`

- 11 assets baixados; sha256 igual ao registrado no Anexo e nas releases (`wheel-files-sha256.json`, `published-annex-identities.json`).
- `released_architecture.json` (ecosystem) aponta 7 wheels; 7/7 batem.
- METADATA: ver §1. Observação adicional: nas wheels `predictor_research_snapshot-1.0.2rc1` e `predictor_research_bundle-1.0.1rc1` o campo `Version` termina em `\r` (METADATA com CRLF). Sem consequência observada (pip lê); registrado como `EPOCA-ECO-2` (P2, OD) porque é sinal de build em ambiente Windows não normalizado, incoerente com "build duplo byte-idêntico" alegado para as demais.
- Construídas do `main` (`uv build --offline`): cain rc16, brasileirão rc6, core 3.2.2, ops rc2, stocks rc4, cripto rc5. Diferenças para as publicadas: só METADATA, `licenses/LICENSE`, `WHEEL` (core, stocks) e string de versão (cain, cripto); **stocks acrescenta 24 módulos** (`stocks_predictor/v2/*`, `adapters/`, `research_*`). Portanto o `main` do stocks tem código que nenhuma wheel publicada contém; a qualificação Etapa A `stocks` cita rc2 e a Etapa B cita rc3.

## 5. Revisão semântica dos deltas pequenos (ET-SRC)

### predictor-ops (14 arquivos; 1 de código)

`src/predictor_ops/runtime.py`: o único trecho de código novo é a correção SHARED-005 em `_mutation_guard` — inicialização do arquivo de guarda com `os.open`/`os.write` sem buffer e tolerância a `PermissionError` no Windows, para o processo perdedor da trava não cair. `tests_v2/test_runtime.py` ganha 42 linhas cobrindo o caso; `test_version_contract.py` acompanha a versão. O resto do delta é CI (`pip-audit` sobre lock exportado, `consumer-contracts.yml`, `delete-branches.yml`, `release.yml`), `Dockerfile`, `LICENSE`, README, CHANGELOG, versão e lock. Nenhuma mudança de contrato observada. Coerente com o ESTADO ("o Ops não mudou" quanto a contratos).

### core-predictor (10 arquivos; 0 de código)

Só README (`--locked` no lugar de `--frozen`, seções de validação), CI, `release.yml`, `LICENSE`, CHANGELOG, `pyproject` (3.2.2) e lock. `src/` intacto entre 9bf43efe e 956891ea.

### ecosystem-predictor (61 arquivos): protocolo V2 e transporte

- `research_protocol.v2` (`__init__.py` 647 linhas, `_schema.py` 217): `ResearchTaskV2`/`ResearchResultV2` com JSON canônico (chaves ordenadas, floats proibidos), IDs qualificados por domínio (`<domínio>:<id>`), `episode_id`, `task_id_for` determinístico, `build_task`/`validate_task`/`build_result`/`validate_result`, `OUTCOME_CLASSES` fechado, registro `data/domains.json` gerado dos três `DOMAIN_RESEARCH_CONTRACT.json` da qualificação em `ec02315a`. Schemas JSON `research-task-2` e `research-result-2` versionados; testes `tests/v2/*` (5 arquivos + vetores). INF: o desenho implementa C18 (IDs com domínio) e C12 (admission por schema + domínio); não foi executado aqui além dos `--check`.
- `research_transport` (spool + consumidor): spool write-once com `os.link` (falha se já existe = duplicata rejeitada), consumidor por domínio com trava exclusiva (`flock`/`msvcrt`), ledger SQLite de entregas, verificação de identidade byte a byte do payload de domínio contra a releitura do adapter, injeção de falha por `PREDICTOR_RESEARCH_TRANSPORT_FAULT`, CLI `predictor-research-consumer` com saídas 0/2/5/6/1 (6 = `CONSUMER_BUSY`), allowlist fixa de adapters (`crypto`, `stocks`, `brasileirao`). Testes em `tests/test_transport.py` (471 linhas). INF: cobre IDEMPOTENCY e o cenário de trava do relato 58/58; não exercitado aqui.
- `scripts/renew_crypto_harness.py` + workflow `crypto-harness-renewal.yml` + `registries/harness_renewal.json`: renovação da attestation do harness crypto por registro, com teste próprio.
- `compat/` (pyproject + lock) e `cross-repo-compatibility.yml`: instalação conjunta das wheels publicadas para o teste de compatibilidade; registros `architecture_registry`, `compatibility_candidate`, `harness_registry`, `project_registry`, `released_architecture` atualizados.

### Adapters V2 e contratos de pesquisa dos três domínios

- Os três `adapters/research_v2.py` (66–68 linhas cada) têm a mesma forma: `identity()`, `request_bytes()`, `submit_task()`, `reread()`, tudo passando pelo `Circuit`/runner do domínio (a `adapter_api` do contrato), sem importar nada de fora dos `adapter_paths`. Isso é o que C24.1 exige; o grafo de imports foi verificado só por leitura, não por ferramenta (as suítes `tests/conformance/test_import_closure.py` existem nos três e não foram rodadas).
- Contratos (`research_contract.py` no cripto e stocks; `research_runtime/contract.py` no brasileirão): cripto declara `BACKTEST_EXISTING_HYPOTHESIS`, refs `protocol/dataset/baseline/cost_model/evidence`, `EXIT_CODES` 0/2/3/4/5 e estados com os negativos do núcleo; brasileirão declara `WALKFORWARD_FORECAST_EVALUATION`, refs `dataset/model/features/baseline/cost_model` + odds opcional, `TARGETS` 1X2/OU25, `MAX_EVENTS` 400, `LEAD_MINUTES` (15, 10080), estado `FORECAST_ONLY`; stocks declara `BACKTEST_PIT_FACTOR` e `COLLECT_EXTERNAL_INTELLIGENCE`, classes PIT, famílias/coletores de inteligência externa, controles negativos, estado `NOT_READY` e statuses `RETRYABLE` extras. Os três seguem o mesmo esqueleto (schema de pedido sem envelope, allowlist tipo→handler, `idempotency_key` sem `client_ref`, `authoritative_result_source`).
- Fora dos adapters, o delta de código dos domínios (cripto 23 módulos, brasileirão 21, stocks 36) **não foi revisado**; ver [cobertura por projeto](COBERTURA_POR_PROJETO.md).

## 6. Inventário dos deltas grandes (pendentes, lista exata)

Listas completas com sha256 e linhas em `../evidencias/epoca-main-20260930/delta/<projeto>-delta-inventory.json`; resumo:

- **cain** (357 arquivos, +61.453 linhas): 110 `.py` de código/scripts (por diretório: `research` 21, `loop` 9, `orchestration` 8, `claims` 8, `evaluation` 6, `sandbox` 5, `memory` 5, `inference` 5, `review` 4, `llm` 4, `findings` 4, demais), 87 testes, 44 docs, 59 dados/texto (config de domínio, fixtures), 6 CI, 6 manifest/lock. Só `docs/ESTADO_2026-09-30.md` foi lido. Sem revisão semântica: `DecisionPolicy`, `policy.py`, configs `crypto.json`/`stocks.json`/`brasileirao.json` (o ESTADO diz byte a byte iguais à rc13 — NV).
- **predictor-qualification** (5.763 arquivos, +1.128.312 linhas): 4.956 `RAW_LOGS`, 198 scripts `.py` (integration-stocks 58, integration-crypto 43, integration-brasileirao 39, brasileirao 30, stocks 24, crypto 11, shared 9), 425 dados/texto, 106 docs. Lidos: `CICLO_D27_20260930.md`, `DECISIONS.json`; executados: `attest.py check`. Os scripts de missão e os relatórios não foram revisados.
- **stocks-predictor** (127 arquivos, +27.812): 41 `.py` de código (`v2/` 24 módulos, `research_*` 11, `adapters/` 2, `ecosystem_plugin.py`, `tools/chronos_forecast.py`, `tools/export_scientific_state.py`), 21 testes, 40 dados/texto, 17 docs. Revisados: adapter, contrato, ESTADO, lacre R8.
- **cripto-predictor** (132 arquivos, +36.747): 28 `.py` (`research/` 10 novos: cpcv, decision_policy, dedup, fm_zero_shot, forecast_metrics, holdout, ledgers, preregistration, reevaluation, strategy_metrics; `research_*` 8; `run_ledger.py`; `v3/` 3; `scripts/` 2), 21 testes, 4 testes V1 movidos para `legacy/v1_integration/`. Revisados: adapter, contrato, runner, ESTADO.
- **brasileirao-predictor** (113 arquivos, +13.984): 25 `.py` (`research_runtime/` 10, `adapters/` 2, `pit.py`, `model.py`/`elo_baseline.py`/`evaluator.py`/`ingest.py`/`serving_evaluator.py` modificados, scripts prospectivos v2, `tools/crossos_*`), 28 testes. Revisados: adapter, contrato, ESTADO. As modificações em `model.py` (604 linhas), `evaluator.py` e `serving_evaluator.py` tocam o caminho de previsão e **não foram lidas**: qualquer conclusão da época original sobre esses módulos vale só para `f8780690`.

## 7. Achados novos desta época

Registrados em `../evidencias/epoca-main-20260930/findings.json` e consolidados em [PROBLEMAS_PRIORIZADOS](PROBLEMAS_PRIORIZADOS.md): `EPOCA-QUAL-1` (P1) attestations não reproduzíveis no `main`; `EPOCA-STOCKS-1` (P1) lacre R8 quebrado por três arquivos e `main` com código sem wheel publicada; `EPOCA-ECO-1` (P2) subdistribuições sem README na METADATA e fora do `released_architecture.json`; `EPOCA-ECO-2` (P2) METADATA com CRLF em snapshot/bundle; `EPOCA-DOCS-1` (P2) frases dos ESTADO incompatíveis com as wheels construídas (LICENSE "fora da wheel"; ops "mesma da release"); `EPOCA-COBERTURA-1` (P2) delta de código não revisado (cain, qualificação, domínios fora dos adapters).

## 8. Limites

Cópia de execução com `.venv` de sessões anteriores (core e ops editable); rede só por proxy (TLS do `urllib` falha); sem Ollama; sem Windows; sem acesso ao PC 2; sem GitHub Actions disparado. Nenhum número de qualificação foi reexecutado. Nenhum capital, treino, coleta ou serviço. Os originais Windows não foram tocados.
