#!/usr/bin/env bash
# Build reproduzível do predictor-research-protocol (método do HYG-001/D-14):
# git archive (bytes exatos dos blobs, core.autocrlf=false), SOURCE_DATE_EPOCH fixo,
# duas árvores extraídas separadamente e duas saídas; mesma wheel = REPRODUCIBLE=YES.
# Uso: build_protocol_v2.sh <repo> <commit> <saída (diretório novo)>
set -euo pipefail
REPO=$1; COMMIT=$2; OUT=$3
export SOURCE_DATE_EPOCH=1758240000
test ! -e "$OUT" || { echo "saída já existe: $OUT"; exit 2; }
mkdir -p "$OUT"
echo "commit=$(git -C "$REPO" rev-parse "$COMMIT") tree=$(git -C "$REPO" rev-parse "$COMMIT:packages/research-protocol") uv=$(uv --version) SOURCE_DATE_EPOCH=$SOURCE_DATE_EPOCH"
for run in a b; do
  src="$OUT/src-$run"; mkdir -p "$src"
  git -C "$REPO" -c core.autocrlf=false archive --format=tar "$COMMIT" packages/research-protocol | tar -x -C "$src"
  uv build --python 3.13 --wheel --no-cache --out-dir "$OUT/dist-$run" "$src/packages/research-protocol"
done
( cd "$OUT/dist-a" && sha256sum *.whl ) > "$OUT/sha256-a.txt"
( cd "$OUT/dist-b" && sha256sum *.whl ) > "$OUT/sha256-b.txt"
cat "$OUT/sha256-a.txt" "$OUT/sha256-b.txt"
for run in a b; do
  echo "dist-$run WHEEL:"; unzip -p "$OUT"/dist-$run/*.whl '*.dist-info/WHEEL'
  echo "dist-$run RECORD:"; unzip -p "$OUT"/dist-$run/*.whl '*.dist-info/RECORD'
done
if diff "$OUT/sha256-a.txt" "$OUT/sha256-b.txt"; then echo "REPRODUCIBLE=YES"; else echo "REPRODUCIBLE=NO"; exit 1; fi
