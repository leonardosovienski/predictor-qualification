#!/usr/bin/env bash
# integration-brasileirao: roda um cenário do harness no runtime suportado do owner_linux (PC 2), com as guardas do
# dado privado: sha256 da fonte e da cópia antes e depois, e o no_data_rows_check (sem mudança) em toda a saída pública
# do cenário. Saída pública = RAW_LOGS/runtime/<run>/<cenário>/; trabalho (estado do CAIN, spool, estado do domínio,
# log privado) = ~/predictors/runtime/integration-brasileirao/priv/<run>/<cenário>/.
#
# Uso: run_scenario.sh <cenário: e2e|n_plus_1|isolation|failure_matrix|soak|…> [args extras do script]
set -uo pipefail
SCEN=$1; shift
HERE="$(cd "$(dirname "$0")" && pwd)"
Q="$(cd "$HERE/.." && pwd)"
P="$HOME/predictors"
RUN=$(cat "$P/runtime/integration-brasileirao/priv/CURRENT_RUN")
PRIV="$P/runtime/integration-brasileirao/priv/$RUN"
OUT="$Q/RAW_LOGS/runtime/$RUN/${SCEN//_/-}"
WORK="$PRIV/${SCEN//_/-}"
PY="$P/tools/python/cpython-3.13-linux-x86_64-gnu/bin/python3.13"
SRC_DATA="$P/data/d16/brasileirao/matches_source_copy.sqlite3"
DATA_SHA=31f30a4dcf33867d1f3aa3d12337a9a66047e6bff10b9a3fa86aae9ef06c9e43
# shellcheck disable=SC1091
source "$PRIV/env.sh"
mkdir -p "$OUT"
[ ! -e "$WORK" ] || { echo "trabalho já existe: $WORK" >&2; exit 2; }
mkdir -p "$WORK"
{
  echo "run=$RUN scenario=$SCEN start=$(date -u +%FT%TZ) host=$(hostname) where=owner_linux (PC 2)"
  echo "data before source=$(sha256sum "$SRC_DATA" | cut -d' ' -f1) copy=$(sha256sum "$DATASET_COPY" | cut -d' ' -f1)"
} > "$OUT/guard.log"
( cd "$HERE" && "$PY" "$SCEN.py" "$Q" "$WORK" "$OUT" "$@" )
rc=$?
{
  echo "scenario exit=$rc end=$(date -u +%FT%TZ)"
  echo "data after source=$(sha256sum "$SRC_DATA" | cut -d' ' -f1) copy=$(sha256sum "$DATASET_COPY" | cut -d' ' -f1) expected=$DATA_SHA"
} >> "$OUT/guard.log"
"$PY" "$Q/../brasileirao/scripts/no_data_rows_check.py" --dataset "$DATASET_COPY" --paths "$OUT" \
  --out "$WORK/no_data_rows_check.json" > "$WORK/no_data_rows_check.log" 2>&1
ndr=$?
cp "$WORK/no_data_rows_check.json" "$OUT/no_data_rows_check.json"
echo "no_data_rows_check exit=$ndr $(cat "$WORK/no_data_rows_check.log")" >> "$OUT/guard.log"
grep -q "copy=$DATA_SHA expected" "$OUT/guard.log" && grep -c "source=$DATA_SHA" "$OUT/guard.log" | grep -q 2 || rc=3
cat "$OUT/guard.log"
[ "$ndr" = 0 ] || exit 4
exit $rc
