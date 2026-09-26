#!/usr/bin/env bash
# DIAGNÓSTICO (não é evidência de gate): um venv py3.13 por domínio com a wheel final da Etapa A
# (URL + sha256 da attestation), as dependências do uv.lock do final_commit exportadas com hashes
# (--require-hashes) e a wheel rc2 do protocolo construída localmente. Tudo em runtime/envelope-v2.
set -euo pipefail
source "$HOME/predictors/runtime/envelope-v2/env.sh"
WHEEL_PROTOCOL=$1
REPOS=$HOME/predictors/repos
declare -A REPO=([crypto]=cripto-predictor [stocks]=stocks-predictor [brasileirao]=brasileirao-predictor)
declare -A SHA=([crypto]=341d270e4d709150c581c3cd93f4518d483009eb [stocks]=61fc017256ffea815ae96bbe02b847dccdb395cc [brasileirao]=25cdf4d9bb309d33f066fbc6a379f5d98c69f08a)
declare -A URL=(
  [crypto]=https://github.com/leonardosovienski/cripto-predictor/releases/download/v1.2.0rc2/cripto_predictor-1.2.0rc2-py3-none-any.whl
  [stocks]=https://github.com/leonardosovienski/stocks-predictor/releases/download/v0.3.0rc2/stocks_predictor-0.3.0rc2-py3-none-any.whl
  [brasileirao]=https://github.com/leonardosovienski/brasileirao-predictor/releases/download/v0.3.0rc3/brasileirao_predictor-0.3.0rc3-py3-none-any.whl)
declare -A WSHA=([crypto]=6e62f67f0779aef7e913d34b4d3d3d6ed5f88ad882e8fa8372f54c4ab59bc8ee [stocks]=92cb1131b4f0ba0b4572d26cb03a1647e239a17f37514c0db1598797119366a8 [brasileirao]=403e6a022b10e2b6d05ef1828894bf3ad0b1d049301e3dfce9cf79dc262000ea)
for d in crypto stocks brasileirao; do
  src=$RT/diag-src-$d; venv=$RT/venv-diag-$d
  echo "=== $d ${REPO[$d]}@${SHA[$d]}"
  rm -rf "$src"; mkdir -p "$src"
  git -C "$REPOS/${REPO[$d]}" -c core.autocrlf=false archive --format=tar "${SHA[$d]}" | tar -x -C "$src"
  (cd "$src" && uv export --locked --no-dev --no-emit-project --format requirements-txt -o "$RT/diag-req-$d.txt" -q)
  echo "requirements: $(grep -c '^[a-z]' "$RT/diag-req-$d.txt") pacotes; sha256 $(sha256sum "$RT/diag-req-$d.txt" | cut -c1-16)"
  mkdir -p "$RT/wheels"
  whl=$RT/wheels/$(basename "${URL[$d]}")
  test -f "$whl" || curl -sSfL -o "$whl" "${URL[$d]}"
  got=$(sha256sum "$whl" | cut -d' ' -f1)
  echo "wheel ${URL[$d]} sha256 $got"
  test "$got" = "${WSHA[$d]}" || { echo "SHA256 DIVERGENTE (esperado ${WSHA[$d]})"; exit 1; }
  rm -rf "$venv"; uv venv -q --python 3.13 "$venv"
  VIRTUAL_ENV=$venv uv pip install -q --require-hashes -r "$RT/diag-req-$d.txt"
  VIRTUAL_ENV=$venv uv pip install -q --no-deps "$whl" "$WHEEL_PROTOCOL"
  VIRTUAL_ENV=$venv uv pip list 2>/dev/null | grep -i -E 'predictor|cripto|stocks|brasileirao|research'
done
echo DIAG_VENVS=OK
