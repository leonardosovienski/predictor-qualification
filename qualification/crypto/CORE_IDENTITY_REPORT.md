# CORE_IDENTITY_REPORT: missão crypto (C4, gates `LOCK_INTEGRITY` e `CORE_IDENTITY`)

Cadeia exigida para cada dependência do stack:
`pyproject range ↔ tool.uv.sources (URL da release) ↔ uv.lock ↔ instalação ↔ hash da wheel ↔ metadata instalado ↔ caminho do módulo em runtime`.

## 1. Baseline (`cripto-predictor` 5fd4e1b; truth-map)

Fonte: `RAW_LOGS/truth-map/core_identity_checkout_baseline.json` (`scripts/core_identity.py` no
venv do clone, que é diagnóstico de checkout: o `cripto-predictor` está em modo editable),
`RAW_LOGS/truth-map/uv_lock_check_baseline.log`, `STACK_BASELINE.json` (`stack_wheel_verification`).

| Pacote | pyproject | tool.uv.sources | uv.lock sha256 | Asset da release | Instalado | Módulo em runtime |
|---|---|---|---|---|---|---|
| predictor-core | `>=3.2.1,<4` | release `v3.2.1` | `10ef42f3…b4e3` | igual (API do GitHub) | 3.2.1, `direct_url` = URL da release | `.venv/site-packages/predictor_core` |
| predictor-ops | `>=4.2.0,<5` | release `v4.2.1` | `da4fa540…6f0e` | igual | 4.2.1, `direct_url` = URL da release | `.venv/site-packages/predictor_ops` |
| predictor-research-protocol | `==1.0.3rc1` | release do ecosystem | `312ab974…4032` | igual | 1.0.3rc1 | `.venv/site-packages/research_protocol` |

- `uv lock --check`: exit 0. `uv sync --locked --all-extras`: exit 0 (`RAW_LOGS/baseline/windows_pytest_5fd4e1b_run2.log`).
- Nenhum pacote do stack vem de índice público, `vendor/` ou checkout de outro repo.
- O uv não grava `archive_info.hash` no `direct_url.json`. A prova de bytes na instalação
  final vem do `pip install --require-hashes` a partir do lock exportado (cleanroom-final).
- `predictor-research-protocol` só serve ao envelope V1 (CAIN). Sai das dependências nesta
  missão (§8 do prompt; D-13).

## 2. Final

Preenchido na fase `cleanroom-final`, com as `final_wheels` instaladas no runtime suportado.
