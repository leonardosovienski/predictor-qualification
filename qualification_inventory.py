#!/usr/bin/env python3
"""
Inventario de qualificacao (passo 1: DECLARED -> IMPLEMENTED).
Status: TEST_ONLY | ONLY_TESTS_USE | DECORATED? | ORPHAN | REFERENCED
Heuristica por nome (tokens), nao analise de fluxo.
Uso: python qualification_inventory.py [PASTA_DOS_REPOS]
"""
import ast, csv, re, sys
from collections import Counter, defaultdict
from pathlib import Path

SKIP_DIRS = {".venv", "venv", ".git", "__pycache__", "node_modules", "build",
             "dist", ".mypy_cache", ".pytest_cache", ".tox", "site-packages"}
TOKEN = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*\b")
WATCH = {"TaskOutbox", "ResultInbox", "ResearchExecutor", "Episode", "Episodes",
         "DecisionPolicy", "Evaluator"}


def is_test(rel):
    parts = {p.lower() for p in rel.parts[:-1]}
    n = rel.name
    return (bool(parts & {"tests", "test", "testing"}) or n.startswith("test_")
            or n.endswith("_test.py") or n == "conftest.py")


def py_files(repo):
    for p in repo.rglob("*.py"):
        if not SKIP_DIRS & set(p.relative_to(repo).parts) and not any(x.startswith("source_archive") for x in p.relative_to(repo).parts):
            yield p


def main():
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / "dev" / "predictors"
    repos = sorted(d for d in root.iterdir() if d.is_dir() and not d.name.startswith((".", "_")))
    if not repos:
        sys.exit(f"Nenhum repo encontrado em {root}")

    uses = {"src": Counter(), "test": Counter()}
    defs = defaultdict(list)
    for repo in repos:
        for f in py_files(repo):
            rel = f.relative_to(repo)
            side = "test" if is_test(rel) else "src"
            text = f.read_text(encoding="utf-8-sig", errors="replace")
            try:
                tree = ast.parse(text)
            except SyntaxError:
                print(f"[aviso] nao parseou: {repo.name}/{rel}", file=sys.stderr)
                continue
            uses[side].update(TOKEN.findall(text))
            for node in tree.body:
                if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) \
                        and not node.name.startswith("_"):
                    kind = "class" if isinstance(node, ast.ClassDef) else "func"
                    defs[node.name].append((repo.name, kind, str(rel), node.lineno,
                                            side, bool(node.decorator_list)))

    rows = []
    for name, ds in defs.items():
        d_src = sum(1 for d in ds if d[4] == "src")
        d_test = len(ds) - d_src
        r_src = uses["src"][name] - d_src
        r_test = uses["test"][name] - d_test
        for repo, kind, rel, line, side, decorated in ds:
            if side == "test":
                if d_src or name.lower().startswith("test") or kind == "func":
                    continue
                status = "TEST_ONLY"
            elif r_src > 0:
                status = "REFERENCED"
            elif decorated:
                status = "DECORATED?"
            elif r_test > 0:
                status = "ONLY_TESTS_USE"
            else:
                status = "ORPHAN"
            rows.append({"repo": repo, "name": name, "kind": kind, "status": status,
                         "src_refs": max(r_src, 0), "test_refs": max(r_test, 0),
                         "file": rel, "line": line, "watch": name in WATCH})

    if not rows:
        sys.exit("Nenhuma classe/funcao publica encontrada.")
    out = root / "qualification_inventory.csv"
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(sorted(rows, key=lambda r: (r["repo"], r["status"], r["name"])))

    statuses = ["REFERENCED", "ONLY_TESTS_USE", "TEST_ONLY", "DECORATED?", "ORPHAN"]
    print(f"\n{'repo':<26}" + "".join(f"{s:>16}" for s in statuses))
    by_repo = defaultdict(Counter)
    for r in rows:
        by_repo[r["repo"]][r["status"]] += 1
    for repo in sorted(by_repo):
        print(f"{repo:<26}" + "".join(f"{by_repo[repo][s]:>16}" for s in statuses))

    print("\n== Itens vigiados (gaps conhecidos) ==")
    watched = [r for r in rows if r["watch"]]
    if not watched:
        print("  (nenhum encontrado pelo nome)")
    for r in watched:
        print(f"  {r['name']:<20} {r['status']:<15} {r['repo']}/{r['file']}:{r['line']}"
              f"  (src={r['src_refs']}, test={r['test_refs']})")

    print("\n== Classes suspeitas (so existem/sao usadas em teste) ==")
    sus = [r for r in rows if r["kind"] == "class" and r["status"] in ("TEST_ONLY", "ONLY_TESTS_USE")]
    for r in sus[:40]:
        print(f"  {r['status']:<15} {r['repo']}/{r['file']}:{r['line']}  {r['name']}")
    if len(sus) > 40:
        print(f"  ... e mais {len(sus) - 40} (ver CSV)")
    print(f"\nCSV completo: {out}")


if __name__ == "__main__":
    main()

