# HOSTED_CI_REPORT — missão stocks (C21; gate HOSTED_CI)

Workflows de `push`/`pull_request` dos repos da missão, no GitHub Actions, nos commits do baseline e nos
`final_commits`, instalando com `uv sync --locked`. Registros brutos (`gh run view --json`, com todos os jobs) em
`qualification/stocks/RAW_LOGS/hosted-ci/`. Nenhum job pulado.

| repo | commit | papel | workflow / evento | run | resultado | jobs |
|---|---|---|---|---|---|---|
| stocks-predictor | `4e98a67` | baseline | CI Pipeline / push | [35822899971](https://github.com/leonardosovienski/stocks-predictor/actions/runs/35822899971) | success | secrets, Quality 3.13, Quality 3.14 |
| stocks-predictor | `9a6c09a` | final_commit (SHA exato) | CI Pipeline / workflow_dispatch na branch | [35950266341](https://github.com/leonardosovienski/stocks-predictor/actions/runs/35950266341) | success | secrets, Quality 3.13, Quality 3.14 |
| stocks-predictor | `9a6c09a` | final_commit (PR #95, ref de merge) | CI Pipeline / pull_request | [35948594270](https://github.com/leonardosovienski/stocks-predictor/actions/runs/35948594270) | success | secrets, Quality 3.13, Quality 3.14 |
| core-predictor | `5a08415` | baseline = final (congelado) | CI / push | [35823003554](https://github.com/leonardosovienski/core-predictor/actions/runs/35823003554) | success | Python 3.13, wheel fora do checkout, auditoria, Python 3.14 |
| predictor-ops | `9831b0d` | baseline = final (v4.2.2rc1, D-17) | CI / push | [35905678198](https://github.com/leonardosovienski/predictor-ops/actions/runs/35905678198) | success | ubuntu 3.13/3.14, windows-latest 3.13, container |
| predictor-ops | `9831b0d` | idem | CI / pull_request | [35905393899](https://github.com/leonardosovienski/predictor-ops/actions/runs/35905393899) | success | idem |
| predictor-ops | `9831b0d` | idem | Release / push | [35905678109](https://github.com/leonardosovienski/predictor-ops/actions/runs/35905678109) | success | build, publicação, verificação da wheel publicada (ubuntu 3.13/3.14, windows 3.13) |

O job `Quality` do stocks-predictor roda `uv sync --locked --all-extras`, ruff, pyright, os verificadores de evidência
do repo (R7, R8 — este com os recibos D-18 —, handoff, arquivos), a suíte completa com cobertura (piso 77%), build
reprodutível e o smoke da wheel fora do checkout; `secrets` roda gitleaks na árvore inteira com controle sintético.

Complementos do repositório de evidência (não substituem o CI do repo): suíte do stocks-predictor no Linux e no
windows-latest a cada mudança (`.github/workflows/stocks-suite.yml`), runtime limpo (`stocks-runtime.yml`), build da
rc (`stocks-build-rc.yml`), varredura de segredos (`stocks-secrets.yml`).

Depois do merge do PR #95 pelo dono, o CI de `push` no `main` roda sobre o commit de merge (outro SHA); o gate
refere-se ao `final_commit` `9a6c09a`, verde no próprio SHA.

## C14 (ST-F006): final_commit `61fc017` (rc2)

Os dependabot #93/#94 foram mesclados antes do #95; o CI de push no merge `2a18513` falhou
(`tools/verify_operational_evidence.py`: selo R8 desatualizado; `RAW_LOGS/c14-rc2/ci_main_2a18513_failure.json`).
Corrigido em `61fc017` (ressela), que passa a ser o final_commit:

| repo | commit | workflow / evento | run | resultado |
|---|---|---|---|---|
| stocks-predictor | `61fc017` (SHA exato) | CI Pipeline / workflow_dispatch | [35953418753](https://github.com/leonardosovienski/stocks-predictor/actions/runs/35953418753) | success (secrets, Quality 3.13, Quality 3.14) |
| stocks-predictor | `61fc017` (PR #96) | CI Pipeline / pull_request | [35953419340](https://github.com/leonardosovienski/stocks-predictor/actions/runs/35953419340) | success (secrets, Quality 3.13, Quality 3.14) |
