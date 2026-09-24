"""stocks / D-16, passo 0: a Etapa A se sustenta? (só stdlib; roda em qualquer Python 3.12+)

Confere, sem mudar nada:
  1. cada ATTESTATION_PARTIAL_*.json: toda evidência citada (gates, environments,
     findings_file, veredictos compartilhados) existe no commit em que o parcial foi
     emitido e o sha256 bate (C7.1 regra 3 "no commit da attestation");
  2. GATES.json no HEAD: toda evidência dos gates existe; para os gates PASS, o sha256
     no HEAD é o mesmo registrado no parcial mais recente (nada mudou desde então);
  3. núcleo, schema, FROZEN_PARAMETERS, perfil e contrato: sha256 do HEAD = parcial mais recente;
  4. runtime_target.json: commit existe no stocks-predictor (clone indicado) e é ancestral de
     origin/main; a wheel publicada e as wheels de Core/Ops de final_wheels são baixadas da
     URL da release e o sha256 confere.

Uso: python verify_stage_a.py <repo de evidência> <clone do stocks-predictor> <saída.json>
Saída: JSON bruto com cada checagem (ok/detalhe) e o resumo; exit 0 se tudo ok, 1 senão.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

CORE_SHA = "50e8f49859daae6dcdf17164781d1837d8b656796924c35060f8d35855ee36e1"
SCHEMA_SHA = "3594e35044626264a18270ee4e079e653e3b940f1e7a72d36f2b70972f5bf970"


def git(repo: Path, *args: str, binary: bool = False):
    out = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, check=False)
    if out.returncode != 0:
        return None
    return out.stdout if binary else out.stdout.decode("utf-8").strip()


def sha_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def main() -> int:
    evidence_repo, stocks_repo, out_path = (Path(a) for a in sys.argv[1:4])
    qc = "qualification/stocks"
    checks: list[dict] = []

    def check(name: str, ok: bool, **detail) -> None:
        checks.append({"check": name, "ok": bool(ok), **detail})

    head = git(evidence_repo, "rev-parse", "HEAD")
    partial_paths = sorted((evidence_repo / qc).glob("ATTESTATION_PARTIAL_*.json"))
    latest = None
    latest_when = ""
    for path in partial_paths:
        rel = path.relative_to(evidence_repo).as_posix()
        added = git(evidence_repo, "log", "--diff-filter=A", "--format=%H %cI", "--", rel)
        commit, when = added.splitlines()[-1].split()
        doc = json.loads(path.read_text(encoding="utf-8"))
        at_commit = json.loads(git(evidence_repo, "show", f"{commit}:{rel}"))
        check(f"{path.name}: unchanged since emission", at_commit == doc, emitted_in=commit)
        items = []
        for gate, entry in doc["gates"].items():
            items += [(f"gate {gate}", e) for e in entry["evidence"]]
        for env in doc.get("environments", []):
            items += [(f"env {env['role']}", e) for e in env["evidence"]]
        items.append(("findings_file", doc["findings_file"]))
        for v in doc.get("shared_dependency_verdicts", []):
            items.append((f"verdict {v['issue_id']}", {"file": v["verdict_file"], "sha256": v["verdict_sha256"]}))
        bad = []
        for label, ev in items:
            raw = git(evidence_repo, "show", f"{commit}:{ev['file']}", binary=True)
            if raw is None or sha_bytes(raw) != ev["sha256"]:
                bad.append({"where": label, "file": ev["file"], "missing": raw is None})
        check(f"{path.name}: every cited evidence exists and matches sha256 at its commit",
              not bad, commit=commit, evidence_items=len(items), mismatches=bad)
        if when > latest_when:
            latest, latest_when = (path, doc, commit), when

    lpath, ldoc, lcommit = latest
    check("latest partial", True, file=lpath.name, emitted_in=lcommit, result=ldoc["result"])
    gates = json.loads((evidence_repo / qc / "GATES.json").read_text(encoding="utf-8"))
    status = {g: s["status"] for g, s in gates["gates"].items()}
    counts = {k: sum(1 for v in status.values() if v == k) for k in ("PASS", "FAIL", "NOT_RUN")}
    check("GATES.json: 27 PASS, 4 NOT_RUN, 0 FAIL", counts == {"PASS": 27, "FAIL": 0, "NOT_RUN": 4},
          counts=counts, not_run=sorted(g for g, s in status.items() if s == "NOT_RUN"))
    missing, changed = [], []
    for gate, state in gates["gates"].items():
        recorded = {e["file"]: e["sha256"] for e in ldoc["gates"].get(gate, {}).get("evidence", [])}
        for item in state.get("evidence", []):
            path = evidence_repo / item
            if not path.is_file():
                missing.append({"gate": gate, "file": item})
                continue
            if state["status"] == "PASS" and recorded.get(item) != sha_bytes(path.read_bytes()):
                changed.append({"gate": gate, "file": item, "recorded": recorded.get(item)})
    check("GATES.json evidence exists at HEAD", not missing, missing=missing)
    check("PASS gates: evidence sha256 at HEAD = latest partial", not changed, changed=changed)
    same_status = {g: (status.get(g), e["status"]) for g, e in ldoc["gates"].items() if status.get(g) != e["status"]}
    check("GATES.json status = latest partial", not same_status, differences=same_status)

    def file_sha(rel: str) -> str | None:
        p = evidence_repo / rel
        return sha_bytes(p.read_bytes()) if p.is_file() else None

    check("core sha256 = v2.0", file_sha("qualification/COMMON_QUALIFICATION_CORE.md") == CORE_SHA == ldoc["common_core_sha256"])
    check("schema sha256", file_sha("qualification/ATTESTATION_SCHEMA.json") == SCHEMA_SHA)
    for key, rel in (("frozen_parameters_sha256", f"{qc}/FROZEN_PARAMETERS.json"),
                     ("protected_set_sha256", f"{qc}/PROTECTED_SET.json"),
                     ("soak_profile_sha256", f"{qc}/QUALIFICATION_PROFILE_STOCKS_V1.json"),
                     ("domain_contract_sha256", f"{qc}/DOMAIN_RESEARCH_CONTRACT.json")):
        check(f"{key}: HEAD = latest partial", file_sha(rel) == ldoc[key], head=file_sha(rel), partial=ldoc[key])
    findings = json.loads((evidence_repo / qc / "FINDINGS.json").read_text(encoding="utf-8"))["findings"]
    open_counts = {s: sum(1 for f in findings if f["status"].startswith("OPEN") and f["severity"] == s)
                   for s in ("P0", "P1", "P2")}
    check("FINDINGS open counts = latest partial", open_counts == ldoc["counts"], head=open_counts, partial=ldoc["counts"])

    target = json.loads((evidence_repo / qc / "runtime_target.json").read_text(encoding="utf-8"))
    commit = target["commit"]
    kind = git(stocks_repo, "cat-file", "-t", commit)
    in_main = subprocess.run(["git", "-C", str(stocks_repo), "merge-base", "--is-ancestor", commit, "origin/main"],
                             check=False).returncode == 0
    check("runtime_target commit exists in stocks-predictor and is in origin/main", kind == "commit" and in_main,
          commit=commit, type=kind, in_origin_main=in_main)
    final_commits = {c["repo"]: c["commit_sha"] for c in ldoc["final_commits"]}
    check("runtime_target commit = final_commits[stocks-predictor]", final_commits.get("stocks-predictor") == commit)
    wheels = [{"name": "stocks-predictor", "url": target["wheel_url"], "sha256": target["wheel_sha256"]}]
    wheels += [w for w in ldoc["final_wheels"] if w["name"] != "stocks-predictor"]
    for wheel in wheels:
        request = urllib.request.Request(wheel["url"], headers={"User-Agent": "stocks-qualification-d16/1"})
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                raw = response.read()
            got = sha_bytes(raw)
            check(f"wheel {wheel['name']}: release asset sha256", got == wheel["sha256"],
                  url=wheel["url"], expected=wheel["sha256"], observed=got, bytes=len(raw))
        except Exception as exc:  # noqa: BLE001 - registrado como falha
            check(f"wheel {wheel['name']}: release asset sha256", False, url=wheel["url"], error=repr(exc))
    stocks_wheel_in_partial = next(w for w in ldoc["final_wheels"] if w["name"] == "stocks-predictor")
    check("runtime_target wheel = final_wheels[stocks-predictor]",
          (stocks_wheel_in_partial["url"], stocks_wheel_in_partial["sha256"]) == (target["wheel_url"], target["wheel_sha256"]))

    summary = {"evidence_head": head, "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
               "partials": len(partial_paths), "checks": checks, "all_ok": all(c["ok"] for c in checks),
               "failed": [c["check"] for c in checks if not c["ok"]]}
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text(json.dumps(summary, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"all_ok": summary["all_ok"], "checks": len(checks), "failed": summary["failed"]}, ensure_ascii=False))
    return 0 if summary["all_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
