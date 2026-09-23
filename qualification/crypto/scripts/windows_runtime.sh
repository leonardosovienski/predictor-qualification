#!/usr/bin/env bash
# crypto: runtime suportado no Windows local (secundário, D-3: C:\Cripto\qualificacao\runtime\).
# Instalação limpa só com as final_wheels (deps do lock com --require-hashes; wheel do Cripto
# pela URL da release, sha256 conferido). Dados reais só aqui (D-16 pendente para Linux).
# Uso: windows_runtime.sh <out_dir> <cripto_commit> <wheel_url> <wheel_sha256> <clone> <real_data_dir>
set -uo pipefail
OUT="$1"; COMMIT="$2"; WHEEL_URL="$3"; WHEEL_SHA="$4"; CLONE="$5"; DATA="$6"
HERE="$(cd "$(dirname "$0")" && pwd)"
. /c/QUALIFICACAO/tools/uvenv.sh
export UV_CACHE_DIR="C:/Cripto/qualificacao/.uv-cache"
STAMP="$(date -u +%m%dT%H%M)"
RT="C:/Cripto/qualificacao/runtime/f$STAMP"       # curto: MAX_PATH (layout do Ops)
mkdir -p "$OUT" "$RT/tmp"; OUT="$(cd "$OUT" && pwd)"
export TMP="$RT/tmp" TEMP="$RT/tmp" TMPDIR="$RT/tmp" CRIPTO_ROOT="$RT"
fail() { echo "SETUP FAIL: $*" >> "$OUT/env.log"; exit 3; }
{ echo "commit=$COMMIT wheel=$WHEEL_URL sha256=$WHEEL_SHA runtime=$RT date=$(date -u +%FT%TZ)"; uv --version; } > "$OUT/env.log" 2>&1

# árvore de testes e lock do final_commit (bytes do git, sem o pacote-fonte)
mkdir -p "$RT/src" "$RT/tree"
git -C "$CLONE" -c core.autocrlf=false archive --format=tar "$COMMIT" tests pyproject.toml uv.lock | tar -x -C "$RT/src" || fail archive
cp -r "$RT/src/tests" "$RT/src/pyproject.toml" "$RT/tree/"
( cd "$RT/src" && uv export --locked --all-extras --no-emit-project --format requirements-txt -o "$RT/req.txt" ) >> "$OUT/env.log" 2>&1 || fail export

uv venv "$RT/v" --python /c/QUALIFICACAO/tools/python/cpython-3.13.14-windows-x86_64-none/python.exe >> "$OUT/env.log" 2>&1 || fail venv
PY="$RT/v/Scripts/python.exe"
"$PY" -m ensurepip >> "$OUT/env.log" 2>&1 || fail ensurepip
"$PY" -m pip install -q --require-hashes -r "$RT/req.txt" >> "$OUT/env.log" 2>&1 || fail deps
curl -sSfL -o "$RT/$(basename "$WHEEL_URL")" "$WHEEL_URL" || fail download
( cd "$RT" && echo "$WHEEL_SHA  $(basename "$WHEEL_URL")" | sha256sum -c - ) >> "$OUT/env.log" 2>&1 || fail "wheel sha256"
"$PY" -m pip install -q --no-deps "$RT/$(basename "$WHEEL_URL")" >> "$OUT/env.log" 2>&1 || fail install
"$PY" -m pip check >> "$OUT/env.log" 2>&1 || fail "pip check"
"$PY" -m pip freeze > "$OUT/pip_freeze.txt"

mkdir -p "$RT/e"
( cd "$RT/e" && "$PY" -I "$HERE/core_identity.py" --lock "$RT/src/uv.lock" --pyproject "$RT/src/pyproject.toml" ) > "$OUT/core_identity.json" 2>&1
( cd "$RT/e" && "$PY" -I "$HERE/runtime_modules.py" cripto-predictor cripto-research --help ) > "$OUT/runtime_trace.log" 2>&1

# conformidade (inclui falhas, restart e corrupção) e suítes temporais sobre a wheel instalada
( cd "$RT/tree" && "$PY" -m pytest -p no:cacheprovider -q -rA tests/conformance --junitxml="$OUT/conformance.junit.xml" ) > "$OUT/conformance.log" 2>&1; echo "[exit $?]" >> "$OUT/conformance.log"
( cd "$RT/tree" && "$PY" -m pytest -p no:cacheprovider -q -rA tests/test_dpl*.py tests/test_v3_wfa_purge_contract.py tests/test_permutation_placebo_control.py tests/test_pbo.py tests/test_gate_power.py --junitxml="$OUT/temporal_suites.junit.xml" ) > "$OUT/temporal_suites.log" 2>&1; echo "[exit $?]" >> "$OUT/temporal_suites.log"

# dados reais: ambiente do operador, E2E + restart + releitura, canário, ablações, placebo
( cd "$RT/e" && "$PY" "$HERE/real_env.py" "$RT/r" "$DATA" ) > "$OUT/real_env.log" 2>&1 || fail real_env
( cd "$RT/e" && "$PY" "$HERE/e2e_runtime.py" --tests "$RT/tree/tests" --work "$RT/rw" --out "$OUT/e2e_real" --real "$RT/r" ) > "$OUT/e2e_real.log" 2>&1; echo "[exit $?]" >> "$OUT/e2e_real.log"
( cd "$RT/e" && "$PY" "$HERE/science_real.py" --tests "$RT/tree/tests" --real "$RT/r" --state "$RT/rs" --out "$OUT/science" ) > "$OUT/science.log" 2>&1; echo "[exit $?]" >> "$OUT/science.log"
echo "done $(date -u +%FT%TZ)" >> "$OUT/env.log"
