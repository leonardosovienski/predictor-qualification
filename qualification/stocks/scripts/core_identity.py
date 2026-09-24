"""C4 (LOCK_INTEGRITY / CORE_IDENTITY): cadeia de identidade dos pacotes do stack num ambiente.

Roda DENTRO do interpretador do ambiente sob teste. Para cada pacote do stack instalado:
versão (metadata), direct_url.json (URL + hash da wheel quando o instalador registra),
INSTALLER, sha256 do RECORD, caminho do módulo importado em runtime e se ele está no
site-packages desse ambiente (não num checkout, vendor/ ou PYTHONPATH).

Opcional: --lock <uv.lock> --pyproject <pyproject.toml> cruza range ↔ tool.uv.sources ↔ lock.
Saída: JSON em stdout.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import sys
import sysconfig
import tomllib
from importlib.metadata import PackageNotFoundError, distribution
from pathlib import Path

STACK = {
    "predictor-core": "predictor_core",
    "predictor-ops": "predictor_ops",
    "stocks-predictor": "stocks_predictor",
    "predictor-research-protocol": "research_protocol",
    "predictor-research-snapshot": "research_snapshot",
    "predictor-research-bundle": "research_bundle",
    "cain-research": "cain",
    "ecosystem-predictor": "ecosystem",
    
}


def installed(name: str, module: str) -> dict | None:
    try:
        dist = distribution(name)
    except PackageNotFoundError:
        return None
    files = {f.name: f for f in (dist.files or [])}
    direct = None
    if "direct_url.json" in files:
        direct = json.loads(Path(str(dist.locate_file(files["direct_url.json"]))).read_text(encoding="utf-8"))
    installer = None
    if "INSTALLER" in files:
        installer = Path(str(dist.locate_file(files["INSTALLER"]))).read_text(encoding="utf-8").strip()
    record_sha = None
    if "RECORD" in files:
        record_sha = hashlib.sha256(Path(str(dist.locate_file(files["RECORD"]))).read_bytes()).hexdigest()
    try:
        mod = importlib.import_module(module)
        mod_file = str(Path(mod.__file__).resolve()) if getattr(mod, "__file__", None) else None
        import_error = None
    except Exception as exc:  # noqa: BLE001 - registrar, não esconder
        mod_file, import_error = None, f"{type(exc).__name__}: {exc}"
    purelib = str(Path(sysconfig.get_paths()["purelib"]).resolve())
    return {
        "name": name,
        "version": dist.version,
        "direct_url": direct,
        "editable": bool((direct or {}).get("dir_info", {}).get("editable")),
        "installer": installer,
        "record_sha256": record_sha,
        "module": module,
        "module_file": mod_file,
        "module_in_site_packages": bool(mod_file and mod_file.lower().startswith(purelib.lower())),
        "import_error": import_error,
    }


def lock_chain(lock_path: Path, pyproject_path: Path) -> list[dict]:
    lock = tomllib.loads(lock_path.read_text(encoding="utf-8"))
    pyproject = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    deps = pyproject["project"].get("dependencies", [])
    sources = pyproject.get("tool", {}).get("uv", {}).get("sources", {})
    out = []
    for pkg in lock.get("package", []):
        if pkg["name"] not in STACK or pkg["name"] == pyproject["project"]["name"]:
            continue
        spec = next((d for d in deps if d.split("[")[0].split("<")[0].split(">")[0].split("=")[0].split("!")[0].strip() == pkg["name"]), None)
        wheels = pkg.get("wheels", [])
        out.append({
            "name": pkg["name"], "pyproject_spec": spec, "uv_source": sources.get(pkg["name"]),
            "lock_version": pkg.get("version"), "lock_source": pkg.get("source"),
            "lock_wheel_url": wheels[0]["url"] if wheels else None,
            "lock_wheel_sha256": wheels[0]["hash"].removeprefix("sha256:") if wheels else None,
        })
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lock", type=Path)
    ap.add_argument("--pyproject", type=Path)
    args = ap.parse_args()
    report = {
        "python": sys.version.split()[0],
        "executable": sys.executable,
        "sys_path": sys.path,
        "packages": [x for x in (installed(n, m) for n, m in STACK.items()) if x],
    }
    if args.lock and args.pyproject:
        report["lock_chain"] = lock_chain(args.lock, args.pyproject)
    print(json.dumps(report, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
