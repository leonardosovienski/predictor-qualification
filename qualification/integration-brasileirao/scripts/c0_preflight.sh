#!/usr/bin/env bash
# integration-brasileirao, C0 (núcleo v2.3): confere num ref do predictor-qualification o sha256 do núcleo, o
# MANIFEST.sha256, as decisões e as pré-condições dos prompts da Etapa B, e o sha256 do dado privado.
# Só leitura: extrai o ref por `git archive` num diretório de trabalho e abre o dado só para o sha256.
# A saída tem só hashes, estados e contagens (nenhum registro do dado).
#
# Uso: c0_preflight.sh <clone do predictor-qualification> <ref> <dataset> <python gerenciado> <dir de trabalho>
set -uo pipefail

REPO=$1 REF=$2 DATASET=$3 PY=$4 WORK=$5
EXPECTED_CORE=beaa5feed193356f554922439936ad401c8f177bfd18d8864ca329fae94216fc
EXPECTED_DATA=31f30a4dcf33867d1f3aa3d12337a9a66047e6bff10b9a3fa86aae9ef06c9e43
HERE=$(cd "$(dirname "$0")" && pwd)

sha="$(git -C "$REPO" rev-parse "$REF")" || exit 2
echo "run_at $(date -u +%FT%TZ)"
echo "ref $REF $sha"
echo "python $("$PY" --version 2>&1)"

snap="$WORK/snapshot-$sha"
rm -rf "$snap" && mkdir -p "$snap"
git -C "$REPO" archive --format=tar "$sha" | tar -x -C "$snap" || exit 2

core="$(sha256sum "$snap/qualification/COMMON_QUALIFICATION_CORE.md" | cut -d' ' -f1)"
[ "$core" = "$EXPECTED_CORE" ] && s=OK || s=FALHA
echo "CHECK 3.1/C0.1-core-sha256 $s $core"

echo "--- sha256sum -c MANIFEST.sha256"
(cd "$snap" && sha256sum -c MANIFEST.sha256)
rc=$?
[ "$rc" -eq 0 ] && s=OK || s=FALHA
echo "CHECK 3.3/C0.2-manifest $s exit=$rc linhas=$(grep -c . "$snap/MANIFEST.sha256")"

data="$(sha256sum "$DATASET" | cut -d' ' -f1)"
[ "$data" = "$EXPECTED_DATA" ] && s=OK || s=FALHA
echo "CHECK 3.6/dado-sha256 $s $data bytes=$(stat -c %s "$DATASET") modo=$(stat -c %a "$DATASET")"

"$PY" "$HERE/c0_preconditions.py" "$snap"
