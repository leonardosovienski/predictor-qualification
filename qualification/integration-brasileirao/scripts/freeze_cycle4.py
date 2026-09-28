"""integration-brasileirao, ciclo 4 da freeze-parameters (decisão do dono, 2026-09-28: "1 hipótese por ciclo").

No diagnóstico privado do soak na rc10 (não é evidência), as 3 hipóteses de qualificação em rodízio por 24 experimentos
diferentes deram SUPPORTED contra climatologia e REFUTED contra mercado na mesma hipótese; a R10 para corretamente e o
piso de 20 ciclos fica inatingível. Decisão do dono: uma hipótese de qualificação por ciclo do soak
(brasileirao:QUAL-SOAK-001..024, cada uma um experimento só), no brasileirao.json da rc11.

  python freeze_cycle4.py profile <qualification/integration-brasileirao>
      antes dos geradores: preserva o perfil do ciclo 2 e grava o perfil do ciclo 4 (só plan.cycles e cycle mudam);
  python freeze_cycle4.py record <qualification/integration-brasileirao>
      depois de build_vectors.py e freeze_parameters.py: GATES (ciclo 4, fase freeze-parameters-c4), FINDINGS (IB-F006
      e IB-F007) e QUALIFICATION_CHANGELOG.md;
  python freeze_cycle4.py check <qualification/integration-brasileirao> <out.json>
      conferência mecânica: o que mudou em relação ao ciclo 3 é só o declarado.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

M = "qualification/integration-brasileirao"
SOAK = [f"brasileirao:QUAL-SOAK-{n:03d}" for n in range(1, 25)]
DECISION = {"date": "2026-09-28", "by": "dono", "channel": "chat da sessão integration-brasileirao (pergunta com opções)",
            "words": "1 hipótese por ciclo (Recommended)"}
PROFILE = "QUALIFICATION_PROFILE_INTEGRATION_BR_V1.json"


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def profile(q: Path) -> None:
    raw = (q / PROFILE).read_bytes()
    keep = q / f"QUALIFICATION_PROFILE_INTEGRATION_BR_V1_cycle2_{sha(raw)[:12]}.json"
    assert not keep.exists()
    keep.write_bytes(raw)
    doc = json.loads(raw)
    doc["plan"]["cycles"] = ("24 ciclos, cada um com a sua hipótese de qualificação admitida pela policy de operador da "
                             "missão (brasileirao:QUAL-SOAK-001..024, uma por ciclo, cada uma um experimento só: nenhuma "
                             "contradição é possível), pedidos distintos por request_id (brasileirao:REQ-IB-SOAK-<nnn>), "
                             "dataset real-20260908 v1, só temporadas 2021–2024 (FROZEN_VECTORS.json → soak_generator)")
    doc["cycle"] = {"number": 4, "supersedes": keep.name,
                    "owner_decision": DECISION,
                    "why": "com 3 hipóteses em rodízio, o dado real deu SUPPORTED × REFUTED na mesma hipótese e a R10 "
                           "travava o soak (diagnóstico privado na rc10); só plan.cycles muda; pisos, definições, "
                           "tolerância zero e conferências finais sem mudança"}
    (q / PROFILE).write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("profile", keep.name, sha((q / PROFILE).read_bytes()))


def record(q: Path) -> None:
    root = q.parents[1]
    evidence = [f"{M}/RAW_LOGS/freeze/freeze_parameters_cycle4.log", f"{M}/RAW_LOGS/freeze/cycle4_check.json"]
    gates = json.loads((q / "GATES.json").read_text(encoding="utf-8"))
    gates["cycle_history"] = gates.get("cycle_history", []) + [gates["cycle"]]
    gates["cycle"] = {"number": 4, "owner_decision": DECISION,
                      "why": "uma hipótese de qualificação por ciclo do soak (QUAL-SOAK-001..024) no brasileirao.json da "
                             "rc11; rc11 também corrige o caminho do LLM para pedidos sem parameters (IB-F006); fases a "
                             "partir do cleanroom-final na rc11 (C14)"}
    gates["phases_completed"].append("freeze-parameters-c4")
    gates["freeze_cycle4_evidence"] = evidence
    (q / "GATES.json").write_text(json.dumps(gates, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    findings = json.loads((q / "FINDINGS.json").read_text(encoding="utf-8"))
    ids = {f["id"] for f in findings["findings"]}
    assert not ids & {"IB-F006", "IB-F007"}
    findings["findings"] += [
        {"id": "IB-F006", "severity": "P1",
         "title": "o modo de proposta do LLM do cain v0.4.13rc10 quebra para o Brasileirão (KeyError 'parameters')",
         "description": "`cain research explain --propose-for-domain brasileirao` morre antes de chamar o modelo: "
                        "src/cain/orchestration/llm.py:204 lê p['parameters'] de cada task emitida, e o pedido do "
                        "Brasileirão (brasileirao-research-request/1) não tem parameters. Reproduzido no diagnóstico "
                        "privado do soak na rc10 (fb0e1dc), depois de 16 ciclos reais.",
         "classification": "C6 P1: defeito real do framework, sem violação observada (nenhuma proposta sai; nada é "
                           "despachado); torna o piso de ≥ 5 propostas de LLM do perfil inatingível na rc10.",
         "evidence": [], "status": "OPEN",
         "fix": "sessão STOCKS, commit f7b56c0 do cain (branch integration-stocks/proposal-overlays-20260928): "
                "p.get('parameters', {}) nos 4 acessos do caminho do LLM + teste "
                "tests/integration/test_orchestration.py::test_llm_proposal_for_a_domain_whose_request_has_no_parameters; "
                "entra na rc11. Fecha quando o soak na rc11 fizer as propostas de LLM chegarem a uma decisão."},
        {"id": "IB-F007", "severity": "P2",
         "title": "o plano congelado do soak (3 hipóteses em rodízio por 24 experimentos) não alcança o piso de ciclos",
         "description": "No diagnóstico privado do soak na rc10, QUAL-SERVING-REAL-001 e -003 receberam SUPPORTED "
                        "(contra climatologia) e REFUTED (contra mercado); a R10 CONTRADICTION_UNRESOLVED para as duas "
                        "hipóteses (comportamento correto do CAIN: contradição nunca decidida por maioria) e o soak "
                        "fica em 16 ciclos (piso 20).",
         "classification": "C6 P2: defeito do desenho do plano da missão, não do CAIN nem do domínio; sem efeito em "
                           "resultado ou operação.",
         "evidence": [], "status": "FIXED",
         "owner_decision_taken": DECISION,
         "resolution": "ciclo 4 da freeze-parameters: uma hipótese de qualificação por ciclo do soak "
                       "(brasileirao:QUAL-SOAK-001..024), definidas antes da execução, no brasileirao.json da rc11; "
                       "pisos e critérios sem mudança"},
    ]
    for f in findings["findings"]:
        if f["id"] in ("IB-F006", "IB-F007"):
            f["evidence"] = [{"file": e, "sha256": sha((root / e).read_bytes())} for e in evidence]
    (q / "FINDINGS.json").write_text(json.dumps(findings, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    log = q / "QUALIFICATION_CHANGELOG.md"
    log.write_text(log.read_text(encoding="utf-8").rstrip("\n") + "\n\n" + CHANGELOG, encoding="utf-8")
    print("record ok")


def check(q: Path, out: Path) -> int:
    checks = []

    def ok(name, cond, **detail):
        checks.append({"check": name, "ok": bool(cond), **detail})

    def load(name):
        return json.loads((q / name).read_text(encoding="utf-8"))

    p4, p3 = load("FROZEN_PARAMETERS.json"), load("FROZEN_PARAMETERS_cycle3_baf78dafe45d.json")
    b4, b3 = p4["decision_policy"]["brasileirao_config"], p3["decision_policy"]["brasileirao_config"]
    ok("brasileirao_config: only proposable_hypotheses changed",
       sorted(k for k in set(b4) | set(b3) if b4.get(k) != b3.get(k)) == ["proposable_hypotheses"])
    ok("proposable_hypotheses = cycle 3 + QUAL-SOAK-001..024",
       sorted(b4["proposable_hypotheses"]) == sorted(b3["proposable_hypotheses"] + SOAK))
    ok("operator_env.hypotheses = cycle 3 + QUAL-SOAK-001..024",
       sorted(p4["operator_env"]["hypotheses"]) == sorted(p3["operator_env"]["hypotheses"] + SOAK))
    top = sorted(k for k in set(p4) | set(p3) if p4.get(k) != p3.get(k))
    base4, base3 = dict(p4["base"]), dict(p3["base"])
    fw4, fw3 = dict(base4.pop("framework_from_integration_stocks")), dict(base3.pop("framework_from_integration_stocks"))
    reports4, reports3 = fw4.pop("decision_policy_reports"), fw3.pop("decision_policy_reports")
    # the only change allowed in `base`: the sha256 of the other missions' DECISION_POLICY_REPORT.md as read at freeze
    # time (they were updated on main by those missions), same paths
    ok("FROZEN_PARAMETERS.base: only the sha256 of the other missions' DECISION_POLICY_REPORT.md (same paths) changed",
       base4 == base3 and fw4 == fw3 and [r["path"] for r in reports4] == [r["path"] for r in reports3]
       and all(sha((q.parents[1] / r["path"]).read_bytes()) == r["sha256"] for r in reports4),
       reports=[{"path": r["path"], "cycle3": o["sha256"][:12], "cycle4": r["sha256"][:12]}
                for r, o in zip(reports4, reports3)])
    ok("FROZEN_PARAMETERS.soak_profile points to the cycle-4 profile",
       p4["soak_profile"]["sha256"] == sha((q / PROFILE).read_bytes())
       and {k: v for k, v in p4["soak_profile"].items() if k != "sha256"}
       == {k: v for k, v in p3["soak_profile"].items() if k != "sha256"})
    ok("FROZEN_PARAMETERS: only base (reports), brasileirao_config, operator_env, cycle and the pointers to the new "
       "vectors/profile",
       top == ["base", "cycle", "decision_policy", "frozen_vectors", "operator_env", "protected_set_initial",
               "soak_profile"]
       and sorted(k for k in p4["decision_policy"] if p4["decision_policy"][k] != p3["decision_policy"].get(k))
       == ["brasileirao_config"], top=top)
    ok("rule_order unchanged", p4["decision_policy"]["rule_order"] == p3["decision_policy"]["rule_order"])
    ok("sealed_scopes unchanged", b4["sealed_scopes"] == b3["sealed_scopes"])
    v4, v3 = load("FROZEN_VECTORS.json"), load("FROZEN_VECTORS_cycle3_913680e90e0e.json")
    sections = sorted(k for k in set(v4) | set(v3) if k != "cycle" and v4.get(k) != v3.get(k))
    ok("FROZEN_VECTORS: only soak_generator changed", sections == ["soak_generator"], sections=sections)
    g4, g3 = v4["soak_generator"], v3["soak_generator"]
    ok("soak_generator: one QUAL-SOAK hypothesis per cycle; schedule, request_id, dataset and cycles unchanged",
       g4["hypotheses"] == SOAK and len(g4["hypotheses"]) == g4["cycles"] == len(g4["schedule"])
       and all(g4[k] == g3[k] for k in ("schedule", "request_id", "dataset", "cycles")))
    f4 = load(PROFILE)
    f2 = json.loads(next(q.glob("QUALIFICATION_PROFILE_INTEGRATION_BR_V1_cycle2_*.json")).read_text(encoding="utf-8"))
    ok("profile: only plan.cycles and cycle changed; minimums, definitions and zero tolerance unchanged",
       sorted(k for k in set(f4) | set(f2) if f4.get(k) != f2.get(k)) == ["cycle", "plan"]
       and sorted(k for k in f4["plan"] if f4["plan"][k] != f2["plan"].get(k)) == ["cycles"])
    bad = [rel for rel, e in v4["files"].items() if sha((q / rel).resolve().read_bytes()) != e["sha256"]]
    ok("every vector file matches its manifest sha256", not bad, mismatched=bad)
    doc = {"schema": "integration-brasileirao/CYCLE4_CHECK/1", "checks": checks,
           "passed": sum(c["ok"] for c in checks), "failed": sum(not c["ok"] for c in checks)}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({k: doc[k] for k in ("passed", "failed")}))
    for c in checks:
        if not c["ok"]:
            print("FAILED", json.dumps(c, ensure_ascii=False))
    return 0 if doc["failed"] == 0 else 1


CHANGELOG = """## Ciclo 4 da freeze-parameters (decisão do dono: uma hipótese por ciclo do soak)

No diagnóstico privado do soak na rc10 (não é evidência), as 3 hipóteses de qualificação em rodízio por 24 experimentos
diferentes receberam SUPPORTED contra climatologia e REFUTED contra mercado na mesma hipótese. A R10
CONTRADICTION_UNRESOLVED parou corretamente essas hipóteses, e o soak ficou em 16 ciclos (piso 20) (IB-F007). Decisão do
dono no chat desta sessão, 2026-09-28: "1 hipótese por ciclo".

| Arquivo | Mudança |
|---|---|
| `FROZEN_PARAMETERS.json` | `brasileirao_config.proposable_hypotheses` e `operator_env.hypotheses` + `brasileirao:QUAL-SOAK-001..024`; ciclo 4 |
| `FROZEN_VECTORS.json` | `soak_generator`: uma hipótese por ciclo (o mesmo calendário de 24 experimentos) |
| `QUALIFICATION_PROFILE_INTEGRATION_BR_V1.json` | só `plan.cycles` e o bloco `cycle`; pisos e critérios iguais |
| `*_cycle3_<sha12>.json`, perfil `*_cycle2_<sha12>.json` | preservados byte a byte |
| `scripts/operator_env.py` | a policy do operador admite as 24 hipóteses |

O mesmo diagnóstico achou o IB-F006: na rc10, o modo de proposta do LLM quebra para o Brasileirão (`KeyError
'parameters'` em `llm.py:204`, o pedido do Brasileirão não tem parameters). A correção é da sessão STOCKS e entra na
rc11 junto com o brasileirao.json deste ciclo. Conferência mecânica: `scripts/freeze_cycle4.py check`.
"""


if __name__ == "__main__":
    mode, q = sys.argv[1], Path(sys.argv[2])
    if mode == "profile":
        profile(q)
    elif mode == "record":
        record(q)
    else:
        raise SystemExit(check(q, Path(sys.argv[3])))
