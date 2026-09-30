"""integration-stocks: registra o IS-F010 (piso llm_proposals do soak não atingido na primeira execução do ciclo 5).

Números saem dos SUMMARY.json e commands.log dos dois runs do soak (o que falhou e o refeito). Idempotente.
Uso: python add_finding_is_f010.py <raiz do predictor-qualification> <run que falhou> <run refeito>
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1])
M = ROOT / "qualification/integration-stocks"
FIRST, SECOND = sys.argv[2], sys.argv[3]


def ref(rel: str) -> dict:
    return {"file": f"qualification/integration-stocks/{rel}", "sha256": hashlib.sha256((M / rel).read_bytes()).hexdigest()}


def soak_facts(run: str) -> dict:
    summary = json.loads((M / f"RAW_LOGS/runtime/{run}/soak/SUMMARY.json").read_text(encoding="utf-8"))
    log = (M / f"RAW_LOGS/runtime/{run}/soak/commands.log").read_text(encoding="utf-8")
    attempts = len(re.findall(r'"label": "llm proposal (\d+)"', log))
    truncated = log.count("Modelo atingiu o limite de geração; resposta incompleta.")
    ollama = re.search(r"ollama version is ([0-9.]+)", (M / f"RAW_LOGS/runtime/{run}/soak-llm-setup/ollama_setup.log")
                       .read_text(encoding="utf-8", errors="replace"))
    return {"run": run, "passed": summary["passed"], "failed": summary["failed"],
            "llm_proposals": summary["counters"]["llm_proposals"], "attempts": attempts, "truncated": truncated,
            "ollama": ollama.group(1) if ollama else "?",
            "zero_tolerance_ok": all(x["ok"] for x in summary["checks"] if not x["check"].startswith("floor llm_proposals"))}


def main() -> int:
    path = M / "FINDINGS.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    if any(f["id"] == "IS-F010" for f in doc["findings"]):
        print("IS-F010 já registrado")
        return 0
    a, b = soak_facts(FIRST), soak_facts(SECOND)
    fixed = b["failed"] == 0 and b["llm_proposals"] >= 5
    doc["findings"].append({
        "id": "IS-F010",
        "severity": "P2",
        "title": "soak do ciclo 5: piso llm_proposals >= 5 não atingido na primeira execução (4 de 6 tentativas úteis); "
                 "a CAIN recusou fail-closed as respostas truncadas do modelo local",
        "description": (
            f"Run {a['run']} (todas as fases, cain 0.4.13rc15 + transporte 0.1.0rc7): {a['passed']} conferências OK e "
            f"{a['failed']} falha, só no piso llm_proposals ({a['llm_proposals']} < 5). O laço do soak faz "
            f"{a['attempts']} tentativas (piso + 1) e em {a['truncated']} delas o modelo qwen2.5:0.5b (ollama "
            f"{a['ollama']}; nos ciclos anteriores, ollama 0.34.4 com 0 ou 1 truncamento) estourou num_predict=256 — "
            "'Modelo atingiu o limite de geração; resposta incompleta.' — e o `cain research explain --propose-for-domain` "
            "saiu com código 2 (LLM_PROPOSAL_FAILED), sem proposta. Todas as conferências de tolerância zero (efeito "
            f"duplicado, resultado perdido, provenance, contaminação) passaram: {a['zero_tolerance_ok']}. A fase soak foi "
            f"refeita sozinha, com o mesmo perfil V1 congelado e as mesmas wheels, no run {b['run']}: {b['passed']} OK, "
            f"{b['failed']} falhas, llm_proposals {b['llm_proposals']} em {b['attempts']} tentativas "
            f"({b['truncated']} truncamentos). Os dois logs brutos ficam em RAW_LOGS; nenhum foi editado."),
        "classification": ("C6 P2: sem efeito em resultado nem em operação — o caminho com LLM não é prova (C9) e a "
                           "recusa da resposta incompleta é o comportamento fail-closed esperado; o que faltou foi "
                           "cobertura do perfil (1 tentativa de folga para o piso) num modelo local não determinístico "
                           "entre versões do ollama. Perfil congelado não muda neste ciclo (C15); para um perfil V2, "
                           "fixar a versão do ollama e dar mais folga ao laço de tentativas."),
        "evidence": [ref(f"RAW_LOGS/runtime/{a['run']}/soak/SUMMARY.json"), ref(f"RAW_LOGS/runtime/{a['run']}/soak/commands.log"),
                     ref(f"RAW_LOGS/runtime/{a['run']}/soak-llm-setup/ollama_setup.log"),
                     ref(f"RAW_LOGS/runtime/{b['run']}/soak/SUMMARY.json"), ref(f"RAW_LOGS/runtime/{b['run']}/soak/commands.log"),
                     ref("scripts/soak.py")],
        "status": "ACCEPTED_LIMITATION" if fixed else "OPEN",
        "owner_decision": "nenhuma pendente" if fixed else "SOAK segue FAIL no ciclo 5; decidir novo ciclo do perfil (C14)",
    })
    path.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("IS-F010 registrado:", a, b)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
