#!/usr/bin/env bash
# integration-crypto, fase publish-candidates (C5): build reprodutível + pré-release nova, sem sobrescrever asset.
#
# Método do HYG-001/D-14 (o mesmo da release do protocolo V2): `git archive` do commit (core.autocrlf=false,
# bytes exatos dos blobs), SOURCE_DATE_EPOCH fixo, duas árvores extraídas separadamente, duas wheels; só publica se
# as duas forem idênticas. A release aponta para o commit (`--target <sha completo>`), é pré-release e leva a wheel
# (e o sdist com WITH_SDIST=1).
# Depois baixa a wheel anonimamente pela URL pública e confere o sha256 e o digest da API.
#
# Uso: publish_rc.sh <clone> <owner/repo> <commit completo> <subdir do pacote ou .> <tag> <título> <notas.md> <out>
# WITH_SDIST=1: também constrói e publica o sdist (as releases do cripto-predictor levam wheel + sdist).
set -euo pipefail
CLONE=$1 REPO=$2 COMMIT=$3 SUBDIR=$4 TAG=$5 TITLE=$6 NOTES=$7 OUT=$8
export SOURCE_DATE_EPOCH=1758240000
[[ "$COMMIT" =~ ^[0-9a-f]{40}$ ]] || { echo "commit precisa ser SHA completo"; exit 2; }
test ! -e "$OUT" || { echo "saída já existe: $OUT"; exit 2; }
if gh release view "$TAG" -R "$REPO" >/dev/null 2>&1 || git -C "$CLONE" ls-remote --exit-code --tags origin "refs/tags/$TAG" >/dev/null; then
  echo "tag/release $TAG já existe: não sobrescrevo"; exit 1
fi
git -C "$CLONE" fetch -q origin
git -C "$CLONE" cat-file -e "$COMMIT^{commit}"
git -C "$CLONE" branch -r --contains "$COMMIT" | grep -q . || { echo "commit $COMMIT não está em nenhuma branch remota"; exit 1; }
mkdir -p "$OUT"
echo "run_at=$(date -u +%FT%TZ) host=$(hostname) (PC 2, WSL) repo=$REPO commit=$COMMIT subdir=$SUBDIR tag=$TAG"
echo "tree=$(git -C "$CLONE" rev-parse "$COMMIT:$SUBDIR") uv=$(uv --version) SOURCE_DATE_EPOCH=$SOURCE_DATE_EPOCH"
for run in a b; do
  src="$OUT/src-$run"; mkdir -p "$src"
  if [ "$SUBDIR" = "." ]; then
    git -C "$CLONE" -c core.autocrlf=false archive --format=tar "$COMMIT" | tar -x -C "$src"
  else
    git -C "$CLONE" -c core.autocrlf=false archive --format=tar "$COMMIT" "$SUBDIR" | tar -x -C "$src"
  fi
  if [ "${WITH_SDIST:-0}" = 1 ]; then kinds=""; else kinds="--wheel"; fi
  uv build --python 3.13 $kinds --no-cache --out-dir "$OUT/dist-$run" "$src/$SUBDIR" > "$OUT/build-$run.log" 2>&1
  tail -1 "$OUT/build-$run.log"
done
( cd "$OUT/dist-a" && sha256sum * ) > "$OUT/sha256-a.txt"
( cd "$OUT/dist-b" && sha256sum * ) > "$OUT/sha256-b.txt"
cat "$OUT/sha256-a.txt" "$OUT/sha256-b.txt"
unzip -p "$OUT"/dist-a/*.whl '*.dist-info/WHEEL'
if diff "$OUT/sha256-a.txt" "$OUT/sha256-b.txt"; then echo "REPRODUCIBLE=YES"; else echo "REPRODUCIBLE=NO"; exit 1; fi
WHL=$(ls "$OUT"/dist-a/*.whl)
EXPECTED=$(sha256sum "$WHL" | cut -d' ' -f1)
echo "\$ gh release create $TAG -R $REPO --target $COMMIT --prerelease --title '$TITLE' --notes-file $(basename "$NOTES") $(basename "$WHL")"
ASSETS=("$WHL"); [ "${WITH_SDIST:-0}" = 1 ] && ASSETS+=("$(ls "$OUT"/dist-a/*.tar.gz)")
gh release create "$TAG" -R "$REPO" --target "$COMMIT" --prerelease --title "$TITLE" --notes-file "$NOTES" "${ASSETS[@]}"
echo "release_exit=$?"
mkdir -p "$OUT/download-verify"
URL="https://github.com/$REPO/releases/download/$TAG/$(basename "$WHL")"
echo "\$ curl -sSfL (anônimo) $URL"
env -u GH_TOKEN -u GITHUB_TOKEN curl -sSfL -o "$OUT/download-verify/$(basename "$WHL")" "$URL"
GOT=$(sha256sum "$OUT/download-verify/$(basename "$WHL")" | cut -d' ' -f1)
echo "downloaded_sha256=$GOT expected=$EXPECTED"
echo "api: $(gh api "repos/$REPO/releases/tags/$TAG" -q '[.prerelease, (.assets[] | "\(.name) \(.digest) \(.size)")] | @tsv')"
echo "tag -> $(git -C "$CLONE" ls-remote origin "refs/tags/$TAG" | cut -f1)"
test "$GOT" = "$EXPECTED" && echo "RELEASE_VERIFIED=YES url=$URL sha256=$EXPECTED"
