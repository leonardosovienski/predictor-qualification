"""integration-crypto, C14 na cain 0.4.13rc15 + transporte 0.1.0rc7 + cripto 1.2.0rc4 (D-27, 2026-09-30): ledger GATES.json
do ciclo, a partir do run 36648103793 (Linux primário, todas as fases) e das conferências estáticas rc15.

Diferenças em relação a update_gates.py (rc13):
  * WINDOWS_SMOKE fica NOT_RUN ("BLOCKED"): o secundário é o Windows do PC 2 do dono (D-23), fora desta sessão;
  * PROTECTED_ARTIFACTS_UNCHANGED fica NOT_RUN ("BLOCKED"): os domínios estão intactos, mas o item compartilhado
    qualification/crypto/runtime_target.json mudou pela reabertura V1.2 do crypto (D-27); aceitar o pin novo é decisão do
    dono (mesmo caminho da IC-F011 para o FROZEN_PARAMETERS);
  * a attestation da Etapa A do cripto no main continua sendo a V1.1 (QUALIFIED para 341d270 / rc2); a V1.2 (21f8b182 / rc4,
    alvo deste ciclo) está BLOCKED no WINDOWS_SMOKE. C7.1 regra 7 só fecha quando a V1.2 for QUALIFIED.
Estado terminal do ciclo nesta sessão: BLOCKED (C7.3) → só parcial. Idempotente.
Uso: python rc15_gates.py <raiz do predictor-qualification>
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve()
M = "qualification/integration-crypto"
CLONES = Path("/home/user")
targets = json.loads((ROOT / M / "runtime_targets.json").read_text(encoding="utf-8"))
RUN = "run36648103793"
R = f"{M}/RAW_LOGS/runtime/{RUN}"
FM = f"{R}/failure-matrix"


def lock(repo: str, commit: str) -> dict:
    raw = subprocess.run(["git", "-C", str(CLONES / repo), "show", f"{commit}:uv.lock"], capture_output=True, text=True, check=True).stdout
    return {p["name"]: p for p in tomllib.loads(raw)["package"]}


def main() -> None:
    cl, kl = lock("cain", targets["cain"]["commit"]), lock("cripto-predictor", targets["cripto"]["commit"])
    wheels = []
    for key, name in (("cain", "cain-research"), ("cripto", "cripto-predictor"),
                      ("transport", "predictor-research-transport"), ("protocol", "predictor-research-protocol")):
        t = targets[key]
        wheels.append({"name": name, "version": t["version"], "url": t["url"], "sha256": t["sha256"]})
    for lk, name in ((cl, "predictor-research-snapshot"), (cl, "predictor-research-bundle"), (kl, "predictor-core"), (kl, "predictor-ops")):
        (w,) = lk[name]["wheels"]
        wheels.append({"name": name, "version": lk[name]["version"], "url": w["url"], "sha256": w["hash"].split(":", 1)[1]})
    g = json.loads((ROOT / M / "GATES.json").read_text(encoding="utf-8"))
    g["cycle_rc15"] = {
        "why": "D-27 (2026-09-29/30): cain 0.4.13rc15, transporte 0.1.0rc7 e cripto 1.2.0rc4 (main; Etapa A reaberta como V1.2, BLOCKED no Windows local); "
               "C14: fases que exercitam as wheels refeitas no Linux primário",
        "run": RUN, "state_this_session": "BLOCKED",
        "domain_attestation_note": "a attestation da Etapa A no main (2b1491a0…) é QUALIFIED para 341d270/rc2; o alvo deste ciclo é 21f8b182/rc4 (V1.2, "
                                   "parcial v1-2-attestation-blocked). C7.1 regra 7 fecha só com a V1.2 QUALIFIED.",
        "previous_cycle": "rc13 (run36462444590, QUALIFIED, attestation atual)",
    }
    g["final_commits"] = [
        {"repo": "cain", "commit_sha": targets["cain"]["commit"]},
        {"repo": "ecosystem-predictor", "commit_sha": targets["transport"]["commit"]},
        {"repo": "cripto-predictor", "commit_sha": targets["cripto"]["commit"]},
        {"repo": "core-predictor", "commit_sha": "5a0841509f091ea0aa95bde0d3d65e2a1a9e984d"},
        {"repo": "predictor-ops", "commit_sha": "9831b0d5e727972b1d85ff48be14ffa58677898b"},
    ]
    g["final_wheels"] = wheels
    g["environments"] = [
        {"os": "linux", "python": "3.13", "role": "primary", "where": "github_actions", "result": "PASS",
         "evidence": [f"{R}/ci_runtime.log", f"{R}/env/runtime_env.log", f"{R}/e2e/SUMMARY.json", f"{R}/soak/SUMMARY.json"]},
        {"os": "windows", "python": "3.13", "role": "secondary", "where": "local_windows", "result": "NOT_RUN",
         "evidence": [f"{M}/QUALIFICATION_CHANGELOG.md"]},
    ]
    for phase in ("publish-candidates-rc15", "cleanroom-final-rc15", "contract-revalidation-rc15", "e2e-rc15", "n-plus-1-rc15",
                  "isolation-ids-contradiction-rc15", "idempotency-failure-rc15", "hosted-ci-rc15", "soak-rc15", "windows-smoke-rc15"):
        if phase not in g["phases_completed"]:
            g["phases_completed"].append(phase)

    def p(status, ev, note):
        for e in ev:
            if not (ROOT / e).is_file():
                raise SystemExit(f"evidência ausente: {e}")
        return {"status": status, "evidence": ev, "note": note}

    gates = g["gates"]
    CI = f"{M}/RAW_LOGS/core-identity-rc15/core_identity.json"
    gates["LOCK_INTEGRITY"] = p("PASS", [CI, f"{R}/env/runtime_env.log", f"{M}/CORE_IDENTITY_REPORT.md"],
                                "rc15: runtimes só de uv.lock --require-hashes + wheels publicadas conferidas por sha256 (12/12 conferências)")
    gates["CORE_IDENTITY"] = p("PASS", [CI, f"{R}/cleanroom-final/cleanroom_final.log", f"{M}/CORE_IDENTITY_REPORT.md"],
                               "rc15: pyproject ↔ uv.sources ↔ uv.lock ↔ wheel ↔ instalado ↔ site-packages (cain rc15, transporte rc7, protocolo rc2, cripto rc4)")
    gates["CLEANROOM_FINAL"] = p("PASS", [f"{R}/cleanroom-final/cleanroom_final.log", f"{R}/cleanroom-final/conformance.junit.xml",
                                          f"{R}/cleanroom-final/transport.junit.xml", f"{R}/cleanroom-final/cain.junit.xml", f"{M}/CLEANROOM_REPORT.md"],
                                 "rc15: só wheels publicadas, venvs limpos fora dos checkouts")
    gates["E2E"] = p("PASS", [f"{R}/e2e/SUMMARY.json", f"{R}/e2e/commands.log", f"{M}/CAIN_ROUNDTRIP_REPORT.md"],
                     "rc15: entrypoints cain e predictor-research-consumer, dados reais, restart do consumidor e do CAIN, outros domínios intercalados")
    gates["PROVENANCE"] = p("PASS", [f"{R}/e2e/SUMMARY.json", f"{FM}/F08/SUMMARY.json"], "rc15: envelope ↔ show ↔ admission ↔ journal ↔ Ops ↔ task ↔ adapter em cada resultado")
    gates["IDEMPOTENCY"] = p("PASS", [f"{FM}/FAILURE_MATRIX_RESULTS.json", f"{FM}/F09/SUMMARY.json", f"{FM}/F10/SUMMARY.json", f"{FM}/F12/SUMMARY.json", f"{R}/e2e/SUMMARY.json"],
                             "rc15: retry, reentrega e reproposta sem segundo efeito")
    gates["RESTART_RECOVERY"] = p("PASS", [f"{FM}/F0{i}/SUMMARY.json" for i in range(1, 9)], "rc15: morte real (exit 86) em cada ponto crítico do CAIN e do consumidor")
    gates["FAILURE_INJECTION"] = p("PASS", [f"{FM}/FAILURE_MATRIX_RESULTS.json", f"{M}/FAILURE_MATRIX.json"], "rc15: F01–F15 na borda, fail closed")
    gates["AUTHORITY_SEPARATION"] = p("PASS", [f"{R}/e2e/SUMMARY.json", f"{FM}/F14/SUMMARY.json", f"{FM}/F15/SUMMARY.json"],
                                      "rc15: estados copiados como vieram; RETRYABLE não é resultado; RECONCILIATION_REQUIRED para o domínio; capital sempre false")
    gates["FUTURE_CANARY"] = p("PASS", [f"{R}/e2e/SUMMARY.json"], "rc15: canário recusado pelo domínio; token e instantes pós-cutoff ausentes da memória")
    gates["WINDOWS_SMOKE"] = {"status": "NOT_RUN", "evidence": [],
                              "note": "BLOCKED: o secundário desta missão é o Windows do PC 2 do dono (D-23, C:\\Cripto\\qualificacao\\runtime\\integration-crypto\\), fora "
                                      "desta sessão. Falta o dono repetir o E2E + restart com os alvos rc15 (runtime_targets.json)."}
    gates["SHARED_DEPENDENCY_CLEAR"] = p("PASS", [f"{M}/RAW_LOGS/c0/c0_preflight.log", "qualification/shared/SHARED_ISSUES.json"],
                                         "nenhum issue bloqueante para as wheels usadas (Ops 4.2.2rc1, Core 3.2.1; inalteradas na rc15)")
    gates["SECRETS_CLEAN"] = p("PASS", [f"{M}/RAW_LOGS/secrets-rc15/secrets_scan.json"],
                               "rc15: 0 achados nos diffs rc13→rc15 (cain), rc6→rc7 (ecosystem), rc3→rc4 (cripto) e nos arquivos da missão")
    gates["CAPITAL_FORBIDDEN"] = p("PASS", [f"{R}/e2e/SUMMARY.json", f"{R}/n-plus-1/SUMMARY.json", f"{M}/DECISION_POLICY_REPORT.md"],
                                   "rc15: nenhum caminho concede capital; receipts e resultados com capital_permission=false")
    gates["ENVELOPE_V2_CONFORMANCE"] = p("PASS", [f"{R}/contract-revalidation/SUMMARY.json", f"{R}/e2e/SUMMARY.json", f"{FM}/F11/SUMMARY.json", f"{FM}/F13/SUMMARY.json",
                                                  f"{M}/ENVELOPE_V2_CONFORMANCE_REPORT.md"],
                                         "rc15: release congelada 2.0.0rc2; adapter só pela adapter_api; payload byte-idêntico")
    gates["CAIN_INGESTION"] = p("PASS", [f"{FM}/F11/SUMMARY.json", f"{FM}/F12/SUMMARY.json", f"{FM}/F13/SUMMARY.json", f"{R}/e2e/SUMMARY.json"],
                                "rc15: só V2 conhecido, task existente do mesmo domínio, correlação e provenance válidas")
    gates["CAIN_CONTAINMENT"] = p("PASS", [f"{R}/cleanroom-final/cain.junit.xml", f"{R}/env/runtime_env.log", f"{M}/CAIN_ROUNDTRIP_REPORT.md"],
                                  "rc15: loop do PR #50 fora do runtime; venv do CAIN sem domínio; PR #51 só leitura, SHA completo")
    gates["DECISION_POLICY"] = p("PASS", [f"{R}/cleanroom-final/cain.junit.xml", f"{R}/n-plus-1/SUMMARY.json", f"{M}/DECISION_POLICY_REPORT.md"],
                                 "rc15: determinística, versionada (código + configuração), receipt sem LLM; policy.py da rc15 difere da rc13 só por uma anotação de tipo; crypto.json igual")
    gates["N_PLUS_1_DETERMINISTIC"] = p("PASS", [f"{R}/n-plus-1/SUMMARY.json"], "rc15: 6 candidatas × 3 processos novos, receipts byte a byte iguais, estado inalterado")
    gates["NEGATIVE_RESULT_NEUTRALITY"] = p("PASS", [f"{R}/cleanroom-final/cain.junit.xml"], "rc15: budget, prioridade e escopo constantes da configuração; teste contra a wheel publicada")
    gates["CROSS_DOMAIN_ISOLATION"] = p("PASS", [f"{R}/isolation/SUMMARY.json", f"{R}/e2e/SUMMARY.json"], "rc15: fixtures V2 congeladas de stocks e brasileirao recusadas nos dois sentidos")
    gates["DOMAIN_QUALIFIED_IDS"] = p("PASS", [f"{R}/isolation/SUMMARY.json"], "rc15: mesmo H9 nos três domínios, IDs distintos; ID sem domínio recusado")
    gates["CONTRADICTION_PRESERVATION"] = p("PASS", [f"{R}/isolation/SUMMARY.json"], "rc15: SUPPORTED × REFUTED → REQUIRE_HUMAN; os dois fatos preservados; sem maioria")
    gates["DOMAIN_CONTRACTS_PRESERVED"] = p("PASS", [f"{M}/RAW_LOGS/contract-revalidation-rc15/static_checks.json", f"{R}/cleanroom-final/conformance.junit.xml",
                                                     f"{R}/contract-revalidation/SUMMARY.json", f"{M}/CONTRACT_REVALIDATION_REPORT.md"],
                                            "rc15: C24.3 (a)–(f) verdes com a Etapa A vigente = V1.2 (21f8b182): diff do domínio vazio (o adapter já está no alvo)")
    hosted = json.loads((ROOT / M / "RAW_LOGS/hosted-ci/final-rc15/HOSTED_CI_SUMMARY.json").read_text(encoding="utf-8"))
    hosted_ok = all(item["ok"] for item in hosted)
    gates["HOSTED_CI"] = p("PASS" if hosted_ok else "FAIL",
                           [f"{M}/RAW_LOGS/hosted-ci/baseline/HOSTED_CI_SUMMARY.json", f"{M}/RAW_LOGS/hosted-ci/final-rc15/HOSTED_CI_SUMMARY.json", f"{M}/HOSTED_CI_REPORT.md"],
                           "rc15: runs de push verdes nos SHAs exatos (cain ae00017, ecosystem b0da4fd, cripto 21f8b18)" if hosted_ok else "job não verde: ver resumo")
    gates["SOAK"] = p("PASS", [f"{R}/soak/SUMMARY.json", f"{R}/soak/commands.log", f"{M}/QUALIFICATION_PROFILE_INTEGRATION_CRYPTO_V1.json", f"{M}/SOAK_REPORT.md"],
                      "rc15: perfil V1 sem mudança, todos os pisos atingidos (24 ciclos, 18 duplicatas, 6 restarts do domínio, 10 do CAIN, 6 intercalados, 6 propostas de LLM), tolerância zero")
    protected = json.loads((ROOT / M / "RAW_LOGS/protected-rc15/protected_check.json").read_text(encoding="utf-8"))
    changed_shared = [s["path"] for s in protected["shared"] if not s["ok"] and not s.get("chain", {}).get("ok")]
    gates["PROTECTED_ARTIFACTS_UNCHANGED"] = {
        "status": "NOT_RUN", "evidence": [f"{M}/RAW_LOGS/protected-rc15/protected_check.json", f"{M}/PROTECTED_SET.json"],
        "note": ("BLOCKED: domínios intactos (crypto 1387, stocks 89, brasileirao 1884 blobs iguais); FROZEN_PARAMETERS encadeado (IC-F011); item compartilhado "
                 f"alterado fora desta missão: {changed_shared} (pin do alvo da Etapa A do crypto, mudado pela reabertura V1.2/D-27). Aceitar o pin novo neste "
                 "ciclo é decisão do dono (mesmo caminho da IC-F011); até lá o gate não fecha por pressuposto.")}
    fw = f"{M}/RAW_LOGS/final-wheels-rc15/final_wheels_check_{RUN}.json"
    gates["EVIDENCE_CONSISTENCY"] = p("PASS" if (ROOT / fw).is_file() else "NOT_RUN",
                                      [f"{M}/EVIDENCE_NUMBERS.json", f"{M}/scripts/evidence_numbers.py", f"{M}/scripts/render_reports.py"] + ([fw] if (ROOT / fw).is_file() else []),
                                      "rc15: números dos relatórios gerados de RAW_LOGS por script versionado; saída dos jobs devolvida por branch (SHA256SUMS); final_wheels conferidas (C7.1 regra 4)")
    findings = json.loads((ROOT / M / "FINDINGS.json").read_text(encoding="utf-8"))
    blocking = [f["id"] for f in findings["findings"] if f["status"] in findings["open_statuses"] and f["severity"] in ("P0", "P1")]
    gates["BLOCKERS_ZERO"] = p("FAIL" if blocking else "PASS", [f"{M}/FINDINGS.json"], ("P0/P1 abertos: " + ", ".join(blocking)) if blocking else "nenhum P0/P1 aberto")
    not_run = sorted(k for k, v in gates.items() if v["status"] == "NOT_RUN")
    failed = sorted(k for k, v in gates.items() if v["status"] == "FAIL")
    g["cycle_rc15"]["terminal"] = "NOT_QUALIFIED" if failed or blocking else ("BLOCKED" if not_run else "QUALIFIED")
    g["cycle_rc15"]["terminal_note"] = f"FAIL em {failed}" if failed else (f"BLOCKED: NOT_RUN em {not_run}; attestation da Etapa A do cripto para 21f8b182 ainda não QUALIFIED (V1.2 BLOCKED)" if not_run else "todos PASS")
    g["final_result"] = "NOT_QUALIFIED" if failed or blocking else g.get("final_result")
    # a attestation vigente (rc13, QUALIFIED) é a que uma futura final substituiria
    g["supersedes_sha256"] = hashlib.sha256((ROOT / M / "QUALIFICATION_ATTESTATION.json").read_bytes()).hexdigest()
    (ROOT / M / "GATES.json").write_text(json.dumps(g, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("rc15:", g["cycle_rc15"]["terminal"], "|", g["cycle_rc15"]["terminal_note"])
    print({k: v["status"] for k, v in gates.items() if v["status"] != "PASS"})


if __name__ == "__main__":
    main()
