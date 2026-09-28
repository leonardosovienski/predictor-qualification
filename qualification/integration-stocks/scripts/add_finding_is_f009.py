"""integration-stocks: registra o IS-F009 (disputa de consumidores) com a decisão do dono, no ciclo 3.

O teste de disputa (scripts/race.py, RAW_LOGS/pos-attestation-c2/race/) rodou depois da attestation do ciclo 2 e foi
registrado no CHANGELOG (PR #82); pela decisão do dono, o achado entra no FINDINGS.json na reemissão seguinte, que é
a do ciclo 3. Os números saem do RACE.json. Idempotente: não duplica o achado.
Uso: python add_finding_is_f009.py <raiz do predictor-qualification>
"""

from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(sys.argv[1])
M = ROOT / "qualification/integration-stocks"


def ref(rel: str) -> dict:
    return {"file": f"qualification/integration-stocks/{rel}", "sha256": hashlib.sha256((M / rel).read_bytes()).hexdigest()}


def main() -> int:
    path = M / "FINDINGS.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    if any(f["id"] == "IS-F009" for f in doc["findings"]):
        print("IS-F009 já registrado")
        return 0
    race = json.loads((M / "RAW_LOGS/pos-attestation-c2/race/RACE.json").read_text(encoding="utf-8"))
    spurious = Counter(x["status"] for r in race["rows"] for x in r["results_in_spool"]
                       if x["status"] not in ("RESULT", "DUPLICATE"))
    reps, ok = race["reps"], race["ok"]
    doc["findings"].append({
        "id": "IS-F009",
        "severity": "P2",
        "title": "dois consumidores do stocks na mesma task: o perdedor publica envelope falso, e o "
                 "RECONCILIATION_REQUIRED faz o CAIN segurar o domínio (R09)",
        "description": (
            f"Teste de disputa (scripts/race.py, {reps} repetições no runtime qualificado do ciclo 2: cain 0.4.13rc12, "
            "stocks-predictor 0.3.0rc3, transporte 0.1.0rc5). Dois predictor-research-consumer começam juntos sobre a "
            f"mesma task real. Em {ok} das {reps}: um experimento no journal, uma admissão, RESULT terminal ingerido e "
            "nenhuma queda de processo. Em todas, o perdedor publica um envelope falso ao lado do RESULT do vencedor: "
            + ", ".join(f"{n}× {s}" for s, n in sorted(spurious.items()))
            + ". OPS_FAILED_RETRYABLE vem de 'OPS_SKIPPED lock_not_acquired' (a trava do Ops funciona, mas a perda é "
            "anunciada como falha); RECONCILIATION_REQUIRED vem de 'materialized reference changed after "
            "materialization: readiness' (o stocks materializa as referências no estado do domínio antes do run_job "
            "do Ops, fora da trava). O CAIN ingere o REQUIRES_HUMAN e a proposta seguinte vira REQUIRE_HUMAN "
            "DOMAIN_RECONCILIATION_PENDING (R09): parada falsa, fail-closed. Mesmo padrão do cripto (IC-F016, IC-F017)."),
        "classification": ("C6 P2: sem efeito duplicado nem perdido; o efeito é uma parada fail-closed que pede humano, "
                           "e só com dois consumidores do mesmo domínio ao mesmo tempo."),
        "evidence": [ref("RAW_LOGS/pos-attestation-c2/race/RACE.json"), ref("RAW_LOGS/pos-attestation-c2/race/race.log"),
                     ref("scripts/race.py")],
        "status": "ACCEPTED_LIMITATION",
        "owner_decision": ("escolher: (a) registrar + regra (um consumidor por domínio por vez, como no cripto); (b) "
                           "registrar e reemitir já; (c) corrigir no stocks (trava antes da materialização; código fora "
                           "dos adapter_paths, reabre a Etapa A pela C24.4); (d) não registrar"),
        "owner_decision_taken": {
            "date": "2026-09-28", "by": "dono", "channel": "chat da sessão (pergunta com opções)",
            "words": "Registrar + regra (Recomendado)",
            "option_text": ("Mesma regra do cripto: um consumidor por domínio por vez. Registro agora no CHANGELOG da "
                            "integration-stocks, como pós-attestation (a attestation segue válida), e o achado IS-F009 "
                            "(P2) entra no FINDINGS.json na próxima reemissão. Sem mudar código."),
            "applied": ("CHANGELOG pós-attestation do ciclo 2 (PR #82); este registro no ciclo 3. Regra de operação: um "
                        "consumidor por domínio por vez (o agendador do Ops já garante). Código sem mudança.")},
    })
    path.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("IS-F009 registrado:", dict(spurious))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
