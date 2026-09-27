#!/usr/bin/env bash
# integration-crypto: fases de runtime no Linux primário (workflow integration-crypto-runtime.yml).
# Monta o runtime suportado (runtime_env.sh) uma vez e roda as fases pedidas, cada uma num diretório próprio.
# Uso: ci_runtime.sh "<fases>" <work> <out>     fases ⊆ {cleanroom contract e2e n1 isolation failures soak}
set -uo pipefail
PHASES=$1 WORK=$2 OUT=$3
HERE="$(cd "$(dirname "$0")" && pwd)"
MISSION="$(cd "$HERE/.." && pwd)"
export PYTHON="$(uv python find 3.13)"
mkdir -p "$WORK" "$OUT"
echo "ci_runtime phases=[$PHASES] commit=$(git -C "$MISSION" rev-parse HEAD) run_at=$(date -u +%FT%TZ)" | tee "$OUT/ci_runtime.log"
bash "$HERE/runtime_env.sh" "$MISSION/runtime_targets.json" "$WORK/rt" "$OUT/env" || { echo "RUNTIME_ENV_FAILED" | tee -a "$OUT/ci_runtime.log"; exit 3; }
# shellcheck disable=SC1091
source "$WORK/rt/env.sh"
status=0
for phase in $PHASES; do
  case "$phase" in
    cleanroom) bash "$HERE/cleanroom_final.sh" "$MISSION/runtime_targets.json" "$WORK/rt" "$OUT/cleanroom-final" ;;
    e2e) ( cd "$HERE" && "$PYTHON" e2e.py "$MISSION" "$WORK/e2e" "$OUT/e2e" ) ;;
    n1) ( cd "$HERE" && "$PYTHON" n_plus_1.py "$MISSION" "$WORK/n1" "$OUT/n-plus-1" ) ;;
    isolation) ( cd "$HERE" && "$PYTHON" isolation.py "$MISSION" "$WORK/isolation" "$OUT/isolation" ) ;;
    failures) ( cd "$HERE" && "$PYTHON" failure_matrix.py "$MISSION" "$WORK/failures" "$OUT/failure-matrix" ) ;;
    soak)
      # without the local model the soak still runs; its llm_proposals floor then fails (never skipped)
      if bash "$HERE/ollama_setup.sh" "$OUT/soak-llm-setup"; then
        export SOAK_OLLAMA_URL=http://127.0.0.1:11434 SOAK_OLLAMA_MODEL=qwen2.5:0.5b
      fi
      ( cd "$HERE" && "$PYTHON" soak.py "$MISSION" "$WORK/soak" "$OUT/soak" ) ;;
    contract) ( cd "$HERE" && "$PYTHON" contract_d.py "$MISSION" "$WORK/contract" "$OUT/contract-revalidation" ) ;;
    *) echo "fase desconhecida: $phase"; false ;;
  esac
  rc=$?
  echo "phase=$phase exit=$rc at=$(date -u +%FT%TZ)" | tee -a "$OUT/ci_runtime.log"
  status=$((status | rc))
done
echo "ci_runtime status=$status" | tee -a "$OUT/ci_runtime.log"
exit $status
