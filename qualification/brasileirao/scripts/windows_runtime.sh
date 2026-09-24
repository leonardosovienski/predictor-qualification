#!/usr/bin/env bash
# brasileirao: windows-smoke no runtime Windows D-3 (C:\QUALIFICACAO\runtime\brasileirao\venv, só final wheels).
# 1) dado real: pedidos por temporada/alvo/baseline (real_env.py) pelo brasileirao-research instalado
# 2) E2E real: processo -> término -> processo novo relê o mesmo resultado; cadeia de provenance
# 3) conformidade: suíte tests/conformance do final_commit contra a wheel instalada (árvore sem os pacotes-fonte)
# Uso: windows_runtime.sh <commit> <out_dir>
set -uo pipefail
COMMIT="$1"; OUT="$2"
. /c/QUALIFICACAO/tools/uvenv.sh
export PYTHONIOENCODING=utf-8
HERE="$(cd "$(dirname "$0")" && pwd)"
R=/c/QUALIFICACAO/runtime/brasileirao
PY="$R/venv/Scripts/python.exe"
SCRIPT="$R/venv/Scripts/brasileirao-research.exe"
mkdir -p "$OUT"
{ echo "commit=$COMMIT date=$(date -u +%FT%TZ)"; "$PY" -c "import sys,platform;print(sys.version,platform.platform())"; } > "$OUT/env.log" 2>&1

# 1) dado real
rm -rf "$R/r2"
uv run -q --no-project --with pyyaml python "$HERE/real_env.py" --script "$SCRIPT" --repo C:/QUALIFICACAO/repos/brasileirao-predictor \
  --commit "$COMMIT" --dataset C:/QUALIFICACAO/runtime/brasileirao/data/matches_source_copy.sqlite3 \
  --dataset-sha256 31f30a4dcf33867d1f3aa3d12337a9a66047e6bff10b9a3fa86aae9ef06c9e43 --as-of 2026-09-08T19:31:32Z \
  --work C:/QUALIFICACAO/runtime/brasileirao/r2 --out "$OUT/real" > "$OUT/real.log" 2>&1
echo "[exit $?]" >> "$OUT/real.log"

# 2) E2E real (estado do passo 1; pedido novo 2024 OU25 mercado com client_ref)
mkdir -p "$R/r2/req"
cat > "$R/r2/req/e2e.json" <<'JSON'
{"schema_version": "brasileirao-research-request/1", "request_id": "brasileirao:REQ-E2E-REAL-001",
 "request_type": "WALKFORWARD_FORECAST_EVALUATION", "research_id": "brasileirao:R-REAL-20260924",
 "hypothesis_id": "brasileirao:HQ-SERVING-BASELINE", "competition": "Brasileirão Série A", "season": 2024, "target": "OU25",
 "events": {"kickoff_from": "2024-07-01T00:00:00Z", "kickoff_to": "2024-10-01T00:00:00Z"},
 "data_cutoff": "2026-09-08T19:31:32Z", "decision_lead_minutes": 60,
 "references": {"dataset": {"name": "real-20260908", "version": "1"}, "model": {"name": "serving-baseline", "version": "1"},
   "features": {"name": "elo-home-advantage", "version": "1"}, "baseline": {"name": "market", "version": "1"},
   "cost_model": {"name": "close-slippage-tax", "version": "1"}, "odds": {"name": "sofascore-close", "version": "1"}},
 "priority_hint": "NORMAL", "client_ref": {"e2e": "real"}}
JSON
TREE="$R/tree"; rm -rf "$TREE"; mkdir -p "$TREE"
git -C C:/QUALIFICACAO/repos/brasileirao-predictor archive --format=tar "$COMMIT" | tar -x -C "$TREE"
rm -rf "$TREE/brasileirao_predictor" "$TREE/brasileirao_scripts"
( cd /c && "$PY" "$HERE/e2e_runtime.py" --tests "$TREE/tests" --work "$R/r2/e2e" --out "$OUT/e2e_real" \
    --real-state "$R/r2/s" --real-policy "$R/r2/policy.json" --real-objects "$R/r2/obj" --real-request "$R/r2/req/e2e.json" ) > "$OUT/e2e_real.log" 2>&1
echo "[exit $?]" >> "$OUT/e2e_real.log"

# 3) conformidade contra a wheel instalada, num venv de teste separado (o runtime fica só com as final wheels):
#    mesmas wheels + extra dev do lock (pytest), tudo com --require-hashes
CV="$R/venv-conf"; rm -rf "$CV"
( cd "$R/src" && uv export --locked --all-extras --no-emit-project --format requirements-txt -o "$R/req-conf.txt" ) >> "$OUT/env.log" 2>&1
uv venv "$CV" --python 3.13 >> "$OUT/env.log" 2>&1
uv pip install --python "$CV/Scripts/python.exe" --require-hashes --no-deps -r "$R/req-conf.txt" >> "$OUT/env.log" 2>&1
uv pip install --python "$CV/Scripts/python.exe" --no-deps "$R/$(basename "$(ls "$R"/brasileirao_predictor-*.whl | tail -1)")" >> "$OUT/env.log" 2>&1
CPY="$CV/Scripts/python.exe"
mkdir -p "$R/t3"; rm -rf "$R/t3"/*
export BRASILEIRAO_RESEARCH_TEST_ROOT="C:/QUALIFICACAO/runtime/brasileirao/t3"
( cd "$TREE" && "$CPY" -c "import brasileirao_predictor;print('package from', brasileirao_predictor.__file__)" ) >> "$OUT/env.log" 2>&1
( cd "$TREE" && "$CPY" -m pytest -p no:cacheprovider -q -rfE tests/conformance --junitxml="$(cygpath -w "$OUT/conformance.junit.xml")" ) > "$OUT/conformance.log" 2>&1
echo "[exit $?]" >> "$OUT/conformance.log"
echo "done $(date -u +%FT%TZ)" >> "$OUT/env.log"
