"""integration-stocks: FINDINGS.json inicial (C6), gerado com os sha256 das evidências citadas.

Achados até o fim da fase baseline. Fases seguintes editam o arquivo (status) e acrescentam achados; este script só
cria o arquivo se ele não existir (nunca sobrescreve). Os achados conhecidos da Etapa A do Stocks (3 P2 abertos em
qualification/stocks/FINDINGS.json, ST-F006, ST-F007, ST-F008 aceitos pela D-21) não são repetidos aqui (9.5).

Uso: python findings_init.py <raiz do predictor-qualification>
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(sys.argv[1])
M = "qualification/integration-stocks"


def ev(rel: str) -> dict:
    return {"file": rel, "sha256": hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()}


FINDINGS = [
    {
        "id": "IS-F001",
        "severity": "P2",
        "title": "main do stocks-predictor diverge do runtime qualificado e declara a mesma versão",
        "description": "61fc017 (v0.3.0rc2, runtime_target) é ancestral do main e o merge 36081a6 do PR #96 tem a mesma "
                       "árvore (bea6dce6). O main (01c2212) tem mais 23 commits (#99, #101, #102, #104, #105, #106), "
                       "80 arquivos: no pacote só stocks_predictor/v2/, nada em stocks_predictor/adapters/, "
                       "pyproject.toml e uv.lock iguais, versão ainda 0.3.0rc2 com código diferente da wheel rc2. Uma "
                       "wheel construída do main teria o mesmo nome/versão e outros bytes.",
        "classification": "C6 P2: sem efeito nesta missão, porque base e runtime são identificados por commit e sha256 "
                          "(D-24) e nada de 61fc017..main entra; a ambiguidade de versão é risco fora do runtime "
                          "qualificado. O PR do adapter (base main) repete a situação: o main pós-merge conterá "
                          "#99–#106 + adapter e não será o commit qualificado (o final_commit é o da tag v0.3.0rc3).",
        "evidence": [ev(f"{M}/RAW_LOGS/c0/c0_preflight_6af1e32.log")],
        "status": "OPEN",
        "owner_decision": "nenhuma exigida para esta missão (D-24); opcional: numerar o main com versão própria",
    },
    {
        "id": "IS-F002",
        "severity": "P2",
        "title": "DecisionPolicy genérica exige custos em todo tipo de pedido: coleta do Stocks sempre bloqueada",
        "description": "cain.orchestration.policy.decide (R06) compara config.costs com request.parameters de todo "
                       "pedido. O pedido COLLECT_EXTERNAL_INTELLIGENCE do contrato do Stocks não tem fee_bps/slippage_bps, "
                       "então qualquer proposta de coleta recebe BLOCK COST_MODEL_MISMATCH (vetor n1/17-collection). A "
                       "configuração lista o tipo (handler_allowlist do contrato), mas o CAIN desta missão não consegue "
                       "propor coleta.",
        "classification": "C6 P2: falha fechada (o CAIN propõe menos do que o domínio aceita); sem efeito em resultado. "
                          "Corrigir exige mudar o framework (prompt da sessão 6.4 / §3.3 do prompt do Stocks: C14 do "
                          "cripto), fora da menor mudança suficiente.",
        "evidence": [ev(f"{M}/FROZEN_PARAMETERS.json"), ev(f"{M}/fixtures/proposals/n1/17-collection.json")],
        "status": "OPEN",
        "owner_decision": "decidir se o framework passa a aplicar custos só aos tipos de pedido que os carregam "
                          "(mudança no cain + C14 da integration-crypto e desta missão)",
    },
    {
        "id": "IS-F003",
        "severity": "P2",
        "title": "propostas de LLM do framework carregam um parâmetro do cripto: no Stocks viram SCHEMA_INVALID",
        "description": "cain.orchestration.llm.propose grava request.parameters.placebo_seed (parâmetro do contrato do "
                       "cripto). O request_schema do Stocks tem additionalProperties false e o protocolo congelado valida "
                       "o payload, então toda proposta de LLM do Stocks recebe BLOCK SCHEMA_INVALID (vetor "
                       "n1/18-llm-shape). O caminho de LLM só existe no soak e não é gate (C9).",
        "classification": "C6 P2: falha fechada, sem efeito em resultado nem em gate; o piso de ≥ 5 propostas "
                          "auditadas do soak conta propostas que chegam à política (mesma regra da integration-crypto).",
        "evidence": [ev(f"{M}/FROZEN_PARAMETERS.json"), ev(f"{M}/fixtures/proposals/n1/18-llm-shape.json")],
        "status": "OPEN",
        "owner_decision": "decidir se o framework passa a variar o pedido por parâmetro próprio de cada domínio "
                          "(mudança no cain + C14 da integration-crypto e desta missão)",
    },
    {
        "id": "IS-F004",
        "severity": "P2",
        "title": "regra 9.3 (HOSTED_CI só por run de push no SHA exato) inatingível no stocks-predictor",
        "description": "O .github/workflows/ci.yml do stocks-predictor (intocável pela D-24 (4c)) dispara push só em "
                       "main; o final_commit desta missão é o commit da tag v0.3.0rc3 numa branch e nunca terá run de "
                       "push, e o merge do PR cria outro SHA. A Etapa A do Stocks provou o CI do final_commit por "
                       "workflow_dispatch no SHA exato (qualification/stocks/HOSTED_CI_REPORT.md). cain e "
                       "ecosystem-predictor disparam push em qualquer branch e não têm o problema.",
        "classification": "C6 P2 (processo; sem efeito em resultado): o gate HOSTED_CI fica NOT_RUN com BLOCKED até "
                          "a decisão; o critério não é relaxado pelo agente (prompt da sessão 12).",
        "evidence": [ev(f"{M}/FROZEN_PARAMETERS.json")],
        "status": "OPEN_AWAITING_OWNER",
        "owner_decision": "aceitar, só para o stocks-predictor, o run workflow_dispatch do CI Pipeline no SHA exato do "
                          "final_commit como o run de C21 (precedente da Etapa A), ou indicar outro caminho",
    },
]


def main() -> int:
    path = ROOT / M / "FINDINGS.json"
    previous = json.loads(path.read_text(encoding="utf-8"))  # registro do C0 ABORTED (PRs #58/#59), preservado
    if previous.get("findings"):
        raise SystemExit("FINDINGS.json já tem achados; edite, não recrie")
    doc = {
        "schema": "integration-stocks/FINDINGS/1",
        "severity_scale": "C6: P0 quebra o que dá dinheiro ou faz perder; P1 defeito real sem violação observada; "
                          "P2 sem efeito em resultado ou operação",
        "status_values": ["OPEN", "OPEN_AWAITING_OWNER", "FIXED", "NOT_A_DEFECT", "ACCEPTED_LIMITATION"],
        "known_from_stage_a_not_repeated": "3 P2 abertos em qualification/stocks/FINDINGS.json; ST-F006; ST-F007 e "
                                           "ST-F008 aceitos pela D-21 (prompt da sessão 9.5)",
        "c0_history": "o registro ABORTED do C0 de 2026-09-27 (PRs #58/#59) continua na chave c0 abaixo; o C0 desta "
                      "execução passou (RAW_LOGS/c0/c0_preflight_9937894.log e c0_preflight_6af1e32.log)",
        "findings": FINDINGS,
    }
    doc["c0"] = previous["c0"]
    path.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({f["id"]: f["severity"] for f in FINDINGS}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
