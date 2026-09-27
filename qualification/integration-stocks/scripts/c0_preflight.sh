#!/usr/bin/env bash
# integration-stocks, C0 (núcleo v2.3) = pré-voo 4.1–4.7 do prompt da sessão de 2026-09-27.
# Só leitura: extrai o ref do predictor-qualification por `git archive` num diretório de trabalho, confere
# núcleo e MANIFEST e baixa por URL a wheel do Stocks (v0.3.0rc2) e a do protocolo V2 congelado; o resto
# (decisões, pré-condições, base do Stocks, sha256 dos downloads) fica em c0_preconditions.py.
# A saída tem só hashes, estados e contagens.
#
# Uso: c0_preflight.sh <clone do predictor-qualification> <ref> <clone do stocks-predictor> <python gerenciado> <dir de trabalho>
set -uo pipefail

REPO=$1 REF=$2 STOCKS=$3 PY=$4 WORK=$5
EXPECTED_CORE=beaa5feed193356f554922439936ad401c8f177bfd18d8864ca329fae94216fc
HERE=$(cd "$(dirname "$0")" && pwd)

sha="$(git -C "$REPO" rev-parse "$REF")" || exit 2
echo "run_at $(date -u +%FT%TZ)"
echo "ref $REF $sha"
echo "python $("$PY" --version 2>&1)"
echo "stocks_origin_main $(git -C "$STOCKS" rev-parse origin/main)"

snap="$WORK/snapshot-$sha"
rm -rf "$snap" && mkdir -p "$snap"
git -C "$REPO" archive --format=tar "$sha" | tar -x -C "$snap" || exit 2

core="$(sha256sum "$snap/qualification/COMMON_QUALIFICATION_CORE.md" | cut -d' ' -f1)"
[ "$core" = "$EXPECTED_CORE" ] && s=OK || s=FALHA
echo "CHECK 4.1/C0.1-core-sha256 $s $core"

echo "--- sha256sum -c MANIFEST.sha256"
(cd "$snap" && sha256sum -c MANIFEST.sha256)
rc=$?
[ "$rc" -eq 0 ] && s=OK || s=FALHA
echo "CHECK 4.3/C0.2-manifest $s exit=$rc linhas=$(grep -c . "$snap/MANIFEST.sha256")"

# 4.6(c) e 4.7: download por URL (a URL vem do main; o sha256 é conferido no .py)
dl="$WORK/downloads"
mkdir -p "$dl"
download() { # <rótulo> <url>
  local out="$dl/$(basename "$2")"
  rm -f "$out"
  if curl -fsSL --retry 3 -o "$out" "$2"; then
    echo "DOWNLOAD $1 OK url=$2 bytes=$(stat -c %s "$out")"
  else
    echo "DOWNLOAD $1 FALHA url=$2"
  fi
}
download stocks-wheel "$("$PY" -c 'import json,sys;print(json.load(open(sys.argv[1]))["wheel_url"])' "$snap/qualification/stocks/runtime_target.json")"
download protocol-wheel "$("$PY" -c 'import json,sys;print(json.load(open(sys.argv[1]))["protocol"]["wheel"]["url"])' "$snap/qualification/shared/ENVELOPE_V2_FREEZE.json")"

"$PY" "$HERE/c0_preconditions.py" "$snap" "$STOCKS" "$dl"
