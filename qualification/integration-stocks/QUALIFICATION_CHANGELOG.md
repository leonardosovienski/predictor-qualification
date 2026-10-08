# integration-stocks — QUALIFICATION_CHANGELOG

O que o agente mudou, onde, por quê, commit e PR (C6). Sessão única (D-5), executada no **PC 2** do dono (Claude Code
desktop, comandos Linux no WSL Ubuntu 24.04 só para desenvolvimento, diagnóstico e recibos R8). Toda afirmação de gate
cita arquivo de evidência + sha256 no `GATES.json` / attestation.

## 2026-09-27 — C0 ABORTED (histórico)

| Onde | O quê | Por quê | Commit / PR |
|---|---|---|---|
| `qualification/integration-stocks/FINDINGS.json` (chave `c0`), `RAW_LOGS/c0/`, `scripts/c0_*` | C0 ABORTED: integration-crypto ainda não QUALIFIED no main | regra única do pré-voo | #58, #59 |

## 2026-09-27/28 — C0, D-24, freeze-parameters, baseline

| Onde | O quê | Por quê | Commit / PR |
|---|---|---|---|
| `qualification/DECISIONS.json` | acrescenta a D-24 (só ela), gerada por `scripts/add_d24.py` com conferência byte a byte das 23 anteriores | decisão explícita do dono no prompt da sessão (5.5) | `fc9f01b`, PR #63 (mergeado) |
| `RAW_LOGS/c0/` + `scripts/c0_preconditions.py` | pré-voo 4.1–4.7 refeito em cada mudança do main: 9937894 e 6af1e32 com 0 falhas; o script passa a baixar cada `final_wheel` de cain/ecosystem da integration-crypto e conferir o sha256, e confere as SHARED contra a pilha completa | C0 + pré-voo da sessão | este PR |
| `FROZEN_PARAMETERS.json` + `scripts/freeze_parameters.py`, `FROZEN_VECTORS.json` + `scripts/build_vectors.py` + `fixtures/`, `FAILURE_MATRIX.json`, `QUALIFICATION_PROFILE_INTEGRATION_STOCKS_V1.json` | parâmetros, vetores, matriz de falhas e perfil de soak congelados; configuração da DecisionPolicy do Stocks lida de 61fc017 (SHA completo) e do contrato; limites do framework achados antes do congelamento (IS-F002, IS-F003) | C15 (primeira fase); mostrados ao dono neste PR antes de qualquer execução de gate | este PR |
| `STACK_BASELINE.json` + `scripts/mission_baseline.py`, `RAW_LOGS/baseline/` | baseline com o coletor do STACK_BASELINE_V2.0 sem mudança, cain/ecosystem nos final_commits da integration-crypto; a primeira comparação (todos os campos) acusou só o estado remoto do cripto (main e release rc3 novos) e ficou preservada em `mission_baseline_run1_strict.log`; o script passou a separar campos de estado remoto dos da base | C3 | este PR |
| `FINDINGS.json`, `GATES.json`, `scripts/{attest,findings_init}.py`, `ATTESTATION_PARTIAL_{freeze-parameters,baseline}.json` | achados IS-F001..IS-F004 (P2) acrescentados preservando o registro do C0; ledger de gates; parciais validados no schema | C6, C7, C8 | este PR |
| `tools/pyproject.toml`, `tools/uv.lock` | ferramentas da missão: protocolo 2.0.0rc2 da release congelada (sha256 no lock) + jsonschema | venvs só de uv.lock | este PR |

## 2026-09-28 — truth-map e cleanroom-baseline

| Onde | O quê | Por quê | Commit / PR |
|---|---|---|---|
| `ARCHITECTURE_TRUTH_MAP.json`, `PROTECTED_SET.json`, `scripts/truth_map.py`, `RAW_LOGS/truth-map/` | mapa do circuito com o cain e o ecosystem nos final_commits da integration-crypto; conjunto protegido: blobs do cripto (ee3d3d1), do stocks (61fc017) e do brasileirao, mais os artefatos compartilhados, entre eles os da integration-crypto | C13, C15.1 | `205cd7e`, #64 (mergeado) |
| `CLEANROOM_REPORT.md` (seção baseline), `scripts/cleanroom_baseline.sh`, `RAW_LOGS/cleanroom-baseline/` | diagnóstico sem valor de gate: conformidade da Etapa A verde contra a wheel 0.3.0rc2; `ADAPTER_UNAVAILABLE` no consumidor e `CONFIG_INVALID` no `cain research propose --domain stocks` (o ponto de partida desta missão) | C5 | `205cd7e`, #64 |

## 2026-09-28 — envelope-v2, domain-adapter, cain-wiring-decision-policy, publish-candidates

| Onde | O quê | Por quê | Commit / PR |
|---|---|---|---|
| `stocks-predictor` `stocks_predictor/adapters/research_v2.py`, `tests/adapters/` (novos), recibos R8 e selo, versão 0.3.0rc3 | adapter V2 só pela `adapter_api` (`Circuit.submit_request/show`), só stdlib; procedimento R8 da D-24 (4b) com os recibos real e de capacidade e o selo refeito (`RAW_LOGS/domain-adapter/r8_procedure.log`); suíte local completa em 6f857b2, árvore limpa antes e depois (`stocks_suite_6f857b2.log`). O passo `quality_exception_control` falhou na 1ª execução por defeito do script da suíte (ruff fora do PATH); foi reexecutado com o PATH do venv e passou (`stocks_quality_exception_control_rerun_6f857b2.log`), e o log original ficou preservado | C24, D-24 (4) | `6f857b2`; leonardosovienski/stocks-predictor#107; pré-release `v0.3.0rc3` |
| `cain` `src/cain/orchestration/data/stocks.json`, `tools/build_domain_config.py`, testes; transporte 0.1.0rc4 e versão 0.4.13rc7 | configuração do Stocks lida de 61fc017 (SHA completo), do contrato e dos parâmetros congelados; framework sem mudança | C11, C12 | `581b760`, `deccaaa`; leonardosovienski/cain#60; pré-release `v0.4.13rc7` |
| `ecosystem-predictor` `packages/research-transport` | entrada `stocks` na allowlist fixa de adapters, 0.1.0rc4 | C11 | `1304b20`; leonardosovienski/ecosystem-predictor#32; pré-release `predictor-research-transport-v0.1.0rc4` |
| `RAW_LOGS/publish-candidates/`, `release-notes/`, `runtime_targets.json`, `scripts/publish_*.sh` | três pré-releases com build reprodutível (duas builds, mesmos bytes), conferidas por download anônimo (`RELEASE_VERIFIED`) | C7.1 regra 4, C21 | `552337a` |
| `.github/workflows/integration-stocks-runtime.yml`, `scripts/` (harness, e2e, n_plus_1, isolation, failure_matrix, soak, contract_d, cleanroom_final, runtime_env, operator_env, ci_runtime, ollama_setup) | runtime suportado: Linux primário e Windows secundário no GitHub Actions (D-1, D-9, D-16), só wheels publicadas, dados públicos B3/CVM baixados no job pela URL oficial e conferidos pelo sha256 do pin | C8, C9, C10 | `552337a` |
| `data/SOURCES.json`, `RAW_LOGS/pin/` | pin das fontes públicas antes do run (`build_real_panel.py pin`, sem mudança) | D-11, D-16 | `552337a` |
| `RAW_LOGS/contract-revalidation/static_checks.json`, `scripts/contract_revalidation.py` | C24.3 (a), (b) e (e) verdes. (f) sem run de push verde no SHA exato | C24.3 | `552337a` |
| `RAW_LOGS/hosted-ci/stocks-predictor_6f857b2_run36363108348*`, `FINDINGS.json` | run `workflow_dispatch` do CI no final_commit: Quality verde e `secrets` vermelho por falso positivo do main. Achado IS-F005 (P1, decisão do dono) | C21, prompt 9.3 | `552337a` |

## 2026-09-28 — C14 da integration-crypto (cain e ecosystem mudaram)

Ver `qualification/integration-crypto/QUALIFICATION_CHANGELOG.md`, seção "reemissão C14 pela integration-stocks". Fases refeitas com as wheels finais desta missão: run 36365192302 e Windows no PC 2 (D-23). A attestation QUALIFIED anterior foi preservada (`_superseded_112d18a35c7b`) e a reemitida também é **QUALIFIED**. Commits: `e0b4bc3` (alvos do runtime e domínio sem configuração do isolamento: `brasileirao`) e este PR.

## 2026-09-28 — runtime, fechamento dos gates e attestation

| Onde | O quê | Por quê | Commit / PR |
|---|---|---|---|
| `RAW_LOGS/runtime/run36365355063/` (Linux) e `run36365355063-windows/` | run de push no commit `e0b4bc3`, com `run.json` de cada lado. Linux: cleanroom-final, C24.3 (d), E2E, N+1 congelado e integrado, isolamento com o cripto integrado, contradição, F01–F15 e soak (LLM local no runner). Windows: E2E + restart. Todas as fases terminaram com exit 0 | C8–C10, C24.3 | este PR |
| `RAW_LOGS/{core-identity,final-wheels,protected,secrets}/`, `RAW_LOGS/hosted-ci/final/` | conferências finais; o conjunto protegido acusa a attestation da integration-crypto reemitida (IS-F006) | C4, C7.1, C15.1, C21 | este PR |
| `scripts/protected_check.py` | registra, para uma attestation alterada, o arquivo `_superseded_` e o `supersedes_sha256`, só como registro: o item continua contado como alterado | C15.1 | este PR |
| `scripts/render_reports.py`, `scripts/evidence_numbers.py`, relatórios `*_REPORT.md`, `EVIDENCE_NUMBERS.json` | relatórios gerados de `RAW_LOGS/`. A configuração da política vem de `FROZEN_PARAMETERS.json` e a decisão de cada proposta de LLM vem do `commands.log`; nada é digitado | C20 | este PR |
| `RAW_LOGS/pr-merge-check/`, `FINDINGS.json` | cain#60 e ecosystem#32 contra o main atual (merge-tree, sem merge). IS-F006 (P2): parâmetros congelados contraditórios, C14 × conjunto protegido. IS-F007 (P2): o main do cain declara 0.4.13rc7 com outro código (PR #59, fora desta missão) | C6 | este PR |
| `scripts/update_gates.py`, `GATES.json`, `ATTESTATION_PARTIAL_<fase>.json`, `QUALIFICATION_ATTESTATION.json` | ledger aplicado fase a fase e parciais C8 gravados na ordem das fases (as fases do runtime rodaram num único run). Attestation final **NOT_QUALIFIED**: `BLOCKERS_ZERO` FAIL (IS-F005 P1), `PROTECTED_ARTIFACTS_UNCHANGED` FAIL pela letra (IS-F006), `HOSTED_CI` e `DOMAIN_CONTRACTS_PRESERVED` NOT_RUN com BLOCKED (IS-F004/IS-F005) e os demais gates PASS | C7.3 | este PR |

## 2026-09-28 — reemissão 1: decisões do dono sobre IS-F004, IS-F005 e IS-F006 → **QUALIFIED**

Decisões do dono no chat da sessão:
- **IS-F004 e IS-F005, opção (b):** "aceita o run workflow_dispatch (b) e reemite".
- **IS-F006, opção (a):** "(a) Aceitar a reemissão C14", escolhida numa pergunta com opções.

Nenhuma fase do runtime foi refeita: o código, as wheels e o runtime não mudaram. Foram reavaliados os gates que dependiam das decisões, com evidência nova em diretórios `-r1`. Os raw logs da attestation anterior não mudaram.

| Onde | O quê | Por quê | Commit / PR |
|---|---|---|---|
| `RAW_LOGS/c0/c0_preflight_81f539c.log`, `..._run1_strict.log`, `scripts/c0_preconditions.py` | pré-voo 4.1–4.7 refeito no main novo (`81f539c`). A 1ª execução acusou `5.1/adapters-intocados-no-main`, porque o dono mergeou o stocks-predictor#107 e o main passou a ter o adapter desta missão. A checagem passa a seguir o texto da 5.1 do prompt: a divergência não toca `adapters/`, o único commit não-merge que toca `adapters/` em `61fc017..main` é o `6f857b2` da missão, e a árvore de `adapters/` do main é a do `6f857b2`. O resultado literal fica como OBS e o log estrito foi preservado. 2ª execução: 0 falhas | pré-voo antes de cada commit | este PR |
| `FINDINGS.json`, `scripts/owner_decision_is_f004_f005.py`, `scripts/owner_decision_is_f006.py` | IS-F004, IS-F005 e IS-F006 passam a `ACCEPTED_LIMITATION`, com as palavras do dono e o que cada decisão cobre. Correção do IS-F005: o commit acusado é `9f7cce3`, da branch `evidence/prompt1-segredos-20260924`, e não o `28f17d2` do main; o registro anterior também não dizia que a varredura da árvore e o controle do job `secrets` ficaram pulados. IS-F001 atualizado: depois do #107, o main do stocks declara 0.3.0rc3 com outro código | C6 | este PR |
| `RAW_LOGS/hosted-ci/final-r1/`, `scripts/hosted_ci_owner_acceptance.py` | coleta nova do HOSTED_CI e conferência mecânica da decisão (b): 9 OK. A 1ª execução falhou por defeito do próprio script: contava os passos automáticos do runner (`Post Run`, `Complete job`). O log e o JSON dela foram preservados | C21, prompt 9.3, decisão do dono | este PR |
| `RAW_LOGS/hosted-ci/final-r1/tree_scan_local.log`, `*.sarif`, `scripts/tree_scan_local.sh` | os dois passos pulados do job `secrets` foram reproduzidos localmente, como diagnóstico e não como CI hospedado. Mesmo gitleaks 8.24.3, com o tar conferido contra o `gitleaks_sums.txt` da release. Resultado: árvore de `6f857b2` com o `.gitleaks.toml` do repo sem achados, e controle do token sintético detectado | cobrir a lacuna do run aceito | este PR |
| `RAW_LOGS/contract-revalidation-r1/`, `scripts/contract_revalidation.py` | C24.3 (f) aceita o run de push verde ou o run `workflow_dispatch` aceito pelo dono e conferido. Resultado: 12 OK, 0 falhas | C24.3, decisão do dono | este PR |
| `RAW_LOGS/protected-r1/`, `scripts/update_gates.py` | conjunto protegido reconferido: 3386/3387 iguais. O item alterado é aceito pela decisão do IS-F006 só com a supersessão conferida; todo outro item alterado continuaria FAIL | C15.1, decisão do dono | este PR |
| `RAW_LOGS/secrets-r1/`, `EVIDENCE_NUMBERS.json`, relatórios, `scripts/render_reports.py` | varredura de segredos refeita: 0 achados. Números e relatórios regerados; HOSTED_CI e PROTECTED descrevem as decisões a partir dos arquivos | C20 | este PR |
| `QUALIFICATION_ATTESTATION_superseded_a441c88dfbbe.json`, `ATTESTATION_PARTIAL_r1-attestation.json`, `QUALIFICATION_ATTESTATION.json` | a attestation NOT_QUALIFIED foi preservada. A nova é **QUALIFIED**: 30/30 gates PASS, P0=0, P1=0, P2=4 abertos (IS-F001, IS-F002, IS-F003, IS-F007), com `supersedes_sha256` apontando para a anterior | C7.1 regra 8, C7.3 | este PR |

## 2026-09-28 — depois da attestation: IS-F001, IS-F002, IS-F003 e IS-F007 corrigidos nos mains

Pedido do dono no chat da sessão: "arruma esses erros" (os achados P2 que ficaram abertos na attestation QUALIFIED). As correções estão nos `main` dos repositórios, não no runtime qualificado. A attestation (`12411b51…`) continua valendo como está: ela fixa as wheels `v0.3.0rc3` e `v0.4.13rc7`, onde IS-F002 e IS-F003 continuam verdadeiros. O `FINDINGS.json` é evidência da attestation (`findings_file` com sha256), por isso os status não mudam aqui. Eles serão atualizados na próxima reemissão: segundo a sessão do cripto, o dono decidiu fazer uma release única do cain e uma requalificação C14 das três integrações depois da integration-brasileirao.

| Onde | O quê | Achado | Commit / PR |
|---|---|---|---|
| `stocks-predictor` `pyproject.toml`, `uv.lock`, recibos R8 em `docs/engineering/2026-09-28-integration-stocks/evidence/`, selo | versão do main passa a 0.3.0rc4 (não publicada), com o procedimento R8. Recibo real: 55.986 linhas, fonte `34b77468…` igual antes e depois, `rows_sha256` `6d47c43e…`, PASS. Capacidade: 250.000 linhas, PASS. Selo de 263 arquivos, verify PASS. Suíte local em `7ea3657`: todos os passos com exit 0, 1192 passed + 71 subtests, cobertura 80%. CI de push do main `4c82885`: success. Logs em `RAW_LOGS/pos-attestation/` | IS-F001 | `7ea3657`; leonardosovienski/stocks-predictor#108 (mergeado) |
| `cain` `src/cain/orchestration/{policy,llm}.py`, teste, `docs/ORCHESTRATION_V2.md` | `policy.declared_parameters`: variantes de `parameters` do `request_schema` congelado do domínio. A R06 compara custos só quando a variante declara as chaves de custo; o LLM grava `placebo_seed` só onde a variante declara esse parâmetro. No cripto nada muda. Suíte local: 1367 passed, 3 skipped, cobertura 87.42%. CI do PR e de push do main `51bfec3`: success | IS-F002, IS-F003 | `d8b8061`; leonardosovienski/cain#62 (mergeado) |
| `cain` versão do main | 0.4.13rc8 (não publicada), feita pela sessão do cripto | IS-F007 | leonardosovienski/cain#61 (mergeado) |
| `RAW_LOGS/c0/c0_preflight_ebf32fa.log` | pré-voo 4.1–4.7 no main novo, antes deste commit: 46 checks, 0 falhas | pré-voo antes de cada commit | este PR |

## 2026-09-28 — ciclo 2 da freeze-parameters (C14): política v2 do cain e hipóteses só para o LLM (cain 0.4.13rc11)

Decisões do dono no chat desta sessão, em perguntas com opções:
- **"Aprovo o ciclo novo"**: ciclo novo dos parâmetros congelados na release única do cain. As mudanças propostas foram:
  - 17-collection passa a ALLOW;
  - as fixtures de contradição viram experimentos distintos;
  - os vetores do N+1 são recalculados;
  - REAL-001/002/003 viram experimentos distintos.
  Perfil de soak, dados e pisos não mudam.
- **"Hipóteses para o LLM"**: com a R17, o piso da C10 (≥ 5 propostas de LLM) ficou inatingível na rc10. A decisão cria 5 hipóteses de qualificação só para o LLM, cada uma um experimento distinto (controle negativo com semente própria), admitidas pelo operador. Isso exige uma nova release do cain (rc11) e a C14 das três integrações.

Pela C14, a fase inteira é um novo ciclo. As fases a partir de publish-candidates serão refeitas na rc11. **Nenhuma fase roda antes do merge deste PR pelo dono (C15).**

| Onde | O quê | Por quê |
|---|---|---|
| `FROZEN_PARAMETERS.json`, `FROZEN_PARAMETERS_cycle1_771b8a23e9b9.json`, `scripts/freeze_cycle2.py` | `decision_policy` v2: `rule_order` R01–R17 conferida contra a docstring de `policy.py` em `fb0e1dc` (v0.4.13rc10), mais `policy_module` com o sha256. `stocks_config` ganha as 5 hipóteses `stocks:QUAL-LLM-CTRL-001..005` (proponíveis, `proposal_overlays` com controle negativo SHUFFLED_LABELS, sementes 9001–9005) e o estado dos limites de framework do ciclo 1 (IS-F002 e IS-F003, corrigidos no cain#62). Outras mudanças: `operator_env` com as 5 hipóteses; `base.framework_cycle2` (rc10 + o que entra na rc11); `repos`; `c14_cycle2`; `hosted_ci_rule` com a decisão IS-F004/IS-F005; `decisions_cited` com as palavras do dono; bloco `cycle` com supersedes. O ciclo 1 fica byte a byte (mesmo blob git) no arquivo de supersedes | C14, C15 |
| `FROZEN_VECTORS.json`, `FROZEN_VECTORS_cycle1_3ad4d197cb79.json`, `scripts/build_vectors.py`, `fixtures/proposals/**`, `fixtures/v2/stocks/contradiction-*` | Viram outro experimento, com controle negativo SHUFFLED_LABELS: e2e/02 e e2e/08 (sementes 2 e 8), n1/01-next (semente 1) e contradição 02–04 (sementes 2–4). n1/17-collection passa a ALLOW (cain#62). No soak, o 1º ciclo é o backtest real sem controle e do 2º em diante usa semente = número do ciclo. Entram 5 fixtures `fixtures/proposals/llm/` (o builder do cain lê delas o tipo de pedido) e a seção `llm_hypotheses`. O bloco `cycle` aponta para o ciclo 1 | R17 (mesmo experimento com outro nome) |
| `scripts/operator_env.py`, `scripts/soak.py`, `scripts/failure_matrix.py`, `scripts/isolation.py` | Operador admite as 5 hipóteses do LLM. Soak: semente por ciclo a partir do 2º, e a checagem final aceita as hipóteses do LLM. Matriz: a 2ª proposta de cada ponto recebe controle negativo de semente k, para F07, F10 e F14 não caírem na R17 antes da regra que testam. Isolamento: na rc10+ os três domínios têm configuração, então o domínio fora do protocolo (`forex`) dá CONFIG_INVALID e a proposta do stocks na orquestração do brasileirao dá BLOCK DOMAIN_MISMATCH, como na integration-crypto | C14 |
| `FINDINGS.json` (`IS-F008`, `scripts/add_finding_is_f008.py`) | O ciclo 2 troca quatro itens do `PROTECTED_SET.json`: os congelados desta missão (parâmetros e vetores) e dois da integration-crypto (os congelados do ciclo 2 dela e a attestation reemitida em dois saltos). Os bytes protegidos ficam preservados e encadeados. **Aguarda a decisão do dono** | C15.1 |
| `GATES.json`, `scripts/cycle2_gates.py`, `ATTESTATION_PARTIAL_freeze-parameters-c2.json` | Gates refeitos no ciclo 2 voltam a NOT_RUN, com o ciclo 1 em `cycle1_evidence`. Ficam como estão STACK_BASELINE_FROZEN e BLOCKERS_ZERO. `supersedes_sha256` passa a ser a attestation atual. Parcial com P0=0, P1=0, P2=5 | C14, C8 |
| `RAW_LOGS/freeze/freeze_parameters_cycle2.log` | Execução dos scripts, com os sha256 do ciclo 1 e a igualdade do blob git dos arquivos preservados | C20 |

Diagnóstico local antes de congelar (WSL do PC 2, não é gate; `RAW_LOGS/freeze/diag-c2/`, com os `SUMMARY.json` de cada fase e o `phases.log`). Foi feito com o `runtime_env.sh` da missão e uma wheel candidata da rc11: cain `fb0e1dc` + cain#72 + `stocks.json` gerado destes congelados. Completam o runtime o transporte rc5, o stocks rc3 e o cripto integrado.
- e2e 55/0.
- N+1 63/0; integrado 64/0.
- Isolamento 28/0; contradição 9/0.
- Matriz F01–F15 sem falha.
- Soak 43/0, com o modelo local `qwen3.5:4b` (no Actions é `qwen2.5:0.5b`):
  - todos os pisos atingidos;
  - as 5 hipóteses do LLM viraram 5 tasks distintas (ALLOW, sementes 9001–9005);
  - a 6ª chamada parou em NO_ELIGIBLE_HYPOTHESIS;
  - `llm_proposals` = 5, exatamente o piso: sobra uma tentativa para falha do modelo (no ciclo 1 do Actions, o `qwen2.5:0.5b` acertou 6 de 6).
- Soak, 1ª tentativa (`soak-try1/`), com controle em todos os ciclos: 40/3.
  - O LLM escolheu `stocks:QUAL-PIT-MOM-001`, proponível desde o ciclo 1 mas não admitida pelo operador desta integração, e o domínio recusou (TERMINAL_REFUSAL).
  - Três checagens de tolerância zero contam só resultados admitidos.
  - Daí o 1º ciclo do soak sem controle: o molde emprestado dessa hipótese passa a repetir um experimento já rodado (R17).

## 2026-09-28 — IS-F008: decisão do dono (reemissão encadeada)

Decisão no chat da sessão, numa pergunta com opções: **"(a) Encadeada (Recomendado)"**. O gate PROTECTED_ARTIFACTS_UNCHANGED aceita cada um dos 4 itens do IS-F008 só com a cadeia conferida byte a byte até o sha256 protegido (arquivo preservado + ponteiro, salto a salto). Todo outro item alterado continua FAIL.

| Onde | O quê |
|---|---|
| `FINDINGS.json`, `scripts/owner_decision_is_f008.py` | IS-F008 → `ACCEPTED_LIMITATION`, com as palavras do dono e o texto da opção |
| `scripts/protected_check.py` | Para os 4 itens, segue os ponteiros (`cycle.supersedes` nos congelados; `supersedes_sha256` + `_superseded_<sha12>` nas attestations) até `MAX_HOPS`. `all_unchanged` continua sendo a letra da C15.1; o gate usa `all_unchanged_or_chained`. Teste a seco no checkout deste commit: 3387 itens, os 4 encadeados (a attestation da integration-crypto em 2 saltos), nenhum outro alterado. A conferência que vale como evidência é a da fase protected do ciclo 2 |
| `RAW_LOGS/c0/c0_preflight_30c02c7.log` | Pré-voo 4.1–4.7 no main novo |

## 2026-09-28 — ciclo 2: run na cain 0.4.13rc11 e decisão do dono de seguir para a rc12

- **Run 36435997297** (push em `integration-stocks/runtime-…-c2`, commit `e1cf15a`; artefatos em `RAW_LOGS/runtime/run36435997297/` e `-windows/`). Rodou com o cain 0.4.13rc11 (`3b65ffe`), o transporte 0.1.0rc5 e o stocks rc3. Todas as fases terminaram com exit 0:
  - cleanroom-final;
  - C24.3 (d) 11/0;
  - e2e 55/0;
  - N+1 63/0, integrado 64/0;
  - isolamento 28/0; contradição 9/0;
  - F01–F15 sem falha;
  - soak 43/0 com `qwen2.5:0.5b`: 5 propostas de LLM, uma por hipótese `QUAL-LLM-CTRL`, sementes 9001–9005. O modelo errou 1 das 6 tentativas.
  - Windows: e2e + restart verde.
- **Conferências feitas na rc11** (stocks-predictor `6f857b2`, que não muda):
  - `RAW_LOGS/hosted-ci/final-c2/`: aceite do dono IS-F004/IS-F005 (b) reconferido 9/0. A varredura local da árvore agora usa um Python gerenciado, e `tree_scan_local.sh` corrige o desvio da reemissão 1: PASS, controle detectado.
  - `RAW_LOGS/contract-revalidation-c2/`: C24.3 estático 12/0. A 1ª execução, chamada sem o arquivo do aceite, fica preservada como `*_run1_sem_aceite.*`.
- **Regressão da rc11 no cripto.** A sessão cripto achou que, com `result_metrics`, o contexto do LLM do cripto passava do orçamento do provider. A correção é o cain#75 (só `llm.py`), mergeado pelo dono, e sai na rc12. O stocks não é atingido.
- **Decisão do dono** no chat, pergunta com opções: **"Seguir para a rc12 (Recomendado)"**. A integration-stocks fecha a attestation na mesma release das outras duas integrações, com C14 de novo: run e conferências refeitos na rc12.
  - Não há novo ciclo de congelados: a política (`policy.py`, sha256 `aff2f5fc…`) e o `stocks.json` são byte a byte os da rc11.
  - O `FROZEN_PARAMETERS.json` do ciclo 2 cita a rc11 como a release planejada; o `runtime_targets.json` fixa a rc12.
  - O run da rc11 fica preservado como evidência.

## 2026-09-28 — ciclo 2 fechado na cain 0.4.13rc12: attestation reemitida **QUALIFIED**

A cain v0.4.13rc12 foi publicada pela sessão cripto: `302a5c8`, rc11 + cain#75, orçamento de contexto do modo de proposta. Esta sessão a conferiu de forma independente (`RAW_LOGS/publish-candidates/verify_cain_0.4.13rc12.log`):
- tag → commit;
- digest da API = download anônimo;
- `policy.py` e `stocks.json` na wheel com os bytes do congelado e da rc11;
- CI de push do main e CI da tag verdes.

| Onde | O quê |
|---|---|
| `runtime_targets.json`, `hosted_ci_targets.json`, `data/SOURCES.json`, `RAW_LOGS/pin/pin_3.log` | Alvos na rc12 e pin novo antes do run, com o mesmo painel `8509f54f…` (D-16) |
| `RAW_LOGS/runtime/run36440479456/` e `-windows/` | Run de push em `integration-stocks/runtime-…-rc12` (`686e7de`), todas as fases com exit 0: cleanroom-final; C24.3 (d) 11/0; e2e 55/0; N+1 63/0 e integrado 64/0; isolamento 28/0; contradição 9/0; F01–F15; soak 43/0 com 5 propostas de LLM (`qwen2.5:0.5b`), uma por hipótese `QUAL-LLM-CTRL`, todas ALLOW (R14). Windows: e2e + restart 55/0 |
| `scripts/cycle2_publish.py` | Fase publish-candidates-c2: final_commits e final_wheels (cain 0.4.13rc12 `302a5c8`, transporte 0.1.0rc5 `b11494a`, stocks 0.3.0rc3 `6f857b2`) |
| `RAW_LOGS/core-identity-c2/`, `RAW_LOGS/final-wheels/final_wheels_check_run36440479456.json` | Identidade do Core 13/0; final_wheels 19/0 |
| `RAW_LOGS/hosted-ci/final-rc12/` | Push verde no SHA exato: cain `302a5c8` e ecosystem `b11494a`. stocks-predictor pelo aceite do dono (IS-F004/IS-F005 b), reconferido 9/0. Varredura local da árvore com Python gerenciado: PASS |
| `RAW_LOGS/contract-revalidation-rc12/` | C24.3 estático 12/0, com o aceite da rc12 |
| `RAW_LOGS/protected-c2/` | Conjunto protegido, 3387 itens, conferido duas vezes: no checkout desta branch e num snapshot do main `8817b7c`, que já tem o ciclo 3 da integration-crypto. Nos dois, só os 4 itens do IS-F008 mudam, e cada um fecha a cadeia salto a salto até o sha256 protegido: a attestation da integration-crypto em 2 saltos na branch e em 3 no main. Aceito pela decisão do dono no IS-F008 |
| `RAW_LOGS/secrets-c2/`, `scripts/secrets_scan.py` | 0 achados, com os finais lidos de `runtime_targets.json` |
| `FINDINGS.json`, `scripts/cycle2_findings.py`, `RAW_LOGS/findings-c2/versions.log` | Passam a FIXED, cada um conferido contra raw log: IS-F001 (main do stocks em 0.3.0rc4, sem release rc4), IS-F002 (17-collection ALLOW no N+1), IS-F003 (propostas de LLM sem `placebo_seed`) e IS-F007 (main do cain = commit da tag da versão que declara) |
| relatórios, `scripts/render_reports.py`, `scripts/update_gates.py`, `scripts/evidence_numbers.py` | Relatórios do ciclo 2: política v2 e `rule_order` lidas dos congelados; cadeias do IS-F008; hipóteses só para o LLM; limites do framework com o estado do ciclo 2. `update_gates.py` aponta para as evidências do ciclo 2; as do ciclo 1 ficam em `GATES.json → cycle1_evidence` e no histórico |
| `QUALIFICATION_ATTESTATION_superseded_12411b51d527.json`, `ATTESTATION_PARTIAL_ciclo2-attestation.json`, `QUALIFICATION_ATTESTATION.json` | A attestation da reemissão 1 do ciclo 1 (QUALIFIED, cain rc7) fica preservada. A nova é **QUALIFIED**: 30/30 gates PASS, P0=0, P1=0, P2=0, `supersedes_sha256` = `12411b51…` |
| `RAW_LOGS/c0/c0_preflight_8817b7c.log` | Pré-voo 4.1–4.7 no main atual: 0 falhas |

## 2026-09-28 — depois da attestation do ciclo 2: disputa de consumidores (registro + regra, decisão do dono)

Isto não é fase nem gate. A attestation QUALIFIED do ciclo 2 (`9979d19b…`, PR #80, merge `957b13b`) continua como está. O `FINDINGS.json` é evidência dela (sha256), por isso o achado entra nele só na próxima reemissão, como **IS-F009 (P2)**.

**Teste** (`scripts/race.py`; evidência em `RAW_LOGS/pos-attestation-c2/race/RACE.json` e `race.log`):
- Sugerido pela sessão cripto, rodado numa rodada de uso real do CAIN com o stocks no WSL do PC 2.
- Runtime qualificado do ciclo 2: cain 0.4.13rc12, stocks-predictor 0.3.0rc3, transporte 0.1.0rc5, painel real.
- Em cada uma das 20 repetições, com estado novo: a semente (backtest real) é despachada, e dois `predictor-research-consumer` idênticos começam juntos sobre a mesma task.

**O que o teste mostrou:**
- **Nas 20:** um experimento no journal do domínio, uma admissão aceita, RESULT terminal ingerido e nenhuma queda de processo. Sem efeito duplicado nem perdido.
- **Também nas 20, o consumidor perdedor publica um envelope falso ao lado do RESULT do vencedor:**
  - **16×** `OPS_FAILED_RETRYABLE`, motivo `OPS_SKIPPED lock_not_acquired`: a trava do Ops funciona, mas a perda é anunciada como falha;
  - **4×** `RECONCILIATION_REQUIRED`, motivo `REFERENCE: materialized reference changed after materialization: readiness`: o stocks materializa as referências no estado do domínio antes do `run_job` do Ops, fora da trava, e o perdedor vê o arquivo reescrito pelo vencedor.
- **Efeito no CAIN:** nos 4 casos de `RECONCILIATION_REQUIRED`, o CAIN ingere o `REQUIRES_HUMAN` e segura o domínio. A proposta seguinte vira `REQUIRE_HUMAN DOMAIN_RECONCILIATION_PENDING` (R09), com o experimento feito uma vez e certo. É uma parada falsa, fail-closed.
- **Mesmo padrão no cripto:** IC-F016 e IC-F017, na integration-crypto.

**Decisão do dono** no chat da sessão, pergunta com opções: **"Registrar + regra (Recomendado)"**.
- **Regra:** um consumidor por domínio por vez, o que o agendador do Ops já garante. É a mesma regra decidida no cripto, que a sessão cripto põe no documento do stack da Etapa B no ecosystem-predictor.
- **Código:** não muda. A correção de fundo (tomar a trava antes de materializar) é código de domínio fora dos adapter_paths; pela C24.4 ela reabriria a Etapa A do stocks.

## 2026-09-28 — ciclo 3 da freeze-parameters (C14): cain 0.4.13rc13 e 8 hipóteses só para o LLM

**Decisão do dono** no chat da sessão, pergunta com opções, depois da segunda rodada de utilidade prática do CAIN com o stocks na rc12: **"cain rc13 + ciclo 3 (Recomendado)"**. Isso cobre:
- no cain, as correções da rodada;
- no stocks, mais 3 hipóteses só para o LLM, para dar folga ao piso do soak;
- ciclo 3 dos congelados citando a rc13;
- IS-F009 no FINDINGS;
- C14 nas três integrações.

Família (D-24) e disputa no código do stocks ficam como estão. **Nenhuma fase roda antes do merge deste PR pelo dono (C15).**

| Onde | O quê |
|---|---|
| `FROZEN_PARAMETERS.json`, `FROZEN_PARAMETERS_cycle2_11ad4cb7f255.json`, `scripts/freeze_cycle3.py` | O ciclo 2 fica byte a byte no arquivo de supersedes, que aponta para o ciclo 1. Mudanças: `stocks_config` e `operator_env` com **8 hipóteses só para o LLM** (`QUAL-LLM-CTRL-001..008`, sementes 9001–9008); `decision_policy.framework` na rc13; `policy_module` conferido de novo no commit do cain#77, com os mesmos bytes; `base.framework_cycle3`; `repos.cain`; `c14_cycle3`; decisões do dono com as palavras |
| `FROZEN_VECTORS.json`, `FROZEN_VECTORS_cycle2_efba834f780f.json`, `scripts/build_vectors.py`, `fixtures/proposals/llm/06..08` | 3 fixtures novas. O bloco `cycle` aponta para o ciclo 2 e guarda o histórico do ciclo 2 |
| `scripts/operator_env.py` | O operador admite as 8 |
| `FINDINGS.json`, `scripts/add_finding_is_f009.py` | **IS-F009 (P2, ACCEPTED_LIMITATION):** disputa de consumidores, com as contagens do `RACE.json` (16× `OPS_FAILED_RETRYABLE`, 4× `RECONCILIATION_REQUIRED`) e a decisão "Registrar + regra (Recomendado)" |
| `GATES.json`, `scripts/cycle3_gates.py`, `ATTESTATION_PARTIAL_freeze-parameters-c3.json` | Gates do ciclo 3 voltam a NOT_RUN, com o ciclo 2 em `cycle2_evidence`. Parcial com P0=P1=P2=0 |
| `RAW_LOGS/freeze/freeze_parameters_cycle3.log` | Execução, com os sha256 do ciclo 2 e a igualdade do blob git |
| `RAW_LOGS/freeze/diag-c3/` | Diagnóstico antes de congelar (abaixo) |

**O que a rc13 junta:**
- a rc12 (`302a5c8`);
- o **cain#77**, aprovado na revisão independente da sessão integration-brasileirao, com o soak da missão cripto conferido pela sessão cripto;
- o `stocks.json` regenerado do merge deste ciclo e a versão.

**O que muda no cain#77:**
- o molde do LLM nunca é task recusada;
- `allowed_requests` no contexto do modelo;
- `refusal_mismatches` na justificativa;
- linter: números de identificador entre crases são nomes, número solto continua checado, 95% ↔ 0.95, e número colado a unidade é número;
- `findings-policy` v2: nome de família ou trial no enunciado, e candidatos por embedding só para revisão.

**Diagnóstico local** (WSL, não é gate; `RAW_LOGS/freeze/diag-c3/`), com a wheel candidata (cain#77 + `stocks.json` destes congelados) e o runtime da missão:
- **Fases:**
  - e2e 55/0; N+1 63/0 e integrado 64/0;
  - isolamento 28/0; contradição 9/0; F01–F15 sem falha;
  - **soak 44/0 com 6 propostas de LLM** (piso 5; no ciclo 2 foram exatamente 5).
- **Rodada de utilidade 3** (10 chamadas ao modelo, `utility-round3/`):
  - **8 experimentos distintos**, depois NO_ELIGIBLE;
  - depois das guardas, **nenhuma reproposta do canário** (na rc12, o molde emprestado era a task recusada);
  - guardas 12/12;
  - memória = fonte autoritativa 10/10;
  - `allowed_requests` no prompt; o modelo descreveu o experimento certo ("controle negativo de rótulos embaralhados");
  - `refusal_mismatches` acusou a frase falsa "001 a 005 foram recusadas";
  - findings: `momentum 12-1 cross-sectional` agora reconhecida como encerrada;
  - linter: 5/5 casos.
- **Limites que continuam:**
  - paráfrase sem nome não é decidida;
  - os candidatos por embedding acertam 1 de 3;
  - IS-F009 fica pela regra;
  - famílias do main do stocks ficam pela D-24.

## 2026-09-28 — ciclo 4 da freeze-parameters (C14): famílias do main (D-26), transporte 0.1.0rc6 e cain 0.4.13rc13 com o cain#78

**Decisões do dono** no chat da sessão, perguntas com opções, depois de "arruma os não resolvidos":
- **"Somar as famílias do main (Recomendado)"**, registrada como **D-26** no `qualification/DECISIONS.json`. Muda só a D-24 (2) quanto à lista de famílias congeladas.
- **"Só o transporte (Recomendado)"**: trava por domínio no consumidor do transporte (0.1.0rc6). Nenhum domínio muda.
- **"Calibrar embedding (Recomendado)"**: medição no cain#78. Pela regra fixada antes de medir, deu `KEEP_REVIEW_ONLY`, e a findings-policy continua na v2.
- **Agenda de pesquisa, "todas":** não entra neste ciclo. Cada frente pede fator novo no código do stocks e reabertura da Etapa A (C24.4).

**Nenhuma fase roda antes do merge deste PR pelo dono (C15).**

| Onde | O quê |
|---|---|
| `qualification/DECISIONS.json`, `scripts/owner_decision_d26.py` | D-26 com as palavras do dono, a pergunta e as duas opções. O script confere se o arquivo regravado volta aos mesmos bytes, blob e sha256 do `research/scientific_state.json` em `4c82885` e as famílias acrescentadas |
| `FROZEN_PARAMETERS.json`, `FROZEN_PARAMETERS_cycle3_6cd6a68059c7.json`, `scripts/freeze_cycle4.py` | O ciclo 3 fica byte a byte no arquivo de supersedes, que aponta para o ciclo 2. Mudanças descritas abaixo da tabela |
| `GATES.json`, `scripts/cycle4_gates.py`, `ATTESTATION_PARTIAL_freeze-parameters-c4.json` | Nenhum gate do ciclo 3 chegou a rodar. Continuam NOT_RUN, com nota do ciclo 4; o bloco do ciclo 3 fica dentro do novo. Parcial com P0=P1=P2=0 |
| `RAW_LOGS/c0/c0_preflight_108d42f.log` | Pré-voo 4.1–4.7 no main `108d42f`: 0 falhas |
| `RAW_LOGS/freeze/freeze_parameters_cycle4.log` | Execução com o merge do cain#78 no main (`1f38e71`, árvore igual à do head da PR). A execução 1, que citava o head da PR antes do merge, fica em `freeze_parameters_cycle4_run1_head_da_pr.log` |
| `RAW_LOGS/freeze/diag-c4/` | Diagnóstico antes de congelar (abaixo) |

**Mudanças no `FROZEN_PARAMETERS.json`:**
- `stocks_config.frozen_families`: **17 famílias**. Entram `quality_net_margin` e `quality_roe_leverage_double_filter`, e nenhuma sai.
- `stocks_config.additional_frozen_families`: o que o builder do cain lê e confere.
- `protected_set_initial.never_read` com a exceção da D-26.
- `decision_policy.framework` na rc13 com o cain#78 e o transporte 0.1.0rc6.
- `policy_module` conferido de novo no merge, com os mesmos bytes.
- `base.framework_cycle4`, `repos.cain`, `repos.ecosystem-predictor` e `c14_cycle4`.
- Os vetores são os do ciclo 3, sem mudança.

**O que a rc13 junta:**
- a rc12 (`302a5c8`) e o **cain#77**;
- o **cain#78**, mergeado pelo dono (`1f38e71`, CI do push verde):
  - builder: `additional_frozen_families`, que só acrescenta; `crypto.json`, `brasileirao.json` e o `stocks.json` atual saem com os mesmos bytes;
  - `ingest-state --describe`;
  - calibração selada: conjunto, procedimento e medição em três commits;
  - transporte 0.1.0rc6 no `uv.lock`;
- o `stocks.json` regenerado do merge deste ciclo e a versão.

**Transporte 0.1.0rc6** (ecosystem-predictor#36, publicado por esta missão):
- tag `predictor-research-transport-v0.1.0rc6` em `bac1f7b`, wheel `6c7e83c4…`;
- build reprodutível 2×; download anônimo igual ao digest da API.
- A sessão cripto conferiu no Windows (msvcrt): 20/20, perdedor com exit 6 e nada publicado, morte da dona da trava com retomada 3/3.
- **Observação da sessão cripto**, fora da matriz congelada e sem ligação com a trava: com morte em `after_result_write`, o sucessor reentrega, o domínio responde `DUPLICATE`, e o inbox do CAIN fica com 2 entradas `TERMINAL_RESULT` com o mesmo payload e 1 fato na memória. Fica como melhoria possível do inbox numa versão futura.

**Diagnóstico local** (WSL, não é gate; `RAW_LOGS/freeze/diag-c4/`). Rodou com a wheel candidata (cain#78 + `stocks.json` destes congelados) e o runtime da missão com o transporte 0.1.0rc6 publicado.
- **Fases:**
  - e2e 55/0;
  - N+1 63/0 e integrado 64/0; ciclo do cripto 1/0;
  - isolamento 28/0; contradição 9/0;
  - F01–F15 sem falha;
  - **soak 44/0 com 6 propostas de LLM** (piso 5).
- **Famílias:** `quality_net_margin`, `quality_roe_leverage_double_filter` e `net_margin` dão BLOCK R05 `HYPOTHESIS_CLOSED`; sem família, ALLOW R14.
- **Disputa (race.py, 20 repetições):** 20/20 com exits (0, 6), 1 `RESULT` e 1 experimento em cada, **0 envelopes falsos** e 0 exceções. Com o transporte 0.1.0rc5 eram 16× `OPS_FAILED_RETRYABLE` e 4× `RECONCILIATION_REQUIRED` falsos. Na reemissão, IS-F009 passa a FIXED se a disputa nas wheels publicadas repetir isto.

**Limites que continuam:**
- paráfrase sem nome não é decidida: embedding só para revisão, e o número fica com o dono;
- as frentes da agenda esperam a Etapa A do stocks.

## 2026-09-28 — ciclo 4 fechado na cain 0.4.13rc13 e no transporte 0.1.0rc6: attestation reemitida **QUALIFIED**

**Releases publicadas por esta sessão:**
- **cain v0.4.13rc13**, de `960fb25` (main com cain#77, #78 e #79; CI de push 8/8 verde e CI da tag verde). Build reprodutível 2×; wheel `a1d94fd5…`, com download anônimo = digest da API.
  - Dentro da wheel: `policy.py` `aff2f5fc…` (igual), `stocks.json` `c514a7b0…` (17 famílias, 8 hipóteses do LLM), `crypto.json` e `brasileirao.json` iguais byte a byte, findings-policy v2.
  - Log: `RAW_LOGS/publish-candidates/publish_cain_0.4.13rc13.log`.
- **predictor-research-transport v0.1.0rc6**, de `bac1f7b`: `publish_transport_0.1.0rc6.log`.

**Decisões do dono depois do merge do ciclo 4** (chat da sessão, perguntas com opções):
- **Paráfrase: "Só revisão (Recomendado)".** O embedding continua listando candidatos para revisão humana, e a findings-policy fica na v2. A medição do cain#78 mostrou que o modelo local separa mal: 11/33 na validação em t* = 0,650.
- **Agenda: "H18/H19 + coleta (Recomendado)".** Vira uma missão própria no main do stocks: certificar a base de ações, rodar H18/H19 com os lacres de 04/09 e ligar a coleta prospectiva de VLMO e aluguel. A reabertura formal da Etapa A (C24.4), para levar fator novo ao CAIN, só depois desta reemissão. Nada disso muda esta integração.

| Onde | O quê |
|---|---|
| `runtime_targets.json`, `hosted_ci_targets.json`, `data/SOURCES.json`, `RAW_LOGS/pin/pin_4.log` | Alvos na rc13 e no transporte rc6; pin novo antes do run, com o mesmo painel `8509f54f…` (D-16) |
| `RAW_LOGS/runtime/run36462320273/` e `-windows/` | Run de push em `integration-stocks/runtime-…-rc13` (`8ace5f8`), todas as fases com exit 0: cleanroom-final; C24.3 (d) 11/0; e2e 55/0; N+1 63/0 e integrado 64/0; isolamento 28/0; contradição 9/0; F01–F15; soak 43/0 com 5 propostas de LLM (`qwen2.5:0.5b`, piso 5). Windows: e2e + restart 55/0 |
| `scripts/cycle4_publish.py` | Fase publish-candidates-c4: cain 0.4.13rc13 `960fb25`, transporte 0.1.0rc6 `bac1f7b`, stocks 0.3.0rc3 `6f857b2` |
| `RAW_LOGS/core-identity-c4/`, `RAW_LOGS/final-wheels/final_wheels_check_run36462320273.json` | Identidade do Core 13/0; final_wheels 19/0 |
| `RAW_LOGS/hosted-ci/final-rc13/` | Push verde no SHA exato: cain `960fb25` e ecosystem `bac1f7b`. stocks-predictor pelo aceite do dono (IS-F004/IS-F005 b), reconferido 9/0. Varredura local da árvore: PASS. A 1ª coleta, feita com o CI da tag v0.4.13rc13 ainda rodando, fica em `run1_ci_da_tag_em_andamento/` |
| `RAW_LOGS/contract-revalidation-rc13/` | C24.3 estático 12/0 |
| `RAW_LOGS/protected-c4/` | Conjunto protegido (3387 itens) na branch e num snapshot do main `37a0e28`. Só os 4 itens do IS-F008 mudam, todos encadeados até o sha256 protegido. Os congelados do stocks chegam ao ciclo 1 em 3 saltos (ciclo 3 → ciclo 2 → ciclo 1) |
| `RAW_LOGS/race-c4/`, `FINDINGS.json`, `scripts/cycle4_findings.py` | **IS-F009 → FIXED.** Disputa refeita com as wheels publicadas (`runtime_env.sh` com os alvos deste ciclo): 20/20, exits (0, 6) em todas, 1 experimento e só RESULT em cada, 0 envelopes falsos e 0 exceções. O script confere tudo isso e o transporte instalado antes de mudar o status |
| `RAW_LOGS/secrets-c4/` | 0 achados, com os diffs até os finais do ciclo 4 |
| `RAW_LOGS/c0/c0_preflight_37a0e28.log` | Pré-voo 4.1–4.7 no main `37a0e28`: 0 falhas |
| relatórios, `scripts/render_reports.py`, `scripts/update_gates.py` | Relatórios do ciclo 4 (famílias da D-26 no `DECISION_POLICY_REPORT.md`); gates com as constantes do ciclo 4 e fases com o sufixo `-c4` |
| `QUALIFICATION_ATTESTATION.json`, `QUALIFICATION_ATTESTATION_superseded_9979d19be7fc.json`, `ATTESTATION_PARTIAL_ciclo4-attestation.json` | A attestation do ciclo 2 fica preservada. A nova é **QUALIFIED**, 30/30 gates PASS, P0=P1=P2=0, `supersedes_sha256` = `9979d19b…` |

**C14 nas outras integrações:** a sessão cripto e a sessão Brasileirão foram avisadas da rc13 (wheel, sha256, conteúdo) e refazem as fases delas nas próprias sessões.

## 2026-09-28 — conjunto protegido: cadeia sem limite fixo de saltos (pós-attestation do ciclo 4)

**Pedido do dono** no chat da sessão: **"Resolve"**, sobre a pendência avisada depois do merge do pq#87.
- `scripts/protected_check.py` seguia no máximo 5 saltos de cadeia (`MAX_HOPS = 5`).
- Com a C14 da integration-crypto na rc13 (pq#86), a attestation dela ficou exatamente em 5 saltos até o sha256 protegido.
- A próxima reemissão do cripto faria a conferência do stocks acusar um item legitimamente encadeado.

**O que muda:**
- A cadeia agora segue até uma destas paradas, gravadas no campo `stop`:
  - o sha256 protegido (`protected_sha256`);
  - um documento sem ponteiro (`no_pointer`);
  - um arquivo com bytes diferentes dos do ponteiro (`bytes_differ`) ou ausente (`missing`);
  - um arquivo já visitado (`cycle`).
- Só o sha256 protegido dá ok; as outras paradas continuam FAIL.
- `CHAIN_GUARD = 1000` só impede laço sem fim.
- A regra do IS-F008 ("(a) Encadeada") não muda: salto a salto, com cada arquivo nos bytes que o ponteiro diz.

**Evidência (`RAW_LOGS/protected-chain/`):**
- `selftest.log` (`scripts/protected_chain_selftest.py`), cadeias sintéticas, **6/6**:
  - 7 saltos: ok (com o limite de 5, falhava);
  - attestation com 6 saltos: ok;
  - bytes trocados, arquivo ausente, ciclo e documento sem ponteiro: FAIL, cada um com a parada certa.
- `protected_check_main_875e762.json`, o script novo no main `875e762` (depois dos pq#86 e pq#87), comparado com `protected_check_main_875e762_script_anterior.json`, o script anterior no mesmo main:
  - mesmos 3387 itens, mesmos domínios, mesmos 4 itens encadeados;
  - os mesmos saltos: attestation do cripto 5, congelados do cripto 2, congelados do stocks 3, vetores do stocks 2;
  - todos com parada `protected_sha256`.
- `RAW_LOGS/c0/c0_preflight_875e762.log`: pré-voo 4.1–4.7 com 0 falhas.

**O que não muda:** a attestation do ciclo 4 (`60b75594…`) não cita o script. As evidências dela (`RAW_LOGS/protected-c4/`) ficam como estão.

## 2026-09-30 — ciclo 5 (D-27, C14): cain 0.4.13rc15 e transporte 0.1.0rc7, Linux primário e `windows-latest` verdes; **BLOCKED** no pin do conjunto protegido

Ciclo 5 da `freeze-parameters` (C14, wheel nova do cain e do transporte; stocks 0.3.0rc3 `6f857b2` e cripto 1.2.0rc3 `ee3d3d1` sem mudança;
perfil V1 do soak e vetores congelados sem mudança). Nenhuma release nova publicada por esta missão: a cain v0.4.13rc15 (`ae00017a`) e o
transporte v0.1.0rc7 (`b0da4fd8`) já existiam (sessões do cain e do ecosystem-predictor). Resultado: **29/30 gates `PASS`**, P0 = P1 = 0;
`PROTECTED_ARTIFACTS_UNCHANGED` em `NOT_RUN` (`BLOCKED`): o item compartilhado `qualification/crypto/runtime_target.json` mudou pela reabertura
V1.2 do crypto (D-27), fora desta missão; aceitar o pin novo é decisão do dono (mesmo caminho da IS-F008/IC-F011). Estado C7.3 **BLOCKED**:
só o parcial `ATTESTATION_PARTIAL_ciclo5-attestation-blocked.json` (`IN_PROGRESS`, schema OK); a attestation vigente continua a do ciclo 4
(`QUALIFIED`; `supersedes_sha256` do parcial = `60b75594a229…`).

| Onde | O quê |
|---|---|
| `runtime_targets.json`, `hosted_ci_targets_rc15.json`, `data/SOURCES.json` (+ `SOURCES-c4.json`), `RAW_LOGS/pin/pin_5.log`, `RAW_LOGS/pin/run36648601522/` | Alvos na cain rc15 e no transporte rc7; pin novo dos dados públicos antes do run |
| `RAW_LOGS/runtime/run36649880023/` e `-windows/` | Run de push em `integration-stocks/runtime-…-rc15` (`f696026`): cleanroom-final (suítes pelas wheels publicadas); C24.3 (d) 11/0; e2e 55/0; N+1 crypto-cycle 1/0; n-plus-1 63/0; n-plus-1-integrated 64/0; isolamento/contradição isolation-ids-contradiction 28/0; contradiction 9/0; isolation-crypto-side 0/0; F01–F15 50/0; Windows (`windows-latest`, D-1) E2E + restart 55/0. **Soak 41/1**: só o piso `llm_proposals >= 5` ficou em 4 (IS-F010) |
| `RAW_LOGS/runtime/run36652132817/` | Só a fase `soak`, mesmo perfil V1 e mesmas wheels (branch `integration-stocks/runtime-soak-rc15b`, `db8305f`): **43/0**, `llm_proposals` 5, tolerância zero intacta. Os dois runs ficam em `RAW_LOGS`; nenhum log editado |
| `FINDINGS.json`, `scripts/add_finding_is_f010.py` | **IS-F010 (P2, `ACCEPTED_LIMITATION`)**: o modelo local `qwen2.5:0.5b` (ollama 0.35.0; antes 0.34.4) estourou `num_predict=256` em 2 de 6 tentativas e a CAIN recusou fail-closed (`LLM_PROPOSAL_FAILED`); o laço tem 1 tentativa de folga. Caminho com LLM não é prova (C9); perfil congelado não muda neste ciclo (C15) |
| `RAW_LOGS/core-identity-c5/`, `RAW_LOGS/final-wheels/final_wheels_check_run36649880023.json` | Identidade do Core 13/0; final_wheels 19/0 (assets das releases × instalado no run) |
| `RAW_LOGS/hosted-ci/final-rc15/`, `RAW_LOGS/static-rc15/` | CI de push verde no SHA exato: cain `ae00017a`, ecosystem `b0da4fd8`. stocks-predictor `6f857b2` sem mudança: aceite do dono (IS-F004/IS-F005 b) e varredura da árvore do ciclo 4 (`final-rc13/`) |
| `RAW_LOGS/contract-revalidation-rc15/` | C24.3 estático 12/0 (`static_checks.json`, com o arquivo de aceite do dono para (f)); a primeira rodada, sem esse arquivo, fica em `static_checks_sem_aceite.json` (11/1) |
| `RAW_LOGS/protected-c5/` | Conjunto protegido (3387 itens) na branch e num snapshot do main `7cae574`: 3382 iguais; alterados 5: os 4 do IS-F008 encadeados salto a salto e o pin do crypto (D-27) → `NOT_RUN`/`BLOCKED` |
| `RAW_LOGS/secrets-c5/` | 0 achados nos diffs até os finais do ciclo 5 e nos arquivos da missão; os logs novos dos runs conferidos por padrão de token/chave: nada |
| `scripts/cycle5_gates.py`, `scripts/cycle5_publish.py`, `scripts/update_gates_c5.py`, `scripts/render_reports.py` (arg. 8: run do soak), `GATES.json` | Ledger no ciclo 5 (`freeze-parameters-c5` … `soak-c5`); `cycle4_evidence` preservado |
| relatórios, `EVIDENCE_NUMBERS.json` | Regenerados de `RAW_LOGS` por script (C20); `SOAK_REPORT.md` cita o run do soak refeito |
| `ATTESTATION_PARTIAL_ciclo5-attestation-blocked.json` | `IN_PROGRESS`, 29/30 `PASS`, P0=P1=P2 abertos = 0, validado contra o schema; `domain_attestations` do stocks com revalidação C24.3 `PASS` |

**Falta (só o dono):** decidir o pin de `qualification/crypto/runtime_target.json` no conjunto protegido compartilhado das três integrações
(aceitar a V1.2 do crypto como alvo, ou reabrir o conjunto num novo ciclo); com a decisão registrada em `DECISIONS.json`, o ciclo 5 fecha
com `PROTECTED_ARTIFACTS_UNCHANGED` `PASS` e a attestation é reemitida (`supersedes_sha256` → ciclo 4).

## 2026-10-07 — ciclo 6 (D-34, C14): cain 0.4.13rc16 com o lock por registro (D-32); attestation reemitida **QUALIFIED**

Ciclo 6 da `freeze-parameters` (C14: wheel nova do cain; stocks 0.3.0rc3 `6f857b2`, cripto 1.2.0rc3 `ee3d3d1`, transporte rc7 `b0da4fd8` e
protocolo rc2 sem mudança; perfil V1 do soak e vetores congelados sem mudança). A cain v0.4.13rc16 (`de5db06b`, wheel `d8fca502…`, build
duplo byte-idêntico) tem o código do pacote idêntico ao da rc15; o `uv.lock` passa a fixar as wheels do stack por `STACK_WHEELS.json` +
índice local, sem URL de release (R01/D-32). Os assets do ecosystem passam a ser lidos no repositório renomeado `ecosystem-predictor-cain`.
A D-29 (escrita hoje, delegada pelo dono em 2026-09-30) fecha o que bloqueava o ciclo 5. Resultado: **30/30 gates `PASS`**, P0 = P1 = P2 = 0.

| Onde | O quê |
|---|---|
| `runtime_targets.json` (`cycle = c6`), `hosted_ci_targets_c6.json`, `data/SOURCES.json` (+ `SOURCES-c5.json`), `RAW_LOGS/pin/pin_6.log`, `RAW_LOGS/pin/run37696821981/` | alvos na cain rc16; pin novo dos dados públicos antes do run (workflow `integration-stocks pin`, run 37696821981) |
| `scripts/runtime_env.sh`, `scripts/cleanroom_final.sh`, `scripts/transport_dev_requirements.py`, `scripts/core_identity.py`, `scripts/final_wheels_check.py`, `scripts/secrets_scan.py`, `.github/workflows/integration-stocks-runtime.yml` | lado do CAIN instalado pelo registro (`fetch` + `check` + `requirements` com hash + `--find-links`); requisitos de teste do transporte lidos do lock rc7 por tomllib (o lock fixa o protocolo pela URL aposentada); cadeia de identidade do registro (D-32); download anônimo dos assets; clone do `ecosystem-predictor-cain`; conferências estáticas rotuladas pelo ciclo; token do job para o fetch |
| `RAW_LOGS/runtime/run37698400981/` e `-windows/` | run [37698400981](https://github.com/leonardosovienski/predictor-qualification/actions/runs/37698400981) (push em `integration-stocks/runtime-…-c6`, `2367e3c`), todas as fases exit 0: cleanroom-final (conformidade 87/0, adapters 11/0, transporte 20/0, cain 84/0); C24.3 (d) 11/0; e2e 55/0; N+1 congelado 63/0, integrado 64/0, crypto-cycle 1/0; isolamento 28/0, contradição 9/0; F01–F15 50/0; **soak 43/0** (`llm_proposals` 5, tolerância zero). Windows (`windows-latest`, D-1): E2E + restart 55/0 |
| `RAW_LOGS/core-identity-c6/`, `RAW_LOGS/final-wheels/final_wheels_check_run37698400981.json` | identidade 14/0 (stocks por URL; cain rc16 pelo registro); final_wheels 19/0 (assets × instalado no run; o cripto integrado é o rc3 de `runtime_targets.json`) |
| `RAW_LOGS/static/run37698400981/`, `RAW_LOGS/hosted-ci/final-c6/`, `RAW_LOGS/contract-revalidation-c6/` | CI de push verde no SHA exato: cain `de5db06b`, ecosystem-predictor-cain `b0da4fd8`; stocks-predictor `6f857b2` sem mudança (aceite do dono IS-F004/IS-F005 b, `final-rc13/`); C24.3 estático 12/0 com o arquivo de aceite (a rodada do job, sem ele, em `static_checks_sem_aceite.json`, 11/1) |
| `RAW_LOGS/protected-c6/` | conjunto protegido (3387 itens) na branch e no snapshot `713b89d`: domínios intactos; os 4 itens encadeados do IS-F008 (agora incluindo a attestation rc16 da integration-crypto, encadeada por `supersedes_sha256`); os itens do crypto V1.2 re-congelados pela D-29 (`PROTECTED_SET.json`) |
| `RAW_LOGS/secrets-c6/` | 0 achados nos diffs (cain rc15→rc16; stocks base→final) e nos arquivos da missão |
| `scripts/cycle6_gates.py`, `scripts/cycle6_publish.py`, `scripts/update_gates_c6.py`, `GATES.json`, `EVIDENCE_NUMBERS.json`, relatórios | ledger no ciclo 6 (`freeze-parameters-c6` … `soak-c6`); `cycle5_evidence` preservado; números de `RAW_LOGS` por script (C20) |
| `QUALIFICATION_ATTESTATION_superseded_60b75594a229.json` (ciclo 4, preservada), `ATTESTATION_PARTIAL_ciclo6-attestation.json`, `QUALIFICATION_ATTESTATION.json` | attestation **QUALIFIED** para stocks `6f857b2` / rc3, cain `de5db06b` / rc16, ecosystem-predictor-cain `b0da4fd8` / transporte rc7, cripto `ee3d3d1` / rc3, core 3.2.1, ops 4.2.2rc1; `supersedes_sha256` = ciclo 4 (`60b75594…`); `attest.py check` OK |

Limites (C22): vale para os `final_commits`/`final_wheels` declarados e para os vetores e perfis congelados; não garante edge nem lucro.

## 2026-10-08 — ciclo 7 (C14 refeito): adoção da cain rc16 na lock conjunta do ecosystem; attestation reemitida **QUALIFIED**

Por quê: o `ecosystem-predictor-cain` adotou a cain 0.4.13rc16 na lock conjunta `compat/` e publicou ecosystem `v0.2.2` (`main` `6aeec475`,
PR #56). Pela C14 (mudança no ecosystem-predictor), as fases que o exercitam foram refeitas com as mesmas wheels do ciclo 6 (cain rc16,
transporte rc7, protocolo rc2, stocks rc3, cripto rc3, core, ops); `final_commits`/`final_wheels` não mudam (o commit do ecosystem continua
sendo o da tag do transporte); o `main` do ecosystem entra em `hosted_ci_targets_c7.json` (CI de push verde em `6aeec475`) e em
`GATES.json → cycle.ecosystem_main_commit`. Pin novo dos dados públicos antes do run (run 37703320854, `data/SOURCES.json`; o do ciclo 6 em
`SOURCES-c6.json`). Resultado: **30/30 gates `PASS`**, P0 = P1 = P2 = 0.

| Onde | O quê |
|---|---|
| `RAW_LOGS/runtime/run37704456789/` e `-windows/`, `RAW_LOGS/static/run37704456789/` (cópias em `*-c7/`) | run [37704456789](https://github.com/leonardosovienski/predictor-qualification/actions/runs/37704456789) (push em `integration-stocks/runtime-…-c7`, `c608144`), todas as fases exit 0: cleanroom-final (conformidade 87/0, adapters 11/0, transporte 20/0, cain 84/0); C24.3 (d) 11/0; e2e 55/0; N+1 63/0, integrado 64/0, crypto-cycle 1/0; isolamento 28/0, contradição 9/0; F01–F15 50/0; soak 43/0 (`llm_proposals` 5); Windows E2E + restart 55/0; identidade 14/0; final_wheels 19/0; CI de push verde nos SHAs exatos (cain `de5db06b`, ecosystem-predictor-cain `b0da4fd8` e `6aeec475`; stocks `6f857b2` pelo aceite IS-F004/IS-F005); C24.3 estático 12/0 com o aceite (11/1 sem ele, `static_checks_sem_aceite.json`); protegidos encadeados (agora incluindo as attestations rc16e/c6 por `supersedes_sha256`) na branch e no snapshot; segredos 0 |
| `scripts/cycle7_gates.py`, `scripts/cycle7_publish.py`, `scripts/update_gates_c7.py`, `GATES.json`, `EVIDENCE_NUMBERS.json`, relatórios | ledger no ciclo 7 (`freeze-parameters-c7` … `soak-c7`); `cycle6_evidence` preservado |
| `QUALIFICATION_ATTESTATION_superseded_f70b54cc7cdc.json` (ciclo 6, preservada), `ATTESTATION_PARTIAL_ciclo7-attestation.json`, `QUALIFICATION_ATTESTATION.json` | attestation **QUALIFIED**, mesmos `final_commits`/`final_wheels` do ciclo 6; `supersedes_sha256` = ciclo 6 (`f70b54cc…`); `attest.py check` OK |
