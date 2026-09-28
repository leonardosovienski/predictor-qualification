#!/usr/bin/env bash
# integration-brasileirao, C0 complementar (item 4.5 do prompt da sessão de 2026-09-27): o que esta missão reutiliza da
# integration-stocks QUALIFIED.
#   1. final_commits de cain e ecosystem-predictor (existem no repositório; relação com o main atual);
#   2. final_wheels desses dois repositórios: download pela url declarada e sha256 conferido;
#   3. descrição do framework qualificado do CAIN (DECISION_POLICY_REPORT.md das integrações anteriores).
# Só leitura: clones bare parciais e downloads num diretório de trabalho. Nenhum conteúdo de domínio do Stocks é lido.
#
# Uso: c0_reuse_stocks.sh <snapshot extraído do ref> <python gerenciado> <dir de trabalho>
set -uo pipefail

SNAP=$1 PY=$2 WORK=$3
OWNER=leonardosovienski
ATT=$SNAP/qualification/integration-stocks/QUALIFICATION_ATTESTATION.json
fails=0
check() { local s=OK; [ "$2" = ok ] || { s=FALHA; fails=$((fails + 1)); }; echo "CHECK $1 $s $3"; }
mkdir -p "$WORK/mirror" "$WORK/downloads/reuse"
echo "run_at $(date -u +%FT%TZ)"
echo "attestation sha256=$(sha256sum "$ATT" | cut -d' ' -f1)"

r=$("$PY" -c 'import json,sys; print(json.load(open(sys.argv[1]))["result"])' "$ATT")
[ "$r" = QUALIFIED ] && check "4.5/integration-stocks-result" ok "$r" || check "4.5/integration-stocks-result" falha "$r"

# 1. final_commits
for repo in cain ecosystem-predictor; do
  sha=$("$PY" -c 'import json,sys; print(next(c["commit_sha"] for c in json.load(open(sys.argv[1]))["final_commits"] if c["repo"]==sys.argv[2]))' "$ATT" "$repo")
  M=$WORK/mirror/$repo.git
  if [ -d "$M" ]; then git -C "$M" fetch -q --tags origin '+refs/heads/*:refs/heads/*'
  else git clone -q --bare --filter=blob:none "https://github.com/$OWNER/$repo.git" "$M"; fi
  if git -C "$M" cat-file -e "$sha^{commit}" 2>/dev/null; then
    check "4.5/final_commit-$repo" ok "$sha"
    main=$(git -C "$M" rev-parse refs/heads/main)
    anc=$(git -C "$M" merge-base --is-ancestor "$sha" "$main" && echo sim || echo nao)
    ahead=$(git -C "$M" rev-list --count "$sha..$main")
    same=$([ "$(git -C "$M" rev-parse "$sha^{tree}")" = "$(git -C "$M" rev-parse "$main^{tree}")" ] && echo sim || echo nao)
    echo "INFO 4.5/main-$repo main=$main final_ancestral_do_main=$anc commits_main_alem_do_final=$ahead mesma_arvore=$same"
    git -C "$M" log --format="INFO 4.5/main-$repo-commit %H %s" "$sha..$main"
  else
    check "4.5/final_commit-$repo" falha "$sha não encontrado"
  fi
done

# 2. final_wheels de cain e ecosystem-predictor
"$PY" - "$ATT" <<'PYEOF' > "$WORK/downloads/reuse/wheels.tsv"
import json, sys
a = json.load(open(sys.argv[1], encoding="utf-8"))
for w in a["final_wheels"]:
    if "/leonardosovienski/cain/" in w["url"] or "/leonardosovienski/ecosystem-predictor/" in w["url"]:
        print(w["name"], w["version"], w["sha256"], w["url"], sep="\t")
PYEOF
while IFS=$'\t' read -r name ver sha url; do
  f=$WORK/downloads/reuse/$(basename "$url")
  rm -f "$f"
  curl -fsSL -o "$f" "$url"; rc=$?
  got=$(sha256sum "$f" 2>/dev/null | cut -d' ' -f1)
  [ "$rc" -eq 0 ] && [ "$got" = "$sha" ] && check "4.5/final_wheel-$name" ok "$ver sha256=$got bytes=$(stat -c %s "$f")" \
    || check "4.5/final_wheel-$name" falha "$ver curl_exit=$rc sha256=$got esperado=$sha"
done < "$WORK/downloads/reuse/wheels.tsv"
echo "INFO 4.5/final_wheels-cain-ecosystem $(wc -l < "$WORK/downloads/reuse/wheels.tsv")"

# 3. descrição do framework
for b in integration-crypto integration-stocks; do
  f=$SNAP/qualification/$b/DECISION_POLICY_REPORT.md
  [ -f "$f" ] && check "4.5/framework-$b-DECISION_POLICY_REPORT" ok "sha256=$(sha256sum "$f" | cut -d' ' -f1)" \
    || check "4.5/framework-$b-DECISION_POLICY_REPORT" falha "ausente"
done

echo "reuse_falhas $fails"
