"""Acrescenta IS-F005 ao FINDINGS.json da missão (sem tocar nos demais)."""
import hashlib
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
rel = "qualification/integration-stocks/FINDINGS.json"
path = root / rel
doc = json.loads(path.read_text(encoding="utf-8"))
assert not any(f["id"] == "IS-F005" for f in doc["findings"])


def ev(r: str) -> dict:
    return {"file": r, "sha256": hashlib.sha256((root / r).read_bytes()).hexdigest()}


doc["findings"].append({
    "id": "IS-F005",
    "severity": "P1",
    "title": "CI Pipeline do stocks-predictor no SHA exato do final_commit: job secrets vermelho por falso positivo "
             "pré-existente no histórico do main",
    "description": "O run workflow_dispatch do CI Pipeline no final_commit 6f857b2 (run 36363108348) tem Quality 3.13 e "
                   "3.14 verdes e o job secrets vermelho: no workflow_dispatch o gitleaks-action varre o histórico de "
                   "todas as branches (checkout com fetch-depth 0) e acusa generic-api-key em "
                   "docs/evidence/2026-09-24-prompt1-segredos.md:57, commit 28f17d2 do main (PR #99), fora desta branch "
                   "(não é ancestral de 6f857b2). A linha é uma tabela de auditoria que descreve um falso positivo já "
                   "revisado (import de constantes de config); o .gitleaksignore da base não tem essa fingerprint. O CI "
                   "de push do main não reexamina commits antigos e fica verde. Junto com IS-F004, nenhum run do CI do "
                   "stocks-predictor no SHA exato do final_commit pode ficar verde sem mudança fora do autorizado.",
    "classification": "C6 P1 (precedente IC-F004 da integration-crypto: CI vermelho por fator anterior à missão): "
                      "evidência exigida (CI verde no final_commit, C21/9.2) incompleta, sem violação observada; o "
                      "código da missão não tem segredo (varredura do diff limpa; o job secrets não acusa arquivo desta "
                      "branch).",
    "evidence": [ev("qualification/integration-stocks/RAW_LOGS/hosted-ci/stocks-predictor_6f857b2_run36363108348.json"),
                 ev("qualification/integration-stocks/RAW_LOGS/hosted-ci/stocks-predictor_6f857b2_run36363108348_secrets_job.log")],
    "status": "OPEN_AWAITING_OWNER",
    "owner_decision": "escolher: (a) autorizar, como exceção explícita além da D-24 (4), acrescentar ao .gitleaksignore "
                      "da branch do adapter a fingerprint 28f17d2…:docs/evidence/2026-09-24-prompt1-segredos.md:"
                      "generic-api-key:57 (arquivo fora dos adapter_paths; muda o selo R8 ⇒ nova rc e C14 das fases do "
                      "Stocks); ou (b) aceitar como CI do final_commit do stocks-predictor o run workflow_dispatch com "
                      "Quality verde e secrets vermelho só por este falso positivo do main; ou (c) outro caminho",
})
path.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print("IS-F005 added")
