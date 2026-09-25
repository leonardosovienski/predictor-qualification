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
- `c14/method_error_contract_sha/QUALIFICATION_ATTESTATION_METHOD_ERROR_contract_sha.json` (15:46:01Z): a primeira attestation
  final saiu com o `domain_contract_sha256` do contrato anterior (`e6f98ca2…`; o `attest.py` copiava o valor do `GATES.json`),
  não com o do contrato que foi para o `main` com ela (`1c75fc45…`). A reconferência independente (`stage_a_recheck.py`)
  acusou antes do commit; a attestation válida foi gerada de novo (15:47:18Z) e o `attest.py` passou a conferir a C7.1(7)
  (teste `test_final_attestation_checks_the_contract_sha256`).

## 9. Revisão final (2026-09-24, depois do merge; diagnóstico, não muda gate)

Saída bruta em `RAW_LOGS/c14-rc3-20260924/review-final/`, pelos scripts versionados `scripts/strict_audit.py` e
`scripts/optimum_check.py`, no runtime da wheel rc3 do PC 2 e com a cópia do dado (sha256 `31f30a4d…` antes e depois).

- **Comparação exata, sem tolerância** (`strict_audit_rc3.log`): rc3 Linux PC 2 × rc3 Windows PC 2, o resultado `show`
  inteiro dos 20 pedidos: nenhum número não finito (NaN/inf) nos dois lados; os 24 campos que diferem são só IDs, instantes e
  hashes de execução (`result_id`, `admission_id`, `ops_facts/*_at`, `effect_sha256`, `identity`, `references`,
  `provenance/*`...); todo o conteúdo de domínio é bit a bit igual. Os mesmos 24 campos diferem entre duas execuções rc3 no
  mesmo Linux. Isso cobre também uma lacuna latente do `compare_real_tolerance.py`: ele trataria NaN de um lado contra número
  do outro como igual; não há NaN, então o 20/20 não depende disso. O comparador fica como está (é evidência atestada).
- **O ótimo novo nunca é pior** (`optimum_check_real.json`): nos 62 refits mensais reais (2021-05 a 2026-09), na mesma `negll`,
  o método da rc3 chega a um valor **menor** que o da rc2 em 62/62 (diferença de −3,7e-6 a −0,17; nenhum igual ou pior). No
  ponto final da rc3 o gradiente projetado é ≤ 7,7e-14; no da rc2, mediana 1,17 e máximo 15,2: o L-BFGS-B com diferenças
  finitas parava longe da raiz do gradiente, e era aí que o ruído de cada SO decidia o ponto de parada (máx. |Δθ| entre os
  dois pontos: 2,94).
- Os parciais `c14-*` foram gravados em sequência entre 15:43:13Z e 15:45:38Z, depois de as fases rodarem: cada
  um tem o estado do ledger depois da fase dele (E2E, depois SOAK, e por último `BLOCKERS_ZERO` em `PASS`), mas o
  `generated_at` é o da gravação, não o do fim da fase.
- Fora do caminho qualificado: `xg_model.py`, `dixon_coles.py` (usado pelo `evaluator.py`) e `event_models.py` também usam
  L-BFGS-B sem gradiente analítico. O worker de pesquisa (entrypoint do contrato) usa só `model.fit_goal_model`, corrigido e
  provado acima; o `QUALIFIED` não cobre esses módulos (C22). A pista foi investigada depois e virou o **BR-F019 (P2)**:
  ver §11.

## 10. Attestation reemitida (2026-09-24T20:54:38Z; C7.1(8))

A conferência dos `.md` achou três problemas em relatórios citados pela attestation. No `SOAK_REPORT.md`, um número
não batia com a fonte citada (81 em vez de 82 arquivos na varredura sem dado) e a seção da noite D-16 estava sem
desfecho. No `HOSTED_CI_REPORT.md`, faltava o CI do `main` depois do merge do #80. Os três foram corrigidos, e a
attestation foi reemitida:
- a nova `QUALIFICATION_ATTESTATION.json` (`b16ecbba…`) aponta `supersedes_sha256` para a anterior;
- a anterior está preservada byte a byte como `QUALIFICATION_ATTESTATION_superseded_094d9571c5e8.json`;
- nenhum gate, achado, contrato, alvo ou vetor mudou: continua `QUALIFIED`, 32 `PASS`, P0 = P1 = 0;
- o gate `HOSTED_CI` ganhou as 2 evidências do `main`.
`attest.py check` OK e `stage_a_recheck.py` OK (164 evidências): `RAW_LOGS/c14-rc3-20260924/review-final/attestation_reemitted.log`.

## 11. A pista dos outros otimizadores (2026-09-25; BR-F019, P2) e o BR-F010

`scripts/other_optimizers_sensitivity.py` → `RAW_LOGS/c14-rc3-20260924/review-final/other_optimizers_sensitivity.{json,log}`,
pela wheel rc3 no PC 2 (dado real só para o `fit_event_model`, cópia `31f30a4d…` antes e depois). Em cada ajuste: a mesma
entrada duas vezes e 1 ULP numa entrada contínua (`math.nextafter`).

| Ajuste | Mesma entrada | 1 ULP: máx. \|Δ\| parâmetros / probabilidades | Onde roda |
|---|---|---|---|
| `model.fit_goal_model` (controle, corrigido no BR-F018) | — | 1,8e-15 | worker de pesquisa (qualificado) |
| `event_models.fit_event_model` Poisson, dado real (escanteios / cartões) | igual | 5,5e-8 / 1,9e-8 — 4,1e-7 / 8,8e-8 | `brasileirao-predict --corners/--cards/--full` (rotulado SEM VALIDAÇÃO; tela em % inteiro) e `backtest_event` |
| `event_models.fit_event_model` Poisson, sintético | igual | 2,6e-7 / 1,0e-7 | idem |
| `event_models.fit_event_model` NB, sintético | igual | 2,0e-4 / 2,3e-4 | nenhum chamador usa a NB |
| `dixon_coles.fit_dixon_coles_parameters`, sintético | igual | 4,1e-6 | só scripts de benchmark (`evaluator.py`) |
| `xg_model.fit`, sintético | igual | 1,2e-5 | cron do cache e `serving_evaluator`; ensemble xG desligado (`ensemble_xg.enabled: false`) |

É a mesma classe do BR-F018: com diferenças finitas, o ponto de parada depende do último bit. Mas nada disso chega ao
resultado de pesquisa, à sombra diária ou a uma aposta, e o único uso na tela arredonda para porcentagem inteira. Por
isso é **P2** (C6: defeito sem efeito em resultado ou operação), `OPEN`. Corrigir exige mudar o domínio fora dos
`adapter_paths` (C24.4), então é decisão do dono.

**BR-F010 → `FIXED`.** O achado dizia que o teste do pré-registro fazia `pytest.skip` com o atestado de poder vencido.
Desde o A-04 (#79, `e0dab9a`, na rc3), o teste não pula mais: avisa e roda com o atestado real no instante em que era
válido. Renovar o atestado continua decisão do dono (artefato protegido).

A contagem de P2 abertos continua 5 (sai o BR-F010, entra o BR-F019), mas o `FINDINGS.json` mudou. Por isso a
attestation foi reemitida de novo (C7.1(8)) às 16:06:11Z, gerando a `efc56671…`
(`RAW_LOGS/c14-rc3-20260924/review-final/attestation_reemitted_2.log`). Depois disso, a nota do gate `BLOCKERS_ZERO`
ainda listava o BR-F010 entre os P2 abertos. Corrigi a nota (`ledger.py gate`) e reemiti mais uma vez às 16:07:34Z
(`attestation_reemitted_3.log`). A vigente é a `a4fa2fee…`, e a cadeia `supersedes_sha256` é
`a4fa2fee → efc56671 → b16ecbba → 094d9571`, com todas preservadas byte a byte. Continua `QUALIFIED`, 32 `PASS`,
P0 = P1 = 0, P2 = 5; `attest.py check` OK; `stage_a_recheck` OK (164 evidências).
