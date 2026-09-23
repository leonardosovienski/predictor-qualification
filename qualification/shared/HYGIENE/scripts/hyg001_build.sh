#!/usr/bin/env bash
# HYG-001: build reproduzível dos três pacotes do protocolo a partir de git archive,
# duas vezes em diretórios distintos. EOL=lf (padrão, D-14) usa os bytes exatos
# dos blobs; EOL=crlf reproduz um checkout Windows com core.autocrlf=true.
# Uso: hyg001_build.sh <ecosystem_repo> <commit> <out_dir> [lf|crlf]
set -euo pipefail
REPO=$1; COMMIT=$2; OUT=$3; EOL=${4:-lf}   # lf = bytes exatos dos blobs; crlf = checkout Windows (autocrlf=true)
export SOURCE_DATE_EPOCH=1758240000
PKGS=${PKGS:-"research-protocol research-snapshot research-bundle"}
rm -rf "$OUT"; mkdir -p "$OUT"
AUTOCRLF=false; [ "$EOL" = crlf ] && AUTOCRLF=true
for run in a b; do
  src="$OUT/src-$run"; mkdir -p "$src"
  git -C "$REPO" -c core.autocrlf=$AUTOCRLF archive --format=tar "$COMMIT" packages | tar -x -C "$src"
  for p in $PKGS; do
    uv build --python 3.13.14 --wheel --no-cache --out-dir "$OUT/dist-$run" "$src/packages/$p"
  done
done
( cd "$OUT/dist-a" && sha256sum *.whl ) > "$OUT/sha256-a.txt"
( cd "$OUT/dist-b" && sha256sum *.whl ) > "$OUT/sha256-b.txt"
cat "$OUT/sha256-a.txt"; cat "$OUT/sha256-b.txt"
if diff "$OUT/sha256-a.txt" "$OUT/sha256-b.txt"; then echo "REPRODUCIBLE=YES"; else echo "REPRODUCIBLE=NO"; exit 1; fi
