"""integration-crypto, LOCK_INTEGRITY / CORE_IDENTITY (C4): a mesma wheel em toda a cadeia de cada pacote do stack.

Para cada dependência entre repos do stack no runtime desta missão:
    pyproject (range/pin) ↔ tool.uv.sources (URL da release) ↔ uv.lock (URL + sha256) ↔ wheel da release
    (sha256 de runtime_targets.json, conferido no download) ↔ versão instalada (pip freeze do runtime) ↔ módulo em
    site-packages (cleanroom_final.log)
Lê os pyproject/uv.lock dos commits finais por `git show` (SHA completo) e os logs do run do Actions.
Uso: python core_identity.py <clones> <runtime_targets.json> <dir do artefato do run> <out.json>
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tomllib
from pathlib import Path


def show(repo: Path, commit: str, path: str) -> str:
    return subprocess.run(["git", "-C", str(repo), "show", f"{commit}:{path}"], capture_output=True, text=True,
                          check=True).stdout


def freeze(path: Path) -> dict[str, str]:
    out = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if "==" in line:
            name, version = line.split("==", 1)
            out[name.strip().lower()] = version.strip()
        elif " @ " in line:
            name, ref = line.split(" @ ", 1)
            m = re.search(r"-(\d[^-]*)-py3-none-any\.whl", ref)
            out[name.strip().lower()] = m.group(1) if m else ref.strip()
    return out


def main() -> int:
    repos, targets, run, out = Path(sys.argv[1]), json.loads(Path(sys.argv[2]).read_text()), Path(sys.argv[3]), Path(sys.argv[4])
    checks = []

    def check(name, ok, **detail):
        checks.append({"check": name, "ok": bool(ok), **detail})

    consumer = freeze(run / "env" / "pip_freeze_consumer.txt")
    cain_env = freeze(run / "env" / "pip_freeze_cain.txt")
    specs = [
        ("cain", "cain", targets["cain"]["commit"],
         {"predictor-research-protocol": targets["protocol"], "predictor-research-transport": targets["transport"]}),
        ("cripto-predictor", "cripto", targets["cripto"]["commit"], {}),
    ]
    for repo, _key, commit, expected in specs:
        pyproject = tomllib.loads(show(repos / repo, commit, "pyproject.toml"))
        lock = {p["name"]: p for p in tomllib.loads(show(repos / repo, commit, "uv.lock"))["package"]}
        sources = pyproject.get("tool", {}).get("uv", {}).get("sources", {})
        deps = pyproject["project"]["dependencies"]
        stack = [n for n in lock if n.startswith(("predictor-", "cain-research", "cripto-predictor"))
                 and lock[n].get("source", {}).get("url")]
        for name in stack:
            entry = lock[name]
            (wheel,) = entry["wheels"]
            src = sources.get(name, {}).get("url")
            spec = next((d for d in deps if re.split(r"[<>=!~ ;\[]", d, maxsplit=1)[0] == name), None)
            installed = (cain_env if repo == "cain" else consumer).get(name)
            ok = src == entry["source"]["url"] == wheel["url"] and installed == entry["version"]
            detail = {"repo": repo, "commit": commit, "package": name, "pyproject": spec, "uv_source": src,
                      "lock_url": wheel["url"], "lock_sha256": wheel["hash"], "lock_version": entry["version"],
                      "installed_version": installed}
            if name in expected:
                ok &= wheel["hash"] == "sha256:" + expected[name]["sha256"] and wheel["url"] == expected[name]["url"]
                detail["release_sha256"] = expected[name]["sha256"]
            check(f"{repo}: {name} same wheel in pyproject/uv.sources/uv.lock/install", ok, **detail)
    for key, env in (("cain", cain_env), ("cripto", consumer), ("transport", consumer), ("protocol", consumer)):
        name = {"cain": "cain-research", "cripto": "cripto-predictor", "transport": "predictor-research-transport",
                "protocol": "predictor-research-protocol"}[key]
        check(f"{name}: installed version == published final wheel", env.get(name) == targets[key]["version"],
              installed=env.get(name), final=targets[key]["version"], sha256=targets[key]["sha256"])
    env_log = (run / "env" / "runtime_env.log").read_text(encoding="utf-8")
    oks = re.findall(r"^(\S+\.whl): OK$", env_log, re.M)
    check("every final wheel downloaded by URL passed sha256sum -c in the runtime", len(oks) >= 4, verified=oks)
    cleanroom = (run / "cleanroom-final" / "cleanroom_final.log").read_text(encoding="utf-8")
    paths = re.findall(r"^(cripto|transport|cain) (\S+) (\S+)$", cleanroom, re.M)
    check("runtime modules load from site-packages (not a checkout)", paths and all("site-packages" in p[2] for p in paths),
          modules=paths)
    doc = {"schema": "integration-crypto/CORE_IDENTITY/1", "checks": checks,
           "passed": sum(c["ok"] for c in checks), "failed": sum(not c["ok"] for c in checks)}
    Path(out).write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({k: doc[k] for k in ("passed", "failed")}))
    for c in checks:
        if not c["ok"]:
            print("FAILED", json.dumps(c))
    return 0 if doc["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
