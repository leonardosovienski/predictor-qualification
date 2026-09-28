"""Diagnóstico local (não é prova, C3.1): o adapter do Brasileirão no checkout, contra o domínio real, com dados sintéticos.

Passos (processos separados):
  vector  <tree> <out.json>                      → vetor da Etapa A (tests/conformance/fixtures.request) [venv dev]
  task    <vector.json> <out.json>               → ResearchTaskV2 pelo protocolo congelado + hash do vetor [tools]
  submit  <tree> <task.json> <hashes.json> <out> → laboratório de conformidade + adapter.submit_task/reread [venv dev]
"""

import hashlib
import json
import sys
from pathlib import Path

mode = sys.argv[1]
if mode == "vector":
    sys.path.insert(0, sys.argv[2])
    from tests.conformance import fixtures

    Path(sys.argv[3]).write_text(json.dumps(fixtures.request("brasileirao:REQ-E2E-RUNTIME-001")), encoding="utf-8")
elif mode == "task":
    from research_protocol import v2

    vector = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    task = v2.build_task("brasileirao", vector, episode_id="brasileirao:episode-1", proposal_id="cain:ADAPTER-SMOKE",
                         created_at="2026-09-28T00:00:00Z")
    Path(sys.argv[3]).write_bytes(v2.dumps_task(task))
    Path(sys.argv[3] + ".hash").write_text(v2.request_content_hash(vector), encoding="utf-8")
elif mode == "submit":
    sys.path.insert(0, sys.argv[2])
    from brasileirao_predictor.adapters import research_v2 as adapter
    from tests.conformance import harness

    task = json.loads(Path(sys.argv[3]).read_text(encoding="utf-8"))
    vector_hash = Path(sys.argv[3] + ".hash").read_text(encoding="utf-8")
    manifest_hash = sys.argv[4]
    lab = harness.standard_lab()
    config = {"state": str(lab.state), "policy": str(lab.policy_path), "objects": str(lab.objects)}
    checks = {}
    outcome = adapter.submit_task(task, config)
    checks["status RESULT"] = outcome.get("status") == "RESULT"
    result = outcome.get("result") or {}
    checks["client_ref devolvido igual"] = outcome.get("client_ref") == task["payload"]["client_ref"]
    checks["hash canônico do pedido = vetor = Etapa A"] = (
        result.get("provenance", {}).get("request_content_hash") == vector_hash == manifest_hash)
    code, shown = adapter.reread(task["payload"]["request_id"], config)
    canon = lambda v: json.dumps(v, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()  # noqa: E731
    checks["show exit 0"] = code == 0
    checks["payload do adapter_api = show (bytes canônicos)"] = canon(result) == canon(shown.get("result", shown))
    again = adapter.submit_task(task, config)
    checks["reenvio = DUPLICATE com o mesmo result_id"] = (
        again.get("status") == "DUPLICATE" and (again.get("result") or {}).get("result_id") == result.get("result_id"))
    bad = dict(task, domain="stocks")
    try:
        adapter.request_bytes(bad)
        checks["task de outro domínio recusada"] = False
    except adapter.AdapterRefusal:
        checks["task de outro domínio recusada"] = True
    wrong = json.loads(json.dumps(task))
    wrong["payload"]["client_ref"] = {"schema": "research-client-ref/2", "task_id": "brasileirao:TASK-" + "0" * 32}
    try:
        adapter.request_bytes(wrong)
        checks["client_ref de outra task recusado"] = False
    except adapter.AdapterRefusal:
        checks["client_ref de outra task recusado"] = True
    out = {"identity": adapter.identity(), "checks": checks, "ok": all(checks.values()),
           "result_sha256": hashlib.sha256(canon(result)).hexdigest()}
    Path(sys.argv[5]).write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=1))
    lab.cleanup()
