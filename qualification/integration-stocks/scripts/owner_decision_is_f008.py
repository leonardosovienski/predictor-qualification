"""Registra no FINDINGS.json a decisão do dono sobre IS-F008, opção (a).

Pergunta no chat da sessão (2026-09-28), com a resposta escolhida pelo dono: "(a) Encadeada (Recomendado)". O texto
da opção era: "O gate aceita cada um dos 4 itens só com a cadeia conferida byte a byte até o sha256 protegido
(arquivo preservado + ponteiro, salto a salto). Todo outro item alterado continua FAIL. É o mesmo critério do IS-F006
e do IC-F011 do cripto."
Aplicação: scripts/protected_check.py segue a cadeia de cada um dos quatro itens (cycle.supersedes nos congelados;
supersedes_sha256 + _superseded_<sha12> nas attestations) e só marca o item como encadeado se cada salto conferir
e a cadeia chegar ao sha256 protegido; all_unchanged continua sendo a letra.
Uso: python owner_decision_is_f008.py <raiz do predictor-qualification>
"""
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
path = root / "qualification/integration-stocks/FINDINGS.json"
doc = json.loads(path.read_text(encoding="utf-8"))
f = {x["id"]: x for x in doc["findings"]}["IS-F008"]
assert f["status"] == "OPEN_AWAITING_OWNER"
f["status"] = "ACCEPTED_LIMITATION"
f["owner_decision_taken"] = {
    "date": "2026-09-28", "by": "dono", "channel": "chat da sessão (pergunta com opções)",
    "words": "(a) Encadeada (Recomendado)",
    "option_text": "O gate aceita cada um dos 4 itens só com a cadeia conferida byte a byte até o sha256 protegido "
                   "(arquivo preservado + ponteiro, salto a salto). Todo outro item alterado continua FAIL. É o mesmo "
                   "critério do IS-F006 e do IC-F011 do cripto.",
    "applied": "scripts/protected_check.py: para os quatro itens do IS-F008, segue a cadeia salto a salto "
               "(cycle.supersedes nos FROZEN_*; supersedes_sha256 e QUALIFICATION_ATTESTATION_superseded_<sha12>.json "
               "nas attestations) e registra o item como encadeado só se cada arquivo preservado tiver os bytes que o "
               "ponteiro diz e a cadeia chegar ao sha256 protegido. all_unchanged continua sendo a letra da C15.1; o "
               "gate usa all_unchanged_or_chained. Todo outro item alterado continua FAIL.",
    "evidence": "RAW_LOGS/protected do ciclo 2 (protected_check.json)"}
path.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print("IS-F008 -> ACCEPTED_LIMITATION")
