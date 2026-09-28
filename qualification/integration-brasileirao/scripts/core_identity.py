"""integration-brasileirao, LOCK_INTEGRITY / CORE_IDENTITY (C4): a mesma wheel em toda a cadeia de cada pacote do stack.

Adaptado de qualification/integration-stocks/scripts/core_identity.py (mesma lógica; domínio brasileirao; o run é o do
runtime suportado local no PC 2, RAW_LOGS/runtime/<run>/). Para cada dependência entre repos do stack no runtime:
    pyproject (range/pin) ↔ tool.uv.sources (URL da release) ↔ uv.lock (URL + sha256) ↔ wheel da release
    (sha256 de runtime_targets.json, conferido no download) ↔ versão instalada (pip freeze do runtime) ↔ módulo em
    site-packages (cleanroom_final.log)
Core e Ops: a wheel do uv.lock do Brasileirão no commit final é a mesma da Etapa A (predictor-core 3.2.1 e
predictor-ops 4.2.2rc1, prefixos de sha256 congelados no runtime_targets.json → core_ops).
Lê os pyproject/uv.lock dos commits finais por `git show` (SHA completo).
Uso: python core_identity.py <clones> <runtime_targets.json> <RAW_LOGS/runtime/<run>> <out.json>
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tomllib
from pathlib import Path

FROZEN_STACK = {"predictor-core": ("3.2.1", "10ef42f3"), "predictor-ops": ("4.2.2rc1", "0be70bfb")}


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
    repos, targets = Path(sys.argv[1]), json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    run, out = Path(sys.argv[3]), Path(sys.argv[4])
    checks = []

    def check(name, ok, **detail):
        checks.append({"check": name, "ok": bool(ok), **detail})

    consumer = freeze(run / "pip_freeze_consumer.txt")
    cain_env = freeze(run / "pip_freeze_cain.txt")
    specs = [
        ("cain", targets["cain"]["commit"],
         {"predictor-research-protocol": targets["protocol"], "predictor-research-transport": targets["transport"]}),
        ("brasileirao-predictor", targets["brasileirao"]["commit"], {}),
    ]
    for repo, commit, expected in specs:
        pyproject = tomllib.loads(show(repos / repo, commit, "pyproject.toml"))
        lock = {p["name"]: p for p in tomllib.loads(show(repos / repo, commit, "uv.lock"))["package"]}
        sources = pyproject.get("tool", {}).get("uv", {}).get("sources", {})
        deps = pyproject["project"]["dependencies"]
        stack = [n for n in lock if n.startswith(("predictor-", "cain-research", "brasileirao-predictor"))
                 and lock[n].get("source", {}).get("url")]
        check(f"{repo}: stack packages found in uv.lock", bool(stack), stack=stack)
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
            if name in FROZEN_STACK:
                version, prefix = FROZEN_STACK[name]
                ok &= entry["version"] == version and wheel["hash"].startswith("sha256:" + prefix)
                detail["frozen"] = {"version": version, "sha256_prefix": prefix}
            check(f"{repo}: {name} same wheel in pyproject/uv.sources/uv.lock/install", ok, **detail)
    for key, env in (("cain", cain_env), ("brasileirao", consumer), ("transport", consumer), ("protocol", consumer)):
        name = {"cain": "cain-research", "brasileirao": "brasileirao-predictor",
                "transport": "predictor-research-transport", "protocol": "predictor-research-protocol"}[key]
        check(f"{name}: installed version == published final wheel", env.get(name) == targets[key]["version"],
              installed=env.get(name), final=targets[key]["version"], sha256=targets[key]["sha256"])
    check("transport in the CAIN venv == transport in the consumer venv (one transport in the stack)",
          cain_env.get("predictor-research-transport") == consumer.get("predictor-research-transport")
          == targets["transport"]["version"], cain=cain_env.get("predictor-research-transport"),
          consumer=consumer.get("predictor-research-transport"))
    check("no domain package in the CAIN venv", not any(n in cain_env for n in (
        "brasileirao-predictor", "stocks-predictor", "cripto-predictor")), cain_packages=sorted(cain_env))
    env_log = (run / "runtime_env.log").read_text(encoding="utf-8")
    oks = sorted({Path(p).name for p in re.findall(r"^(\S+\.whl): OK$", env_log, re.M)})
    wanted = sorted(Path(targets[k]["url"]).name for k in ("cain", "brasileirao", "transport", "protocol"))
    check("every final wheel downloaded by URL passed sha256sum -c in the runtime", set(wanted) <= set(oks),
          verified=oks, wanted=wanted)
    cleanroom = (run / "cleanroom-final" / "cleanroom_final.log").read_text(encoding="utf-8")
    modules = {}
    for line in cleanroom.splitlines():
        m = re.match(r"^(brasileirao|adapter|transport|cain) ", line)
        if m:
            modules.setdefault(m.group(1), []).extend(t for t in line.split() if t.endswith(".py"))
    check("runtime modules load from site-packages (not a checkout)",
          set(modules) == {"brasileirao", "adapter", "transport", "cain"}
          and all(paths and all("site-packages" in p for p in paths) for paths in modules.values()),
          modules={k: len(v) for k, v in modules.items()})
    doc = {"schema": "integration-brasileirao/CORE_IDENTITY/1", "checks": checks,
           "passed": sum(c["ok"] for c in checks), "failed": sum(not c["ok"] for c in checks)}
    out.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({k: doc[k] for k in ("passed", "failed")}))
    for c in checks:
        if not c["ok"]:
            print("FAILED", json.dumps(c))
    return 0 if doc["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
