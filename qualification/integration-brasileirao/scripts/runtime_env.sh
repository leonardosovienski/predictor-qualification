#!/usr/bin/env bash
# integration-brasileirao: runtime suportado (C3.1) no owner_linux (PC 2, D-19/D-25) — venvs limpos, só com as wheels
# publicadas dos final_commits.
#
#   CAIN        : dependências exportadas do uv.lock do cain no commit final (--locked, --no-dev, --require-hashes;
#                 inclui o protocolo e o transporte pelas URLs das releases com sha256) + a wheel publicada do cain
#                 (--no-deps, sha256 conferido).
#   Brasileirão : dependências exportadas do uv.lock do brasileirao-predictor no commit final (runtime, como
#                 qualification/brasileirao/scripts/pc2_d16_runtime.sh; Core e Ops pelas URLs das releases) + as wheels
#                 publicadas do Brasileirão, do transporte e do protocolo (--no-deps, sha256 conferido).
#   INTEGRATED=1: também os consumidores do cripto e do stocks (final_commits/wheels das integrações deles, com o
#                 transporte desta missão) e os dados públicos + operadores deles, pelos scripts versionados das
#                 missões deles, sem mudança (isolamento e ciclos intercalados pelo runtime integrado, prompt §5).
# Os lados só conversam pelo spool (arquivos); o venv do CAIN não tem domínio nenhum instalado.
# Árvores de código só por `git archive` dos clones de ~/predictors/repos (sem checkout, sem editable, sem PYTHONPATH).
# uv e Python 3.13 só os gerenciados de ~/predictors/tools. Sem segredos.
# Dado real do Brasileirão (D-11/D-16): só a cópia conferida em ~/predictors/runtime/integration-brasileirao/data/, com
# sha256 antes e depois; o ambiente de operador (objetos, datasets, canário) fica no diretório privado <priv>.
# Saídas: <out> = só o que pode ir para RAW_LOGS (sem registro do dado); <priv> = tudo o que tem conteúdo por jogo.
#
# Uso: runtime_env.sh <runtime_targets.json> <priv> <out>   (grava <priv>/env.sh)
set -euo pipefail
TARGETS=$1 PRIV=$2 OUT=$3
HERE="$(cd "$(dirname "$0")" && pwd)"
QC="$(cd "$HERE/.." && pwd)"
REPO_ROOT="$(cd "$QC/../.." && pwd)"
P="$HOME/predictors"
REPOS="$P/repos"
export PATH="$P/tools/uv:$PATH" UV_PYTHON_INSTALL_DIR="$P/tools/python" UV_CACHE_DIR="$P/tools/uv-cache" \
  UV_PYTHON_PREFERENCE=only-managed
SRC_DATA="$P/data/d16/brasileirao/matches_source_copy.sqlite3"
COPY="$P/runtime/integration-brasileirao/data/matches_source_copy.sqlite3"
DATA_SHA=31f30a4dcf33867d1f3aa3d12337a9a66047e6bff10b9a3fa86aae9ef06c9e43
mkdir -p "$PRIV" "$OUT"
[ -z "$(ls -A "$PRIV")" ] || { echo "diretório privado não vazio: $PRIV" >&2; exit 2; }
exec > >(tee -a "$OUT/runtime_env.log") 2>&1
echo "runtime_env run_at=$(date -u +%FT%TZ) host=$(hostname) where=owner_linux (PC 2) uname=$(uname -srm)"
echo "os=$(. /etc/os-release && echo "$PRETTY_NAME") wsl=$(grep -qi microsoft /proc/version && echo yes || echo no)"
echo "uv=$(uv --version) integrated=${INTEGRATED:-0} evidence_commit=$(git -C "$REPO_ROOT" rev-parse HEAD)"
echo "provision_receipt_sha256=$(sha256sum "$P/PROVISION_RECEIPT.json" | cut -d' ' -f1)"
field() { "$P/tools/python/cpython-3.13-linux-x86_64-gnu/bin/python3.13" -c "import json,sys;d=json.load(open(sys.argv[1]));print(d$1)" "$TARGETS"; }
fetch() {  # url sha256 dest
  curl -sSfL --retry 3 -o "$3" "$1"
  echo "$2  $3" | sha256sum -c -
}
tree() {  # repo commit dest
  mkdir -p "$3"
  git -C "$REPOS/$1" cat-file -e "$2^{commit}"
  git -C "$REPOS/$1" -c core.autocrlf=false archive --format=tar "$2" | tar -x -C "$3"
  echo "$1 $2 (git archive)"
}
venv() {  # dir src extras
  ( cd "$2" && uv export --locked --no-emit-project $3 --format requirements-txt -o "$1.req.txt" -q )
  uv venv -q "$1" --python 3.13
  uv pip install -q --python "$1/bin/python" --require-hashes --no-deps -r "$1.req.txt"
}
wheel() {  # venv key
  local url sha dest
  url=$(field "['$2']['url']"); sha=$(field "['$2']['sha256']"); dest="$PRIV/wheels/$(basename "$url")"
  mkdir -p "$PRIV/wheels"
  [ -f "$dest" ] || fetch "$url" "$sha" "$dest"
  echo "$sha  $dest" | sha256sum -c -
  uv pip install -q --python "$1/bin/python" --no-deps "$dest"
}
# ---------------------------------------------------------------- dado real: cópia conferida (antes)
[ "$(sha256sum "$SRC_DATA" | cut -d' ' -f1)" = "$DATA_SHA" ] || { echo "fonte com sha256 diferente"; exit 3; }
[ "$(sha256sum "$COPY" | cut -d' ' -f1)" = "$DATA_SHA" ] || { echo "cópia com sha256 diferente"; exit 3; }
echo "dataset source=$DATA_SHA copy=$DATA_SHA (antes)"
# ---------------------------------------------------------------- CAIN
tree cain "$(field "['cain']['commit']")" "$PRIV/cain-src"
venv "$PRIV/cain-venv" "$PRIV/cain-src" "--no-dev"
wheel "$PRIV/cain-venv" cain
uv pip check --python "$PRIV/cain-venv/bin/python"
uv pip freeze --python "$PRIV/cain-venv/bin/python" > "$OUT/pip_freeze_cain.txt"
# ---------------------------------------------------------------- consumidor do Brasileirão
tree brasileirao-predictor "$(field "['brasileirao']['commit']")" "$PRIV/br-src"
venv "$PRIV/consumer-venv" "$PRIV/br-src" ""
for key in brasileirao transport protocol; do wheel "$PRIV/consumer-venv" "$key"; done
uv pip check --python "$PRIV/consumer-venv/bin/python"
uv pip freeze --python "$PRIV/consumer-venv/bin/python" > "$OUT/pip_freeze_consumer.txt"
for pkg in brasileirao_predictor stocks_predictor GarimpoInvestimentos; do
  if "$PRIV/cain-venv/bin/python" -c "import $pkg" 2>/dev/null; then echo "CAIN venv has $pkg installed"; exit 3; fi
done
echo "CAIN venv sem pacote de domínio"
# árvore do final_commit sem o pacote (conformidade, suíte e smoke do adapter pela wheel instalada)
tree brasileirao-predictor "$(field "['brasileirao']['commit']")" "$PRIV/br-tree"
rm -rf "$PRIV/br-tree/brasileirao_predictor" "$PRIV/br-tree/brasileirao_scripts"
CPY="$PRIV/consumer-venv/bin/python"
mkdir -p "$PRIV/elsewhere"
( cd "$PRIV/elsewhere" && "$CPY" -I -c "import brasileirao_predictor, brasileirao_predictor.adapters.research_v2 as a, research_transport.adapters as t, importlib.metadata as m
print('brasileirao', m.version('brasileirao-predictor'), brasileirao_predictor.__file__)
print('transport', m.version('predictor-research-transport'), sorted(t.ADAPTERS))
print('adapter', a.identity())
assert 'site-packages' in brasileirao_predictor.__file__" )
( cd "$PRIV/elsewhere" && "$PRIV/cain-venv/bin/python" -I -c "import cain, importlib.metadata as m
from importlib.resources import files
print('cain', m.version('cain-research'), cain.__file__)
print('configs', sorted(p.name for p in files('cain.orchestration').joinpath('data').iterdir()))
assert 'site-packages' in cain.__file__" )
# ---------------------------------------------------------------- operador do Brasileirão (privado)
( cd "$PRIV/elsewhere" && "$CPY" -I "$HERE/operator_env.py" --script "$PRIV/consumer-venv/bin/brasileirao-research" \
    --repo "$REPOS/brasileirao-predictor" --commit "$(field "['brasileirao']['commit']")" --dataset "$COPY" \
    --dataset-sha256 "$DATA_SHA" --work "$PRIV/op" ) > "$OUT/operator_env.json"
cat "$OUT/operator_env.json"
cat > "$PRIV/env.sh" <<ENV
export CAIN_BIN="$PRIV/cain-venv/bin/cain"
export CAIN_PY="$PRIV/cain-venv/bin/python"
export CONSUMER_BIN="$PRIV/consumer-venv/bin/predictor-research-consumer"
export CONSUMER_PY="$CPY"
export BRASILEIRAO_RESEARCH_BIN="$PRIV/consumer-venv/bin/brasileirao-research"
export OP_POLICY="$PRIV/op/policy.json"
export OP_OBJECTS="$PRIV/op/obj"
export REAL_ENV="$PRIV/op/REAL_ENV.json"
export BR_TREE="$PRIV/br-tree"
export DATASET_COPY="$COPY"
ENV
# ---------------------------------------------------------------- cripto e stocks integrados
if [ "${INTEGRATED:-0}" = 1 ]; then
  tree cripto-predictor "$(field "['cripto']['commit']")" "$PRIV/cripto-src"
  venv "$PRIV/crypto-venv" "$PRIV/cripto-src" "--all-extras"
  for key in cripto transport protocol; do wheel "$PRIV/crypto-venv" "$key"; done
  uv pip check --python "$PRIV/crypto-venv/bin/python"
  uv pip freeze --python "$PRIV/crypto-venv/bin/python" > "$OUT/pip_freeze_crypto.txt"
  XPY="$PRIV/crypto-venv/bin/python"
  "$XPY" "$REPO_ROOT/qualification/crypto/scripts/build_real_dataset.py" "$PRIV/crypto-data" > "$OUT/crypto_build_real_dataset.log" 2>&1
  mkdir -p "$PRIV/crypto-op"
  ( cd "$PRIV" && "$XPY" -I "$REPO_ROOT/qualification/integration-crypto/scripts/operator_env.py" "$PRIV/crypto-op" "$PRIV/crypto-data" ) > "$OUT/crypto_operator_env.json"
  tree stocks-predictor "$(field "['stocks']['commit']")" "$PRIV/stocks-src"
  venv "$PRIV/stocks-venv" "$PRIV/stocks-src" "--all-extras"
  for key in stocks transport protocol; do wheel "$PRIV/stocks-venv" "$key"; done
  uv pip check --python "$PRIV/stocks-venv/bin/python"
  uv pip freeze --python "$PRIV/stocks-venv/bin/python" > "$OUT/pip_freeze_stocks.txt"
  SPY="$PRIV/stocks-venv/bin/python"
  mkdir -p "$PRIV/stocks-tree"
  git -C "$REPOS/stocks-predictor" archive "$(field "['stocks']['commit']")" | tar -x -C "$PRIV/stocks-tree"
  rm -rf "$PRIV/stocks-tree/stocks_predictor"
  STOCKS_SOURCES=$(field "['stocks_sources']")
  cp "$REPO_ROOT/$STOCKS_SOURCES" "$OUT/STOCKS_SOURCES.json"
  export PYTHONUTF8=1
  ( cd "$PRIV/elsewhere" && "$SPY" -I "$REPO_ROOT/qualification/stocks/d16/build_real_panel.py" build "$PRIV/stocks-cache" \
      "$REPO_ROOT/$STOCKS_SOURCES" "$PRIV/stocks-panel" ) > "$OUT/stocks_build_real_panel.log" 2>&1 \
    || { echo "STOCKS_PANEL_BUILD_FAILED"; tail -20 "$OUT/stocks_build_real_panel.log"; exit 3; }
  ( cd "$PRIV/elsewhere" && "$SPY" -I "$REPO_ROOT/qualification/stocks/d16/verify_prefilter.py" "$PRIV/stocks-panel/panel.json" \
      "$PRIV/stocks-panel/panel_full.json" "$REPO_ROOT/qualification/stocks/d16/PROTOCOL_REAL.json" "$OUT/stocks_verify_prefilter.json" ) \
      > "$OUT/stocks_verify_prefilter.log" 2>&1 || { echo "STOCKS_PREFILTER_CHANGED_UNIVERSE"; exit 3; }
  rm -f "$PRIV/stocks-panel/panel_full.json"
  mkdir -p "$PRIV/stocks-op"
  ( cd "$PRIV/elsewhere" && "$SPY" -I "$REPO_ROOT/qualification/integration-stocks/scripts/operator_env.py" "$PRIV/stocks-op" \
      "$PRIV/stocks-panel" "$REPO_ROOT/qualification/stocks/d16/PROTOCOL_REAL.json" \
      "$PRIV/stocks-tree/EXTERNAL_INTELLIGENCE_TRIAL_READINESS_MATRIX.json" ) > "$OUT/stocks_operator_env.json"
  cat >> "$PRIV/env.sh" <<ENV
export CRYPTO_CONSUMER_BIN="$PRIV/crypto-venv/bin/predictor-research-consumer"
export CRIPTO_RESEARCH_BIN="$PRIV/crypto-venv/bin/cripto-research"
export CRYPTO_OP_POLICY="$PRIV/crypto-op/policy.json"
export CRYPTO_OP_OBJECTS="$PRIV/crypto-op/objects"
export STOCKS_CONSUMER_BIN="$PRIV/stocks-venv/bin/predictor-research-consumer"
export STOCKS_RESEARCH_BIN="$PRIV/stocks-venv/bin/stocks-research"
export STOCKS_OP_POLICY="$PRIV/stocks-op/policy.json"
export STOCKS_OP_OBJECTS="$PRIV/stocks-op/objects"
export STOCKS_REAL_ENV="$PRIV/stocks-op/REAL_ENV.json"
ENV
fi
# ---------------------------------------------------------------- dado real: cópia conferida (depois)
[ "$(sha256sum "$SRC_DATA" | cut -d' ' -f1)" = "$DATA_SHA" ] && [ "$(sha256sum "$COPY" | cut -d' ' -f1)" = "$DATA_SHA" ] \
  || { echo "dado mudou durante o runtime_env"; exit 3; }
echo "dataset source=$DATA_SHA copy=$DATA_SHA (depois)"
echo "runtime_env done $(date -u +%FT%TZ)"
