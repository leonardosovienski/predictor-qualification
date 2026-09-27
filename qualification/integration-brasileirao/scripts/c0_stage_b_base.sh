#!/usr/bin/env bash
# integration-brasileirao, C0 complementar (sessão de 2026-09-27): itens do pré-voo que o c0_preflight.sh não cobre.
#   4.4  artefatos compartilhados do envelope V2 no ref (existência + sha256)
#   4.5  attestations das integrações anteriores (integration-stocks, integration-crypto) e o que delas seria reutilizado
#   4.6  base do Brasileirão: runtime_target × attestation da Etapa A × STACK_BASELINE_V2.0 × tag/asset da release
#        × ancestralidade e igualdade de árvore 25cdf4d = d80a4ed = main atual
#   4.7  PROVISION_RECEIPT.json (prova do host owner_linux, D-19)
#   4.8  wheel do protocolo V2 indicada em ENVELOPE_V2_FREEZE.json: download pela URL + sha256
# Só leitura: repositórios de código consultados por clone bare parcial num diretório de trabalho; downloads no mesmo
# diretório. A saída tem só hashes, estados e contagens (nenhum registro do dado).
#
# Uso: c0_stage_b_base.sh <snapshot extraído do ref> <python gerenciado> <dir de trabalho> <PROVISION_RECEIPT.json>
set -uo pipefail

SNAP=$1 PY=$2 WORK=$3 RECEIPT=$4
BASE=25cdf4d9bb309d33f066fbc6a379f5d98c69f08a
MERGE=d80a4edee94ca0219ec308911d56628499792885
TREE=88b1efa6167655b21b9603c144a423755ef8fb46
WHEEL=403e6a022b10e2b6d05ef1828894bf3ad0b1d049301e3dfce9cf79dc262000ea
SDIST=306d2149424c53b48d74000b392e8785afc29f48710bd3fa2a04e85eb13f59b4
OWNER=leonardosovienski
fails=0
check() { # id ok|falha detalhe
  local s=OK; [ "$2" = ok ] || { s=FALHA; fails=$((fails + 1)); }
  echo "CHECK $1 $s $3"
}
Q=$SNAP/qualification
mkdir -p "$WORK/mirror" "$WORK/downloads"
echo "run_at $(date -u +%FT%TZ)"

# 4.4
for f in ENVELOPE_V2_FREEZE.json STACK_BASELINE_V2.0.json; do
  if [ -f "$Q/shared/$f" ]; then check "4.4/$f" ok "sha256=$(sha256sum "$Q/shared/$f" | cut -d' ' -f1)"
  else check "4.4/$f" falha "ausente"; fi
done

# 4.5: attestations das integrações anteriores e estado registrado por elas
for b in integration-stocks integration-crypto; do
  att=$Q/$b/QUALIFICATION_ATTESTATION.json
  if [ -f "$att" ]; then
    r=$("$PY" -c 'import json,sys; print(json.load(open(sys.argv[1]))["result"])' "$att")
    [ "$r" = QUALIFIED ] && check "4.5/$b-attestation" ok "result=$r" || check "4.5/$b-attestation" falha "result=$r"
  else
    parts=$(ls "$Q/$b" 2>/dev/null | grep -c '^ATTESTATION_PARTIAL_' || true)
    st=$("$PY" - "$Q/$b/FINDINGS.json" <<'PYEOF'
import json, sys
try:
    d = json.load(open(sys.argv[1], encoding="utf-8"))
except FileNotFoundError:
    print("FINDINGS.json ausente"); raise SystemExit
c0 = d.get("c0") or {}
print(f"c0.state={c0.get('state')} findings={len(d.get('findings') or [])}")
PYEOF
)
    check "4.5/$b-attestation" falha "QUALIFICATION_ATTESTATION.json ausente; parciais=$parts; $st"
  fi
done
if [ -f "$Q/integration-stocks/QUALIFICATION_ATTESTATION.json" ]; then
  "$PY" - "$Q/integration-stocks/QUALIFICATION_ATTESTATION.json" <<'PYEOF'
import json, sys
a = json.load(open(sys.argv[1], encoding="utf-8"))
for c in a.get("final_commits", []):
    print(f"INFO 4.5/stocks-final_commit {c.get('repo')} {c.get('commit_sha')}")
for w in a.get("final_wheels", []):
    print(f"INFO 4.5/stocks-final_wheel {w.get('name')} {w.get('version')} {w.get('sha256')}")
PYEOF
else
  echo "INFO 4.5/reuso final_commits/final_wheels de cain e ecosystem-predictor: indisponíveis (sem attestation QUALIFIED da integration-stocks)"
fi

# 4.6(a) runtime_target e attestation da Etapa A
"$PY" - "$Q" "$BASE" "$WHEEL" "$SDIST" <<'PYEOF'
import hashlib, json, sys
from pathlib import Path
q, base, wheel, sdist = Path(sys.argv[1]), *sys.argv[2:]
fails = 0
def check(i, ok, d):
    global fails
    fails += not ok
    print(f"CHECK {i} {'OK' if ok else 'FALHA'} {d}")
t = json.loads((q / "brasileirao/runtime_target.json").read_text(encoding="utf-8"))
check("4.6a/runtime_target", t["commit"] == base and t["version"] == "0.3.0rc3" and t["wheel_sha256"] == wheel
      and t.get("sdist_sha256") == sdist,
      f"commit={t['commit']} version={t['version']} wheel={t['wheel_sha256']} sdist={t.get('sdist_sha256')}")
raw = (q / "brasileirao/QUALIFICATION_ATTESTATION.json").read_bytes()
a = json.loads(raw)
fc = {c["repo"]: c["commit_sha"] for c in a["final_commits"]}
fw = {w["name"]: w["sha256"] for w in a["final_wheels"]}
check("4.6a/attestation-etapaA", a["result"] == "QUALIFIED" and fc.get("brasileirao-predictor") == base
      and fw.get("brasileirao-predictor") == wheel,
      f"sha256={hashlib.sha256(raw).hexdigest()} result={a['result']} commit={fc.get('brasileirao-predictor')} wheel={fw.get('brasileirao-predictor')}")
# 4.6(b) STACK_BASELINE_V2.0
sb = json.loads((q / "shared/STACK_BASELINE_V2.0.json").read_text(encoding="utf-8"))
def find(o):
    if isinstance(o, dict):
        if "brasileirao" in o and isinstance(o["brasileirao"], dict) and "runtime_target" in o["brasileirao"]:
            return o["brasileirao"]
        for v in o.values():
            r = find(v)
            if r: return r
    elif isinstance(o, list):
        for v in o:
            r = find(v)
            if r: return r
e = find(sb)
rt = e["runtime_target"]
bfc = {c["repo"]: c["commit_sha"] for c in e["final_commits"]}
bfw = {w["name"]: w["sha256"] for w in e["final_wheels"]}
check("4.6b/STACK_BASELINE_V2.0", rt["commit"] == base and rt["wheel_sha256"] == wheel
      and bfc.get("brasileirao-predictor") == base and bfw.get("brasileirao-predictor") == wheel,
      f"runtime_target.commit={rt['commit']} wheel={rt['wheel_sha256']} final_commit={bfc.get('brasileirao-predictor')} final_wheel={bfw.get('brasileirao-predictor')}")
ops = {w["name"]: (w["version"], w["sha256"][:8]) for w in e["final_wheels"]}
print(f"INFO 4.6b/final_wheels {ops}")
print(f"PYFAILS {fails}")
PYEOF

# 4.6(c) tag e asset da release
M=$WORK/mirror/brasileirao-predictor.git
if [ -d "$M" ]; then git -C "$M" fetch -q --tags origin '+refs/heads/*:refs/heads/*'
else git clone -q --bare --filter=blob:none "https://github.com/$OWNER/brasileirao-predictor.git" "$M"; fi
tagc=$(git -C "$M" rev-parse "v0.3.0rc3^{commit}" 2>/dev/null)
[ "$tagc" = "$BASE" ] && check "4.6c/tag-v0.3.0rc3" ok "commit=$tagc" || check "4.6c/tag-v0.3.0rc3" falha "commit=$tagc"
gh release view v0.3.0rc3 -R "$OWNER/brasileirao-predictor" --json tagName,isPrerelease,assets \
  --jq '"INFO 4.6c/release prerelease=\(.isPrerelease) " + ([.assets[] | "\(.name)=\(.digest)"] | join(" "))'
rm -f "$WORK/downloads/brasileirao_predictor-0.3.0rc3-py3-none-any.whl"
gh release download v0.3.0rc3 -R "$OWNER/brasileirao-predictor" -p 'brasileirao_predictor-0.3.0rc3-py3-none-any.whl' -D "$WORK/downloads" 2>&1
w=$(sha256sum "$WORK/downloads/brasileirao_predictor-0.3.0rc3-py3-none-any.whl" | cut -d' ' -f1)
[ "$w" = "$WHEEL" ] && check "4.6c/asset-wheel" ok "sha256=$w" || check "4.6c/asset-wheel" falha "sha256=$w"

# 4.6(d) ancestralidade e árvores
main=$(git -C "$M" rev-parse refs/heads/main)
echo "INFO 4.6d/main $main"
git -C "$M" merge-base --is-ancestor "$BASE" "$main" && check "4.6d/base-ancestral-do-main" ok "$BASE" || check "4.6d/base-ancestral-do-main" falha "$BASE"
tb=$(git -C "$M" rev-parse "$BASE^{tree}"); tm=$(git -C "$M" rev-parse "$MERGE^{tree}"); tmain=$(git -C "$M" rev-parse "$main^{tree}")
[ "$tb" = "$TREE" ] && [ "$tm" = "$TREE" ] && check "4.6d/arvore-25cdf4d=d80a4ed" ok "$tb $tm" || check "4.6d/arvore-25cdf4d=d80a4ed" falha "$tb $tm"
if [ "$main" = "$MERGE" ]; then echo "INFO 4.6d/main-avancou nao (main = d80a4ed)"
else
  n=$(git -C "$M" rev-list --count "$MERGE..$main")
  echo "INFO 4.6d/main-avancou sim commits_depois_de_d80a4ed=$n arvore_main=$tmain igual_base=$([ "$tmain" = "$TREE" ] && echo sim || echo nao)"
  git -C "$M" diff --stat "$MERGE" "$main" | tail -n 1 | sed 's/^/INFO 4.6d\/diff /'
  ad=$(git -C "$M" diff --name-only "$MERGE" "$main" -- brasileirao_predictor/adapters/ | wc -l)
  echo "INFO 4.6d/diff-em-adapters $ad"
fi

# 4.7 PROVISION_RECEIPT
if [ -f "$RECEIPT" ]; then
  "$PY" - "$RECEIPT" <<'PYEOF'
import hashlib, json, sys
raw = open(sys.argv[1], "rb").read()
d = json.loads(raw)
print(f"CHECK 4.7/PROVISION_RECEIPT OK sha256={hashlib.sha256(raw).hexdigest()} chaves={sorted(d)}")
PYEOF
else check "4.7/PROVISION_RECEIPT" falha "ausente"; fi

# 4.8 wheel do protocolo V2
read -r url sha < <("$PY" -c 'import json,sys; w=json.load(open(sys.argv[1]))["protocol"]["wheel"]; print(w["url"], w["sha256"])' "$Q/shared/ENVELOPE_V2_FREEZE.json")
f=$WORK/downloads/$(basename "$url")
rm -f "$f"
curl -fsSL -o "$f" "$url"; rc=$?
got=$(sha256sum "$f" 2>/dev/null | cut -d' ' -f1)
[ "$rc" -eq 0 ] && [ "$got" = "$sha" ] && check "4.8/protocolo-V2-wheel" ok "url=$url sha256=$got bytes=$(stat -c %s "$f")" \
  || check "4.8/protocolo-V2-wheel" falha "url=$url curl_exit=$rc sha256=$got esperado=$sha"

echo "sh_falhas $fails (as de 4.6a/4.6b estão na linha PYFAILS)"
