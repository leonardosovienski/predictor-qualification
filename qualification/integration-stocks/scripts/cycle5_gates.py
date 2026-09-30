"""integration-stocks: GATES.json do ciclo 5 (C14), no mesmo padrão do cycle2_gates.py.

Os gates que o ciclo 5 refaz voltam a NOT_RUN, com o estado do ciclo 2 preservado em cycle4_evidence (status,
evidências e nota como estavam, mais ambientes, final_commits, final_wheels, revalidação, final_result e
supersedes). Ficam como estão só STACK_BASELINE_FROZEN e BLOCKERS_ZERO. phases_completed ganha freeze-parameters-c5;
supersedes_sha256 passa a ser a attestation atual (a do ciclo 2). Idempotente.
Uso: python cycle5_gates.py <raiz do predictor-qualification>
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
    if g.get("cycle", {}).get("number") == 5:
        print("GATES.json já está no ciclo 5")
        return 0
    assert g["cycle"]["number"] == 4
    g["cycle4_evidence"] = {
        "gates": {k: v for k, v in g["gates"].items() if k not in KEEP},
        "environments": g["environments"], "final_commits": g["final_commits"], "final_wheels": g["final_wheels"],
        "domain_revalidation": g["domain_revalidation"], "final_result": g.pop("final_result"),
        "shared_dependency_verdicts": g["shared_dependency_verdicts"], "supersedes_sha256": g["supersedes_sha256"],
        "cycle": g["cycle"],
    }
    for name in g["gates"]:
        if name not in KEEP:
            g["gates"][name] = {"status": "NOT_RUN", "evidence": [],
                                "note": "ciclo 5: refazer na cain 0.4.13rc15 com o transporte 0.1.0rc7 (ciclo 4, cain 0.4.13rc13 + transporte rc6, em cycle4_evidence)"}
    g["supersedes_sha256"] = hashlib.sha256(path.with_name("QUALIFICATION_ATTESTATION.json").read_bytes()).hexdigest()
    g["environments"], g["final_commits"], g["final_wheels"] = [], [], []
    g["domain_revalidation"] = {"status": "NOT_RUN", "evidence": []}
    g["phases_completed"].append("freeze-parameters-c5")
    g["cycle"] = {
        "number": 5,
        "why": "D-27 (2026-09-30): cain 0.4.13rc15 e transporte 0.1.0rc7 publicados com as correções de 2026-09-29; pela C14, as fases a partir de "
               "publish-candidates são refeitas; stocks 0.3.0rc3, cripto 1.2.0rc3 e protocolo rc2 inalterados; ciclo 4 preservado nos parciais, na attestation "
               "atual e em cycle4_evidence",
        "supersedes_on_attestation": "supersedes_sha256 = a attestation atual (ciclo 2), preservada como _superseded_ "
                                     "na reemissão",
    }
    path.write_text(json.dumps(g, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("GATES.json → ciclo 5:", sorted(k for k, v in g["gates"].items() if v["status"] != "NOT_RUN"), "mantidos")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
