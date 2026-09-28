#!/usr/bin/env bash
# integration-stocks, fase publish-candidates (C5): pré-release do stocks-predictor pelo processo do próprio repositório
# (tools/reproducible_build.py: checkout limpo e commitado, duas builds wheel + sdist com os mesmos bytes,
# SOURCE_DATE_EPOCH = data do commit, ferramentas de build de tools/build-requirements.txt por hash), como a v0.3.0rc2.
# Nunca sobrescreve tag nem asset. Publica wheel, sdist e build-receipt.json; a release aponta para o commit
# (--target <sha completo>). Depois baixa a wheel anonimamente pela URL pública e confere o sha256 e o digest da API.
#
# Uso: publish_stocks_rc.sh <commit completo> <tag> <título> <notas.md> <out>
set -euo pipefail
COMMIT=$1 TAG=$2 TITLE=$3 NOTES=$4 OUT=$5
REPO=leonardosovienski/stocks-predictor
[[ "$COMMIT" =~ ^[0-9a-f]{40}$ ]] || { echo "commit precisa ser SHA completo"; exit 2; }
test ! -e "$OUT" || { echo "saída já existe: $OUT"; exit 2; }
if gh release view "$TAG" -R "$REPO" >/dev/null 2>&1 || git ls-remote --exit-code --tags "https://github.com/$REPO.git" "refs/tags/$TAG" >/dev/null; then
  echo "tag/release $TAG já existe: não sobrescrevo"; exit 1
fi
mkdir -p "$OUT"
echo "run_at=$(date -u +%FT%TZ) host=$(hostname) (PC 2, WSL) repo=$REPO commit=$COMMIT tag=$TAG uv=$(uv --version)"
git clone -q "https://github.com/$REPO.git" "$OUT/src"
git -C "$OUT/src" -c advice.detachedHead=false checkout -q "$COMMIT"
git -C "$OUT/src" branch -r --contains "$COMMIT" | grep -q . || { echo "commit não está em nenhuma branch remota"; exit 1; }
cd "$OUT/src"
echo "head=$(git rev-parse HEAD) tree=$(git rev-parse HEAD^{tree}) clean=$(git status --porcelain | wc -l)"
uv sync --locked --all-extras --python 3.13 > "$OUT/uv_sync.log" 2>&1
uv pip install --python .venv/bin/python --require-hashes --no-deps --only-binary :all: -r tools/build-requirements.txt > "$OUT/build_tools.log" 2>&1
git status --porcelain
uv run --no-sync python tools/reproducible_build.py | tee "$OUT/reproducible_build.log"
WHL=$(ls dist/*.whl); SDIST=$(ls dist/*.tar.gz)
sha256sum dist/* build-receipt.json | tee "$OUT/SHA256SUMS"
EXPECTED=$(sha256sum "$WHL" | cut -d' ' -f1)
echo "\$ gh release create $TAG -R $REPO --target $COMMIT --prerelease --title '$TITLE' --notes-file $(basename "$NOTES") $(basename "$WHL") $(basename "$SDIST") build-receipt.json"
gh release create "$TAG" -R "$REPO" --target "$COMMIT" --prerelease --title "$TITLE" --notes-file "$NOTES" "$WHL" "$SDIST" build-receipt.json
echo "release_exit=$?"
mkdir -p "$OUT/download-verify"
URL="https://github.com/$REPO/releases/download/$TAG/$(basename "$WHL")"
echo "\$ curl -sSfL (anônimo) $URL"
env -u GH_TOKEN -u GITHUB_TOKEN curl -sSfL -o "$OUT/download-verify/$(basename "$WHL")" "$URL"
GOT=$(sha256sum "$OUT/download-verify/$(basename "$WHL")" | cut -d' ' -f1)
echo "downloaded_sha256=$GOT expected=$EXPECTED"
echo "api: $(gh api "repos/$REPO/releases/tags/$TAG" -q '[.prerelease, (.assets[] | "\(.name) \(.digest) \(.size)")] | @tsv')"
echo "tag -> $(git ls-remote "https://github.com/$REPO.git" "refs/tags/$TAG" | cut -f1)"
test "$GOT" = "$EXPECTED" && echo "RELEASE_VERIFIED=YES url=$URL sha256=$EXPECTED"
