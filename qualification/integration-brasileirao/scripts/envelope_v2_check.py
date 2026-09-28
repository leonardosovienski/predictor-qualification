"""integration-brasileirao, fase envelope-v2: o protocolo V2 consumido é a release congelada, sem mudança.

Conferências (só leitura; ambiente tools/ desta missão, instalado por `uv sync --locked` com a wheel pinada por sha256):
  1. versão instalada = 2.0.0rc2; wheel baixada da URL do ENVELOPE_V2_FREEZE.json com o sha256 do freeze;
  2. schemas e registro de domínios dentro da wheel instalada = sha256 do freeze; REGISTRY_SHA256 = domains.json;
  3. entrada brasileirao do registro = contrato do Brasileirão no main (sha256, request_schema canônico,
     adapter_paths, adapter_api);
  4. roundtrip determinístico com as fixtures V2 congeladas do Brasileirão (integration-crypto/fixtures/v2): task e
     resultado validam; reconstruir a task pelo build_task dá os mesmos bytes; o payload de domínio do resultado é o
     payload_canonical; o hash de conteúdo do pedido ignora client_ref;
  5. IDs do Brasileirão com domínio (C18): task_id, episode_id, request_id e hypothesis_id começam com "brasileirao:".
Imprime uma linha por conferência (CHECK <id> OK|FALHA <detalhe>) e um JSON-resumo; exit 1 se algo falhar.

Uso: python envelope_v2_check.py <raiz do predictor-qualification> <wheel baixada do protocolo> <saída.json>
"""

from __future__ import annotations

import hashlib
import json
import sys
from importlib import metadata
from importlib.resources import files
from pathlib import Path

import research_protocol
import research_protocol.v2 as v2

ROOT, WHEEL, OUT = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
FIX = ROOT / "qualification/integration-crypto/fixtures/v2/brasileirao"
checks: list[dict] = []


def check(cid: str, ok: bool, detail: str) -> None:
    checks.append({"id": cid, "ok": bool(ok), "detail": detail})
    print(f"CHECK {cid} {'OK' if ok else 'FALHA'} {detail}")


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


freeze = json.loads((ROOT / "qualification/shared/ENVELOPE_V2_FREEZE.json").read_bytes())
wheel = freeze["protocol"]["wheel"]
installed = metadata.version("predictor-research-protocol")
check("1/version", installed == freeze["protocol"]["version"], f"installed={installed} package={research_protocol.__file__}")
check("1/wheel-sha256", sha(WHEEL.read_bytes()) == wheel["sha256"], f"{WHEEL.name} sha256={sha(WHEEL.read_bytes())}")
for item in freeze["schemas"]:
    rel = item["in_wheel"].removeprefix("research_protocol/")
    raw = files("research_protocol").joinpath(rel).read_bytes()
    check(f"2/schema/{Path(rel).name}", sha(raw) == item["sha256"], f"sha256={sha(raw)}")
check("2/registry-sha256", v2.REGISTRY_SHA256 == next(s["sha256"] for s in freeze["schemas"]
                                                      if s["in_wheel"].endswith("domains.json")),
      f"REGISTRY_SHA256={v2.REGISTRY_SHA256}")
contract_raw = (ROOT / "qualification/brasileirao/DOMAIN_RESEARCH_CONTRACT.json").read_bytes()
contract = json.loads(contract_raw)
entry = v2.REGISTRY["domains"]["brasileirao"]
check("3/contract-sha256", entry["contract"]["sha256"] == sha(contract_raw), f"registry={entry['contract']['sha256']}")
check("3/request_schema", v2.canonical(entry["request_schema"]) == v2.canonical(contract["request_schema"]),
      f"$id={entry['request_schema']['$id']}")
check("3/adapter_paths", entry["adapter_paths"] == contract["adapter_paths"], f"{entry['adapter_paths']}")
check("3/adapter_api", entry["adapter_api"] == contract["adapter_api"], "função, reread e same_path_as_entrypoint")
for label in ("etapa-a", "h9"):
    task_raw = (FIX / f"task-{label}.json").read_bytes()
    result_raw = (FIX / f"result-{label}.json").read_bytes()
    task = v2.loads_task(task_raw)
    result = v2.loads_result(result_raw, task=task)
    request = {k: v for k, v in task["payload"].items() if k != "client_ref"}
    rebuilt = v2.build_task("brasileirao", request, episode_id=task["episode_id"], proposal_id=task["proposal_id"],
                            created_at=task["created_at"], based_on=task.get("based_on", []),
                            previous_task_id=task.get("previous_task_id"))
    check(f"4/{label}/task-bytes", v2.dumps_task(rebuilt) == task_raw, f"task_id={task['task_id']}")
    check(f"4/{label}/result-bytes", v2.dumps_result(result, task=task) == result_raw, f"status={result['outcome']['status']}")
    body = result["result"]
    check(f"4/{label}/payload", sha(body["payload_canonical"].encode("utf-8")) == body["payload_sha256"],
          f"payload_sha256={body['payload_sha256'][:16]}")
    other = dict(request, client_ref={"x": 1})
    check(f"4/{label}/content-hash-ignores-client_ref",
          v2.request_content_hash(request) == v2.request_content_hash(other),
          "request_content_hash igual com e sem client_ref")
    ids = [task["task_id"], task["episode_id"], task["payload"]["request_id"], task["payload"]["hypothesis_id"]]
    check(f"5/{label}/qualified-ids", all(i.startswith("brasileirao:") for i in ids), ", ".join(ids))
summary = {"schema": "integration-brasileirao/ENVELOPE_V2_CHECK/1", "protocol_version": installed,
           "registry_sha256": v2.REGISTRY_SHA256, "checks": len(checks),
           "ok": sum(c["ok"] for c in checks), "failed": [c["id"] for c in checks if not c["ok"]]}
OUT.write_text(json.dumps(summary, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps(summary, ensure_ascii=False))
raise SystemExit(0 if not summary["failed"] else 1)
