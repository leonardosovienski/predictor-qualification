"""integration-stocks: GATES.json do ciclo 3 (C14), no mesmo padrão do cycle2_gates.py.

Os gates que o ciclo 3 refaz voltam a NOT_RUN, com o estado do ciclo 2 preservado em cycle2_evidence (status,
evidências e nota como estavam, mais ambientes, final_commits, final_wheels, revalidação, final_result e
supersedes). Ficam como estão só STACK_BASELINE_FROZEN e BLOCKERS_ZERO. phases_completed ganha freeze-parameters-c3;
supersedes_sha256 passa a ser a attestation atual (a do ciclo 2). Idempotente.
Uso: python cycle3_gates.py <raiz do predictor-qualification>
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
    if g.get("cycle", {}).get("number") == 3:
        print("GATES.json já está no ciclo 3")
        return 0
    assert g["cycle"]["number"] == 2
    g["cycle2_evidence"] = {
        "gates": {k: v for k, v in g["gates"].items() if k not in KEEP},
        "environments": g["environments"], "final_commits": g["final_commits"], "final_wheels": g["final_wheels"],
        "domain_revalidation": g["domain_revalidation"], "final_result": g.pop("final_result"),
        "shared_dependency_verdicts": g["shared_dependency_verdicts"], "supersedes_sha256": g["supersedes_sha256"],
        "cycle": g["cycle"],
    }
    for name in g["gates"]:
        if name not in KEEP:
            g["gates"][name] = {"status": "NOT_RUN", "evidence": [],
                                "note": "ciclo 3: refazer no cain 0.4.13rc13 (ciclo 2, cain 0.4.13rc12, em cycle2_evidence)"}
    g["supersedes_sha256"] = hashlib.sha256(path.with_name("QUALIFICATION_ATTESTATION.json").read_bytes()).hexdigest()
    g["environments"], g["final_commits"], g["final_wheels"] = [], [], []
    g["domain_revalidation"] = {"status": "NOT_RUN", "evidence": []}
    g["phases_completed"].append("freeze-parameters-c3")
    g["cycle"] = {
        "number": 3,
        "why": "decisão do dono (2026-09-28, \"cain rc13 + ciclo 3 (Recomendado)\"): correções da rodada de utilidade "
               "no cain 0.4.13rc13 e 8 hipóteses só para o LLM; pela C14, as fases a partir de publish-candidates são "
               "refeitas; ciclo 2 preservado nos parciais, na attestation atual e nos arquivos *_cycle2_*",
        "supersedes_on_attestation": "supersedes_sha256 = a attestation atual (ciclo 2), preservada como _superseded_ "
                                     "na reemissão",
    }
    path.write_text(json.dumps(g, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("GATES.json → ciclo 3:", sorted(k for k, v in g["gates"].items() if v["status"] != "NOT_RUN"), "mantidos")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
