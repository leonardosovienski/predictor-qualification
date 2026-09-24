# CLEANROOM_REPORT — missão stocks (C5; gate CLEANROOM_FINAL)

Runtime suportado (C3.1): venv novo, dependências só do `uv.lock` exportado com `--require-hashes`, wheel do
stocks-predictor **publicada** (`v0.3.0rc2`, sha256 `92cb1131…`, conferido antes de instalar), Core e Ops pelas
wheels das releases; árvore de testes = final_commit **sem** `stocks_predictor/` (o código só pode vir da wheel);
execução a partir de um diretório fora de tudo. Script: `qualification/stocks/scripts/runtime_cleanroom.sh`,
workflow `.github/workflows/stocks-runtime.yml`, run 35954279991.

## cleanroom-final (Linux primário e windows-latest)

| | Linux primário | windows-latest |
|---|---|---|
| suíte de conformidade (junit) | 87/87 | 87/87 |
| E2E pelo entrypoint | 24/24 checagens | 24/24 checagens |
| `pip check` | sem requisitos quebrados | sem requisitos quebrados |
| suíte legada (árvore sem fonte) | 48 erros de coleta | 48 erros de coleta |

A suíte legada importa módulos planos da pasta-fonte (ST-F004, P2): não valida wheel instalada, igual ao
baseline. A validação da wheel pela suíte legada é feita no CI do repo (smoke da wheel fora do checkout, verde no
final_commit) e pela suíte completa com instalação `uv sync --locked` no final_commit: Linux
`1049 passed, 71 subtests passed in 218.01s (0:03:38)`, windows-latest
`1049 passed, 71 subtests passed in 403.73s (0:06:43)` (`qualification/stocks/RAW_LOGS/c14-rc2/suite-run35953426762`).
A rc1 (`9a6c09a`, `3cc4e04a…`, run 35949779357) teve o mesmo resultado; foi substituída pela rc2 depois dos
dependabot #93/#94 (C14, ST-F006).

## cleanroom-baseline (diagnóstico, 4e98a67)

Wheel construída do commit (não havia wheel publicada do HEAD). `python -m stocks_predictor doctor --check`
quebra no windows-latest por falta de `tzdata` (ST-F001, `qualification/stocks/RAW_LOGS/cleanroom-baseline/run35943720554/stocks-runtime-windows-latest/runtime_trace.log`);
os scripts extras do conjunto protegido não executam fora da máquina original (ST-F003).

Qualquer mudança de código depois deste cleanroom-final invalida-o (C14).
