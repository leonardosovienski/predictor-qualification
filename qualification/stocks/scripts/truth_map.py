"""stocks / fase `truth-map`: conjunto protegido e grafo de imports do stocks-predictor.

Adaptado de qualification/crypto/scripts/truth_map.py.

Só leitura do repo (git ls-tree / git show no commit dado; nada é executado do repo).

Saídas:
  * PROTECTED_SET.json: arquivos por hash de blob git no commit, com o motivo
    (glob do prompt ou declaração em documento de freeze).
  * import_graph.json: para cada raiz ([project.scripts], entry-points), a closure
    transitiva de imports (estáticos, relativos, dentro de funções, e módulos que o
    código lança como subprocesso por "-m <módulo>"), e os pacotes externos alcançados.

Uso:
  python truth_map.py protected --repo <clone> --commit <sha> --out PROTECTED_SET.json
  python truth_map.py imports --repo <clone> --commit <sha> --out import_graph.json
           [--forbid research_protocol --forbid cain ...] [--adapter-path <dir> ...]
"""

from __future__ import annotations

import argparse
import ast
import fnmatch
import json
import re
import subprocess
import tomllib
from collections import deque
from pathlib import PurePosixPath

PROMPT_GLOBS = [
    "RESEARCH_FREEZE.md",
    "experiments/BIG_WINNER_*/frozen_signals/**",
    "experiments/BIG_WINNER_IMPROVEMENT_PROGRAM_V1/V2_FINAL_FREEZE.json",
    "experiments/BIG_WINNER_IMPROVEMENT_PROGRAM_V1/V2_SELECTION_FREEZE.yaml",
    "trials.json", "trials_v2.json", "trials.harness_attestation.json",
    "EXTERNAL_INTELLIGENCE_TRIAL_READINESS_MATRIX.json",
    "EXTERNAL_INTELLIGENCE_TRIAL_READINESS_PROTOCOL.json",
    "research/session-20260907/deliverables/historical-protected-integrity.json",
    "research/session-20260907/deliverables/real-integration-protected-integrity.json",
    "research/session-20260907/scripts/verify_history_protected.py",
    "research/session-20260907/scripts/verify_real_protected.py",
]
# "tudo que esses documentos declarem congelado" — cada entrada cita a declaração.
DECLARED = [
    ("stocks_predictor/big_winner_shadow.py", "V2_FINAL_FREEZE.json (implementação) + pyproject.toml: byte-frozen scientific artifact"),
    ("stocks_predictor/big_winner_v2.py", "pyproject.toml: byte-frozen scientific artifact (ruff per-file-ignores)"),
    ("stocks_predictor/prospective_big_winner.py", "V2_FINAL_FREEZE.json + pyproject.toml IMMUTABLE_SCIENTIFIC_ARTIFACT_TYPECHECK_EXCEPTION (frozen V2 receipt)"),
    ("config.yaml", "config.yaml [H1..Hn-FROZEN] + RESEARCH_FREEZE.md §1 (configs preservadas, _frozen_hash)"),
    ("config_rj.yaml", "RESEARCH_FREEZE.md §1 (configs/protocolo RJ preservados)"),
    ("reports/*_verdict*.md", "RESEARCH_FREEZE.md §1: registros de julgamento não reconstituíveis"),
    ("vendor/predictor_core/**", "RESEARCH_FREEZE.md §1/§5: vendor snapshot com CORE_MANIFEST.json"),
    ("docs/research/2026-09-07-h17-observations.jsonl", "RESEARCH_FREEZE.md: ledger de observações H17 preservado"),
    ("experiments/BIG_WINNER_*/frozen_signals/MANIFEST.json", "manifesto dos sinais congelados"),
]


def git(repo: str, *args: str) -> str:
    return subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True,
                          encoding="utf-8", check=True).stdout


def tree(repo: str, commit: str) -> dict[str, str]:
    out = {}
    for line in git(repo, "ls-tree", "-r", commit).splitlines():
        meta, path = line.split("\t", 1)
        out[path] = meta.split()[2]
    return out


def match(path: str, pattern: str) -> bool:
    if pattern.endswith("/**"):
        prefix = pattern[:-3].split("/")
        parts = path.split("/")
        return len(parts) > len(prefix) and fnmatch.fnmatchcase("/".join(parts[: len(prefix)]), "/".join(prefix))
    if "**/" in pattern:
        head, tail = pattern.split("**/", 1)
        return path.startswith(head) and fnmatch.fnmatch(PurePosixPath(path).name, tail)
    return path == pattern or fnmatch.fnmatchcase(path, pattern)


def protected(args) -> None:
    blobs = tree(args.repo, args.commit)
    items = {}
    for pattern in PROMPT_GLOBS:
        for path in blobs:
            if match(path, pattern):
                items.setdefault(path, {"path": path, "git_blob": blobs[path], "reasons": []})
                items[path]["reasons"].append(f"prompt §5: {pattern}")
    for pattern, reason in DECLARED:
        hit = False
        for path in blobs:
            if match(path, pattern):
                hit = True
                items.setdefault(path, {"path": path, "git_blob": blobs[path], "reasons": []})
                items[path]["reasons"].append(f"declarado: {reason}")
        if not hit:
            raise SystemExit(f"padrão declarado sem arquivo no commit: {pattern}")
    doc = {
        "schema": "stocks/PROTECTED_SET/1",
        "repo": "stocks-predictor",
        "commit": args.commit,
        "identity": "hash do blob git (C15.1)",
        "rule": "o conjunto só cresce; item alterado = P0",
        "prompt_globs": PROMPT_GLOBS,
        "declared": [{"pattern": p, "reason": r} for p, r in DECLARED],
        "count": len(items),
        "items": [items[k] for k in sorted(items)],
    }
    with open(args.out, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(doc, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print(f"{args.out}: {len(items)} arquivos protegidos")


def module_of(path: str) -> str:
    parts = list(PurePosixPath(path).with_suffix("").parts)
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


SPAWN = re.compile(r"^(stocks_predictor(?:\.[A-Za-z_][\w]*)+)$")


def imports(args) -> None:
    blobs = tree(args.repo, args.commit)
    pyproject = tomllib.loads(git(args.repo, "show", f"{args.commit}:pyproject.toml"))
    modules = {module_of(p): p for p in blobs if p.startswith("stocks_predictor/") and p.endswith(".py")}
    packages = {module_of(p) for p in blobs if p.endswith("/__init__.py") and p.startswith("stocks_predictor/")}
    edges: dict[str, list[dict]] = {}
    for mod, path in modules.items():
        src = git(args.repo, "show", f"{args.commit}:{path}")
        tree_ = ast.parse(src, filename=path)
        pkg = mod if mod in packages else mod.rsplit(".", 1)[0]
        out = []
        for node in ast.walk(tree_):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    out.append({"target": alias.name, "line": node.lineno, "kind": "import"})
            elif isinstance(node, ast.ImportFrom):
                if node.level:
                    base = pkg.split(".")
                    base = base[: len(base) - (node.level - 1)] if node.level > 1 else base
                    target = ".".join(base + ([node.module] if node.module else []))
                else:
                    target = node.module or ""
                out.append({"target": target, "line": node.lineno, "kind": "from"})
                for alias in node.names:
                    out.append({"target": f"{target}.{alias.name}", "line": node.lineno, "kind": "from-name"})
            elif isinstance(node, ast.Constant) and isinstance(node.value, str) and SPAWN.match(node.value):
                out.append({"target": node.value, "line": node.lineno, "kind": "spawn -m"})
        edges[mod] = out

    def resolve(target: str) -> str | None:
        while target:
            if target in modules:
                return target
            target = target.rsplit(".", 1)[0] if "." in target else ""
        return None

    flat = {m.split(".")[1] for m in modules if m.count(".") == 1}
    roots = {}
    for name, ref in pyproject["project"].get("scripts", {}).items():
        roots[f"[project.scripts] {name}"] = ref.split(":")[0]
    for group, entries in pyproject["project"].get("entry-points", {}).items():
        for name, ref in entries.items():
            roots[f"[entry-points.{group}] {name}"] = ref.split(":")[0]
    for extra in args.root or []:
        roots[f"[extra-root] {extra}"] = extra

    report = {"schema": "stocks/IMPORT_GRAPH/1", "repo": "stocks-predictor", "commit": args.commit,
              "method": "AST de todo .py de stocks_predictor/ no commit (import, from, relativos, dentro de funções; strings 'stocks_predictor.x' usadas em -m contam como aresta spawn); pacotes pais entram na closure",
              "forbidden_external": args.forbid or [], "adapter_paths": args.adapter_path or [], "roots": {}}
    for label, root in roots.items():
        seen, external, parent = {}, {}, {}
        queue = deque([root])
        seen[root] = None
        while queue:
            mod = queue.popleft()
            # pacotes pais são importados antes do módulo
            parts = mod.split(".")
            chain = [".".join(parts[:i]) for i in range(1, len(parts))]
            for step in chain + [e["target"] for e in edges.get(mod, [])]:
                # módulos planos do pacote também são importados sem prefixo quando
                # __package__ é vazio (ex.: `import backtest`, `from config import ...`)
                if step and step.split(".")[0] in flat and not step.startswith("stocks_predictor"):
                    step = "stocks_predictor." + step
                local = resolve(step) if step.startswith("stocks_predictor") else None
                if local:
                    if local not in seen:
                        seen[local] = mod
                        queue.append(local)
                elif not step.startswith("stocks_predictor"):
                    top = step.split(".")[0]
                    if top:
                        external.setdefault(top, mod)
        def path_to(mod):
            out = []
            while mod is not None:
                out.append(mod)
                mod = seen.get(mod)
            return list(reversed(out))
        forbidden_hits = {f: path_to(external[f]) for f in (args.forbid or []) if f in external}
        adapter_hits = [m for m in seen if any(modules[m].startswith(a.rstrip("/") + "/") for a in (args.adapter_path or []))]
        report["roots"][label] = {
            "module": root,
            "closure_size": len(seen),
            "closure": sorted(seen),
            "external_top_level": sorted(external),
            "forbidden_reached": forbidden_hits,
            "adapter_paths_reached": sorted(adapter_hits),
            "components": {c: (path_to(c) if c in seen else None) for c in (args.component or [])},
        }
    with open(args.out, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(report, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    for label, data in report["roots"].items():
        print(label, data["closure_size"], "forbidden:", sorted(data["forbidden_reached"]),
              "components:", {k: bool(v) for k, v in data["components"].items()})


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=("protected", "imports"))
    ap.add_argument("--repo", required=True)
    ap.add_argument("--commit", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--forbid", action="append")
    ap.add_argument("--adapter-path", action="append")
    ap.add_argument("--component", action="append")
    ap.add_argument("--root", action="append")
    args = ap.parse_args()
    (protected if args.mode == "protected" else imports)(args)


if __name__ == "__main__":
    main()
