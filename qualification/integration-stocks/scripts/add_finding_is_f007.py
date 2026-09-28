"""Acrescenta IS-F007 ao FINDINGS.json da missão (sem tocar nos demais)."""
import hashlib
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
rel = "qualification/integration-stocks/FINDINGS.json"
path = root / rel
doc = json.loads(path.read_text(encoding="utf-8"))
assert not any(f["id"] == "IS-F007" for f in doc["findings"])


def ev(r: str) -> dict:
    return {"file": r, "sha256": hashlib.sha256((root / r).read_bytes()).hexdigest()}


doc["findings"].append({
    "id": "IS-F007",
    "severity": "P2",
    "title": "cain: o main declara 0.4.13rc7 com código diferente da pré-release v0.4.13rc7 publicada por esta missão",
    "description": "A pré-release v0.4.13rc7 do cain foi publicada por esta missão em 2026-09-28T00:51:59Z a partir de "
                   "deccaaa: framework da integration-crypto sem mudança, configuração do Stocks e transporte 0.1.0rc4. "
                   "É o final_wheel das duas integrações. Às 00:55:44Z entrou no main do cain o PR #59 (305a2d7: "
                   "política v2 com R15 e propostas por LLM ancoradas no estado do domínio), fora desta missão, que "
                   "também declara 0.4.13rc7 ('não publicada'). São duas árvores com a mesma versão, como no IS-F001 do "
                   "stocks-predictor. Nenhum resultado de qualificação muda: o runtime instala a wheel pela URL e pelo "
                   "sha256, e o main do cain não entra no runtime, logo não há C14. A branch desta missão "
                   "(integration-stocks/stocks-config-20260927) faz merge textual limpo com o main (git merge-tree), e a "
                   "suíte do cain na árvore do merge passa (diagnóstico no WSL: 1365 passed, 4 skipped). Mergeada, porém, "
                   "o main continuaria declarando 0.4.13rc7 com um código diferente das duas árvores.",
    "classification": "C6 P2: sem efeito em resultado ou operação (runtime fixado por sha256); é versionamento do main "
                      "do cain, fora do escopo desta missão.",
    "evidence": [ev("qualification/integration-stocks/RAW_LOGS/pr-merge-check/pr_merge_check.log"),
                 ev("qualification/integration-stocks/RAW_LOGS/publish-candidates/publish_cain_0.4.13rc7.log")],
    "status": "OPEN_AWAITING_OWNER",
    "owner_decision": "escolher a próxima versão do main do cain (por exemplo, 0.4.13rc8) antes de publicar a política v2. "
                      "Pôr a política v2 no runtime qualificado exige um ciclo C14 novo nas duas integrações, com "
                      "parâmetros novos (nota do próprio PR #59).",
})
path.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print("IS-F007 acrescentado;", len(doc["findings"]), "achados")
