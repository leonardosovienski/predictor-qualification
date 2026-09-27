#!/usr/bin/env bash
# Publica a pré-release predictor-research-protocol-v2.0.0rc2 depois do merge do ecosystem-predictor#29.
# Nunca sobrescreve asset: aborta se a tag ou a release já existirem.
set -euo pipefail
source "$HOME/predictors/runtime/envelope-v2/env.sh"
REPO=leonardosovienski/ecosystem-predictor
TAG=predictor-research-protocol-v2.0.0rc2
EXPECTED=34a1e4121e4085b901e3bd96552e2f5b4067c5e6af5e99dc1c26d6276fc7c820
PKG_TREE_PR=4a7c66e75597fb9c65c4c9a297ae164addce78ea
state=$(gh pr view 29 -R $REPO --json state -q .state)
test "$state" = MERGED || { echo "PR #29 não está MERGED ($state)"; exit 1; }
M=$(gh pr view 29 -R $REPO --json mergeCommit -q .mergeCommit.oid)
git -C "$EC" fetch origin -q
git -C "$EC" merge-base --is-ancestor "$M" origin/main || { echo "merge $M fora do origin/main"; exit 1; }
echo "merge_commit=$M origin_main=$(git -C "$EC" rev-parse origin/main)"
echo "package_tree_at_merge=$(git -C "$EC" rev-parse "$M:packages/research-protocol") package_tree_pr=$PKG_TREE_PR"
if gh release view $TAG -R $REPO >/dev/null 2>&1 || git -C "$EC" ls-remote --exit-code --tags origin "refs/tags/$TAG" >/dev/null; then
  echo "tag/release $TAG já existe: não sobrescrevo"; exit 1
fi
OUT=$RT/build-rc2-${M:0:7}
bash "$RT/build_protocol_v2.sh" "$EC" "$M" "$OUT" > "$RT/raw/build_protocol_v2_rc2_${M:0:7}.log" 2>&1
grep -E 'REPRODUCIBLE' "$RT/raw/build_protocol_v2_rc2_${M:0:7}.log"
WHL=$(ls "$OUT"/dist-a/*.whl)
GOT=$(sha256sum "$WHL" | cut -d' ' -f1)
test "$GOT" = "$EXPECTED" || { echo "wheel do merge $GOT != $EXPECTED (build do PR)"; exit 1; }
bash "$RT/suite_protocol_v2.sh" "$EC" "$M" "$RT/suite-${M:0:7}" > "$RT/raw/suite_protocol_v2_${M:0:7}.log" 2>&1
grep -E 'passed|SUITE_EXIT' "$RT/raw/suite_protocol_v2_${M:0:7}.log"
{
  echo "\$ gh release create $TAG -R $REPO --target $M --prerelease --title 'predictor-research-protocol 2.0.0rc2' --notes-file release_notes_rc2.md $(basename "$WHL")"
  gh release create $TAG -R $REPO --target "$M" --prerelease --title "predictor-research-protocol 2.0.0rc2" \
    --notes-file "$RT/release_notes_rc2.md" "$WHL"
  echo "exit=$?"
} 2>&1 | tee "$RT/raw/release_publish_rc2.log"
mkdir -p "$RT/download-verify"
URL=https://github.com/$REPO/releases/download/$TAG/$(basename "$WHL")
{
  echo "\$ curl -sSfL (anônimo) $URL"
  env -u GH_TOKEN -u GITHUB_TOKEN curl -sSfL -o "$RT/download-verify/$(basename "$WHL")" "$URL"; echo "exit=$?"
  sha256sum "$RT/download-verify/$(basename "$WHL")"
  echo "digest, tamanho e pré-release pela API:"
  gh api repos/$REPO/releases/tags/$TAG -q '.prerelease, (.assets[] | "\(.name) \(.digest) \(.size)")'
  echo "tag -> commit:"
  git -C "$EC" ls-remote origin "refs/tags/$TAG" "refs/tags/$TAG^{}"
} 2>&1 | tee "$RT/raw/release_download_verify_rc2.log"
test "$(sha256sum "$RT/download-verify/$(basename "$WHL")" | cut -d' ' -f1)" = "$EXPECTED" && echo "RELEASE_VERIFIED=YES merge=$M"
