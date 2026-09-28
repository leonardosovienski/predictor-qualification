"""integration-crypto (IC-F004, decisão do dono 2026-09-27): registra no ecosystem-predictor a reemissão genuína dos
atestados de harness do cripto, no mesmo formato do precedente 09d2844/7c147a9.

- As entradas ALIGNED do cripto já vencidas passam a EXPIRED com reissue_required=true (evidência original intacta).
- Os dois atestados novos (harness oficial pipeline-power/2, árvore limpa, Core 3.2.1) são copiados byte a byte para
  docs/engineering_controls/<data>/ e entram como entradas ALIGNED com evidence_path + evidence_sha256.
Os campos das entradas novas saem dos próprios atestados (check_recorded_evidence do ecosystem confere).
Uso: python renew_harness_registry.py <checkout do ecosystem> <dir dos atestados> <data AAAAMMDD> <core_code_sha>
"""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

FILES = {"psr": "crypto-trials.harness_attestation.json", "spearman_ic": "crypto-trials.phase1_harness_attestation.json"}
SOURCES = {"psr": "trials.harness_attestation.json", "spearman_ic": "trials.phase1_harness_attestation.json"}
SCOPE = "Synthetic judge power controls only; no economic verdict, trading action or capital authorization"


def main() -> int:
    eco, src, day, core_sha = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3], sys.argv[4]
    registry_path = eco / "registries" / "harness_registry.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    now = datetime.now(UTC)
    expired = []
    for item in registry["harnesses"]:
        if item["repo"] == "cripto-predictor" and item["status"] == "ALIGNED":
            if datetime.fromisoformat(item["expires_at"].replace("Z", "+00:00")) > now:
                raise SystemExit(f"entrada ALIGNED ainda válida, não mexo: {item['expires_at']}")
            item["status"] = "EXPIRED"
            item["reissue_required"] = True
            item["basis"] = ("Official installed Crypto harness with fixed edge/noise seeds and canonical Core; expired "
                             "at the recorded boundary and requires genuine reissue; original evidence unchanged")
            expired.append(item["metric"])
    if sorted(expired) != sorted(FILES):
        raise SystemExit(f"esperava as duas entradas ALIGNED vencidas do cripto (psr, spearman_ic), achei {expired}")
    target = eco / "docs" / "engineering_controls" / day
    target.mkdir(parents=True, exist_ok=False)
    for metric in ("psr", "spearman_ic"):
        raw = (src / SOURCES[metric]).read_bytes()
        att = json.loads(raw)
        if att["metric"] != metric or att["core_version"] != registry["current_released_core_version"]:
            raise SystemExit(f"atestado inesperado para {metric}: {att}")
        (target / FILES[metric]).write_bytes(raw)
        registry["harnesses"].append({
            "repo": "cripto-predictor",
            "harness_version": att["schema_version"],
            "reported_core_version": att["core_version"],
            "core_code_sha": core_sha,
            "domain_code_version": att["code_version"],
            "executed_at": att["passed_at"],
            "expires_at": att["expires_at"],
            "status": "ALIGNED",
            "reissue_required": False,
            "metric": metric,
            "pipeline_fingerprint": att["pipeline_fingerprint"],
            "evidence_path": f"docs/engineering_controls/{day}/{FILES[metric]}",
            "evidence_sha256": hashlib.sha256(raw).hexdigest(),
            "scope": SCOPE,
            "basis": ("Genuine clean-tree reissue against Core 3.2.1 (cripto-predictor v1.2.0rc3 source, attestations "
                      "staged outside the repo; canonical domain attestation files untouched); fixed edge/noise "
                      "controls passed"),
        })
    registry["last_verified_at"] = now.date().isoformat()
    registry_path.write_text(json.dumps(registry, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"expired": expired, "added": [f"docs/engineering_controls/{day}/{f}" for f in FILES.values()]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
