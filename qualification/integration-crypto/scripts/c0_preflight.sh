#!/usr/bin/env bash
# integration-crypto, C0 (núcleo v2.3) + pré-voo do prompt da sessão (itens 4.1–4.7).
# Confere num ref do predictor-qualification: sha256 do núcleo, MANIFEST.sha256 num snapshot `git archive`,
# D-16/D-22, artefatos compartilhados, C0.3, §1 dos prompts; a base do cripto (runtime_target × STACK_BASELINE_V2.0
# × tag/asset da release × igualdade de árvore 341d270 = 174573d) e a release congelada do protocolo V2 por URL + sha256.
# Só leitura nos clones; baixa as wheels num diretório de trabalho e confere o sha256. Não usa API da Binance.
#
# Uso: c0_preflight.sh <clone predictor-qualification> <ref> <clone cripto-predictor> <clone ecosystem-predictor>
#                      <python gerenciado> <dir de trabalho>
set -uo pipefail

REPO=$1 REF=$2 CRIPTO=$3 ECO=$4 PY=$5 WORK=$6
EXPECTED_CORE=beaa5feed193356f554922439936ad401c8f177bfd18d8864ca329fae94216fc
BASE=341d270e4d709150c581c3cd93f4518d483009eb
SQUASH=174573d
EXPECTED_TREE=22dd6a860939424393bd232ad1c59ff18442cb85
HERE=$(cd "$(dirname "$0")" && pwd)

sha="$(git -C "$REPO" rev-parse "$REF")" || exit 2
echo "run_at $(date -u +%FT%TZ)"
echo "host $(hostname) (PC 2, WSL $(uname -r))"
echo "ref $REF $sha"
echo "python $("$PY" --version 2>&1) $PY"

snap="$WORK/snapshot-$sha"
rm -rf "$snap" && mkdir -p "$snap"
git -C "$REPO" archive --format=tar "$sha" | tar -x -C "$snap" || exit 2

core="$(sha256sum "$snap/qualification/COMMON_QUALIFICATION_CORE.md" | cut -d' ' -f1)"
[ "$core" = "$EXPECTED_CORE" ] && s=OK || s=FALHA
echo "CHECK 4.1/C0.1-core-sha256 $s $core"

echo "--- sha256sum -c MANIFEST.sha256 (snapshot git archive)"
(cd "$snap" && sha256sum -c MANIFEST.sha256)
rc=$?
[ "$rc" -eq 0 ] && s=OK || s=FALHA
echo "CHECK 4.3/C0.2-manifest $s exit=$rc linhas=$(grep -c . "$snap/MANIFEST.sha256")"

echo "--- cripto-predictor (clone $CRIPTO, só leitura)"
git -C "$CRIPTO" fetch -q origin --tags || echo "AVISO fetch cripto falhou"
tag_commit="$(git -C "$CRIPTO" rev-parse 'refs/tags/v1.2.0rc2^{commit}' 2>/dev/null)"
remote_tag="$(git -C "$CRIPTO" ls-remote origin refs/tags/v1.2.0rc2 | cut -f1)"
[ "$tag_commit" = "$BASE" ] && [ "$remote_tag" = "$BASE" ] && s=OK || s=FALHA
echo "CHECK 4.6c/tag-v1.2.0rc2 $s local=$tag_commit remoto=$remote_tag"
t1="$(git -C "$CRIPTO" rev-parse "$BASE^{tree}")"
t2="$(git -C "$CRIPTO" rev-parse "$SQUASH^{tree}")"
squash_full="$(git -C "$CRIPTO" rev-parse "$SQUASH^{commit}")"
[ "$t1" = "$EXPECTED_TREE" ] && [ "$t2" = "$EXPECTED_TREE" ] && s=OK || s=FALHA
echo "CHECK 4.6d/tree-igual $s $BASE=$t1 $squash_full=$t2"
main="$(git -C "$CRIPTO" rev-parse origin/main)"
if git -C "$CRIPTO" merge-base --is-ancestor "$BASE" "$main"; then anc=sim; else anc=nao; fi
git -C "$CRIPTO" merge-base --is-ancestor "$squash_full" "$main" && sq_anc=sim || sq_anc=nao
echo "INFO 5.1/main $main base_ancestral_do_main=$anc squash_ancestral_do_main=$sq_anc"
echo "INFO 5.1/commits_squash..main $(git -C "$CRIPTO" rev-list --count "$squash_full..$main")"
git -C "$CRIPTO" log --format='INFO 5.1/commit %H %s' "$squash_full..$main"
echo "INFO 5.1/arquivos_em_adapters_mudados $(git -C "$CRIPTO" diff --name-only "$squash_full" "$main" -- GarimpoInvestimentos/adapters/ | grep -c .)"
echo "INFO 5.1/arquivos_mudados_total $(git -C "$CRIPTO" diff --name-only "$squash_full" "$main" | grep -c .)"
git -C "$CRIPTO" diff --name-only "$squash_full" "$main" | awk -F/ '{print $1}' | sort | uniq -c | sed 's/^/INFO 5.1\/topo /'
echo "INFO 5.1/pyproject_version_main $(git -C "$CRIPTO" show "$main:pyproject.toml" | grep -m1 '^version')"
echo "INFO 5.1/pyproject_version_base $(git -C "$CRIPTO" show "$BASE:pyproject.toml" | grep -m1 '^version')"

echo "--- ecosystem-predictor (clone $ECO, só leitura)"
git -C "$ECO" fetch -q origin --tags || echo "AVISO fetch ecosystem falhou"
echo "INFO 4.7/tag-protocol-v2.0.0rc2 $(git -C "$ECO" rev-parse 'refs/tags/predictor-research-protocol-v2.0.0rc2^{commit}' 2>/dev/null)"

wheels="$WORK/wheels" && mkdir -p "$wheels"
"$PY" "$HERE/c0_preconditions.py" "$snap" "$wheels" "$tag_commit" "$(git -C "$ECO" rev-parse 'refs/tags/predictor-research-protocol-v2.0.0rc2^{commit}' 2>/dev/null)"
