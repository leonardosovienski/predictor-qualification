# HOSTED_CI_REPORT — missão crypto (C21, gate `HOSTED_CI`)

Fonte: respostas brutas da API do GitHub em `RAW_LOGS/hosted-ci/` (`run_*.json`, `jobs_*.json`).
Todos os jobs listados passaram; nenhum foi pulado. Instalação por `uv sync --locked` nos
jobs de teste de cada repo.

| Repo | Commit | Papel | Workflow (evento) | Run | Jobs |
|---|---|---|---|---|---|
| cripto-predictor | `5fd4e1b` | baseline | CI (push, main) | [35822807920](https://github.com/leonardosovienski/cripto-predictor/actions/runs/35822807920) | quality, all-extras, python-314-experimental, container: success |
| cripto-predictor | `2bc63eb` | **final_commit** | CI (push, branch) | [35881545740](https://github.com/leonardosovienski/cripto-predictor/actions/runs/35881545740) | quality, all-extras, python-314-experimental, container: success |
| cripto-predictor | `2bc63eb` | final_commit (tag `v1.2.0rc1`) | CI (push, tag) | [35883171383](https://github.com/leonardosovienski/cripto-predictor/actions/runs/35883171383) | os mesmos 4: success |
| core-predictor | `5a08415` | baseline = final (congelado) | CI (push, main) | [35823003554](https://github.com/leonardosovienski/core-predictor/actions/runs/35823003554) | Python 3.13, wheel fora do checkout, auditoria, Python 3.14: success |
| core-predictor | `5a08415` | baseline = final | Push on main dynamic | [35823003519](https://github.com/leonardosovienski/core-predictor/actions/runs/35823003519) | Analyze (actions, python): success |
| predictor-ops | `7bd99eb` | baseline = final (congelado) | CI (push, main) | [35823068759](https://github.com/leonardosovienski/predictor-ops/actions/runs/35823068759) | test (ubuntu 3.13, ubuntu 3.14, windows 3.13), container: success |
| predictor-ops | `7bd99eb` | baseline = final | Push on main dynamic | [35823068277](https://github.com/leonardosovienski/predictor-ops/actions/runs/35823068277) | Analyze (actions): success |

Commits intermediários da branch com CI vermelho (preservados, **não** são `final_commit`):
`33fed6b` (pyright e higiene do `.gitignore`) e `9844976` (combine do coverage, CR-F014).
Estão corrigidos em `6f73051`, verde.

O PR [cripto-predictor#126](https://github.com/leonardosovienski/cripto-predictor/pull/126)
dispara o mesmo CI no evento `pull_request`.
