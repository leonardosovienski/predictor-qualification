"""integration-stocks: ambiente de operador do Stocks (objetos de referência + policy de admission).

É a fronteira do operador do Stocks (não do CAIN): a mesma de qualification/stocks/d16/real_env.py da Etapa A
(PROTOCOL_REAL.json, painel stocks-pit-panel/1 do construtor, matriz de prontidão do final_commit, fonte VLMO), com os
valores congelados em FROZEN_PARAMETERS.json → operator_env: três hipóteses de qualificação no lugar de uma (rodízio
exigido pelo cooldown da política), as cinco hipóteses só para o LLM do ciclo 2 (o mesmo protocolo com controle
negativo de semente própria; FROZEN_VECTORS.json → llm_hypotheses) e o painel canário (FROZEN_PARAMETERS.json →
data.future_canary). Roda com o
stocks-predictor INSTALADO (ReferenceStore real, canonical do domínio). Não cria pedidos: na Etapa B os pedidos vêm
das tasks V2 do CAIN.

Uso: python operator_env.py <raiz> <dir do build do painel> <PROTOCOL_REAL.json> <matriz.json>
Saída: <raiz>/policy.json, <raiz>/objects/, <raiz>/REAL_ENV.json (impresso também).
"""

from __future__ import annotations

import copy
import hashlib
import json
import sys
from datetime import date, timedelta
from pathlib import Path

from stocks_predictor.research_admission import KNOWN_HANDLERS
from stocks_predictor.research_contract import canonical
from stocks_predictor.research_execution import ReferenceStore

HYPOTHESES = ("stocks:QUAL-PIT-MOM-REAL-001", "stocks:QUAL-PIT-MOM-REAL-002", "stocks:QUAL-PIT-MOM-REAL-003")
LLM_HYPOTHESES = tuple(f"stocks:QUAL-LLM-CTRL-{k:03d}" for k in range(1, 6))
COLLECTION_HYPOTHESIS = "stocks:QUAL-EI-COLLECTION-001"
POLICY_ID = "stocks-integration-qualification"
CANARY = "FUTURE_CANARY_STOCKS_INTEGRATION_001"
NAMES = {"universe": "real", "features": "momentum-12-1", "model": "quintile-real", "baseline": "ew-universe",
         "cost_model": "h1-frozen", "readiness": "matrix-20260921", "source": "vlmo-real"}


def canary_panel(panel: dict) -> tuple[dict, dict]:
    """FROZEN_PARAMETERS.json → data.future_canary.construction (same rule as the Stage A future_canary vector)."""
    value = copy.deepcopy(panel)
    value["dataset_version"] = panel["dataset_version"] + "-canary"
    last = max(bar["session"] for bar in panel["bars"])
    security = min(bar["security_id"] for bar in panel["bars"] if bar["session"] == last)
    session = (date.fromisoformat(panel["data_cutoff"][:10]) + timedelta(days=3)).isoformat()
    available = (date.fromisoformat(session) + timedelta(days=1)).isoformat() + "T03:00:00Z"
    value["bars"].append({"security_id": security, "session": session, "close": 987.654321,
                          "volume_fin": 123456789.0, "available_at": available})
    value["canary"] = {"token": CANARY, "security_id": security, "session": session, "close": 987.654321}
    return value, {"security_id": security, "session": session, "available_at": available}


def provision(root: Path, build: Path, protocol: dict, matrix: dict) -> dict:
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
    canary, canary_bar = canary_panel(panel)
    objects = {
        ("dataset", "b3-cvm-real"): panel,
        ("dataset", "b3-cvm-real-canary"): canary,
        ("universe", NAMES["universe"]): dict(protocol["universe"]),
        ("features", NAMES["features"]): protocol["features"],
        ("model", NAMES["model"]): protocol["model"],
        ("baseline", NAMES["baseline"]): protocol["baseline"],
        ("cost_model", NAMES["cost_model"]): protocol["cost_model"],
        ("readiness", NAMES["readiness"]): matrix,
        ("source", NAMES["source"]): source,
    }
    registry, hashes = [], {}
    for (kind, name), value in sorted(objects.items()):
        object_hash = store.put_operator_bytes(canonical(value))
        hashes[f"{kind}:{name}"] = object_hash
        registry.append({"kind": kind, "name": name, "version": "v1",
                         "revision_id": f"{kind}:{name}:integration-v1", "content_hash": object_hash})
    if hashes["dataset:b3-cvm-real"] != hashlib.sha256(panel_raw).hexdigest():
        raise SystemExit("dataset object hash differs from the builder panel sha256")
    family = protocol["model"]["hypothesis_family"]
    hypotheses = {h: {"hypothesis_family": family,
                      "purpose": "qualification probe on real B3/CVM data; not a scientific hypothesis"}
                  for h in HYPOTHESES}
    hypotheses.update({h: {"hypothesis_family": family,
                           "purpose": "LLM-only qualification probe: negative control of the same protocol on real "
                                      "B3/CVM data; not a scientific hypothesis"}
                       for h in LLM_HYPOTHESES})
    hypotheses[COLLECTION_HYPOTHESIS] = {"hypothesis_family": "stocks-ei-collection-only",
                                         "purpose": "External Intelligence collection monitoring; never a trial"}
    policy = {
        "schema_version": "StocksResearchAdmissionPolicyV1",
        "policy_id": POLICY_ID,
        "policy_version": protocol["policy"]["policy_version"],
        "owner": "STOCKS_OPERATOR",
        "requester_trust": "LOCAL_FILE_ONLY",
        "handlers": dict(KNOWN_HANDLERS),
        "hypotheses": hypotheses,
        "registry": registry,
        "limits": dict(protocol["policy"]["limits"]),
        "allowed_collectors": ["cvm-vlmo"],
    }
    raw_policy = json.dumps(policy, indent=1).encode("utf-8")
    (root / "policy.json").write_bytes(raw_policy)
    env = {"object_hashes": hashes, "policy_sha256": hashlib.sha256(raw_policy).hexdigest(),
           "policy": str(root / "policy.json"), "objects": str(root / "objects"),
           "data_cutoff": panel["data_cutoff"], "dataset_version": panel["dataset_version"],
           "panel_sha256": hashlib.sha256(panel_raw).hexdigest(), "panel_bytes": len(panel_raw),
           "canary": canary_bar, "canary_markers": [canary_bar["session"], canary_bar["available_at"]],
           "hypotheses": list(HYPOTHESES), "llm_hypotheses": list(LLM_HYPOTHESES), "timeout_seconds": policy["limits"]["timeout_seconds"]}
    (root / "REAL_ENV.json").write_text(json.dumps(env, indent=1), encoding="utf-8")
    return env


def main() -> int:
    root, build, protocol_path, matrix_path = (Path(a) for a in sys.argv[1:5])
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    print(json.dumps(provision(root, build, protocol, matrix), indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
