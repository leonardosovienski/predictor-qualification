#!/usr/bin/env bash
# integration-stocks: runtime suportado (C3.1) — venvs limpos, só com as wheels publicadas dos final_commits.
#
#   CAIN        : dependências exportadas do uv.lock do cain no commit final (--require-hashes); o protocolo, o transporte,
#                 o snapshot e o bundle vêm do registro STACK_WHEELS.json do cain (fetch pela API + sha256, D-32) + a wheel
#                 publicada do cain (--no-deps, sha256).
#   consumidor  : dependências exportadas do uv.lock do stocks-predictor no commit final (--all-extras, como na Etapa A;
#                 Core e Ops pelas URLs das releases) + as wheels publicadas do Stocks, do transporte e do protocolo
#                 (--no-deps, sha256 conferido antes de instalar).
#   cripto      : só com INTEGRATED=1 (isolamento contra o cripto pelo runtime integrado, prompt do Stocks §4): o mesmo
#                 consumidor do cripto da integration-crypto (wheel rc3) e os dados/operador dela, sem mudança.
# Os lados só conversam pelo spool (arquivos); o venv do CAIN não tem domínio nenhum instalado.
# Dados do Stocks: build_real_panel.py da Etapa A (sem mudança) com o pin do run (URL + sha256 fixados antes, D-16/D-21);
# ambiente de operador com operator_env.py (policy + objetos + painel canário). Sem segredos.
# Linux e Windows (Git Bash do windows-latest, como qualification/stocks/d16/d16_run.sh).
#
# Uso: runtime_env.sh <runtime_targets.json> <SOURCES.json> <work> <out>   (grava <work>/env.sh)
set -euo pipefail
TARGETS=$1 SOURCES=$2 WORK=$3 OUT=$4
HERE="$(cd "$(dirname "$0")" && pwd)"
QC="$(cd "$HERE/.." && pwd)"
REPO_ROOT="$(cd "$QC/../.." && pwd)"
PY=${PYTHON:-python3.13}
EXE=""; BIN=bin; [ "${OS:-}" = "Windows_NT" ] && { EXE=".exe"; BIN=Scripts; }
# caminhos do env.sh no formato nativo (o Python do Windows não entende /c/... em variável de ambiente)
np() { if [ -n "$EXE" ]; then cygpath -m "$1"; else printf %s "$1"; fi; }
mkdir -p "$WORK" "$OUT"
exec > >(tee -a "$OUT/runtime_env.log") 2>&1
echo "runtime_env run_at=$(date -u +%FT%TZ) host=$(hostname) where=${GITHUB_ACTIONS:+github_actions} os=${OS:-linux} uname=$(uname -srm)"
echo "python=$("$PY" --version 2>&1) uv=$(uv --version) integrated=${INTEGRATED:-0} evidence_commit=$(git -C "$REPO_ROOT" rev-parse HEAD)"
field() { "$PY" -c "import json,sys;d=json.load(open(sys.argv[1]));print(d$1)" "$TARGETS"; }
fetch() {  # url sha256 dest
  curl -sSfL --retry 3 -o "$3" "$1"
  echo "$2  $3" | sha256sum -c -
}
venv() {  # dir req.txt
  "$PY" -m venv "$1"
  "$1/$BIN/python$EXE" -m pip install -q --require-hashes -r "$2"
}
wheel() {  # venv key
  local url sha dest
  url=$(field "['$2']['url']"); sha=$(field "['$2']['sha256']"); dest="$WORK/$(basename "$url")"
  [ -f "$dest" ] || fetch "$url" "$sha" "$dest"
  echo "$sha  $dest" | sha256sum -c -
  "$1/$BIN/python$EXE" -m pip install -q --no-deps "$dest"
}
clone() {  # repo dest commit
  git clone -q "https://github.com/leonardosovienski/$1.git" "$2"
  git -C "$2" -c advice.detachedHead=false checkout -q "$3"
  echo "$1 $(git -C "$2" rev-parse HEAD)"
}
# ---------------------------------------------------------------- CAIN
clone cain "$WORK/cain-src" "$(field "['cain']['commit']")"
# c6 (D-32): o lock do cain fixa as wheels do stack no índice local .stack-wheels/ (STACK_WHEELS.json: repositório, tag,
# asset, sha256); `fetch` baixa pela API e confere o sha256; `requirements` acrescenta --hash às linhas do stack, e o pip
# instala tudo com --require-hashes, achando as wheels do stack só no índice local (--find-links).
( cd "$WORK/cain-src" && uv run --no-project python tools/stack_wheels.py fetch && uv run --no-project python tools/stack_wheels.py check )
( cd "$WORK/cain-src" && uv export --locked --no-dev --no-emit-project --format requirements-txt -o "$WORK/cain-req-nostack.txt" -q \
  && "$PY" tools/stack_wheels.py requirements --project . --input "$WORK/cain-req-nostack.txt" --output "$WORK/cain-req.txt" )
( cd "$WORK/cain-src/.stack-wheels" && sha256sum *.whl | tee "$OUT/stack_wheels_cain.sha256" )
"$PY" -m venv "$WORK/cain-venv"
"$WORK/cain-venv/$BIN/python$EXE" -m pip install -q --require-hashes --find-links "$(np "$WORK/cain-src/.stack-wheels")" -r "$WORK/cain-req.txt"
wheel "$WORK/cain-venv" cain
"$WORK/cain-venv/$BIN/python$EXE" -m pip check
"$WORK/cain-venv/$BIN/python$EXE" -m pip freeze > "$OUT/pip_freeze_cain.txt"
# ---------------------------------------------------------------- consumidor do Stocks
clone stocks-predictor "$WORK/stocks-src" "$(field "['stocks']['commit']")"
( cd "$WORK/stocks-src" && uv export --locked --all-extras --no-emit-project --format requirements-txt -o "$WORK/stocks-req.txt" -q )
venv "$WORK/consumer-venv" "$WORK/stocks-req.txt"
for key in stocks transport protocol; do wheel "$WORK/consumer-venv" "$key"; done
"$WORK/consumer-venv/$BIN/python$EXE" -m pip check
"$WORK/consumer-venv/$BIN/python$EXE" -m pip freeze > "$OUT/pip_freeze_consumer.txt"
# the CAIN side must not have any domain package installed
for pkg in stocks_predictor GarimpoInvestimentos; do
  if "$WORK/cain-venv/$BIN/python$EXE" -c "import $pkg" 2>/dev/null; then echo "CAIN venv has $pkg installed"; exit 3; fi
done
# tree of the domain final commit without the package (conformance + adapter tests, readiness matrix)
mkdir -p "$WORK/stocks-tree"
git -C "$WORK/stocks-src" archive --format=tar HEAD | tar -x -C "$WORK/stocks-tree"
rm -rf "$WORK/stocks-tree/stocks_predictor"
CPY="$WORK/consumer-venv/$BIN/python$EXE"
mkdir -p "$WORK/elsewhere"
( cd "$WORK/elsewhere" && "$CPY" -I -c "import stocks_predictor, stocks_predictor.adapters.research_v2 as a, research_transport.adapters as t, importlib.metadata as m
print('stocks', m.version('stocks-predictor'), stocks_predictor.__file__)
print('transport', m.version('predictor-research-transport'), sorted(t.ADAPTERS))
print('adapter', a.identity())
assert 'site-packages' in stocks_predictor.__file__" )
# ---------------------------------------------------------------- painel real (pin do run) + operador
export PYTHONUTF8=1
cp "$SOURCES" "$OUT/SOURCES.json"
( cd "$WORK/elsewhere" && "$CPY" -I "$REPO_ROOT/qualification/stocks/d16/build_real_panel.py" build "$WORK/cache" "$SOURCES" "$WORK/panel" ) > "$OUT/build_real_panel.log" 2>&1 \
  || { echo "PANEL_BUILD_FAILED"; tail -20 "$OUT/build_real_panel.log"; exit 3; }
cp "$WORK/panel/BUILD_MANIFEST.json" "$OUT/BUILD_MANIFEST.json"
( cd "$WORK/elsewhere" && "$CPY" -I "$REPO_ROOT/qualification/stocks/d16/verify_prefilter.py" "$WORK/panel/panel.json" "$WORK/panel/panel_full.json" \
    "$REPO_ROOT/qualification/stocks/d16/PROTOCOL_REAL.json" "$OUT/verify_prefilter.json" ) > "$OUT/verify_prefilter.log" 2>&1 \
  || { echo "PREFILTER_CHANGED_UNIVERSE"; exit 3; }
rm -f "$WORK/panel/panel_full.json"
mkdir -p "$WORK/op"
( cd "$WORK/elsewhere" && "$CPY" -I "$HERE/operator_env.py" "$WORK/op" "$WORK/panel" "$REPO_ROOT/qualification/stocks/d16/PROTOCOL_REAL.json" \
    "$WORK/stocks-tree/EXTERNAL_INTELLIGENCE_TRIAL_READINESS_MATRIX.json" ) > "$OUT/operator_env.json"
cp "$WORK/op/REAL_ENV.json" "$OUT/REAL_ENV.json"; cp "$WORK/op/policy.json" "$OUT/policy.json"
cat > "$WORK/env.sh" <<ENV
export CAIN_BIN="$(np "$WORK/cain-venv/$BIN/cain$EXE")"
export CAIN_PY="$(np "$WORK/cain-venv/$BIN/python$EXE")"
export CONSUMER_BIN="$(np "$WORK/consumer-venv/$BIN/predictor-research-consumer$EXE")"
export CONSUMER_PY="$(np "$CPY")"
export STOCKS_RESEARCH_BIN="$(np "$WORK/consumer-venv/$BIN/stocks-research$EXE")"
export OP_POLICY="$(np "$WORK/op/policy.json")"
export OP_OBJECTS="$(np "$WORK/op/objects")"
export REAL_ENV="$(np "$WORK/op/REAL_ENV.json")"
export STOCKS_TREE="$(np "$WORK/stocks-tree")"
ENV
# ---------------------------------------------------------------- cripto integrado (isolamento pelo runtime integrado)
if [ "${INTEGRATED:-0}" = 1 ]; then
  clone cripto-predictor "$WORK/cripto-src" "$(field "['cripto']['commit']")"
  ( cd "$WORK/cripto-src" && uv export --locked --all-extras --no-emit-project --format requirements-txt -o "$WORK/cripto-req.txt" -q )
  venv "$WORK/crypto-venv" "$WORK/cripto-req.txt"
  for key in cripto transport protocol; do wheel "$WORK/crypto-venv" "$key"; done
  "$WORK/crypto-venv/$BIN/python$EXE" -m pip check
  "$WORK/crypto-venv/$BIN/python$EXE" -m pip freeze > "$OUT/pip_freeze_crypto.txt"
  XPY="$WORK/crypto-venv/$BIN/python$EXE"
  "$XPY" "$REPO_ROOT/qualification/crypto/scripts/build_real_dataset.py" "$WORK/crypto-data" > "$OUT/crypto_build_real_dataset.log" 2>&1
  mkdir -p "$WORK/crypto-op"
  ( cd "$WORK" && "$XPY" -I "$REPO_ROOT/qualification/integration-crypto/scripts/operator_env.py" "$WORK/crypto-op" "$WORK/crypto-data" ) > "$OUT/crypto_operator_env.json"
  cat >> "$WORK/env.sh" <<ENV
export CRYPTO_CONSUMER_BIN="$WORK/crypto-venv/$BIN/predictor-research-consumer$EXE"
export CRIPTO_RESEARCH_BIN="$WORK/crypto-venv/$BIN/cripto-research$EXE"
export CRYPTO_OP_POLICY="$WORK/crypto-op/policy.json"
export CRYPTO_OP_OBJECTS="$WORK/crypto-op/objects"
ENV
fi
cat "$WORK/env.sh"
echo "runtime_env done $(date -u +%FT%TZ)"
