"""integration-crypto: registra os achados da validação prática CAIN × cripto na rc10 (IC-F012..IC-F015).

Idempotente: não duplica achado existente. Evidência em RAW_LOGS/pratica-rc10/ (fora da prova de gate; diagnóstico
com as wheels publicadas da rc10, dados reais e o modelo local).
Uso: python add_findings_pratica.py <qualification/integration-crypto>
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


def ref(m: Path, rel: str) -> dict:
    return {"file": f"qualification/integration-crypto/{rel}", "sha256": hashlib.sha256((m / rel).read_bytes()).hexdigest()}


def main() -> int:
    m = Path(sys.argv[1])
    path = m / "FINDINGS.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    have = {f["id"] for f in doc["findings"]}
    audit, check, loop = "RAW_LOGS/pratica-rc10/A1/audit_config.json", "RAW_LOGS/pratica-rc10/A2/check_results.json", \
        "RAW_LOGS/pratica-rc10/loop/campaign.jsonl"
    new = [
        {"id": "IC-F012", "severity": "P2",
         "title": "config do CAIN aceita o que a admissão real do cripto não aceita: QUAL-SHADOW-001 e os datasets "
                  "positive v1 e future-canary v1",
         "description": ("Auditoria do crypto.json da wheel rc10 contra as fontes pinadas: 10 conferências OK e 2 "
                         "divergências com a admissão do domínio no ambiente real. (1) crypto:QUAL-SHADOW-001 é "
                         "proponível no CAIN, mas o cripto não a admite: no ciclo real custou 1 tarefa recusada "
                         "(HYPOTHESIS_NOT_ADMITTED), e depois a R15 a barrou. (2) Os datasets 'positive v1' e "
                         "'future-canary v1' são referências permitidas no CAIN e não existem no registro do domínio; "
                         "o modo LLM não escolhe referências (reusa o molde), então não chegaram a ser pedidos. Os três "
                         "itens vêm do vetor sintético da Etapa A, do qual partem os vetores congelados de N+1 "
                         "(00/01/02) e de contradição (01): tirá-los muda decisões esperadas congeladas."),
         "classification": "C6 P2: contido pela política (R15) e sem efeito em resultado ou operação; decisão do dono",
         "evidence": [ref(m, audit), ref(m, loop)],
         "status": "ACCEPTED_LIMITATION",
         "owner_decision": ("escolher: (a) manter e registrar (a R15 contém); (b) tirar os três itens e reconstruir "
                            "os vetores de N+1 e contradição com hipóteses reais (novo ciclo com vetores novos)"),
         "owner_decision_taken": {"date": "2026-09-28", "by": "dono",
                                  "channel": "chat da sessão cripto (pergunta com opções)",
                                  "words": "Manter e registrar (Recomendado)"}},
        {"id": "IC-F013", "severity": "P2",
         "title": "memória e contexto do LLM sem as métricas dos resultados (só rótulos de estado)",
         "description": ("No ciclo real (20 rodadas), os fatos da memória guardavam estado, classe, IDs e o hash do "
                         "payload, e o prompt do modo de proposta só trazia rótulos ('INCONCLUSIVE ×2'): o modelo "
                         "não via retorno líquido, IC nem amostra."),
         "classification": "C6 P2: limita a utilidade das propostas; sem efeito em resultado, capital ou decisão da política",
         "evidence": [ref(m, loop), ref(m, "RAW_LOGS/pratica-rc10/loop/episodes_final.json")],
         "status": "FIXED",
         "owner_decision_taken": {"date": "2026-09-28", "by": "dono", "channel": "chat da sessão cripto",
                                  "words": "Código + config (Recomendado)"},
         "fix": ("cain#73 (merge c3a28d9, na rc11): chave opcional result_metrics; números finitos nos fatos, no view e "
                 "no contexto do LLM; ciclo 3 dos congelados declara net_return_bps, net_ci_low_bps, net_ci_high_bps e "
                 "sample_size. Mini-ciclo com o código: 4/4 resultados com métricas no prompt."),
         "evidence_refs": ["qualification/integration-crypto/RAW_LOGS/pratica-rc10/loop-dev/campaign.jsonl"]},
        {"id": "IC-F014", "severity": "P2",
         "title": "findings check não reconhecia o ID qualificado (crypto:H9) de uma hipótese fechada",
         "description": ("`cain findings check --hypothesis-id H9` casava com a H9 fechada; `crypto:H9` (C18, o formato "
                         "do envelope V2) respondia 'não equivalente', porque o estado científico entra com IDs sem "
                         "prefixo. A proteção da orquestração não dependia disso (a R05 usa os IDs qualificados da "
                         "configuração)."),
         "classification": "C6 P2: sem efeito na orquestração (R05); consulta de equivalência respondia errado",
         "evidence": [ref(m, check)],
         "status": "FIXED",
         "owner_decision_taken": {"date": "2026-09-28", "by": "dono", "channel": "chat da sessão cripto",
                                  "words": "Código + config (Recomendado)"},
         "fix": "cain#73 (merge c3a28d9, na rc11): o ID qualificado do próprio domínio vale como o do estado; prefixo de outro domínio nunca casa"},
        {"id": "IC-F015", "severity": "P2",
         "title": "paráfrase de hipótese fechada não é detectada pelo findings check",
         "description": ("5 paráfrases de hipóteses fechadas (H1, H2, H4, H6, H9) sem ID nem família: 0 detectadas. A "
                         "política de equivalência é identidade ou Jaccard lexical ≥ 0,6 (valor inicial, não "
                         "calibrado, segundo a própria política), e o enunciado guardado de cada tentativa é o nome mais "
                         "os parâmetros em JSON. O embedding só ordena e nunca decide. Na orquestração, hipótese nova "
                         "vira REQUIRE_HUMAN (R11), então a paráfrase chega ao dono, mas sem aviso de semelhança."),
         "classification": "C6 P2: contido pela R11 (decisão humana); falta o aviso de semelhança ao dono",
         "evidence": [ref(m, check)],
         "status": "OPEN_AWAITING_OWNER",
         "owner_decision": ("escolher: (a) calibrar a equivalência (nova versão da política, por exemplo com enunciados "
                            "em linguagem natural das tentativas e limiar medido); (b) manter o comportamento atual "
                            "(identidade e família; paráfrase vai ao dono pela R11)")},
    ]
    added = [f["id"] for f in new if f["id"] not in have]
    doc["findings"].extend(f for f in new if f["id"] not in have)
    path.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("registrados:", added or "nenhum (já existiam)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
