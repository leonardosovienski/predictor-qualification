# integration-brasileirao — QUALIFICATION_CHANGELOG

O que o agente mudou, onde, por quê, commit e PR (C6). Uma sessão do app do Claude no **PC 2** (Ubuntu 24.04 WSL2 =
`owner_linux`, D-19; Windows local do PC 2 = ambiente secundário, D-25 (3)), um único agente, sem subagentes.

## Histórico do C0

| Data | `main` | Estado | Registro |
|---|---|---|---|
| 2026-09-26 | `76a4cbe` | ABORTED | `FINDINGS.json` → `c0` (PR #53) |
| 2026-09-27 | `788b001` | ABORTED (integration-stocks/crypto sem attestation QUALIFIED) | `c0_rechecks[0]` (PR #60) |
| 2026-09-28 | `e63a84c` | ABORTED (integration-stocks NOT_QUALIFIED) | `c0_rechecks[1]` (PR #66) |
| 2026-09-28 | `e78a39f` | **PASSED** | `c0_rechecks[2]`, `RAW_LOGS/c0-20260928-pass/` |

O C0 aprovado substitui operacionalmente, para esta sessão, os registros ABORTED, que continuam como histórico.

## Decisão D-25 (item 5.4 do prompt da sessão)

Primeira mudança depois do pré-voo: `qualification/DECISIONS.json` ganhou a D-25 (decisões do dono 5.1–5.3), sem mudar
outra decisão. Commit `ec9fa66`, PR #68, mergeado (`b246f4e`).

## Fase freeze-parameters

| Arquivo | O quê | Por quê |
|---|---|---|
| `FINDINGS.json` | C0 aprovado em `c0_rechecks`; achados IB-F001 (P2) e IB-F002 (P1, aguardando o dono) | C6; os registros ABORTED preservados (`scripts/findings_init.py` confere com `assert`) |
| `FROZEN_PARAMETERS.json` | base rc3, fontes pinadas, configuração do Brasileirão para a DecisionPolicy, memória herdada, C14 das outras integrações, ambientes, dado, operador, conjunto protegido inicial, gates e fases | C15 (`scripts/freeze_parameters.py`, log `RAW_LOGS/freeze/freeze_parameters.log`) |
| `FAILURE_MATRIX.json` | F01–F16 (F16 = morte no meio do circuito do domínio) | §8 do prompt comum, C10 |
| `QUALIFICATION_PROFILE_INTEGRATION_BR_V1.json` | pisos do soak (8.3), ciclos intercalados pelos runtimes integrados | C10, prompt da sessão 8.3 |
| `FROZEN_VECTORS.json` + `fixtures/` | E2E (dado real, 2021–2024, canário e controle), N+1 (23 candidatas), holdout (3, só receipt), contradição, soak (24) | C15 (`scripts/build_vectors.py`) |
| `RAW_LOGS/freeze/hypothesis_sources_pin_check.log` | 22/22 fontes iguais entre `e540f97` e `25cdf4d` | D-25 (2) (`scripts/hypothesis_sources_pin_check.py`) |
| `GATES.json`, `scripts/attest.py`, `tools/` | ledger dos gates, gerador/conferidor das attestations, ferramentas da missão (`uv sync --locked`) | C7, C8 |
| `.gitattributes` (raiz) | `RAW_LOGS/**` e `E2E_EVIDENCE/**` desta missão com `-text` | C20: log bruto preservado byte a byte (mesmo padrão das outras missões) |

## Fases baseline, truth-map e cleanroom-baseline

| Arquivo | O quê | Por quê |
|---|---|---|
| `STACK_BASELINE.json` (`scripts/mission_baseline.py`) | coleta pelo coletor compartilhado `collect_stack_baseline_v2.py` (sem mudança) com cain `deccaaa` e ecosystem `1304b20`; igual ao STACK_BASELINE_V2.0 fora esses dois; base do Brasileirão `25cdf4d` | C3 (gate STACK_BASELINE_FROZEN) |
| `PROTECTED_SET.json`, `ARCHITECTURE_TRUTH_MAP.json` (`scripts/truth_map.py`) | conjuntos da Etapa A íntegros nas bases (cripto 1387, stocks 89, brasileirao 1884 itens; 0 problemas); dado privado com sha256 igual; componentes da Etapa B; loop do PR #50 fora dos console scripts | C15.1, C2 |
| `RAW_LOGS/cleanroom-baseline/` (`scripts/cleanroom_baseline.sh`) | diagnóstico: conformidade 89 passed contra a rc3 instalada; transporte 0.1.0rc4 e cain 0.4.13rc7 ainda sem o Brasileirão | C5 |
| `FINDINGS.json` | IB-F003 (P2): regex numérica do `no_data_rows_check` sem agrupamento acusa substring (falso positivo num hash de blob); verificador não alterado; causa corrigida nos artefatos (conjuntos dos outros domínios por referência; log bruto do coletor no diretório privado, sha256 registrado) | prompt da sessão 6 e 15 |

## Fases envelope-v2, domain-adapter, cain-wiring-decision-policy, publish-candidates, cleanroom-final, contract-revalidation, e2e e n-plus-1

Runtime no **PC 2** (owner_linux, Ubuntu 24.04 WSL2), run `run-20260928T034216Z-br`; saídas públicas em `RAW_LOGS/runtime/run-20260928T034216Z-br/`, estado e
conteúdo por jogo só no diretório privado `~/predictors/runtime/integration-brasileirao/priv/run-20260928T034216Z-br/`.

| Repositório | Mudança | Commit | PR / release |
|---|---|---|---|
| brasileirao-predictor | `brasileirao_predictor/adapters/research_v2.py` (novo) + versão 0.3.0rc4 (C24.3 a) | `1fc2e88` | brasileirao-predictor#81; release `v0.3.0rc4` (wheel `1874e22f…`, sdist `410d0917…`) |
| ecosystem-predictor | entrada `brasileirao` na allowlist do transporte, testes, README, versão 0.1.0rc5 | `b11494a` | ecosystem-predictor#33; release `predictor-research-transport-v0.1.0rc5` (wheel `408d73c2…`) |
| cain | `data/brasileirao.json`, `tools/build_domain_config.py` (entrada brasileirao; crypto/stocks regenerados iguais), teste novo, 2 testes para domínio fora do registro, transporte rc5, versão 0.4.13rc9 | `4b2f556`, `3e515fd` | cain#63 (CONFLICTING com o main: pendência do dono); release `v0.4.13rc9` (wheel `6e0d31a1…`) |

| Arquivo (predictor-qualification) | O quê |
|---|---|
| `scripts/envelope_v2_check.py`, `RAW_LOGS/envelope-v2/` | protocolo congelado 20/20 |
| `scripts/adapter_smoke.py`, `RAW_LOGS/domain-adapter/`, `RAW_LOGS/cain-wiring-decision-policy/` | diagnósticos locais (não são prova) |
| `scripts/publish_rc.sh`, `release-notes/`, `RAW_LOGS/publish-candidates/` | três pré-releases, build reprodutível, download anônimo conferido |
| `runtime_targets.json`, `scripts/runtime_env.sh`, `scripts/operator_env.py` | runtime suportado do PC 2 e operador privado (dataset real + canário) |
| `scripts/cleanroom_final.sh` | conformidade 89, transporte 15, cain 70, contra as wheels publicadas |
| `scripts/contract_revalidation.py`, `scripts/contract_d.py` | C24.3: (a)(b)(c)(d)(e) verdes; (f) IB-F005 |
| `scripts/harness.py`, `scripts/run_scenario.sh`, `scripts/e2e.py`, `scripts/n_plus_1.py` | E2E real 79/79; N+1 78/81 (as 3 falhas são o holdout, IB-F002) |
| `FINDINGS.json` | IB-F004 (inbox do CAIN com o ResultV2 bruto) e IB-F005 (CI do domínio × regra 10.3), ambos aguardando o dono |

## Ciclo 2 da freeze-parameters (decisão do dono, 2026-09-28)

Decisão no chat desta sessão (pergunta com opções, "Trocar para a rc8"): a base do cain passa de `deccaaa`
(rc7/rc9, política v1) para a release única **cain v0.4.13rc8**, que junta a política v2 (#59), o #62, a configuração
do Brasileirão (#64 e o PR que materializa os lacres) e a regra genérica **R16 REQUIRE_HUMAN SEALED_SCOPE** (#65, escrita
pela sessão cripto e revisada aqui). Pela C14 ("Parâmetro/vetor/perfil congelado"), a fase inteira é um novo ciclo, e as
fases a partir do cleanroom-final são refeitas na rc8.

| Arquivo | Mudança |
|---|---|
| `FROZEN_PARAMETERS.json` | `brasileirao_config.sealed_scopes` em formato de máquina (season 2025/2026; janela em 2025; fixtures em 2025, opcional); política v2 com `rule_order` (R16 depois da R05); ciclo 2 e decisão do dono; cada sessão requalifica a sua integração na rc8 |
| `FROZEN_VECTORS.json` | plano do holdout com `expected_reason: SEALED_SCOPE` (as 60 fixtures com os mesmos bytes) |
| `QUALIFICATION_PROFILE_INTEGRATION_BR_V1.json` | definição de proposta de LLM (a rc8 inclui o #62) e menção à release rc8 |
| `*_cycle1_<sha12>.json` | os três arquivos do ciclo 1 preservados byte a byte |
| `GATES.json` | ciclo 2; o CLEANROOM_FINAL do ciclo 1 (rc9) guardado em `cycle1_evidence` e o gate volta a NOT_RUN até a rc8 |

Diagnóstico com o código da R16 (cain#65, `1e49bd0`): os três lacres passam na validação da configuração e as três
propostas de holdout congeladas dão REQUIRE_HUMAN SEALED_SCOPE (R16); os controles continuam ALLOW (R14).

## Ciclo 3 da freeze-parameters (release única publicada como cain v0.4.13rc10)

A release única da decisão do dono ("rc8" nos textos) foi publicada pela sessão cripto como **cain v0.4.13rc10**
(tag → `fb0e1dc`, wheel sha256 `752de98d3855…`), já que a v0.4.13rc9 existia (pré-release desta missão, política
v1). Ela leva também os PRs da sessão STOCKS: cain#67 (tipo de pedido por hipótese: R04 e molde do LLM), cain#68
(**R17 DUPLICATE EQUIVALENT_REQUEST**: o mesmo pedido sem request_id, hypothesis_id, research_id e client_ref, já rodado
ou pendente, não gera task; avaliada antes da R12) e cain#69 (justificativa do LLM conferida). Todos foram mergeados pelo
dono, junto com o cain#66 (lacres do Brasileirão).

| Arquivo | Mudança |
|---|---|
| `FROZEN_PARAMETERS.json` | `rule_order` com a R17 entre R11 e R12 e a R04 por hipótese; framework e ciclo 3; `brasileirao_config` sem mudança |
| `FROZEN_VECTORS.json` | `n1/01-next` e `contradiction/02-refuted` passam ao alvo OU25 (eram o mesmo experimento da semente e do 01-supported e esperavam ALLOW); tasks e resultados da contradição reencadeados; vetor novo `n1/24-equivalent-request` (DUPLICATE EQUIVALENT_REQUEST) |
| `*_cycle2_<sha12>.json` | os arquivos do ciclo 2 preservados byte a byte |
| `runtime_targets.json` | cain → v0.4.13rc10 |
| `GATES.json`, `FINDINGS.json` | ciclo 3; IB-F001 FIXED; IB-F002 com a release publicada |

Conferência mecânica (`scripts/cycle3_check.py`, 13/0): o `brasileirao_config` é igual ao de `417024e`; só mudaram
`rule_order`, framework, ciclo e os ponteiros para os vetores novos; os vetores mudaram só onde foi declarado; o
`brasileirao.json` da wheel publicada é, byte a byte, o que o `tools/build_domain_config.py` do commit da release gera a
partir de `417024e`. Nenhum limiar, holdout, critério ou waiver muda.

## Ciclo 4 da freeze-parameters (decisão do dono: uma hipótese por ciclo do soak)

No diagnóstico privado do soak na rc10 (não é evidência), as 3 hipóteses de qualificação em rodízio por 24 experimentos
diferentes receberam SUPPORTED contra climatologia e REFUTED contra mercado na mesma hipótese. A R10
CONTRADICTION_UNRESOLVED parou corretamente essas hipóteses, e o soak ficou em 16 ciclos (piso 20) (IB-F007). Decisão do
dono no chat desta sessão, 2026-09-28: "1 hipótese por ciclo".

| Arquivo | Mudança |
|---|---|
| `FROZEN_PARAMETERS.json` | `brasileirao_config.proposable_hypotheses` e `operator_env.hypotheses` + `brasileirao:QUAL-SOAK-001..024`; ciclo 4 |
| `FROZEN_VECTORS.json` | `soak_generator`: uma hipótese por ciclo (o mesmo calendário de 24 experimentos) |
| `QUALIFICATION_PROFILE_INTEGRATION_BR_V1.json` | só `plan.cycles` e o bloco `cycle`; pisos e critérios iguais |
| `*_cycle3_<sha12>.json`, perfil `*_cycle2_<sha12>.json` | preservados byte a byte |
| `scripts/operator_env.py` | a policy do operador admite as 24 hipóteses |

O mesmo diagnóstico achou o IB-F006: na rc10, o modo de proposta do LLM quebra para o Brasileirão (`KeyError
'parameters'` em `llm.py:204`, o pedido do Brasileirão não tem parameters). A correção é da sessão STOCKS e entra na
rc11 junto com o brasileirao.json deste ciclo. Conferência mecânica: `scripts/freeze_cycle4.py check`.

## Fases de runtime na cain v0.4.13rc12 (run `run-20260928T145525Z-br12`, PC 2)

A release que as três integrações usam é a **cain v0.4.13rc12** (tag → `302a5c8`, adotada por
`scripts/adopt_release.py`, 7/7). As rc10 e rc11 foram adotadas antes e trocadas pela C14: a rc11 levou o brasileirao.json
do ciclo 4 e a correção do LLM (cain#72, IB-F006); a rc12, o contexto do LLM dentro do orçamento (cain#75). O
cleanroom-final da rc11 (`run-20260928T142258Z-br11`) ficou como registro. Configurações da rc12 iguais às da rc11.

| Fase | Resultado |
|---|---|
| cleanroom-final | conformidade 89, transporte 15, cain 90 testes, 0 falhas |
| contract-revalidation | estática 10/10 ((f) pelo IB-F005, conferido por `ib_f005_acceptance.py`); (d) 11/11 |
| e2e | 79/79 |
| n-plus-1 | congelado 84/84, integrado 85/85; holdout 2025 → REQUIRE_HUMAN SEALED_SCOPE (IB-F002 FIXED) |
| isolation-ids-contradiction | 30/30; contradição 9/9 |
| idempotency-failure | F01–F16: 65 conferências, 0 falhas |
| windows-smoke (PC 2) | E2E 79/79; dado real devolvido ao WSL: 141 arquivos conferidos |
| soak | 61/62: todos os pisos, menos o de LLM (IB-F009, waiver do dono) |

Decisões do dono neste trecho (chat da sessão, perguntas com opções):
- "Cadeia preservada (Recommended)": PROTECTED_ARTIFACTS_UNCHANGED com a regra da cadeia preservada (IB-F008).
- "Waiver do piso de LLM (Recommended)": o piso de ≥ 5 propostas de LLM dispensado só para o Brasileirão (IB-F009). O
  dono decidiu depois de saber que a alternativa (rc13 com sobreposição de campos do pedido) obrigaria o cripto e o stocks,
  já QUALIFIED na rc12, a refazer as fases.

Registro no Windows do PC 2: o console da primeira execução do `windows_smoke.ps1` foi gravado em `%TEMP%`, fora da pasta
autorizada. Só havia mensagens do script e o resumo do E2E, sem linha do dado. O arquivo foi movido para o diretório privado
do runtime no WSL (sha256 conferido) e removido do `%TEMP%`. A pasta `C:\QUALIFICACAO\runtime\integration-brasileirao\`
ficou sem nenhum banco do dado real fora de tools/venv.

## Reemissão na cain v0.4.13rc13 + transporte 0.1.0rc6 (C14; run `run-20260928T183300Z-br13`, PC 2)

O cain (rodadas de utilidade do stocks: cain#77, D-26) e o transporte (um consumidor por domínio: ecosystem-predictor#36)
mudaram, e a C14 manda refazer as fases que os exercitam. Alvos adotados por `scripts/adopt_release.py` (7/7): cain
v0.4.13rc13 `960fb25` (a1d94fd5…) e transporte v0.1.0rc6 `bac1f7b` (6c7e83c4…), pinado pelo uv.lock da rc13. O
brasileirao.json e o policy.py são byte a byte os da rc12.

| Fase | Resultado |
|---|---|
| cleanroom-final | conformidade 89, transporte 19, cain 95 testes, 0 falhas |
| contract-revalidation | estática 10/10 ((f) pelo IB-F005); (d) 11/11 |
| e2e | 79/79 |
| n-plus-1 | congelado 84/84, integrado 85/85; holdout 2025 → REQUIRE_HUMAN SEALED_SCOPE |
| isolation-ids-contradiction | 30/30; contradição 9/9 |
| idempotency-failure | F01–F16: 65 conferências, 0 falhas |
| windows-smoke (PC 2) | E2E 79/79; dado real devolvido ao WSL: 142 arquivos conferidos |
| soak | 61/62: todos os pisos, menos o de LLM (IB-F009, waiver do dono, mantido) |

Registro: um run anterior na mesma pilha (`run-20260928T180538Z-br13`) deu os mesmos resultados, mas o no_data_rows_check acusou o
falso positivo IB-F003 no `real_env.policy.sha256` do operador daquele run (7 dígitos dentro do hex de 64). O run saiu do
RAW_LOGS (privado, SUMMARY do E2E sha256 `978881495657…`); este run tem operador novo e saída limpa. O checker
não foi alterado. A attestation da rc12 fica preservada em `QUALIFICATION_ATTESTATION_superseded_<sha12>.json`, e a nova
aponta para ela por `supersedes_sha256`.

## 2026-09-30 — C14 na cain v0.4.13rc15 + transporte v0.1.0rc7 (D-27): só conferências estáticas; runtime BLOCKED (PC 2)

As correções de 2026-09-29 foram publicadas como cain v0.4.13rc15 (`ae00017a`, wheel `ff642b72…`) e transporte v0.1.0rc7 (`b0da4fd8`,
wheel `d3dfbff4…`). A C14 manda refazer as fases desta missão que os exercitam. Esta sessão (Linux na nuvem, sem o PC 2) fez o que não
depende do runtime privado; o resto fica para o dono no PC 2 (owner_linux + Windows, D-19/D-25).

| Onde | O quê |
|---|---|
| `runtime_targets.json` (`adopt_release.py record`) | cain rc15 `ae00017a` e transporte rc7 `b0da4fd8`; brasileirao rc4, protocolo rc2, cripto rc3 e stocks rc3 inalterados |
| `RAW_LOGS/release-rc15/` | `adopt_release.py check` 7/7: wheel = asset; `brasileirao.json` da rc15 pina `FROZEN_PARAMETERS.json` em `0920d903` e é byte a byte o que `tools/build_domain_config.py` de `ae00017a` regenera (`f51ac735…`, igual ao da rc13); 3 sealed_scopes; QUAL-SOAK-001..024; `policy.py` difere da rc13 só por uma anotação de tipo (`release_rc15.log`) |
| `RAW_LOGS/hosted-ci/final-rc15/`, `hosted_ci_final_targets_rc15.json` | push verde nos SHAs exatos (cain, ecosystem; brasileirao pelo caminho da IB-F005); API pública via `qualification/shared/scripts/gh_shim.py` |
| `RAW_LOGS/contract-revalidation-rc15/` | C24.3 estático 9/10 ((f) pelo aceite IB-F005, como na rc13); (c)/(d) exigem runtime |
| `RAW_LOGS/protected-rc15/` | 3397 itens; domínios intactos; itens compartilhados encadeados exceto `qualification/crypto/runtime_target.json`, mudado pela reabertura V1.2 do crypto (D-27) |
| `RAW_LOGS/secrets-rc15/` | 0 achados |
| `scripts/rc15_static.py`, `GATES.json`, `ATTESTATION_PARTIAL_rc15-static.json` | ledger do ciclo: HOSTED_CI, SECRETS_CLEAN, SHARED_DEPENDENCY_CLEAR e BLOCKERS_ZERO PASS; os demais NOT_RUN com `BLOCKED: …`; `supersedes_sha256` = attestation rc13 vigente, que **continua vigente** |

**Estado terminal desta sessão: `BLOCKED`** (C7.3; só parcial). Falta o dono, no PC 2: `runtime_env.sh` + cenários (cleanroom-final, C24.3 c/d, e2e,
N+1, isolamento, F01–F16, soak) e `windows_smoke.ps1` com os alvos rc15; depois `attest.py final` (supersede da rc13). Também pendente a decisão sobre
o pin do crypto no conjunto protegido (mesma decisão pedida na integration-crypto).
