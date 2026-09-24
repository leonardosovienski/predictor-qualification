#!/usr/bin/env bash
# stocks: runtime limpo (C3.1/C5) — instalação só com o lock exportado (--require-hashes) e a wheel
# do stocks-predictor, fora do checkout. Alvo em qualification/stocks/runtime_target.json.
#   mode=baseline  → DIAGNÓSTICO: wheel construída do commit (não existe wheel publicada do HEAD)
#   mode=final     → wheel publicada (URL da release + sha256): cleanroom-final, e2e,
#                    idempotência/falhas (conformidade), soak diagnóstico (D-16)
# Uso: runtime_cleanroom.sh <out_dir> <soak:0|1>
set -uo pipefail
OUT="$1"; SOAK="${2:-0}"
HERE="$(cd "$(dirname "$0")" && pwd)"; TARGET="$HERE/../runtime_target.json"
mkdir -p "$OUT"; OUT="$(cd "$OUT" && pwd)"
EXE=""; [ "${OS:-}" = "Windows_NT" ] && EXE=".exe"
if [ -n "$EXE" ]; then mkdir -p /c/q; export TMPDIR=/c/q; fi   # raiz curta (MAX_PATH)
WORK="$(mktemp -d)"
BIN=bin; [ -n "$EXE" ] && BIN=Scripts
j() { python3 -c "import json,sys;print(json.load(open(sys.argv[1]))[sys.argv[2]] or '')" "$TARGET" "$1" 2>/dev/null || python -c "import json,sys;print(json.load(open(sys.argv[1]))[sys.argv[2]] or '')" "$TARGET" "$1"; }
MODE="$(j mode)"; COMMIT="$(j commit)"; WHEEL_URL="$(j wheel_url)"; WHEEL_SHA="$(j wheel_sha256)"
fail() { echo "SETUP FAIL: $*" >> "$OUT/env.log"; exit 3; }
{
  echo "mode=$MODE commit=$COMMIT wheel=$WHEEL_URL sha256=$WHEEL_SHA date=$(date -u +%FT%TZ) uname=$(uname -a)"
  uv --version
  cat "$TARGET"
} > "$OUT/env.log" 2>&1

# 1) fonte só para o lock e para a árvore de testes (sem o pacote-fonte stocks_predictor/)
git clone -q https://github.com/leonardosovienski/stocks-predictor.git "$WORK/src" >> "$OUT/env.log" 2>&1 || fail clone
git -C "$WORK/src" -c advice.detachedHead=false checkout -q "$COMMIT" >> "$OUT/env.log" 2>&1 || fail checkout
( cd "$WORK/src" && uv lock --check ) > "$OUT/uv_lock_check.log" 2>&1; echo "[exit $?]" >> "$OUT/uv_lock_check.log"
( cd "$WORK/src" && uv export --locked --all-extras --no-emit-project --format requirements-txt -o "$WORK/req.txt" ) >> "$OUT/env.log" 2>&1 || fail export
cp "$WORK/req.txt" "$OUT/requirements.locked.txt"
mkdir -p "$WORK/tree"
git -C "$WORK/src" archive --format=tar "$COMMIT" | tar -x -C "$WORK/tree"
rm -rf "$WORK/tree/stocks_predictor"
[ -e "$WORK/tree/stocks_predictor" ] && fail "package source still in test tree"

# 2) wheel do stocks-predictor
mkdir -p "$WORK/wheel"
if [ "$MODE" = "final" ]; then
  curl -sSfL -o "$WORK/wheel/$(basename "$WHEEL_URL")" "$WHEEL_URL" || fail download
  ( cd "$WORK/wheel" && echo "$WHEEL_SHA  $(basename "$WHEEL_URL")" | sha256sum -c - ) >> "$OUT/env.log" 2>&1 || fail "wheel sha256"
else
  echo "DIAGNOSTIC: wheel construída do commit (não publicada)" >> "$OUT/env.log"
  ( cd "$WORK/src" && uv build --wheel -o "$WORK/wheel" ) >> "$OUT/env.log" 2>&1 || fail build
fi
WHEEL="$(ls "$WORK"/wheel/*.whl)"; sha256sum "$WHEEL" > "$OUT/stocks_wheel.sha256"

# 3) venv limpo: dependências do lock com --require-hashes; wheel do Stocks sem deps
uv venv "$WORK/venv" --python 3.13 >> "$OUT/env.log" 2>&1 || fail venv
PY="$WORK/venv/$BIN/python$EXE"
"$PY" -m ensurepip >> "$OUT/env.log" 2>&1 || fail ensurepip
"$PY" -m pip install -q --require-hashes -r "$WORK/req.txt" >> "$OUT/env.log" 2>&1 || fail deps
"$PY" -m pip install -q --no-deps "$WHEEL" >> "$OUT/env.log" 2>&1 || fail install
"$PY" -m pip check >> "$OUT/env.log" 2>&1 || fail "pip check"
"$PY" -m pip freeze > "$OUT/pip_freeze.txt" 2>&1
"$PY" -m pip list -v > "$OUT/pip_list_v.txt" 2>&1

# 4) identidade (C4) e trace em runtime (C2/C3.1), de um diretório fora de tudo
mkdir -p "$WORK/elsewhere"
( cd "$WORK/elsewhere" && "$PY" -I "$HERE/core_identity.py" --lock "$WORK/src/uv.lock" --pyproject "$WORK/src/pyproject.toml" ) > "$OUT/core_identity.json" 2>&1
( cd "$WORK/elsewhere" && "$PY" -I "$HERE/runtime_modules.py" -m stocks_predictor doctor --check ) > "$OUT/runtime_trace.log" 2>&1
if [ "$MODE" = "final" ]; then
  ( cd "$WORK/elsewhere" && "$PY" -I "$HERE/runtime_modules.py" stocks-predictor stocks-research --help ) >> "$OUT/runtime_trace.log" 2>&1
fi
export PYTHONUTF8=1

# 5) suíte sobre a wheel instalada (árvore sem stocks_predictor/)
( cd "$WORK/tree" && "$PY" -c "import stocks_predictor,sys;print('stocks_predictor', stocks_predictor.__file__)" ) >> "$OUT/env.log" 2>&1
if [ -d "$WORK/tree/tests/conformance" ]; then
  ( cd "$WORK/tree" && "$PY" -m pytest -p no:cacheprovider -q -rA tests/conformance --junitxml="$OUT/conformance.junit.xml" ) > "$OUT/conformance.log" 2>&1
  echo "[exit $?]" >> "$OUT/conformance.log"
fi
( cd "$WORK/tree" && "$PY" -m pytest -p no:cacheprovider -q -rfE tests --junitxml="$OUT/full_suite.junit.xml" ) > "$OUT/full_suite.log" 2>&1
echo "[exit $?]" >> "$OUT/full_suite.log"

# 6) baseline: checagem extra do conjunto protegido (prompt §5), em cópia descartável
if [ "$MODE" = "baseline" ]; then
  mkdir -p "$WORK/verify" && git -C "$WORK/src" archive --format=tar "$COMMIT" | tar -x -C "$WORK/verify"
  for s in verify_history_protected verify_real_protected; do
    ( cd "$WORK/verify/research/session-20260907/scripts" && "$PY" "$s.py" ) > "$OUT/$s.log" 2>&1
    echo "[exit $?]" >> "$OUT/$s.log"
  done
fi

# 7) final: E2E pelo entrypoint instalado e soak (diagnóstico com fixture até a D-16)
if [ "$MODE" = "final" ]; then
  ( cd "$WORK/elsewhere" && "$PY" "$HERE/e2e_runtime.py" --tests "$WORK/tree/tests" --work "$WORK/e2e" --out "$OUT/e2e" ) > "$OUT/e2e.log" 2>&1
  echo "[exit $?]" >> "$OUT/e2e.log"
  if [ "$SOAK" = "1" ]; then
    ( cd "$WORK/elsewhere" && "$PY" "$HERE/soak.py" --tests "$WORK/tree/tests" --work "$WORK/soak" --log "$OUT/soak.jsonl" ) > "$OUT/soak.log" 2>&1
    echo "[exit $?]" >> "$OUT/soak.log"
  fi
fi
echo "done $(date -u +%FT%TZ)" >> "$OUT/env.log"
