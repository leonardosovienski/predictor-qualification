"""integration-crypto (C7.1 regra 4): cada final_wheels[*].sha256 confere com o asset da url, e as final_wheels
cobrem todo pacote do stack instalado no runtime (pip freeze dos venvs do run do Linux primário).

Baixa cada asset pela url (gh release download, sem token no log) para um diretório temporário fora do checkout.
Uso: python final_wheels_check.py <qualification/integration-crypto> <run do runtime> <out.json>
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

STACK = re.compile(r"^(cain-research|cripto-predictor|predictor-[a-z-]+) @ \S+#sha256=([0-9a-f]{64})$")
URL = re.compile(r"^https://github\.com/([^/]+/[^/]+)/releases/download/([^/]+)/([^/]+)$")


def main() -> int:
    m, run, out = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3])
    ledger = json.loads((m / "GATES.json").read_text(encoding="utf-8"))
    wheels = {w["name"]: w for w in ledger["final_wheels"]}
    env = m / "RAW_LOGS" / "runtime" / run / "env"
    installed: dict[str, set[str]] = {}
    # rc16 (D-32): no venv do CAIN as wheels do stack vêm do índice local .stack-wheels (pip freeze mostra name==version,
    # sem URL); a identidade é o sha256 que o fetch conferiu (env/stack_wheels_cain.sha256) e que o pip exigiu
    # (--require-hashes) para o mesmo nome+versão.
    fetched: dict[str, str] = {}
    for sums in sorted(env.glob("stack_wheels_*.sha256")):
        for line in sums.read_text(encoding="utf-8").splitlines():
            digest, _, asset = line.partition("  ")
            fetched[asset.strip()] = digest.strip()
    PINNED = re.compile(r"^(cain-research|cripto-predictor|predictor-[a-z-]+)==(\S+)$")
    for freeze in sorted(env.glob("pip_freeze_*.txt")):
        for line in freeze.read_text(encoding="utf-8").splitlines():
            hit = STACK.match(line.strip())
            if hit:
                installed.setdefault(hit.group(1), set()).add(hit.group(2))
                continue
            pin = PINNED.match(line.strip())
            if pin:
                asset = f"{pin.group(1).replace('-', '_')}-{pin.group(2)}-py3-none-any.whl"
                if asset in fetched:
                    installed.setdefault(pin.group(1), set()).add(fetched[asset])
    checks = []
    with tempfile.TemporaryDirectory() as tmp:
        for name, w in sorted(wheels.items()):
            repo, tag, asset = URL.match(w["url"]).groups()
            subprocess.run(["gh", "release", "download", tag, "-R", repo, "-p", asset, "-D", tmp], check=True,
                           capture_output=True)
            got = hashlib.sha256((Path(tmp) / asset).read_bytes()).hexdigest()
            checks.append({"check": f"{name}: sha256 do asset == final_wheels", "ok": got == w["sha256"],
                           "url": w["url"], "asset_sha256": got, "declared_sha256": w["sha256"]})
            checks.append({"check": f"{name}: instalado no runtime com o mesmo sha256",
                           "ok": installed.get(name) == {w["sha256"]}, "installed": sorted(installed.get(name, ()))})
    missing = sorted(set(installed) - set(wheels))
    checks.append({"check": "final_wheels cobrem todo pacote do stack instalado", "ok": not missing,
                   "installed_stack": sorted(installed), "missing": missing})
    doc = {"scenario": "final-wheels", "run": run, "passed": sum(c["ok"] for c in checks),
           "failed": sum(not c["ok"] for c in checks), "checks": checks}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"passed": doc["passed"], "failed": doc["failed"]}))
    return 0 if doc["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
