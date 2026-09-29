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

## V1.1 (D-17: predictor-ops 4.2.2rc1)

Fonte: `RAW_LOGS/v1.1/hosted-ci/`. Todos os jobs com sucesso; nenhum pulado.

| Repo | Commit | Workflow (evento) | Run |
|---|---|---|---|
| cripto-predictor | `341d270` (final) | CI (push, branch) | [35906112873](https://github.com/leonardosovienski/cripto-predictor/actions/runs/35906112873) — 4 jobs |
| cripto-predictor | `341d270` | CI (push, tag `v1.2.0rc2`) | [35925694691](https://github.com/leonardosovienski/cripto-predictor/actions/runs/35925694691) — 4 jobs |
| predictor-ops | `9831b0d` (final) | CI (pull_request #26) | [35905393899](https://github.com/leonardosovienski/predictor-ops/actions/runs/35905393899) — ubuntu 3.13/3.14, windows-latest, container |
| predictor-ops | `9831b0d` | CI (push, tag `v4.2.2rc1`) | [35905678198](https://github.com/leonardosovienski/predictor-ops/actions/runs/35905678198) |
| predictor-ops | `9831b0d` | Release (tag) | [35905678109](https://github.com/leonardosovienski/predictor-ops/actions/runs/35905678109) — build com attestation + validação da wheel publicada |
| core-predictor | `5a08415` | inalterado (ver acima) | |

## V1.2 (reabertura D-27: cripto 1.2.0rc4 / 21f8b182)

Fonte: `RAW_LOGS/v1.2/hosted-ci/` (API pública do GitHub, sem edição). Baseline = final desta reabertura (`21f8b182`, `main`).

| Repo | Commit | Papel | Workflow (evento) | Run | Jobs |
|---|---|---|---|---|---|
| cripto-predictor | `21f8b182` | baseline = final_commit V1.2 | CI (push, main) | [36642919823](https://github.com/leonardosovienski/cripto-predictor/actions/runs/36642919823) | quality: success, all-extras: success, python-314-experimental: success, container: success |
| cripto-predictor | `21f8b182` | release v1.2.0rc4 | Release (workflow_dispatch) | [36643518795](https://github.com/leonardosovienski/cripto-predictor/actions/runs/36643518795) | release: success |
| core-predictor | `5a08415` | final (congelado; wheel inalterada) | herdado da V1.0 (mesmo commit) | [35823003554](https://github.com/leonardosovienski/core-predictor/actions/runs/35823003554) | success |
| predictor-ops | `9831b0d` | final (congelado; wheel inalterada) | herdado da V1.1 (mesmo commit) | [35905678198](https://github.com/leonardosovienski/predictor-ops/actions/runs/35905678198) | success |

`HOSTED_CI` V1.2: **PASS**. Nenhum job pulado.
