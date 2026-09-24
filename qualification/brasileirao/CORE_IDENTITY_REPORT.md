# CORE_IDENTITY_REPORT — missão brasileirao (gates `LOCK_INTEGRITY`, `CORE_IDENTITY`, C4)

## 1. Baseline (truth-map)

`e14f339` consumia predictor-core 3.2.1 (`10ef42f3…`) e **predictor-ops 4.2.1** (`da4fa540…`), a wheel
bloqueante da SHARED-005 (BR-F003). Cadeia coerente, mas versão errada para a V1.1 (D-17).

## 2. Final (`04b42c9`, v0.3.0rc2)

Cadeia de cada dependência do stack:

| Elo | predictor-core | predictor-ops |
|---|---|---|
| `pyproject` range | `>=3.2.1,<4` | `>=4.2.2rc1,<5` (commit `5344b5f`) |
| `tool.uv.sources` | release `v3.2.1` | release `v4.2.2rc1` |
| `uv.lock` (versão, URL, hash) | 3.2.1, `…/v3.2.1/predictor_core-3.2.1-py3-none-any.whl`, `10ef42f34ace8bb2df5f83ff7de2ceec79b035a25ea0a690e8942bd60d2fb4e3` | 4.2.2rc1, `…/v4.2.2rc1/predictor_ops-4.2.2rc1-py3-none-any.whl`, `0be70bfbb2437dfb080baceb9af41043a09d03b15a358903b8bd7007f5f169b3` |
| asset da release | idem (sha256 do asset) | idem (asset oficial do workflow Release do Ops, D-17) |
| `constraints/shared-wheels.sha256` + CI/Dockerfiles | baixa e confere o mesmo sha256 antes de instalar | idem |
| instalação (CI: `uv sync --locked`; cleanroom e Windows: `uv export --locked` + `--require-hashes`) | wheel da URL (`direct_url.json` com o sha256) | idem |
| metadata instalado | 3.2.1, não editable | 4.2.2rc1, não editable |
| módulo em runtime | `site-packages/predictor_core` do venv | `site-packages/predictor_ops` do venv |

Evidência por ambiente (`core_identity.py` roda dentro do interpretador sob teste, a partir de um
diretório fora de tudo):

| Ambiente | Arquivo |
|---|---|
| Linux primário (Actions, venv limpo, wheels publicadas) | `RAW_LOGS/cleanroom-final/run35963501898/brasileirao-runtime-linux-primary/core_identity.json` |
| windows-latest | `RAW_LOGS/cleanroom-final/run35963501898/brasileirao-runtime-windows-latest/core_identity.json` |
| Windows local (runtime D-3) | `RAW_LOGS/windows-smoke/rc2/core_identity_windows_local.json` |

Nos três: os três pacotes do stack (core 3.2.1, ops 4.2.2rc1, brasileirao-predictor 0.3.0rc2) vêm de
wheel, não editable, com o módulo no `site-packages` do venv; `lock_chain` = pyproject ↔ source ↔ lock
com a mesma URL e o mesmo sha256. `runtime_trace.log` confirma a origem dos módulos carregados ao
executar os entrypoints instalados (`brasileirao-research`, `brasileirao-predict`,
`brasileirao-shadow`). Nenhum pacote do stack vem de índice público, `vendor/` ou checkout.

A wheel do próprio brasileirao-predictor (`70344f2264e99c41808e90db26bdc94369504e3b45d125c77e01aebe71ad7b1a`)
foi baixada da URL da release v0.3.0rc2 e conferida por sha256 antes de instalar (env.log: `OK`).

## 3. Lock

`uv lock --check`/`uv sync --locked` passam no CI do commit final (job `python`) e no Windows local
(`RAW_LOGS/contract-admission/windows_suite_cff7a3a.log`: `uv sync exit=0`); o lock só mudou na troca
de versão do Ops e do próprio pacote (diffs de 8 e 2 linhas).
