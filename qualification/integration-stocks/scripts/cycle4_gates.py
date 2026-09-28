"""integration-stocks: GATES.json do ciclo 4 (C14), a partir do ciclo 3.

No ciclo 3 nenhum gate chegou a rodar (todos NOT_RUN, menos STACK_BASELINE_FROZEN e BLOCKERS_ZERO). Então o ciclo 4
só troca a nota dos NOT_RUN para a rc13 do ciclo 4, guarda o bloco cycle do ciclo 3 dentro do novo e acrescenta
freeze-parameters-c4 a phases_completed. supersedes_sha256 continua a attestation atual (ciclo 2). Idempotente.
Uso: python cycle4_gates.py <raiz do predictor-qualification>
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

KEEP = {"STACK_BASELINE_FROZEN", "BLOCKERS_ZERO"}


def main() -> int:
    path = Path(sys.argv[1]) / "qualification/integration-stocks/GATES.json"
    g = json.loads(path.read_text(encoding="utf-8"))
    if g.get("cycle", {}).get("number") == 4:
        print("GATES.json já está no ciclo 4")
        return 0
    assert g["cycle"]["number"] == 3
    ran = sorted(k for k, v in g["gates"].items() if k not in KEEP and v["status"] != "NOT_RUN")
    if ran:
        raise SystemExit(f"gates do ciclo 3 já rodados, preservar antes: {ran}")
    for name in g["gates"]:
        if name not in KEEP:
            g["gates"][name] = {"status": "NOT_RUN", "evidence": [],
                                "note": "ciclo 4: refazer no cain 0.4.13rc13 (cain#77 + cain#78) com o transporte "
                                        "0.1.0rc6 (ciclo 2, cain 0.4.13rc12, em cycle2_evidence)"}
    g["phases_completed"].append("freeze-parameters-c4")
    g["cycle"] = {
        "number": 4,
        "why": "decisões do dono (2026-09-28, \"arruma os não resolvidos\"): D-26 (\"Somar as famílias do main\"), "
               "\"Só o transporte\" (transporte 0.1.0rc6) e a calibração do embedding (fica só revisão); pela C14, as "
               "fases a partir de publish-candidates são refeitas; nenhum gate do ciclo 3 chegou a rodar",
        "supersedes_on_attestation": g["cycle"]["supersedes_on_attestation"],
        "cycle3": g["cycle"],
    }
    path.write_text(json.dumps(g, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("GATES.json → ciclo 4:", sorted(k for k, v in g["gates"].items() if v["status"] != "NOT_RUN"), "mantidos")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
