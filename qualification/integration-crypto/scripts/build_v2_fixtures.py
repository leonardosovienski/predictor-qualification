"""integration-crypto, freeze-parameters: fixtures V2 congeladas dos três domínios (C9, C18, prompt §4).

Stocks e Brasileirão ainda não estão integrados: CROSS_DOMAIN_ISOLATION, DOMAIN_QUALIFIED_IDS e o N+1 usam
fixtures V2 montadas a partir dos vetores da Etapa A deles, sem rodar os predictors. O mesmo vale para o
conjunto congelado de resultados do Cripto usado pelo N+1.

Para cada domínio:
  1. resultado: o resultado real do E2E da Etapa A, lido do predictor-qualification (caminho + sha256);
  2. pedido: a função ``request`` de ``tests/conformance/fixtures.py`` no final_commit do domínio (lida por
     ``git show`` com o SHA completo; hash do blob conferido contra o FROZEN_VECTORS.json da Etapa A), avaliada
     só com as constantes literais do módulo e o cutoff do resultado; o pedido reconstruído só é aceito se o
     sha256 canônico sem ``client_ref`` for igual ao ``provenance.request_content_hash`` do resultado real;
  3. par V2 da Etapa A (episódio 1): ``build_task`` + ``build_result`` do protocolo congelado 2.0.0rc2;
  4. par V2 ``H9`` (episódio 2), para o teste com o mesmo ``H9`` nos três domínios (C18): o mesmo pedido e o
     mesmo resultado com ``hypothesis_id = <domínio>:H9`` e ``request_id = <domínio>:REQ-ISO-H9-001``
     (derivação declarada no manifesto; os demais bytes do resultado ficam iguais).

Uso: python build_v2_fixtures.py --qualification <checkout do predictor-qualification> --repos <dir dos clones>
                                 --out <dir de saída>
Precisa de ``research_protocol.v2`` (predictor-research-protocol 2.0.0rc2, instalado por tools/uv.lock).
"""

from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import json
import subprocess
from pathlib import Path

import research_protocol.v2 as v2
from importlib.metadata import version

DOMAINS = {
    "crypto": {
        "repo": "cripto-predictor",
        "commit": "341d270e4d709150c581c3cd93f4518d483009eb",
        "vectors_commit_note": "FROZEN_VECTORS.json da Etapa A registra 2bc63eb; o blob de fixtures.py é o mesmo em 341d270",
        "result_file": "qualification/crypto/E2E_EVIDENCE/linux-primary-synthetic/outcome_file.json",
        "result_key": "result",
        "request_args": ("crypto:REQ-E2E-RUNTIME-001",),
        "stubs": {},
    },
    "stocks": {
        "repo": "stocks-predictor",
        "commit": "61fc017256ffea815ae96bbe02b847dccdb395cc",
        "result_file": "qualification/stocks/E2E_EVIDENCE/linux-primary/outcome_file.json",
        "result_key": "result",
        "request_args": ("stocks:REQ-E2E-RUNTIME-001",),
        "stubs": {"cutoff_field": "as_of"},
    },
    "brasileirao": {
        "repo": "brasileirao-predictor",
        "commit": "25cdf4d9bb309d33f066fbc6a379f5d98c69f08a",
        "result_file": "qualification/brasileirao/E2E_EVIDENCE/linux-primary-synthetic/show_2.stdout.json",
        "result_key": "result",
        "request_args": ("brasileirao:REQ-E2E-RUNTIME-001",),
        "stubs": {},
    },
}
FIXTURE_PATH = "tests/conformance/fixtures.py"
CREATED_AT = "2026-09-27T00:00:00Z"


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def git(repo: Path, *args: str) -> bytes:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, check=True).stdout


def load_request_function(source: str, cutoff: str):
    """The fixture's ``request`` function with only its literal module constants and a cutoff stub."""
    tree = ast.parse(source)
    namespace: dict = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            try:
                value = ast.literal_eval(node.value)
            except ValueError:
                continue
            for target in node.targets:
                if isinstance(target, ast.Name):
                    namespace[target.id] = value
                elif isinstance(target, ast.Tuple) and isinstance(value, tuple):
                    for name, item in zip(target.elts, value, strict=True):
                        if isinstance(name, ast.Name):
                            namespace[name.id] = item
    function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "request")
    module = ast.Module(body=[function], type_ignores=[])
    namespace["dataset_object"] = lambda _name: {"data_cutoff": cutoff}
    namespace["panel"] = lambda _name: {"data_cutoff": cutoff}
    exec(compile(module, FIXTURE_PATH, "exec"), namespace)  # noqa: S102 - só literais + a função
    return namespace["request"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--qualification", type=Path, required=True)
    ap.add_argument("--repos", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema": "integration-crypto/V2_FIXTURES/1",
        "protocol": {"package": "predictor-research-protocol", "version": version("predictor-research-protocol"),
                     "registry_sha256": v2.REGISTRY_SHA256},
        "rule": "fixtures congeladas antes de qualquer execução (C15); identidade = sha256 dos bytes canônicos",
        "domains": {},
        "files": {},
    }
    for domain, spec in DOMAINS.items():
        repo = args.repos / spec["repo"]
        result_path = args.qualification / spec["result_file"]
        result_raw = result_path.read_bytes()
        domain_result = json.loads(result_raw)[spec["result_key"]]
        vectors = json.loads((args.qualification / f"qualification/{domain}/FROZEN_VECTORS.json").read_bytes())
        frozen_blob = next(f["git_blob"] for f in vectors["files"] if f["path"] == FIXTURE_PATH)
        blob = git(repo, "rev-parse", f"{spec['commit']}:{FIXTURE_PATH}").decode().strip()
        if blob != frozen_blob:
            raise SystemExit(f"{domain}: blob de {FIXTURE_PATH} {blob} != FROZEN_VECTORS {frozen_blob}")
        source = git(repo, "show", f"{spec['commit']}:{FIXTURE_PATH}").decode("utf-8")
        cutoff = domain_result.get(spec["stubs"].get("cutoff_field", "__none__"))
        request = load_request_function(source, cutoff)(*spec["request_args"])
        request.pop("client_ref", None)
        content = v2.request_content_hash(request)
        expected = domain_result["provenance"]["request_content_hash"]
        if content != expected:
            raise SystemExit(f"{domain}: pedido reconstruído {content} != request_content_hash {expected}")
        adapter = {"distribution": spec["repo"], "module": "fixture:etapa-a-e2e", "version": vectors["commit"][:12]}
        pairs = {}
        h9_request = copy.deepcopy(request) | {"hypothesis_id": f"{domain}:H9", "request_id": f"{domain}:REQ-ISO-H9-001"}
        h9_result = copy.deepcopy(domain_result) | {"hypothesis_id": f"{domain}:H9",
                                                    "request_id": f"{domain}:REQ-ISO-H9-001"}
        previous = None
        for number, (label, req, res) in enumerate(
            (("etapa-a", request, domain_result), ("h9", h9_request, h9_result)), start=1
        ):
            task = v2.build_task(domain, req, episode_id=v2.episode_id_for(domain, number),
                                 proposal_id=f"cain:FIXTURE-{domain.upper()}-{label.upper()}",
                                 created_at=CREATED_AT, previous_task_id=previous)
            outcome = {"status": "RESULT", "exit_code": 0, "request_id": task["request_id"],
                       "client_ref": task["payload"]["client_ref"], "result": res}
            result = v2.build_result(task, outcome, adapter=adapter, produced_at=CREATED_AT)
            previous = task["task_id"]
            for kind, raw in (("task", v2.dumps_task(task)), ("result", v2.dumps_result(result, task=task))):
                name = f"{domain}/{kind}-{label}.json"
                (args.out / domain).mkdir(exist_ok=True)
                (args.out / name).write_bytes(raw)
                manifest["files"][name] = {"sha256": sha256(raw), "bytes": len(raw)}
            pairs[label] = {"task_id": task["task_id"], "episode_id": task["episode_id"],
                            "request_id": task["request_id"], "hypothesis_id": task["hypothesis_id"],
                            "payload_sha256": task["payload_sha256"],
                            "result_payload_sha256": result["result"]["payload_sha256"]}
        manifest["domains"][domain] = {
            "repo": spec["repo"], "commit": spec["commit"], "fixture_blob": blob,
            "note": spec.get("vectors_commit_note"),
            "stage_a_result": {"path": spec["result_file"], "sha256": sha256(result_raw)},
            "request_function": f"{FIXTURE_PATH}::request{spec['request_args']!r}",
            "request_content_hash_verified": content,
            "h9_derivation": "hypothesis_id → <domínio>:H9 e request_id → <domínio>:REQ-ISO-H9-001 no pedido e no "
                             "resultado; nenhum outro campo muda",
            "pairs": pairs,
        }
    raw = json.dumps(manifest, indent=1, ensure_ascii=False, sort_keys=True).encode() + b"\n"
    (args.out / "FIXTURES_MANIFEST.json").write_bytes(raw)
    print(json.dumps({d: m["pairs"] for d, m in manifest["domains"].items()}, indent=1))
    print("manifest_sha256", sha256(raw))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
