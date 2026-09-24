#!/usr/bin/env bash
# Etapa 1 (diagnóstico): suíte completa do cripto-predictor no commit do runtime_target.json, método do CI (ci.yml job test).
set -uo pipefail
export PATH="$HOME/predictors/tools/uv:$PATH" UV_PYTHON_INSTALL_DIR="$HOME/predictors/tools/python" UV_CACHE_DIR="$HOME/predictors/tools/uv-cache" UV_PYTHON_PREFERENCE=only-managed
export UV_PROJECT_ENVIRONMENT="$HOME/predictors/runtime/cripto/venv"
L="$HOME/predictors/runtime/cripto/logs"
cd "$HOME/predictors/work/cripto-cripto-predictor"
{ echo "start $(date -u +%FT%TZ) HEAD=$(git rev-parse HEAD) status=[$(git status --porcelain | wc -l) alterações]"; uv --version; sha256sum uv.lock; } > "$L/suite_env.log" 2>&1
uv sync --locked --all-extras >> "$L/suite_env.log" 2>&1; echo "[uv sync exit $?]" >> "$L/suite_env.log"
"$UV_PROJECT_ENVIRONMENT/bin/python" -V >> "$L/suite_env.log" 2>&1
uv build >> "$L/suite_env.log" 2>&1; echo "[uv build exit $?]" >> "$L/suite_env.log"
uv run --no-sync pytest --cov=GarimpoInvestimentos --cov-report=term-missing -p no:cacheprovider --junitxml="$L/suite.junit.xml" > "$L/suite_pytest.log" 2>&1
echo "[pytest exit $?]" >> "$L/suite_pytest.log"
echo "end $(date -u +%FT%TZ)" >> "$L/suite_env.log"
