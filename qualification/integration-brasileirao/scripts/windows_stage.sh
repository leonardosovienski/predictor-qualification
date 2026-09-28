#!/usr/bin/env bash
# integration-brasileirao, fase windows-smoke: prepara no WSL (runtime privado) o que o windows_smoke.ps1 copia para
# C:\QUALIFICACAO\runtime\integration-brasileirao\stage\ (só o PowerShell escreve no Windows).
#   runtime_targets.json; req-cain.txt e req-brasileirao.txt exportados dos uv.lock dos final_commits (--locked,
#   --require-hashes, por `git archive`); brasileirao-predictor.bundle (git bundle do final_commit: o operator_env.py lê
#   o config.yaml por `git show` num clone do próprio Windows, sem mexer em safe.directory); a cópia de
#   qualification/integration-brasileirao e das fixtures V2 congeladas da integration-crypto; STAGE_SHA256SUMS.txt.
# Nenhum dado real vai para o stage (o dado é copiado pelo .ps1 direto da cópia conferida do WSL, com sha256).
# Uso: windows_stage.sh <runtime_targets.json> <stage>
set -euo pipefail
TARGETS=$1 STAGE=$2
HERE="$(cd "$(dirname "$0")" && pwd)"
QC="$(cd "$HERE/.." && pwd)"
P="$HOME/predictors"
REPOS="$P/repos"
export PATH="$P/tools/uv:$PATH" UV_PYTHON_INSTALL_DIR="$P/tools/python" UV_CACHE_DIR="$P/tools/uv-cache" \
  UV_PYTHON_PREFERENCE=only-managed
PY="$(uv python find 3.13)"
field() { "$PY" -c "import json,sys;d=json.load(open(sys.argv[1]));print(d$1)" "$TARGETS"; }
mkdir -p "$STAGE"
[ -z "$(ls -A "$STAGE")" ] || { echo "stage não vazio: $STAGE" >&2; exit 2; }
cp "$TARGETS" "$STAGE/runtime_targets.json"
export_req() {  # repo commit extras out
  local tmp
  tmp=$(mktemp -d)
  git -C "$REPOS/$1" -c core.autocrlf=false archive --format=tar "$2" | tar -x -C "$tmp"
  ( cd "$tmp" && uv export --locked --no-emit-project $3 --format requirements-txt -o "$4" -q )
  rm -rf "$tmp"
  echo "$1 $2 -> $(basename "$4")"
}
export_req cain "$(field "['cain']['commit']")" "--no-dev" "$STAGE/req-cain.txt"
export_req brasileirao-predictor "$(field "['brasileirao']['commit']")" "" "$STAGE/req-brasileirao.txt"
BR_COMMIT="$(field "['brasileirao']['commit']")"
# clone temporário (nada é escrito em ~/predictors/repos): um ref só, no final_commit
CLONE=$(mktemp -d)
git clone -q --no-checkout "$REPOS/brasileirao-predictor" "$CLONE/r"
git -C "$CLONE/r" branch --no-track windows-stage-final "$BR_COMMIT"
git -C "$CLONE/r" bundle create "$STAGE/brasileirao-predictor.bundle" windows-stage-final
git -C "$CLONE/r" bundle verify "$STAGE/brasileirao-predictor.bundle"
rm -rf "$CLONE"
mkdir -p "$STAGE/qualification/integration-crypto/fixtures"
cp -r "$QC" "$STAGE/qualification/integration-brasileirao"
rm -rf "$STAGE/qualification/integration-brasileirao/RAW_LOGS" "$STAGE/qualification/integration-brasileirao/scripts/__pycache__"
cp -r "$QC/../integration-crypto/fixtures/v2" "$STAGE/qualification/integration-crypto/fixtures/v2"
( cd "$STAGE" && find . -type f ! -name STAGE_SHA256SUMS.txt -print0 | sort -z | xargs -0 sha256sum ) \
  > "$STAGE/STAGE_SHA256SUMS.txt"
echo "stage $(wc -l < "$STAGE/STAGE_SHA256SUMS.txt") arquivos; bundle commit $BR_COMMIT"
