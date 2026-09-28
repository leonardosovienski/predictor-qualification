"""Registra no FINDINGS.json a decisão do dono sobre IS-F006, opção (a).

Pergunta no chat da sessão (2026-09-28), com a resposta escolhida pelo dono: "(a) Aceitar a reemissão C14". O texto
da opção era: "Decido que a reemissão prevista em c14_integration_crypto, com os bytes protegidos preservados e
encadeados, satisfaz a C15.1 para esse item. A attestation reemitida sai com 30/30 gates PASS."
O gate PROTECTED_ARTIFACTS_UNCHANGED só aplica a decisão se a supersessão estiver conferida no protected_check.json:
o arquivo _superseded_ tem o sha256 esperado, e o supersedes_sha256 da attestation atual é esse sha256.
Uso: python owner_decision_is_f006.py <raiz do predictor-qualification>
"""
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
path = root / "qualification/integration-stocks/FINDINGS.json"
doc = json.loads(path.read_text(encoding="utf-8"))
f = {x["id"]: x for x in doc["findings"]}["IS-F006"]
assert f["status"] == "OPEN_AWAITING_OWNER"
f["status"] = "ACCEPTED_LIMITATION"
f["owner_decision_taken"] = {
    "date": "2026-09-28", "by": "dono", "channel": "chat da sessão (pergunta com opções)",
    "words": "(a) Aceitar a reemissão C14",
    "option_text": "Decido que a reemissão prevista em c14_integration_crypto, com os bytes protegidos preservados e "
                   "encadeados, satisfaz a C15.1 para esse item. A attestation reemitida sai com 30/30 gates PASS.",
    "applied": "PROTECTED_ARTIFACTS_UNCHANGED aceita o item qualification/integration-crypto/QUALIFICATION_ATTESTATION"
               ".json só com a supersessão conferida: o _superseded_112d18a35c7b.json tem o sha256 esperado "
               "(112d18a3…), e o supersedes_sha256 da attestation atual é ele. Todo outro item alterado continua FAIL.",
    "evidence": "qualification/integration-stocks/RAW_LOGS/protected-r1/protected_check.json"}
path.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print("IS-F006 -> ACCEPTED_LIMITATION")
