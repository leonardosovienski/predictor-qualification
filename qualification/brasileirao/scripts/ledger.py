"""brasileirao: edita GATES.json e FINDINGS.json de forma controlada (sem editar à mão).

Uso:
  python ledger.py init                      cria GATES.json com todos os gates exigidos em NOT_RUN
  python ledger.py gate <GATE> <STATUS> <nota> [evidência ...]
  python ledger.py phase <fase>              acrescenta a fase a phases_completed
  python ledger.py set <campo> <json>        campo de topo do GATES.json (final_commits, final_wheels, ...)
  python ledger.py finding <json>            acrescenta um achado (id novo) ou atualiza pelo id
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
QC = ROOT / "qualification" / "brasileirao"
GATES = QC / "GATES.json"
FINDINGS = QC / "FINDINGS.json"

COMMON = [
    "BLOCKERS_ZERO", "STACK_BASELINE_FROZEN", "LOCK_INTEGRITY", "CORE_IDENTITY", "CLEANROOM_FINAL",
    "HOSTED_CI", "E2E", "IDEMPOTENCY", "RESTART_RECOVERY", "FAILURE_INJECTION", "PROVENANCE",
    "AUTHORITY_SEPARATION", "FUTURE_CANARY", "PROTECTED_ARTIFACTS_UNCHANGED", "SOAK", "WINDOWS_SMOKE",
    "SHARED_DEPENDENCY_CLEAR", "EVIDENCE_CONSISTENCY", "SECRETS_CLEAN", "CAPITAL_FORBIDDEN",
]
STAGE_A = ["DOMAIN_CONTRACT", "ADMISSION", "OPS_RUNTIME", "CORE_PARTICIPATION", "TEMPORAL_INTEGRITY"]
ARM = [
    "BR_OPS_REUSE", "BR_KICKOFF_ORDERING", "BR_TIMEZONE_INTEGRITY", "BR_SAME_KICKOFF_ISOLATION",
    "BR_METAMORPHIC", "BR_CACHE_STATE", "BR_FUTURE_INJECTION",
]
STATUSES = {"PASS", "FAIL", "NOT_RUN"}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def save(path: Path, doc: dict) -> None:
    path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def main() -> None:
    mode = sys.argv[1]
    if mode == "init":
        if GATES.exists():
            raise SystemExit("GATES.json já existe")
        save(
            GATES,
            {
                "note": "Fonte única dos estados de gate (attest.py). Editado só por scripts/ledger.py.",
                "common_baseline_id": "STACK_BASELINE_V1.1",
                "supersedes_sha256": None,
                "domain_contract_sha256": None,
                "final_commits": [],
                "final_wheels": [],
                "phases_completed": [],
                "environments": [],
                "shared_dependency_verdicts": [],
                "gates": {g: {"status": "NOT_RUN", "evidence": [], "note": "fase ainda não executada"} for g in COMMON + STAGE_A + ARM},
            },
        )
        return
    if mode == "gate":
        gate, status, note, *evidence = sys.argv[2:]
        if status not in STATUSES:
            raise SystemExit(f"status inválido: {status}")
        doc = load(GATES)
        if gate not in doc["gates"]:
            raise SystemExit(f"gate desconhecido: {gate}")
        for item in evidence:
            if not (ROOT / item).is_file():
                raise SystemExit(f"evidência ausente: {item}")
        doc["gates"][gate] = {"status": status, "evidence": evidence, "note": note}
        save(GATES, doc)
        return
    if mode == "phase":
        doc = load(GATES)
        if sys.argv[2] not in doc["phases_completed"]:
            doc["phases_completed"].append(sys.argv[2])
        save(GATES, doc)
        return
    if mode == "set":
        doc = load(GATES)
        doc[sys.argv[2]] = json.loads(sys.argv[3])
        save(GATES, doc)
        return
    if mode == "finding":
        entry = json.loads(sys.argv[2])
        doc = load(FINDINGS)
        for index, item in enumerate(doc["findings"]):
            if item["id"] == entry["id"]:
                doc["findings"][index] = {**item, **entry}
                break
        else:
            required = {"id", "severity", "status", "phase", "title", "description", "evidence"}
            if not required <= set(entry):
                raise SystemExit(f"achado novo exige {sorted(required)}")
            doc["findings"].append(entry)
        save(FINDINGS, doc)
        return
    raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
