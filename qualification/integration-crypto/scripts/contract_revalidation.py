"""integration-crypto, fase contract-revalidation (C24.3; DOMAIN_CONTRACTS_PRESERVED), parte estática (a), (b), (e), (f).

  (a) diff do cripto entre o final_commit da Etapa A (341d270) e o final_commit desta missão: só em adapter_paths,
      exceto a versão pré-release (pyproject `version`, `__version__`, a linha da versão do projeto no uv.lock);
      cada linha fora de adapter_paths é conferida;
  (b) regras de adapter_paths no commit final, pelo grafo de imports (AST) dos arquivos do pacote: nada fora de
      GarimpoInvestimentos/adapters/ importa algo de dentro; nenhum console script aponta para dentro (o teste congelado
      da suíte de conformidade roda no cleanroom-final, parte (c));
  (e) conjunto protegido: todo item do PROTECTED_SET.json da missão (domínio crypto) tem o mesmo blob no commit final;
  (f) CI do domínio: run de push no SHA exato do commit final, concluído com success (C21).
As partes (c) e (d) rodam no runtime suportado (cleanroom_final.sh e contract_d.py).

Uso: python contract_revalidation.py <clone do cripto-predictor> <final_commit> <qualification/integration-crypto> <out.json>
"""

from __future__ import annotations

import ast
import json
import subprocess
import sys
import tomllib
from pathlib import Path

# Etapa A vigente do crypto = qualification/crypto/runtime_target.json (V1.2 = 21f8b182 depois da reabertura D-27; antes, 341d270).
STAGE_A = json.loads((Path(__file__).resolve().parents[3] / "qualification" / "crypto" / "runtime_target.json").read_text(encoding="utf-8"))["commit"]
ADAPTERS = "GarimpoInvestimentos/adapters/"


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=True).stdout


def main() -> int:
    repo, final, mission, out = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3]), Path(sys.argv[4])
    checks = []

    def check(name: str, ok: bool, **detail) -> None:
        checks.append({"check": name, "ok": bool(ok), **detail})

    # (a)
    changed = git(repo, "diff", "--name-only", STAGE_A, final).split()
    outside = [p for p in changed if not p.startswith(ADAPTERS)]
    check("(a) files changed outside adapter_paths are only the version files", set(outside) <=
          {"pyproject.toml", "uv.lock", "GarimpoInvestimentos/__init__.py"}, changed=changed)
    for path in outside:
        diff = git(repo, "diff", "--unified=0", STAGE_A, final, "--", path)
        lines = [line for line in diff.splitlines() if line[:1] in "+-" and not line.startswith(("+++", "---"))]
        allowed = {"pyproject.toml": ('version = "1.2.0rc2"', 'version = "1.2.0rc3"'),
                   "uv.lock": ('version = "1.2.0rc2"', 'version = "1.2.0rc3"'),
                   "GarimpoInvestimentos/__init__.py": ('__version__ = "1.2.0rc2"', '__version__ = "1.2.0rc3"')}.get(path, ())
        check(f"(a) {path}: only the pre-release version line changed",
              sorted(line[1:] for line in lines) == sorted(allowed), lines=lines)
    lock_a = tomllib.loads(git(repo, "show", f"{STAGE_A}:uv.lock"))
    lock_f = tomllib.loads(git(repo, "show", f"{final}:uv.lock"))
    strip = lambda lock: [{k: v for k, v in p.items() if not (p["name"] == "cripto-predictor" and k == "version")}  # noqa: E731
                          for p in lock["package"]]
    check("(a) uv.lock identical apart from the project version (no dependency change)", strip(lock_a) == strip(lock_f))
    # (b)
    tree = git(repo, "ls-tree", "-r", "--name-only", final).split()
    offenders = []
    for path in tree:
        if path.startswith("GarimpoInvestimentos/") and path.endswith(".py") and not path.startswith(ADAPTERS):
            for node in ast.walk(ast.parse(git(repo, "show", f"{final}:{path}"))):
                names = []
                if isinstance(node, ast.Import):
                    names = [a.name for a in node.names]
                elif isinstance(node, ast.ImportFrom) and node.module:
                    names = [node.module]
                if any(n == "GarimpoInvestimentos.adapters" or n.startswith("GarimpoInvestimentos.adapters.") for n in names):
                    offenders.append(path)
    check("(b) nothing outside adapter_paths imports from it", offenders == [], offenders=offenders)
    scripts = tomllib.loads(git(repo, "show", f"{final}:pyproject.toml"))["project"]["scripts"]
    check("(b) no console script points into adapter_paths", not any("adapters" in v for v in scripts.values()),
          scripts=scripts)
    # (e)
    protected = json.loads((mission / "PROTECTED_SET.json").read_text(encoding="utf-8"))["domains"]["crypto"]
    blobs = {}
    for line in git(repo, "ls-tree", "-r", final).splitlines():
        meta, path = line.split("\t", 1)
        blobs[path] = meta.split()[2]
    changed_protected = [e["path"] for e in protected["entries"] if blobs.get(e["path"]) != e["git_blob"]]
    check("(e) every protected item of the crypto domain has the same blob at the final commit",
          changed_protected == [], items=protected["items"], changed=changed_protected)
    # (f)
    runs = json.loads(subprocess.run(["gh", "run", "list", "-R", "leonardosovienski/cripto-predictor", "--commit", final,
                                      "--event", "push", "--json", "databaseId,conclusion,status,headSha,url,name"],
                                     capture_output=True, text=True, check=True).stdout)
    ci = [r for r in runs if r["name"] == "CI"]
    check("(f) CI of the domain green on the exact final commit (push run)", bool(ci) and all(
        r["headSha"] == final and r["status"] == "completed" and r["conclusion"] == "success" for r in ci), runs=ci)
    doc = {"schema": "integration-crypto/CONTRACT_REVALIDATION_STATIC/1", "stage_a_final_commit": STAGE_A,
           "final_commit": final, "checks": checks, "passed": sum(c["ok"] for c in checks),
           "failed": sum(not c["ok"] for c in checks)}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({k: doc[k] for k in ("final_commit", "passed", "failed")}))
    return 0 if doc["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
