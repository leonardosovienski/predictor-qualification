#!/usr/bin/env bash
# integration-stocks, reemissão 1: reproduz localmente (diagnóstico, NÃO é CI hospedado) os dois passos do job secrets
# do CI Pipeline do stocks-predictor que ficaram pulados no run workflow_dispatch 36363108348 porque o passo do
# gitleaks (histórico de todas as branches) falhou pelo falso positivo de IS-F005:
#   1. "Scan the complete tracked tree including merged code": gitleaks --no-git na árvore do commit (git archive) com o
#      .gitleaks.toml do próprio repo;
#   2. "Prove an exempted file still detects a synthetic token": o mesmo gitleaks tem de achar um token sintético
#      acrescentado a stocks_predictor/trials_gate.py.
# Mesmos comandos e flags do .github/workflows/ci.yml do commit. Usa o gitleaks 8.24.3 oficial já presente em
# ~/predictors/tools/secscan/, com o tar conferido contra o gitleaks_sums.txt da release.
# Ciclo 2: os passos que usavam o python3 do sistema (contar achados, anexar e conferir o token) passam a usar o Python gerenciado em $PY
# (regra "só Python gerenciado"; o desvio da reemissão 1 está registrado no log da missão).
# Uso: PY=<python gerenciado> tree_scan_local.sh <clone do stocks-predictor> <commit> <dir de trabalho fora do checkout> <out_dir>
set -uo pipefail
CLONE=$1 COMMIT=$2 WORK=$3 OUT=$4
PY=${PY:?defina PY com um Python gerenciado}
SEC=$HOME/predictors/tools/secscan
TAR=gitleaks_8.24.3_linux_x64.tar.gz
mkdir -p "$OUT"
echo "run_at $(date -u +%FT%TZ) commit $(git -C "$CLONE" rev-parse "$COMMIT") (diagnóstico local, WSL do PC 2)"
expected=$(grep " $TAR\$" "$SEC/gitleaks_sums.txt" | cut -d' ' -f1)
got=$(sha256sum "$SEC/$TAR" | cut -d' ' -f1)
echo "gitleaks tar sha256 esperado=$expected obtido=$got"
[ -n "$expected" ] && [ "$expected" = "$got" ] || { echo "FALHA: tar do gitleaks não confere"; exit 3; }
rm -rf "$WORK" && mkdir -p "$WORK/bin" "$WORK/tree"
tar -xzf "$SEC/$TAR" -C "$WORK/bin" gitleaks
GL=$WORK/bin/gitleaks
echo "gitleaks $("$GL" version)"
git -C "$CLONE" archive "$COMMIT" | tar -x -C "$WORK/tree"
echo "arquivos rastreados: $(git -C "$CLONE" ls-tree -r --name-only "$COMMIT" | wc -l)"
echo "=== passo 1: árvore completa do commit"
"$GL" detect --no-git --config "$WORK/tree/.gitleaks.toml" --source "$WORK/tree" --redact --exit-code=2 \
  --report-format=sarif --report-path="$OUT/stocks-current-tree.sarif" 2>&1 | grep -v "^\s*$"
rc1=${PIPESTATUS[0]}
echo "passo1_exit $rc1 achados=$("$PY" -c "import json;print(len(json.load(open('$OUT/stocks-current-tree.sarif'))['runs'][0]['results']))")"
echo "=== passo 2: controle (token sintético em stocks_predictor/trials_gate.py)"
"$PY" - "$WORK/tree/stocks_predictor/trials_gate.py" <<'PY'
import secrets
import sys
with open(sys.argv[1], "a", encoding="utf-8") as stream:
    stream.write('\napi_key = "' + secrets.token_urlsafe(32) + '"\n')
PY
"$GL" detect --no-git --config "$WORK/tree/.gitleaks.toml" --source "$WORK/tree" --redact --exit-code=2 \
  --report-format=sarif --report-path="$OUT/stocks-scan-control.sarif" 2>&1 | grep -v "^\s*$"
rc2=${PIPESTATUS[0]}
"$PY" - "$OUT/stocks-scan-control.sarif" <<'PY'
import json
import sys
findings = json.load(open(sys.argv[1]))["runs"][0]["results"]
hit = any(f["ruleId"] == "generic-api-key" and f["locations"][0]["physicalLocation"]["artifactLocation"]["uri"]
          .endswith("stocks_predictor/trials_gate.py") for f in findings)
print(f"controle_detectou_token_sintetico {hit} achados={len(findings)}")
PY
echo "passo2_exit $rc2"
rm -rf "$WORK/tree"
[ "$rc1" -eq 0 ] && [ "$rc2" -eq 2 ] && echo "RESULTADO PASS" || echo "RESULTADO FALHA"
