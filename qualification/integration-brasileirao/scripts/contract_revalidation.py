"""integration-brasileirao, fase contract-revalidation (C24.3; DOMAIN_CONTRACTS_PRESERVED), parte estática (a), (b), (e), (f).

Adaptado de qualification/integration-stocks/scripts/contract_revalidation.py (domínio brasileirao; prompt da sessão 10.1).
  (a) diff do brasileirao-predictor entre o final_commit da Etapa A (25cdf4d) e o final_commit desta missão: só em
      adapter_paths (brasileirao_predictor/adapters/), exceto (C24.3 a) a versão pré-release (linha `version` do
      pyproject e a linha da versão do projeto no uv.lock); tests/, docs/, .github/, README.md, config.yaml e
      data/trials.harness_attestation.json intocados (prompt da sessão 10.1);
  (b) regras de adapter_paths no commit final, pelo grafo de imports (AST) dos arquivos do pacote: nada fora de
      brasileirao_predictor/adapters/ importa algo de dentro; nenhum console script ou plugin aponta para dentro
      (adapter_entrypoints vazio: [project.scripts] igual ao da Etapa A); o adapter importa só a stdlib e a adapter_api
      (brasileirao_predictor.research_runtime.runner); o teste congelado roda no cleanroom-final, parte (c);
  (e) conjunto protegido: todo item do PROTECTED_SET.json da missão (domínio brasileirao) tem o mesmo blob no commit final;
  (f) CI do domínio no SHA exato do commit final: todos os runs do CI Pipeline e do publication-validation nesse SHA, com
      evento e jobs (C21; a regra 10.3 do prompt da sessão exige evento push; o ci.yml do Brasileirão só dispara push em
      main: IB-F005, decisão do dono).
As partes (c) e (d) rodam no runtime suportado (cleanroom_final.sh e contract_d.py).

Uso: python contract_revalidation.py <clone do brasileirao-predictor> <final_commit> <qualification/integration-brasileirao>
     <out.json> [<aceite do dono (IB-F005)>]
"""

from __future__ import annotations

import ast
import json
import subprocess
import sys
import tomllib
from pathlib import Path

STAGE_A = "25cdf4d9bb309d33f066fbc6a379f5d98c69f08a"
ADAPTERS = "brasileirao_predictor/adapters/"
UNTOUCHABLE = ("tests/", "docs/", ".github/", "README.md", "config.yaml", "data/trials.harness_attestation.json")
REPO = "leonardosovienski/brasileirao-predictor"


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=True).stdout


def imports(source: str) -> list[str]:
    names = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            names += [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.append(("." * node.level) + node.module)
    return names


def main() -> int:
    repo, final, mission, out = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3]), Path(sys.argv[4])
    checks = []

    def check(name: str, ok: bool, **detail) -> None:
        checks.append({"check": name, "ok": bool(ok), **detail})

    # (a)
    status = [line.split("\t") for line in git(repo, "diff", "--name-status", STAGE_A, final).splitlines()]
    changed = {p[-1]: p[0] for p in status}
    outside = {p: s for p, s in changed.items() if not p.startswith(ADAPTERS)}
    check("(a) outside adapter_paths only the version files", set(outside) <= {"pyproject.toml", "uv.lock"},
          changed=changed)
    check("(a) tests/, docs/, .github/, README.md, config.yaml and data/trials.harness_attestation.json untouched",
          not [p for p in changed if p.startswith(UNTOUCHABLE)], touched=[p for p in changed if p.startswith(UNTOUCHABLE)])
    for path in ("pyproject.toml", "uv.lock"):
        diff = git(repo, "diff", "--unified=0", STAGE_A, final, "--", path)
        lines = [line for line in diff.splitlines() if line[:1] in "+-" and not line.startswith(("+++", "---"))]
        check(f"(a) {path}: only the pre-release version line changed",
              sorted(line[1:] for line in lines) == sorted(['version = "0.3.0rc3"', 'version = "0.3.0rc4"']),
              lines=lines)
    lock_a = tomllib.loads(git(repo, "show", f"{STAGE_A}:uv.lock"))
    lock_f = tomllib.loads(git(repo, "show", f"{final}:uv.lock"))
    strip = lambda lock: [{k: v for k, v in p.items() if not (p["name"] == "brasileirao-predictor" and k == "version")}  # noqa: E731
                          for p in lock["package"]]
    check("(a) uv.lock identical apart from the project version (no dependency change)", strip(lock_a) == strip(lock_f))
    # (b)
    tree = git(repo, "ls-tree", "-r", "--name-only", final).split()
    offenders = []
    for path in tree:
        if path.startswith(("brasileirao_predictor/", "brasileirao_scripts/")) and path.endswith(".py") \
                and not path.startswith(ADAPTERS):
            names = imports(git(repo, "show", f"{final}:{path}"))
            if any(n == "brasileirao_predictor.adapters" or n.startswith("brasileirao_predictor.adapters.")
                   or n in ("adapters", ".adapters") or n.startswith(".adapters.") for n in names):
                offenders.append(path)
    check("(b) nothing outside adapter_paths imports from it", offenders == [], offenders=offenders)
    project_a = tomllib.loads(git(repo, "show", f"{STAGE_A}:pyproject.toml"))["project"]
    project_f = tomllib.loads(git(repo, "show", f"{final}:pyproject.toml"))["project"]
    check("(b) no console script or plugin entry point added (adapter_entrypoints is empty)",
          project_a.get("scripts") == project_f.get("scripts")
          and project_a.get("entry-points") == project_f.get("entry-points")
          and not any("adapters" in v for v in project_f.get("scripts", {}).values()), scripts=project_f.get("scripts"))
    stdlib = set(sys.stdlib_module_names) | {"__future__"}
    adapter_files = [p for p in tree if p.startswith(ADAPTERS) and p.endswith(".py")]
    foreign = {}
    for path in adapter_files:
        for name in imports(git(repo, "show", f"{final}:{path}")):
            top = name.lstrip(".").split(".")[0]
            if top in stdlib or name == "brasileirao_predictor.research_runtime.runner":
                continue
            foreign.setdefault(path, []).append(name)
    check("(b) the adapter imports only the standard library and the adapter_api "
          "(brasileirao_predictor.research_runtime.runner)", foreign == {}, adapter_files=adapter_files, foreign=foreign)
    # (e)
    protected = json.loads((mission / "PROTECTED_SET.json").read_text(encoding="utf-8"))["domains"]["brasileirao"]
    blobs = {}
    for line in git(repo, "ls-tree", "-r", final).splitlines():
        meta, path = line.split("\t", 1)
        blobs[path] = meta.split()[2]
    changed_protected = [e["path"] for e in protected["entries"] if blobs.get(e["path"]) != e["git_blob"]]
    check("(e) every protected item of the brasileirao domain has the same blob at the final commit",
          changed_protected == [], items=protected["items"], changed=changed_protected)
    # (f)
    runs = json.loads(subprocess.run(["gh", "run", "list", "-R", REPO, "--commit", final, "--limit", "50",
                                      "--json", "databaseId,conclusion,status,headSha,url,name,event,headBranch"],
                                     capture_output=True, text=True, check=True).stdout)
    detail = []
    for r in runs:
        if r["name"] not in ("CI Pipeline", "Scoped synthetic publication validation"):
            continue
        jobs = json.loads(subprocess.run(["gh", "run", "view", str(r["databaseId"]), "-R", REPO, "--json", "jobs"],
                                         capture_output=True, text=True, check=True).stdout)["jobs"]
        detail.append(r | {"jobs": {j["name"]: j["conclusion"] for j in jobs}})
    ci_push = [r for r in detail if r["name"] == "CI Pipeline" and r["event"] == "push" and r["conclusion"] == "success"]
    pv_push = [r for r in detail if r["name"] == "Scoped synthetic publication validation" and r["event"] == "push"
               and r["conclusion"] == "success"]
    accepted = None
    if len(sys.argv) > 5:
        acc = json.loads(Path(sys.argv[5]).read_text(encoding="utf-8"))
        accepted = acc.get("accepted") is True and acc.get("final_commit") == final
    check("(f) CI of the domain on the exact final commit: green push runs of CI Pipeline and publication validation "
          "(prompt 10.3), or the path accepted by the owner (IB-F005)", (bool(ci_push) and bool(pv_push)) or bool(accepted),
          runs=detail, ci_pipeline_push=bool(ci_push), publication_validation_push=bool(pv_push),
          acceptance=sys.argv[5] if len(sys.argv) > 5 else None)
    doc = {"schema": "integration-brasileirao/CONTRACT_REVALIDATION_STATIC/1", "stage_a_final_commit": STAGE_A,
           "final_commit": final,
           "authorized_outside_adapter_paths": {"C24.3(a)": "versão pré-release (pyproject version, linha do projeto no uv.lock)"},
           "checks": checks, "passed": sum(c["ok"] for c in checks), "failed": sum(not c["ok"] for c in checks)}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({k: doc[k] for k in ("final_commit", "passed", "failed")}))
    for c in checks:
        if not c["ok"]:
            print("FAILED", json.dumps(c, ensure_ascii=False)[:600])
    return 0 if doc["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
