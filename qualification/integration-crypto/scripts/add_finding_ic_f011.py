"""integration-crypto: registra o IC-F011 (ciclo 2 dos parâmetros congelados × C15.1) com a decisão do dono.

O FROZEN_PARAMETERS.json desta missão está no conjunto protegido (truth-map). A C14 manda refazer a fase inteira como
novo ciclo quando um parâmetro congelado muda (a DecisionPolicy do cain v0.4.13rc10), e o novo ciclo troca o arquivo.
O dono viu o ciclo 2 antes de congelar (C15) e decidiu a reemissão encadeada. Idempotente: não duplica o achado.
Uso: python add_finding_ic_f011.py <qualification/integration-crypto>
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


def ref(m: Path, name: str) -> dict:
    return {"file": f"qualification/integration-crypto/{name}", "sha256": hashlib.sha256((m / name).read_bytes()).hexdigest()}


def main() -> int:
    m = Path(sys.argv[1])
    path = m / "FINDINGS.json"
    findings = json.loads(path.read_text(encoding="utf-8"))
    if any(f["id"] == "IC-F011" for f in findings["findings"]):
        print("IC-F011 já registrado")
        return 0
    cycle = json.loads((m / "FROZEN_PARAMETERS.json").read_text(encoding="utf-8"))["cycle"]
    kept = cycle["supersedes"]["file"]
    findings["findings"].append({
        "id": "IC-F011",
        "severity": "P2",
        "title": "ciclo 2 dos parâmetros congelados (cain v0.4.13rc10) troca um item do conjunto protegido desta missão",
        "description": (
            "A release única do cain (v0.4.13rc10, fb0e1dc) muda a DecisionPolicy (v1 → v2: R04 por hipótese, R15, "
            "R16, R17 e a regra de custos do #62) e acrescenta chaves à configuração do cripto (proposable_request_types, "
            "sealed_scopes). decision_policy é parâmetro congelado da missão: pela C14, a fase inteira, como novo ciclo. "
            "O FROZEN_PARAMETERS.json está no PROTECTED_SET.json de truth-map (sha256 "
            f"{cycle['supersedes']['sha256'][:16]}…), e o ciclo 2 troca o arquivo: o gate PROTECTED_ARTIFACTS_UNCHANGED "
            "(C15.1: hashes iguais de truth-map até a attestation) fica FAIL pela letra. Os bytes do ciclo 1 ficam "
            f"iguais em {kept}, e o bloco cycle.supersedes do ciclo 2 aponta para eles por sha256. Nada mais do "
            "conjunto protegido muda. O agente não reinterpreta o critério: a decisão é do dono."),
        "classification": ("C6 P2: sem efeito em resultado ou operação (mudança prevista pela C14, bytes protegidos "
                           "preservados e encadeados); conflito de especificação para o dono resolver."),
        "evidence": [ref(m, kept), ref(m, "FROZEN_PARAMETERS.json"), ref(m, "PROTECTED_SET.json")],
        "status": "ACCEPTED_LIMITATION",
        "owner_decision": ("escolher: (a) congelar o ciclo 2 com reemissão encadeada (ciclo 1 preservado no arquivo de "
                           "supersedes; o gate aceita o item só com a supersessão conferida); (b) manter o ciclo 1 "
                           "intocado e gravar o ciclo 2 num arquivo novo, somado ao conjunto protegido; ou (c) não "
                           "congelar agora"),
        "owner_decision_taken": {
            "date": "2026-09-28",
            "by": "dono",
            "channel": "chat da sessão cripto (pergunta com opções, depois de ver o diff do ciclo 1 para o ciclo 2)",
            "words": "Aprovo; reemissão encadeada (Recomendado)",
            "option_text": ("Congelo o ciclo 2 como está no diff. O ciclo 1 fica preservado byte a byte em "
                            f"{kept}, e o ciclo 2 aponta para ele por sha256. O gate "
                            "PROTECTED_ARTIFACTS_UNCHANGED aceita esse item só com a supersessão conferida, como você "
                            "decidiu no IS-F006."),
            "applied": ("scripts/protected_check.py: o item conta como alterado (all_unchanged, a letra) e como "
                        "encadeado só se o arquivo do ciclo 1 tiver os bytes protegidos e cycle.supersedes apontar "
                        "para eles (all_unchanged_or_chained); scripts/update_gates.py usa este último e cita o "
                        "IC-F011."),
        },
    })
    path.write_text(json.dumps(findings, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("IC-F011 registrado")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
