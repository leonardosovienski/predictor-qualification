"""integration-brasileirao, fase truth-map: ARCHITECTURE_TRUTH_MAP.json e PROTECTED_SET.json (C2, C15.1).

Só leitura (git nos clones com SHA completo; nada é instalado nem executado dos repositórios):
  1. conjunto protegido: para cada domínio, cada item do PROTECTED_SET.json e do FROZEN_VECTORS.json da Etapa A é
     conferido pelo hash do blob git no commit base da Etapa B; item divergente = P0 (C15.1). Mais os artefatos
     compartilhados e os congelados desta missão (sha256).
  2. mapa de verdade: presença e blob de cada componente do circuito da Etapa B na base; fecho estático de imports
     (AST, inclusive imports dentro de funções) a partir de cada console script do cain, para saber o que é
     alcançável (C2 REACHABLE).

Adaptado de qualification/integration-stocks/scripts/truth_map.py: bases dos três domínios nos estados integrados
(cripto ee3d3d1 e stocks 6f857b2 = final_commits das integrações; brasileirao 25cdf4d = runtime_target rc3); cain e
ecosystem = final_commits da integration-stocks; componentes da Etapa B do Brasileirão; o sha256 do dado privado
(lido só para o hash) entra no conjunto protegido.

Uso: python truth_map.py --qualification <checkout> --repos <dir dos clones> --out-dir <qualification/integration-brasileirao> --dataset <cópia do dado>
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
    "crypto": ("cripto-predictor", "ee3d3d17de0b76cf731808243ffa838a0f5ee8cc"),
    "stocks": ("stocks-predictor", "6f857b232eaa63f3fccda6a16f92dbfc8983ab3b"),
    "brasileirao": ("brasileirao-predictor", "25cdf4d9bb309d33f066fbc6a379f5d98c69f08a"),
}
CAIN = "deccaaa0a0e2cb2b5f292614659eb4bf2e943e50"
ECOSYSTEM = "1304b206239d1488fa6a8757364d7571d6c8cf81"
DATA_SHA = "31f30a4dcf33867d1f3aa3d12337a9a66047e6bff10b9a3fa86aae9ef06c9e43"


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
                        "all_equal_at_base": all(i["ok"] for i in items)}
        # Os itens do domínio da missão ficam listados um a um. Os dos outros dois domínios ficam por referência: os
        # arquivos-fonte (PROTECTED_SET.json e FROZEN_VECTORS.json da Etapa A, sha256 acima) já listam cada path e hash
        # de blob, e cada item foi conferido aqui (problems). Copiar os hashes deles fazia o no_data_rows_check
        # acusar um falso positivo dentro de um hash hexadecimal (IB-F003).
        if domain == "brasileirao":
            sets[domain]["entries"] = items
        else:
            sets[domain]["entries_by_reference"] = "cada item dos arquivos em sources, conferido pelo hash do blob"
    shared = []
    for rel in ("qualification/shared/ENVELOPE_V2_FREEZE.json", "qualification/shared/STACK_BASELINE_V2.0.json",
                "qualification/COMMON_QUALIFICATION_CORE.md", "qualification/ATTESTATION_SCHEMA.json",
                "qualification/crypto/runtime_target.json", "qualification/crypto/DOMAIN_RESEARCH_CONTRACT.json",
                "qualification/stocks/DOMAIN_RESEARCH_CONTRACT.json",
                "qualification/brasileirao/DOMAIN_RESEARCH_CONTRACT.json",
                "qualification/crypto/QUALIFICATION_ATTESTATION.json",
                "qualification/stocks/QUALIFICATION_ATTESTATION.json",
                "qualification/brasileirao/QUALIFICATION_ATTESTATION.json",
                "qualification/stocks/runtime_target.json", "qualification/stocks/build_target.json",
                "qualification/stocks/d16/build_real_panel.py", "qualification/stocks/d16/PROTOCOL_REAL.json",
                "qualification/stocks/d16/real_env.py", "qualification/stocks/d16/verify_prefilter.py",
                "qualification/integration-crypto/QUALIFICATION_ATTESTATION.json",
                "qualification/integration-crypto/FROZEN_PARAMETERS.json",
                "qualification/integration-crypto/FROZEN_VECTORS.json",
                "qualification/integration-crypto/FAILURE_MATRIX.json",
                "qualification/integration-crypto/QUALIFICATION_PROFILE_INTEGRATION_CRYPTO_V1.json",
                "qualification/integration-crypto/fixtures/v2/FIXTURES_MANIFEST.json",
                "qualification/integration-stocks/FROZEN_PARAMETERS.json",
                "qualification/integration-stocks/FROZEN_VECTORS.json",
                "qualification/integration-stocks/FAILURE_MATRIX.json",
                "qualification/integration-stocks/QUALIFICATION_PROFILE_INTEGRATION_STOCKS_V1.json",
                "qualification/integration-stocks/QUALIFICATION_ATTESTATION.json",
                "qualification/brasileirao/runtime_target.json", "qualification/brasileirao/scripts/real_env.py",
                "qualification/brasileirao/scripts/no_data_rows_check.py",
                "qualification/brasileirao/scripts/pc2_d16_runtime.sh",
                "qualification/brasileirao/scripts/pc2_windows_runtime.sh",
                "qualification/integration-brasileirao/FROZEN_PARAMETERS.json",
                "qualification/integration-brasileirao/FROZEN_VECTORS.json",
                "qualification/integration-brasileirao/FAILURE_MATRIX.json",
                "qualification/integration-brasileirao/QUALIFICATION_PROFILE_INTEGRATION_BR_V1.json"):
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
    br_tree = ls_tree(repos / "brasileirao-predictor", BASES["brasileirao"][1])
    stocks_tree = ls_tree(repos / "stocks-predictor", BASES["stocks"][1])
    crypto_tree = ls_tree(repos / "cripto-predictor", BASES["crypto"][1])
    eco_tree = ls_tree(repos / "ecosystem-predictor", ECOSYSTEM)
    transport_adapters = show(repos / "ecosystem-predictor", ECOSYSTEM,
                              "packages/research-transport/src/research_transport/adapters.py").decode()
    br_adapters = sorted(p for p in br_tree if p.startswith("brasileirao_predictor/adapters/"))

    def comp(name, repo, tree, path, module, maturity, note):
        return {"component": name, "repo": repo, "path": path, "git_blob": tree.get(path),
                "module": module, "reachable_from_console_scripts": (module in reachable_any) if module else None,
                "maturity_at_base": maturity, "note": note}

    components = [
        comp("TaskOutbox/ResultInbox V2 + episódios por domínio", "cain", cain_tree, "src/cain/orchestration/service.py",
             "cain.orchestration.service", "PROVEN", "HERDADO das integrações crypto e stocks (QUALIFIED); sem mudança"),
        comp("DecisionPolicy genérica + receipt", "cain", cain_tree, "src/cain/orchestration/policy.py",
             "cain.orchestration.policy", "PROVEN", "HERDADO; sem mudança nesta missão (IB-F002: sem regra de holdout)"),
        comp("configuração da DecisionPolicy do cripto", "cain", cain_tree, "src/cain/orchestration/data/crypto.json",
             None, "PROVEN", "HERDADO; não muda"),
        comp("configuração da DecisionPolicy do Stocks", "cain", cain_tree, "src/cain/orchestration/data/stocks.json",
             None, "PROVEN", "HERDADO; não muda"),
        comp("configuração da DecisionPolicy do Brasileirão", "cain", cain_tree,
             "src/cain/orchestration/data/brasileirao.json", None,
             "PRESENT" if "src/cain/orchestration/data/brasileirao.json" in cain_tree else "NOT_PRESENT",
             "criada nesta missão (FROZEN_PARAMETERS -> decision_policy.brasileirao_config)"),
        comp("memória bitemporal com cubo por domínio (PR #45)", "cain", cain_tree, "src/cain/memory/store.py",
             "cain.memory.store", "REACHABLE", "cubo = namespace do domínio (brasileirao)"),
        comp("loop governado (PR #50): execução direta do avaliador", "cain", cain_tree, "src/cain/loop/evaluator.py",
             "cain.loop.evaluator", "IMPLEMENTED", "cercado pela integration-crypto (opção b): fora dos console scripts"),
        comp("leitura de registros por git show (PR #51)", "cain", cain_tree, "src/cain/findings/ingest.py",
             "cain.findings.ingest", "REACHABLE", "só leitura de arquivo versionado num commit fixado"),
        comp("protocolo V2 (release congelada 2.0.0rc2)", "ecosystem-predictor", eco_tree,
             "packages/research-protocol/src/research_protocol/v2/__init__.py", None, "PROVEN", "HERDADO; não muda"),
        comp("transporte (spool) + consumidor por domínio", "ecosystem-predictor", eco_tree,
             "packages/research-transport/src/research_transport/consumer.py", None, "PROVEN",
             "HERDADO para crypto e stocks"),
        {"component": "entrada brasileirao na allowlist fixa do transporte", "repo": "ecosystem-predictor",
         "path": "packages/research-transport/src/research_transport/adapters.py",
         "git_blob": eco_tree.get("packages/research-transport/src/research_transport/adapters.py"),
         "module": None, "reachable_from_console_scripts": None,
         "maturity_at_base": "PRESENT" if '"brasileirao"' in transport_adapters else "NOT_PRESENT",
         "note": "a entrada do Brasileirão é criada nesta missão (só ela)"},
        {"component": "adapter do Brasileirão", "repo": "brasileirao-predictor",
         "path": "brasileirao_predictor/adapters/", "git_blob": {p: br_tree[p] for p in br_adapters},
         "module": None, "reachable_from_console_scripts": None,
         "maturity_at_base": "NOT_PRESENT" if br_adapters == ["brasileirao_predictor/adapters/__init__.py"] else "PRESENT",
         "note": "pacote reservado na Etapa A (só __init__.py); o adapter entra aqui"},
        comp("circuito do Brasileirão (adapter_api Circuit.submit_request/show)", "brasileirao-predictor", br_tree,
             "brasileirao_predictor/research_runtime/runner.py", None, "PROVEN",
             "HERDADO da Etapa A (attestation QUALIFIED a4fa2fee); não reexecutado nesta fase"),
        comp("adapter do cripto (integrado)", "cripto-predictor", crypto_tree,
             "GarimpoInvestimentos/adapters/research_v2.py", None, "PROVEN", "HERDADO da integration-crypto; não muda"),
        comp("adapter do Stocks (integrado)", "stocks-predictor", stocks_tree,
             "stocks_predictor/adapters/research_v2.py", None, "PROVEN", "HERDADO da integration-stocks; não muda"),
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
    ap.add_argument("--dataset", type=Path, required=True)
    a = ap.parse_args()
    prot = protected(a.qualification, a.repos)
    protected_doc = {
        "schema": "integration-brasileirao/PROTECTED_SET/1",
        "phase": "truth-map",
        "identity": "hash do blob git nos commits base da Etapa B (arquivos versionados) ou sha256 (artefatos do "
                    "predictor-qualification)",
        "rule": "C15.1: só cresce; item alterado = P0; PROTECTED_ARTIFACTS_UNCHANGED confere de truth-map até a attestation",
        "domains": prot["sets"],
        "shared": prot["shared"],
        "private_data": {"path": "~/predictors/data/d16/brasileirao/matches_source_copy.sqlite3",
                         "sha256": sha(a.dataset.read_bytes()), "expected": DATA_SHA,
                         "ok": sha(a.dataset.read_bytes()) == DATA_SHA},
        "other_integrations_attestations_rule": "reemissão pela C14 (FROZEN_PARAMETERS -> c14_other_integrations): os "
                                                "bytes atuais continuam iguais em QUALIFICATION_ATTESTATION_superseded_"
                                                "<sha12>.json, apontados por supersedes_sha256",
        "problems_at_truth_map": prot["problems"],
    }
    tmap = {"schema": "integration-brasileirao/ARCHITECTURE_TRUTH_MAP/1", "phase": "truth-map",
            "maturity_scale": "C2: NOT_PRESENT < DECLARED < IMPLEMENTED < INSTANTIATED < REACHABLE < EXERCISED < PROVEN",
            **truth(a.repos)}
    for name, doc in (("PROTECTED_SET.json", protected_doc), ("ARCHITECTURE_TRUTH_MAP.json", tmap)):
        raw = json.dumps(doc, indent=1, ensure_ascii=False).encode() + b"\n"
        (a.out_dir / name).write_bytes(raw)
        print(name, sha(raw))
    summary = {d: {"items": s["items"], "all_equal_at_base": s["all_equal_at_base"]} for d, s in prot["sets"].items()}
    print(json.dumps({"protected": summary, "problems": len(prot["problems"]),
                      "loop_evaluator_reachable": any(c.get("module") == "cain.loop.evaluator"
                                                      and c["reachable_from_console_scripts"]
                                                      for c in tmap["components"])}, indent=1))
    return 1 if prot["problems"] or not protected_doc["private_data"]["ok"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
