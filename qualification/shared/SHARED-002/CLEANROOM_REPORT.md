# SHARED-002 — cleanroom-baseline dos 7 repos (C5)

Missão: `prompts/baseline_comum_rev8.md` (núcleo v2.0, sha256 `50e8f498…ee36e1`, conferido no C0).
**Diagnóstico, não qualificação.** Registra o que quebra quando cada repo é instalado só com
wheels publicadas; nada foi consertado. Nenhum gate foi avaliado, nenhum treinamento iniciado,
nenhum capital movido, nenhuma instalação operacional tocada.

## Como foi feito

| Item | Valor |
|---|---|
| Ambiente | GitHub Actions `ubuntu-24.04` (Ubuntu 24.04.5 LTS, kernel 6.17.0-1022-azure, x86_64), CPython 3.13.15 gerenciado, uv 0.12.18 (sha256 conferido) |
| Commits | os do `STACK_BASELINE_V1` (`qualification/shared/STACK_BASELINE_V1.json`) |
| Plano congelado | `CLEANROOM_PLAN_V2.json` (sha256 `a85fcabd…c627b`); substitui `CLEANROOM_PLAN.json` (V1, `7ed2c84f…7a80`), ver abaixo |
| Run de referência | [35827048915](https://github.com/leonardosovienski/predictor-qualification/actions/runs/35827048915) no commit `e8dae41` (plano V2), 7/7 jobs `success` (harness completo) |
| Run anterior | [35826713033](https://github.com/leonardosovienski/predictor-qualification/actions/runs/35826713033) no commit `ab7aeb8` (plano V1), preservado |
| Números | `SUMMARY_run35827048915.txt` (sha256 `a37e99b2…c92f`) e `SUMMARY_run35826713033.txt` (`a9198bda…51d8`), gerados por `scripts/summarize_cleanroom.py` a partir de `RAW_LOGS/SHARED-002/run*/` |

Para cada repo, num venv novo fora do checkout:

1. `uv lock --check` no clone do commit; `uv export --frozen --no-emit-project --all-extras --no-dev`;
2. instalação só pelo lock exportado (`--require-hashes --no-deps`: terceiros + wheels do stack por URL de release)
   e pelas wheels próprias (`--no-deps`);
3. `uv pip check`; identidade (versão, `direct_url`, caminho do módulo em `site-packages`);
   `--help` de cada `console_scripts`; carga dos entry points `predictor.plugins`;
4. suíte de testes do commit, numa árvore em que os diretórios de pacote de layout plano foram
   excluídos por sparse-checkout (para a suíte não importar o checkout), com um plugin (`cleanroom_guard`)
   que registra a origem de todo módulo do stack importado;
5. comparação arquivo a arquivo entre a wheel publicada e a construída do commit.

Duas variantes por repo:

- **`published`** — wheels próprias = assets da última release do repo. É o runtime suportado (C3.1).
- **`head_build`** — **diagnóstico**: wheels próprias construídas do commit do baseline (`uv build`).
  Não é cleanroom e nunca vale como PROVEN. Serve para separar deriva de versão (publicada ≠ commit) de
  quebra de instalação (o próprio commit instalado por wheel).

### Plano V1 → V2

O V1 tinha três defeitos de método, vistos no run 35826713033: (1) excluía `src/` também nos repos de
layout `src/`, apagando arquivos que testes leem por caminho (cain 2 falhas, ops 1), sem proteger
nada; (2) um erro de coleta interrompia a sessão do pytest (cain, brasileirao e stocks rodaram 0 testes);
(3) o conftest de `packages/research-export/tests` abortou a suíte principal do cripto (exit 4).
O V2 corrige só isso: instala as mesmas wheels e roda os mesmos testes. Como o V2 foi escrito depois de ver
o run 1, a troca fica exposta aqui e no PR para o dono aceitar ou não.

## Resultado — instalação e identidade (7/7 repos)

| Repo | commit | `uv lock --check` | instala pelo lock | wheels publicadas (sha256) | `pip check` (publicada) | `--help` | plugins |
|---|---|---|---|---|---|---|---|
| cain | `8b8915aa` | OK | OK | 1/1 | **FAIL**: `cain-research 0.4.5` exige `predictor-research-snapshot==1.0.0`, lock tem `1.0.2rc1` | 1/1 (publicada), 3/3 (commit) | — |
| ecosystem-predictor | `0a4f87e5` | OK | OK | 4/4 | OK | — | — |
| core-predictor | `5a084150` | OK | OK | 1/1 | OK | — | — |
| predictor-ops | `7bd99eba` | OK | OK | 1/1 | OK | 1/1 | — |
| brasileirao-predictor | `e14f3394` | OK | OK | 1/1 | OK | 3/3 | 1/1 |
| cripto-predictor | `5fd4e1b0` | OK | OK | 2/2 | **FAIL**: `crypto-research-export` exige `predictor-research-snapshot`, ausente do lock | 2/3 (`crypto-research-export` sai 1) | 1/1 |
| stocks-predictor | `4e98a67b` | OK | OK | 1/1 | OK | nenhum `[project.scripts]` | 1/1 |

Em todos os repos e nas duas variantes, todo pacote do stack importado veio do `site-packages` do venv
(introspecção + guard). Exceções: o módulo `crypto_research_export` não importa (falta `research_snapshot`),
e o guard não gravou saída no brasileirao (ver Limites).

## Resultado — suíte de testes (run 35827048915)

Linhas-resumo do pytest, copiadas do log bruto:

| Repo | `published` (runtime suportado) | `head_build` (diagnóstico) |
|---|---|---|
| cain | 80 failed, 316 passed, 46 errors | **920 passed**, 2 skipped |
| ecosystem-predictor | 2 failed, 184 passed | **186 passed** |
| core-predictor | **278 passed** | **278 passed** |
| predictor-ops | 3 failed, 85 passed | 3 failed, 85 passed |
| brasileirao-predictor | 76 failed, 1990 passed, 1 skipped, 36 errors (30 integration deselected) | 40 failed, 2143 passed, 1 skipped, 2 errors (30 deselected) |
| cripto-predictor `tests` | 21 failed, 1540 passed, 6 errors | 18 failed, 1600 passed |
| cripto-predictor `packages/research-export/tests` | não coleta (exit 4: `No module named 'research_snapshot'`) | idem |
| stocks-predictor | 23 failed, 433 passed, 50 errors | 25 failed, 475 passed, 48 errors |

## O que quebra, por repo

Classes: **R** = defeito no runtime suportado (afeta a Etapa A/B); **V** = deriva de versão (wheel
publicada ≠ commit); **T** = o teste pressupõe checkout ou instalação editable (o código instalado não é o
problema); **M** = artefato deste método. A severidade é **sugestão** para a missão dona; aqui nada é
bloqueio nem veredito.

### core-predictor — limpo

Wheel publicada 3.2.1 (`10ef42f3…`) = commit (só `METADATA`/`WHEEL` diferem). 278/278 nas duas variantes.

### predictor-ops — SHARED-004

Wheel publicada 4.2.1 (`da4fa540…`) = commit (só `METADATA`/`WHEEL` diferem). As mesmas 3 falhas nas duas
variantes: `test_source_clean_dirty_detached_and_missing_commit`,
`test_strict_editable_fails_closed_and_permissive_is_safe` e
`test_strict_setup_failure_is_terminal_and_child_never_runs`. No CI do Ops (editable) as três passam.

- **R ou T (sem veredito):** `collect_provenance(strict=True, source_root=<fonte suja>)` acumula o erro da
  fonte e cai em `_verify_wheel`. Com instalação por wheel, isso devolve `VALIDATED` (identidade da wheel
  do Ops) em vez de falhar fechado. `runner.py:237` chama sem `source_root` (não afetado);
  `cli.py:47` (proveniência com `--source-root`) é afetado. Registrado como **SHARED-004** em
  `SHARED_ISSUES.json`. Classificação e `blocking` ficam com a missão dona (proposta: `crypto`).
- **SHARED-003** (`test_timeout_and_truncation`): **passou** a partir da wheel publicada e da wheel do
  commit, nos dois runs (4/4). Acrescentado à triagem.
- **M:** `test_wheel_record_tampering_fails_in_isolated_environment` falhou só no V1, porque constrói wheel de
  uma árvore sem `src/`.

### ecosystem-predictor

- **V/R (P1 sugerido para a Etapa B):** a `ecosystem-predictor 0.2.0` publicada (`c0925a60…`, tag em
  `2e8be61`) difere do commit em `ecosystem/registry/__init__.py`. Com ela falham
  `test_plugin_exception_messages_never_escape` (o texto da exceção do plugin, `SYNTHETIC_PRIVATE_VALUE`, sai no
  log) e `test_constructor_error_does_not_crash_discovery`. O commit corrige isso (186/186), mas a correção
  não está publicada.
- **V (C4):** publicada e commit têm a **mesma versão, `0.2.0`**, com bytes diferentes.
- As três rc do protocolo publicadas têm conteúdo igual ao commit (só `METADATA` difere).

### cain

- **V:** não existe wheel publicada da versão do commit (`0.4.13rc4`); a última release é `v0.4.5`
  (`89f23665…`, 30 arquivos diferentes e 37 só no commit). Ela é incompatível com o lock
  (`predictor-research-snapshot==1.0.0`). Daí as 80 falhas e os 46 erros.
- Commit instalado por wheel: 920 passed, 2 skipped. Instala e roda limpo; falta só publicar.

### brasileirao-predictor

- **V (C4):** a publicada `0.2.0` (`2a862b4c…`, tag em `4dbd353`) difere do commit em 4 módulos, e 2
  módulos existem só no commit (`prospective_metrics`, `prospective_protocol_v2`). A versão é a mesma, `0.2.0`.
- **T (23 das 42 falhas+erros no commit):** testes abrem arquivos de `brasileirao_scripts/` pelo caminho no repo
  (`report_shadow_mode.py`, `install_windows_scheduler.ps1`, `sombra*.py`, `sync_matches_from_sofascore.py`, …).
  Na árvore sem o pacote eles não existem.
- **R leve / configuração (as outras 19 no commit):** instalado, `ingest.load_config()` procura
  `site-packages/config.yaml` e o avaliador procura `site-packages/data/trials.harness_attestation.json`,
  porque a raiz do projeto é derivada de `__file__`. O código aceita `BRASILEIRAO_CONFIG_PATH` /
  `BRASILEIRAO_PROJECT_ROOT`, então no runtime suportado a Etapa A precisa fornecê-los explicitamente. A
  wheel não traz `config.yaml` (`RAW_LOGS/SHARED-002/wheel_content_checks.log`).
- Os 3 entrypoints respondem a `--help`; o plugin carrega.

### cripto-predictor

- **R (P1 sugerido para a Etapa A):** `GarimpoInvestimentos/output/` (`reporter.py`) fica **fora das duas
  wheels** porque o `.gitignore` tem `output/` sem âncora (linha 12), e o hatchling respeita o `.gitignore`.
  `GarimpoInvestimentos/main.py:58` e `services/reporting.py:1` importam
  `GarimpoInvestimentos.output.reporter`. O caminho padrão de análise do `cripto-predictor` falha no runtime
  suportado; o `--help` passa porque sai antes do import. Confirmado na wheel publicada `41e48e0d…` (185
  entradas, nenhuma em `output/`): `RAW_LOGS/SHARED-002/wheel_content_checks.log`.
- **R (P2 sugerido):** `crypto-research-export 1.0.1` (publicada no mesmo release) exige
  `predictor-research-snapshot`, que não está no `uv.lock` do cripto. O módulo não importa, o console script
  sai 1 e os testes do pacote não coletam.
- **V:** não existe wheel publicada da versão do commit (`1.1.1rc4`); a `1.1.0` difere em 17 arquivos e tem 24
  a menos.
- **T (demais falhas do commit):** assinaturas no log bruto: 11 × `GarimpoInvestimentos/trials.json` lido pelo caminho no repo, 2 × `dist/` esperado na árvore, e leituras de outros arquivos pelo
  caminho ou do checkout (git, gitignore).
  Uma falha é a do `output` acima.

### stocks-predictor

- **R (P1 sugerido para a Etapa A, C24 `entrypoint`):** não há `[project.scripts]`. A CLI operacional é
  `main.py` na raiz do repo, que fica fora da wheel e importa módulos soltos (`import config`).
- **R (P1 sugerido, teste exigido ausente):** a suíte importa módulos com nome solto (`import adjust`,
  `db`, `backtest`, …) via `sys.path.insert(0, ROOT/"stocks_predictor")` em `tests/conftest.py`. Nessa forma ela
  **nunca exercita a wheel instalada**: no cleanroom são 48–50 erros de coleta por isso, e no CI do repo os testes
  rodam sobre o checkout.
- **V (C4):** a publicada `0.2.0` (`a839aeca…`, tag em `56c1a7b`) difere do commit em `operations.py`, e 4
  módulos existem só no commit. A versão é a mesma.
- O plugin carrega.

## Entrada para a Etapa A

| Missão | O que o cleanroom-baseline mostra |
|---|---|
| todas | Core 3.2.1 e Ops 4.2.1 publicados = commit; locks íntegros e com as wheels certas. Veredito da SHARED-004 antes de `SHARED_DEPENDENCY_CLEAR`. |
| crypto | publicar rc da versão do commit; `output/` fora da wheel; `crypto-research-export` sem dependência no lock; testes que leem o checkout. Dona proposta da SHARED-003 e da SHARED-004. |
| brasileirao | publicar versão nova (a `0.2.0` publicada ≠ commit); runtime instalado precisa de `BRASILEIRAO_CONFIG_PATH`/`BRASILEIRAO_PROJECT_ROOT`; testes que abrem scripts por caminho. |
| stocks | criar entrypoint em `[project.scripts]`; suíte que importe `stocks_predictor.*` da wheel; publicar versão nova. |

CAIN e Ecosystem mudam só na Etapa B. Para eles fica registrado que o commit instala e roda limpo por
wheel, mas não há release dele.

## Limites deste diagnóstico

- Uma execução por variante, só Linux × 3.13.15 (Windows não coberto aqui).
- Brasileirão: o guard não gravou saída nas duas variantes, com causa não determinada. A suíte não teve como
  importar o checkout: a árvore não tinha `brasileirao_predictor/` nem `brasileirao_scripts/`
  (`tree_strip_paths_absent` = true) e os tracebacks apontam para `venv-*/site-packages`.
- Os 30 testes `integration` do Brasileirão (Redis) ficaram de fora, como no `addopts` do repo.
- `head_build` usa `uv build` do commit, sem `SOURCE_DATE_EPOCH`. Por isso só `METADATA`/`WHEEL` diferem
  nas wheels de conteúdo igual.
- Classes **T** e **R** são leitura do log e do código, não veredito. A decisão é da missão dona.
