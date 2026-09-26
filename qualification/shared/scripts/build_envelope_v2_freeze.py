"""ENVELOPE_V2_FREEZE.json: congelamento do envelope V2 (prompt_preparacao_envelope_v2_rev8.md, item 4).

Tudo é derivado de fonte primária, nunca digitado: bytes no commit do ecosystem-predictor (`git show`),
a release do GitHub (`gh api`, digest do asset e commit da tag), a wheel baixada (sha256 e arquivos
internos), os contratos e attestations no predictor-qualification e os logs brutos em RAW_LOGS (C20).
Qualquer divergência aborta sem gravar. `--check` refaz tudo e compara com o arquivo existente
(ignorando `generated_at`).

Uso:
  python build_envelope_v2_freeze.py --ecosystem CLONE --commit SHA --tag TAG --wheel ARQ.whl
      --qualification WORKTREE [--qualification-rev origin/main] --raw RAW_LOGS/envelope-v2-20260926 --baseline STACK_BASELINE_V2.0.json
      --raw-log LOG --out ENVELOPE_V2_FREEZE.json [--check]
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
import tomllib
import zipfile
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("collect_stack_baseline_v1", HERE / "collect_stack_baseline.py")
v1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(v1)

OWNER = v1.OWNER
CORE_SHA256 = "beaa5feed193356f554922439936ad401c8f177bfd18d8864ca329fae94216fc"
PKG = "packages/research-protocol"
DATA = "research_protocol/v2/data"
SCHEMAS = ("research-task-2.schema.json", "research-result-2.schema.json", "domains.json")
MISSIONS = ("crypto", "brasileirao", "stocks")
RC1 = {"tag": "predictor-research-protocol-v2.0.0rc1", "commit": "fcc005c26bf7b709a3e75f7dce9b68a6baf7bf3c"}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fail(message: str) -> None:
    raise SystemExit(f"FREEZE ABORTADO: {message}")


def tag_commit(r: v1.Runner, repo: str, tag: str) -> str:
    obj = r.gh_api(f"repos/{OWNER}/{repo}/git/ref/tags/{tag}")["object"]
    if obj["type"] == "tag":
        obj = r.gh_api(f"repos/{OWNER}/{repo}/git/tags/{obj['sha']}")["object"]
    return obj["sha"]


def parse_build_log(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    head = re.search(r"^commit=([0-9a-f]{40}) tree=([0-9a-f]{40}) uv=(.+?) SOURCE_DATE_EPOCH=(\d+)$", text, re.M)
    hashes = re.findall(r"^([0-9a-f]{64})  (\S+\.whl)$", text, re.M)
    generators = sorted(set(re.findall(r"^Generator: (.+)$", text, re.M)))
    return {"log": path.name, "log_sha256": sha(path.read_bytes()), "commit": head[1], "package_tree": head[2],
            "uv": head[3], "source_date_epoch": int(head[4]), "outputs": [h for h, _ in hashes],
            "generator": generators, "reproducible": "REPRODUCIBLE=YES" in text}


def parse_suite_log(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    head = re.search(r"^commit=([0-9a-f]{40}) tree=([0-9a-f]{40})", text, re.M)
    runs = re.findall(r"^== python (\S+)\n(\S+) (\S+)\n(\d+) passed(?:, (\d+) \w+)? in", text, re.M)
    return {"log": path.name, "log_sha256": sha(path.read_bytes()), "commit": head[1], "package_tree": head[2],
            "runs": [{"python": full, "package_version": ver, "passed": int(n), "other": int(o or 0)}
                     for _py, full, ver, n, o in runs],
            "exit_ok": "SUITE_EXIT=0" in text}


def parse_diag_log(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    final = re.search(r"^RESULTADO: (OK|FALHOU) \((\d+) checagens\)$", text, re.M)
    return {"log": path.name, "log_sha256": sha(path.read_bytes()), "result": final[1], "checks": int(final[2]),
            "pass": len(re.findall(r"^PASS ", text, re.M)), "fail": len(re.findall(r"^FAIL ", text, re.M))}


def build(args: argparse.Namespace, r: v1.Runner) -> dict:
    eco, q, commit = str(args.ecosystem), str(args.qualification), args.commit
    q_commit = r.git(q, "rev-parse", "--verify", f"{args.qualification_rev}^{{commit}}").strip()
    commit = r.git(eco, "rev-parse", "--verify", f"{commit}^{{commit}}").strip()
    if v1.sha256_bytes(v1.blob_bytes(q, q_commit, "qualification/COMMON_QUALIFICATION_CORE.md")) != CORE_SHA256:
        fail("núcleo diferente da v2.3")
    pyproject = tomllib.loads(v1.blob_bytes(eco, commit, f"{PKG}/pyproject.toml").decode("utf-8"))["project"]
    version = pyproject["version"]
    if not args.tag.endswith(f"-v{version}"):
        fail(f"tag {args.tag} não é da versão {version}")
    # --- release publicada
    release = r.gh_api(f"repos/{OWNER}/ecosystem-predictor/releases/tags/{args.tag}")
    wheels = [a for a in release["assets"] if a["name"].endswith(".whl")]
    if len(wheels) != 1:
        fail(f"release com {len(wheels)} wheels")
    asset = wheels[0]
    digest = asset["digest"].removeprefix("sha256:")
    released_commit = tag_commit(r, "ecosystem-predictor", args.tag)
    if released_commit != commit:
        fail(f"tag {args.tag} aponta para {released_commit}, não para {commit}")
    wheel_bytes = args.wheel.read_bytes()
    if sha(wheel_bytes) != digest or args.wheel.name != asset["name"]:
        fail("wheel baixada difere do asset da release")
    # --- SPEC, schemas e registro: bytes no commit == bytes na wheel
    spec_bytes = v1.blob_bytes(eco, commit, f"{PKG}/SPEC_V2.md")
    schemas = []
    with zipfile.ZipFile(args.wheel) as zf:
        names = sorted(zf.namelist())
        for name in SCHEMAS:
            in_repo = v1.blob_bytes(eco, commit, f"{PKG}/src/{DATA}/{name}")
            in_wheel = zf.read(f"{DATA}/{name}")
            if in_repo != in_wheel:
                fail(f"{name}: bytes da wheel != bytes do commit")
            schemas.append({"path": f"{PKG}/src/{DATA}/{name}", "sha256": sha(in_repo),
                            "git_blob": r.git(eco, "rev-parse", f"{commit}:{PKG}/src/{DATA}/{name}").strip(),
                            "in_wheel": f"{DATA}/{name}"})
        metadata = zf.read(f"predictor_research_protocol-{version}.dist-info/METADATA").decode("utf-8")
        generator = re.search(r"^Generator: (.+)$", zf.read(
            f"predictor_research_protocol-{version}.dist-info/WHEEL").decode("utf-8"), re.M)[1]
    registry = json.loads(v1.blob_bytes(eco, commit, f"{PKG}/src/{DATA}/domains.json"))
    # --- contratos e attestations da Etapa A (main do predictor-qualification)
    contracts = []
    for mission in MISSIONS:
        path = f"qualification/{mission}/DOMAIN_RESEARCH_CONTRACT.json"
        contract_sha = v1.sha256_bytes(v1.blob_bytes(q, q_commit, path))
        att_raw = v1.blob_bytes(q, q_commit, f"qualification/{mission}/QUALIFICATION_ATTESTATION.json")
        att = json.loads(att_raw)
        entry = registry["domains"][mission]
        if entry["contract"]["sha256"] != contract_sha:
            fail(f"{mission}: domains.json cita {entry['contract']['sha256']}, o main tem {contract_sha}")
        if att["result"] != "QUALIFIED" or att["domain_contract_sha256"] != contract_sha:
            fail(f"{mission}: attestation não QUALIFIED ou contrato divergente")
        contracts.append({"domain": mission, "path": path, "sha256": contract_sha,
                          "request_schema_id": entry["request_schema_id"], "result_schema_id": entry["result_schema_id"],
                          "adapter_paths": entry["adapter_paths"],
                          "attestation": {"path": f"qualification/{mission}/QUALIFICATION_ATTESTATION.json",
                                          "sha256": sha(att_raw), "result": att["result"]}})
    # --- evidência bruta (C20)
    raw = args.raw
    builds = [parse_build_log(p) for p in sorted(raw.glob("build_protocol_v2_*.log"))]
    release_build = [b for b in builds if b["commit"] == commit]
    if not release_build or not all(b["reproducible"] and set(b["outputs"]) == {digest} for b in release_build):
        fail("sem build 2× reproduzível do commit da release com o mesmo sha256 do asset")
    suites = [parse_suite_log(p) for p in sorted(raw.glob("suite_protocol_v2_*.log"))]
    if not any(s["commit"] == commit and s["exit_ok"] and len(s["runs"]) == 4 for s in suites):
        fail("sem suíte nos 4 Pythons no commit da release")
    diags = {m: parse_diag_log(raw / f"diag_v2_rc2_{m}.log") for m in MISSIONS}
    if any(d["result"] != "OK" or d["fail"] for d in diags.values()):
        fail("diagnóstico com falha")
    baseline_bytes = args.baseline.read_bytes()
    baseline = json.loads(baseline_bytes)
    if baseline["baseline_id"] != "STACK_BASELINE_V2.0" or not baseline["all_final_wheels_match"]:
        fail("STACK_BASELINE_V2.0 inválido")
    eco_base = next(x for x in baseline["repos"] if x["repo"] == "ecosystem-predictor")["base"]["commit"]
    if eco_base != commit:
        fail(f"STACK_BASELINE_V2.0 usa ecosystem {eco_base}, o freeze usa {commit}")
    rc1_release = r.gh_api(f"repos/{OWNER}/ecosystem-predictor/releases/tags/{RC1['tag']}")
    rc1_digest = next(a["digest"].removeprefix("sha256:") for a in rc1_release["assets"] if a["name"].endswith(".whl"))
    evidence = [{"path": str(p.relative_to(args.qualification)), "sha256": sha(p.read_bytes())}
                for p in sorted(raw.rglob("*")) if p.is_file()]
    return {
        "freeze_id": "ENVELOPE_V2_FREEZE",
        "envelope_version": "V2",
        "common_core_version": "2.3",
        "common_core_sha256": CORE_SHA256,
        "decisions": ["D-4", "D-12", "D-14", "D-22"],
        "mission_prompt": "prompts/prompt_preparacao_envelope_v2_rev8.md",
        "predictor_qualification_commit": q_commit,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "generator": "qualification/shared/scripts/build_envelope_v2_freeze.py",
        "protocol": {
            "package": pyproject["name"], "version": version, "repo": "leonardosovienski/ecosystem-predictor",
            "commit": commit, "tag": args.tag, "tag_commit": released_commit,
            "release_url": release["html_url"], "prerelease": release["prerelease"],
            "wheel": {"name": asset["name"], "url": asset["browser_download_url"], "sha256": digest,
                      "size": asset["size"], "files": names, "generator": generator,
                      "requires_python": re.search(r"^Requires-Python: (.+)$", metadata, re.M)[1]},
            "sdist_published": False,
            "sdist_note": "só a wheel é publicada: o sdist do setuptools não é byte-reproduzível (HYG-001/D-14)",
            "reproducible_builds": release_build,
            "test_suites": [s for s in suites if s["commit"] == commit],
        },
        "spec": {"path": f"{PKG}/SPEC_V2.md", "sha256": sha(spec_bytes),
                 "git_blob": r.git(eco, "rev-parse", f"{commit}:{PKG}/SPEC_V2.md").strip(),
                 "mapping_section": "10. Mapeamento V2 ↔ contrato por domínio (gerado de domains.json)"},
        "schemas": schemas,
        "domain_registry": {"path": f"{PKG}/src/{DATA}/domains.json", "sha256": schemas[2]["sha256"],
                            "source": registry["source"], "domains": sorted(registry["domains"])},
        "domain_contracts": contracts,
        "envelope": {
            "task_schema": "research-task/2", "result_schema": "research-result/2",
            "client_ref_schema": "research-client-ref/2",
            "domain_required": True,
            "episode_id": "<domain>:episode-<n> (task e resultado; o CAIN numera por domínio)",
            "previous_task_id": "null ou <domain>:TASK-<32 hex> do episódio anterior do mesmo domínio",
            "task_id": "<domain>:TASK-sha256(canonical({domain, episode_id, payload_sha256, request_id}))[:32]",
            "hmac_required": False,
        },
        "consumers": {
            "v2": [],
            "note": "nenhum repo consome a V2 no congelamento; o cain usa a V1 1.0.3rc1 e os domínios não dependem do "
                    "protocolo. Consumidores V2 (cain, adapters, transporte) nascem na Etapa B e consomem esta release.",
        },
        "diagnostics_real_outcomes": {"note": "diagnóstico, não evidência de gate", **diags},
        "stack_baseline": {"path": "qualification/shared/STACK_BASELINE_V2.0.json", "sha256": sha(baseline_bytes)},
        "superseded": [{"version": "2.0.0rc1", "tag": RC1["tag"], "commit": RC1["commit"], "wheel_sha256": rc1_digest,
                        "why": "anterior à D-22 (sem correlação por episódio), recusava STATE_BUSY_RETRYABLE real sem "
                               "client_ref e citava o contrato brasileirao e6f98ca2… (rc2 do domínio)"}],
        "change_policy": "mudar o envelope depois deste congelamento = C14 (refazer as fases das integrações que o "
                         "exercitam, inclusive as já QUALIFIED)",
        "evidence": evidence,
        "capital_permission": False,
        "training_started": False,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    for name in ("--ecosystem", "--wheel", "--qualification", "--raw", "--baseline", "--raw-log", "--out"):
        ap.add_argument(name, required=True, type=Path)
    ap.add_argument("--commit", required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--qualification-rev", default="origin/main")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    args.raw_log.parent.mkdir(parents=True, exist_ok=True)
    r = v1.Runner(args.raw_log)
    freeze = build(args, r)
    if args.check:
        current = json.loads(args.out.read_text(encoding="utf-8"))
        current.pop("generated_at"), freeze.pop("generated_at")
        same = current == freeze
        print("FREEZE_CHECK=" + ("OK" if same else "DIVERGE"))
        sys.exit(0 if same else 1)
    args.out.write_text(json.dumps(freeze, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"{args.out}: {freeze['protocol']['version']} {freeze['protocol']['wheel']['sha256']}")


if __name__ == "__main__":
    main()
