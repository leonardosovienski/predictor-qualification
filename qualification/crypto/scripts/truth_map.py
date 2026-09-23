"""crypto / fase `truth-map`: conjunto protegido e grafo de imports do cripto-predictor.

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
    "charters/**", "observation_plans/**", "observation_reports/**",
    "CR_RESEARCH_FREEZE.md", "CR_FREEZE_INDEX.md", "docs/EVIDENCE_REGISTRY.md",
    "docs/HYPOTHESES.md", "docs/case_studies/**", "docs/evidence/**/*freeze*.json",
]
# "tudo que esses documentos declarem congelado" — cada entrada cita a declaração.
DECLARED = [
    ("GarimpoInvestimentos/dpl/**", "CR_RESEARCH_FREEZE.md preserved_components"),
    ("GarimpoInvestimentos/analyzers/pbo.py", "CR_RESEARCH_FREEZE.md preserved_components"),
    ("GarimpoInvestimentos/analyzers/gate_power.py", "CR_RESEARCH_FREEZE.md preserved_components"),
    ("GarimpoInvestimentos/v3/costs.py", "CR_RESEARCH_FREEZE.md preserved_components; costs.py docstring (mudança exige trial nova)"),
    ("GarimpoInvestimentos/trading/cost_policy.py", "CR_RESEARCH_FREEZE.md preserved_components"),
    ("GarimpoInvestimentos/trading/costs.py", "CR_RESEARCH_FREEZE.md archived_components"),
    ("GarimpoInvestimentos/trials.json", "CR_RESEARCH_FREEZE.md archived_components; HYPOTHESES.md (trials byte-idênticos)"),
    ("GarimpoInvestimentos/trials.harness_attestation.json", "CR_FREEZE_INDEX.md §8 atestado"),
    ("GarimpoInvestimentos/trials.phase1_harness_attestation.json", "CR_FREEZE_INDEX.md §8 atestado"),
    ("GarimpoInvestimentos/h6_status.json", "CR_FREEZE_INDEX.md §7; HYPOTHESES.md (h6_status byte-idêntico)"),
    ("GarimpoInvestimentos/profit_recovery_v1.py", "pyproject.toml: bytes congelados por docs/continuity_20260919/BASELINE_V1.json"),
    ("docs/continuity_20260919/BASELINE_V1.json", "fixa measurement_module_sha256"),
    ("scripts/attest_harness.py", "CR_RESEARCH_FREEZE.md preserved_components"),
    ("scripts/check_reopen_dossier.py", "CR_RESEARCH_FREEZE.md preserved_components (portão de reabertura)"),
    ("scripts/freeze_h6_definition.py", "CR_RESEARCH_FREEZE.md reopen_policy (hash de definição H6)"),
    ("docs/ADR-014_modelo_bitemporal.md", "CR_RESEARCH_FREEZE.md preserved_components"),
    ("docs/ADR-015_experiment_registry_e_trava_de_poder.md", "CR_RESEARCH_FREEZE.md preserved_components"),
    ("docs/H5_ACOMPANHAMENTO_2026-07-25.md", "CR_RESEARCH_FREEZE.md preserved_components"),
    ("docs/H6_REFREEZE_2026-08-27.md", "CR_RESEARCH_FREEZE.md preserved_components"),
    ("docs/TRADING_LAYER_INVENTORY.md", "CR_RESEARCH_FREEZE.md preserved_components"),
    ("tests/test_v3_wfa_purge_contract.py", "CR_RESEARCH_FREEZE.md preserved_components"),
    ("tests/test_permutation_placebo_control.py", "CR_RESEARCH_FREEZE.md preserved_components"),
    ("docs/evidence/**", "EVIDENCE_REGISTRY.md: evidência das claims formais"),
    ("docs/open_source_research/20260911T0233/**", "ci.yml: bytes congelados (git diff --exit-code 39b0f57)"),
    ("docs/open_source_research/20260911T0525/**", "ci.yml: bytes congelados (git diff --exit-code 39b0f57)"),
    (".gitattributes", "SESSION_HANDOFF_20260908.md: .gitattributes preserva os bytes congelados"),
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
        return path.startswith(pattern[:-3] + "/")
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
        "schema": "crypto/PROTECTED_SET/1",
        "repo": "cripto-predictor",
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


SPAWN = re.compile(r"^(GarimpoInvestimentos(?:\.[A-Za-z_][\w]*)+)$")


def imports(args) -> None:
    blobs = tree(args.repo, args.commit)
    pyproject = tomllib.loads(git(args.repo, "show", f"{args.commit}:pyproject.toml"))
    modules = {module_of(p): p for p in blobs if p.startswith("GarimpoInvestimentos/") and p.endswith(".py")}
    packages = {module_of(p) for p in blobs if p.endswith("/__init__.py") and p.startswith("GarimpoInvestimentos/")}
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

    roots = {}
    for name, ref in pyproject["project"].get("scripts", {}).items():
        roots[f"[project.scripts] {name}"] = ref.split(":")[0]
    for group, entries in pyproject["project"].get("entry-points", {}).items():
        for name, ref in entries.items():
            roots[f"[entry-points.{group}] {name}"] = ref.split(":")[0]
    for extra in args.root or []:
        roots[f"[extra-root] {extra}"] = extra

    report = {"schema": "crypto/IMPORT_GRAPH/1", "repo": "cripto-predictor", "commit": args.commit,
              "method": "AST de todo .py de GarimpoInvestimentos/ no commit (import, from, relativos, dentro de funções; strings 'GarimpoInvestimentos.x' usadas em -m contam como aresta spawn); pacotes pais entram na closure",
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
                local = resolve(step) if step.startswith("GarimpoInvestimentos") else None
                if local:
                    if local not in seen:
                        seen[local] = mod
                        queue.append(local)
                elif not step.startswith("GarimpoInvestimentos"):
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
