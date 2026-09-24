#!/usr/bin/env bash
# stocks: suíte completa do stocks-predictor num commit (antes/depois de cada mudança).
# Uso: suite.sh <out_dir>   (alvo em qualification/stocks/suite_target.json)
# Instala só pelo lock (uv sync --locked --all-extras); nada fora do lock. Log bruto sem edição.
set -uo pipefail
OUT="$1"; HERE="$(cd "$(dirname "$0")" && pwd)"; TARGET="$HERE/../suite_target.json"
mkdir -p "$OUT"; OUT="$(cd "$OUT" && pwd)"
COMMIT="$(sed -n 's/.*"commit": *"\([0-9a-f]\{40\}\)".*/\1/p' "$TARGET")"
WORK="$(mktemp -d)"
{
  echo "commit=$COMMIT date=$(date -u +%FT%TZ) uname=$(uname -a) runner_os=${RUNNER_OS:-?}"
  uv --version
  cat "$TARGET"
} > "$OUT/env.log" 2>&1
git clone -q https://github.com/leonardosovienski/stocks-predictor.git "$WORK/src" >> "$OUT/env.log" 2>&1 || { echo "SETUP FAIL clone" >> "$OUT/env.log"; exit 3; }
git -C "$WORK/src" -c advice.detachedHead=false checkout -q "$COMMIT" >> "$OUT/env.log" 2>&1 || { echo "SETUP FAIL checkout" >> "$OUT/env.log"; exit 3; }
git -C "$WORK/src" rev-parse HEAD > "$OUT/head.txt"
cd "$WORK/src"
( uv lock --check ) > "$OUT/uv_lock_check.log" 2>&1; echo "[exit $?]" >> "$OUT/uv_lock_check.log"
( uv sync --locked --all-extras --python 3.13 ) > "$OUT/uv_sync.log" 2>&1; rc=$?; echo "[exit $rc]" >> "$OUT/uv_sync.log"
[ $rc -ne 0 ] && { echo "SETUP FAIL uv sync" >> "$OUT/env.log"; exit 3; }
uv pip list --python .venv > "$OUT/pip_list.txt" 2>&1
export PYTHONUTF8=1
( uv run --no-sync python -m pytest -q -rfE -p no:cacheprovider --durations=15 --junitxml="$OUT/junit.xml" ) > "$OUT/pytest.log" 2>&1
echo "[exit $?]" >> "$OUT/pytest.log"
( uv run --no-sync python main.py doctor --check ) > "$OUT/doctor.log" 2>&1; echo "[exit $?]" >> "$OUT/doctor.log"
echo "done $(date -u +%FT%TZ)" >> "$OUT/env.log"
