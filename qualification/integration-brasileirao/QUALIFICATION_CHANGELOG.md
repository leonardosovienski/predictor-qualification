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
