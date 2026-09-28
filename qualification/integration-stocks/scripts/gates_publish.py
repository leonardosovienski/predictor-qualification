"""Ledger: fases envelope-v2 .. publish-candidates (final_commits/final_wheels) e parciais, uma fase por vez."""
import json
import subprocess
import sys
from pathlib import Path

root = Path(sys.argv[1])
gpath = root / "qualification/integration-stocks/GATES.json"
targets = json.loads((root / "qualification/integration-stocks/runtime_targets.json").read_text(encoding="utf-8"))
ic = json.loads((root / "qualification/integration-crypto/QUALIFICATION_ATTESTATION.json").read_text(encoding="utf-8"))
ic_wheels = {w["name"]: w for w in ic["final_wheels"]}
attest = [sys.executable, str(root / "qualification/integration-stocks/scripts/attest.py"), "partial"]


def add_phase(name, update=None):
    g = json.loads(gpath.read_text(encoding="utf-8"))
    assert name not in g["phases_completed"]
    g["phases_completed"].append(name)
    if update:
        update(g)
    gpath.write_text(json.dumps(g, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    subprocess.run(attest + [name], check=True, cwd=root)


def finals(g):
    g["final_commits"] = [
        {"repo": "stocks-predictor", "commit_sha": targets["stocks"]["commit"]},
        {"repo": "cain", "commit_sha": targets["cain"]["commit"]},
        {"repo": "ecosystem-predictor", "commit_sha": targets["transport"]["commit"]},
        {"repo": "cripto-predictor", "commit_sha": targets["cripto"]["commit"]},
        {"repo": "core-predictor", "commit_sha": "5a0841509f091ea0aa95bde0d3d65e2a1a9e984d"},
        {"repo": "predictor-ops", "commit_sha": "9831b0d5e727972b1d85ff48be14ffa58677898b"},
    ]
    wheels = [
        {"name": "stocks-predictor", "version": targets["stocks"]["version"], "url": targets["stocks"]["url"],
         "sha256": targets["stocks"]["sha256"]},
        {"name": "cain-research", "version": targets["cain"]["version"], "url": targets["cain"]["url"],
         "sha256": targets["cain"]["sha256"]},
        {"name": "predictor-research-transport", "version": targets["transport"]["version"],
         "url": targets["transport"]["url"], "sha256": targets["transport"]["sha256"]},
    ]
    for name in ("predictor-research-protocol", "predictor-research-snapshot", "predictor-research-bundle",
                 "cripto-predictor", "predictor-core", "predictor-ops"):
        w = ic_wheels[name]
        wheels.append({"name": name, "version": w["version"], "url": w["url"], "sha256": w["sha256"]})
    g["final_wheels"] = wheels


for phase, fn in (("envelope-v2", None), ("domain-adapter", None), ("cain-wiring-decision-policy", None),
                  ("publish-candidates", finals)):
    add_phase(phase, fn)
print("ok")
