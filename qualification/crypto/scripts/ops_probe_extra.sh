#!/usr/bin/env bash
# SHARED-003: sondas extras (A/B causal + árvore real) num python com predictor_ops já instalado.
# Uso: ops_probe_extra.sh <python> <out_dir> <n_exact>
set -u
PY="$1"; OUT="$2"; N="$3"
PROBE="$(cd "$(dirname "$0")" && pwd)/ops_timeout_probe.py"
mkdir -p "$OUT"; WORK="$(mktemp -d)"
"$PY" -c "import predictor_ops,sys;print('predictor_ops', predictor_ops.__file__, sys.version)" > "$OUT/env.log" 2>&1 || exit 3
for i in $(seq 1 "$N"); do "$PY" "$PROBE" test-exact "$WORK/t$i" >> "$OUT/probe_test_exact.jsonl" 2>>"$OUT/probe_errors.log"; done
for i in $(seq 1 20); do "$PY" "$PROBE" startup "$WORK/s$i" >> "$OUT/probe_startup.jsonl" 2>>"$OUT/probe_errors.log"; done
for i in $(seq 1 10); do "$PY" "$PROBE" slow-start "$WORK/w$i" >> "$OUT/probe_slow_start.jsonl" 2>>"$OUT/probe_errors.log"; done
for i in $(seq 1 10); do "$PY" "$PROBE" ample "$WORK/a$i" >> "$OUT/probe_ample.jsonl" 2>>"$OUT/probe_errors.log"; done
for i in $(seq 1 3); do "$PY" "$PROBE" real-tree "$WORK/r$i" >> "$OUT/probe_real_tree.jsonl" 2>>"$OUT/probe_errors.log"; done
echo "done $(date -u +%FT%TZ)" >> "$OUT/env.log"
