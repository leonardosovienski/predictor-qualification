"""integration-brasileirao, C14 na cain 0.4.13rc15 + transporte 0.1.0rc7 (D-27, 2026-09-30): ledger GATES.json do ciclo com o que
esta sessão (Linux na nuvem, sem acesso ao PC 2) conseguiu provar — só as conferências estáticas.

O Linux primário desta missão é o PC 2 do dono (owner_linux, D-19: dado real privado) e o secundário é o Windows do PC 2 (D-25).
Nenhuma fase de runtime roda aqui: E2E, N+1, isolamento, falhas, soak, cleanroom-final, C24.3 (c)/(d), identidade das wheels
instaladas e WINDOWS_SMOKE ficam NOT_RUN com "BLOCKED: …". Estáticas feitas: release check da cain rc15 (7/7), hosted-ci nos
SHAs finais, C24.3 estático (9/10: a (f) passa só pelo aceite IB-F005, como na rc13), conjunto protegido (domínios intactos;
qualification/crypto/runtime_target.json mudou pela reabertura V1.2 do crypto) e segredos. A attestation rc13 (QUALIFIED)
continua vigente. Idempotente.
Uso: python rc15_static.py <raiz do predictor-qualification>
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve()
M = "qualification/integration-brasileirao"
CLONES = Path("/home/user")


def lock(repo: str, commit: str) -> dict:
    raw = subprocess.run(["git", "-C", str(CLONES / repo), "show", f"{commit}:uv.lock"], capture_output=True, text=True, check=True).stdout
    return {p["name"]: p for p in tomllib.loads(raw)["package"]}


def main() -> None:
    t = json.loads((ROOT / M / "runtime_targets.json").read_text(encoding="utf-8"))
    g = json.loads((ROOT / M / "GATES.json").read_text(encoding="utf-8"))
    cl, bl = lock("cain", t["cain"]["commit"]), lock("brasileirao-predictor", t["brasileirao"]["commit"])
    wheels = [{"name": n, "version": t[k]["version"], "url": t[k]["url"], "sha256": t[k]["sha256"]}
              for k, n in (("cain", "cain-research"), ("brasileirao", "brasileirao-predictor"),
                           ("transport", "predictor-research-transport"), ("protocol", "predictor-research-protocol"))]
    for lk, name in ((bl, "predictor-core"), (bl, "predictor-ops")):
        (w,) = lk[name]["wheels"]
        wheels.append({"name": name, "version": lk[name]["version"], "url": w["url"], "sha256": w["hash"].split(":", 1)[1]})
    g["final_wheels"] = wheels
    g["final_commits"] = [
        {"repo": "cain", "commit_sha": t["cain"]["commit"]},
        {"repo": "ecosystem-predictor", "commit_sha": t["transport"]["commit"]},
        {"repo": "brasileirao-predictor", "commit_sha": t["brasileirao"]["commit"]},
        {"repo": "core-predictor", "commit_sha": "7bb212cfa06333886e11e849b209c5aab801c04b"},
        {"repo": "predictor-ops", "commit_sha": "9831b0d5e727972b1d85ff48be14ffa58677898b"},
    ]
    g["cycle_rc15"] = {
        "why": "D-27 (2026-09-30): cain 0.4.13rc15 e transporte 0.1.0rc7; C14 manda refazer as fases que os exercitam",
        "state_this_session": "BLOCKED",
        "note": "sessão sem acesso ao PC 2 (owner_linux/Windows): só conferências estáticas; runtime, soak e Windows ficam para o dono no PC 2 "
                "(scripts desta missão: runtime_env.sh, run_scenario.sh, windows_stage.sh, windows_smoke.ps1) com os alvos de runtime_targets.json",
        "previous_cycle": "rc13 (run-20260928T183300Z-br13, QUALIFIED, attestation atual)",
    }
    for phase in ("publish-candidates-rc15", "hosted-ci-rc15"):
        if phase not in g["phases_completed"]:
            g["phases_completed"].append(phase)
    g["environments"] = [
        {"os": "linux", "python": "3.13", "role": "primary", "where": "owner_linux", "result": "NOT_RUN", "evidence": [f"{M}/QUALIFICATION_CHANGELOG.md"]},
        {"os": "windows", "python": "3.13", "role": "secondary", "where": "local_windows", "result": "NOT_RUN", "evidence": [f"{M}/QUALIFICATION_CHANGELOG.md"]},
    ]

    def p(status, ev, note):
        for e in ev:
            if not (ROOT / e).is_file():
                raise SystemExit(f"evidência ausente: {e}")
        return {"status": status, "evidence": ev, "note": note}

    gates = g["gates"]
    blocked = "BLOCKED: fase de runtime do Linux primário desta missão (PC 2 do dono, owner_linux, dado privado; D-19/D-25); não roda nesta sessão. Refazer no PC 2 com os alvos rc15."
    for gid in ("LOCK_INTEGRITY", "CORE_IDENTITY", "CLEANROOM_FINAL", "E2E", "IDEMPOTENCY", "RESTART_RECOVERY", "FAILURE_INJECTION", "PROVENANCE",
                "AUTHORITY_SEPARATION", "FUTURE_CANARY", "SOAK", "CAPITAL_FORBIDDEN", "ENVELOPE_V2_CONFORMANCE", "CAIN_INGESTION", "CAIN_CONTAINMENT",
                "DECISION_POLICY", "N_PLUS_1_DETERMINISTIC", "NEGATIVE_RESULT_NEUTRALITY", "CROSS_DOMAIN_ISOLATION", "DOMAIN_QUALIFIED_IDS",
                "CONTRADICTION_PRESERVATION", "EVIDENCE_CONSISTENCY"):
        gates[gid] = {"status": "NOT_RUN", "evidence": [], "note": blocked}
    gates["WINDOWS_SMOKE"] = {"status": "NOT_RUN", "evidence": [], "note": "BLOCKED: Windows do PC 2 do dono (D-25), fora desta sessão."}
    hosted = json.loads((ROOT / M / "RAW_LOGS/hosted-ci/final-rc15/HOSTED_CI_SUMMARY.json").read_text(encoding="utf-8"))
    ok = all(i["ok"] for i in hosted)
    gates["HOSTED_CI"] = p("PASS" if ok else "FAIL", [f"{M}/RAW_LOGS/hosted-ci/final-rc15/HOSTED_CI_SUMMARY.json", f"{M}/hosted_ci_final_targets_rc15.json"],
                           "rc15: runs de push verdes nos SHAs exatos (cain ae00017, ecosystem b0da4fd, brasileirao 1fc2e88 pelo caminho aceito na IB-F005); coletado por API pública (gh_shim)")
    sec = json.loads((ROOT / M / "RAW_LOGS/secrets-rc15/secrets_scan.json").read_text(encoding="utf-8"))
    gates["SECRETS_CLEAN"] = p("PASS" if sec["clean"] else "FAIL", [f"{M}/RAW_LOGS/secrets-rc15/secrets_scan.json"],
                               f"rc15: {len(sec['findings'])} achados nos diffs até ae00017 (cain), b0da4fd (ecosystem), 1fc2e88 (brasileirao) e nos arquivos da missão")
    st = json.loads((ROOT / M / "RAW_LOGS/contract-revalidation-rc15/static_checks.json").read_text(encoding="utf-8"))
    gates["DOMAIN_CONTRACTS_PRESERVED"] = {"status": "NOT_RUN", "evidence": [f"{M}/RAW_LOGS/contract-revalidation-rc15/static_checks.json"],
                                          "note": f"BLOCKED: parte estática {st['passed']}/{st['passed'] + st['failed']} ((f) passa só pelo aceite IB-F005, como na rc13); (c) e (d) exigem o runtime do PC 2."}
    pr = json.loads((ROOT / M / "RAW_LOGS/protected-rc15/protected_check.json").read_text(encoding="utf-8"))
    changed = [s["path"] for s in pr["shared"] if not s["ok"]]
    gates["PROTECTED_ARTIFACTS_UNCHANGED"] = {"status": "NOT_RUN", "evidence": [f"{M}/RAW_LOGS/protected-rc15/protected_check.json", f"{M}/PROTECTED_SET.json"],
                                             "note": f"BLOCKED: domínios intactos ({pr['items_total']} itens); alterado fora desta missão: {changed} (pin do alvo da Etapa A do crypto, reabertura V1.2/D-27) — aceitar é decisão do dono."}
    gates["SHARED_DEPENDENCY_CLEAR"]["note"] = "rc15: Ops 4.2.2rc1 e Core inalterados; " + gates["SHARED_DEPENDENCY_CLEAR"]["note"]
    findings = json.loads((ROOT / M / "FINDINGS.json").read_text(encoding="utf-8"))
    open_st = findings.get("open_statuses", ["OPEN", "OPEN_AWAITING_OWNER"])
    blocking = [f["id"] for f in findings["findings"] if f["status"] in open_st and f["severity"] in ("P0", "P1")]
    gates["BLOCKERS_ZERO"] = p("FAIL" if blocking else "PASS", [f"{M}/FINDINGS.json"], ("P0/P1 abertos: " + ", ".join(blocking)) if blocking else "nenhum P0/P1 aberto")
    g["cycle_rc15"]["release_check"] = f"{M}/RAW_LOGS/release-rc15/release_check.json"
    g["supersedes_sha256"] = hashlib.sha256((ROOT / M / "QUALIFICATION_ATTESTATION.json").read_bytes()).hexdigest()
    (ROOT / M / "GATES.json").write_text(json.dumps(g, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print({k: v["status"] for k, v in gates.items() if v["status"] == "PASS"})
    print("NOT_RUN:", len([1 for v in gates.values() if v["status"] == "NOT_RUN"]), "FAIL:", [k for k, v in gates.items() if v["status"] == "FAIL"])


if __name__ == "__main__":
    main()
