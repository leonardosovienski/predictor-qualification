#!/usr/bin/env bash
# Salva, sem edição, a evidência bruta de um run do GitHub Actions:
#   <out>/<repo>_run<id>.json  metadados (commit, evento, conclusão, jobs, URL)
#   <out>/<repo>_run<id>.log   log completo do run (gh run view --log)
# Uso: collect_run.sh <repo> <run_id> <out_dir>
set -euo pipefail
REPO=$1; RUN=$2; OUT=$3
mkdir -p "$OUT"
gh run view "$RUN" -R "leonardosovienski/$REPO" \
  --json databaseId,workflowName,event,headBranch,headSha,status,conclusion,createdAt,url,jobs \
  > "$OUT/${REPO}_run${RUN}.json"
gh run view "$RUN" -R "leonardosovienski/$REPO" --log > "$OUT/${REPO}_run${RUN}.log"
echo "$REPO run $RUN -> $(wc -c < "$OUT/${REPO}_run${RUN}.log") bytes"
