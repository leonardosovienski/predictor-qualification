#!/usr/bin/env bash
# SHARED-003/004 no Windows local (D-3: C:\Cripto\qualificacao\runtime\ops-failure), mesmo script do CI.
# Uso: ops_failure_local.sh <out_root>
set -u
OUT="$1"
. /c/QUALIFICACAO/tools/uvenv.sh
export UV_CACHE_DIR="C:/Cripto/qualificacao/.uv-cache"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
BASE="C:/Cripto/qualificacao/runtime/ops-failure/$STAMP"
mkdir -p "$BASE/tmp"
export TMPDIR="$BASE/tmp" TMP="$BASE/tmp" TEMP="$BASE/tmp"
HERE="$(cd "$(dirname "$0")" && pwd)"
echo "base=$BASE" > "$OUT.env"
bash "$HERE/ops_failure_matrix.sh" source "$OUT/windows-local-source" 10 3 1
bash "$HERE/ops_failure_matrix.sh" wheel "$OUT/windows-local-wheel" 10 3 1
echo "fim $(date -u +%FT%TZ)" >> "$OUT.env"
