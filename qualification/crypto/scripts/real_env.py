"""crypto: ambiente de pesquisa com o dataset REAL (Windows local; D-16 pendente para Linux).

Monta, com o GarimpoInvestimentos INSTALADO (ReferenceStore real, fronteira do operador):
  <root>/objects   objetos imutáveis: protocolo, dataset real in-sample, dataset real canário,
                   baseline, custo V3 congelado, evidência
  <root>/policy.json
  <root>/requests/*.json   pedidos do contrato
Os datasets reais entram com os MESMOS bytes do build_real_dataset.py (sha256 conferido contra
o MANIFEST.json antes de provisionar).

Uso: python real_env.py <root> <dir do dataset real (C:\\Cripto\\qualificacao\\data\\binance-um-btcusdt)>
Imprime JSON com os caminhos e hashes.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

from GarimpoInvestimentos.research_contract import canonical
from GarimpoInvestimentos.research_execution import ReferenceStore

CUTOFF = "2026-08-31T00:00:00Z"
HYPOTHESIS = "crypto:QUAL-SHADOW-REAL-001"
FAMILY = "crypto-qualification-fixed-shadow"


def request(request_id: str, dataset: str, **params) -> dict:
    parameters = {"symbol": "BTCUSDT", "horizon_days": 7, "max_observations": 100, "fee_bps": 10, "slippage_bps": 5}
    parameters.update(params)
    return {
        "schema_version": "crypto-research-request/1",
        "request_id": request_id,
        "request_type": "BACKTEST_EXISTING_HYPOTHESIS",
        "research_id": "crypto:RESEARCH-QUALIFICATION-REAL",
        "hypothesis_id": HYPOTHESIS,
        "references": {
            "protocol": {"name": "fixed-shadow", "version": "v1"},
            "dataset": {"name": dataset, "version": "v1"},
            "baseline": {"name": "flat", "version": "v1"},
            "cost_model": {"name": "v3-frozen", "version": "v1"},
            "evidence": {"name": "none", "version": "v1"},
        },
        "data_cutoff": CUTOFF,
        "parameters": parameters,
        "priority_hint": "NORMAL",
    }


def main() -> None:
    root, data = Path(sys.argv[1]), Path(sys.argv[2])
    manifest = json.loads((data / "MANIFEST.json").read_text(encoding="utf-8"))["objects"]
    store = ReferenceStore(root / "objects")
    registry = []
    small = {
        ("protocol", "fixed-shadow"): {
            "handler": "crypto.handlers.backtest_existing_hypothesis.v1", "minimum_sample": 20, "turnover_bps": 0,
            "hypothesis_family": FAMILY, "feature_version": "none-fixed-signal-v1", "model_version": "fixed-long-shadow-v1",
            "selection_path": {"family": FAMILY, "candidate_set": ["fixed-long-shadow-v1"],
                               "selection_metric": "predeclared", "selected_candidate": "fixed-long-shadow-v1"}},
        ("baseline", "flat"): {"baseline_id": "crypto:BASELINE-FLAT", "gross_return_bps": 0, "net_return_bps": 0},
        ("cost_model", "v3-frozen"): {"fee_bps": 10, "slippage_bps": 5},
        ("evidence", "none"): {"receipt_id": "crypto:EVIDENCE-NONE", "classification": "qualification"},
    }
    for (kind, name), value in small.items():
        registry.append({"kind": kind, "name": name, "version": "v1", "revision_id": f"{kind}:{name}:real-v1",
                         "content_hash": store.put_operator_bytes(canonical(value))})
    datasets = {"real-in-sample": "dataset-real-in-sample.json", "real-future-canary": "dataset-real-future-canary.json"}
    hashes = {}
    for name, filename in datasets.items():
        raw = (data / filename).read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        if digest != manifest[filename]["sha256"]:
            raise SystemExit(f"dataset {filename} diverge do MANIFEST")
        object_hash = store.put_operator_bytes(raw)
        assert object_hash == digest
        hashes[name] = digest
        registry.append({"kind": "dataset", "name": name, "version": "v1", "revision_id": f"dataset:{name}:v1",
                         "content_hash": object_hash})
    # Ablações temporais (FROZEN_PARAMETERS.negative_controls.temporal_ablation), derivadas
    # dos bytes reais: a) duas observações com a ordem trocada; b) uma linha disponível antes
    # de ser observada. As duas têm de falhar fechadas (TEMPORAL_INTEGRITY_VIOLATION).
    base = json.loads((data / datasets["real-in-sample"]).read_text(encoding="utf-8"))
    swapped = json.loads(json.dumps(base))
    swapped["rows"][10], swapped["rows"][11] = swapped["rows"][11], swapped["rows"][10]
    swapped["dataset_version"] += "-ablation-order"
    early = json.loads(json.dumps(base))
    early["rows"][10]["available_at"] = early["rows"][9]["observed_at"]
    early["dataset_version"] += "-ablation-availability"
    for name, value in (("real-ablation-order", swapped), ("real-ablation-availability", early)):
        object_hash = store.put_operator_bytes(canonical(value))
        hashes[name] = object_hash
        registry.append({"kind": "dataset", "name": name, "version": "v1", "revision_id": f"dataset:{name}:v1",
                         "content_hash": object_hash})
    policy = {
        "schema_version": "CryptoResearchAdmissionPolicyV2", "policy_id": "crypto-qualification-real",
        "policy_version": 1, "owner": "CRIPTO_OPERATOR", "requester_trust": "LOCAL_FILE_ONLY",
        "handlers": {"BACKTEST_EXISTING_HYPOTHESIS": "crypto.handlers.backtest_existing_hypothesis.v1"},
        "hypotheses": {HYPOTHESIS: {"hypothesis_family": FAMILY,
                                    "purpose": "qualification probe on real public data; not a scientific hypothesis"}},
        "registry": registry,
        "limits": {"max_pending_requests": 1000, "max_request_bytes": 16384, "max_parameter_bytes": 1024,
                   "max_concurrency": 1, "cpu_seconds": 120, "memory_mb": 512, "disk_mb": 256,
                   "timeout_seconds": 120, "max_retries": 2, "max_priority": "NORMAL"},
        "allowed_symbols": ["BTCUSDT"],
    }
    (root / "policy.json").write_text(json.dumps(policy, indent=1), encoding="utf-8")
    requests = root / "requests"
    requests.mkdir(exist_ok=True)
    written = {}
    vectors = {"e2e": request("crypto:REQ-REAL-E2E-001", "real-in-sample"),
               "canary": request("crypto:REQ-REAL-CANARY-001", "real-future-canary"),
               "ablation-order": request("crypto:REQ-REAL-ABLATION-ORDER-001", "real-ablation-order"),
               "ablation-availability": request("crypto:REQ-REAL-ABLATION-AVAIL-001", "real-ablation-availability")}
    for seed in range(100):
        vectors[f"placebo-{seed:03d}"] = request(f"crypto:REQ-REAL-PLACEBO-{seed:03d}", "real-in-sample", placebo_seed=seed)
    for name, value in vectors.items():
        path = requests / f"{name}.json"
        path.write_text(json.dumps(value, indent=1), encoding="utf-8")
        written[name] = str(path)
    print(json.dumps({"root": str(root), "policy": str(root / "policy.json"), "objects": str(root / "objects"),
                      "dataset_hashes": hashes, "requests": len(written)}, indent=1))


if __name__ == "__main__":
    main()
