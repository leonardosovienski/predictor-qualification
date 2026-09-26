#!/usr/bin/env bash
# Suíte do predictor-research-protocol num commit fixo: git archive do pacote, venv novo por Python,
# `uv lock --check`, `uv sync --locked --no-editable` e pytest (como o job research-packages do CI).
# Uso: suite_protocol_v2.sh <repo> <commit> <saída (diretório novo)>
set -uo pipefail
REPO=$1; COMMIT=$2; OUT=$3
test ! -e "$OUT" || { echo "saída já existe: $OUT"; exit 2; }
mkdir -p "$OUT/src"
git -C "$REPO" -c core.autocrlf=false archive --format=tar "$COMMIT" packages/research-protocol | tar -x -C "$OUT/src"
echo "commit=$(git -C "$REPO" rev-parse "$COMMIT") tree=$(git -C "$REPO" rev-parse "$COMMIT:packages/research-protocol") uv=$(uv --version)"
cd "$OUT/src/packages/research-protocol"
status=0
for py in 3.11 3.12 3.13 3.14; do
  echo "== python $py"
  export UV_PROJECT_ENVIRONMENT=$OUT/venv-$py
  uv lock --check --python "$py" || status=1
  uv sync --locked --no-editable --python "$py" -q || status=1
  "$OUT/venv-$py/bin/python" -c "import sys, importlib.metadata as m; print(sys.version.split()[0], m.version('predictor-research-protocol'))"
  uv run --locked --no-sync pytest tests -q -p no:cacheprovider 2>&1 | tail -1 || status=1
done
echo "SUITE_EXIT=$status"
exit $status
