"""integration-crypto: registra IC-F016 e IC-F017 (disputa da trava do Ops, teste de ecossistema pós-attestation).

Dois consumidores do cripto iniciados ao mesmo tempo sobre a mesma task, o mesmo spool, o mesmo ledger e o mesmo estado,
20 repetições no Windows (PC 2) e 20 no Linux (WSL), com a cain 0.4.13rc12 e as wheels finais. Decisão do dono:
"Registrar + regra". Idempotente. Uso: python add_findings_disputa.py <qualification/integration-crypto>
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


def ref(m: Path, rel: str) -> dict:
    return {"file": f"qualification/integration-crypto/{rel}", "sha256": hashlib.sha256((m / rel).read_bytes()).hexdigest()}


DECISION = {"date": "2026-09-28", "by": "dono", "channel": "chat da sessão cripto (pergunta com opções)",
            "words": "Registrar + regra (Recomendado)",
            "option_text": ("Registro os dois como achados P2 do cripto (IC-F016 e IC-F017), com a regra operacional \"um "
                            "consumidor por domínio por vez\" (o agendador do Ops já serializa). Reemito a attestation só "
                            "pelos achados, sem refazer fases, e deixo anotada a correção para a próxima versão do cripto.")}
RULE = ("regra operacional: um consumidor por domínio por vez (uma execução do predictor-research-consumer por estado de "
        "domínio); o agendador do Ops já serializa os jobs")


def main() -> int:
    m = Path(sys.argv[1])
    path = m / "FINDINGS.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    have = {f["id"] for f in doc["findings"]}
    win, lin = "RAW_LOGS/ops-disputa-windows", "RAW_LOGS/ops-disputa-linux"
    new = [
        {"id": "IC-F016", "severity": "P2",
         "title": "no Windows, com dois consumidores do cripto sobre a mesma task, o processo perdedor pode morrer "
                  "(PermissionError) antes da trava do Ops",
         "description": ("Disputa da trava do Ops com a cain 0.4.13rc12 e as wheels finais: dois consumidores iniciados "
                         "ao mesmo tempo sobre a mesma task, spool, ledger e estado do domínio. No Windows (PC 2), em 1 "
                         "de 20 repetições, o perdedor morreu com PermissionError em "
                         "GarimpoInvestimentos/durable_io.atomic_write → os.replace de reference-materialization.json. "
                         "Essa escrita é feita por research_execution.execute antes do run_job do Ops, portanto fora da "
                         "trava do Ops, e no Windows os.replace falha se o outro processo está com o arquivo aberto. No "
                         "Linux, 0 quedas em 20. Nas 40 repetições houve exatamente uma admissão, um experimento e um "
                         "RESULT terminal no CAIN: nenhum efeito duplicado ou perdido. A trava do próprio Ops (a correção "
                         "SHARED-005 da 4.2.2rc1) nunca derrubou processo. Mesma classe de defeito da SHARED-005, em "
                         "outro ponto: o código do cripto, fora dos adapter_paths. O cenário não está na matriz de falhas "
                         "congelada."),
         "classification": "C6 P2: sem efeito em resultado ou operação (a task termina certa, com um experimento); "
                           "queda de um processo redundante, só no Windows, com dois consumidores concorrentes",
         "evidence": [ref(m, f"{win}/SUMMARY.json"), ref(m, f"{win}/commands.log"), ref(m, f"{lin}/SUMMARY.json")],
         "status": "ACCEPTED_LIMITATION", "owner_decision_taken": DECISION, "operational_rule": RULE,
         "fix_plan": ("próxima versão do cripto: tomar a trava do Ops (ou uma trava do pedido) antes da materialização das "
                      "referências, ou repetir o os.replace no Windows quando o destino está aberto por outro processo. "
                      "É código fora dos adapter_paths: pela C24.4, reabre a Etapa A do cripto quando for feito.")},
        {"id": "IC-F017", "severity": "P2",
         "title": "o consumidor que perde a disputa publica OPS_FAILED_RETRYABLE para uma task que o vencedor concluiu",
         "description": ("Na mesma disputa, em 39 das 40 repetições (19/20 no Windows, 20/20 no Linux), o consumidor "
                         "perdedor publicou um resultado OPS_FAILED_RETRYABLE (attempt 2) ao lado do RESULT do vencedor. "
                         "O CAIN guarda isso como RETRYABLE, não terminal, e mantém um único fato com o RESULT. Nada é "
                         "reexecutado nem duplicado, mas o registro sugere uma falha do Ops que não houve."),
         "classification": "C6 P2: sem efeito em resultado ou operação; registro enganoso para quem lê o inbox",
         "evidence": [ref(m, f"{win}/SUMMARY.json"), ref(m, f"{lin}/SUMMARY.json"), ref(m, f"{lin}/commands.log")],
         "status": "ACCEPTED_LIMITATION", "owner_decision_taken": DECISION, "operational_rule": RULE,
         "fix_plan": ("próxima versão: o perdedor da trava informa a task como já em execução ou concluída (DUPLICATE ou "
                      "SKIPPED), não como falha retryable; ponto de correção a localizar entre o adapter do cripto e o "
                      "consumidor do transporte")},
    ]
    added = [f["id"] for f in new if f["id"] not in have]
    doc["findings"].extend(f for f in new if f["id"] not in have)
    path.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("registrados:", added or "nenhum (já existiam)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
