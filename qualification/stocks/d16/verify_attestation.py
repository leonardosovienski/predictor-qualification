"""stocks: confere as 8 regras C7.1 da QUALIFICATION_ATTESTATION.json num commit do repositório de evidência.

attest.py confere 1, 2, 3 e 6; aqui também 4 (sha256 de cada final_wheel = asset baixado da URL da release;
final_wheels cobrem todo pacote do stack instalado no runtime — core_identity.json dos runs citados), 5 (um
Linux primary e um Windows secondary), 7 (domain_contract_sha256 = sha256 do contrato no commit) e 8
(supersedes_sha256 aponta para a attestation anterior, se houver) + schema JSON 2020-12 (se jsonschema existir).

Regra 6 (núcleo v2.3, D-22): vale o núcleo vigente quando a attestation foi emitida, desde que seja uma versão do
núcleo no histórico do main. Conferida de dois jeitos: pela tabela CORE_VERSIONS do attest.py no commit (lida por
ast, fonte única, com common_core_version coerente; a tabela precisa conhecer o núcleo do commit) e, sem depender da
tabela, pelas versões reais de COMMON_QUALIFICATION_CORE.md no histórico git até o commit.

Uso: python verify_attestation.py <repo de evidência> <commit> <saída.json>
"""

from __future__ import annotations

import ast
import hashlib
import json
import subprocess
import sys
import urllib.request
from pathlib import Path

CORE_SHA = "50e8f49859daae6dcdf17164781d1837d8b656796924c35060f8d35855ee36e1"
STACK = {"predictor-core", "predictor-ops", "stocks-predictor"}
ATT = "qualification/stocks/QUALIFICATION_ATTESTATION.json"


CORE_PATH = "qualification/COMMON_QUALIFICATION_CORE.md"


def core_versions(attest_source: bytes) -> dict[str, str]:
    """sha256 → versão do núcleo, do CORE_VERSIONS do attest.py (sem importar: o attest.py importa jsonschema)."""
    for node in ast.parse(attest_source.decode("utf-8")).body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "CORE_VERSIONS" for t in node.targets):
            return ast.literal_eval(node.value)
    return {}


def core_history(repo: Path, commit: str) -> set[str]:
    """sha256 de toda versão do núcleo no histórico git até ``commit``."""
    log = subprocess.run(["git", "-C", str(repo), "log", "--format=%H", commit, "--", CORE_PATH],
                         capture_output=True, text=True, check=True).stdout.split()
    return {hashlib.sha256(subprocess.run(["git", "-C", str(repo), "show", f"{sha}:{CORE_PATH}"], capture_output=True,
                                          check=True).stdout).hexdigest() for sha in log}


def core_rule(doc: dict, core_now: str, versions: dict[str, str], history: set[str]) -> dict:
    """C7.1 regra 6 do núcleo v2.3: detalhe da checagem, com ``ok``."""
    emitted = doc["common_core_sha256"]
    detail = {"attestation": emitted, "attestation_version": doc.get("common_core_version"),
              "table_version": versions.get(emitted), "in_git_history": emitted in history,
              "core_at_commit": core_now, "core_at_commit_in_table": core_now in versions}
    detail["ok"] = (detail["in_git_history"] and detail["table_version"] is not None
                    and detail["table_version"] == detail["attestation_version"] and detail["core_at_commit_in_table"])
    return detail


def main() -> int:
    repo, commit, out = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3])

    def show(path: str) -> bytes | None:
        r = subprocess.run(["git", "-C", str(repo), "show", f"{commit}:{path}"], capture_output=True, check=False)
        return r.stdout if r.returncode == 0 else None

    checks = []

    def check(rule: str, ok: bool, **detail) -> None:
        checks.append({"rule": rule, "ok": bool(ok), **detail})

    raw = show(ATT)
    doc = json.loads(raw)
    schema = json.loads(show("qualification/ATTESTATION_SCHEMA.json"))
    try:
        import jsonschema
        jsonschema.Draft202012Validator(schema).validate(doc)
        check("schema", True, validator="jsonschema Draft202012")
    except ModuleNotFoundError:
        check("schema", False, error="jsonschema ausente")
    except Exception as exc:  # noqa: BLE001
        check("schema", False, error=str(exc)[:500])

    findings = json.loads(show("qualification/stocks/FINDINGS.json"))["findings"]
    open_counts = {s: sum(1 for f in findings if f["status"].startswith("OPEN") and f["severity"] == s) for s in ("P0", "P1", "P2")}
    statuses = {g: v["status"] for g, v in doc["gates"].items()}
    blocking = [v["issue_id"] for v in doc["shared_dependency_verdicts"] if v["blocking"]]
    qualified_ok = all(s == "PASS" for s in statuses.values()) and open_counts["P0"] == 0 and open_counts["P1"] == 0 and not blocking
    check("C7.1(1) QUALIFIED ⇔ gates PASS, P0=P1=0, sem veredito bloqueante", (doc["result"] == "QUALIFIED") == qualified_ok,
          result=doc["result"], gates=len(statuses), not_pass=[g for g, s in statuses.items() if s != "PASS"], blocking=blocking)
    check("C7.1(2) counts = FINDINGS abertos", doc["counts"] == open_counts, attestation=doc["counts"], findings=open_counts)
    items = [(f"gate {g}", e) for g, v in doc["gates"].items() for e in v["evidence"]]
    items += [(f"env {e['role']}", ev) for e in doc["environments"] for ev in e["evidence"]]
    items.append(("findings_file", doc["findings_file"]))
    items += [(f"verdict {v['issue_id']}", {"file": v["verdict_file"], "sha256": v["verdict_sha256"]}) for v in doc["shared_dependency_verdicts"]]
    bad = []
    for label, ev in items:
        blob = show(ev["file"])
        if blob is None or hashlib.sha256(blob).hexdigest() != ev["sha256"]:
            bad.append({"where": label, "file": ev["file"], "missing": blob is None})
    check("C7.1(3) toda evidência existe e o sha256 confere no commit", not bad, items=len(items), mismatches=bad)
    wheel_ok = []
    for w in doc["final_wheels"]:
        req = urllib.request.Request(w["url"], headers={"User-Agent": "stocks-qualification-verify/1"})
        with urllib.request.urlopen(req, timeout=120) as resp:
            got = hashlib.sha256(resp.read()).hexdigest()
        wheel_ok.append({"name": w["name"], "version": w["version"], "ok": got == w["sha256"], "observed": got})
    installed = set()
    for label, ev in items:
        if ev["file"].endswith("core_identity.json"):
            data = json.loads(show(ev["file"]))
            installed |= {p["name"] for p in data.get("packages", []) if p["name"] in STACK or p["name"].startswith("predictor-")}
    covered = {w["name"] for w in doc["final_wheels"]}
    check("C7.1(4) final_wheels = assets das releases e cobrem os pacotes do stack instalados",
          all(w["ok"] for w in wheel_ok) and installed <= covered and installed, wheels=wheel_ok,
          installed_stack_packages=sorted(installed), covered=sorted(covered))
    envs = {(e["os"], e["role"]) for e in doc["environments"]}
    check("C7.1(5) Linux primary + Windows secondary", ("linux", "primary") in envs and ("windows", "secondary") in envs,
          environments=[(e["os"], e["role"], e["where"], e["result"]) for e in doc["environments"]])
    core_now = hashlib.sha256(show(CORE_PATH)).hexdigest()
    rule6 = core_rule(doc, core_now, core_versions(show("qualification/stocks/scripts/attest.py") or b""),
                      core_history(repo, commit))
    check("C7.1(6) common_core_sha256 = núcleo vigente na emissão, versão do histórico do main (v2.3)",
          rule6.pop("ok"), **rule6, v2_0=CORE_SHA)
    manifest = show("MANIFEST.sha256")
    if manifest is not None:  # C0.2 (v2.2): schema e núcleo pelo sha256 registrado no MANIFEST do commit
        listed = {}
        for line in manifest.decode("utf-8").splitlines():
            if line.strip():
                digest, name = line.split(None, 1)
                listed[name.lstrip("*").strip()] = digest
        wrong = {name: digest for name, digest in listed.items()
                 if show(name) is None or hashlib.sha256(show(name)).hexdigest() != digest}
        check("C0.2 MANIFEST.sha256 confere (inclui schema e núcleo)", not wrong
              and "qualification/ATTESTATION_SCHEMA.json" in listed, entries=len(listed), wrong=wrong)
    contract = hashlib.sha256(show("qualification/stocks/DOMAIN_RESEARCH_CONTRACT.json")).hexdigest()
    check("C7.1(7) domain_contract_sha256 = contrato no commit", doc["domain_contract_sha256"] == contract,
          attestation=doc["domain_contract_sha256"], contract=contract)
    history = subprocess.run(["git", "-C", str(repo), "log", "--format=%H", commit, "--", ATT], capture_output=True, text=True).stdout.split()
    previous = []
    for h in history[1:]:
        old = subprocess.run(["git", "-C", str(repo), "show", f"{h}:{ATT}"], capture_output=True).stdout
        if old:
            previous.append(hashlib.sha256(old).hexdigest())
    check("C7.1(8) supersedes_sha256 aponta para a anterior (nenhuma = null)",
          (doc["supersedes_sha256"] is None and not [p for p in previous if p != hashlib.sha256(raw).hexdigest()])
          or doc["supersedes_sha256"] in previous, supersedes=doc["supersedes_sha256"], versions_in_history=len(history))
    check("capital_permission=false e training_started=false", doc["capital_permission"] is False and doc["training_started"] is False)
    report = {"commit": commit, "attestation_sha256": hashlib.sha256(raw).hexdigest(), "checks": checks,
              "all_ok": all(c["ok"] for c in checks)}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"all_ok": report["all_ok"], "failed": [c["rule"] for c in checks if not c["ok"]]}, ensure_ascii=False))
    return 0 if report["all_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
