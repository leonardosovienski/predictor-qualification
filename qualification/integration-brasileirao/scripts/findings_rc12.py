"""integration-brasileirao: atualiza FINDINGS.json com o que o runtime na cain v0.4.13rc12 comprovou.

  * IB-F002 FIXED: os 3 vetores congelados do holdout dão REQUIRE_HUMAN SEALED_SCOPE (R16), receipts iguais em 3
    processos, no N+1 congelado e no integrado; nenhum pedido de 2025+ despachado;
  * IB-F006 FIXED: na rc12 (cain#72) o modo de proposta do LLM não quebra mais com o pedido sem parameters (o explain
    responde com um erro fechado, sem traceback);
  * IB-F008: evidência do protected_check (cadeia preservada);
  * IB-F009 (novo): o piso de ≥ 5 propostas de LLM do perfil é inatingível para o Brasileirão na rc12 (o CAIN não
    pergunta ao modelo: NO_ELIGIBLE_HYPOTHESIS, todo molde é um experimento já rodado, R17; sem parameters no pedido,
    proposal_overlays não se aplica). Decisão do dono (2026-09-28, pergunta com opções, depois de saber que uma rc13
    obrigaria o cripto e o stocks, já QUALIFIED na rc12, a refazer as fases): "Waiver do piso de LLM (Recommended)".
Toda evidência é um arquivo do run (sha256 calculado aqui). Uso: python findings_rc12.py <qualification/integration-brasileirao> <run>
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

M = "qualification/integration-brasileirao"


def main() -> int:
    q, run = Path(sys.argv[1]), sys.argv[2]
    root = q.parents[1]
    r = f"{M}/RAW_LOGS/runtime/{run}"

    def ev(*paths):
        return [{"file": p, "sha256": hashlib.sha256((root / p).read_bytes()).hexdigest()} for p in paths]

    doc = json.loads((q / "FINDINGS.json").read_text(encoding="utf-8"))
    by = {f["id"]: f for f in doc["findings"]}
    assert "IB-F009" not in by
    soak = json.loads((root / r / "soak/SUMMARY.json").read_text(encoding="utf-8"))
    failed = [c["check"] for c in soak["checks"] if not c["ok"]]
    assert failed == ["floor llm_proposals >= 5"], failed
    by["IB-F002"].update(status="FIXED", resolution=(
        "cain v0.4.13rc12 (R16 SEALED_SCOPE, brasileirao.json com os 3 sealed_scopes): os vetores holdout 01-season-2025, "
        "02-window-into-2025 e 03-season-2026 dão REQUIRE_HUMAN SEALED_SCOPE, receipts iguais em 3 processos novos, no N+1 "
        "congelado e no integrado; nunca despachados"))
    by["IB-F002"]["evidence"] += ev(f"{r}/n-plus-1/frozen/SUMMARY.json", f"{r}/n-plus-1/integrated/SUMMARY.json")
    by["IB-F006"].update(status="FIXED", resolution=(
        "cain#72 (na rc11 e na rc12): o caminho do LLM aceita pedido sem parameters; no soak da rc12 o explain responde "
        "com o erro fechado LLM_PROPOSAL_FAILED/NO_ELIGIBLE_HYPOTHESIS, sem traceback (a causa do piso é o IB-F009)"))
    by["IB-F006"]["evidence"] = ev(f"{r}/soak/commands.log", f"{r}/soak/SUMMARY.json")
    by["IB-F008"]["evidence"] = ev(f"{M}/RAW_LOGS/protected/protected_check.json")
    doc["findings"].append({
        "id": "IB-F009", "severity": "P1",
        "title": "piso de ≥ 5 propostas de LLM do soak inatingível para o Brasileirão na cain v0.4.13rc12",
        "description": "No soak na rc12, os 6 pedidos `cain research explain --propose-for-domain brasileirao` terminam "
                       "com LLM_PROPOSAL_FAILED: NO_ELIGIBLE_HYPOTHESIS ('DUPLICATE EQUIVALENT_REQUEST'), sem chamar o "
                       "modelo. O molde do LLM é sempre uma task já emitida com a hipótese trocada; o pedido do "
                       "Brasileirão não tem parameters, então proposal_overlays não gera outro experimento, e a R17 "
                       "segura todas as hipóteses. Todos os outros pisos e conferências do soak passaram.",
        "classification": "C6 P1: limite real do framework para domínio sem parameters, sem violação observada (nenhuma "
                          "proposta sai, nada é despachado); a saída seria uma rc13 com sobreposição de campos do pedido "
                          "(o que obrigaria o cripto e o stocks, já QUALIFIED na rc12, a refazer as fases pela C14).",
        "evidence": ev(f"{r}/soak/SUMMARY.json", f"{r}/soak/commands.log"),
        "status": "ACCEPTED_LIMITATION",
        "owner_decision_taken": {"date": "2026-09-28", "by": "dono",
                                 "channel": "chat da sessão integration-brasileirao (pergunta com opções)",
                                 "words": "Waiver do piso de LLM (Recommended)"},
        "applied": "o gate SOAK conta o piso de LLM como dispensado pelo dono só para o Brasileirão; a conferência que "
                   "falhou continua no SUMMARY.json do soak (61 de 62) e é citada na nota do gate",
    })
    (q / "FINDINGS.json").write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print({f["id"]: f["status"] for f in doc["findings"]})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
