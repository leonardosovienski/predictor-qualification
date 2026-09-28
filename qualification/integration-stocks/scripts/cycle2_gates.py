"""integration-stocks: GATES.json do ciclo 2 (C14), no padrão do ciclo 2 da integration-brasileirao.

Os gates que o ciclo 2 refaz voltam a NOT_RUN, com o estado do ciclo 1 preservado em cycle1_evidence (status,
evidências e nota como estavam); ambientes, final_commits, final_wheels, revalidação do domínio e final_result do ciclo
1 também. Ficam como estão só STACK_BASELINE_FROZEN (baseline de antes de qualquer mudança da missão; a fase não é
refeita) e BLOCKERS_ZERO (reavaliado na attestation a partir do FINDINGS.json). phases_completed ganha
freeze-parameters-c2. Idempotente: não roda duas vezes.
Uso: python cycle2_gates.py <raiz do predictor-qualification>
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
    if "cycle" in g:
        print("GATES.json já está no ciclo 2")
        return 0
    g["cycle1_evidence"] = {
        "gates": {k: v for k, v in g["gates"].items() if k not in KEEP},
        "environments": g["environments"], "final_commits": g["final_commits"], "final_wheels": g["final_wheels"],
        "domain_revalidation": g["domain_revalidation"], "final_result": g.pop("final_result"),
        "shared_dependency_verdicts": g["shared_dependency_verdicts"],
    }
    for name in g["gates"]:
        if name not in KEEP:
            g["gates"][name] = {"status": "NOT_RUN", "evidence": [],
                                "note": "ciclo 2: refazer no cain 0.4.13rc11 (ciclo 1, cain 0.4.13rc7, em cycle1_evidence)"}
    g["cycle1_evidence"]["supersedes_sha256"] = g["supersedes_sha256"]
    # a attestation do ciclo 2 substitui a atual (reemissão 1 do ciclo 1), preservada como _superseded_ ao reemitir
    g["supersedes_sha256"] = hashlib.sha256(path.with_name("QUALIFICATION_ATTESTATION.json").read_bytes()).hexdigest()
    g["environments"], g["final_commits"], g["final_wheels"] = [], [], []
    g["domain_revalidation"] = {"status": "NOT_RUN", "evidence": []}
    g["phases_completed"].append("freeze-parameters-c2")
    g["cycle"] = {
        "number": 2,
        "why": "decisões do dono (2026-09-28, \"Aprovo o ciclo novo\" e \"Hipóteses para o LLM\"): política v2 do cain e "
               "hipóteses só para o LLM (cain 0.4.13rc11); pela C14, as fases a partir de publish-candidates são "
               "refeitas; ciclo 1 preservado nos parciais, na attestation atual e nos arquivos *_cycle1_*",
        "supersedes_on_attestation": "supersedes_sha256 = a attestation atual (QUALIFICATION_ATTESTATION.json "
                                     "do ciclo 1, reemissão 1), preservada como _superseded_ na reemissão",
    }
    path.write_text(json.dumps(g, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("GATES.json → ciclo 2:", sorted(k for k, v in g["gates"].items() if v["status"] != "NOT_RUN"), "mantidos")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
