"""Acrescenta IS-F006 ao FINDINGS.json da missão (sem tocar nos demais)."""
import hashlib
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
rel = "qualification/integration-stocks/FINDINGS.json"
path = root / rel
doc = json.loads(path.read_text(encoding="utf-8"))
assert not any(f["id"] == "IS-F006" for f in doc["findings"])


def ev(r: str) -> dict:
    return {"file": r, "sha256": hashlib.sha256((root / r).read_bytes()).hexdigest()}


doc["findings"].append({
    "id": "IS-F006",
    "severity": "P2",
    "title": "parâmetros congelados contraditórios: a reemissão C14 da attestation da integration-crypto (prevista) "
             "altera um item do conjunto protegido desta missão",
    "description": "FROZEN_PARAMETERS.json manda, em c14_integration_crypto, refazer as fases da integration-crypto e "
                   "reemitir a attestation dela no mesmo ciclo (C14: cain e ecosystem-predictor mudaram), e põe essa "
                   "mesma attestation (sha256 112d18a3…) em protected_set_initial.integration_crypto; o PROTECTED_SET.json "
                   "de truth-map a herdou. A reemissão foi feita: o arquivo "
                   "qualification/integration-crypto/QUALIFICATION_ATTESTATION.json tem agora outro sha256 (QUALIFIED, "
                   "cain 0.4.13rc7 e transporte 0.1.0rc4). Os bytes protegidos estão preservados, iguais, em "
                   "QUALIFICATION_ATTESTATION_superseded_112d18a35c7b.json, e a nova attestation aponta para eles por "
                   "supersedes_sha256 (C7.1 regra 8). Os outros 3386 itens estão iguais. O gate "
                   "PROTECTED_ARTIFACTS_UNCHANGED (C15.1: hashes iguais de truth-map até a attestation) fica FAIL pela "
                   "letra; o agente não reinterpreta o critério. Correção: a nota 'rule' do PROTECTED_SET.json resume a "
                   "C15.1 como 'item alterado = P0', mas o núcleo diz 'item descoberto depois já alterado = P0', que não "
                   "é este caso.",
    "classification": "C6 P2: sem efeito em resultado ou operação (a mudança é a prevista, com os bytes originais "
                      "preservados e encadeados); conflito de especificação para o dono resolver.",
    "evidence": [ev("qualification/integration-stocks/RAW_LOGS/protected/protected_check.json"),
                 ev("qualification/integration-stocks/FROZEN_PARAMETERS.json"),
                 ev("qualification/integration-stocks/PROTECTED_SET.json"),
                 ev("qualification/integration-crypto/QUALIFICATION_ATTESTATION_superseded_112d18a35c7b.json")],
    "status": "OPEN_AWAITING_OWNER",
    "owner_decision": "escolher: (a) aceitar que a reemissão C14 prevista em c14_integration_crypto, com os bytes "
                      "protegidos preservados no arquivo _superseded_ e encadeados por supersedes_sha256, satisfaz a "
                      "C15.1 para este item (PROTECTED_ARTIFACTS_UNCHANGED reavaliado na reemissão desta attestation); "
                      "ou (b) outro caminho",
})
path.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print("IS-F006 acrescentado;", len(doc["findings"]), "achados")
