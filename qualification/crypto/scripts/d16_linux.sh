#!/usr/bin/env bash
# Missão crypto, D-16: os 5 gates que exigem dados reais no Linux primário
# (E2E, SOAK, CRYPTO_UNCOMFORTABLE_CASES, CRYPTO_ECONOMIC_METRICS, CRYPTO_NEGATIVE_CONTROLS).
#
# TRAVA: só roda se qualification/DECISIONS.json (no checkout deste repo) tiver D-16 APPROVED.
# Alvo: qualification/crypto/runtime_target.json (final_commit + wheel publicada com sha256).
# Dados: Binance data.vision públicos, baixados aqui e conferidos contra o .CHECKSUM publicado
# (build_real_dataset.py); ficam fora do repositório (D-11). Sem segredos.
#
# Uso: d16_linux.sh <out_dir> [data_dir]
#   out_dir   evidência bruta (copiar depois para qualification/crypto/RAW_LOGS/d16/)
#   data_dir  onde gravar/reusar os dados reais (padrão: $HOME/qualificacao/data/binance-um-btcusdt)
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/../../.." && pwd)"
OUT="$1"; DATA="${2:-$HOME/qualificacao/data/binance-um-btcusdt}"
mkdir -p "$OUT" "$DATA"; OUT="$(cd "$OUT" && pwd)"; DATA="$(cd "$DATA" && pwd)"
fail() { echo "SETUP FAIL: $*" | tee -a "$OUT/env.log"; exit 3; }

# 0) trava da decisão
python3 - "$REPO/qualification/DECISIONS.json" <<'EOF' || { echo "BLOCKED: D-16 não está APPROVED em qualification/DECISIONS.json" | tee "$OUT/env.log"; exit 4; }
import json, sys
d = json.load(open(sys.argv[1], encoding="utf-8"))
ok = any(x.get("decision_id") == "D-16" and x.get("status") == "APPROVED" for x in d["decisions"])
sys.exit(0 if ok else 1)
EOF
T="$REPO/qualification/crypto/runtime_target.json"
COMMIT=$(python3 -c "import json;print(json.load(open('$T'))['commit'])")
WHEEL_URL=$(python3 -c "import json;print(json.load(open('$T'))['wheel_url'])")
WHEEL_SHA=$(python3 -c "import json;print(json.load(open('$T'))['wheel_sha256'])")
{ echo "d16 where=$([ -n "${GITHUB_ACTIONS:-}" ] && echo github_actions || echo cloud_vm) commit=$COMMIT wheel=$WHEEL_URL sha256=$WHEEL_SHA data=$DATA date=$(date -u +%FT%TZ) uname=$(uname -a)"
  grep -h '"D-16"' -A4 "$REPO/qualification/DECISIONS.json"; uv --version; } > "$OUT/env.log" 2>&1 || fail "uv ausente (rode provision_linux_vm.sh)"
[ "$(uname -s)" = Linux ] || fail "Linux obrigatório (host primário)"

WORK="$(mktemp -d)"
git clone -q https://github.com/leonardosovienski/cripto-predictor.git "$WORK/src" || fail clone
git -C "$WORK/src" checkout -q "$COMMIT" || fail checkout
( cd "$WORK/src" && uv export --locked --all-extras --no-emit-project --format requirements-txt -o "$WORK/req.txt" ) >> "$OUT/env.log" 2>&1 || fail export
mkdir -p "$WORK/tree"; git -C "$WORK/src" archive --format=tar "$COMMIT" | tar -x -C "$WORK/tree"
rm -rf "$WORK/tree/GarimpoInvestimentos"

# 1) runtime suportado: venv limpo, deps do lock com --require-hashes, wheel do Cripto conferida
uv venv "$WORK/venv" --python 3.13 >> "$OUT/env.log" 2>&1 || fail venv
PY="$WORK/venv/bin/python"
"$PY" -m ensurepip >> "$OUT/env.log" 2>&1 || fail ensurepip
"$PY" -m pip install -q --require-hashes -r "$WORK/req.txt" >> "$OUT/env.log" 2>&1 || fail deps
curl -sSfL -o "$WORK/$(basename "$WHEEL_URL")" "$WHEEL_URL" || fail download
( cd "$WORK" && echo "$WHEEL_SHA  $(basename "$WHEEL_URL")" | sha256sum -c - ) >> "$OUT/env.log" 2>&1 || fail "wheel sha256"
"$PY" -m pip install -q --no-deps "$WORK/$(basename "$WHEEL_URL")" >> "$OUT/env.log" 2>&1 || fail install
"$PY" -m pip check >> "$OUT/env.log" 2>&1 || fail "pip check"
"$PY" -m pip freeze > "$OUT/pip_freeze.txt"
mkdir -p "$WORK/e"; cd "$WORK/e"
"$PY" -I "$HERE/core_identity.py" --lock "$WORK/src/uv.lock" --pyproject "$WORK/src/pyproject.toml" > "$OUT/core_identity.json" 2>&1

# 2) dados reais: download + conferência pelo .CHECKSUM publicado (fonte pública, sem versionar)
"$PY" "$HERE/build_real_dataset.py" "$DATA" > "$OUT/build_real_dataset.log" 2>&1 || fail "dados reais"
cp "$DATA/MANIFEST.json" "$OUT/data_MANIFEST.json"
"$PY" "$HERE/real_env.py" "$WORK/r" "$DATA" > "$OUT/real_env.log" 2>&1 || fail real_env

export CRIPTO_ROOT="$WORK/cr"; mkdir -p "$CRIPTO_ROOT/tmp"
export TMP="$CRIPTO_ROOT/tmp" TEMP="$CRIPTO_ROOT/tmp" TMPDIR="$CRIPTO_ROOT/tmp"
# 3) E2E real (entrypoint → término → processo novo relê o mesmo resultado; provenance)
"$PY" "$HERE/e2e_runtime.py" --tests "$WORK/tree/tests" --work "$WORK/e2e" --out "$OUT/e2e_real" --real "$WORK/r" > "$OUT/e2e_real.log" 2>&1; echo "[exit $?]" >> "$OUT/e2e_real.log"
# 4) casos A/B/C no runtime (B só com o vetor sintético congelado; A e C também no soak real)
"$PY" "$HERE/e2e_runtime.py" --tests "$WORK/tree/tests" --work "$WORK/e2e-syn" --out "$OUT/e2e_cases" > "$OUT/e2e_cases.log" 2>&1; echo "[exit $?]" >> "$OUT/e2e_cases.log"
# 5) métricas econômicas + controles negativos + canário com dados reais
"$PY" "$HERE/science_real.py" --tests "$WORK/tree/tests" --real "$WORK/r" --state "$WORK/rs" --out "$OUT/science" > "$OUT/science.log" 2>&1; echo "[exit $?]" >> "$OUT/science.log"
# 6) soak com o perfil congelado sobre os dados reais
"$PY" "$HERE/soak.py" --tests "$WORK/tree/tests" --work "$WORK/soak" --log "$OUT/soak_real.jsonl" --real "$WORK/r" > "$OUT/soak_real.log" 2>&1; echo "[exit $?]" >> "$OUT/soak_real.log"
# 7) conformidade (sanidade do mesmo runtime)
( cd "$WORK/tree" && "$PY" -m pytest -p no:cacheprovider -q -rA tests/conformance --junitxml="$OUT/conformance.junit.xml" ) > "$OUT/conformance.log" 2>&1; echo "[exit $?]" >> "$OUT/conformance.log"
echo "done $(date -u +%FT%TZ)" >> "$OUT/env.log"
for f in e2e_real e2e_cases science soak_real conformance; do echo "$f: $(tail -1 "$OUT/$f.log")"; done
