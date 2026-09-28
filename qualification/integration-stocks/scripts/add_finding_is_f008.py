"""integration-stocks: registra o IS-F008 (ciclo 2 dos parâmetros congelados × C15.1), aguardando o dono.

O PROTECTED_SET.json de truth-map tem itens que o ciclo 2 troca: os congelados desta missão (parâmetros e vetores,
ciclo 2) e dois da integration-crypto (os congelados do ciclo 2 dela, IC-F011, e a attestation reemitida de novo no
ciclo 2 dela). A C15.1 manda hashes iguais de truth-map até a attestation; a C14 manda novo ciclo quando um parâmetro
congelado muda. Os bytes protegidos ficam preservados e encadeados. O agente não reinterpreta o critério: a decisão é
do dono. Idempotente: não duplica o achado.
Uso: python add_finding_is_f008.py <raiz do predictor-qualification>
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(sys.argv[1])
Q = ROOT / "qualification"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(rel: str) -> dict:
    return {"file": f"qualification/{rel}", "sha256": sha(Q / rel)}


def main() -> int:
    path = Q / "integration-stocks/FINDINGS.json"
    findings = json.loads(path.read_text(encoding="utf-8"))
    if any(f["id"] == "IS-F008" for f in findings["findings"]):
        print("IS-F008 já registrado")
        return 0
    protected = {s["path"]: s["sha256"] for s in
                 json.loads((Q / "integration-stocks/PROTECTED_SET.json").read_text(encoding="utf-8"))["shared"]}
    params = json.loads((Q / "integration-stocks/FROZEN_PARAMETERS.json").read_text(encoding="utf-8"))["cycle"]
    vectors = json.loads((Q / "integration-stocks/FROZEN_VECTORS.json").read_text(encoding="utf-8"))["cycle"]
    ic_params = json.loads((Q / "integration-crypto/FROZEN_PARAMETERS.json").read_text(encoding="utf-8"))["cycle"]
    ic_att = json.loads((Q / "integration-crypto/QUALIFICATION_ATTESTATION.json").read_text(encoding="utf-8"))
    chains = [
        {"item": "qualification/integration-stocks/FROZEN_PARAMETERS.json",
         "protected_sha256": protected["qualification/integration-stocks/FROZEN_PARAMETERS.json"],
         "kept_in": "qualification/integration-stocks/" + params["supersedes"]["file"],
         "pointer": "cycle.supersedes do arquivo atual", "pointer_sha256": params["supersedes"]["sha256"]},
        {"item": "qualification/integration-stocks/FROZEN_VECTORS.json",
         "protected_sha256": protected["qualification/integration-stocks/FROZEN_VECTORS.json"],
         "kept_in": "qualification/integration-stocks/" + vectors["supersedes"]["file"],
         "pointer": "cycle.supersedes do arquivo atual", "pointer_sha256": vectors["supersedes"]["sha256"]},
        {"item": "qualification/integration-crypto/FROZEN_PARAMETERS.json",
         "protected_sha256": protected["qualification/integration-crypto/FROZEN_PARAMETERS.json"],
         "kept_in": "qualification/integration-crypto/" + ic_params["supersedes"]["file"],
         "pointer": "cycle.supersedes do arquivo atual (ciclo 2 da integration-crypto, IC-F011)",
         "pointer_sha256": ic_params["supersedes"]["sha256"]},
        {"item": "qualification/integration-crypto/QUALIFICATION_ATTESTATION.json",
         "protected_sha256": protected["qualification/integration-crypto/QUALIFICATION_ATTESTATION.json"],
         "kept_in": "qualification/integration-crypto/QUALIFICATION_ATTESTATION_superseded_112d18a35c7b.json",
         "pointer": "supersedes_sha256 em dois saltos: a atual aponta para o _superseded_2d588e3df966 (reemissão do "
                    "ciclo 2 da integration-crypto), que aponta para o _superseded_112d18a35c7b",
         "pointer_sha256": ic_att["supersedes_sha256"]},
    ]
    for chain in chains:
        chain["current_sha256"] = sha(ROOT / chain["item"])
        chain["kept_sha256"] = sha(ROOT / chain["kept_in"])
    findings["findings"].append({
        "id": "IS-F008",
        "severity": "P2",
        "title": "ciclo 2 dos parâmetros congelados troca itens do conjunto protegido desta missão (os congelados "
                 "dela e dois da integration-crypto)",
        "description": (
            "O ciclo 2 (decisões do dono de 2026-09-28: \"Aprovo o ciclo novo\" e \"Hipóteses para o LLM\") troca o "
            "FROZEN_PARAMETERS.json e o FROZEN_VECTORS.json desta missão; a integration-crypto, no ciclo 2 dela, "
            "trocou o FROZEN_PARAMETERS.json dela (IC-F011) e reemitiu a attestation de novo. Os quatro estão no "
            "PROTECTED_SET.json de truth-map. Pela letra da C15.1 (hashes iguais de truth-map até a attestation), "
            "PROTECTED_ARTIFACTS_UNCHANGED fica FAIL no ciclo 2. Os bytes protegidos de cada item ficam iguais num "
            "arquivo preservado, e o arquivo atual aponta para eles por sha256 (a attestation da integration-crypto em "
            "dois saltos). A decisão do IS-F006 cobre só um salto da attestation da integration-crypto e diz que todo "
            "outro item alterado continua FAIL. Nada mais do conjunto protegido muda por este ciclo (conferido na fase "
            "protected do ciclo 2). O agente não reinterpreta o critério: a decisão é do dono."),
        "classification": ("C6 P2: sem efeito em resultado ou operação (mudanças previstas pela C14, bytes protegidos "
                           "preservados e encadeados); conflito de especificação para o dono resolver."),
        "chains": chains,
        "evidence": [ref("integration-stocks/PROTECTED_SET.json"), ref("integration-stocks/FROZEN_PARAMETERS.json"),
                     ref("integration-stocks/" + params["supersedes"]["file"]),
                     ref("integration-stocks/FROZEN_VECTORS.json"),
                     ref("integration-stocks/" + vectors["supersedes"]["file"]),
                     ref("integration-crypto/FROZEN_PARAMETERS.json"),
                     ref("integration-crypto/" + ic_params["supersedes"]["file"]),
                     ref("integration-crypto/QUALIFICATION_ATTESTATION.json"),
                     ref("integration-crypto/QUALIFICATION_ATTESTATION_superseded_2d588e3df966.json"),
                     ref("integration-crypto/QUALIFICATION_ATTESTATION_superseded_112d18a35c7b.json")],
        "status": "OPEN_AWAITING_OWNER",
        "owner_decision": ("escolher: (a) reemissão encadeada: o gate aceita cada um dos quatro itens só com a cadeia "
                           "conferida byte a byte até o sha256 protegido (arquivo preservado com esses bytes e ponteiro "
                           "do atual, salto a salto); todo outro item alterado continua FAIL; (b) manter a letra: o "
                           "gate fica FAIL e a attestation do ciclo 2 sai NOT_QUALIFIED; (c) refazer o truth-map no "
                           "ciclo 2, com um conjunto protegido novo (só cresce) e hashes a partir dele"),
    })
    path.write_text(json.dumps(findings, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("IS-F008 registrado")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
