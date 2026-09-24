# CLEANROOM_REPORT — missão brasileirao (C5)

## 1. cleanroom-baseline (diagnóstico do estado inicial)

Os commits do baseline da missão são os do `STACK_BASELINE_V1.1`: brasileirao `e14f339`,
core `5a08415`; o Ops do baseline do brasileirao ainda é a wheel 4.2.1 (`da4fa540…`) do `uv.lock`
(BR-F003). O cleanroom-baseline Linux × 3.13 de `e14f339` já existe, feito pelo SHARED-002
(run 35827048915, `qualification/shared/SHARED-002/CLEANROOM_REPORT.md`). Esta missão o
reaproveita como diagnóstico e não refaz a execução, porque o commit é o mesmo
(`STACK_BASELINE.json` → `head_vs_stack_baseline_v1_1`: brasileirao e core `equal: true`).

O que ele mostra para o brasileirao:

- A wheel publicada `0.2.0` (`2a862b4c…`, tag `4dbd353`) difere do commit com a mesma versão
  → **BR-F009**. Resolve com release nova em `publish-candidates`.
- Runtime instalado: `config.yaml` não vai na wheel e `ingest.load_config()`/avaliadores derivam a
  raiz de `__file__`; fora de checkout é preciso `BRASILEIRAO_CONFIG_PATH`/`BRASILEIRAO_PROJECT_ROOT`.
  O circuito novo não depende disso: dados, modelo e custos entram como objetos de referência com
  sha256 (contrato).
- Na árvore sem o pacote, 40 falhas + 2 erros do build do commit são testes que abrem arquivos de
  `brasileirao_scripts/` pelo caminho do repo ou a configuração do checkout (classe T do SHARED-002).
- Os 3 entrypoints respondem a `--help`; o plugin carrega.

Windows × 3.13 no baseline (checkout, diagnóstico): `RAW_LOGS/baseline/windows_suite_e14f339.log`
— ruff, format e pyright limpos; pytest 2207 passed, 1 skipped (BR-F010), 30 deselected
(integração com Redis de serviço, que roda só no CI).

## 2. cleanroom-final (gate `CLEANROOM_FINAL`)

Instalação limpa só com wheels publicadas, fora do checkout:

- brasileirao-predictor **0.3.0rc2**: [release v0.3.0rc2](https://github.com/leonardosovienski/brasileirao-predictor/releases/tag/v0.3.0rc2), sha256 `70344f2264e99c41808e90db26bdc94369504e3b45d125c77e01aebe71ad7b1a`, construída de `04b42c9`; build reprodutível (2 builds idênticos, `RAW_LOGS/publish-candidates/build_rc_04b42c9.log`).
- predictor-core 3.2.1 (`10ef42f3…`) e predictor-ops 4.2.2rc1 (`0be70bfb…`, D-17): releases publicadas, congeladas.
- Método: venv novo; dependências por `uv export --locked` com `--require-hashes`; a wheel do brasileirao baixada da URL da release e conferida por sha256 antes de instalar; `pip check`. Testes numa árvore = `final_commit` **sem** `brasileirao_predictor/` e `brasileirao_scripts/`, então o pacote só pode vir do site-packages (confirmado em `env.log` e `core_identity.json`).

| Ambiente | Conformidade | Suíte completa pela wheel | E2E (entrypoint, restart, releitura) | Evidência |
|---|---|---|---|---|
| Linux primário (ubuntu-latest, 3.13) | 89/89 | 2315 casos: 44 failed + 2 errors, todos classe T (BR-F017) | 26/26 checagens (sintético) | `RAW_LOGS/cleanroom-final/run35963501898/brasileirao-runtime-linux-primary/` |
| windows-latest (3.13) | 89/89 | idem (44 + 2 T) | 26/26 (sintético) | `…/brasileirao-runtime-windows-latest/` |
| Windows local (D-3, `C:\QUALIFICACAO\runtime\brasileirao\`) | 89/89 | — | 25/25, **dado real** | `RAW_LOGS/windows-smoke/rc2/` |

Números tirados do junit/logs brutos por `scripts/evidence_numbers.py` → `EVIDENCE_NUMBERS.json`
(`junit.conformance_rc2`, `junit.full_suite_wheel_rc2`, `e2e.rc2`).

As 46 T: 42 são as mesmas do cleanroom-baseline (SHARED-002: scripts lidos pelo caminho do repo,
`config.yaml`/`data/` do checkout, atestado do repo); 4 dependem de `git`/`.gitignore` e a árvore do
`git archive` não tem `.git`. Nenhuma exercita o código instalado; todas passam no CI do commit
(2305 passed). O circuito instalado é coberto pela conformidade inteira.

Execuções anteriores preservadas (não contam):

- `run35957989022` (v0.3.0rc1, `d3d8a8c`): conformidade 88/88 no Linux; no windows-latest 1 failed +
  15 errors na limpeza do laboratório (conexões SQLite não fechadas pelos testes, WinError 32) —
  defeito só de teste, corrigido em `cff7a3a`; a suíte completa parou na coleta (sem
  `--continue-on-collection-errors`). A rc1 não tem a correção BR-F015 e não é final_wheel.
- `run35956380520`: disparado pelo push do workflow antes de existir `runtime_target.json` (falha de setup, sem valor).
