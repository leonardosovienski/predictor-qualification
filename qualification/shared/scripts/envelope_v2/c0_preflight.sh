#!/usr/bin/env bash
# C0 da preparação do envelope V2 (núcleo v2.3 C0 + pré-condições do prompt_preparacao_envelope_v2_rev8.md),
# rodado na raiz de um worktree destacado do origin/main do predictor-qualification.
# Uso: c0_preflight.sh <worktree do origin/main> <python gerenciado>
set -uo pipefail
W=$1; PY=$2
cd "$W"
echo "predictor-qualification HEAD=$(git rev-parse HEAD) em $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "== C0.1 núcleo"; sha256sum qualification/COMMON_QUALIFICATION_CORE.md
echo "esperado beaa5feed193356f554922439936ad401c8f177bfd18d8864ca329fae94216fc (v2.3)"
echo "== C0.2 MANIFEST"; sha256sum -c MANIFEST.sha256; echo "manifest_rc=$?"
"$PY" - <<'PY'
import hashlib, json
def load(p): return json.load(open(p, encoding="utf-8"))
print("== C0.3 arquivos")
dec = {d["decision_id"]: d["status"] for d in load("qualification/DECISIONS.json")["decisions"]}
print("D-22:", dec.get("D-22"))
hyg = load("qualification/HYGIENE.json")
items = hyg.get("items", hyg) if isinstance(hyg, dict) else hyg
statuses = [i["status"] for i in items] if isinstance(items, list) else []
print("HYGIENE:", len(statuses), "itens;", sorted(set(statuses)))
print("== C0.4 pré-condições do prompt")
for m in ("crypto", "brasileirao", "stocks"):
    raw = open(f"qualification/{m}/QUALIFICATION_ATTESTATION.json", "rb").read()
    att = json.loads(raw)
    contract = hashlib.sha256(open(f"qualification/{m}/DOMAIN_RESEARCH_CONTRACT.json", "rb").read()).hexdigest()
    print(m, "result=" + att["result"], "attestation=" + hashlib.sha256(raw).hexdigest(),
          "contract=" + contract, "domain_contract_sha256_ok=" + str(att["domain_contract_sha256"] == contract),
          "ops=" + next(w["sha256"] for w in att["final_wheels"] if (w.get("package") or w.get("name")) == "predictor-ops"))
issues = load("qualification/shared/SHARED_ISSUES.json")["issues"]
for i in issues:
    v = i.get("verdict", {})
    print(i["issue_id"], i["status"], "wheel=" + i["wheel_sha256"], "blocking=" + str(v.get("blocking")),
          "resolution=" + json.dumps(i.get("resolution", {}).get("wheel_sha256")),
          "still_blocking_for=" + json.dumps(i.get("resolution", {}).get("still_blocking_for")))
PY
