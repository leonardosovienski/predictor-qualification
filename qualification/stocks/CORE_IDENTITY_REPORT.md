# CORE_IDENTITY_REPORT — missão stocks (C4; gates LOCK_INTEGRITY, CORE_IDENTITY, STOCKS_CORE_PIN)

Cadeia exigida (C4): range no `pyproject` ↔ `tool.uv.sources` (URL da release) ↔ `uv.lock` ↔ instalação ↔ hash da
wheel ↔ metadata instalada ↔ caminho do módulo em runtime. Medida pelo script
`qualification/stocks/scripts/core_identity.py`, rodando **dentro** do interpretador do runtime, num diretório fora
de qualquer checkout.

## Antes da mudança (baseline `4e98a67`, wheel do Stocks construída do commit — diagnóstico)

Fonte: `qualification/stocks/RAW_LOGS/cleanroom-baseline/run35943720554/stocks-runtime-linux-primary/core_identity.json`.

| pacote | versão | sha256 da wheel instalada | módulo em site-packages |
|---|---|---|---|
| predictor-core | 3.2.1 | `10ef42f34ace8bb2df5f83ff7de2ceec79b035a25ea0a690e8942bd60d2fb4e3` | True |
| stocks-predictor | 0.2.0 | `b0b64211c6a3540ee15f912f9ceab7529a4adeeae16ebf7a59d391ed4446f9c6` | True |

`predictor-ops` ausente (prompt §3 confirmado: nenhuma dependência nem import).
`uv lock --check`: `qualification/stocks/RAW_LOGS/cleanroom-baseline/run35943720554/stocks-runtime-linux-primary/uv_lock_check.log`.

## Depois de adicionar o Ops (final_commit `9a6c09a`, só wheels publicadas)

Fontes: `qualification/stocks/RAW_LOGS/cleanroom-final/run35949779357/stocks-runtime-linux-primary/core_identity.json` e `qualification/stocks/RAW_LOGS/cleanroom-final/run35949779357/stocks-runtime-windows-latest/core_identity.json`;
lock conferido por `uv lock --check` (`qualification/stocks/RAW_LOGS/cleanroom-final/run35949779357/stocks-runtime-linux-primary/uv_lock_check.log`) e instalação por
`pip install --require-hashes -r` do lock exportado (`qualification/stocks/RAW_LOGS/cleanroom-final/run35949779357/stocks-runtime-linux-primary/requirements.locked.txt`).

| runtime | pacote | versão | sha256 instalado | range no pyproject | sha256 no uv.lock | em site-packages | editable |
|---|---|---|---|---|---|---|---|
| Linux primário (ubuntu-latest) | predictor-core | 3.2.1 | `10ef42f34ace8bb2df5f83ff7de2ceec79b035a25ea0a690e8942bd60d2fb4e3` | predictor-core>=3.2.1,<4 | `10ef42f34ace8bb2df5f83ff7de2ceec79b035a25ea0a690e8942bd60d2fb4e3` | True | False |
| Linux primário (ubuntu-latest) | predictor-ops | 4.2.2rc1 | `0be70bfbb2437dfb080baceb9af41043a09d03b15a358903b8bd7007f5f169b3` | predictor-ops==4.2.2rc1 | `0be70bfbb2437dfb080baceb9af41043a09d03b15a358903b8bd7007f5f169b3` | True | False |
| Linux primário (ubuntu-latest) | stocks-predictor | 0.3.0rc1 | `3cc4e04a04967efb11e16000815b8c632cf9659e2703b097a1277dabf5639467` | — (o próprio pacote) | wheel da release v0.3.0rc1 | True | False |
| windows-latest | predictor-core | 3.2.1 | `10ef42f34ace8bb2df5f83ff7de2ceec79b035a25ea0a690e8942bd60d2fb4e3` | predictor-core>=3.2.1,<4 | `10ef42f34ace8bb2df5f83ff7de2ceec79b035a25ea0a690e8942bd60d2fb4e3` | True | False |
| windows-latest | predictor-ops | 4.2.2rc1 | `0be70bfbb2437dfb080baceb9af41043a09d03b15a358903b8bd7007f5f169b3` | predictor-ops==4.2.2rc1 | `0be70bfbb2437dfb080baceb9af41043a09d03b15a358903b8bd7007f5f169b3` | True | False |
| windows-latest | stocks-predictor | 0.3.0rc1 | `3cc4e04a04967efb11e16000815b8c632cf9659e2703b097a1277dabf5639467` | — (o próprio pacote) | wheel da release v0.3.0rc1 | True | False |

`tool.uv.sources`: Core `…/core-predictor/releases/download/v3.2.1/predictor_core-3.2.1-py3-none-any.whl`,
Ops `…/predictor-ops/releases/download/v4.2.2rc1/predictor_ops-4.2.2rc1-py3-none-any.whl` (URL de release;
nenhum pacote do stack vem de índice público, `vendor/` ou checkout). A wheel do Stocks vem da release
`v0.3.0rc1` (asset conferido por sha256 antes da instalação, `qualification/stocks/RAW_LOGS/cleanroom-final/run35949779357/stocks-runtime-linux-primary/env.log`).

**STOCKS_CORE_PIN:** range `>=3.2.1,<4` (D-7), fonte = release v3.2.1, lock = 3.2.1 `10ef42f3…`, wheel instalada =
`10ef42f3…`, nos dois runtimes.
