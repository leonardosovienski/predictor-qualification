"""integration-brasileirao: registra o C0 aprovado e os achados iniciais em FINDINGS.json (C6), sem apagar o histórico.

Preserva, byte a byte no conteúdo, o registro ``c0`` (ABORTED de 2026-09-26, PR #53) e as entradas de ``c0_rechecks``
(ABORTED de 2026-09-27 e 2026-09-28, PRs #60 e #66); acrescenta o C0 aprovado desta sessão como nova entrada de
``c0_rechecks`` e cria a lista ``findings``. Só roda uma vez: se ``findings`` já tiver itens, recusa (edite, não
recrie). Os achados conhecidos da Etapa A do Brasileirão (5 P2 abertos em qualification/brasileirao/FINDINGS.json,
BR-F019, A-04/BR-F010, docs do domínio, NO_EDGE) não são repetidos aqui (prompt da sessão 10.5).

Uso: python findings_init.py <raiz do predictor-qualification>
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(sys.argv[1])
M = "qualification/integration-brasileirao"
C0 = f"{M}/RAW_LOGS/c0-20260928-pass"


def ev(rel: str) -> dict:
    return {"file": rel, "sha256": hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()}


def c0_pass() -> dict:
    logs = [f"{C0}/c0_preflight_e78a39f.log", f"{C0}/c0_stage_b_base_e78a39f.log", f"{C0}/c0_reuse_stocks_e78a39f.log"]
    return {
        "state": "PASSED",
        "rule": "COMMON_QUALIFICATION_CORE.md v2.3, C0 + pré-voo 4.1–4.8 do prompt da sessão de 2026-09-27",
        "checked_at": "2026-09-28T02:44:48Z",
        "evidence_repo_ref": "origin/main e78a39f328247df39a68e4363f3daaa0236ff718",
        "common_core_sha256": "beaa5feed193356f554922439936ad401c8f177bfd18d8864ca329fae94216fc",
        "scripts": [f"{M}/scripts/c0_preflight.sh (+ c0_preconditions.py)", f"{M}/scripts/c0_stage_b_base.sh",
                    f"{M}/scripts/c0_reuse_stocks.sh"],
        "python": "3.13.15 gerenciado (~/predictors/tools), WSL do PC 2",
        "raw_logs": [{"path": e["file"], "sha256": e["sha256"]} for e in map(ev, logs)],
        "failed": [],
        "summary": "c0_falhas 0, sh_falhas 0, PYFAILS 0, reuse_falhas 0: núcleo, MANIFEST 13/13, D-16/19/22, "
                   "integration-crypto e integration-stocks QUALIFIED, Etapa A 3/3 e contratos, envelope V2 e "
                   "STACK_BASELINE_V2.0, SHARED-003/004/005, HYGIENE 13/13, base rc3 (runtime_target = attestation "
                   "a4fa2fee = baseline V2.0 = tag/asset; árvore 25cdf4d = d80a4ed = main), dado 31f30a4d, "
                   "PROVISION_RECEIPT, protocolo 2.0.0rc2, final_commits/final_wheels de cain e ecosystem-predictor "
                   "da integration-stocks (5 wheels com sha256 conferido) e DECISION_POLICY_REPORT das duas integrações",
        "relation_to_previous": "Este C0 aprovado substitui operacionalmente, para esta sessão, os registros ABORTED "
                                "acima (c0 de 2026-09-26 e c0_rechecks de 2026-09-27/28), que continuam como "
                                "histórico. Nenhum deles é parcial nem attestation.",
    }


FINDINGS = [
    {
        "id": "IB-F001",
        "severity": "P2",
        "title": "main do cain diverge do final_commit qualificado (política v2 e versão 0.4.13rc8 não publicada)",
        "description": "O final_commit do cain declarado pela integration-stocks QUALIFIED é deccaaa (cain-research "
                       "0.4.13rc7, política v1). O main do cain (0e8ae79) tem mais 6 commits, com árvore diferente: "
                       "#59 (política v2, regra R15, propostas por LLM ancoradas), #60 e #61 (declara 0.4.13rc8, não "
                       "publicada). O main do ecosystem-predictor (1fa9098) tem 2 merges depois de 1304b20, com a "
                       "mesma árvore.",
        "classification": "C6 P2: sem efeito nesta missão. A base do cain e do ecosystem-predictor é identificada por "
                          "commit e sha256 (prompt da sessão 7.4), e nada do main posterior entra. Mesmo fato do IS-F007 "
                          "da integration-stocks, não é defeito novo do domínio.",
        "evidence": [ev(f"{C0}/c0_reuse_stocks_e78a39f.log")],
        "status": "OPEN",
        "owner_decision": "nenhuma exigida para esta missão; a linha do cain é decisão do dono (reconciliação)",
    },
    {
        "id": "IB-F002",
        "severity": "P1",
        "title": "a DecisionPolicy qualificada não consegue devolver REQUIRE_HUMAN para proposta que exigiria o "
                 "holdout 2025",
        "description": "A decisão do dono 5.2 (D-25 (2)) exige REQUIRE_HUMAN para toda proposta que exigiria acesso ao "
                       "holdout 2025. A política genérica do cain em deccaaa (R01–R14) não lê season, events nem "
                       "data_cutoff do pedido. O schema cain-domain-config/1 tem chaves fixas (config.KEYS), e a "
                       "configuração do Brasileirão não tem onde declarar escopo lacrado. Com a hipótese de "
                       "qualificação, uma proposta da temporada 2025 sai ALLOW (R14), e só a admission do domínio a "
                       "recusa (REJECTED HOLDOUT_SEALED). A R15 da política v2 (#59) também não resolve: só age depois "
                       "de uma recusa HYPOTHESIS_NOT_ADMITTED. Uma regra nova muda a rule_order congelada no "
                       "FROZEN_PARAMETERS da integration-crypto (e herdada pela integration-stocks), o que é novo ciclo "
                       "dessas missões (C14 'Parâmetro/vetor/perfil congelado'), não só reemissão.",
        "classification": "C6 P1: requisito do dono não atendido, sem violação observada. O holdout continua lacrado "
                          "pela admission do domínio. O vetor congelado espera REQUIRE_HUMAN e vai falhar até a regra "
                          "existir; o agente não relaxa o critério (prompt da sessão 13).",
        "evidence": [ev(f"{C0}/c0_reuse_stocks_e78a39f.log")],
        "status": "OPEN_AWAITING_OWNER",
        "owner_decision": "(a) aprovar uma regra genérica de escopo lacrado no framework (configuração com escopos "
                          "lacrados por campo do pedido → REQUIRE_HUMAN SEALED_SCOPE; lista vazia para cripto e "
                          "stocks), com novo ciclo da rule_order nas três integrações; ou (b) aprovar explicitamente, "
                          "para o Brasileirão, BLOCK no CAIN + HOLDOUT_SEALED no domínio em lugar de REQUIRE_HUMAN. "
                          "Informação recebida da sessão cripto em 2026-09-28 (não vale como aprovação nesta sessão): "
                          "o dono teria escolhido reconciliar as linhas do cain no fim, incluindo essa regra",
    },
]


def main() -> int:
    path = ROOT / M / "FINDINGS.json"
    previous = json.loads(path.read_text(encoding="utf-8"))
    if previous.get("findings"):
        raise SystemExit("FINDINGS.json já tem achados; edite, não recrie")
    keep_c0, keep_rechecks = json.dumps(previous["c0"], sort_keys=True), json.dumps(previous["c0_rechecks"], sort_keys=True)
    doc = {
        "schema": "integration-brasileirao/FINDINGS/1",
        "severity_scale": previous["severity_scale"],
        "status_values": ["OPEN", "OPEN_AWAITING_OWNER", "FIXED", "NOT_A_DEFECT", "ACCEPTED_LIMITATION"],
        "known_from_stage_a_not_repeated": "5 P2 abertos em qualification/brasileirao/FINDINGS.json (entre eles "
                                           "BR-F019); A-04/BR-F010 FIXED (ExpiredHarnessAttestationWarning esperado); "
                                           "README.md e docs/ESTADO_ATUAL.md desatualizados por decisão do dono; "
                                           "resultado econômico NO_EDGE (C22); C0 ABORTED de 2026-09-26 (#53)",
        "c0": previous["c0"],
        "c0_rechecks": [*previous["c0_rechecks"], c0_pass()],
        "findings": FINDINGS,
    }
    assert json.dumps(doc["c0"], sort_keys=True) == keep_c0
    assert json.dumps(doc["c0_rechecks"][:-1], sort_keys=True) == keep_rechecks
    path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({f["id"]: f["severity"] for f in FINDINGS}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
