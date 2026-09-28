#!/usr/bin/env bash
# integration-stocks: suíte local do stocks-predictor num commit (diagnóstico no WSL; a prova é o CI hospedado).
# Espelha os passos do .github/workflows/ci.yml (job quality) que rodam localmente, na ordem, sem escrever no
# worktree (COVERAGE_FILE, junit e caches fora dele). Exige árvore limpa antes e confere que continua limpa depois.
# Uso: stocks_suite.sh <worktree> <venv> <out_dir>
set -uo pipefail
REPO=$1 VENV=$2 OUT=$3
mkdir -p "$OUT"
exec > >(tee "$OUT/suite.log") 2>&1
cd "$REPO"
echo "run_at $(date -u +%FT%TZ) head $(git rev-parse HEAD) python $("$VENV/bin/python" --version)"
dirty=$(git status --porcelain | wc -l); echo "dirty_before $dirty"; [ "$dirty" = 0 ] || { echo "ÁRVORE SUJA"; exit 4; }
export PYTHONDONTWRITEBYTECODE=1 COVERAGE_FILE="$OUT/.coverage" RUFF_CACHE_DIR="$OUT/ruff-cache"
export LD_LIBRARY_PATH=/home/superleo13/predictors/runtime/brasileirao/sysroot/x/usr/lib/x86_64-linux-gnu
export PYRIGHT_PYTHON_CACHE_DIR=/home/superleo13/predictors/runtime/integration-stocks/pyright-cache
B="$VENV/bin"
export PATH="$B:$PATH"  # como `uv run` no CI: ruff e pyright do venv no PATH (quality_exception_control)
step() { local name=$1; shift; echo "=== $name"; "$@"; local rc=$?; echo "[$name exit $rc]"; }
step doctor "$B/python" main.py doctor --check
step ruff "$B/ruff" check stocks_predictor tests main.py tools/data_bank.py tools/benchmark_ingestion.py tools/benchmark_real_ingestion.py tools/materialize_source_revision.py tools/reproducible_build.py tools/audit_registry.py tools/operational_validation.py tools/verify_operational_evidence.py tools/check_project_files.py research/session-20260910/final_review/verify.py research/session-20260909/data_completion research/session-20260910/integral research/session-20260910/profit_validation research/session-20260910/gap_resolution
step pyright "$B/pyright" --pythonversion 3.13 --pythonpath "$B/python"
step quality_exception_control "$B/python" tools/quality_exception_control.py
step verify_audit "$B/python" research/session-20260910/integral/verify_audit.py
step gap_resolution "$B/python" research/session-20260910/gap_resolution/verify.py
step archived_regressions env PYTHONPATH=stocks_predictor:research/session-20260908/chat-review:research/session-20260908/h20-profit-test "$B/python" -m pytest -p no:cacheprovider -q --import-mode=importlib research/session-20260908/chat-review/test_h20_evidence_integrity.py research/session-20260908/h20-profit-test/test_h20_profit_comparison.py
step audit_registry "$B/python" tools/audit_registry.py
step verify_operational_evidence "$B/python" tools/verify_operational_evidence.py
step final_review "$B/python" research/session-20260910/final_review/verify.py
step check_project_files "$B/python" tools/check_project_files.py
step tests "$B/coverage" run -m pytest -p no:cacheprovider -q --durations=15 --junitxml="$OUT/test-results.xml"
step coverage_json "$B/coverage" json -o "$OUT/coverage.json"
step coverage_report "$B/coverage" report
dirty=$(git status --porcelain | wc -l); echo "dirty_after $dirty"
echo "done $(date -u +%FT%TZ)"
