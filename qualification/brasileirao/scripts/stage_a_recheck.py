"""brasileirao: a Etapa A se sustenta? Reconferência independente do que o main afirma (noite D-16, PC 2).

Sem rede e sem editar nada. Confere, a partir da árvore do repositório de evidência:
  * GATES.json: estado de cada gate e toda evidência citada (gates, environments, veredictos
    compartilhados) existe; sha256 atual = sha256 gravado no último ATTESTATION_PARTIAL (C7.1 regra 3);
  * hashes de identidade do último parcial (núcleo, baseline comum, FROZEN_PARAMETERS, PROTECTED_SET,
    FROZEN_VECTORS, perfil do soak, FINDINGS) e domain_contract_sha256 = contrato no main. O núcleo segue a
    C7.1 regra 6 do núcleo v2.3: vale o núcleo vigente quando o parcial foi emitido, se for uma versão do
    histórico (tabela CORE_VERSIONS do attest.py), com common_core_version coerente;
  * counts do parcial = achados abertos em FINDINGS.json (C7.1 regra 2);
  * FROZEN_VECTORS.json: blob git e sha256 de cada arquivo no commit final do brasileirao-predictor;
  * final_commits existem nos clones locais; runtime_target.json = final_wheels do GATES.json;
  * uv.lock e constraints/shared-wheels.sha256 do commit final apontam as mesmas wheels (URL + sha256)
    de Core e Ops declaradas em final_wheels;
  * wheels baixadas (--wheels): sha256 = final_wheels[*].sha256.

Uso: python stage_a_recheck.py --root <worktree da evidência> --br-repo <clone> --core-repo <clone>
         --ops-repo <clone> --wheels <dir com as wheels baixadas> --out <json>
Exit 1 se houver divergência.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import subprocess
import tomllib
from pathlib import Path

OPEN = {"OPEN", "OPEN_AWAITING_VERDICT", "OPEN_BLOCKED"}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def core_versions() -> dict[str, str]:
    """sha256 → versão do núcleo, lido do CORE_VERSIONS do attest.py (fonte única, sem importar o jsonschema)."""
    tree = ast.parse((Path(__file__).resolve().parent / "attest.py").read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "CORE_VERSIONS" for t in node.targets):
            return ast.literal_eval(node.value)
    raise SystemExit("CORE_VERSIONS ausente no attest.py")


def git(repo: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", repo, *args], capture_output=True, check=False)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, required=True)
    ap.add_argument("--br-repo", required=True)
    ap.add_argument("--core-repo", required=True)
    ap.add_argument("--ops-repo", required=True)
    ap.add_argument("--wheels", type=Path, required=True)
    ap.add_argument("--partial", default="ATTESTATION_PARTIAL_attestation.json")
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    root = args.root.resolve()
    qc = root / "qualification" / "brasileirao"
    ledger = json.loads((qc / "GATES.json").read_text(encoding="utf-8"))
    partial = json.loads((qc / args.partial).read_text(encoding="utf-8"))
    problems: list[str] = []
    report: dict = {"schema": "brasileirao/STAGE_A_RECHECK/1", "partial": args.partial,
                    "partial_generated_at": partial.get("generated_at"), "partial_result": partial.get("result")}

    # 1) gates: status and evidence (existence + sha256 against the latest partial)
    status_count: dict[str, int] = {}
    evidence_rows = []
    for gate, state in ledger["gates"].items():
        status_count[state["status"]] = status_count.get(state["status"], 0) + 1
        recorded = {e["file"]: e["sha256"] for e in partial["gates"].get(gate, {}).get("evidence", [])}
        if partial["gates"].get(gate, {}).get("status") != state["status"]:
            problems.append(f"gate {gate}: status GATES.json={state['status']} parcial={partial['gates'].get(gate, {}).get('status')}")
        for item in state.get("evidence", []):
            path = root / item
            row = {"gate": gate, "file": item, "exists": path.is_file()}
            if not row["exists"]:
                problems.append(f"gate {gate}: evidência ausente {item}")
            else:
                row["sha256"] = sha(path)
                row["partial_sha256"] = recorded.get(item)
                row["match"] = row["sha256"] == recorded.get(item)
                if not row["match"]:
                    problems.append(f"gate {gate}: sha256 divergente {item}")
            evidence_rows.append(row)
    report["gate_status_count"] = status_count
    report["gates_not_pass"] = {g: s["status"] for g, s in ledger["gates"].items() if s["status"] != "PASS"}
    report["gate_evidence"] = {"files": len(evidence_rows), "missing": sum(1 for r in evidence_rows if not r["exists"]),
                               "sha_mismatch": sum(1 for r in evidence_rows if r["exists"] and not r["match"]),
                               "rows": evidence_rows}

    # 2) environments and shared verdicts
    env_rows = []
    recorded_envs = {(e["os"], e["role"]): {x["file"]: x["sha256"] for x in e["evidence"]} for e in partial.get("environments", [])}
    for env in ledger.get("environments", []):
        for item in env.get("evidence", []):
            path = root / item
            ok = path.is_file() and sha(path) == recorded_envs.get((env["os"], env["role"]), {}).get(item)
            env_rows.append({"env": f"{env['os']}/{env['role']}/{env['where']}", "result": env["result"], "file": item, "ok": ok})
            if not ok:
                problems.append(f"environment {env['os']}/{env['role']}: evidência ausente ou divergente {item}")
    report["environments"] = env_rows
    verdict_rows = []
    recorded_verdicts = {v["issue_id"]: v for v in partial.get("shared_dependency_verdicts", [])}
    for v in ledger.get("shared_dependency_verdicts", []):
        path = root / v["verdict_file"]
        actual = sha(path) if path.is_file() else None
        ok = actual is not None and actual == recorded_verdicts.get(v["issue_id"], {}).get("verdict_sha256")
        verdict_file = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
        verdict_rows.append({"issue_id": v["issue_id"], "file": v["verdict_file"], "ok": ok, "blocking_ledger": v["blocking"],
                             "blocking_file": verdict_file.get("blocking"), "classification_file": verdict_file.get("classification")})
        if not ok:
            problems.append(f"veredito {v['issue_id']}: ausente ou divergente")
        if verdict_file.get("blocking") not in (None, v["blocking"]):
            problems.append(f"veredito {v['issue_id']}: blocking no arquivo difere do GATES.json")
    report["shared_verdicts"] = verdict_rows

    # 3) identity hashes of the latest partial
    identity = {
        "common_core_sha256": root / "qualification" / "COMMON_QUALIFICATION_CORE.md",
        "common_baseline_sha256": root / "qualification" / "shared" / f"{partial['common_baseline_id']}.json",
        "frozen_parameters_sha256": qc / "FROZEN_PARAMETERS.json",
        "protected_set_sha256": qc / "PROTECTED_SET.json",
        "frozen_vectors_sha256": qc / "FROZEN_VECTORS.json",
        "soak_profile_sha256": qc / "QUALIFICATION_PROFILE_BR_V1.json",
        "domain_contract_sha256": qc / "DOMAIN_RESEARCH_CONTRACT.json",
    }
    id_rows = {}
    versions = core_versions()
    for key, path in identity.items():
        actual = sha(path)
        id_rows[key] = {"partial": partial.get(key), "actual": actual, "match": actual == partial.get(key)}
        if key == "common_core_sha256":
            # C7.1 regra 6 (núcleo v2.3): vale o núcleo vigente na emissão, desde que seja do histórico
            row = id_rows[key]
            row["in_history"] = partial.get(key) in versions
            row["version"] = versions.get(partial.get(key))
            if actual not in versions:
                problems.append(f"common_core_sha256: núcleo atual {actual} fora do CORE_VERSIONS do attest.py")
            if not row["in_history"]:
                problems.append(f"common_core_sha256: parcial {partial.get(key)} fora do histórico do núcleo")
            elif partial.get("common_core_version") != row["version"]:
                problems.append(f"common_core_version: parcial {partial.get('common_core_version')} != {row['version']}")
            continue
        if actual != partial.get(key):
            problems.append(f"{key}: parcial {partial.get(key)} != atual {actual}")
    if ledger.get("domain_contract_sha256") != id_rows["domain_contract_sha256"]["actual"]:
        problems.append("domain_contract_sha256 do GATES.json != contrato no main")
    findings_actual = sha(qc / "FINDINGS.json")
    id_rows["findings_file"] = {"partial": partial["findings_file"]["sha256"], "actual": findings_actual,
                                "match": findings_actual == partial["findings_file"]["sha256"]}
    if not id_rows["findings_file"]["match"]:
        problems.append("FINDINGS.json difere do parcial")
    report["identity_hashes"] = id_rows
    findings = json.loads((qc / "FINDINGS.json").read_text(encoding="utf-8"))["findings"]
    counts = {"P0": 0, "P1": 0, "P2": 0}
    for f in findings:
        if f["status"] in OPEN:
            counts[f["severity"]] += 1
    report["open_findings"] = counts
    if counts != partial["counts"]:
        problems.append(f"counts do parcial {partial['counts']} != FINDINGS.json {counts}")
    report["capital_permission"] = partial.get("capital_permission")
    report["training_started"] = partial.get("training_started")
    if partial.get("capital_permission") is not False or partial.get("training_started") is not False:
        problems.append("capital_permission/training_started diferente de false")

    # 4) final commits exist; frozen vectors against the final commit
    repos = {"brasileirao-predictor": args.br_repo, "core-predictor": args.core_repo, "predictor-ops": args.ops_repo}
    commit_rows = []
    for fc in ledger["final_commits"]:
        done = git(repos[fc["repo"]], "cat-file", "-t", fc["commit_sha"])
        ok = done.returncode == 0 and done.stdout.decode().strip() == "commit"
        commit_rows.append({"repo": fc["repo"], "commit": fc["commit_sha"], "exists": ok})
        if not ok:
            problems.append(f"commit ausente {fc['repo']} {fc['commit_sha']}")
    report["final_commits"] = commit_rows
    br_commit = next(fc["commit_sha"] for fc in ledger["final_commits"] if fc["repo"] == "brasileirao-predictor")
    vectors = json.loads((qc / "FROZEN_VECTORS.json").read_text(encoding="utf-8"))
    vec_rows = []
    if vectors["commit"] != br_commit:
        problems.append("FROZEN_VECTORS.commit != final_commit do brasileirao-predictor")
    for item in vectors["files"]:
        blob = git(args.br_repo, "rev-parse", f"{br_commit}:{item['path']}").stdout.decode().strip()
        body = git(args.br_repo, "show", f"{br_commit}:{item['path']}").stdout
        ok = blob == item["git_blob"] and hashlib.sha256(body).hexdigest() == item["sha256"]
        vec_rows.append({"path": item["path"], "ok": ok})
        if not ok:
            problems.append(f"vetor congelado divergente {item['path']}")
    report["frozen_vectors"] = vec_rows

    # 5) runtime_target.json, uv.lock and shared-wheels constraints of the final commit
    target = json.loads((qc / "runtime_target.json").read_text(encoding="utf-8"))
    wheels = {w["name"]: w for w in ledger["final_wheels"]}
    rt_checks = {
        "commit": target["commit"] == br_commit,
        "br_wheel_url": target["wheel_url"] == wheels["brasileirao-predictor"]["url"],
        "br_wheel_sha256": target["wheel_sha256"] == wheels["brasileirao-predictor"]["sha256"],
        "core_sha256": target["stack"]["predictor-core"]["sha256"] == wheels["predictor-core"]["sha256"],
        "ops_sha256": target["stack"]["predictor-ops"]["sha256"] == wheels["predictor-ops"]["sha256"],
        "ops_commit": target["stack"]["predictor-ops"]["commit"] == next(fc["commit_sha"] for fc in ledger["final_commits"] if fc["repo"] == "predictor-ops"),
    }
    lock = tomllib.loads(git(args.br_repo, "show", f"{br_commit}:uv.lock").stdout.decode("utf-8"))
    pyproject = tomllib.loads(git(args.br_repo, "show", f"{br_commit}:pyproject.toml").stdout.decode("utf-8"))
    for pkg in lock["package"]:
        if pkg["name"] in ("predictor-core", "predictor-ops"):
            w = pkg["wheels"][0]
            rt_checks[f"lock_{pkg['name']}_url"] = w["url"] == wheels[pkg["name"]]["url"]
            rt_checks[f"lock_{pkg['name']}_sha256"] = w["hash"].removeprefix("sha256:") == wheels[pkg["name"]]["sha256"]
        if pkg["name"] == "brasileirao-predictor":
            rt_checks["lock_project_version"] = pkg["version"] == wheels["brasileirao-predictor"]["version"]
    rt_checks["pyproject_version"] = pyproject["project"]["version"] == wheels["brasileirao-predictor"]["version"]
    constraint = git(args.br_repo, "show", f"{br_commit}:constraints/shared-wheels.sha256").stdout.decode()
    for name in ("predictor-core", "predictor-ops"):
        rt_checks[f"constraints_{name}"] = f"{wheels[name]['sha256']}  {wheels[name]['url'].rsplit('/', 1)[1]}" in constraint
    report["runtime_target_and_lock"] = rt_checks
    problems += [f"runtime_target/lock: {k}" for k, v in rt_checks.items() if not v]

    # 6) downloaded wheels
    wheel_rows = []
    for w in ledger["final_wheels"]:
        path = args.wheels / w["url"].rsplit("/", 1)[1]
        actual = sha(path) if path.is_file() else None
        wheel_rows.append({"name": w["name"], "version": w["version"], "url": w["url"], "expected": w["sha256"],
                           "downloaded_sha256": actual, "match": actual == w["sha256"]})
        if actual != w["sha256"]:
            problems.append(f"wheel {w['name']}: sha256 baixado {actual} != {w['sha256']}")
    report["final_wheels"] = wheel_rows

    report["problems"] = problems
    report["verdict"] = "OK" if not problems else "DIVERGENCE"
    args.out.write_text(json.dumps(report, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"verdict": report["verdict"], "problems": problems, "gate_status_count": status_count,
                      "evidence_files": report["gate_evidence"]["files"]}, ensure_ascii=False))
    return 0 if not problems else 1


if __name__ == "__main__":
    raise SystemExit(main())
