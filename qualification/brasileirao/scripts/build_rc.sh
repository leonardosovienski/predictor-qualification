#!/usr/bin/env bash
# brasileirao / publish-candidates: build reprodutível da wheel/sdist rc do brasileirao-predictor.
# Bytes exatos dos blobs do commit (git archive, sem árvore de trabalho), SOURCE_DATE_EPOCH
# fixo (o mesmo da D-14), duas vezes; os sha256 têm de bater. Nada é publicado aqui.
# Uso: build_rc.sh <clone> <commit> <out_dir>
set -euo pipefail
CLONE="$1"; COMMIT="$2"; OUT="$3"
. /c/QUALIFICACAO/tools/uvenv.sh
export SOURCE_DATE_EPOCH=1758240000
mkdir -p "$OUT"
for n in 1 2; do
  SRC="$OUT/src$n"; mkdir -p "$SRC" "$OUT/dist$n"
  git -C "$CLONE" -c core.autocrlf=false archive --format=tar "$COMMIT" | tar -x -C "$SRC"
  ( cd "$SRC" && uv build --out-dir "$OUT/dist$n" 2>&1 | tail -3 )
done
( cd "$OUT" && sha256sum dist1/* dist2/* )
a=$(cd "$OUT/dist1" && sha256sum *.whl | awk '{print $1}'); b=$(cd "$OUT/dist2" && sha256sum *.whl | awk '{print $1}')
[ "$a" = "$b" ] && echo "REPRODUCIBLE wheel sha256=$a" || { echo "NOT REPRODUCIBLE $a != $b"; exit 3; }
/c/QUALIFICACAO/tools/python/cpython-3.13.14-windows-x86_64-none/python.exe -m zipfile -l "$OUT"/dist1/*.whl | grep -E "brasileirao_predictor/(research_runtime/(runner|worker|execution|faults)|adapters/__init__|pit).py|entry_points"
