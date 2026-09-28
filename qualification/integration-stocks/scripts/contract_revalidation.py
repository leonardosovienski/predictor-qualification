"""integration-stocks, fase contract-revalidation (C24.3; DOMAIN_CONTRACTS_PRESERVED), parte estática (a), (b), (e), (f).

Adaptado de qualification/integration-crypto/scripts/contract_revalidation.py (domínio stocks; D-24 (4)).
  (a) diff do stocks-predictor entre o final_commit da Etapa A (61fc017) e o final_commit desta missão: só em
      adapter_paths (stocks_predictor/adapters/), exceto (C24.3 a) a versão pré-release (linha `version` do pyproject e
      a linha da versão do projeto no uv.lock) e (D-24 (4)) arquivos NOVOS em tests/adapters/, os dois recibos R8 novos
      (só .json em docs/engineering/<data>-integration-stocks/evidence/) e o selo
      docs/engineering/current-operational-evidence.json; cada linha fora de adapter_paths é conferida;
  (b) regras de adapter_paths no commit final, pelo grafo de imports (AST) dos arquivos do pacote: nada fora de
      stocks_predictor/adapters/ importa algo de dentro; nenhum console script aponta para dentro (adapter_entrypoints
      vazio: [project.scripts] igual ao da Etapa A); o teste congelado roda no cleanroom-final, parte (c);
  (e) conjunto protegido: todo item do PROTECTED_SET.json da missão (domínio stocks) tem o mesmo blob no commit final;
  (f) CI do domínio no SHA exato do commit final: todo run do CI Pipeline nesse SHA, com evento e jobs (C21; a regra 9.3
      do prompt da sessão exige evento push: IS-F004/IS-F005).
As partes (c) e (d) rodam no runtime suportado (cleanroom_final.sh e contract_d.py).

Uso: python contract_revalidation.py <clone do stocks-predictor> <final_commit> <qualification/integration-stocks> <out.json>
"""

from __future__ import annotations

import ast
import json
import re
import subprocess
import sys
import tomllib
from pathlib import Path

STAGE_A = "61fc017256ffea815ae96bbe02b847dccdb395cc"
ADAPTERS = "stocks_predictor/adapters/"
SEAL = "docs/engineering/current-operational-evidence.json"
R8_DIR = re.compile(r"docs/engineering/\d{4}-\d{2}-\d{2}-integration-stocks/evidence/[^/]+\.json\Z")


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=True).stdout


def main() -> int:
    repo, final, mission, out = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3]), Path(sys.argv[4])
    checks = []

    def check(name: str, ok: bool, **detail) -> None:
        checks.append({"check": name, "ok": bool(ok), **detail})

    # (a)
    status = [line.split("\t") for line in git(repo, "diff", "--name-status", STAGE_A, final).splitlines()]
    changed = {p[-1]: p[0] for p in status}
    outside = {p: s for p, s in changed.items() if not p.startswith(ADAPTERS)}
    new_tests = {p for p, s in outside.items() if p.startswith("tests/adapters/") and s == "A"}
    receipts = {p for p, s in outside.items() if R8_DIR.fullmatch(p) and s == "A"}
    rest = set(outside) - new_tests - receipts
    check("(a) outside adapter_paths only: version files, new tests/adapters/, new R8 receipts (.json) and the seal",
          rest <= {"pyproject.toml", "uv.lock", SEAL} and all(s == "A" for p, s in outside.items()
                                                             if p.startswith("tests/")),
          changed=changed, tests_adapters_new=sorted(new_tests), r8_receipts_new=sorted(receipts), other=sorted(rest))
    check("(a) no existing test changed (tests/ outside tests/adapters/ untouched)",
          not [p for p in changed if p.startswith("tests/") and not p.startswith("tests/adapters/")])
    check("(a) no new Markdown and nothing under tools/, .github/, research/, policy/ or the rest of docs/",
          not [p for p in changed if p.endswith(".md") or p.startswith(("tools/", ".github/", "research/", "policy/"))
               or (p.startswith("docs/") and p != SEAL and p not in receipts)])
    for path in ("pyproject.toml", "uv.lock"):
        diff = git(repo, "diff", "--unified=0", STAGE_A, final, "--", path)
        lines = [line for line in diff.splitlines() if line[:1] in "+-" and not line.startswith(("+++", "---"))]
        check(f"(a) {path}: only the pre-release version line changed",
              sorted(line[1:] for line in lines) == sorted(['version = "0.3.0rc2"', 'version = "0.3.0rc3"']),
              lines=lines)
    lock_a = tomllib.loads(git(repo, "show", f"{STAGE_A}:uv.lock"))
    lock_f = tomllib.loads(git(repo, "show", f"{final}:uv.lock"))
    strip = lambda lock: [{k: v for k, v in p.items() if not (p["name"] == "stocks-predictor" and k == "version")}  # noqa: E731
                          for p in lock["package"]]
    check("(a) uv.lock identical apart from the project version (no dependency change)", strip(lock_a) == strip(lock_f))
    seal = json.loads(git(repo, "show", f"{final}:{SEAL}"))
    check("(a) the seal points to the new R8 receipts and never enables capital or certifies profit",
          seal["real_validation"] in receipts and seal["capacity_validation"] in receipts
          and seal["capital_enabled"] is False and seal["profit_certified"] is False,
          real=seal["real_validation"], capacity=seal["capacity_validation"])
    old_receipts = [p for p in git(repo, "ls-tree", "-r", "--name-only", STAGE_A, "docs/engineering/").split()
                    if p.endswith(".json") and "/evidence/" in p]
    check("(a) previous R8 receipts intact", not [p for p in old_receipts if p in changed], previous=len(old_receipts))
    # (b)
    tree = git(repo, "ls-tree", "-r", "--name-only", final).split()
    offenders = []
    for path in tree:
        if path.startswith("stocks_predictor/") and path.endswith(".py") and not path.startswith(ADAPTERS):
            for node in ast.walk(ast.parse(git(repo, "show", f"{final}:{path}"))):
                names = []
                if isinstance(node, ast.Import):
                    names = [a.name for a in node.names]
                elif isinstance(node, ast.ImportFrom) and node.module:
                    names = [node.module]
                if any(n == "stocks_predictor.adapters" or n.startswith("stocks_predictor.adapters.")
                       or n in ("adapters", ".adapters") for n in names):
                    offenders.append(path)
    check("(b) nothing outside adapter_paths imports from it", offenders == [], offenders=offenders)
    scripts_a = tomllib.loads(git(repo, "show", f"{STAGE_A}:pyproject.toml"))["project"]
    scripts_f = tomllib.loads(git(repo, "show", f"{final}:pyproject.toml"))["project"]
    check("(b) no console script or plugin entry point added (adapter_entrypoints is empty)",
          scripts_a.get("scripts") == scripts_f.get("scripts")
          and scripts_a.get("entry-points") == scripts_f.get("entry-points")
          and not any("adapters" in v for v in scripts_f.get("scripts", {}).values()), scripts=scripts_f.get("scripts"))
    # (e)
    protected = json.loads((mission / "PROTECTED_SET.json").read_text(encoding="utf-8"))["domains"]["stocks"]
    blobs = {}
    for line in git(repo, "ls-tree", "-r", final).splitlines():
        meta, path = line.split("\t", 1)
        blobs[path] = meta.split()[2]
    changed_protected = [e["path"] for e in protected["entries"] if blobs.get(e["path"]) != e["git_blob"]]
    check("(e) every protected item of the stocks domain has the same blob at the final commit",
          changed_protected == [], items=protected["items"], changed=changed_protected)
    # (f)
    runs = json.loads(subprocess.run(["gh", "run", "list", "-R", "leonardosovienski/stocks-predictor", "--commit", final,
                                      "--json", "databaseId,conclusion,status,headSha,url,name,event"],
                                     capture_output=True, text=True, check=True).stdout)
    ci = [r for r in runs if r["name"] == "CI Pipeline"]
    detail = []
    for r in ci:
        jobs = json.loads(subprocess.run(["gh", "run", "view", str(r["databaseId"]), "-R", "leonardosovienski/stocks-predictor",
                                          "--json", "jobs"], capture_output=True, text=True, check=True).stdout)["jobs"]
        detail.append(r | {"jobs": {j["name"]: j["conclusion"] for j in jobs}})
    push_green = [r for r in detail if r["event"] == "push" and r["conclusion"] == "success"]
    check("(f) CI of the domain green on the exact final commit (push run, prompt 9.3)", bool(push_green), runs=detail)
    doc = {"schema": "integration-stocks/CONTRACT_REVALIDATION_STATIC/1", "stage_a_final_commit": STAGE_A,
           "final_commit": final, "authorized_outside_adapter_paths": {
               "C24.3(a)": "versão pré-release (pyproject version, linha do projeto no uv.lock)",
               "D-24 (4)": "arquivos novos em tests/adapters/; recibos R8 novos (.json) e o selo current-operational-evidence.json"},
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
