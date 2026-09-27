#!/usr/bin/env bash
# integration-crypto: runtime suportado (C3.1) — dois venvs limpos, só com as wheels publicadas dos final_commits.
#
#   CAIN        : dependências exportadas do uv.lock do cain no commit final (--require-hashes; inclui o protocolo e o
#                 transporte pelas URLs das releases com sha256) + a wheel publicada do cain (--no-deps, sha256).
#   consumidor  : dependências exportadas do uv.lock do cripto-predictor no commit final (--all-extras, como na
#                 Etapa A; Core e Ops pelas URLs das releases) + as wheels publicadas do cripto, do transporte e do
#                 protocolo (--no-deps, sha256 conferido antes de instalar).
# Os dois lados só conversam pelo spool (arquivos); o venv do CAIN não tem o domínio instalado.
# Dados: build_real_dataset.py da Etapa A (Binance data.vision, .CHECKSUM), fora do repositório; ambiente de operador
# com operator_env.py (policy + objetos de referência). Sem segredos, sem API da Binance.
#
# Uso: runtime_env.sh <runtime_targets.json> <work> <out>   (imprime as variáveis de ambiente úteis em <work>/env.sh)
set -euo pipefail
TARGETS=$1 WORK=$2 OUT=$3
HERE="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$HERE/../../.." && pwd)"
PY=${PYTHON:-python3.13}
mkdir -p "$WORK" "$OUT"
exec > >(tee -a "$OUT/runtime_env.log") 2>&1
echo "runtime_env run_at=$(date -u +%FT%TZ) host=$(hostname) where=${GITHUB_ACTIONS:+github_actions} uname=$(uname -srm)"
echo "python=$("$PY" --version 2>&1) uv=$(uv --version)"
field() { "$PY" -c "import json,sys;d=json.load(open('$TARGETS'));print(d$1)"; }
fetch() {  # url sha256 dest
  curl -sSfL -o "$3" "$1"
  echo "$2  $3" | sha256sum -c -
}
# ---------------------------------------------------------------- CAIN
CAIN_COMMIT=$(field "['cain']['commit']")
git clone -q https://github.com/leonardosovienski/cain.git "$WORK/cain-src"
git -C "$WORK/cain-src" checkout -q "$CAIN_COMMIT"
( cd "$WORK/cain-src" && uv export --locked --no-dev --no-emit-project --format requirements-txt -o "$WORK/cain-req.txt" -q )
"$PY" -m venv "$WORK/cain-venv"
"$WORK/cain-venv/bin/python" -m pip install -q --require-hashes -r "$WORK/cain-req.txt"
fetch "$(field "['cain']['url']")" "$(field "['cain']['sha256']")" "$WORK/$(basename "$(field "['cain']['url']")")"
"$WORK/cain-venv/bin/python" -m pip install -q --no-deps "$WORK/$(basename "$(field "['cain']['url']")")"
"$WORK/cain-venv/bin/python" -m pip check
"$WORK/cain-venv/bin/python" -m pip freeze > "$OUT/pip_freeze_cain.txt"
# ---------------------------------------------------------------- consumer + domain
CR_COMMIT=$(field "['cripto']['commit']")
git clone -q https://github.com/leonardosovienski/cripto-predictor.git "$WORK/cripto-src"
git -C "$WORK/cripto-src" checkout -q "$CR_COMMIT"
( cd "$WORK/cripto-src" && uv export --locked --all-extras --no-emit-project --format requirements-txt -o "$WORK/cripto-req.txt" -q )
"$PY" -m venv "$WORK/consumer-venv"
"$WORK/consumer-venv/bin/python" -m pip install -q --require-hashes -r "$WORK/cripto-req.txt"
for key in cripto transport protocol; do
  fetch "$(field "['$key']['url']")" "$(field "['$key']['sha256']")" "$WORK/$(basename "$(field "['$key']['url']")")"
  "$WORK/consumer-venv/bin/python" -m pip install -q --no-deps "$WORK/$(basename "$(field "['$key']['url']")")"
done
"$WORK/consumer-venv/bin/python" -m pip check
"$WORK/consumer-venv/bin/python" -m pip freeze > "$OUT/pip_freeze_consumer.txt"
# the CAIN side must not have any domain package installed
if "$WORK/cain-venv/bin/python" -c "import GarimpoInvestimentos" 2>/dev/null; then echo "CAIN venv has the domain installed"; exit 3; fi
# tests tree of the domain final commit, outside the package (for the conformance suite, C24.3 c)
mkdir -p "$WORK/cripto-tests" && cp -r "$WORK/cripto-src/tests/." "$WORK/cripto-tests/"
# ---------------------------------------------------------------- data + operator environment
"$WORK/consumer-venv/bin/python" "$REPO_ROOT/qualification/crypto/scripts/build_real_dataset.py" "$WORK/data" > "$OUT/build_real_dataset.log" 2>&1
cp "$WORK/data/MANIFEST.json" "$OUT/data_MANIFEST.json"
mkdir -p "$WORK/op"
( cd "$WORK" && "$WORK/consumer-venv/bin/python" -I "$HERE/operator_env.py" "$WORK/op" "$WORK/data" ) > "$OUT/operator_env.json"
cat > "$WORK/env.sh" <<ENV
export CAIN_BIN="$WORK/cain-venv/bin/cain"
export CAIN_PY="$WORK/cain-venv/bin/python"
export CONSUMER_BIN="$WORK/consumer-venv/bin/predictor-research-consumer"
export CONSUMER_PY="$WORK/consumer-venv/bin/python"
export CRIPTO_RESEARCH_BIN="$WORK/consumer-venv/bin/cripto-research"
export OP_POLICY="$WORK/op/policy.json"
export OP_OBJECTS="$WORK/op/objects"
export CRIPTO_TESTS="$WORK/cripto-tests"
ENV
cat "$WORK/env.sh"
echo "runtime_env done $(date -u +%FT%TZ)"
