#!/usr/bin/env bash
# stocks, D-16: os 4 gates que exigem dado real (E2E, WINDOWS_SMOKE, SOAK, STOCKS_NEGATIVE_CONTROLS),
# no runtime suportado (C3.1): só as final wheels (stocks v0.3.0rc2 publicada + lock exportado com
# --require-hashes), fora do checkout, pelo entrypoint instalado `stocks-research`.
#
# TRAVA: só roda se qualification/DECISIONS.json (neste checkout) tiver D-16 APPROVED.
# Dados: só públicos, baixados AQUI pela URL oficial e conferidos contra o sha256 fixado em
# qualification/stocks/d16/SOURCES.json (build_real_panel.py falha fechado se divergir). Nem os
# arquivos baixados nem o painel saem do runner (D-11): o artefato leva só logs, manifesto e resultados.
#
# Uso: d16_run.sh <out_dir> <papel>
#   linux-primary   E2E real + soak do perfil congelado + conformidade (ubuntu-latest)
#   linux-controls  controles negativos com as 20 seeds congeladas (ubuntu-latest)
#   windows-latest  E2E real + restart nos pontos de morte + conformidade (WINDOWS_SMOKE, D-1)
set -uo pipefail
OUT="$1"; ROLE="$2"
HERE="$(cd "$(dirname "$0")" && pwd)"; QC="$(cd "$HERE/.." && pwd)"; REPO="$(cd "$QC/../.." && pwd)"
TARGET="$QC/runtime_target.json"
mkdir -p "$OUT"; OUT="$(cd "$OUT" && pwd)"
EXE=""; [ "${OS:-}" = "Windows_NT" ] && EXE=".exe"
if [ -n "$EXE" ]; then mkdir -p /c/q; export TMPDIR=/c/q; fi   # raiz curta (MAX_PATH)
BIN=bin; [ -n "$EXE" ] && BIN=Scripts
SYSPY="$(command -v python3 || command -v python)"
fail() { echo "SETUP FAIL: $*" >> "$OUT/env.log"; exit 3; }
j() { "$SYSPY" -c "import json,sys;print(json.load(open(sys.argv[1]))[sys.argv[2]] or '')" "$TARGET" "$1"; }

# 0) trava da decisão D-16
"$SYSPY" - "$REPO/qualification/DECISIONS.json" <<'EOF' || { echo "BLOCKED: D-16 não está APPROVED em qualification/DECISIONS.json" | tee "$OUT/env.log"; exit 4; }
import json, sys
d = json.load(open(sys.argv[1], encoding="utf-8"))
sys.exit(0 if any(x.get("decision_id") == "D-16" and x.get("status") == "APPROVED" for x in d["decisions"]) else 1)
EOF
MODE="$(j mode)"; COMMIT="$(j commit)"; WHEEL_URL="$(j wheel_url)"; WHEEL_SHA="$(j wheel_sha256)"
{
  echo "d16 role=$ROLE mode=$MODE commit=$COMMIT wheel=$WHEEL_URL sha256=$WHEEL_SHA date=$(date -u +%FT%TZ) uname=$(uname -a)"
  echo "evidence_commit=$(git -C "$REPO" rev-parse HEAD 2>/dev/null)"
  grep -h '"D-16"' -A2 "$REPO/qualification/DECISIONS.json" | head -3
  uv --version
  cat "$TARGET"
} > "$OUT/env.log" 2>&1
[ "$MODE" = "final" ] || fail "runtime_target.json precisa estar em mode=final"
WORK="$(mktemp -d)"

# 1) runtime suportado (o mesmo de runtime_cleanroom.sh, modo final)
git clone -q https://github.com/leonardosovienski/stocks-predictor.git "$WORK/src" >> "$OUT/env.log" 2>&1 || fail clone
git -C "$WORK/src" -c advice.detachedHead=false checkout -q "$COMMIT" >> "$OUT/env.log" 2>&1 || fail checkout
( cd "$WORK/src" && uv lock --check ) > "$OUT/uv_lock_check.log" 2>&1; echo "[exit $?]" >> "$OUT/uv_lock_check.log"
( cd "$WORK/src" && uv export --locked --all-extras --no-emit-project --format requirements-txt -o "$WORK/req.txt" ) >> "$OUT/env.log" 2>&1 || fail export
cp "$WORK/req.txt" "$OUT/requirements.locked.txt"
mkdir -p "$WORK/tree"
git -C "$WORK/src" archive --format=tar "$COMMIT" | tar -x -C "$WORK/tree"
rm -rf "$WORK/tree/stocks_predictor"
[ -e "$WORK/tree/stocks_predictor" ] && fail "package source still in test tree"
mkdir -p "$WORK/wheel"
curl -sSfL -o "$WORK/wheel/$(basename "$WHEEL_URL")" "$WHEEL_URL" || fail download
( cd "$WORK/wheel" && echo "$WHEEL_SHA  $(basename "$WHEEL_URL")" | sha256sum -c - ) >> "$OUT/env.log" 2>&1 || fail "wheel sha256"
WHEEL="$(ls "$WORK"/wheel/*.whl)"; sha256sum "$WHEEL" > "$OUT/stocks_wheel.sha256"
uv venv "$WORK/venv" --python 3.13 >> "$OUT/env.log" 2>&1 || fail venv
PY="$WORK/venv/$BIN/python$EXE"
"$PY" -m ensurepip >> "$OUT/env.log" 2>&1 || fail ensurepip
"$PY" -m pip install -q --require-hashes -r "$WORK/req.txt" >> "$OUT/env.log" 2>&1 || fail deps
"$PY" -m pip install -q --no-deps "$WHEEL" >> "$OUT/env.log" 2>&1 || fail install
"$PY" -m pip check >> "$OUT/env.log" 2>&1 || fail "pip check"
"$PY" -m pip freeze > "$OUT/pip_freeze.txt" 2>&1
mkdir -p "$WORK/elsewhere"
( cd "$WORK/elsewhere" && "$PY" -I "$QC/scripts/core_identity.py" --lock "$WORK/src/uv.lock" --pyproject "$WORK/src/pyproject.toml" ) > "$OUT/core_identity.json" 2>&1
( cd "$WORK/elsewhere" && "$PY" -I "$QC/scripts/runtime_modules.py" stocks-predictor stocks-research --help ) > "$OUT/runtime_trace.log" 2>&1
( cd "$WORK/tree" && "$PY" -c "import stocks_predictor,sys;print('stocks_predictor', stocks_predictor.__file__)" ) >> "$OUT/env.log" 2>&1
export PYTHONUTF8=1

# 2) painel real: download pela URL oficial + sha256 fixado; construção determinística
( cd "$WORK/elsewhere" && "$PY" -I "$HERE/build_real_panel.py" build "$WORK/cache" "$HERE/SOURCES.json" "$WORK/panel" ) > "$OUT/build_real_panel.log" 2>&1
echo "[exit $?]" >> "$OUT/build_real_panel.log"
[ -f "$WORK/panel/BUILD_MANIFEST.json" ] && cp "$WORK/panel/BUILD_MANIFEST.json" "$OUT/BUILD_MANIFEST.json"
grep -q '^\[exit 0\]$' "$OUT/build_real_panel.log" || fail "painel real (ver build_real_panel.log)"
( cd "$WORK/elsewhere" && "$PY" -I "$HERE/verify_prefilter.py" "$WORK/panel/panel.json" "$WORK/panel/panel_full.json" "$HERE/PROTOCOL_REAL.json" "$OUT/verify_prefilter.json" ) > "$OUT/verify_prefilter.log" 2>&1
echo "[exit $?]" >> "$OUT/verify_prefilter.log"
grep -q '^\[exit 0\]$' "$OUT/verify_prefilter.log" || fail "pré-filtro mudou o universo (ver verify_prefilter.json)"
rm -f "$WORK/panel/panel_full.json"
( cd "$WORK/elsewhere" && "$PY" -I "$HERE/real_env.py" "$WORK/real" "$WORK/panel" "$HERE/PROTOCOL_REAL.json" "$WORK/tree/EXTERNAL_INTELLIGENCE_TRIAL_READINESS_MATRIX.json" ) > "$OUT/real_env.log" 2>&1 || fail real_env
cp "$WORK/real/policy.json" "$OUT/policy.json"; cp "$WORK/real/REAL_ENV.json" "$OUT/REAL_ENV.json"

# 3) por papel
case "$ROLE" in
  linux-primary)
    ( cd "$WORK/elsewhere" && "$PY" "$QC/scripts/e2e_runtime.py" --tests "$WORK/tree/tests" --work "$WORK/e2e" --out "$OUT/e2e" --real "$WORK/real" ) > "$OUT/e2e.log" 2>&1
    echo "[exit $?]" >> "$OUT/e2e.log"
    ( cd "$WORK/elsewhere" && "$PY" "$HERE/d16_soak.py" --tests "$WORK/tree/tests" --build "$WORK/panel" --protocol "$HERE/PROTOCOL_REAL.json" \
        --matrix "$WORK/tree/EXTERNAL_INTELLIGENCE_TRIAL_READINESS_MATRIX.json" --work "$WORK/soak" --log "$OUT/soak.jsonl" --profile full ) > "$OUT/soak.log" 2>&1
    echo "[exit $?]" >> "$OUT/soak.log"
    ;;
  linux-controls)
    ( cd "$WORK/elsewhere" && "$PY" "$HERE/d16_science.py" --tests "$WORK/tree/tests" --build "$WORK/panel" --protocol "$HERE/PROTOCOL_REAL.json" \
        --matrix "$WORK/tree/EXTERNAL_INTELLIGENCE_TRIAL_READINESS_MATRIX.json" --work "$WORK/science" --out "$OUT/science" ) > "$OUT/science.log" 2>&1
    echo "[exit $?]" >> "$OUT/science.log"
    ;;
  windows-latest)
    ( cd "$WORK/elsewhere" && "$PY" "$QC/scripts/e2e_runtime.py" --tests "$WORK/tree/tests" --work "$WORK/e2e" --out "$OUT/e2e" --real "$WORK/real" ) > "$OUT/e2e.log" 2>&1
    echo "[exit $?]" >> "$OUT/e2e.log"
    ( cd "$WORK/elsewhere" && "$PY" "$HERE/d16_soak.py" --tests "$WORK/tree/tests" --build "$WORK/panel" --protocol "$HERE/PROTOCOL_REAL.json" \
        --matrix "$WORK/tree/EXTERNAL_INTELLIGENCE_TRIAL_READINESS_MATRIX.json" --work "$WORK/restart" --log "$OUT/restart.jsonl" --profile windows ) > "$OUT/restart.log" 2>&1
    echo "[exit $?]" >> "$OUT/restart.log"
    ;;
  *) fail "papel desconhecido: $ROLE" ;;
esac
if [ "$ROLE" != "linux-controls" ] && [ -d "$WORK/tree/tests/conformance" ]; then
  ( cd "$WORK/tree" && "$PY" -m pytest -p no:cacheprovider -q -rA tests/conformance --junitxml="$OUT/conformance.junit.xml" ) > "$OUT/conformance.log" 2>&1
  echo "[exit $?]" >> "$OUT/conformance.log"
fi
echo "done $(date -u +%FT%TZ)" >> "$OUT/env.log"
for f in build_real_panel verify_prefilter e2e soak science restart conformance; do
  [ -f "$OUT/$f.log" ] && echo "$f: $(tail -1 "$OUT/$f.log")"
done
exit 0
