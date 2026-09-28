"""Ledger GATES.json da missão: final_commits/final_wheels, ambientes e estados dos gates comprovados até aqui.

Reemissão C14 (IC-F004 fechado pela renovação do harness do cripto): evidências novas em diretórios *-c14 e nos
runs novos; os raw logs citados pela attestation anterior não mudam.
"""

import hashlib
import json
import subprocess
import tomllib
from pathlib import Path

M = "qualification/integration-crypto"
targets = json.load(open(f"{M}/runtime_targets.json"))


def lock(repo, commit):
    raw = subprocess.run(["git", "-C", f"/home/superleo13/predictors/repos/{repo}", "show", f"{commit}:uv.lock"],
                         capture_output=True, text=True, check=True).stdout
    return {p["name"]: p for p in tomllib.loads(raw)["package"]}


cl, kl = lock("cain", targets["cain"]["commit"]), lock("cripto-predictor", targets["cripto"]["commit"])
wheels = []
for key, name in (("cain", "cain-research"), ("cripto", "cripto-predictor"),
                  ("transport", "predictor-research-transport"), ("protocol", "predictor-research-protocol")):
    t = targets[key]
    wheels.append({"name": name, "version": t["version"], "url": t["url"], "sha256": t["sha256"]})
for lk, name in ((cl, "predictor-research-snapshot"), (cl, "predictor-research-bundle"), (kl, "predictor-core"),
                 (kl, "predictor-ops")):
    (w,) = lk[name]["wheels"]
    wheels.append({"name": name, "version": lk[name]["version"], "url": w["url"], "sha256": w["hash"].split(":", 1)[1]})
R = f"{M}/RAW_LOGS/runtime/run36360075557"
FM = f"{R}/failure-matrix"
W = f"{M}/RAW_LOGS/windows-smoke-c14"
g = json.load(open(f"{M}/GATES.json", encoding="utf-8"))
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
     "evidence": [f"{R}/run.json", f"{R}/ci_runtime.log", f"{R}/env/runtime_env.log", f"{R}/e2e/SUMMARY.json"]},
    {"os": "windows", "python": "3.13.15", "role": "secondary", "where": "local_windows", "result": "PASS",
     "evidence": [f"{W}/logs/windows_smoke.log", f"{W}/e2e/SUMMARY.json", f"{W}/SHA256SUMS.windows.txt"]},
]
for phase in ("envelope-v2", "domain-adapter", "cain-wiring-decision-policy", "publish-candidates", "cleanroom-final",
              "contract-revalidation", "e2e", "n-plus-1", "isolation-ids-contradiction", "idempotency-failure",
              "windows-smoke", "hosted-ci"):
    if phase not in g["phases_completed"]:
        g["phases_completed"].append(phase)


def p(status, ev, note):
    return {"status": status, "evidence": ev, "note": note}


gates = g["gates"]
gates["LOCK_INTEGRITY"] = p("PASS", [f"{M}/RAW_LOGS/core-identity-c14/core_identity.json", f"{R}/env/runtime_env.log",
                                     f"{M}/CORE_IDENTITY_REPORT.md"],
                            "runtimes só de uv.lock --require-hashes + wheels publicadas conferidas por sha256")
gates["CORE_IDENTITY"] = p("PASS", [f"{M}/RAW_LOGS/core-identity-c14/core_identity.json",
                                    f"{R}/cleanroom-final/cleanroom_final.log", f"{M}/CORE_IDENTITY_REPORT.md"],
                           "pyproject ↔ uv.sources ↔ uv.lock ↔ wheel ↔ instalado ↔ site-packages")
gates["CLEANROOM_FINAL"] = p("PASS", [f"{R}/cleanroom-final/cleanroom_final.log", f"{R}/cleanroom-final/conformance.junit.xml",
                                      f"{R}/cleanroom-final/transport.junit.xml", f"{R}/cleanroom-final/cain.junit.xml",
                                      f"{M}/CLEANROOM_REPORT.md"],
                             "só wheels publicadas, venvs limpos fora dos checkouts")
gates["E2E"] = p("PASS", [f"{R}/e2e/SUMMARY.json", f"{R}/e2e/commands.log", f"{M}/CAIN_ROUNDTRIP_REPORT.md"],
                 "entrypoints cain e predictor-research-consumer, dados reais, restart do consumidor e do CAIN, "
                 "outros domínios intercalados")
gates["PROVENANCE"] = p("PASS", [f"{R}/e2e/SUMMARY.json", f"{FM}/F08/SUMMARY.json"],
                        "envelope ↔ show ↔ admission ↔ journal ↔ Ops ↔ task ↔ adapter em cada resultado")
gates["IDEMPOTENCY"] = p("PASS", [f"{FM}/FAILURE_MATRIX_RESULTS.json", f"{FM}/F09/SUMMARY.json", f"{FM}/F10/SUMMARY.json",
                                  f"{FM}/F12/SUMMARY.json", f"{R}/e2e/SUMMARY.json"],
                         "retry, reentrega e reproposta sem segundo efeito")
gates["RESTART_RECOVERY"] = p("PASS", [f"{FM}/F0{i}/SUMMARY.json" for i in range(1, 9)],
                              "morte real (exit 86) em cada ponto crítico do CAIN e do consumidor")
gates["FAILURE_INJECTION"] = p("PASS", [f"{FM}/FAILURE_MATRIX_RESULTS.json", f"{M}/FAILURE_MATRIX.json"],
                               "F01–F15 na borda, fail closed")
gates["AUTHORITY_SEPARATION"] = p("PASS", [f"{R}/e2e/SUMMARY.json", f"{FM}/F14/SUMMARY.json", f"{FM}/F15/SUMMARY.json"],
                                  "estados copiados como vieram; RETRYABLE não é resultado; RECONCILIATION_REQUIRED "
                                  "para o domínio; capital sempre false")
gates["FUTURE_CANARY"] = p("PASS", [f"{R}/e2e/SUMMARY.json"],
                           "canário recusado pelo domínio; token e instantes pós-cutoff ausentes da memória")
gates["WINDOWS_SMOKE"] = p("PASS", [f"{W}/e2e/SUMMARY.json", f"{W}/logs/windows_smoke.log", f"{W}/logs/data_copy.tsv"],
                           "PC 2 (D-23), pasta C:\\Cripto\\qualificacao\\runtime\\integration-crypto\\, E2E + restart")
gates["SHARED_DEPENDENCY_CLEAR"] = p("PASS", [f"{M}/RAW_LOGS/c0/c0_preflight.log", "qualification/shared/SHARED_ISSUES.json"],
                                     "nenhum issue bloqueante para as wheels usadas (Ops 4.2.2rc1, Core 3.2.1)")
gates["SECRETS_CLEAN"] = p("PASS", [f"{M}/RAW_LOGS/secrets-c14/secrets_scan.json"],
                           "0 achados nos diffs da missão e nos arquivos da missão; gitleaks/scan_secrets nos CIs")
gates["CAPITAL_FORBIDDEN"] = p("PASS", [f"{R}/e2e/SUMMARY.json", f"{R}/n-plus-1/SUMMARY.json",
                                        f"{M}/DECISION_POLICY_REPORT.md"],
                               "nenhum caminho concede capital; receipts e resultados com capital_permission=false")
gates["ENVELOPE_V2_CONFORMANCE"] = p("PASS", [f"{R}/contract-revalidation/SUMMARY.json", f"{R}/e2e/SUMMARY.json",
                                              f"{FM}/F11/SUMMARY.json", f"{FM}/F13/SUMMARY.json",
                                              f"{M}/ENVELOPE_V2_CONFORMANCE_REPORT.md"],
                                     "release congelada 2.0.0rc2; adapter só pela adapter_api; payload byte-idêntico")
gates["CAIN_INGESTION"] = p("PASS", [f"{FM}/F11/SUMMARY.json", f"{FM}/F12/SUMMARY.json", f"{FM}/F13/SUMMARY.json",
                                     f"{R}/e2e/SUMMARY.json"],
                            "só V2 conhecido, task existente do mesmo domínio, correlação e provenance válidas")
gates["CAIN_CONTAINMENT"] = p("PASS", [f"{R}/cleanroom-final/cain.junit.xml", f"{R}/env/runtime_env.log",
                                       f"{M}/CAIN_ROUNDTRIP_REPORT.md"],
                              "loop do PR #50 fora do runtime; venv do CAIN sem domínio; PR #51 só leitura, SHA completo")
gates["DECISION_POLICY"] = p("PASS", [f"{R}/cleanroom-final/cain.junit.xml", f"{R}/n-plus-1/SUMMARY.json",
                                      f"{M}/DECISION_POLICY_REPORT.md"],
                             "determinística, versionada (código + configuração), receipt sem LLM")
gates["N_PLUS_1_DETERMINISTIC"] = p("PASS", [f"{R}/n-plus-1/SUMMARY.json"],
                                    "6 candidatas × 3 processos novos, receipts byte a byte iguais, estado inalterado")
gates["NEGATIVE_RESULT_NEUTRALITY"] = p("PASS", [f"{R}/cleanroom-final/cain.junit.xml"],
                                        "budget, prioridade e escopo são constantes da configuração; teste de "
                                        "neutralidade contra a wheel publicada")
gates["CROSS_DOMAIN_ISOLATION"] = p("PASS", [f"{R}/isolation/SUMMARY.json", f"{R}/e2e/SUMMARY.json"],
                                    "fixtures V2 congeladas de stocks e brasileirao recusadas nos dois sentidos")
gates["DOMAIN_QUALIFIED_IDS"] = p("PASS", [f"{R}/isolation/SUMMARY.json"],
                                  "mesmo H9 nos três domínios, IDs distintos; ID sem domínio recusado")
gates["CONTRADICTION_PRESERVATION"] = p("PASS", [f"{R}/isolation/SUMMARY.json"],
                                        "SUPPORTED × REFUTED → REQUIRE_HUMAN; os dois fatos preservados; sem maioria")
gates["DOMAIN_CONTRACTS_PRESERVED"] = p("PASS", [f"{M}/RAW_LOGS/contract-revalidation-c14/static_checks.json",
                                                 f"{R}/cleanroom-final/conformance.junit.xml",
                                                 f"{R}/contract-revalidation/SUMMARY.json",
                                                 f"{M}/CONTRACT_REVALIDATION_REPORT.md"],
                                        "C24.3 (a)–(f) verdes")
hosted = json.load(open(f"{M}/RAW_LOGS/hosted-ci/final-c14/HOSTED_CI_SUMMARY.json", encoding="utf-8"))
hosted_ok = all(item["ok"] for item in hosted)
gates["HOSTED_CI"] = p("PASS" if hosted_ok else "FAIL",
                       [f"{M}/RAW_LOGS/hosted-ci/baseline/HOSTED_CI_SUMMARY.json",
                        f"{M}/RAW_LOGS/hosted-ci/final-c14/HOSTED_CI_SUMMARY.json", f"{M}/HOSTED_CI_REPORT.md"],
                       "runs de push nos SHAs exatos dos final_commits (cain 10744a9, ecosystem 61f3ac4, cripto ee3d3d1) " + ("todos verdes" if hosted_ok else "com job não verde: ver resumo") + "; o ecosystem da base (49ffb16) ficou vermelho depois só pelo IC-F004, que 61d3430 corrige")
S = f"{M}/RAW_LOGS/runtime/run36360088636"
if "soak" not in g["phases_completed"]:
    g["phases_completed"].append("soak")
gates["SOAK"] = p("PASS", [f"{S}/run.json", f"{S}/soak/SUMMARY.json", f"{S}/soak/commands.log",
                           f"{M}/QUALIFICATION_PROFILE_INTEGRATION_CRYPTO_V1.json", f"{M}/SOAK_REPORT.md"],
                  "perfil V1 sem mudança, todos os pisos atingidos, tolerância zero, com as wheels finais da "
                  "reemissão; soaks anteriores mantidos em RAW_LOGS e listados no SOAK_REPORT")
gates["PROTECTED_ARTIFACTS_UNCHANGED"] = p("PASS", [f"{M}/RAW_LOGS/protected-c14/protected_check.json",
                                                    f"{M}/PROTECTED_SET.json", f"{M}/PROTECTED_ARTIFACT_REPORT.md"],
                                           "conjunto protegido do truth-map igual no final_commit do cripto e no "
                                           "checkout do predictor-qualification")
gates["EVIDENCE_CONSISTENCY"] = p("PASS", [f"{M}/EVIDENCE_NUMBERS.json", f"{M}/scripts/evidence_numbers.py",
                                           f"{M}/scripts/render_reports.py",
                                           f"{M}/RAW_LOGS/final-wheels-c14/final_wheels_check_run36360075557.json",
                                           f"{M}/RAW_LOGS/final-wheels-c14/final_wheels_check_run36360088636.json"],
                                  "números dos relatórios gerados de RAW_LOGS por script versionado; RAW_LOGS "
                                  "-text no .gitattributes (bytes preservados); final_wheels conferidas contra os "
                                  "assets e contra o instalado nos dois runs (C7.1 regra 4)")
findings = json.load(open(f"{M}/FINDINGS.json", encoding="utf-8"))
blocking = [f["id"] for f in findings["findings"]
            if f["status"] in findings["open_statuses"] and f["severity"] in ("P0", "P1")]
gates["BLOCKERS_ZERO"] = p("FAIL" if blocking else "PASS", [f"{M}/FINDINGS.json"],
                           ("P0/P1 abertos: " + ", ".join(blocking)) if blocking else
                           "nenhum P0/P1 aberto; IC-F004 corrigido pela renovação genuína do harness do cripto")
g["final_result"] = ("QUALIFIED" if all(v["status"] == "PASS" for v in gates.values()) and not blocking
                     else "NOT_QUALIFIED")
superseded = sorted(Path(M).glob("QUALIFICATION_ATTESTATION_superseded_*.json"))
if superseded:
    g["supersedes_sha256"] = hashlib.sha256(superseded[-1].read_bytes()).hexdigest()
g["domain_revalidation"] = {"status": "PASS", "evidence": [f"{M}/RAW_LOGS/contract-revalidation-c14/static_checks.json",
                                                           f"{R}/cleanroom-final/conformance.junit.xml",
                                                           f"{R}/contract-revalidation/SUMMARY.json"]}
open(f"{M}/GATES.json", "w", encoding="utf-8").write(json.dumps(g, indent=1, ensure_ascii=False) + "\n")
print({k: v["status"] for k, v in gates.items()})
print(len(wheels), "final wheels")
