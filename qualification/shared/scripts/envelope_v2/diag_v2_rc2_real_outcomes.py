"""DIAGNÓSTICO (não é evidência de gate): outcomes reais dos três domínios pelo envelope V2 rc2.

Roda no venv do domínio (wheel final da Etapa A + lock do final_commit + wheel rc2 do protocolo).
Monta o laboratório sintético da suíte de conformidade congelada do domínio (fixtures do final_commit,
dados sintéticos, sem dado real), embrulha pedidos em ResearchTaskV2 de episódios do domínio, submete os
bytes exatos pelo adapter_api (Circuit.submit_request) e embrulha cada outcome em ResearchResultV2.

Confere: registro × constantes instaladas do contrato; hash canônico do pedido = vetor da Etapa A
(C24.3 d); payload V2 == canonical(resultado) == bytes relidos por Circuit.show; client_ref ecoado;
episódio ecoado; reenvio → DUPLICATE; mesmo pedido em episódio posterior → task nova e DUPLICATE com o
mesmo resultado; conteúdo diferente → CONFLICT; canário do futuro; resultado de outro domínio rejeitado.
Stocks: STATE_BUSY_RETRYABLE real (admission.sqlite travado por outra conexão) → representável na rc2.

Uso: python diag_v2_rc2_real_outcomes.py <domínio> <src_dir> <lab_dir>
"""

from __future__ import annotations

import copy
import importlib
import json
import os
import sqlite3
import sys
from pathlib import Path

from research_protocol import v2

DOMAIN, SRC, LAB = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
LAB.mkdir(parents=True, exist_ok=False)
CONTRACT = {
    "crypto": "GarimpoInvestimentos.research_contract",
    "stocks": "stocks_predictor.research_contract",
    "brasileirao": "brasileirao_predictor.research_runtime.contract",
}[DOMAIN]
RUNNER = {
    "crypto": "GarimpoInvestimentos.research_runner",
    "stocks": "stocks_predictor.research_runner",
    "brasileirao": "brasileirao_predictor.research_runtime.runner",
}[DOMAIN]
ADAPTER = {"distribution": "diagnostic", "version": "0", "module": "diag_v2_rc2_real_outcomes"}
contract = importlib.import_module(CONTRACT)
Circuit = importlib.import_module(RUNNER).Circuit
report: dict = {"domain": DOMAIN, "protocol": v2.__name__, "registry_sha256": v2.REGISTRY_SHA256, "checks": []}
STAMP = iter(f"2026-09-26T06:{m:02d}:00Z" for m in range(60))


def check(name: str, ok: bool, **detail) -> None:
    report["checks"].append({"check": name, "ok": bool(ok), **detail})
    print(("PASS " if ok else "FAIL ") + name, json.dumps(detail, ensure_ascii=False)[:300], flush=True)


# ------------------------------------------------------------------ laboratório (fixtures congeladas)
if DOMAIN == "brasileirao":
    os.environ["BRASILEIRAO_RESEARCH_TEST_ROOT"] = str(LAB)
    sys.path.insert(0, str(SRC))
    harness = importlib.import_module("tests.conformance.harness")
    fixtures = importlib.import_module("tests.conformance.fixtures")
    lab = harness.standard_lab({"synthetic": {}, "canary": {"canary": True}})
    STATE, POLICY, OBJECTS = lab.state, lab.policy_path, lab.objects

    def vector(request_id: str, **overrides) -> dict:
        return fixtures.request(request_id, **overrides)

    CANARY_VECTOR = {"dataset": "canary"}
else:
    sys.path.insert(0, str(SRC / "tests" / "conformance"))
    fixtures = importlib.import_module("fixtures")
    env = fixtures.build(LAB)
    STATE, POLICY, OBJECTS = env["state"], env["policy"], env["objects"]

    def vector(request_id: str, **overrides) -> dict:
        dataset = overrides.pop("dataset", "positive")
        return fixtures.request(request_id, dataset, **overrides)

    CANARY_VECTOR = {"dataset": "future_canary"}
circuit = Circuit(STATE, POLICY, OBJECTS)

# ------------------------------------------------------------------ registro × contrato instalado
entry = v2.REGISTRY["domains"][DOMAIN]
installed = {
    "request_schema_id": contract.REQUEST_SCHEMA,
    "result_schema_id": contract.RESULT_SCHEMA,
    "outcome_exit_codes": dict(contract.EXIT_CODES),
    "result_states": list(contract.RESULT_STATES),
    "operational_states": list(contract.OPERATIONAL_STATES),
    "scientific_states": list(contract.SCIENTIFIC_STATES),
    "economic_states": list(contract.ECONOMIC_STATES),
}
for key, value in installed.items():
    check(f"registro == instalado: {key}", entry[key] == value)
check("registro == instalado: OUTCOME_STATUSES", set(entry["outcome_exit_codes"]) == set(contract.OUTCOME_STATUSES))


def roundtrip(task: dict, label: str, expect: set[str]) -> dict:
    raw = v2.request_bytes(task)
    outcome = circuit.submit_request(raw, source="v2-diagnostic:" + task["task_id"])
    result = v2.build_result(task, outcome, adapter=ADAPTER, produced_at=next(STAMP))
    status = result["outcome"]["status"]
    check(f"{label}: status", status in expect, status=status, reason=result["outcome"]["reason"])
    check(f"{label}: client_ref ecoado", result["client_ref"] == task["payload"]["client_ref"])
    check(f"{label}: episode_id ecoado", result["episode_id"] == task["episode_id"], episode=result["episode_id"])
    again = v2.loads_result(v2.dumps_result(result, task=task), task=task)
    check(f"{label}: ida e volta canônica", again == result)
    if result["result"] is not None:
        payload = v2.domain_payload(result)
        check(f"{label}: payload == canonical(resultado do domínio)", payload == v2.domain_canonical(outcome["result"]))
        code, shown = Circuit(STATE).show(task["request_id"])
        check(f"{label}: payload_sha256 == show().result_sha256",
              code == 0 and shown["result_sha256"] == result["result"]["payload_sha256"])
        check(f"{label}: bytes relidos == payload", v2.domain_canonical(shown["result"]) == payload)
        states = {k: result["result"][k] for k in ("result_state", "operational_state", "scientific_state",
                                                   "economic_state")}
        check(f"{label}: estados copiados sem tradução",
              all(outcome["result"][k] == v for k, v in states.items()), **states)
        check(f"{label}: capital_permission false", result["result"]["capital_permission"] is False)
    return {"task": task, "result": result, "outcome": outcome}


def task_for(request: dict, n: int, previous: str | None = None, based_on=()) -> dict:
    return v2.build_task(DOMAIN, request, episode_id=v2.episode_id_for(DOMAIN, n), previous_task_id=previous,
                         based_on=list(based_on), proposal_id=f"cain:DIAG-{n}", created_at=next(STAMP))


# ------------------------------------------------------------------ episódios
req1 = vector(f"{DOMAIN}:REQ-V2RC2-1")
t1 = task_for(req1, 1)
check("C24.3(d): payload_sha256 == hash canônico do vetor da Etapa A (sem client_ref)",
      t1["payload_sha256"] == v2.digest(contract.canonical(req1)))
if hasattr(contract, "request_content_hash"):
    check("C24.3(d): payload_sha256 == request_content_hash do domínio",
          t1["payload_sha256"] == contract.request_content_hash(t1["payload"]))
e1 = roundtrip(t1, "ep1 pedido", {"RESULT"})
e1b = roundtrip(t1, "ep1 reenvio (mesmos bytes)", {"DUPLICATE"})
check("ep1 reenvio: mesmo payload", v2.domain_payload(e1b["result"]) == v2.domain_payload(e1["result"]))
first_result_id = e1["result"]["result"]["result_id"]
t2 = task_for(vector(f"{DOMAIN}:REQ-V2RC2-1"), 2, previous=t1["task_id"], based_on=[first_result_id])
check("ep2 mesmo pedido: task_id novo", t2["task_id"] != t1["task_id"])
e2 = roundtrip(t2, "ep2 mesmo pedido", {"DUPLICATE"})
check("ep2 mesmo pedido: mesmo result_id e payload (sem 2º efeito)",
      e2["result"]["result"]["result_id"] == first_result_id
      and v2.domain_payload(e2["result"]) == v2.domain_payload(e1["result"]))
changed = vector(f"{DOMAIN}:REQ-V2RC2-1", priority_hint="LOW") if DOMAIN != "brasileirao" else None
if changed is None:
    changed = copy.deepcopy(req1)
    changed["priority_hint"] = "LOW"
t3 = task_for(changed, 3, previous=t2["task_id"])
roundtrip(t3, "ep3 mesmo request_id, outro conteúdo", {"CONFLICT"})
t4 = task_for(vector(f"{DOMAIN}:REQ-V2RC2-CANARY", **CANARY_VECTOR), 4, previous=t3["task_id"])
e4 = roundtrip(t4, "ep4 canário do futuro", {"TEMPORAL_INTEGRITY_VIOLATION", "REJECTED", "RESULT"})
if e4["result"]["result"] is not None:
    check("ep4 canário ausente do payload", fixtures.CANARY not in e4["result"]["result"]["payload_canonical"])
for other in v2.DOMAINS:
    if other == DOMAIN:
        continue
    forged = dict(e1["result"], domain=other)
    try:
        v2.validate_result(forged, task=t1)
        check(f"resultado marcado {other} rejeitado", False)
    except v2.V2Error as exc:
        check(f"resultado marcado {other} rejeitado", True, code=exc.code)

# ------------------------------------------------------------------ stocks: STATE_BUSY_RETRYABLE real
if DOMAIN == "stocks":
    t5 = task_for(vector("stocks:REQ-V2RC2-BUSY"), 5, previous=t4["task_id"])
    lock = sqlite3.connect(Path(STATE) / "admission.sqlite", timeout=1, isolation_level=None)
    lock.execute("BEGIN EXCLUSIVE")
    try:
        busy = circuit.submit_request(v2.request_bytes(t5), source="v2-diagnostic-busy:" + t5["task_id"])
    finally:
        lock.execute("ROLLBACK")
        lock.close()
    (LAB / "state_busy_outcome.json").write_text(json.dumps(busy, sort_keys=True, ensure_ascii=False), encoding="utf-8")
    check("stocks busy: outcome real STATE_BUSY_RETRYABLE sem client_ref",
          busy["status"] == "STATE_BUSY_RETRYABLE" and "client_ref" not in busy and busy.get("request_id") is None,
          status=busy["status"], exit_code=busy.get("exit_code"), reason=busy.get("reason"))
    wrapped = v2.build_result(t5, busy, adapter=ADAPTER, produced_at=next(STAMP))
    check("stocks busy: representável na rc2 (RETRYABLE, client_ref nulo)",
          wrapped["client_ref"] is None and v2.OUTCOME_CLASSES[wrapped["outcome"]["status"]] == "RETRYABLE")
    roundtrip(t5, "stocks busy: reenvio da mesma task depois do lock", {"RESULT"})

report["ok"] = all(item["ok"] for item in report["checks"])
(LAB / "diag_report.json").write_text(json.dumps(report, indent=1, ensure_ascii=False), encoding="utf-8")
print("RESULTADO:", "OK" if report["ok"] else "FALHOU", f"({len(report['checks'])} checagens)")
sys.exit(0 if report["ok"] else 1)
