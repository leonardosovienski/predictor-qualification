# QUALIFICATION_CHANGELOG — missão brasileirao (Etapa A)

O que a missão mudou, onde, por quê, com commit e PR. `core-predictor` e `predictor-ops` **não**
foram alterados (congelados; o Ops 4.2.2rc1 vem da D-17, feita na missão crypto).

## brasileirao-predictor (branch `qualification/brasileirao-stage-a`; PRs #77 e #78)

| Commit | O quê | Por quê | Teste que prova |
|---|---|---|---|
| `5344b5f` | pins do Ops 4.2.1 → **4.2.2rc1** (pyproject `>=4.2.2rc1,<5`, `tool.uv.sources`, `uv.lock`, `constraints/shared-wheels.sha256`, `ci.yml`, `publication-validation.yml`, Dockerfiles) | **BR-F003** (SHARED-005 bloqueante na 4.2.1; D-17) | `test_core_integrity`, `test_shared_dependencies` exigem 4.2.2rc1; suíte Windows 2207/2207 + 1 skip; CI verde |
| `abd232e` | `brasileirao_predictor/pit.py` (regra única: resultado disponível em kickoff + 180 min); `evaluator.py`, `serving_evaluator.py` (serving e H9), `elo_baseline.py` e `backtest_walkforward.py` cortam por disponibilidade, não por kickoff/data | **BR-F004 (P0)**: jogo em andamento entrava no ajuste com o placar final (dado real: 2/20 refits na cadência do benchmark) | `tests/test_result_availability_guard.py` e `tests/test_walkforward_result_availability.py`: falham antes (`RAW_LOGS/contract-admission/BR-F004/repro_*`), passam depois |
| `abd232e` | fixtures de 3 testes antigos de "kickoffs distintos" passam de 2 h para 4 h de intervalo | com a regra PIT, 2 h não garantem resultado existente; a intenção (sem pedágio quando o resultado existe) ficou | os próprios testes |
| `8479ecf` | `_ht_fraction` aceita corte por data (00:00Z) | a suíte completa de `abd232e` mostrou `test_ht_fraction_forward_only` chamando com datas | `test_brasileirao_domain.py` |
| `39efa52` | `brasileirao_predictor/research_runtime/` (contrato, admission, execução via Ops CLI, worker, resultados, recuperação, faults) + `[project.scripts] brasileirao-research` | **BR-F012**: não existia circuito de pesquisa | `tests/conformance/` (89 casos) |
| `39efa52` | lock exclusivo por experimento | **BR-F014**: concorrência na materialização, pega pelo teste de concorrência na 1ª execução | `test_concurrent_submissions_of_the_same_request_produce_one_effect` |
| `39efa52` | `brasileirao_predictor/adapters/` reservado (vazio) | C24.1 `adapter_paths` | `test_import_closure.py` |
| `39efa52` | plugin reporta a versão instalada; versão 0.3.0rc1 | **BR-F011** | `tests/test_ecosystem_plugin_version.py` |
| `d3d8a8c` | teste de corrupção conta só diretórios de experimento | o `.lock` do experimento é arquivo (CI de `39efa52`) | CI verde |
| `cff7a3a` | O/U 2.5 de fechamento lido de `odds_lines` | **BR-F015**: colunas flat vazias no dado real; OU25 inteiro virava INCONCLUSIVE_DATA_QUALITY | `test_ou25_is_evaluated_against_the_canonical_closing_line` falha antes e passa depois (`RAW_LOGS/windows-smoke/BR-F015_*`) |
| `cff7a3a` | testes fecham as conexões SQLite (`contextlib.closing`) | windows-latest: limpeza do laboratório falhava (WinError 32) | conformidade 89/89 no windows-latest |
| `04b42c9` | versão 0.3.0rc2 | release nova, nunca sobrescrever | — |

**final_commit:** `04b42c9245e6ec75d72ec6a27d151ee2afef5e70`. Release pré-release
[`v0.3.0rc2`](https://github.com/leonardosovienski/brasileirao-predictor/releases/tag/v0.3.0rc2),
wheel `70344f2264e99c41808e90db26bdc94369504e3b45d125c77e01aebe71ad7b1a` (build reprodutível).
A `v0.3.0rc1` (`d3d8a8c`, `ebea7722…`) ficou publicada, sem a correção BR-F015; não é final_wheel.

O dono mesclou o #77 em `cff7a3a` (merge `f07dea4`) enquanto a missão seguia; o #78 leva a troca de
versão (`04b42c9`) para o main, para versão do main = wheel publicada.

## predictor-qualification (evidência; branch `brasileirao/stage-a`)

- `qualification/brasileirao/**` (artefatos C16 + scripts versionados).
- `.gitattributes`: `qualification/brasileirao/RAW_LOGS/**` e `E2E_EVIDENCE/**` com `-text` (C20).
- `.github/workflows/brasileirao-runtime.yml`: runtime suportado no Linux primário e windows-latest.
- Nenhuma mudança em `SHARED_ISSUES.json` nem `DECISIONS.json`.

## Erros de método (preservados, não contam)

- `RAW_LOGS/windows-smoke/install_METHOD_ERROR_ensurepip.log`: `ensurepip -q` inválido (o mesmo tropeço do crypto); refeito com `uv pip`.
- `RAW_LOGS/contract-admission/windows_suite_39efa52_INTERRUPTED.log`: interrompida por mim ao ver no CI que 4 testes contavam o `.lock` como experimento.
- `RAW_LOGS/temporal-suite/kickoff_revert_proof_METHOD_ERROR_patch_not_applied.log`: o patch inteiro do `a51a68d` não aplicava mais (contexto mudado pelo BR-F004); a prova válida reverte só o hunk de ordenação.
- `RAW_LOGS/publish-candidates/build_rc_cff7a3a_METHOD_ERROR_version_not_bumped.log`: build com a versão ainda 0.3.0rc1; nada publicado.
- `RAW_LOGS/contract-admission/windows_suite_cff7a3a.log`: 1 teste perdido para o Modern Standby do host (BR-F016); o mesmo teste passa 3/3 sozinho.
- Primeira execução da conformidade no Windows (`conformance_windows_first_run_tail.log`): o pipe guardou só o fim da saída; os detalhes foram reproduzidos teste a teste.
- `RAW_LOGS/secrets/scan_evidence_and_br_diff.json`: a primeira varredura (251 arquivos, o mesmo único alerta revisado) foi sobrescrita por mim por uma segunda (298 arquivos, depois dos relatórios novos) antes do commit. Os parciais `contract-admission` a `soak` citam o sha256 da primeira e por isso não conferem (C7.1 regra 3) nesse item; não foram reescritos (C8). A attestation cita a varredura final, gravada em arquivo novo.

## Noite D-16 no PC 2 (2026-09-24; branch `brasileirao/d16-20260924`)

Nenhuma mudança no brasileirao-predictor, no core-predictor nem no predictor-ops (alvo congelado `04b42c9`
/ 0.3.0rc2 intacto). Só o repositório de evidência mudou:

| O quê | Por quê |
|---|---|
| `scripts/soak.py`: modo `--real-dataset/--real-dataset-sha256/--real-as-of` | o `SOAK_REPORT.md` mandava rodar o perfil com o dado real "sem mudar perfil nem vetores", mas o driver só aceitava o dataset sintético. O modo real mantém perfil, classes de falha, seeds, canário, comparadores, política e objetos JSON; troca só o dataset (cópia real + variantes derivadas; pares reais de mesmo kickoff). Caminho sintético inalterado |
| `scripts/pc2_d16_runtime.sh` (novo) | análogo Linux do `windows_runtime.sh`/`runtime_cleanroom.sh` para o PC 2: dado copiado e conferido, runtime só com as final wheels, conformidade, `real_env.py`, E2E real, soak real, separação evidência × privado, números e varreduras |
| `scripts/pc2_export.py` (novo) | tira do diretório privado só o que não carrega registros do dado; sha256 do resto |
| `scripts/no_data_rows_check.py` (novo) | prova que a evidência não tem linhas do dado (D-11/D-16): marcadores da cópia em `ro&immutable`, saída só com contagens |
| `scripts/pc2_suite.sh` (novo) | suíte completa no PC 2 (método do `ci.yml`, como o `win_suite.sh`) |
| `scripts/stage_a_recheck.py` (novo) | reconferência independente da Etapa A (evidências × último parcial, hashes, vetores, lock, wheels) |
| `scripts/compare_real_metrics.py`, `scripts/fit_sensitivity.py` (novos) | comparação Windows × Linux do dado real e diagnóstico da causa (BR-F018) |
| `RAW_LOGS/d16-pc2-20260924/**` | saída bruta sem dado (C20; `-text` pelo `.gitattributes`) |
| `FINDINGS.json`: BR-F018 (P1, aberto) | o número de um resultado depende do SO |
| `GATES.json`: `BLOCKERS_ZERO` → `FAIL` (BR-F018); `E2E`/`SOAK` continuam `NOT_RUN` com a nota da D-16 e a evidência do PC 2 | |
| `SOAK_REPORT.md`, `REAL_DATA_METRICS.md`, `D16_PC2_REPORT.md` (novo) | números do PC 2 (de `evidence_numbers_pc2.json`), BR-F018 e a emenda proposta da D-9/schema |
| `ATTESTATION_PARTIAL_d16-pc2.json` (novo) | checkpoint (C8) com o estado depois da noite; nenhum parcial anterior reescrito |

Regressão do `soak.py` no Actions: run 35980611463 (`279f3a6`) `success`; soak sintético idêntico ao da Etapa A
(`RAW_LOGS/d16-pc2-20260924/actions-run35980611463/soak_regression.json`).

Erros de método da noite: ver `D16_PC2_REPORT.md` §3.

## Correção do BR-F018 e requalificação C14 (2026-09-24, sessão `brasileirao2`)

### brasileirao-predictor

| Commit | O quê | Por quê | Prova |
|---|---|---|---|
| `e0dab9a` (PR #79) | teste do pré-registro avisa (`ExpiredHarnessAttestationWarning`) em vez de pular com o atestado expirado | A-04; renovar o atestado altera artefato protegido | antes SKIPPED, depois PASSED + aviso |
| `13c24c0` (PR #80) | `fit_goal_model`: gradiente analítico exato + raiz polida (Newton projetado) | **BR-F018** | testes novos falham no código antigo (3/5) e passam no novo; dado real entre SOs 20/20 |
| `ed373c2`, `25cdf4d` | CI: jobs cross-OS ubuntu × windows; `core.longpaths` no Windows | exigência da missão; checkout falhava no Windows | run 36006495178 verde |
| `827a227` | versão 0.3.0rc3 | release nova, nunca sobrescrever | — |

**final_commit:** `25cdf4d9bb309d33f066fbc6a379f5d98c69f08a`. Pré-release `v0.3.0rc3`, wheel `403e6a022b10e2b6d05ef1828894bf3ad0b1d049301e3dfce9cf79dc262000ea`
(build reprodutível no Linux do PC 2). A `v0.3.0rc2` continua publicada; deixa de ser final_wheel.

### predictor-qualification

- `scripts/attest.py` no núcleo v2.2 + CR-F021 (PR #38); `MANIFEST.sha256` dos prompts (PR #35).
- Scripts novos: `pc2_build_rc.sh`, `pc2_windows_runtime.sh`, `pc2_kickoff_revert_proof.sh`, `compare_real_tolerance.py`,
  `corroboration_summary.py`; `pc2_d16_runtime.sh` (`BRQ_RUNTIME`, `BRQ_ONLY_REAL`) e `pc2_export.py` (E2E opcional).
- `BR_F018_FIX_PLAN.json` (tolerâncias declaradas antes de medir, `497715f`), `runtime_target.json` → rc3,
  `FROZEN_VECTORS.json` regravado no `25cdf4d` (mesmos arquivos), contrato: bloco `implementation` → rc3.
- `RAW_LOGS/c14-rc3-20260924/**`, `EVIDENCE_NUMBERS.json` (chaves `*_rc3`), `FINDINGS.json` (BR-F018 `FIXED`), `GATES.json`,
  relatórios (bloco "Requalificação rc3"), `SOAK_REPORT.md`, `REAL_DATA_METRICS.md`, `BR_F018_REQUALIFICATION_REPORT.md`,
  parciais `c14-*` e `QUALIFICATION_ATTESTATION.json`.

Erros de método: ver `BR_F018_REQUALIFICATION_REPORT.md` §8.
