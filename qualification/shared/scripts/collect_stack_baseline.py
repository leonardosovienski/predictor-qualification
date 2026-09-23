"""SHARED-001: coleta o STACK_BASELINE_V1 dos 7 clones de qualificação (C3).

Só leitura: comandos `git` nos clones e `gh api` (repos públicos). Não instala,
não cria venv, não executa código dos repos (regras locais do Stocks e do Cripto).
Todo comando executado e sua saída vão, sem edição, para o log bruto; o JSON é
derivado dessas mesmas saídas.

Uso:
  python collect_stack_baseline.py --raw-log <RAW_LOGS/.../collect.log> --out <STACK_BASELINE_V1.json>
      [--linux-facts <cleanroom facts dir>]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import re
import subprocess
import sys
import time
import tomllib
from datetime import datetime, timezone
from pathlib import Path

OWNER = "leonardosovienski"
REPOS = [
    # (repo, clone, diretórios de pacote que entram em wheel)
    ("cain", r"C:\QUALIFICACAO\repos\cain", ["src/cain"]),
    ("ecosystem-predictor", r"C:\QUALIFICACAO\repos\ecosystem-predictor",
     ["src/ecosystem", "packages/research-protocol/src", "packages/research-snapshot/src",
      "packages/research-bundle/src"]),
    ("core-predictor", r"C:\QUALIFICACAO\repos\core-predictor", ["src/predictor_core"]),
    ("predictor-ops", r"C:\QUALIFICACAO\repos\predictor-ops", ["src/predictor_ops"]),
    ("brasileirao-predictor", r"C:\QUALIFICACAO\repos\brasileirao-predictor",
     ["brasileirao_predictor", "brasileirao_scripts"]),
    ("cripto-predictor", r"C:\Cripto\qualificacao\cripto-predictor",
     ["GarimpoInvestimentos", "packages/research-export/src"]),
    ("stocks-predictor", r"C:\STOCKS\work\qualification\stocks-predictor", ["stocks_predictor"]),
]
STACK_PACKAGES = {
    "predictor-core", "predictor-ops", "predictor-research-protocol", "predictor-research-snapshot",
    "predictor-research-bundle", "cain-research", "ecosystem-predictor", "crypto-research-export",
    "cripto-predictor", "brasileirao-predictor", "stocks-predictor",
}
EXCLUDED_TOP = ("tests/", "test/", "docs/", "audit/", "audits/", "evidence/", "reports/", "research/",
                "legacy/", "vendor/")
SCHEMA_DIRS = ("schemas/", "contracts/", "canonical_contracts/")


class Runner:
    def __init__(self, log_path: Path) -> None:
        self.log = log_path.open("w", encoding="utf-8", newline="\n")

    def run(self, args: list[str], cwd: str | None = None, ok: tuple[int, ...] = (0,)) -> str:
        result = subprocess.run(args, cwd=cwd, capture_output=True, text=True, encoding="utf-8",
                                errors="replace", check=False)
        self.log.write(f"$ (cwd={cwd}) {' '.join(args)}\n[exit {result.returncode}]\n{result.stdout}")
        if result.stderr:
            self.log.write(f"[stderr]\n{result.stderr}")
        self.log.write("\n")
        if result.returncode not in ok:
            raise RuntimeError(f"falhou: {args} ({result.stderr.strip()})")
        return result.stdout

    def git(self, clone: str, *args: str) -> str:
        return self.run(["git", "-C", clone, *args])

    def gh_api(self, path: str) -> object:
        return json.loads(self.run(["gh", "api", path]))


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def blob_bytes(clone: str, rev: str, path: str) -> bytes:
    return subprocess.run(["git", "-C", clone, "show", f"{rev}:{path}"], capture_output=True,
                          check=True).stdout


def workflow_triggers(text: str) -> list[str]:
    inline = re.search(r"^on:\s*\[([^\]]*)\]", text, re.M)
    if inline:
        return sorted(t.strip() for t in inline.group(1).split(",") if t.strip())
    single = re.search(r"^on:\s*([a-z_]+)\s*$", text, re.M)
    if single:
        return [single.group(1)]
    block = re.search(r"^on:\s*\n((?:[ \t]+.*\n|\s*\n)+)", text, re.M)
    if not block:
        return []
    return sorted(set(re.findall(r"^  ([a-z_]+):", block.group(1), re.M)))


def in_packages(path: str, package_dirs: list[str]) -> bool:
    return any(path == d or path.startswith(d + "/") for d in package_dirs)


def collect_repo(r: Runner, repo: str, clone: str, package_dirs: list[str]) -> dict:
    head = r.git(clone, "rev-parse", "HEAD").strip()
    origin_main = r.git(clone, "rev-parse", "origin/main").strip()
    branch = r.git(clone, "rev-parse", "--abbrev-ref", "HEAD").strip()
    porcelain = r.git(clone, "status", "--porcelain", "--untracked-files=all")
    remote = r.git(clone, "remote", "get-url", "origin").strip()
    files = r.git(clone, "ls-tree", "-r", "HEAD").splitlines()
    blobs = {}
    for line in files:
        meta, path = line.split("\t", 1)
        blobs[path] = meta.split()[2]

    pyproject = tomllib.loads(blob_bytes(clone, "HEAD", "pyproject.toml").decode("utf-8"))
    project = pyproject["project"]
    lock_bytes = blob_bytes(clone, "HEAD", "uv.lock")
    lock = tomllib.loads(lock_bytes.decode("utf-8"))
    worktree_lock = (Path(clone) / "uv.lock").read_bytes()

    stack, third_party = [], []
    for pkg in lock.get("package", []):
        source = pkg.get("source", {})
        kind = next(iter(source), "unknown")
        if pkg["name"] in STACK_PACKAGES:
            wheels = pkg.get("wheels", [])
            stack.append({
                "name": pkg["name"], "version": pkg.get("version"), "source_kind": kind,
                "source": source.get(kind),
                "wheel_url": wheels[0].get("url") if wheels else source.get("url"),
                "wheel_sha256": wheels[0]["hash"].removeprefix("sha256:") if wheels else None,
            })
        else:
            third_party.append(f"{pkg['name']}=={pkg.get('version')} ({kind})")

    schemas, ddl_modules, migrations = [], [], []
    for path, blob in sorted(blobs.items()):
        low = path.lower()
        if low.startswith(EXCLUDED_TOP) or "/tests/" in low:
            continue
        if low.endswith(".json") and ("schema" in low or low.startswith(SCHEMA_DIRS)
                                      or (in_packages(path, package_dirs) and "contract" in low)):
            schemas.append({"path": path, "git_blob": blob})
        if "/migrations/" in low or ("migrat" in Path(low).name and low.endswith(".py")):
            migrations.append({"path": path, "git_blob": blob})
    grep = r.run(["git", "-C", clone, "grep", "-l", "-i", "CREATE TABLE", "HEAD", "--", "*.py"], ok=(0, 1))
    for line in grep.splitlines():
        path = line.split(":", 1)[1]
        if in_packages(path, package_dirs):
            ddl_modules.append({"path": path, "git_blob": blobs[path]})

    workflows = []
    for path, blob in sorted(blobs.items()):
        if path.startswith(".github/workflows/") and path.endswith((".yml", ".yaml")):
            text = blob_bytes(clone, "HEAD", path).decode("utf-8")
            name = re.search(r"^name:\s*(.+)$", text, re.M)
            workflows.append({"path": path, "git_blob": blob, "name": name.group(1).strip() if name else None,
                              "triggers": workflow_triggers(text)})
    # A listagem por head_sha às vezes volta vazia de forma transitória; repete (tudo fica no log).
    for attempt in range(4):
        runs = r.gh_api(f"repos/{OWNER}/{repo}/actions/runs?head_sha={head}&per_page=100")
        if runs["workflow_runs"]:
            break
        time.sleep(5 * (attempt + 1))
    ci_runs = sorted(({"workflow": x["name"], "event": x["event"], "status": x["status"],
                       "conclusion": x["conclusion"], "run_id": x["id"], "url": x["html_url"]}
                      for x in runs["workflow_runs"]), key=lambda x: (x["workflow"], x["event"], x["run_id"]))

    releases = r.gh_api(f"repos/{OWNER}/{repo}/releases?per_page=100")
    published = []
    for rel in releases:
        ref = r.gh_api(f"repos/{OWNER}/{repo}/git/ref/tags/{rel['tag_name']}")
        obj = ref["object"]
        if obj["type"] == "tag":
            obj = r.gh_api(f"repos/{OWNER}/{repo}/git/tags/{obj['sha']}")["object"]
        tag_commit = obj["sha"]
        for asset in rel["assets"]:
            if not asset["name"].endswith(".whl"):
                continue
            changed = r.git(clone, "diff", "--name-only", tag_commit, head, "--", *package_dirs).split()
            published.append({
                "tag": rel["tag_name"], "prerelease": rel["prerelease"], "tag_commit": tag_commit,
                "asset": asset["name"], "url": asset["browser_download_url"],
                "sha256": (asset.get("digest") or "").removeprefix("sha256:") or None,
                "package_files_changed_tag_to_head": len(changed),
            })

    return {
        "repo": repo, "clone": clone, "remote": remote, "branch": branch, "head": head,
        "origin_main": origin_main, "head_equals_origin_main": head == origin_main,
        "clean": porcelain.strip() == "", "dirty_entries": len(porcelain.splitlines()),
        "project": {
            "name": project["name"], "version": project["version"],
            "requires_python": project.get("requires-python"),
            "scripts": project.get("scripts", {}),
            "entry_points": project.get("entry-points", {}),
            "uv_sources": pyproject.get("tool", {}).get("uv", {}).get("sources", {}),
        },
        "python_version_file": blob_bytes(clone, "HEAD", ".python-version").decode().strip()
        if ".python-version" in blobs else None,
        "uv_lock": {"sha256": sha256_bytes(lock_bytes), "git_blob": blobs["uv.lock"],
                    "worktree_equals_head": sha256_bytes(worktree_lock) == sha256_bytes(lock_bytes),
                    "requires_python": lock.get("requires-python"),
                    "packages_total": len(lock.get("package", []))},
        "stack_wheels_consumed": stack,
        "third_party_locked": third_party,
        "schemas": schemas, "ddl_modules": ddl_modules, "migrations": migrations,
        "ci_workflows": workflows, "ci_runs_at_head": ci_runs,
        "published_wheels": published,
    }


def verify_stack_wheels(r: Runner, repos: list[dict]) -> list[dict]:
    """Confere o sha256 do lock com o digest do asset da release (API do GitHub)."""
    checks = {}
    for entry in repos:
        for w in entry["stack_wheels_consumed"]:
            if w["source_kind"] != "url":
                continue
            m = re.match(rf"https://github.com/{OWNER}/([^/]+)/releases/download/([^/]+)/(.+)$", w["wheel_url"])
            key = w["wheel_url"]
            if key in checks:
                checks[key]["consumers"].append(entry["repo"])
                continue
            digest = None
            if m:
                rel = r.gh_api(f"repos/{OWNER}/{m.group(1)}/releases/tags/{m.group(2)}")
                digest = next((a.get("digest", "").removeprefix("sha256:") for a in rel["assets"]
                               if a["name"] == m.group(3)), None)
            checks[key] = {"name": w["name"], "version": w["version"], "url": key, "lock_sha256": w["wheel_sha256"],
                           "release_asset_sha256": digest, "match": digest == w["wheel_sha256"],
                           "consumers": [entry["repo"]]}
    return sorted(checks.values(), key=lambda c: (c["name"], c["version"]))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw-log", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--linux-facts", type=Path)
    args = ap.parse_args()
    args.raw_log.parent.mkdir(parents=True, exist_ok=True)
    r = Runner(args.raw_log)
    repos = [collect_repo(r, *spec) for spec in REPOS]
    uv_version = r.run(["uv", "--version"]).strip()
    windows = {
        "role": "secondary (Windows local; ferramentas da qualificação em C:\\QUALIFICACAO\\tools)",
        "os": platform.platform(), "python_collector": sys.version.split()[0], "uv": uv_version,
    }
    linux = None
    if args.linux_facts:
        facts = sorted(args.linux_facts.glob("*/cleanroom_facts.json"))
        envs = {json.dumps(json.loads(f.read_text(encoding="utf-8"))["environment"], sort_keys=True)
                for f in facts}
        linux = {"role": "primary (GitHub Actions, D-9)", "source": "cleanroom-baseline (SHARED-002)",
                 "environments_seen": [json.loads(e) for e in sorted(envs)]}
    baseline = {
        "baseline_id": "STACK_BASELINE_V1",
        "common_core_sha256": "50e8f49859daae6dcdf17164781d1837d8b656796924c35060f8d35855ee36e1",
        "mission_prompt": "prompts/baseline_comum_rev8.md",
        "collected_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "collector": "qualification/shared/scripts/collect_stack_baseline.py",
        "environments": {"windows_local": windows, "linux_primary": linux},
        "repos": repos,
        "stack_wheel_verification": verify_stack_wheels(r, repos),
        "capital_permission": False,
        "training_started": False,
    }
    args.out.write_text(json.dumps(baseline, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"{args.out}: {len(repos)} repos")


if __name__ == "__main__":
    main()
