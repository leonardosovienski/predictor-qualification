#!/usr/bin/env bash
# integration-stocks, D-24 (4b): procedimento R8 do stocks-predictor no commit final do adapter.
# Reproduz o procedimento da Etapa A (docs/engineering/2026-09-24-qualification-stage-a/evidence/operational-real.json):
# tools/operational_validation.py a partir do checkout (sem --installed), saída fora do repositório; recibo real sobre a
# cópia local preservada do COTAHIST_A2026.ZIP com o --receipt da entrada [3] de
# docs/research/2026-09-10-r6/evidence/acquisitions.json; recibo de capacidade com 250.000 linhas sintéticas; os dois
# validation.json copiados sem edição para docs/engineering/<data>-integration-stocks/evidence/; selo por
# tools/materialize_current_operational_evidence.py; conferência por tools/verify_operational_evidence.py.
# Uso: r8_procedure.sh <worktree do stocks-predictor> <python do venv de dev> <dir de trabalho fora do repo> <data AAAA-MM-DD>
set -uo pipefail
REPO=$1 PY=$2 WORK=$3 DAY=$4
SRC=/home/superleo13/predictors/data/d16/stocks/COTAHIST_A2026.ZIP
EXPECTED=34b774681cbd201ef197fb98af8d431e4d7302e801f58b66e54036d2935dc4f4
EVID="docs/engineering/${DAY}-integration-stocks/evidence"
mkdir -p "$WORK"
exec > >(tee "$WORK/r8_procedure.log") 2>&1
echo "run_at $(date -u +%FT%TZ) host $(hostname) (PC 2, WSL — evidência de engenharia da regra R8, D-18/D-24; nunca gate)"
echo "python $("$PY" --version) repo_head $(git -C "$REPO" rev-parse HEAD) dirty_files $(git -C "$REPO" status --porcelain | wc -l)"
before=$(sha256sum "$SRC" | cut -d' ' -f1); echo "source_sha256_before $before bytes $(stat -c %s "$SRC")"
[ "$before" = "$EXPECTED" ] || { echo "FALHA: sha256 da fonte diverge"; exit 3; }
git -C "$REPO" show 61fc017256ffea815ae96bbe02b847dccdb395cc:docs/research/2026-09-10-r6/evidence/acquisitions.json > "$WORK/acquisitions.json"
"$PY" -c "import json,sys; e=json.load(open(sys.argv[1]))[3]; assert e['sha256']==sys.argv[2], e; json.dump(e, open(sys.argv[3],'w'), indent=1); print('receipt[3]', json.dumps(e))" \
  "$WORK/acquisitions.json" "$EXPECTED" "$WORK/receipt-acquisitions-3.json" || exit 3
rm -rf "$WORK/real" "$WORK/capacity"
( cd "$REPO" && "$PY" tools/operational_validation.py --output "$WORK/real" --rows 55986 --archive "$SRC" --receipt "$WORK/receipt-acquisitions-3.json" )
echo "[real exit $?]"
( cd "$REPO" && "$PY" tools/operational_validation.py --output "$WORK/capacity" --rows 250000 )
echo "[capacity exit $?]"
after=$(sha256sum "$SRC" | cut -d' ' -f1); echo "source_sha256_after $after"
[ "$after" = "$EXPECTED" ] || { echo "FALHA: sha256 da fonte mudou"; exit 3; }
[ -f "$WORK/real/validation.json" ] && [ -f "$WORK/capacity/validation.json" ] || { echo "FALHA: recibo ausente"; exit 3; }
mkdir -p "$REPO/$EVID"
cp "$WORK/real/validation.json" "$REPO/$EVID/operational-real.json"
cp "$WORK/capacity/validation.json" "$REPO/$EVID/operational-capacity.json"
sha256sum "$WORK/real/validation.json" "$REPO/$EVID/operational-real.json" "$WORK/capacity/validation.json" "$REPO/$EVID/operational-capacity.json"
"$PY" -c "import json,sys; r=json.load(open(sys.argv[1])); c=json.load(open(sys.argv[2])); print('real', r['status'], r['rows'], r['source_sha256'], r['inspection']['sources'][0]['rows_sha256']); print('capacity', c['status'], c['rows'])" \
  "$REPO/$EVID/operational-real.json" "$REPO/$EVID/operational-capacity.json"
( cd "$REPO" && "$PY" tools/materialize_current_operational_evidence.py --real "$EVID/operational-real.json" \
    --capacity "$EVID/operational-capacity.json" --output docs/engineering/current-operational-evidence.json )
echo "[seal exit $?]"
( cd "$REPO" && "$PY" tools/verify_operational_evidence.py )
echo "[verify exit $?]"
echo "done $(date -u +%FT%TZ)"
