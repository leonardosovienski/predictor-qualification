"""integration-stocks: GATES.json do ciclo 7 (C14), no mesmo padrão do cycle2_gates.py.

Os gates que o ciclo 7 refaz voltam a NOT_RUN, com o estado do ciclo 2 preservado em cycle6_evidence (status,
evidências e nota como estavam, mais ambientes, final_commits, final_wheels, revalidação, final_result e
supersedes). Ficam como estão só STACK_BASELINE_FROZEN e BLOCKERS_ZERO. phases_completed ganha freeze-parameters-c5;
supersedes_sha256 passa a ser a attestation atual (a do ciclo 2). Idempotente.
Uso: python cycle7_gates.py <raiz do predictor-qualification>
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

KEEP = {"STACK_BASELINE_FROZEN", "BLOCKERS_ZERO"}


def main() -> int:
    path = Path(sys.argv[1]) / "qualification/integration-stocks/GATES.json"
    g = json.loads(path.read_text(encoding="utf-8"))
    if g.get("cycle", {}).get("number") == 7:
        print("GATES.json já está no ciclo 7")
        return 0
    assert g["cycle"]["number"] == 6
    g["cycle6_evidence"] = {
        "gates": {k: v for k, v in g["gates"].items() if k not in KEEP},
        "environments": g["environments"], "final_commits": g["final_commits"], "final_wheels": g["final_wheels"],
        "domain_revalidation": g["domain_revalidation"], "final_result": g.pop("final_result"),
        "shared_dependency_verdicts": g["shared_dependency_verdicts"], "supersedes_sha256": g["supersedes_sha256"],
        "cycle": g["cycle"],
    }
    for name in g["gates"]:
        if name not in KEEP:
            g["gates"][name] = {"status": "NOT_RUN", "evidence": [],
                                "note": "ciclo 7: refazer na cain 0.4.13rc15 com o transporte 0.1.0rc7 (ciclo 4, cain 0.4.13rc13 + transporte rc6, em cycle6_evidence)"}
    g["supersedes_sha256"] = hashlib.sha256(path.with_name("QUALIFICATION_ATTESTATION.json").read_bytes()).hexdigest()
    g["environments"], g["final_commits"], g["final_wheels"] = [], [], []
    g["domain_revalidation"] = {"status": "NOT_RUN", "evidence": []}
    g["phases_completed"].append("freeze-parameters-c7")
    g["cycle"] = {
        "number": 7,
        "why": "D-34, C14 (2026-10-07, noite): o ecosystem adotou a cain 0.4.13rc16 na lock conjunta compat/ (ecosystem 0.2.2); pela C14 (mudança no "
               "ecosystem-predictor), as fases que o exercitam são refeitas; as wheels instaladas pelo runtime (cain rc16, transporte rc7, protocolo rc2, "
               "stocks rc3, cripto rc3, core, ops) não mudam; ciclo 6 preservado nos parciais, na attestation atual e em cycle6_evidence",
        "supersedes_on_attestation": "supersedes_sha256 = a attestation atual (ciclo 6), preservada como _superseded_ na reemissão",
    }
    path.write_text(json.dumps(g, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("GATES.json → ciclo 7:", sorted(k for k, v in g["gates"].items() if v["status"] != "NOT_RUN"), "mantidos")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
