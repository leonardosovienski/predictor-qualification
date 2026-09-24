#!/usr/bin/env bash
# Revalidação local (PC 2, Ubuntu WSL2) a pedido do dono: reexecuta as verificações determinísticas dos gates
# que não dependem do ambiente de execução (git, hashes, scripts de números). Um log por verificação.
# Saída: ~/predictors/runtime/cripto/revalidacao/local/
set -uo pipefail
export PATH="$HOME/predictors/tools/uv:$PATH" UV_PYTHON_INSTALL_DIR="$HOME/predictors/tools/python" UV_CACHE_DIR="$HOME/predictors/tools/uv-cache" UV_PYTHON_PREFERENCE=only-managed
EV=~/predictors/work/cripto-evidence
QC=$EV/qualification/crypto
SRC=~/predictors/repos/cripto-predictor
WT=~/predictors/work/cripto-cripto-predictor
OUT=~/predictors/runtime/cripto/revalidacao/local; mkdir -p "$OUT"
TMPD=$(mktemp -d -p ~/predictors/runtime/cripto)
stamp() { echo "# $(date -u +%FT%TZ) evidência @ $(git -C $EV rev-parse --short HEAD) ($(git -C $EV rev-parse --abbrev-ref HEAD))"; }

# 1) PROTECTED_ARTIFACTS_UNCHANGED: conjunto regenerado no commit do truth-map == PROTECTED_SET.json; blobs iguais no final e no main
{ stamp
  echo "\$ truth_map.py protected --commit 5fd4e1b (commit do truth-map)"
  python3 $QC/scripts/truth_map.py protected --repo $SRC --commit 5fd4e1b06c79231fd3d9485a1483f3b65e854bea --out $TMPD/ps_5fd4e1b.json
  python3 - "$QC/PROTECTED_SET.json" "$TMPD/ps_5fd4e1b.json" <<'PY'
import json, sys
a, b = (json.load(open(p)) for p in sys.argv[1:3])
print("regenerado == PROTECTED_SET.json (itens e blobs):", a["items"] == b["items"], "| itens:", a["count"], b["count"])
PY
  for c in 341d270e4d709150c581c3cd93f4518d483009eb 174573df4884b5455f9b38ecc933bf48c67ff4df; do
    python3 - "$QC/PROTECTED_SET.json" "$SRC" "$c" <<'PY'
import json, subprocess, sys
ps, repo, commit = json.load(open(sys.argv[1])), sys.argv[2], sys.argv[3]
tree = {}
for line in subprocess.run(["git", "-C", repo, "ls-tree", "-r", commit], capture_output=True, text=True, check=True).stdout.splitlines():
    meta, path = line.split("\t", 1); tree[path] = meta.split()[2]
same = [i["path"] for i in ps["items"] if tree.get(i["path"]) == i["git_blob"]]
bad = [i["path"] for i in ps["items"] if tree.get(i["path"]) != i["git_blob"]]
print(f"commit {commit[:7]}: {len(same)}/{len(ps['items'])} blobs iguais; alterados/ausentes: {bad[:10]}")
PY
  done
  echo "\$ truth_map.py protected --commit 341d270 (itens novos que casam com os globs depois do truth-map)"
  python3 $QC/scripts/truth_map.py protected --repo $SRC --commit 341d270e4d709150c581c3cd93f4518d483009eb --out $TMPD/ps_341d270.json
  python3 - "$QC/PROTECTED_SET.json" "$TMPD/ps_341d270.json" <<'PY'
import json, sys
a, b = (json.load(open(p)) for p in sys.argv[1:3])
pa = {i["path"] for i in a["items"]}; pb = {i["path"] for i in b["items"]}
print("no 341d270 e fora do conjunto:", sorted(pb - pa)[:20], "| do conjunto e ausentes no 341d270:", sorted(pa - pb)[:20])
PY
} > "$OUT/protected_set.log" 2>&1

# 2) LOCK_INTEGRITY: uv lock --check no final_commit (worktree limpo em 341d270)
{ stamp; echo "HEAD=$(git -C $WT rev-parse HEAD) alterações=$(git -C $WT status --porcelain | grep -v '^?? dist/' | wc -l)"; uv --version
  echo "\$ uv lock --check --offline"; ( cd $WT && uv lock --check --offline ); echo "exit=$?"
  echo "\$ uv lock --check (online)"; ( cd $WT && uv lock --check ); echo "exit=$?"
  echo "sha256 uv.lock: $(sha256sum $WT/uv.lock | cut -c1-64)"
} > "$OUT/uv_lock_check.log" 2>&1

# 3) estado científico congelado (prompt §5) no final_commit e no main
{ stamp
  for c in 341d270 174573d; do echo "== $c"; git -C $SRC show $c:charters/scientific_state.json > $TMPD/state_$c.json
    python3 - $TMPD/state_$c.json <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
expected = {"H1": "CLOSED_NO_GO", "H2": "CLOSED_NO_GO", "H3": "CLOSED_NO_GO", "H5": "CLOSED_NO_GO",
            "H4": "CLOSED_INSUFFICIENT_SAMPLE", "H6": "CLOSED_INSUFFICIENT_SAMPLE", "H9": "CLOSED_INSUFFICIENT_SAMPLE",
            "H7": "REGISTERED_NOT_ACTIVATED", "H8": "REGISTERED_NOT_ACTIVATED"}
print("hipóteses:", d["hypotheses"])
print("igual ao esperado do prompt §5:", d["hypotheses"] == expected,
      "| frozen_families:", d["frozen_families"], "(esperado ['funding_oi_hmm_v3'])",
      "| capital_authorized:", d["capital_authorized"])
PY
  done
} > "$OUT/scientific_state.log" 2>&1

# 4) DOMAIN_CONTRACT: sha do contrato no main × attestation; conformidade roda no Actions
{ stamp
  echo "contrato origin/main: $(git -C $EV show origin/main:qualification/crypto/DOMAIN_RESEARCH_CONTRACT.json | sha256sum | cut -c1-64)"
  echo "contrato branch:      $(sha256sum $QC/DOMAIN_RESEARCH_CONTRACT.json | cut -c1-64)"
  python3 -c "import json; print('attestation domain_contract_sha256:', json.load(open('$QC/QUALIFICATION_ATTESTATION.json'))['domain_contract_sha256'])"
  git -C $EV log -1 --format='último commit do contrato no main: %h %ad %s' --date=iso origin/main -- qualification/crypto/DOMAIN_RESEARCH_CONTRACT.json
} > "$OUT/domain_contract.log" 2>&1

# 5) EVIDENCE_CONSISTENCY: números reproduzidos dos logs brutos, byte a byte
{ stamp
  cd $EV
  run() { local name=$1; shift; python3 $QC/scripts/evidence_numbers.py "$@" --out _reval_$name.json > /dev/null 2>&1; echo "evidence_numbers $name exit=$?"; if cmp -s $QC/_reval_$name.json $QC/$name.json; then echo "  $name.json: reproduz byte a byte"; else echo "  $name.json: DIFERENTE"; diff <(python3 -m json.tool $QC/_reval_$name.json) <(python3 -m json.tool $QC/$name.json) | head -20; fi; rm -f $QC/_reval_$name.json; }
  # V1.0: só a invocação padrão (--out EVIDENCE_NUMBERS.json) omite as linhas V1.1; roda num clone descartável
  git clone -q --branch "$(git -C $EV rev-parse --abbrev-ref HEAD)" $EV $TMPD/v10
  ( cd $TMPD/v10 && python3 qualification/crypto/scripts/evidence_numbers.py > /dev/null 2>&1; echo "evidence_numbers EVIDENCE_NUMBERS (invocação padrão, clone descartável) exit=$?" )
  if [ -z "$(git -C $TMPD/v10 status --porcelain qualification/crypto/EVIDENCE_NUMBERS.json)" ]; then echo "  EVIDENCE_NUMBERS.json: reproduz byte a byte"; else echo "  EVIDENCE_NUMBERS.json: DIFERENTE"; fi
  run EVIDENCE_NUMBERS_V1.1 --runtime-run run35925914768 --local v1.1/windows-local --protected v1.1/protected_set_check_341d270.json --ops-summary ops-failure-v1.1/OPS_FAILURE_SUMMARY.json
  run EVIDENCE_NUMBERS_D16 --runtime-run run35925914768 --local v1.1/windows-local --protected v1.1/protected_set_check_341d270.json --ops-summary ops-failure-v1.1/OPS_FAILURE_SUMMARY.json --d16 d16/35978221282
  echo "\$ analyze_ops_failure.py ops-failure-v1.1 run35924606026 (cópia temporária)"
  cp -r $QC/RAW_LOGS/ops-failure-v1.1 $TMPD/ops11
  python3 $QC/scripts/analyze_ops_failure.py $TMPD/ops11 run35924606026 > /dev/null 2>&1; echo "exit=$?"
  f=$(ls -t $TMPD/ops11/*.json 2>/dev/null | head -1); echo "gerado: $(basename "$f")"
  if cmp -s "$f" $QC/RAW_LOGS/ops-failure-v1.1/OPS_FAILURE_SUMMARY.json; then echo "  OPS_FAILURE_SUMMARY (V1.1): reproduz byte a byte"; else echo "  OPS_FAILURE_SUMMARY (V1.1): DIFERENTE"; diff <(python3 -m json.tool "$f") <(python3 -m json.tool $QC/RAW_LOGS/ops-failure-v1.1/OPS_FAILURE_SUMMARY.json) | head -20; fi
} > "$OUT/evidence_numbers_repro.log" 2>&1

# 6) BLOCKERS_ZERO: contagem de FINDINGS × attestation
{ stamp; python3 - "$QC" <<'PY'
import json, sys, collections
qc = sys.argv[1]
f = json.load(open(f"{qc}/FINDINGS.json"))["findings"]
open_ = collections.Counter(x["severity"] for x in f if x["status"] in ("OPEN", "OPEN_BLOCKED", "OPEN_AWAITING_VERDICT"))
print("abertos por severidade:", dict(open_), "| attestation counts:", json.load(open(f"{qc}/QUALIFICATION_ATTESTATION.json"))["counts"])
print("abertos:", [(x["id"], x["severity"]) for x in f if x["status"].startswith("OPEN")])
PY
} > "$OUT/blockers.log" 2>&1

# 7) attestations: attest.py check + conferência no próprio commit
{ stamp; cd $EV
  for a in $QC/QUALIFICATION_ATTESTATION.json $QC/ATTESTATION_PARTIAL_d16.json; do echo "attest.py check $(basename $a): $(~/predictors/runtime/cripto/attest-tools/.venv/bin/python $QC/scripts/attest.py check $a)"; done
  python3 $QC/scripts/d16_crosscheck.py attestations > $TMPD/att.json
  python3 - $TMPD/att.json <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
for a in d["attestations"]:
    name = a["file"].split("/")[-1]
    print(f"{name:58s} {a['commit'][:7]} {a['result']:13s} checked={a['checked']:3d} problemas={len(a['problems'])}")
PY
} > "$OUT/attestations.log" 2>&1

rm -rf "$TMPD"
for f in "$OUT"/*.log; do echo "== $(basename $f)"; grep -vE '^# ' "$f" | head -40; done
