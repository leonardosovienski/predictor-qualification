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
