"""integration-crypto, fase truth-map: ARCHITECTURE_TRUTH_MAP.json e PROTECTED_SET.json (C2, C15.1).

Só leitura (git nos clones com SHA completo; nada é instalado nem executado dos repositórios):
  1. conjunto protegido: para cada domínio, cada item do PROTECTED_SET.json e do FROZEN_VECTORS.json da Etapa A é
     conferido pelo hash do blob git no commit base da Etapa B; item divergente = P0 (C15.1). Mais os artefatos
     compartilhados e os congelados desta missão (sha256).
  2. mapa de verdade: presença e blob de cada componente do circuito da Etapa B na base; fecho estático de imports
     (AST, inclusive imports dentro de funções) a partir de cada console script do cain, para saber o que é
     alcançável (C2 REACHABLE).

Uso: python truth_map.py --qualification <checkout> --repos <dir dos clones> --out-dir <qualification/integration-crypto>
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import subprocess
import tomllib
from collections import deque
from pathlib import Path

BASES = {
    "crypto": ("cripto-predictor", "341d270e4d709150c581c3cd93f4518d483009eb"),
    "stocks": ("stocks-predictor", "61fc017256ffea815ae96bbe02b847dccdb395cc"),
    "brasileirao": ("brasileirao-predictor", "25cdf4d9bb309d33f066fbc6a379f5d98c69f08a"),
}
CAIN = "f343701937a7a798d66e11d2d8aa18e24395e215"
ECOSYSTEM = "49ffb16380d2e91eb7e4a2a936e63ba779c29033"


def run(*args: str) -> str:
    return subprocess.run(list(args), capture_output=True, text=True, check=True).stdout


def ls_tree(repo: Path, commit: str) -> dict[str, str]:
    out = {}
    for line in run("git", "-C", str(repo), "ls-tree", "-r", commit).splitlines():
        meta, path = line.split("\t", 1)
        out[path] = meta.split()[2]
    return out


def show(repo: Path, commit: str, path: str) -> bytes:
    return subprocess.run(["git", "-C", str(repo), "show", f"{commit}:{path}"], capture_output=True, check=True).stdout


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def protected(qual: Path, repos: Path) -> dict:
    sets, problems = {}, []
    for domain, (repo_name, commit) in BASES.items():
        tree = ls_tree(repos / repo_name, commit)
        items = []
        for source in ("PROTECTED_SET.json", "FROZEN_VECTORS.json"):
            raw = (qual / f"qualification/{domain}/{source}").read_bytes()
            doc = json.loads(raw)
            listed = doc.get("items") if source == "PROTECTED_SET.json" else doc.get("files")
            for item in listed:
                current = tree.get(item["path"])
                ok = current == item["git_blob"]
                if not ok:
                    problems.append({"domain": domain, "path": item["path"], "expected": item["git_blob"],
                                     "at_base": current})
                items.append({"path": item["path"], "git_blob": item["git_blob"], "source": source, "ok": ok})
        sets[domain] = {"repo": repo_name, "commit": commit, "items": len(items),
                        "sources": {s: sha((qual / f"qualification/{domain}/{s}").read_bytes())
                                    for s in ("PROTECTED_SET.json", "FROZEN_VECTORS.json")},
                        "all_equal_at_base": all(i["ok"] for i in items), "entries": items}
    shared = []
    for rel in ("qualification/shared/ENVELOPE_V2_FREEZE.json", "qualification/shared/STACK_BASELINE_V2.0.json",
                "qualification/COMMON_QUALIFICATION_CORE.md", "qualification/ATTESTATION_SCHEMA.json",
                "qualification/crypto/runtime_target.json", "qualification/crypto/DOMAIN_RESEARCH_CONTRACT.json",
                "qualification/stocks/DOMAIN_RESEARCH_CONTRACT.json",
                "qualification/brasileirao/DOMAIN_RESEARCH_CONTRACT.json",
                "qualification/crypto/QUALIFICATION_ATTESTATION.json",
                "qualification/stocks/QUALIFICATION_ATTESTATION.json",
                "qualification/brasileirao/QUALIFICATION_ATTESTATION.json",
                "qualification/integration-crypto/FROZEN_PARAMETERS.json",
                "qualification/integration-crypto/FAILURE_MATRIX.json",
                "qualification/integration-crypto/QUALIFICATION_PROFILE_INTEGRATION_CRYPTO_V1.json",
                "qualification/integration-crypto/fixtures/v2/FIXTURES_MANIFEST.json"):
        shared.append({"path": rel, "sha256": sha((qual / rel).read_bytes())})
    return {"sets": sets, "shared": shared, "problems": problems}


def module_graph(repo: Path, commit: str, root: str) -> dict[str, set[str]]:
    edges: dict[str, set[str]] = {}
    for path, _blob in ls_tree(repo, commit).items():
        if not (path.startswith(root + "/") and path.endswith(".py")):
            continue
        parts = path[len("src/"):-3].split("/") if path.startswith("src/") else path[:-3].split("/")
        is_pkg = parts[-1] == "__init__"
        name = ".".join(parts[:-1] if is_pkg else parts)
        base = name.split(".") if is_pkg else name.split(".")[:-1]
        targets: set[str] = set()
        for node in ast.walk(ast.parse(show(repo, commit, path))):
            if isinstance(node, ast.Import):
                targets.update(a.name for a in node.names)
            elif isinstance(node, ast.ImportFrom):
                if node.level:
                    stem = base[: len(base) - (node.level - 1)] if node.level > 1 else base
                    module = ".".join(stem + ([node.module] if node.module else []))
                else:
                    module = node.module or ""
                targets.add(module)
                targets.update(f"{module}.{a.name}" for a in node.names)
        edges[name] = targets
    return edges


def closure(root: str, edges: dict[str, set[str]]) -> set[str]:
    modules = set(edges)

    def resolve(target: str) -> str | None:
        while target:
            if target in modules:
                return target
            target = target.rpartition(".")[0]
        return None

    seen, queue = {root}, deque([root])
    while queue:
        current = queue.popleft()
        parts = current.split(".")
        for target in [".".join(parts[:i]) for i in range(1, len(parts))] + sorted(edges.get(current, ())):
            local = resolve(target)
            if local and local not in seen:
                seen.add(local)
                queue.append(local)
    return seen


def truth(repos: Path) -> dict:
    cain = repos / "cain"
    pyproject = tomllib.loads(show(cain, CAIN, "pyproject.toml").decode())
    edges = module_graph(cain, CAIN, "src/cain")
    reach = {name: sorted(closure(target.split(":")[0], edges))
             for name, target in pyproject["project"]["scripts"].items()}
    reachable_any = set().union(*map(set, reach.values()))
    cain_tree = ls_tree(cain, CAIN)
    crypto_tree = ls_tree(repos / "cripto-predictor", BASES["crypto"][1])
    eco_tree = ls_tree(repos / "ecosystem-predictor", ECOSYSTEM)

    def comp(name, repo, tree, path, module, maturity, note):
        return {"component": name, "repo": repo, "path": path, "git_blob": tree.get(path),
                "module": module, "reachable_from_console_scripts": (module in reachable_any) if module else None,
                "maturity_at_base": maturity, "note": note}

    components = [
        comp("TaskOutbox V1 (HMAC, envelope V1)", "cain", cain_tree, "src/cain/research_tasks.py",
             "cain.research_tasks", "IMPLEMENTED", "só testes; envelope V1 extinto (D-13)"),
        comp("ResultInbox V1", "cain", cain_tree, "src/cain/research_results.py", "cain.research_results",
             "IMPLEMENTED", "só testes"),
        comp("TaskOutbox/ResultInbox V2", "cain", cain_tree, "src/cain/orchestration", None, "NOT_PRESENT",
             "criados nesta missão"),
        comp("DecisionPolicy + `cain research decision-receipt`", "cain", cain_tree, "src/cain/orchestration", None,
             "NOT_PRESENT", "criados nesta missão (C12)"),
        comp("memória bitemporal com cubo por domínio (PR #45)", "cain", cain_tree, "src/cain/memory/store.py",
             "cain.memory.store", "REACHABLE", "`cain memory`; cubo = namespace do domínio"),
        comp("episódios por domínio", "cain", cain_tree, "src/cain/orchestration", None, "NOT_PRESENT",
             "criados nesta missão"),
        comp("loop governado (PR #50): execução direta do avaliador", "cain", cain_tree, "src/cain/loop/evaluator.py",
             "cain.loop.evaluator", "REACHABLE", "CONFLITO com CAIN_CONTAINMENT (IC-F005)"),
        comp("achados por git show num commit fixado (PR #51)", "cain", cain_tree, "src/cain/findings/ingest.py",
             "cain.findings.ingest", "REACHABLE", "`--commit` padrão origin/main (IC-F006)"),
        comp("protocolo V2 (release congelada 2.0.0rc2)", "ecosystem-predictor", eco_tree,
             "packages/research-protocol/src/research_protocol/v2/__init__.py", None, "IMPLEMENTED",
             "sem consumidor no congelamento (ENVELOPE_V2_FREEZE.consumers.v2 = [])"),
        comp("transporte (spool) + consumidor por domínio", "ecosystem-predictor", eco_tree,
             "packages/research-transport", None, "NOT_PRESENT", "SPEC V2 §12: fora da SPEC, criado na Etapa B"),
        comp("adapter do cripto", "cripto-predictor", crypto_tree, "GarimpoInvestimentos/adapters/__init__.py", None,
             "NOT_PRESENT", "pacote reservado e vazio de propósito (Etapa A)"),
        comp("circuito do cripto (adapter_api Circuit.submit_request)", "cripto-predictor", crypto_tree,
             "GarimpoInvestimentos/research_runner.py", None, "PROVEN",
             "HERDADO da Etapa A (attestation QUALIFIED); não reexecutado nesta fase"),
    ]
    return {
        "cain_commit": CAIN,
        "cain_protocol_dependency": [d for d in pyproject["project"]["dependencies"] if "protocol" in d],
        "cain_console_scripts": pyproject["project"]["scripts"],
        "cain_reachable_modules": reach,
        "components": components,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--qualification", type=Path, required=True)
    ap.add_argument("--repos", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    a = ap.parse_args()
    prot = protected(a.qualification, a.repos)
    protected_doc = {
        "schema": "integration-crypto/PROTECTED_SET/1",
        "phase": "truth-map",
        "identity": "hash do blob git nos commits base da Etapa B (arquivos versionados) ou sha256 (artefatos do "
                    "predictor-qualification)",
        "rule": "C15.1: só cresce; item alterado = P0; PROTECTED_ARTIFACTS_UNCHANGED confere de truth-map até a attestation",
        "domains": prot["sets"],
        "shared": prot["shared"],
        "problems_at_truth_map": prot["problems"],
    }
    tmap = {"schema": "integration-crypto/ARCHITECTURE_TRUTH_MAP/1", "phase": "truth-map",
            "maturity_scale": "C2: NOT_PRESENT < DECLARED < IMPLEMENTED < INSTANTIATED < REACHABLE < EXERCISED < PROVEN",
            **truth(a.repos)}
    for name, doc in (("PROTECTED_SET.json", protected_doc), ("ARCHITECTURE_TRUTH_MAP.json", tmap)):
        raw = json.dumps(doc, indent=1, ensure_ascii=False).encode() + b"\n"
        (a.out_dir / name).write_bytes(raw)
        print(name, sha(raw))
    summary = {d: {"items": s["items"], "all_equal_at_base": s["all_equal_at_base"]} for d, s in prot["sets"].items()}
    print(json.dumps({"protected": summary, "problems": len(prot["problems"]),
                      "loop_evaluator_reachable": any(c["module"] == "cain.loop.evaluator"
                                                      and c["reachable_from_console_scripts"]
                                                      for c in tmap["components"])}, indent=1))
    return 1 if prot["problems"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
