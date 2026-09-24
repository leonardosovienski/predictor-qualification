#!/usr/bin/env bash
# brasileirao / publish-candidates no PC 2 (Linux): o mesmo método do build_rc.sh (que usa caminhos do PC 1).
# Bytes exatos dos blobs do commit (git archive, sem árvore de trabalho), SOURCE_DATE_EPOCH fixo (o da D-14),
# duas vezes; os sha256 têm de bater. uv/Python só os gerenciados em ~/predictors/tools. Nada é publicado aqui.
# Uso: pc2_build_rc.sh <clone> <commit> <out_dir>
set -euo pipefail
CLONE="$1"; COMMIT="$2"; OUT="$3"
P="$HOME/predictors"
export PATH="$P/tools/uv:$PATH" UV_PYTHON_INSTALL_DIR="$P/tools/python" UV_CACHE_DIR="$P/tools/uv-cache" UV_PYTHON_PREFERENCE=only-managed
export SOURCE_DATE_EPOCH=1758240000
mkdir -p "$OUT"
echo "commit=$COMMIT date=$(date -u +%FT%TZ) $(uv --version)"
for n in 1 2; do
  SRC="$OUT/src$n"; rm -rf "$SRC" "$OUT/dist$n"; mkdir -p "$SRC" "$OUT/dist$n"
  git -C "$CLONE" -c core.autocrlf=false archive --format=tar "$COMMIT" | tar -x -C "$SRC"
  ( cd "$SRC" && uv build --python 3.13 --out-dir "$OUT/dist$n" 2>&1 | tail -3 )
done
( cd "$OUT" && sha256sum dist1/* dist2/* )
a=$(cd "$OUT/dist1" && sha256sum *.whl | awk '{print $1}'); b=$(cd "$OUT/dist2" && sha256sum *.whl | awk '{print $1}')
sa=$(cd "$OUT/dist1" && sha256sum *.tar.gz | awk '{print $1}'); sb=$(cd "$OUT/dist2" && sha256sum *.tar.gz | awk '{print $1}')
[ "$a" = "$b" ] && echo "REPRODUCIBLE wheel sha256=$a" || { echo "NOT REPRODUCIBLE wheel $a != $b"; exit 3; }
[ "$sa" = "$sb" ] && echo "REPRODUCIBLE sdist sha256=$sa" || echo "sdist differs between builds: $sa != $sb"
"$P/tools/python/cpython-3.13-linux-x86_64-gnu/bin/python3.13" -m zipfile -l "$OUT"/dist1/*.whl \
  | grep -E "brasileirao_predictor/(model|research_runtime/(runner|worker|execution|faults)|adapters/__init__|pit).py|entry_points"
