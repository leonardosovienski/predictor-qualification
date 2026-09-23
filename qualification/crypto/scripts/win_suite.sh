#!/usr/bin/env bash
# crypto: suíte completa do cripto-predictor no Windows local (secundário, diagnóstico de checkout).
# Método (igual ao job `quality` do ci.yml): uv sync --locked --all-extras; uv build; pytest.
# Isolamento: CRIPTO_ROOT dedicado por execução e TEMP dentro dele (a conftest exige que o
# tmp_path fique dentro de CRIPTO_ROOT; ver FINDINGS CR-F002). Tudo dentro de
# C:\Cripto\qualificacao (regra local). Exige clone sem dist/ (o build desta execução é o único).
# Depois de cada execução o dist/ gerado é movido pelo chamador para a raiz da execução.
# Uso: win_suite.sh <clone> <log> <junit>
set -u
CLONE="$1"; LOG="$2"; JUNIT="$3"
. /c/QUALIFICACAO/tools/uvenv.sh
export UV_CACHE_DIR="C:/Cripto/qualificacao/.uv-cache"
STAMP="$(date -u +%m%dT%H%M%S)"
RUNROOT="C:/Cripto/qualificacao/w/$STAMP"  # curto: MAX_PATH do Windows (layout do Ops)
mkdir -p "$RUNROOT/tmp"
export CRIPTO_ROOT="$RUNROOT" TMP="$RUNROOT/tmp" TEMP="$RUNROOT/tmp" TMPDIR="$RUNROOT/tmp"
export PYRIGHT_PYTHON_CACHE_DIR="C:/Cripto/qualificacao/.pyright-cache"
cd "$CLONE"
{
  echo "# $(date -u +%FT%TZ) commit $(git rev-parse HEAD) dirty_entries=$(git status --porcelain | wc -l) CRIPTO_ROOT=$CRIPTO_ROOT"
  uv --version
  uv sync --locked --all-extras 2>&1; echo "uv sync exit=$?"
  if [ -d dist ]; then echo "dist/ já existe: abortando (não misturar wheels de builds diferentes)"; exit 2; fi
  uv build 2>&1 | tail -3; echo "uv build exit=$?"
  .venv/Scripts/python.exe -c "import sys,platform;print(sys.version,platform.platform())"
  .venv/Scripts/python.exe -m pytest -p no:cacheprovider --junitxml="$(cygpath -w "$JUNIT")" -q 2>&1; echo "pytest exit=$?"
} > "$LOG" 2>&1
tail -3 "$LOG"
