#!/usr/bin/env bash
# SHARED-003 / SHARED-004 (missão crypto, fase ops-failure): matriz congelada em
# qualification/crypto/FROZEN_PARAMETERS.json (shared_003.matrix, shared_004.matrix).
# Um log bruto por execução. Sem segredos; só repos e releases públicos.
#
# Uso: ops_failure_matrix.sh <source|wheel> <out_dir> <runs_003> <runs_004> [full_suite:0|1]
set -uo pipefail

MODE="$1"; OUT="$2"; RUNS3="$3"; RUNS4="$4"; FULL="${5:-1}"
OPS_COMMIT=7bd99ebaea09c74a2ac4243d8991a81c44625a6c
WHEEL_URL=https://github.com/leonardosovienski/predictor-ops/releases/download/v4.2.1/predictor_ops-4.2.1-py3-none-any.whl
WHEEL_SHA=da4fa540703879669caba919521ec7d3c33734b5d57781122823df8817346f0e
T3='tests_v2/test_runner.py::test_timeout_and_truncation'
T4=('tests_v2/test_provenance.py::test_source_clean_dirty_detached_and_missing_commit'
    'tests_v2/test_provenance.py::test_strict_editable_fails_closed_and_permissive_is_safe'
    'tests_v2/test_runner_extended.py::test_strict_setup_failure_is_terminal_and_child_never_runs')
PROBE="$(cd "$(dirname "$0")" && pwd)/ops_timeout_probe.py"
EXE=""; [ "${OS:-}" = "Windows_NT" ] && EXE=".exe"
mkdir -p "$OUT"
OUT="$(cd "$OUT" && pwd)"
WORK="$(mktemp -d)"

{
  echo "mode=$MODE ops_commit=$OPS_COMMIT date=$(date -u +%FT%TZ) uname=$(uname -a)"
  uv --version
} > "$OUT/env.log" 2>&1

git clone -q https://github.com/leonardosovienski/predictor-ops.git "$WORK/ops" >> "$OUT/env.log" 2>&1
git -C "$WORK/ops" checkout -q "$OPS_COMMIT" >> "$OUT/env.log" 2>&1
git -C "$WORK/ops" rev-parse HEAD >> "$OUT/env.log"

if [ "$MODE" = "source" ]; then
  ( cd "$WORK/ops" && uv sync --locked --python 3.13 --all-extras ) >> "$OUT/env.log" 2>&1 || { echo "SETUP FAIL uv sync" >> "$OUT/env.log"; exit 3; }
  TREE="$WORK/ops"
  if [ -n "$EXE" ]; then PY="$TREE/.venv/Scripts/python.exe"; else PY="$TREE/.venv/bin/python"; fi
else
  ( cd "$WORK/ops" && uv export --locked --all-extras --no-emit-project --format requirements-txt -o "$WORK/req.txt" ) >> "$OUT/env.log" 2>&1
  uv venv "$WORK/venv" --python 3.13 >> "$OUT/env.log" 2>&1
  if [ -n "$EXE" ]; then PY="$WORK/venv/Scripts/python.exe"; else PY="$WORK/venv/bin/python"; fi
  "$PY" -m ensurepip >> "$OUT/env.log" 2>&1 || { echo "SETUP FAIL ensurepip" >> "$OUT/env.log"; exit 3; }
  "$PY" -m pip install -q --require-hashes -r "$WORK/req.txt" >> "$OUT/env.log" 2>&1 || { echo "SETUP FAIL deps" >> "$OUT/env.log"; exit 3; }
  curl -sSfL -o "$WORK/predictor_ops-4.2.1-py3-none-any.whl" "$WHEEL_URL"
  ( cd "$WORK" && echo "$WHEEL_SHA  predictor_ops-4.2.1-py3-none-any.whl" | sha256sum -c - ) >> "$OUT/env.log" 2>&1 || { echo "WHEEL SHA MISMATCH" >> "$OUT/env.log"; exit 3; }
  "$PY" -m pip install -q --no-deps "$WORK/predictor_ops-4.2.1-py3-none-any.whl" >> "$OUT/env.log" 2>&1 || { echo "SETUP FAIL wheel" >> "$OUT/env.log"; exit 3; }
  # árvore de teste sem src/: os testes só podem importar a wheel instalada
  mkdir -p "$WORK/tree"
  cp -r "$WORK/ops/tests_v2" "$WORK/ops/pyproject.toml" "$WORK/tree/"
  [ -d "$WORK/ops/posix_integration" ] && cp -r "$WORK/ops/posix_integration" "$WORK/tree/"
  [ -d "$WORK/ops/windows_integration" ] && cp -r "$WORK/ops/windows_integration" "$WORK/tree/"
  TREE="$WORK/tree"
fi
( cd "$TREE" && "$PY" -c "import predictor_ops,sys;print('predictor_ops', predictor_ops.__file__, sys.version)" ) >> "$OUT/env.log" 2>&1 || { echo "SETUP FAIL import" >> "$OUT/env.log"; exit 3; }
( cd "$TREE" && "$PY" -m pip freeze 2>/dev/null || true ) >> "$OUT/env.log"

run_one() {  # label, index, test ids...
  local label="$1" i="$2"; shift 2
  local log="$OUT/${label}_run$(printf %02d "$i").log"
  ( cd "$TREE" && "$PY" -m pytest -p no:cacheprovider -q -rA "$@" ) > "$log" 2>&1
  echo "[exit $?]" >> "$log"
}

for i in $(seq 1 "$RUNS3"); do run_one shared003_test "$i" "$T3"; done
for i in $(seq 1 "$RUNS4"); do run_one shared004_tests "$i" "${T4[@]}"; done
if [ "$FULL" = "1" ]; then run_one full_tests_v2 1 tests_v2; fi

# sondas (run_job real, sem mock): uma linha JSON por execução
for i in $(seq 1 20); do ( cd "$WORK" && "$PY" "$PROBE" startup "$WORK/probe/s$i" ) >> "$OUT/probe_startup.jsonl" 2>>"$OUT/probe_errors.log"; done
for i in $(seq 1 10); do ( cd "$WORK" && "$PY" "$PROBE" test-exact "$WORK/probe/t$i" ) >> "$OUT/probe_test_exact.jsonl" 2>>"$OUT/probe_errors.log"; done
for i in $(seq 1 10); do ( cd "$WORK" && "$PY" "$PROBE" a-b-delay "$WORK/probe/b$i" ) >> "$OUT/probe_a_b_delay.jsonl" 2>>"$OUT/probe_errors.log"; done
for i in $(seq 1 3); do ( cd "$WORK" && "$PY" "$PROBE" real-tree "$WORK/probe/r$i" ) >> "$OUT/probe_real_tree.jsonl" 2>>"$OUT/probe_errors.log"; done
echo "done $(date -u +%FT%TZ)" >> "$OUT/env.log"
