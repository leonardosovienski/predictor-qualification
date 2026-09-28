"""integration-brasileirao: registra a decisão do dono sobre PROTECTED_ARTIFACTS_UNCHANGED (IB-F008).

Sete artefatos compartilhados do conjunto protegido do truth-map mudaram por novo ciclo ou reemissão registrados das
missões donas (attestation e FROZEN_PARAMETERS da integration-crypto; FROZEN_PARAMETERS e FROZEN_VECTORS da
integration-stocks; FROZEN_PARAMETERS, FROZEN_VECTORS e perfil desta missão), cada um com os bytes do truth-map
preservados num arquivo _cycle<N>_/_superseded_ do mesmo diretório. O FROZEN_PARAMETERS deixava pendente do dono aplicar
o critério do IS-F006 (a) da integration-stocks. Decisão do dono no chat desta sessão (pergunta com opções), 2026-09-28:
"Cadeia preservada (Recommended)". Implementada em scripts/protected_check.py.
Uso: python owner_decision_protected.py <qualification/integration-brasileirao>
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

DECISION = {"date": "2026-09-28", "by": "dono", "channel": "chat da sessão integration-brasileirao (pergunta com opções)",
            "words": "Cadeia preservada (Recommended)"}


def main() -> int:
    q = Path(sys.argv[1])
    findings = json.loads((q / "FINDINGS.json").read_text(encoding="utf-8"))
    assert "IB-F008" not in {f["id"] for f in findings["findings"]}
    findings["findings"].append({
        "id": "IB-F008", "severity": "P2",
        "title": "artefatos protegidos compartilhados mudaram por novo ciclo/reemissão das missões donas",
        "description": "Sete itens de PROTECTED_SET.json → shared têm sha256 diferente do truth-map: "
                       "integration-crypto QUALIFICATION_ATTESTATION.json e FROZEN_PARAMETERS.json; integration-stocks "
                       "FROZEN_PARAMETERS.json e FROZEN_VECTORS.json; integration-brasileirao FROZEN_PARAMETERS.json, "
                       "FROZEN_VECTORS.json e QUALIFICATION_PROFILE_INTEGRATION_BR_V1.json. Em todos, os bytes do "
                       "truth-map estão preservados byte a byte num arquivo _cycle<N>_ ou _superseded_ do mesmo "
                       "diretório. Nenhum item de código protegido dos domínios mudou.",
        "classification": "C6 P2: mudanças legítimas e registradas das missões donas; sem efeito em resultado ou "
                          "operação. A leitura estrita da C15.1 (item alterado = P0) exigia decisão do dono sobre o "
                          "critério (FROZEN_PARAMETERS → c14_other_integrations.protected_attestations).",
        "evidence": [], "status": "ACCEPTED_LIMITATION",
        "owner_decision_taken": DECISION,
        "applied": "scripts/protected_check.py: um artefato compartilhado alterado conta como inalterado só se os bytes "
                   "do truth-map estão, com sha256 conferido, num <nome>_cycle<N>_<sha12>.json ou "
                   "QUALIFICATION_ATTESTATION_superseded_<sha12>.json do mesmo diretório; qualquer outra diferença é "
                   "FAIL; os itens de código dos domínios são conferidos sem exceção",
    })
    (q / "FINDINGS.json").write_text(json.dumps(findings, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("IB-F008 registrado")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
