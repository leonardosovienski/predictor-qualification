"""integration-brasileirao, C0: pré-condições da Etapa B num snapshot do predictor-qualification.

Chamado por c0_preflight.sh. Só leitura. Imprime uma linha por verificação,
`CHECK <id> <OK|FALHA> <detalhe>`, e no fim `c0_falhas <n>`.

Uso: python c0_preconditions.py <diretório do snapshot>
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
failures = 0


def check(item: str, ok: bool, detail: str) -> None:
    global failures
    failures += not ok
    print(f"CHECK {item} {'OK' if ok else 'FALHA'} {detail}")


def load(rel: str):
    path = root / rel
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None


# 3.2 e COMUM: decisões
decisions = {d["decision_id"]: d["status"] for d in load("qualification/DECISIONS.json")["decisions"]}
for did in ("D-16", "D-19", "D-22"):
    check(f"3.2/{did}", decisions.get(did) == "APPROVED", f"status={decisions.get(did)}")

# 3.4: prompt da missão §1 (integration-stocks QUALIFIED e, por consequência, integration-crypto)
for branch in ("integration-stocks", "integration-crypto"):
    rel = f"qualification/{branch}/QUALIFICATION_ATTESTATION.json"
    att = load(rel)
    detail = f"result={att.get('result')}" if att else f"{rel} ausente (diretório existe: {(root / 'qualification' / branch).is_dir()})"
    check(f"3.4/{branch}", bool(att) and att.get("result") == "QUALIFIED", detail)

# prompt comum §1: Etapa A QUALIFIED e contratos no main
for branch in ("crypto", "brasileirao", "stocks"):
    att = load(f"qualification/{branch}/QUALIFICATION_ATTESTATION.json")
    check(f"comum1/etapaA-{branch}", bool(att) and att.get("result") == "QUALIFIED", f"result={att.get('result') if att else 'ausente'}")
    rel = f"qualification/{branch}/DOMAIN_RESEARCH_CONTRACT.json"
    check(f"comum1/contrato-{branch}", (root / rel).is_file(), rel)

# prompt comum §1: envelope V2 congelado
rel = "qualification/shared/ENVELOPE_V2_FREEZE.json"
check("comum1/ENVELOPE_V2_FREEZE", (root / rel).is_file(), rel)
baselines = sorted(p.name for p in (root / "qualification/shared").glob("STACK_BASELINE_*.json"))
v2 = [b for b in baselines if b.startswith("STACK_BASELINE_V2.")]
check("comum1/STACK_BASELINE_V2.n", bool(v2), f"baselines no main: {baselines}")

# prompt comum §1: nenhum issue bloqueante (verdict.blocking; resolução por release nova vale só para ela)
for issue in load("qualification/shared/SHARED_ISSUES.json")["issues"]:
    verdict = issue.get("verdict") or {}
    resolution = issue.get("resolution") or {}
    blocking = verdict.get("blocking")
    resolved = bool(resolution) and issue.get("status", "").startswith("RESOLVED")
    detail = f"status={issue.get('status')} classification={verdict.get('classification')} blocking={blocking}"
    if resolved:
        detail += f" resolvido_em={resolution.get('wheel_version')} ({resolution.get('wheel_sha256', '')[:8]}) ainda_bloqueia={resolution.get('still_blocking_for')}"
    check(f"comum1/{issue['issue_id']}", blocking is False or resolved, detail)

# C0.3: higiene e baseline comum
hygiene = load("qualification/HYGIENE.json")
items = hygiene["items"] if isinstance(hygiene, dict) else hygiene
pending = [i.get("id") for i in items if i.get("status") != "DONE"]
check("C0.3/HYGIENE", not pending, f"itens={len(items)} fora_de_DONE={pending}")
check("C0.3/baseline-comum", (root / "qualification/shared/STACK_BASELINE_V1.json").is_file(), "qualification/shared/STACK_BASELINE_V1.json")

# prompt da missão §2: alvo do domínio e contrato
target = load("qualification/brasileirao/runtime_target.json")
ops = target["stack"]["predictor-ops"]
check(
    "missao2/runtime_target",
    target["version"] == "0.3.0rc3",
    f"version={target['version']} commit={target['commit']} wheel={target['wheel_sha256']} ops={ops['version']} ({ops['sha256'][:8]})",
)
contract = load("qualification/brasileirao/DOMAIN_RESEARCH_CONTRACT.json")
check("missao2/contrato-prefixo", contract["domain_prefix"] == "brasileirao", f"domain_prefix={contract['domain_prefix']}")
check(
    "missao2/contrato-adapter_paths",
    contract["adapter_paths"] == ["brasileirao_predictor/adapters/"],
    f"adapter_paths={contract['adapter_paths']}",
)
allowed = contract["adapter_entrypoints"]["allowed_to_create_in_stage_b"]
check(
    "missao2/contrato-adapter_entrypoints",
    any(a.startswith("brasileirao-research-adapter") for a in allowed),
    f"allowed_to_create_in_stage_b={allowed}",
)

print(f"c0_falhas {failures}")
