# BR_F018_REQUALIFICATION_REPORT — missão brasileirao (correção do BR-F018 e requalificação C14)

Sessão `brasileirao2`, 2026-09-24, PC 2. Autorização do dono (missão `brasileirao2`): BR-F018 **"Corrigir"**
(gradiente analítico ou reparametrização, rc nova, requalificação) e emenda da D-9 (D-19, no `main`). Toda a saída
bruta está em `RAW_LOGS/c14-rc3-20260924/`; os números abaixo saem dela (C20). O dado real é privado: fica só no
PC 2; a evidência tem logs sem registros do dado, sha256 e resumos numéricos (`scan_final/no_data_rows_check.json`).

## 1. Resumo

| Item | Resultado |
|---|---|
| Causa do BR-F018 | L-BFGS-B com gradiente por diferenças finitas; a `negll` tem ruído de arredondamento na direção da dispersão, o gradiente numérico ficava dominado por ele e o otimizador parava onde o ruído de cada SO mandava |
| Correção (só o método) | gradiente analítico exato da mesma `negll` + polimento por Newton projetado até a raiz do gradiente; modelo, parametrização, bounds, x0, features e hiperparâmetros iguais |
| Tolerâncias | declaradas **antes** de medir: `BR_F018_FIX_PLAN.json` (commit `497715f`, 13:10:38Z) |
| Testes do defeito | no código antigo 2 passam e **3 falham** (`br-f018/stability_tests_OLD_code_e0dab9a.log`); no novo 5/5 |
| CI ubuntu × windows (vetores sintéticos congelados) | run 36006495178: parâmetros máx. |Δ| 7e-15; demais 2740 floats e 2612 discretos idênticos |
| Dado real, 1 ULP nos pesos | máx. 1,1e-16 nos parâmetros (antes 1,6e-2) — `br-f018/fit_sensitivity_NEW_method.json` |
| **Prova entre SOs com dado real** | rc3 Linux PC 2 × rc3 Windows PC 2: **20/20**, 0 diferenças; rc2: **0/20** |
| rc nova | `v0.3.0rc3`, commit `25cdf4d`, wheel `403e6a02…` (build reprodutível 2×) |
| Requalificação (C14) | publish-candidates, cleanroom-final, temporal-suite, e2e, idempotency-failure, windows-smoke, hosted-ci, soak refeitos na rc3; todos os gates `PASS` |
| E2E e SOAK | fechados no Linux primário `owner_linux` (PC 2, D-19) com o dado real: E2E 25/25; soak BR_V1 com tolerância zero ok |

## 2. A correção (brasileirao-predictor PR #80, sobre o #79)

- `brasileirao_predictor/model.py`: a `negll` foi movida sem nenhuma mudança para `_goal_model_objective`, que também
  devolve o gradiente analítico exato (`ψ(k+r) − ψ(r)` como a soma finita `Σ_{j<k} 1/(r+j)`); o L-BFGS-B recebe `jac=`;
  o ponto de parada é polido por Newton projetado até a raiz do gradiente (KKT nos bounds); o fallback Powell ficou igual.
- `tests/test_fit_numerical_stability.py` (API pública, dado sintético com seed): mesma entrada → bit a bit; pesos ×
  (1 + 2⁻⁵²) → parâmetros |Δ| ≤ 1e-6 e probabilidades/lambdas ≤ 1e-9 (com e sem xG).
- `tests/test_fit_objective_gradient.py`: gradiente analítico = diferenças finitas centrais da `negll`; a solução é raiz do
  gradiente; o ótimo novo nunca é pior, na mesma `negll`, que o do método antigo.
- CI: jobs `crossos-fit` (ubuntu-latest, windows-latest) e `crossos-compare` com `tools/crossos_fit_report.py` (refits
  mensais e walk-forward do worker sobre `tests/conformance/fixtures.py`) e `tools/crossos_fit_compare.py`.
- Suíte completa no `827a227` (Linux, Python 3.13.15): 2318 passed, 1 skipped (teste só do Windows), 30 deselected;
  ruff, format e pyright limpos (`br-f018/suite_827a227.log`). O `25cdf4d` só acrescenta `core.longpaths` no job Windows.

## 3. Prova com dado real entre sistemas operacionais (`crossos-real/`, `scripts/compare_real_tolerance.py`)

Critério `cross_os_real_data` do plano: parâmetros |Δ| ≤ 1e-6; demais floats ≤ 1e-9; discretos iguais; 20/20.

| Comparação | Pedidos dentro | Máx. |Δ| parâmetros / floats |
|---|---|---|
| antes: rc2 Windows local PC 1 × rc2 Linux PC 2 | 0/20 | 1,4e-2 / 4,79 |
| antes (mesma máquina): rc2 Windows PC 2 × rc2 Linux PC 2 | 0/20 | 1,4e-2 / 4,79 |
| controle: rc2 Windows PC 2 × rc2 Windows PC 1 | 20/20 | 0 / 0 |
| **depois: rc3 Linux PC 2 × rc3 Windows PC 2** | **20/20** | **0 / 0** |
| determinismo: rc3 Linux (execução só-real) × rc3 Linux (execução do fechamento) | 20/20 | 0 / 0 |

A divergência da rc2 era do sistema operacional (Windows × Windows em máquinas diferentes dá o mesmo), e some na rc3.
Da rc2 para a rc3 nenhum estado mudou nos 20 pedidos; mudam números como `n_bets` (±1 a 4) — `REAL_DATA_METRICS.md`.

## 4. publish-candidates

`scripts/pc2_build_rc.sh` (Linux; o `build_rc.sh` usa caminhos do PC 1): `git archive` do `25cdf4d`,
`SOURCE_DATE_EPOCH=1758240000`, 2 builds: wheel `403e6a02…` e sdist `306d2149…` iguais. Pré-release
https://github.com/leonardosovienski/brasileirao-predictor/releases/tag/v0.3.0rc3 (tag → `25cdf4d`; `digest` dos assets =
build local; `publish-candidates/`). CI verde no `25cdf4d` antes da publicação.

## 5. Requalificação (C14 "código do domínio depois do cleanroom-final")

| Fase | Evidência (`RAW_LOGS/c14-rc3-20260924/`) | Resultado |
|---|---|---|
| cleanroom-final | `cleanroom-final/run36010604163/` (Actions linux e windows-latest), `d16-pc2-rc3/`, `windows-local-rc3/` | conformidade 89/89 nos 4 ambientes; suíte pela wheel 2327 casos com os mesmos 46 da classe T (BR-F017) |
| temporal-suite | `temporal-suite/gate_tests_rc3.json`, `temporal-suite/kickoff_revert_proof_25cdf4d.log`, `temporal-suite/real_corroboration/REAL_CORROBORATION_SUMMARY.json` | todos os gates verdes nos 4 ambientes; revert do `a51a68d` falha e restaurado passa; corroboração real 7/7 |
| e2e | `d16-pc2-rc3/e2e_real/`, `windows-local-rc3/e2e_real/` | E2E real 25/25 (Linux `owner_linux` e Windows local); sintético 26/26 no Actions |
| idempotency-failure | `temporal-suite/gate_tests_rc3.json` | IDEMPOTENCY, RESTART_RECOVERY e FAILURE_INJECTION verdes nos 4 ambientes |
| windows-smoke | `windows-local-rc3/` | Windows local do PC 2 (`C:\QUALIFICACAO\runtime\brasileirao2\`, autorizado pela missão): install com hashes, E2E real 25/25, conformidade 89/89 |
| hosted-ci | `hosted-ci/` | ci.yml run 36006495178 e publication-validation run 36007498283 verdes no `25cdf4d` |
| soak | `d16-pc2-rc3/soak.jsonl` | 71 chamadas, 49/49/49, 0 perdidos, 0 violações, tolerância zero ok (`SOAK_REPORT.md`) |
| protegidos | `c14/protected_check_25cdf4d.json` | 1877/1877 iguais |
| lock | `c14/lock_check_25cdf4d.log` | `uv lock --check` exit 0 |

Contrato: o bloco `implementation` do `DOMAIN_RESEARCH_CONTRACT.json` passa a apontar a rc3 (`25cdf4d`, `403e6a02…`);
nada mais muda (interface, esquemas, allowlist, entrypoint, `adapter_paths`). Como no precedente do stocks (#13), a
aprovação dessa versão do contrato é o merge do PR desta attestation. `FROZEN_VECTORS.json` regravado para o `25cdf4d`:
os 7 arquivos da suíte têm o mesmo blob e sha256; só o campo `commit` muda.

## 6. Ambientes

- **Linux primário `owner_linux`** (D-19): PC 2, Ubuntu 24.04.5 LTS no WSL2, x86_64, Python 3.13.15 gerenciado;
  `host/PROVISION_RECEIPT.json` (recibo do `provision_linux_vm.sh`) e `host/host.log`.
- **Windows secundário `local_windows`**: Windows 10 do mesmo PC 2, uv 0.12.18 e Python 3.13.15 gerenciados em
  `C:\QUALIFICACAO\runtime\brasileirao2\` (sha256 do uv conferido com o `.sha256` publicado e o `digest` do GitHub).

## 7. A-04 (brasileirao-predictor PR #79)

`data/trials.harness_attestation.json` é artefato protegido (`data/trials*.json`); renovar = P0 (C15.1). O teste que pulava
em silêncio passou a avisar (`ExpiredHarnessAttestationWarning`) e continua exercitando o registro com o atestado real no
instante em que era válido. Renovar o atestado continua sendo decisão do dono.

## 8. Erros de método (preservados, não contam)

- `temporal-suite/kickoff_revert_proof_25cdf4d_METHOD_ERROR_full_patch.log`: o diff inteiro do `a51a68d` não aplica mais
  (segundo trecho mudou com o BR-F004); o revert não aconteceu e o teste passou. A prova válida reverte só o trecho de ordenação.
- Os worktrees da sessão nasceram primeiro dentro dos clones compartilhados (caminho relativo com `git -C`); removidos limpos
  e recriados no lugar certo.
