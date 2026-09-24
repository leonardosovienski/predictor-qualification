"""stocks / D-16: ambiente de operador com o painel real (policy + objetos imutáveis + pedido do E2E).

Roda com o Python do runtime suportado (wheel instalada). Provisiona pela fronteira real do
operador (`ReferenceStore.put_operator_bytes`, a mesma dos vetores de conformidade) os objetos
do protocolo real (PROTOCOL_REAL.json), o painel `stocks-pit-panel/1` do construtor, a matriz de
prontidão congelada do final_commit e a fonte oficial VLMO (só para COLLECTION_ONLY). Confere que o
canonical do stocks_predictor reproduz byte a byte o painel do construtor (mesmo sha256).

Uso: python real_env.py <raiz> <dir do build> <PROTOCOL_REAL.json> <matriz.json> [--timeout N]
Saída: <raiz>/policy.json, <raiz>/objects/, <raiz>/requests/e2e.json, <raiz>/REAL_ENV.json
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

from stocks_predictor.research_admission import KNOWN_HANDLERS
from stocks_predictor.research_contract import canonical
from stocks_predictor.research_execution import ReferenceStore

DATASET = "b3-cvm-real"
SOURCE = "vlmo-real"
NAMES = {"dataset": DATASET, "universe": "real", "features": "momentum-12-1", "model": "quintile-real",
         "baseline": "ew-universe", "cost_model": "h1-frozen", "readiness": "matrix-20260921", "source": SOURCE}


def backtest_request(protocol: dict, request_id: str, as_of: str, *, control: dict | None = None,
                     ei: dict | None = None, client_ref=None) -> dict:
    req = protocol["request"]
    value = {
        "schema_version": "stocks-research-request/1",
        "request_id": request_id,
        "request_type": "BACKTEST_PIT_FACTOR",
        "research_id": req["research_id"],
        "hypothesis_id": req["hypothesis_id"],
        "references": {kind: {"name": NAMES[kind], "version": "v1"}
                       for kind in ("dataset", "universe", "features", "model", "baseline", "cost_model", "readiness")},
        "as_of": as_of,
        "pit": {"availability_rule": "AVAILABLE_AT_LE_DECISION_TIME", "minimum_pit_class": req["minimum_pit_class"]},
        "parameters": {"target": req["target"], "fee_bps": req["fee_bps"], "slippage_bps": req["slippage_bps"],
                       "max_securities": req["max_securities"],
                       "external_intelligence": ei or {"mode": "NONE", "families": []}},
        "priority_hint": "NORMAL",
    }
    if control is not None:
        value["parameters"]["negative_control"] = control
    if client_ref is not None:
        value["client_ref"] = client_ref
    return value


def collection_request(protocol: dict, request_id: str, observed_at: str, *, client_ref=None) -> dict:
    req = protocol["request"]
    value = {
        "schema_version": "stocks-research-request/1",
        "request_id": request_id,
        "request_type": "COLLECT_EXTERNAL_INTELLIGENCE",
        "research_id": "stocks:RESEARCH-D16-EI-COLLECTION",
        "hypothesis_id": req["collection_hypothesis_id"],
        "references": {"source": {"name": SOURCE, "version": "v1"},
                       "readiness": {"name": NAMES["readiness"], "version": "v1"}},
        "as_of": observed_at,
        "pit": {"availability_rule": "AVAILABLE_AT_LE_DECISION_TIME", "minimum_pit_class": req["collection_minimum_pit_class"]},
        "parameters": {"collector": "cvm-vlmo", "period": "2026", "observed_at": observed_at},
        "priority_hint": "NORMAL",
    }
    if client_ref is not None:
        value["client_ref"] = client_ref
    return value


def provision(root: Path, build: Path, protocol: dict, matrix: dict, timeout: int | None = None) -> dict:
    root.mkdir(parents=True, exist_ok=True)
    store = ReferenceStore(root / "objects")
    panel_raw = (build / "panel.json").read_bytes()
    panel = json.loads(panel_raw)
    if canonical(panel) != panel_raw:
        raise SystemExit("stocks_predictor canonical differs from the builder bytes (panel)")
    source_raw = (build / "vlmo_source.json").read_bytes()
    source = json.loads(source_raw)
    if canonical(source) != source_raw:
        raise SystemExit("stocks_predictor canonical differs from the builder bytes (VLMO source)")
    universe = dict(protocol["universe"])
    objects = {
        "dataset": panel,
        "universe": universe,
        "features": protocol["features"],
        "model": protocol["model"],
        "baseline": protocol["baseline"],
        "cost_model": protocol["cost_model"],
        "readiness": matrix,
        "source": source,
    }
    registry = []
    hashes = {}
    for kind in sorted(objects):
        object_hash = store.put_operator_bytes(canonical(objects[kind]))
        hashes[kind] = object_hash
        registry.append({"kind": kind, "name": NAMES[kind], "version": "v1",
                         "revision_id": f"{kind}:{NAMES[kind]}:d16-v1", "content_hash": object_hash})
    if hashes["dataset"] != hashlib.sha256(panel_raw).hexdigest():
        raise SystemExit("dataset object hash differs from the builder panel sha256")
    limits = dict(protocol["policy"]["limits"])
    if timeout is not None:
        limits["timeout_seconds"] = timeout
    policy = {
        "schema_version": "StocksResearchAdmissionPolicyV1",
        "policy_id": protocol["policy"]["policy_id"] + ("" if timeout is None else f"-timeout{timeout}"),
        "policy_version": protocol["policy"]["policy_version"],
        "owner": "STOCKS_OPERATOR",
        "requester_trust": "LOCAL_FILE_ONLY",
        "handlers": dict(KNOWN_HANDLERS),
        "hypotheses": {
            protocol["request"]["hypothesis_id"]: {"hypothesis_family": protocol["model"]["hypothesis_family"],
                                                   "purpose": "qualification probe on real B3/CVM data; not a scientific hypothesis"},
            protocol["request"]["collection_hypothesis_id"]: {"hypothesis_family": "stocks-ei-collection-only",
                                                              "purpose": "External Intelligence collection monitoring; never a trial"},
        },
        "registry": registry,
        "limits": limits,
        "allowed_collectors": ["cvm-vlmo"],
    }
    (root / "policy.json").write_text(json.dumps(policy, indent=1), encoding="utf-8")
    (root / "requests").mkdir(exist_ok=True)
    e2e = backtest_request(protocol, "stocks:REQ-D16-E2E-001", panel["data_cutoff"], client_ref={"d16": "e2e"})
    (root / "requests" / "e2e.json").write_text(json.dumps(e2e, indent=1), encoding="utf-8")
    env = {"object_hashes": hashes, "policy_sha256": hashlib.sha256((root / "policy.json").read_bytes()).hexdigest(),
           "data_cutoff": panel["data_cutoff"], "dataset_version": panel["dataset_version"],
           "timeout_seconds": limits["timeout_seconds"], "e2e_request_id": e2e["request_id"]}
    (root / "REAL_ENV.json").write_text(json.dumps(env, indent=1), encoding="utf-8")
    return {"root": root, "policy": root / "policy.json", "objects": root / "objects", "state": root / "s",
            "requests": root / "requests", "as_of": panel["data_cutoff"], "env": env}


def main() -> int:
    root, build, protocol_path, matrix_path = (Path(a) for a in sys.argv[1:5])
    timeout = int(sys.argv[sys.argv.index("--timeout") + 1]) if "--timeout" in sys.argv else None
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    env = provision(root, build, protocol, matrix, timeout)
    print(json.dumps(env["env"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
