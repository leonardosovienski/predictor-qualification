#!/usr/bin/env bash
# brasileirao: suíte completa do brasileirao-predictor no Windows local (secundário; diagnóstico de checkout).
# Método = job `python` do ci.yml, menos o que exige Redis de serviço (pytest -m integration) e o
# coverage: uv sync --locked --all-extras; seed_test_fixtures; ruff check/format; pyright; pytest; uv build.
# Isolamento: TEMP e runtime dentro de C:\QUALIFICACAO\runtime\brasileirao\w\<stamp> (curto: MAX_PATH).
# Uso: win_suite.sh <clone> <log> <junit>
set -u
CLONE="$1"; LOG="$2"; JUNIT="$3"
. /c/QUALIFICACAO/tools/uvenv.sh
export PYTHONIOENCODING=utf-8
STAMP="$(date -u +%m%dT%H%M%S)"
RUNROOT="C:/QUALIFICACAO/runtime/brasileirao/w/$STAMP"
mkdir -p "$RUNROOT/tmp"
export TMP="$RUNROOT/tmp" TEMP="$RUNROOT/tmp" TMPDIR="$RUNROOT/tmp"
export PYRIGHT_PYTHON_CACHE_DIR="C:/QUALIFICACAO/tools/pyright-cache"
cd "$CLONE"
{
  echo "# $(date -u +%FT%TZ) commit $(git rev-parse HEAD) dirty_entries=$(git status --porcelain | wc -l) RUNROOT=$RUNROOT"
  uv --version
  uv sync --locked --all-extras 2>&1; echo "uv sync exit=$?"
  .venv/Scripts/python.exe -c "import sys,platform;print(sys.version,platform.platform())"
  .venv/Scripts/python.exe -c "import predictor_core,predictor_ops,importlib.metadata as m;print('core',m.version('predictor-core'),predictor_core.__file__);print('ops',m.version('predictor-ops'),predictor_ops.__file__)"
  uv run --locked python brasileirao_scripts/validate_env_example.py 2>&1; echo "validate_env_example exit=$?"
  uv run --locked python brasileirao_scripts/seed_test_fixtures.py 2>&1; echo "seed_test_fixtures exit=$?"
  uv run --locked ruff check brasileirao_predictor brasileirao_scripts tests 2>&1 | tail -5; echo "ruff check exit=${PIPESTATUS[0]}"
  uv run --locked ruff format --check brasileirao_predictor brasileirao_scripts tests 2>&1 | tail -5; echo "ruff format exit=${PIPESTATUS[0]}"
  uv run --locked pyright brasileirao_predictor 2>&1 | tail -5; echo "pyright exit=${PIPESTATUS[0]}"
  .venv/Scripts/python.exe -m pytest -p no:cacheprovider --junitxml="$(cygpath -w "$JUNIT")" -q -o addopts="" -m "not integration" 2>&1 | tail -60; echo "pytest exit=${PIPESTATUS[0]}"
  echo "# git status after: $(git status --porcelain | wc -l) entries"; git status --porcelain
} > "$LOG" 2>&1
tail -4 "$LOG"
