"""integration-stocks, ciclo 4: fase publish-candidates-c4 no GATES.json (final_commits e final_wheels).

Mesma regra de scripts/gates_publish.py → finals() do ciclo 1: stocks, cain e transporte de runtime_targets.json (ciclo
4: cain 0.4.13rc13, transporte 0.1.0rc6); protocolo, snapshot, bundle, cripto, Core e Ops das final_wheels da
attestation QUALIFIED da integration-crypto (os mesmos pacotes que o runtime instala). Não escreve parcial: a do
ciclo 4 é a da attestation (como na integration-crypto). Idempotente.
Uso: python cycle4_publish.py <raiz do predictor-qualification>
"""

import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
gpath = root / "qualification/integration-stocks/GATES.json"
targets = json.loads((root / "qualification/integration-stocks/runtime_targets.json").read_text(encoding="utf-8"))
ic = json.loads((root / "qualification/integration-crypto/QUALIFICATION_ATTESTATION.json").read_text(encoding="utf-8"))
if ic["result"] != "QUALIFIED":
    raise SystemExit("integration-crypto não está QUALIFIED")
ic_wheels = {w["name"]: w for w in ic["final_wheels"]}
g = json.loads(gpath.read_text(encoding="utf-8"))
assert g.get("cycle", {}).get("number") == 4
g["final_commits"] = [
    {"repo": "stocks-predictor", "commit_sha": targets["stocks"]["commit"]},
    {"repo": "cain", "commit_sha": targets["cain"]["commit"]},
    {"repo": "ecosystem-predictor", "commit_sha": targets["transport"]["commit"]},
    {"repo": "cripto-predictor", "commit_sha": targets["cripto"]["commit"]},
    {"repo": "core-predictor", "commit_sha": "5a0841509f091ea0aa95bde0d3d65e2a1a9e984d"},
    {"repo": "predictor-ops", "commit_sha": "9831b0d5e727972b1d85ff48be14ffa58677898b"},
]
wheels = [{"name": "stocks-predictor", "version": targets["stocks"]["version"], "url": targets["stocks"]["url"],
           "sha256": targets["stocks"]["sha256"]},
          {"name": "cain-research", "version": targets["cain"]["version"], "url": targets["cain"]["url"],
           "sha256": targets["cain"]["sha256"]},
          {"name": "predictor-research-transport", "version": targets["transport"]["version"],
           "url": targets["transport"]["url"], "sha256": targets["transport"]["sha256"]}]
for name in ("predictor-research-protocol", "predictor-research-snapshot", "predictor-research-bundle",
             "cripto-predictor", "predictor-core", "predictor-ops"):
    w = ic_wheels[name]
    wheels.append({"name": name, "version": w["version"], "url": w["url"], "sha256": w["sha256"]})
g["final_wheels"] = wheels
if "publish-candidates-c4" not in g["phases_completed"]:
    g["phases_completed"].append("publish-candidates-c4")
gpath.write_text(json.dumps(g, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps({"final_commits": {c["repo"]: c["commit_sha"][:7] for c in g["final_commits"]},
                  "final_wheels": {w["name"]: w["version"] for w in wheels}}))
