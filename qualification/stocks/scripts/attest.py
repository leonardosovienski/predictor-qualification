"""stocks: gera e confere ATTESTATION_PARTIAL_<phase>.json / QUALIFICATION_ATTESTATION.json.

Fonte única dos estados de gate: qualification/stocks/GATES.json (editado a cada fase,
cada gate com status, evidências por caminho e nota). Este script:
  * calcula os sha256 das evidências (arquivo tem de existir);
  * conta P0/P1/P2 abertos em FINDINGS.json (C7.1 regra 2);
  * valida contra qualification/ATTESTATION_SCHEMA.json (JSON Schema 2020-12);
  * confere as regras C7.1 que dá para conferir localmente (1, 2, 3, 6);
  * nunca sobrescreve um parcial existente (C8).

Uso:
  python attest.py partial <phase>
  python attest.py final            (só depois de contract-sign-off)
  python attest.py check <arquivo>  (revalida um arquivo emitido)
"""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import jsonschema  # validado no Actions (stocks-evidence-check.yml); no Windows local nada é instalado (D-1)
except ModuleNotFoundError:  # pragma: no cover
    jsonschema = None

ROOT = Path(__file__).resolve().parents[3]
QC = ROOT / "qualification" / "stocks"
CORE = ROOT / "qualification" / "COMMON_QUALIFICATION_CORE.md"
SCHEMA = ROOT / "qualification" / "ATTESTATION_SCHEMA.json"
V1 = ROOT / "qualification" / "shared" / "STACK_BASELINE_V1.json"
# C7.1 regra 6 (núcleo v2.3, D-22): a attestation vale no núcleo em que foi emitida, desde que seja uma versão
# do núcleo no histórico do main. Versão nova do núcleo entra nesta tabela; sem isso, build() falha fechado.
CORE_VERSIONS = {
    "50e8f49859daae6dcdf17164781d1837d8b656796924c35060f8d35855ee36e1": "2.0",
    "a3b4b7bbae9a4419b64b087fd6fd74b91e5a7ffa5860bfe962132b0ddb0a0c9b": "2.1",
    "d681e423499e202c735ee1f110311a9721019ef11e21ae824f4791bada7c7d2c": "2.2",
    "beaa5feed193356f554922439936ad401c8f177bfd18d8864ca329fae94216fc": "2.3",
}
OPEN = {"OPEN", "OPEN_AWAITING_VERDICT", "OPEN_BLOCKED"}
SKIP_SCHEMA_OK = "--no-schema" in sys.argv


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def core_version() -> str:
    version = CORE_VERSIONS.get(sha(CORE))
    if version is None:
        raise SystemExit("C7.1(6): o núcleo vigente não está em CORE_VERSIONS; acrescente a versão nova (D-22)")
    return version


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def evidence(paths: list[str]) -> list[dict]:
    out = []
    for item in paths:
        path = ROOT / item
        if not path.is_file():
            raise SystemExit(f"evidência ausente: {item}")
        out.append({"file": item, "sha256": sha(path)})
    return out


def optional_sha(name: str) -> str | None:
    path = QC / name
    return sha(path) if path.is_file() else None


def counts() -> dict:
    findings = json.loads((QC / "FINDINGS.json").read_text(encoding="utf-8"))["findings"]
    result = {"P0": 0, "P1": 0, "P2": 0}
    for item in findings:
        if item["status"] in OPEN:
            result[item["severity"]] += 1
    return result


def build(result: str) -> dict:
    ledger = json.loads((QC / "GATES.json").read_text(encoding="utf-8"))
    gates = {}
    for gate, state in ledger["gates"].items():
        entry = {"status": state["status"], "evidence": evidence(state.get("evidence", []))}
        if state.get("note"):
            entry["note"] = state["note"]
        gates[gate] = entry
    environments = []
    for env in ledger.get("environments", []):
        environments.append({**{k: env[k] for k in ("os", "python", "role", "where", "result")},
                             "evidence": evidence(env.get("evidence", []))})
    verdicts = []
    for v in ledger.get("shared_dependency_verdicts", []):
        verdicts.append({**v, "verdict_sha256": sha(ROOT / v["verdict_file"])})
    return {
        "attestation_version": "2.0",
        "stage": "A",
        "branch": "stocks",
        "envelope_version": "NONE",
        "supersedes_sha256": ledger.get("supersedes_sha256"),
        "common_baseline_id": ledger["common_baseline_id"],
        "common_baseline_sha256": sha(ROOT / "qualification" / "shared" / (ledger["common_baseline_id"] + ".json")),
        "common_core_version": core_version(),
        "common_core_sha256": sha(CORE),
        "frozen_parameters_sha256": sha(QC / "FROZEN_PARAMETERS.json"),
        "protected_set_sha256": optional_sha("PROTECTED_SET.json"),
        "frozen_vectors_sha256": optional_sha("FROZEN_VECTORS.json"),
        "soak_profile_sha256": optional_sha("QUALIFICATION_PROFILE_STOCKS_V1.json"),
        "domain_contract_sha256": ledger.get("domain_contract_sha256"),
        "domain_attestations": [],
        "final_commits": ledger.get("final_commits", []),
        "final_wheels": ledger.get("final_wheels", []),
        "phases_completed": ledger["phases_completed"],
        "environments": environments,
        "shared_dependency_verdicts": verdicts,
        "gates": gates,
        "findings_file": evidence(["qualification/stocks/FINDINGS.json"])[0],
        "counts": counts(),
        "capital_permission": False,
        "training_started": False,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "result": result,
    }


def check(doc: dict) -> list[str]:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    if jsonschema is not None:
        jsonschema.Draft202012Validator(schema).validate(doc)
    elif not SKIP_SCHEMA_OK:
        raise SystemExit('jsonschema ausente: rode no Actions ou com --no-schema (validação no stocks-evidence-check.yml)')
    problems = []
    if doc["common_core_sha256"] not in CORE_VERSIONS:
        problems.append("C7.1(6): common_core_sha256 não é uma versão do núcleo no histórico do main")
    if doc["counts"] != counts():
        problems.append("C7.1(2): counts não bate com FINDINGS.json")
    for gate in doc["gates"].values():
        for ev in gate["evidence"]:
            if sha(ROOT / ev["file"]) != ev["sha256"]:
                problems.append(f"C7.1(3): sha256 divergente {ev['file']}")
    # CR-F021: a C7.1(3) vale para todo arquivo de evidência, não só os dos gates
    for env in doc["environments"]:
        for ev in env["evidence"]:
            if sha(ROOT / ev["file"]) != ev["sha256"]:
                problems.append(f"C7.1(3): sha256 divergente {ev['file']} (environment {env['where']})")
    for v in doc["shared_dependency_verdicts"]:
        if "verdict_file" in v and sha(ROOT / v["verdict_file"]) != v.get("verdict_sha256"):
            problems.append(f"C7.1(3): verdict_sha256 divergente {v['verdict_file']}")
    ff = doc["findings_file"]
    if sha(ROOT / ff["file"]) != ff["sha256"]:
        problems.append(f"C7.1(3): findings_file divergente {ff['file']}")
    all_pass = all(g["status"] == "PASS" for g in doc["gates"].values())
    blocking = any(v["blocking"] for v in doc["shared_dependency_verdicts"])
    qualified_ok = all_pass and doc["counts"]["P0"] == 0 and doc["counts"]["P1"] == 0 and not blocking
    if doc["result"] == "QUALIFIED" and not qualified_ok:
        problems.append("C7.1(1): QUALIFIED sem todos os gates PASS / P0=P1=0 / sem veredito bloqueante")
    if doc["result"] == "NOT_QUALIFIED" and qualified_ok:
        problems.append("C7.1(1): NOT_QUALIFIED com todas as condições de QUALIFIED")
    return problems


def write(path: Path, doc: dict) -> None:
    if path.exists():
        raise SystemExit(f"não sobrescrevo {rel(path)} (C8)")
    problems = check(doc)
    if problems:
        raise SystemExit("\n".join(problems))
    path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"{rel(path)}: OK  counts={doc['counts']}  result={doc['result']}")


def main() -> None:
    mode = sys.argv[1]
    if mode == "partial":
        phase = sys.argv[2]
        write(QC / f"ATTESTATION_PARTIAL_{phase}.json", build("IN_PROGRESS"))
    elif mode == "final":
        ledger = json.loads((QC / "GATES.json").read_text(encoding="utf-8"))
        write(QC / "QUALIFICATION_ATTESTATION.json", build(ledger["final_result"]))
    elif mode == "check":
        doc = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
        if "--schema-only" in sys.argv:
            # parciais antigos: schema + C7.1(6); counts e hashes valem no commit em que foram emitidos
            schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
            jsonschema.Draft202012Validator(schema).validate(doc)
            # registros históricos: valem no núcleo em que foram emitidos (v2.0, v2.1 ou v2.2)
            problems = [] if doc["common_core_sha256"] in CORE_VERSIONS else ["C7.1(6)"]
            print("; ".join(problems) if problems else "OK (schema)")
            raise SystemExit(1 if problems else 0)
        problems = check(doc)
        print("\n".join(problems) if problems else "OK")
        raise SystemExit(1 if problems else 0)


if __name__ == "__main__":
    main()
