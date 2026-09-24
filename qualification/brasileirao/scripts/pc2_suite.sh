#!/usr/bin/env bash
# brasileirao: suíte completa do brasileirao-predictor no PC 2 (Ubuntu 24.04 / WSL2) — diagnóstico (conferência geral).
# Método = job `python` do ci.yml, como o win_suite.sh: uv sync --locked --all-extras; validate_env_example;
# seed_test_fixtures; ruff check/format; pyright; pytest -m "not integration"; uv build. Fica de fora só o passo
# `pytest -m integration` (exige o Redis de serviço do CI, que o PC 2 não tem) e o coverage.
# Venv criado só do uv.lock, fora do checkout: ~/predictors/runtime/brasileirao/venv-suite (UV_PROJECT_ENVIRONMENT).
# Python: só o gerenciado em ~/predictors/tools (3.13; o 3.14 da matriz do CI não está instalado no PC 2).
# Uso: pc2_suite.sh <worktree do commit> <log> <junit>
set -u
CLONE="$1"; LOG="$2"; JUNIT="$3"
R="$HOME/predictors/runtime/brasileirao"
export PATH="$HOME/predictors/tools/uv:$PATH" UV_PYTHON_INSTALL_DIR="$HOME/predictors/tools/python" \
  UV_CACHE_DIR="$HOME/predictors/tools/uv-cache" UV_PYTHON_PREFERENCE=only-managed
export UV_PROJECT_ENVIRONMENT="$R/venv-suite"
STAMP="$(date -u +%m%dT%H%M%S)"
RUNROOT="$R/w/$STAMP"
mkdir -p "$RUNROOT/tmp"
export TMP="$RUNROOT/tmp" TEMP="$RUNROOT/tmp" TMPDIR="$RUNROOT/tmp"
export PYRIGHT_PYTHON_CACHE_DIR="$R/pyright-cache"
PY="$UV_PROJECT_ENVIRONMENT/bin/python"
cd "$CLONE"
{
  echo "# $(date -u +%FT%TZ) commit $(git rev-parse HEAD) dirty_entries=$(git status --porcelain | wc -l) RUNROOT=$RUNROOT"
  echo "# host: $(uname -srm) | $(. /etc/os-release && echo "$PRETTY_NAME")"
  uv --version
  uv sync --locked --all-extras 2>&1; echo "uv sync exit=$?"
  "$PY" -c "import sys,platform;print(sys.version,platform.platform())"
  "$PY" -c "import predictor_core,predictor_ops,importlib.metadata as m;print('core',m.version('predictor-core'),predictor_core.__file__);print('ops',m.version('predictor-ops'),predictor_ops.__file__)"
  uv run --locked python brasileirao_scripts/validate_env_example.py 2>&1; echo "validate_env_example exit=$?"
  uv run --locked python brasileirao_scripts/seed_test_fixtures.py 2>&1; echo "seed_test_fixtures exit=$?"
  uv run --locked ruff check brasileirao_predictor brasileirao_scripts tests 2>&1 | tail -5; echo "ruff check exit=${PIPESTATUS[0]}"
  uv run --locked ruff format --check brasileirao_predictor brasileirao_scripts tests 2>&1 | tail -5; echo "ruff format exit=${PIPESTATUS[0]}"
  uv run --locked pyright brasileirao_predictor 2>&1 | tail -5; echo "pyright exit=${PIPESTATUS[0]}"
  "$PY" -m pytest -p no:cacheprovider --junitxml="$JUNIT" -q -o addopts="" -m "not integration" 2>&1 | tail -80; echo "pytest exit=${PIPESTATUS[0]}"
  uv build --out-dir "$RUNROOT/dist" 2>&1 | tail -3; echo "uv build exit=${PIPESTATUS[0]}"
  echo "pytest -m integration: NOT RUN (exige o Redis de serviço do CI; ausente no PC 2)"
  echo "# git status after: $(git status --porcelain | wc -l) entries"; git status --porcelain
  echo "# done $(date -u +%FT%TZ)"
} > "$LOG" 2>&1
tail -6 "$LOG"
