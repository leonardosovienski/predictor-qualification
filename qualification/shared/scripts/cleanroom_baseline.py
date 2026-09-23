"""SHARED-002: cleanroom-baseline (C5) de um repo do stack, no Linux do GitHub Actions.

Diagnóstico: registra o que quebra, não conserta. Lê o plano congelado
(qualification/shared/SHARED-002/CLEANROOM_PLAN.json) e, para o repo pedido:

  1. clona o repo no SHA do baseline (clone completo) e confere HEAD/limpeza;
  2. `uv lock --check`; exporta o lock (terceiros + wheels do stack por URL, com hash);
  3. baixa as wheels publicadas do repo e confere o sha256 do plano;
  4. para cada variante (`published` = runtime suportado; `head_build` = diagnóstico com
     wheel construída do commit), cria um venv novo fora do checkout e instala só pelo
     lock exportado (--require-hashes --no-deps) + as wheels próprias (--no-deps);
  5. `uv pip check`, identidade (versão, direct_url, caminho do módulo), `--help` de cada
     console script das distribuições próprias, carga dos entry points `predictor.plugins`;
  6. roda a suíte do commit numa árvore sparse (sem os diretórios de pacote), com um
     guard que registra a origem de todo módulo do stack importado;
  7. compara, arquivo a arquivo, a wheel publicada com a construída do commit.

Sem segredos: nenhum token é lido; clones e downloads são públicos e anônimos.
Uso: python cleanroom_baseline.py <plan.json> <repo> <out_dir>
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import time
import urllib.request
import zipfile
from pathlib import Path
from xml.etree import ElementTree

OWNER_URL = "https://github.com/leonardosovienski"
HERE = Path(__file__).resolve().parent


class Log:
    def __init__(self, out: Path) -> None:
        self.dir = out / "logs"
        self.dir.mkdir(parents=True, exist_ok=True)

    def run(self, name: str, args: list[str], cwd: Path | None = None, env: dict | None = None,
            timeout: int | None = None) -> dict:
        """Executa e grava stdout+stderr brutos em logs/<name>.log; devolve exit e duração."""
        path = self.dir / f"{name}.log"
        start = time.monotonic()
        with path.open("w", encoding="utf-8", errors="replace") as fh:
            fh.write(f"$ (cwd={cwd}) {' '.join(args)}\n")
            fh.flush()
            try:
                proc = subprocess.run(args, cwd=cwd, env=env, stdout=fh, stderr=subprocess.STDOUT,
                                      timeout=timeout, check=False)
                code = proc.returncode
            except subprocess.TimeoutExpired:
                code = "TIMEOUT"
            except OSError as exc:
                fh.write(f"\n[oserror] {exc}\n")
                code = "OSERROR"
            fh.write(f"\n[exit {code}]\n")
        return {"exit": code, "seconds": round(time.monotonic() - start, 1), "log": f"logs/{name}.log"}

    def text(self, name: str) -> str:
        return (self.dir / f"{name}.log").read_text(encoding="utf-8", errors="replace")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def wheel_digest(path: Path) -> dict[str, str]:
    """sha256 de cada arquivo da wheel, sem RECORD (que muda com qualquer byte)."""
    with zipfile.ZipFile(path) as zf:
        return {i.filename: hashlib.sha256(zf.read(i)).hexdigest() for i in zf.infolist()
                if not i.filename.endswith(".dist-info/RECORD") and not i.is_dir()}


def dist_key(filename: str) -> str:
    return filename.split("-")[0].replace("_", "-").lower()


def junit_counts(path: Path) -> dict | None:
    if not path.exists():
        return None
    root = ElementTree.parse(path).getroot()
    suites = [root] if root.tag == "testsuite" else list(root.iter("testsuite"))
    totals = {"tests": 0, "failures": 0, "errors": 0, "skipped": 0}
    for s in suites:
        for k in totals:
            totals[k] += int(s.get(k, 0))
    totals["passed"] = totals["tests"] - totals["failures"] - totals["errors"] - totals["skipped"]
    failed = [f"{c.get('classname')}::{c.get('name')}" for c in root.iter("testcase")
              if c.find("failure") is not None or c.find("error") is not None]
    totals["failed_ids"] = failed
    return totals


INTROSPECT = r"""
import importlib, importlib.metadata as md, json, sys, sysconfig
own, stack = json.loads(sys.argv[1]), json.loads(sys.argv[2])
site = sysconfig.get_paths()["purelib"]
out = {"site_packages": site, "dists": {}, "modules": {}, "console_scripts": [], "plugins": []}
for d in md.distributions():
    name = d.metadata["Name"].lower().replace("_", "-")
    if name in own or name in ("predictor-core", "predictor-ops", "predictor-research-protocol",
                               "predictor-research-snapshot", "predictor-research-bundle",
                               "cain-research", "ecosystem-predictor", "crypto-research-export",
                               "cripto-predictor", "brasileirao-predictor", "stocks-predictor"):
        direct = d.read_text("direct_url.json")
        out["dists"][name] = {"version": d.version, "direct_url": json.loads(direct) if direct else None,
                              "requires": d.requires or []}
        if name in own:
            for ep in d.entry_points:
                if ep.group == "console_scripts":
                    out["console_scripts"].append({"dist": name, "name": ep.name, "value": ep.value})
                elif ep.group == "predictor.plugins":
                    try:
                        ep.load()
                        out["plugins"].append({"dist": name, "name": ep.name, "value": ep.value, "load": "OK"})
                    except Exception as exc:
                        out["plugins"].append({"dist": name, "name": ep.name, "value": ep.value,
                                               "load": f"{type(exc).__name__}: {exc}"[:500]})
for mod in stack:
    try:
        m = importlib.import_module(mod)
        f = getattr(m, "__file__", None)
        out["modules"][mod] = {"file": f, "in_site_packages": bool(f) and f.startswith(site)}
    except ModuleNotFoundError as exc:
        if exc.name == mod:
            continue
        out["modules"][mod] = {"error": f"{type(exc).__name__}: {exc}"[:500]}
    except Exception as exc:
        out["modules"][mod] = {"error": f"{type(exc).__name__}: {exc}"[:500]}
print(json.dumps(out))
"""


def main() -> None:
    plan_path, repo_name, out_arg = sys.argv[1], sys.argv[2], sys.argv[3]
    plan = json.loads(Path(plan_path).read_text(encoding="utf-8"))
    spec = next(r for r in plan["repos"] if r["repo"] == repo_name)
    out = Path(out_arg).resolve()
    out.mkdir(parents=True, exist_ok=True)
    work = Path(os.environ.get("RUNNER_TEMP", "/tmp")) / "cleanroom" / repo_name
    shutil.rmtree(work, ignore_errors=True)
    work.mkdir(parents=True)
    log = Log(out)
    uv = os.environ["CLEANROOM_UV"]
    py_version = plan["environment"]["python"]
    base_env = {k: v for k, v in os.environ.items()
                if not k.startswith(("GITHUB_TOKEN", "ACTIONS_", "INPUT_")) and "TOKEN" not in k}
    base_env.update({"UV_NO_CONFIG": "1", "UV_PYTHON_PREFERENCE": "only-managed", "PIP_NO_INPUT": "1"})
    base_env.pop("PYTHONPATH", None)
    facts: dict = {"repo": repo_name, "sha": spec["sha"], "plan_id": plan["plan_id"],
                   "plan_sha256": sha256_file(Path(plan_path)), "steps": {}}

    # Ambiente
    os_release = dict(line.split("=", 1) for line in Path("/etc/os-release").read_text().splitlines() if "=" in line)
    facts["environment"] = {
        "os": os_release.get("PRETTY_NAME", "").strip('"'), "kernel": platform.release(),
        "machine": platform.machine(), "runner_image": os.environ.get("ImageOS", "") + " " + os.environ.get("ImageVersion", ""),
        "uv": subprocess.run([uv, "--version"], capture_output=True, text=True).stdout.strip(),
        "python": subprocess.run([uv, "python", "find", py_version], capture_output=True, text=True).stdout.strip(),
    }
    python = facts["environment"]["python"]
    facts["environment"]["python_version"] = subprocess.run(
        [python, "-c", "import sys; print(sys.version.split()[0])"], capture_output=True, text=True).stdout.strip()

    # 1. Clone completo no SHA + árvore de testes sparse
    full, tree = work / "full", work / "tree"
    url = f"{OWNER_URL}/{repo_name}.git"
    steps = facts["steps"]
    steps["clone"] = log.run("clone", ["git", "clone", "--quiet", "--no-checkout", url, str(full)], env=base_env)
    steps["checkout"] = log.run("checkout", ["git", "-C", str(full), "-c", "advice.detachedHead=false",
                                             "checkout", "--quiet", spec["sha"]], env=base_env)
    head = subprocess.run(["git", "-C", str(full), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "-C", str(full), "status", "--porcelain"], capture_output=True, text=True).stdout
    facts["head_matches_plan"] = head == spec["sha"]
    facts["clone_clean"] = dirty == ""
    if not facts["head_matches_plan"]:
        facts["aborted"] = f"HEAD {head} != {spec['sha']}"
        (out / "cleanroom_facts.json").write_text(json.dumps(facts, indent=2), encoding="utf-8")
        return
    log.run("tree_clone", ["git", "clone", "--quiet", "--no-checkout", str(full), str(tree)], env=base_env)
    patterns = ["/*"] + [f"!/{p}/" for p in spec["strip_paths"]]
    log.run("tree_sparse", ["git", "-C", str(tree), "sparse-checkout", "set", "--no-cone", *patterns], env=base_env)
    steps["tree_checkout"] = log.run("tree_checkout", ["git", "-C", str(tree), "-c", "advice.detachedHead=false",
                                                       "checkout", "--quiet", spec["sha"]], env=base_env)
    facts["tree_strip_paths_absent"] = {p: not (tree / p).exists() for p in spec["strip_paths"]}

    # 2. Lock
    steps["uv_lock_check"] = log.run("uv_lock_check", [uv, "lock", "--check", "--python", python], cwd=full, env=base_env)
    req = work / "lock-requirements.txt"
    steps["uv_export"] = log.run("uv_export", [uv, "export", "--frozen", "--no-emit-project", "--format",
                                               "requirements-txt", *spec["export_args"], "--output-file", str(req)],
                                 cwd=full, env=base_env)
    kept, dropped = [], []
    if req.exists():
        # Linhas de caminho local (pacotes do próprio repo por path) não são wheels publicadas.
        logical, buf = [], ""
        for line in req.read_text(encoding="utf-8").splitlines():
            buf += line.rstrip("\\").rstrip() + " " if line.endswith("\\") else line
            if not line.endswith("\\"):
                logical.append(buf.strip())
                buf = ""
        for entry in logical:
            if not entry or entry.startswith("#"):
                continue
            (dropped if entry.startswith(("-e", ".", "/", "file:")) else kept).append(entry)
        (work / "lock-requirements.filtered.txt").write_text("\n".join(kept) + "\n", encoding="utf-8")
        shutil.copy(req, out / "lock-requirements.txt")
    facts["lock_export"] = {"requirements": len(kept), "dropped_local_entries": dropped,
                            "stack_entries": [k.split(" ")[0] for k in kept if "github.com/leonardosovienski" in k]}

    # 3. Wheels publicadas
    published_dir = work / "published"
    published_dir.mkdir()
    downloads = []
    for w in spec["published_wheels"]:
        dest = published_dir / w["url"].rsplit("/", 1)[1]
        try:
            urllib.request.urlretrieve(w["url"], dest)
            got = sha256_file(dest)
            downloads.append({"name": w["name"], "version": w["version"], "url": w["url"],
                              "expected_sha256": w["sha256"], "sha256": got, "match": got == w["sha256"]})
        except Exception as exc:
            downloads.append({"name": w["name"], "url": w["url"], "error": f"{type(exc).__name__}: {exc}"})
    facts["published_download"] = downloads

    # Wheels do commit (diagnóstico)
    head_dir = work / "head_build"
    head_dir.mkdir()
    builds = []
    for b in spec["head_build"]:
        tag = b["dir"].strip("./").replace("/", "_") or "root"
        r = log.run(f"head_build_{tag}", [uv, "build", "--wheel", "--python", python, "--out-dir", str(head_dir), b["dir"]],
                    cwd=full, env=base_env)
        builds.append({"dir": b["dir"], **r})
    facts["head_build"] = {"builds": builds, "wheels": {p.name: sha256_file(p) for p in sorted(head_dir.glob("*.whl"))}}

    # 7. Comparação publicada × commit
    drift = []
    head_wheels = {dist_key(p.name): p for p in head_dir.glob("*.whl")}
    for p in sorted(published_dir.glob("*.whl")):
        h = head_wheels.get(dist_key(p.name))
        if h is None:
            drift.append({"dist": dist_key(p.name), "published": p.name, "head_build": None})
            continue
        a, b = wheel_digest(p), wheel_digest(h)
        norm = lambda d: {k.split("/", 1)[1] if ".dist-info/" in k else k: v for k, v in d.items()}
        na, nb = norm(a), norm(b)
        drift.append({
            "dist": dist_key(p.name), "published": p.name, "head_build": h.name,
            "identical_files": sum(1 for k in na if nb.get(k) == na[k]),
            "different_files": sorted(k for k in na if k in nb and nb[k] != na[k]),
            "only_published": sorted(k for k in na if k not in nb),
            "only_head_build": sorted(k for k in nb if k not in na),
        })
    facts["published_vs_head_build"] = drift

    # 4-6. Variantes
    facts["variants"] = {}
    stack_modules = plan["stack_modules"]
    for variant, wheel_dir in (("published", published_dir), ("head_build", head_dir)):
        v: dict = {}
        facts["variants"][variant] = v
        venv = work / f"venv-{variant}"
        v["venv"] = log.run(f"{variant}_venv", [uv, "venv", "--python", python, str(venv)], env=base_env)
        vpy = venv / "bin" / "python"
        if req.exists():
            v["install_lock"] = log.run(f"{variant}_install_lock",
                                        [uv, "pip", "install", "--python", str(vpy), "--require-hashes", "--no-deps",
                                         "-r", str(work / "lock-requirements.filtered.txt")], env=base_env)
        own = sorted(wheel_dir.glob("*.whl"))
        v["own_wheels"] = {p.name: sha256_file(p) for p in own}
        if own:
            v["install_own"] = log.run(f"{variant}_install_own",
                                       [uv, "pip", "install", "--python", str(vpy), "--no-deps", *map(str, own)],
                                       env=base_env)
        v["pip_check"] = log.run(f"{variant}_pip_check", [uv, "pip", "check", "--python", str(vpy)], env=base_env)
        v["pip_check_output"] = log.text(f"{variant}_pip_check").splitlines()[1:-2][:60]
        log.run(f"{variant}_pip_freeze", [uv, "pip", "freeze", "--python", str(vpy)], env=base_env)

        empty = work / f"cwd-{variant}"
        empty.mkdir()
        venv_env = dict(base_env, VIRTUAL_ENV=str(venv), PATH=f"{venv / 'bin'}:{base_env['PATH']}")
        intro = subprocess.run([str(vpy), "-I", "-c", INTROSPECT, json.dumps(spec["own_dists"]), json.dumps(stack_modules)],
                               cwd=empty, env=venv_env, capture_output=True, text=True, timeout=300)
        (log.dir / f"{variant}_introspect.log").write_text(intro.stdout + "\n[stderr]\n" + intro.stderr, encoding="utf-8")
        try:
            v["introspect"] = json.loads(intro.stdout)
        except json.JSONDecodeError:
            v["introspect"] = {"error": intro.stderr[-2000:]}

        v["console_scripts"] = []
        for cs in v["introspect"].get("console_scripts", []):
            r = log.run(f"{variant}_help_{cs['name']}", [str(venv / "bin" / cs["name"]), "--help"], cwd=empty,
                        env=venv_env, timeout=plan["limits"]["entrypoint_help_timeout_s"])
            v["console_scripts"].append({**cs, **r})

        for i, cmd in enumerate(spec["pre_test"]):
            argv = [str(vpy) if cmd[0] == "python" else cmd[0], *cmd[1:]]
            v[f"pre_test_{i}"] = log.run(f"{variant}_pre_test_{i}", argv, cwd=tree, env=venv_env)

        guard_out = work / f"guard-{variant}.json"
        junit = out / f"junit-{variant}.xml"
        test_env = dict(venv_env, PYTHONPATH=str(HERE / "cleanroom_guard"), CLEANROOM_GUARD_OUT=str(guard_out),
                        CLEANROOM_GUARD_MODULES=",".join(stack_modules), CLEANROOM_GUARD_SITE=v["introspect"].get("site_packages", ""))
        v["pytest"] = log.run(f"{variant}_pytest",
                              [str(vpy), "-m", "pytest", *spec["pytest_args"], "-p", "cleanroom_guard",
                               "-p", "no:cacheprovider", "-o", "pythonpath=", f"--junitxml={junit}", "-rfE"],
                              cwd=tree, env=test_env, timeout=plan["limits"]["pytest_timeout_s"])
        v["pytest_counts"] = junit_counts(junit)
        v["pytest_summary_line"] = next((line for line in reversed(log.text(f"{variant}_pytest").splitlines())
                                         if line.startswith("=") and (" in " in line)), None)
        v["guard"] = json.loads(guard_out.read_text()) if guard_out.exists() else None
        # Limpa o que a suíte gerou na árvore para a próxima variante (a árvore volta ao commit).
        subprocess.run(["git", "-C", str(tree), "checkout", "--quiet", "--", "."], check=False)
        subprocess.run(["git", "-C", str(tree), "clean", "-fdxq"], check=False)

    (out / "cleanroom_facts.json").write_text(json.dumps(facts, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"repo": repo_name, "published": facts["variants"]["published"].get("pytest_counts"),
                      "head_build": facts["variants"]["head_build"].get("pytest_counts")}, default=str)[:2000])


if __name__ == "__main__":
    main()
