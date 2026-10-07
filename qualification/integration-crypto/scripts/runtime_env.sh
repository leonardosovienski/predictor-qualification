#!/usr/bin/env bash
# integration-crypto: runtime suportado (C3.1) — dois venvs limpos, só com as wheels publicadas dos final_commits.
#
#   CAIN        : dependências exportadas do uv.lock do cain no commit final (--require-hashes); o protocolo, o transporte,
#                 o snapshot e o bundle vêm do registro STACK_WHEELS.json do cain (fetch pela API + sha256, D-32) + a wheel
#                 publicada do cain (--no-deps, sha256).
#   consumidor  : dependências exportadas do uv.lock do cripto-predictor no commit final (--all-extras, como na
#                 Etapa A; Core e Ops pelas URLs das releases) + as wheels publicadas do cripto, do transporte e do
#                 protocolo (--no-deps, sha256 conferido antes de instalar).
# Os dois lados só conversam pelo spool (arquivos); o venv do CAIN não tem o domínio instalado.
# Dados: build_real_dataset.py da Etapa A (Binance data.vision, .CHECKSUM), fora do repositório; ambiente de operador
# com operator_env.py (policy + objetos de referência). Sem segredos, sem API da Binance.
#
# Linux e Windows (Git Bash do windows-latest, como qualification/integration-stocks/scripts/runtime_env.sh).
#
# Uso: runtime_env.sh <runtime_targets.json> <work> <out>   (imprime as variáveis de ambiente úteis em <work>/env.sh)
set -euo pipefail
TARGETS=$1 WORK=$2 OUT=$3
HERE="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$HERE/../../.." && pwd)"
PY=${PYTHON:-python3.13}
EXE=""; BIN=bin; [ "${OS:-}" = "Windows_NT" ] && { EXE=".exe"; BIN=Scripts; }
# caminhos do env.sh no formato nativo (o Python do Windows não entende /c/... em variável de ambiente)
np() { if [ -n "$EXE" ]; then cygpath -m "$1"; else printf %s "$1"; fi; }
mkdir -p "$WORK" "$OUT"
exec > >(tee -a "$OUT/runtime_env.log") 2>&1
echo "runtime_env run_at=$(date -u +%FT%TZ) host=$(hostname) where=${GITHUB_ACTIONS:+github_actions} os=${OS:-linux} uname=$(uname -srm)"
echo "python=$("$PY" --version 2>&1) uv=$(uv --version)"
field() { "$PY" -c "import json,sys;d=json.load(open(sys.argv[1]));print(d$1)" "$TARGETS"; }  # caminho por argv (MSYS converte)
fetch() {  # url sha256 dest
  curl -sSfL --retry 3 -o "$3" "$1"
  echo "$2  $3" | sha256sum -c -
}
# ---------------------------------------------------------------- CAIN
CAIN_COMMIT=$(field "['cain']['commit']")
git clone -q https://github.com/leonardosovienski/cain.git "$WORK/cain-src"
git -C "$WORK/cain-src" checkout -q "$CAIN_COMMIT"
# rc16 (D-32): o lock do cain fixa as wheels do stack no índice local .stack-wheels/ (STACK_WHEELS.json: repositório,
# tag, asset, sha256); `fetch` baixa pela API e confere o sha256; `requirements` acrescenta --hash às linhas do stack,
# e o pip instala tudo com --require-hashes, achando as wheels do stack só no índice local (--find-links).
( cd "$WORK/cain-src" && uv run --no-project python tools/stack_wheels.py fetch && uv run --no-project python tools/stack_wheels.py check )
( cd "$WORK/cain-src" && uv export --locked --no-dev --no-emit-project --format requirements-txt -o "$WORK/cain-req-nostack.txt" -q \
  && "$PY" tools/stack_wheels.py requirements --project . --input "$WORK/cain-req-nostack.txt" --output "$WORK/cain-req.txt" )
( cd "$WORK/cain-src/.stack-wheels" && sha256sum *.whl | tee "$OUT/stack_wheels_cain.sha256" )
"$PY" -m venv "$WORK/cain-venv"
"$WORK/cain-venv/$BIN/python$EXE" -m pip install -q --require-hashes --find-links "$(np "$WORK/cain-src/.stack-wheels")" -r "$WORK/cain-req.txt"
fetch "$(field "['cain']['url']")" "$(field "['cain']['sha256']")" "$WORK/$(basename "$(field "['cain']['url']")")"
"$WORK/cain-venv/$BIN/python$EXE" -m pip install -q --no-deps "$WORK/$(basename "$(field "['cain']['url']")")"
"$WORK/cain-venv/$BIN/python$EXE" -m pip check
"$WORK/cain-venv/$BIN/python$EXE" -m pip freeze > "$OUT/pip_freeze_cain.txt"
# ---------------------------------------------------------------- consumer + domain
CR_COMMIT=$(field "['cripto']['commit']")
git clone -q https://github.com/leonardosovienski/cripto-predictor.git "$WORK/cripto-src"
git -C "$WORK/cripto-src" checkout -q "$CR_COMMIT"
( cd "$WORK/cripto-src" && uv export --locked --all-extras --no-emit-project --format requirements-txt -o "$WORK/cripto-req.txt" -q )
"$PY" -m venv "$WORK/consumer-venv"
"$WORK/consumer-venv/$BIN/python$EXE" -m pip install -q --require-hashes -r "$WORK/cripto-req.txt"
for key in cripto transport protocol; do
  fetch "$(field "['$key']['url']")" "$(field "['$key']['sha256']")" "$WORK/$(basename "$(field "['$key']['url']")")"
  "$WORK/consumer-venv/$BIN/python$EXE" -m pip install -q --no-deps "$WORK/$(basename "$(field "['$key']['url']")")"
done
"$WORK/consumer-venv/$BIN/python$EXE" -m pip check
"$WORK/consumer-venv/$BIN/python$EXE" -m pip freeze > "$OUT/pip_freeze_consumer.txt"
# the CAIN side must not have any domain package installed
if "$WORK/cain-venv/$BIN/python$EXE" -c "import GarimpoInvestimentos" 2>/dev/null; then echo "CAIN venv has the domain installed"; exit 3; fi
# tests tree of the domain final commit, outside the package (for the conformance suite, C24.3 c)
mkdir -p "$WORK/cripto-tests" && cp -r "$WORK/cripto-src/tests/." "$WORK/cripto-tests/"
# ---------------------------------------------------------------- data + operator environment
"$WORK/consumer-venv/$BIN/python$EXE" "$REPO_ROOT/qualification/crypto/scripts/build_real_dataset.py" "$WORK/data" > "$OUT/build_real_dataset.log" 2>&1
cp "$WORK/data/MANIFEST.json" "$OUT/data_MANIFEST.json"
mkdir -p "$WORK/op"
( cd "$WORK" && "$WORK/consumer-venv/$BIN/python$EXE" -I "$HERE/operator_env.py" "$WORK/op" "$WORK/data" ) > "$OUT/operator_env.json"
cat > "$WORK/env.sh" <<ENV
export CAIN_BIN="$(np "$WORK/cain-venv/$BIN/cain$EXE")"
export CAIN_PY="$(np "$WORK/cain-venv/$BIN/python$EXE")"
export CONSUMER_BIN="$(np "$WORK/consumer-venv/$BIN/predictor-research-consumer$EXE")"
export CONSUMER_PY="$(np "$WORK/consumer-venv/$BIN/python$EXE")"
export CRIPTO_RESEARCH_BIN="$(np "$WORK/consumer-venv/$BIN/cripto-research$EXE")"
export OP_POLICY="$(np "$WORK/op/policy.json")"
export OP_OBJECTS="$(np "$WORK/op/objects")"
export CRIPTO_TESTS="$(np "$WORK/cripto-tests")"
ENV
cat "$WORK/env.sh"
echo "runtime_env done $(date -u +%FT%TZ)"
