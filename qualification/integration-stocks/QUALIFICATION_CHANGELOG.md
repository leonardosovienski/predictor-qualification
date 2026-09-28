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
