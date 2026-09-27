"""integration-crypto: ambiente de operador do domínio (objetos de referência + policy de admission).

É a fronteira do operador do cripto (não do CAIN): igual a qualification/crypto/scripts/real_env.py da Etapa A,
com os valores congelados em FROZEN_PARAMETERS.json → operator_env (três hipóteses de qualificação da família
fixed-shadow no lugar de uma). Roda com o GarimpoInvestimentos INSTALADO (ReferenceStore real). Os datasets reais
entram com os MESMOS bytes do build_real_dataset.py (sha256 conferido contra o MANIFEST.json antes de provisionar).
Não cria pedidos: na Etapa B os pedidos vêm das tasks V2 do CAIN.

Uso: python operator_env.py <root> <dir do dataset real (com MANIFEST.json)>
Imprime JSON com os caminhos e hashes.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

from GarimpoInvestimentos.research_contract import canonical
from GarimpoInvestimentos.research_execution import ReferenceStore

HYPOTHESES = ("crypto:QUAL-SHADOW-REAL-001", "crypto:QUAL-SHADOW-REAL-002", "crypto:QUAL-SHADOW-REAL-003")
FAMILY = "crypto-qualification-fixed-shadow"
DATASETS = {"real-in-sample": "dataset-real-in-sample.json", "real-future-canary": "dataset-real-future-canary.json"}


def main() -> None:
    root, data = Path(sys.argv[1]), Path(sys.argv[2])
    manifest = json.loads((data / "MANIFEST.json").read_text(encoding="utf-8"))["objects"]
    store = ReferenceStore(root / "objects")
    registry = []
    small = {
        ("protocol", "fixed-shadow"): {
            "handler": "crypto.handlers.backtest_existing_hypothesis.v1", "minimum_sample": 20, "turnover_bps": 0,
            "hypothesis_family": FAMILY, "feature_version": "none-fixed-signal-v1",
            "model_version": "fixed-long-shadow-v1",
            "selection_path": {"family": FAMILY, "candidate_set": ["fixed-long-shadow-v1"],
                               "selection_metric": "predeclared", "selected_candidate": "fixed-long-shadow-v1"}},
        ("baseline", "flat"): {"baseline_id": "crypto:BASELINE-FLAT", "gross_return_bps": 0, "net_return_bps": 0},
        ("cost_model", "v3-frozen"): {"fee_bps": 10, "slippage_bps": 5},
        ("evidence", "none"): {"receipt_id": "crypto:EVIDENCE-NONE", "classification": "qualification"},
    }
    for (kind, name), value in small.items():
        registry.append({"kind": kind, "name": name, "version": "v1", "revision_id": f"{kind}:{name}:real-v1",
                         "content_hash": store.put_operator_bytes(canonical(value))})
    hashes = {}
    for name, filename in DATASETS.items():
        raw = (data / filename).read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        if digest != manifest[filename]["sha256"]:
            raise SystemExit(f"dataset {filename} diverge do MANIFEST")
        object_hash = store.put_operator_bytes(raw)
        assert object_hash == digest
        hashes[name] = digest
        registry.append({"kind": "dataset", "name": name, "version": "v1", "revision_id": f"dataset:{name}:v1",
                         "content_hash": object_hash})
    policy = {
        "schema_version": "CryptoResearchAdmissionPolicyV2", "policy_id": "crypto-integration-qualification",
        "policy_version": 1, "owner": "CRIPTO_OPERATOR", "requester_trust": "LOCAL_FILE_ONLY",
        "handlers": {"BACKTEST_EXISTING_HYPOTHESIS": "crypto.handlers.backtest_existing_hypothesis.v1"},
        "hypotheses": {h: {"hypothesis_family": FAMILY,
                           "purpose": "qualification probe on real public data; not a scientific hypothesis"}
                       for h in HYPOTHESES},
        "registry": registry,
        "limits": {"max_pending_requests": 1000, "max_request_bytes": 16384, "max_parameter_bytes": 1024,
                   "max_concurrency": 1, "cpu_seconds": 120, "memory_mb": 512, "disk_mb": 256,
                   "timeout_seconds": 120, "max_retries": 2, "max_priority": "NORMAL"},
        "allowed_symbols": ["BTCUSDT"],
    }
    raw_policy = json.dumps(policy, indent=1).encode("utf-8")
    (root / "policy.json").write_bytes(raw_policy)
    print(json.dumps({"root": str(root), "policy": str(root / "policy.json"),
                      "policy_sha256": hashlib.sha256(raw_policy).hexdigest(), "objects": str(root / "objects"),
                      "dataset_hashes": hashes, "hypotheses": list(HYPOTHESES)}, indent=1))


if __name__ == "__main__":
    main()
