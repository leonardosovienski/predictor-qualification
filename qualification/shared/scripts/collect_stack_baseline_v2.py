"""STACK_BASELINE_V2.0 (C3): base da Etapa B, coletada na preparação do envelope V2.

C3: "STACK_BASELINE_V2.0 = final_commits das três missões da Etapa A + release do protocolo V2".
A base de cada repo é:
  * cripto-predictor, brasileirao-predictor, stocks-predictor, core-predictor, predictor-ops: os
    final_commits das attestations da Etapa A no main (as três precisam concordar em Core e Ops);
  * ecosystem-predictor: o commit do main que contém a SPEC V2 congelada (--ecosystem-commit);
  * cain: o origin/main no congelamento (--cain-commit); o cain muda livremente na Etapa B.
O origin/main de cada repo entra só como informação (commits à frente/atrás, mesma árvore ou não).

Só leitura: git nos clones (rev fixada, `git show`/`ls-tree`, sem checkout nem mudança no clone) e
`gh api` (repos públicos). Não instala nem executa código dos repos. Todo comando e sua saída vão, sem
edição, para o log bruto; o JSON é derivado dessas saídas. Reaproveita as funções do coletor V1
(`collect_stack_baseline.py`), que fica sem mudança.

Uso:
  python collect_stack_baseline_v2.py --repos ~/predictors/repos --qualification <worktree do main>
      --ecosystem-commit SHA --cain-commit SHA --protocol-tag TAG --raw-log LOG --out FILE
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import platform
import re
import subprocess
import sys
import time
import tomllib
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("collect_stack_baseline_v1", HERE / "collect_stack_baseline.py")
v1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(v1)

OWNER = v1.OWNER
CORE_SHA256 = "beaa5feed193356f554922439936ad401c8f177bfd18d8864ca329fae94216fc"
MISSIONS = ("crypto", "brasileirao", "stocks")
DOMAIN_REPO = {"crypto": "cripto-predictor", "brasileirao": "brasileirao-predictor", "stocks": "stocks-predictor"}
# (repo, diretórios de pacote que entram em wheel) — os mesmos do coletor V1.
PACKAGE_DIRS = {repo: dirs for repo, _clone, dirs in v1.REPOS}
ORDER = [repo for repo, _clone, _dirs in v1.REPOS]


def collect_at(r: v1.Runner, repo: str, clone: str, rev: str) -> dict:
    package_dirs = PACKAGE_DIRS[repo]
    blobs = {}
    for line in r.git(clone, "ls-tree", "-r", rev).splitlines():
        meta, path = line.split("\t", 1)
        blobs[path] = meta.split()[2]
    pyproject = tomllib.loads(v1.blob_bytes(clone, rev, "pyproject.toml").decode("utf-8"))
    project = pyproject["project"]
    lock_bytes = v1.blob_bytes(clone, rev, "uv.lock")
    lock = tomllib.loads(lock_bytes.decode("utf-8"))
    stack, third_party = [], []
    for pkg in lock.get("package", []):
        source = pkg.get("source", {})
        kind = next(iter(source), "unknown")
        if pkg["name"] in v1.STACK_PACKAGES:
            wheels = pkg.get("wheels", [])
            stack.append({
                "name": pkg["name"], "version": pkg.get("version"), "source_kind": kind,
                "source": source.get(kind),
                "wheel_url": wheels[0].get("url") if wheels else source.get("url"),
                "wheel_sha256": wheels[0]["hash"].removeprefix("sha256:") if wheels else None,
            })
        else:
            third_party.append(f"{pkg['name']}=={pkg.get('version')} ({kind})")
    subpackages = []
    for path in sorted(blobs):
        if re.fullmatch(r"packages/[^/]+/pyproject\.toml", path):
            sub = tomllib.loads(v1.blob_bytes(clone, rev, path).decode("utf-8"))["project"]
            lock_path = path.replace("pyproject.toml", "uv.lock")
            subpackages.append({
                "path": path.rsplit("/", 1)[0], "name": sub["name"], "version": sub["version"],
                "dependencies": sub.get("dependencies", []),
                "uv_lock_sha256": v1.sha256_bytes(v1.blob_bytes(clone, rev, lock_path)) if lock_path in blobs else None,
            })
    schemas, ddl_modules, migrations = [], [], []
    for path, blob in sorted(blobs.items()):
        low = path.lower()
        if low.startswith(v1.EXCLUDED_TOP) or "/tests/" in low:
            continue
        if low.endswith(".json") and ("schema" in low or low.startswith(v1.SCHEMA_DIRS)
                                      or (v1.in_packages(path, package_dirs) and "contract" in low)):
            schemas.append({"path": path, "git_blob": blob})
        if "/migrations/" in low or ("migrat" in Path(low).name and low.endswith(".py")):
            migrations.append({"path": path, "git_blob": blob})
    grep = r.run(["git", "-C", clone, "grep", "-l", "-i", "CREATE TABLE", rev, "--", "*.py"], ok=(0, 1))
    for line in grep.splitlines():
        path = line.split(":", 1)[1]
        if v1.in_packages(path, package_dirs):
            ddl_modules.append({"path": path, "git_blob": blobs[path]})
    workflows = []
    for path, blob in sorted(blobs.items()):
        if path.startswith(".github/workflows/") and path.endswith((".yml", ".yaml")):
            text = v1.blob_bytes(clone, rev, path).decode("utf-8")
            name = re.search(r"^name:\s*(.+)$", text, re.M)
            workflows.append({"path": path, "git_blob": blob, "name": name.group(1).strip() if name else None,
                              "triggers": v1.workflow_triggers(text)})
    for attempt in range(4):
        runs = r.gh_api(f"repos/{OWNER}/{repo}/actions/runs?head_sha={rev}&per_page=100")
        if runs["workflow_runs"]:
            break
        time.sleep(5 * (attempt + 1))
    ci_runs = sorted(({"workflow": x["name"], "event": x["event"], "status": x["status"],
                       "conclusion": x["conclusion"], "run_id": x["id"], "url": x["html_url"]}
                      for x in runs["workflow_runs"]), key=lambda x: (x["workflow"], x["event"], x["run_id"]))
    return {
        "project": {
            "name": project["name"], "version": project["version"],
            "requires_python": project.get("requires-python"),
            "scripts": project.get("scripts", {}), "entry_points": project.get("entry-points", {}),
            "uv_sources": pyproject.get("tool", {}).get("uv", {}).get("sources", {}),
        },
        "subpackages": subpackages,
        "python_version_file": v1.blob_bytes(clone, rev, ".python-version").decode().strip()
        if ".python-version" in blobs else None,
        "uv_lock": {"sha256": v1.sha256_bytes(lock_bytes), "git_blob": blobs["uv.lock"],
                    "requires_python": lock.get("requires-python"), "packages_total": len(lock.get("package", []))},
        "stack_wheels_consumed": stack,
        "third_party_locked": third_party,
        "schemas": schemas, "ddl_modules": ddl_modules, "migrations": migrations,
        "ci_workflows": workflows, "ci_runs_at_base": ci_runs,
    }


def exit_code(r: v1.Runner, args: list[str]) -> int:
    """Roda um comando cujo resultado é o código de saída, com o mesmo registro do Runner."""
    result = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
    r.log.write(f"$ (cwd=None) {' '.join(args)}\n[exit {result.returncode}]\n{result.stdout}")
    if result.stderr:
        r.log.write(f"[stderr]\n{result.stderr}")
    r.log.write("\n")
    return result.returncode


def relation(r: v1.Runner, clone: str, base: str) -> dict:
    main = r.git(clone, "rev-parse", "origin/main").strip()
    code = exit_code(r, ["git", "-C", clone, "merge-base", "--is-ancestor", base, "origin/main"])
    if code not in (0, 1):
        raise RuntimeError(f"merge-base --is-ancestor falhou em {clone}")
    ahead = int(r.git(clone, "rev-list", "--count", f"{base}..origin/main").strip())
    behind = int(r.git(clone, "rev-list", "--count", f"origin/main..{base}").strip())
    same_tree = r.git(clone, "rev-parse", f"{base}^{{tree}}").strip() == r.git(
        clone, "rev-parse", "origin/main^{tree}").strip()
    changed = r.git(clone, "diff", "--name-only", base, "origin/main").split()
    top = sorted({p.split("/", 1)[0] + ("/" if "/" in p else "") for p in changed})
    return {"commit": main, "base_is_ancestor": code == 0, "commits_main_not_base": ahead,
            "commits_base_not_main": behind, "same_tree": same_tree, "files_changed": len(changed),
            "top_level_paths_changed": top}


def release_wheels(r: v1.Runner, repo: str, clone: str, base: str) -> list[dict]:
    published = []
    for rel in r.gh_api(f"repos/{OWNER}/{repo}/releases?per_page=100"):
        ref = r.gh_api(f"repos/{OWNER}/{repo}/git/ref/tags/{rel['tag_name']}")
        obj = ref["object"]
        if obj["type"] == "tag":
            obj = r.gh_api(f"repos/{OWNER}/{repo}/git/tags/{obj['sha']}")["object"]
        for asset in rel["assets"]:
            if asset["name"].endswith(".whl"):
                published.append({
                    "tag": rel["tag_name"], "prerelease": rel["prerelease"], "tag_commit": obj["sha"],
                    "tag_commit_is_base": obj["sha"] == base, "asset": asset["name"],
                    "url": asset["browser_download_url"],
                    "sha256": (asset.get("digest") or "").removeprefix("sha256:") or None,
                })
    return published


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repos", required=True, type=Path)
    ap.add_argument("--qualification", required=True, type=Path)
    ap.add_argument("--ecosystem-commit", required=True)
    ap.add_argument("--cain-commit", required=True)
    ap.add_argument("--protocol-tag", required=True)
    ap.add_argument("--raw-log", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--note")
    args = ap.parse_args()
    args.raw_log.parent.mkdir(parents=True, exist_ok=True)
    r = v1.Runner(args.raw_log)
    q = str(args.qualification)
    q_commit = r.git(q, "rev-parse", "HEAD").strip()
    core_sha = v1.sha256_bytes(v1.blob_bytes(q, "HEAD", "qualification/COMMON_QUALIFICATION_CORE.md"))
    if core_sha != CORE_SHA256:
        raise SystemExit(f"núcleo {core_sha} != v2.3 {CORE_SHA256}")

    missions, finals = {}, {}
    for mission in MISSIONS:
        att_path = f"qualification/{mission}/QUALIFICATION_ATTESTATION.json"
        raw = v1.blob_bytes(q, "HEAD", att_path)
        att = json.loads(raw)
        contract_path = f"qualification/{mission}/DOMAIN_RESEARCH_CONTRACT.json"
        contract_sha = v1.sha256_bytes(v1.blob_bytes(q, "HEAD", contract_path))
        target = json.loads(v1.blob_bytes(q, "HEAD", f"qualification/{mission}/runtime_target.json"))
        if att["result"] != "QUALIFIED" or att["domain_contract_sha256"] != contract_sha:
            raise SystemExit(f"{mission}: attestation não QUALIFIED ou contrato divergente")
        commits = {c["repo"]: c["commit_sha"] for c in att["final_commits"]}
        if target["commit"] != commits[DOMAIN_REPO[mission]]:
            raise SystemExit(f"{mission}: runtime_target {target['commit']} != final_commit")
        for repo, sha in commits.items():
            if finals.setdefault(repo, sha) != sha:
                raise SystemExit(f"final_commits divergentes para {repo}: {finals[repo]} × {sha}")
        missions[mission] = {
            "attestation": {"path": att_path, "sha256": v1.sha256_bytes(raw), "result": att["result"],
                            "common_core_version": att["common_core_version"],
                            "counts": att["counts"], "generated_at": att["generated_at"]},
            "domain_contract": {"path": contract_path, "sha256": contract_sha},
            "runtime_target": {"path": f"qualification/{mission}/runtime_target.json", "commit": target["commit"],
                               "wheel_sha256": target["wheel_sha256"]},
            "final_commits": att["final_commits"],
            "final_wheels": att["final_wheels"],
        }
    bases = dict(finals)
    bases["ecosystem-predictor"] = args.ecosystem_commit
    bases["cain"] = args.cain_commit
    base_source = {repo: "final_commits das attestations da Etapa A (crypto, brasileirao, stocks)" for repo in finals}
    for mission in MISSIONS:
        base_source[DOMAIN_REPO[mission]] = f"final_commit da attestation {mission} (= runtime_target.json)"
    base_source["ecosystem-predictor"] = "main com a SPEC V2 congelada (ENVELOPE_V2_FREEZE.json)"
    base_source["cain"] = "origin/main no congelamento; o cain muda livremente na Etapa B (C3)"

    repos = []
    for repo in ORDER:
        clone = str(args.repos / repo)
        base = r.git(clone, "rev-parse", "--verify", f"{bases[repo]}^{{commit}}").strip()
        entry = {"repo": repo, "clone": clone, "remote": r.git(clone, "remote", "get-url", "origin").strip(),
                 "base": {"commit": base, "source": base_source[repo],
                          "tags_at_base": r.git(clone, "tag", "--points-at", base).split()},
                 "origin_main": relation(r, clone, base)}
        entry.update(collect_at(r, repo, clone, base))
        entry["published_wheels"] = release_wheels(r, repo, clone, base)
        repos.append(entry)

    # final_wheels da Etapa B = as da Etapa A + a wheel do protocolo V2, cada uma contra o digest do asset
    wheels = {}
    for mission in MISSIONS:
        for w in missions[mission]["final_wheels"]:
            wheels.setdefault(w["url"], dict(w, used_by=[]))["used_by"].append(mission)
    rel = r.gh_api(f"repos/{OWNER}/ecosystem-predictor/releases/tags/{args.protocol_tag}")
    proto = [a for a in rel["assets"] if a["name"].endswith(".whl")]
    if len(proto) != 1:
        raise SystemExit(f"{args.protocol_tag}: esperava 1 wheel, achei {len(proto)}")
    wheels[proto[0]["browser_download_url"]] = {
        "package": "predictor-research-protocol", "version": args.protocol_tag.rsplit("-v", 1)[1],
        "url": proto[0]["browser_download_url"], "sha256": proto[0]["digest"].removeprefix("sha256:"),
        "used_by": ["envelope-v2"]}
    verification = []
    for url, w in sorted(wheels.items()):
        m = re.match(rf"https://github.com/{OWNER}/([^/]+)/releases/download/([^/]+)/(.+)$", url)
        release = r.gh_api(f"repos/{OWNER}/{m.group(1)}/releases/tags/{m.group(2)}")
        digest = next((a.get("digest", "").removeprefix("sha256:") for a in release["assets"]
                       if a["name"] == m.group(3)), None)
        verification.append({"package": w.get("package") or w.get("name"), "version": w["version"], "url": url,
                             "declared_sha256": w["sha256"], "release_asset_sha256": digest,
                             "match": digest == w["sha256"], "prerelease": release["prerelease"],
                             "used_by": w["used_by"]})
    host = {"role": "coletor (só git e gh api; nada dos repos é executado)", "os": platform.platform(),
            "python_collector": sys.version.split()[0], "uv": r.run(["uv", "--version"]).strip(),
            "gh": r.run(["gh", "--version"]).splitlines()[0]}
    baseline = {
        "baseline_id": "STACK_BASELINE_V2.0",
        "note": args.note,
        "common_core_version": "2.3",
        "common_core_sha256": CORE_SHA256,
        "decisions": ["D-12", "D-22"],
        "mission_prompt": "prompts/prompt_preparacao_envelope_v2_rev8.md",
        "predictor_qualification_commit": q_commit,
        "collected_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "collector": "qualification/shared/scripts/collect_stack_baseline_v2.py",
        "environments": {"collector_host": host},
        "stage_a": missions,
        "repos": repos,
        "final_wheel_verification": verification,
        "all_final_wheels_match": all(v["match"] for v in verification),
        "capital_permission": False,
        "training_started": False,
    }
    args.out.write_text(json.dumps(baseline, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"{args.out}: {len(repos)} repos; final_wheels {sum(v['match'] for v in verification)}/{len(verification)} OK")


if __name__ == "__main__":
    main()
