"""integration-stocks: ledger GATES.json (fonte única dos estados de gate para scripts/attest.py), por fase C8.

Adaptado de qualification/integration-crypto/scripts/update_gates.py (mesma forma: final_commits/final_wheels,
ambientes, estado + evidências + nota por gate). Aqui cada fase do runtime aplica só os gates que ela comprova, para
que cada ATTESTATION_PARTIAL_<fase>.json registre o ledger daquela fase (C8). As fases do runtime rodaram num só run
do GitHub Actions (Linux primário: todas; Windows secundário: E2E + restart).

Uso: python update_gates.py <fase>   (aplica, cumulativamente, todas as fases até ela, na ordem de PHASES)
"""

import json
import re
import sys

M = "qualification/integration-stocks"
RUN = "run36365355063"
R = f"{M}/RAW_LOGS/runtime/{RUN}"
W = f"{M}/RAW_LOGS/runtime/{RUN}-windows"
FM = f"{R}/failure-matrix"
HOSTED = f"{M}/RAW_LOGS/hosted-ci/final"


def p(status, ev, note):
    return {"status": status, "evidence": ev, "note": note}


def python_of(env_log):
    return re.search(r"^python=Python (\S+)", open(env_log, encoding="utf-8").read(), re.M).group(1)


def cleanroom_final(g, gates):
    g["environments"] = [e for e in g["environments"] if e["os"] != "linux"] + [
        {"os": "linux", "python": python_of(f"{R}/env/runtime_env.log"), "role": "primary", "where": "github_actions",
         "result": "PASS", "evidence": [f"{R}/run.json", f"{R}/ci_runtime.log", f"{R}/env/runtime_env.log",
                                        f"{R}/e2e/SUMMARY.json"]}]
    gates["LOCK_INTEGRITY"] = p("PASS", [f"{M}/RAW_LOGS/core-identity/core_identity.json", f"{R}/env/runtime_env.log",
                                         f"{M}/CORE_IDENTITY_REPORT.md"],
                                "runtimes só de uv.lock --require-hashes + wheels publicadas conferidas por sha256")
    gates["CORE_IDENTITY"] = p("PASS", [f"{M}/RAW_LOGS/core-identity/core_identity.json",
                                        f"{R}/cleanroom-final/cleanroom_final.log", f"{M}/CORE_IDENTITY_REPORT.md"],
                               "pyproject ↔ uv.sources ↔ uv.lock ↔ wheel ↔ instalado ↔ site-packages; Core 3.2.1 e "
                               "Ops 4.2.2rc1 os mesmos da Etapa A do Stocks")
    gates["CLEANROOM_FINAL"] = p("PASS", [f"{R}/cleanroom-final/cleanroom_final.log",
                                          f"{R}/cleanroom-final/conformance.junit.xml",
                                          f"{R}/cleanroom-final/adapters.junit.xml",
                                          f"{R}/cleanroom-final/transport.junit.xml",
                                          f"{R}/cleanroom-final/cain.junit.xml", f"{M}/CLEANROOM_REPORT.md"],
                                 "só wheels publicadas, venvs limpos fora dos checkouts")
    gates["CAIN_CONTAINMENT"] = p("PASS", [f"{R}/cleanroom-final/cain.junit.xml", f"{R}/env/runtime_env.log",
                                           f"{M}/CAIN_ROUNDTRIP_REPORT.md"],
                                  "modo operacional do CAIN fora do runtime; venv do CAIN sem domínio; o loop só "
                                  "propõe pela DecisionPolicy")
    gates["NEGATIVE_RESULT_NEUTRALITY"] = p("PASS", [f"{R}/cleanroom-final/cain.junit.xml",
                                                     f"{M}/DECISION_POLICY_REPORT.md"],
                                            "budget, prioridade e escopo são constantes da configuração do stocks; "
                                            "teste de neutralidade contra a wheel publicada")


def contract_revalidation(g, gates):
    blocked = ("BLOCKED: (a), (b), (c), (d) e (e) verdes; (f) CI do domínio no SHA exato do final_commit sem run que "
               "conte: nenhum run de push (IS-F004) e o run workflow_dispatch tem o job secrets vermelho por falso "
               "positivo pré-existente no histórico do main (IS-F005); decisão do dono pendente")
    ev = [f"{M}/RAW_LOGS/contract-revalidation/static_checks.json", f"{R}/cleanroom-final/conformance.junit.xml",
          f"{R}/contract-revalidation/SUMMARY.json"]
    gates["DOMAIN_CONTRACTS_PRESERVED"] = p("NOT_RUN", ev + [f"{M}/CONTRACT_REVALIDATION_REPORT.md"], blocked)
    g["domain_revalidation"] = {"status": "NOT_RUN", "evidence": ev}
    prot = json.load(open(f"{M}/RAW_LOGS/protected/protected_check.json", encoding="utf-8"))
    changed = [c for d in prot["domains"].values() for c in d["changed"]] + [s["path"] for s in prot["shared"]
                                                                             if not s["ok"]]
    note = (f"conjunto protegido do truth-map ({prot['items_total']} itens) igual no final_commit do stocks e no "
            "checkout do predictor-qualification")
    if changed:
        note = (f"{prot['items_total'] - len(changed)} de {prot['items_total']} itens iguais; alterados: "
                + ", ".join(changed) + ". A attestation da integration-crypto foi reemitida pela C14 prevista em "
                "FROZEN_PARAMETERS.c14_integration_crypto, com os bytes protegidos preservados no arquivo _superseded_ "
                "e encadeados por supersedes_sha256; FAIL pela letra da C15.1, decisão do dono pendente (IS-F006)")
    gates["PROTECTED_ARTIFACTS_UNCHANGED"] = p("FAIL" if changed else "PASS",
                                               [f"{M}/RAW_LOGS/protected/protected_check.json",
                                                f"{M}/PROTECTED_SET.json", f"{M}/PROTECTED_ARTIFACT_REPORT.md"], note)


def e2e(g, gates):
    gates["E2E"] = p("PASS", [f"{R}/e2e/SUMMARY.json", f"{R}/e2e/commands.log", f"{M}/CAIN_ROUNDTRIP_REPORT.md"],
                     "entrypoints cain e predictor-research-consumer, dados reais públicos (B3/CVM), restart do "
                     "consumidor e do CAIN, outros domínios intercalados")
    gates["FUTURE_CANARY"] = p("PASS", [f"{R}/e2e/SUMMARY.json"],
                               "canário FUTURE_CANARY_STOCKS_INTEGRATION_001 recusado pelo domínio; token e instantes "
                               "pós-cutoff ausentes da memória do CAIN")


def n_plus_1(g, gates):
    gates["N_PLUS_1_DETERMINISTIC"] = p("PASS", [f"{R}/n-plus-1/frozen/SUMMARY.json",
                                                 f"{R}/n-plus-1/integrated/SUMMARY.json"],
                                        "candidatas congeladas × 3 processos novos, receipts byte a byte iguais, "
                                        "estado inalterado; variante integrada com resultado real no spool")
    gates["DECISION_POLICY"] = p("PASS", [f"{R}/cleanroom-final/cain.junit.xml", f"{R}/n-plus-1/frozen/SUMMARY.json",
                                          f"{M}/DECISION_POLICY_REPORT.md"],
                                 "determinística, versionada (código + configuração do stocks), receipt sem LLM; "
                                 "limites do framework registrados em IS-F002 e IS-F003 (P2)")
    gates["CAPITAL_FORBIDDEN"] = p("PASS", [f"{R}/e2e/SUMMARY.json", f"{R}/n-plus-1/frozen/SUMMARY.json",
                                            f"{M}/DECISION_POLICY_REPORT.md"],
                                   "nenhum caminho concede capital; receipts e resultados com capital_permission=false")


def isolation(g, gates):
    gates["CROSS_DOMAIN_ISOLATION"] = p("PASS", [f"{R}/isolation/SUMMARY.json", f"{R}/e2e/SUMMARY.json"],
                                        "cripto integrado no mesmo estado do CAIN e fixtures V2 congeladas do "
                                        "brasileirao recusadas nos dois sentidos")
    gates["DOMAIN_QUALIFIED_IDS"] = p("PASS", [f"{R}/isolation/SUMMARY.json"],
                                      "mesmo H<n> em domínios diferentes, IDs distintos; ID sem domínio recusado")
    gates["CONTRADICTION_PRESERVATION"] = p("PASS", [f"{R}/isolation/contradiction/SUMMARY.json"],
                                            "SUPPORTED × REFUTED → REQUIRE_HUMAN; os dois fatos preservados; sem "
                                            "maioria")


def idempotency_failure(g, gates):
    gates["IDEMPOTENCY"] = p("PASS", [f"{FM}/FAILURE_MATRIX_RESULTS.json", f"{FM}/F09/SUMMARY.json",
                                      f"{FM}/F10/SUMMARY.json", f"{FM}/F12/SUMMARY.json", f"{R}/e2e/SUMMARY.json"],
                             "retry, reentrega e reproposta sem segundo efeito")
    gates["RESTART_RECOVERY"] = p("PASS", [f"{FM}/F0{i}/SUMMARY.json" for i in range(1, 9)],
                                  "morte real (exit 86) em cada ponto crítico do CAIN e do consumidor")
    gates["FAILURE_INJECTION"] = p("PASS", [f"{FM}/FAILURE_MATRIX_RESULTS.json", f"{M}/FAILURE_MATRIX.json"],
                                   "F01–F15 na borda, fail closed")
    gates["PROVENANCE"] = p("PASS", [f"{R}/e2e/SUMMARY.json", f"{FM}/F08/SUMMARY.json"],
                            "envelope ↔ show ↔ admission ↔ journal ↔ Ops ↔ task ↔ adapter em cada resultado")
    gates["AUTHORITY_SEPARATION"] = p("PASS", [f"{R}/e2e/SUMMARY.json", f"{FM}/F14/SUMMARY.json",
                                               f"{FM}/F15/SUMMARY.json"],
                                      "estados copiados como vieram; RETRYABLE não é resultado; "
                                      "RECONCILIATION_REQUIRED para o domínio; capital sempre false")
    gates["ENVELOPE_V2_CONFORMANCE"] = p("PASS", [f"{R}/contract-revalidation/SUMMARY.json", f"{R}/e2e/SUMMARY.json",
                                                  f"{FM}/F11/SUMMARY.json", f"{FM}/F13/SUMMARY.json",
                                                  f"{M}/ENVELOPE_V2_CONFORMANCE_REPORT.md"],
                                         "release congelada 2.0.0rc2; adapter só pela adapter_api; payload "
                                         "byte-idêntico")
    gates["CAIN_INGESTION"] = p("PASS", [f"{FM}/F11/SUMMARY.json", f"{FM}/F12/SUMMARY.json", f"{FM}/F13/SUMMARY.json",
                                         f"{R}/e2e/SUMMARY.json"],
                                "só V2 conhecido, task existente do mesmo domínio, correlação e provenance válidas")


def windows_smoke(g, gates):
    g["environments"] = [e for e in g["environments"] if e["os"] != "windows"] + [
        {"os": "windows", "python": python_of(f"{W}/env/runtime_env.log"), "role": "secondary",
         "where": "github_actions", "result": "PASS",
         "evidence": [f"{W}/run.json", f"{W}/ci_runtime.log", f"{W}/env/runtime_env.log", f"{W}/e2e/SUMMARY.json"]}]
    gates["WINDOWS_SMOKE"] = p("PASS", [f"{W}/e2e/SUMMARY.json", f"{W}/e2e/commands.log", f"{W}/ci_runtime.log"],
                               "GitHub Actions windows-latest (D-1: nada instalado no Windows do PC 2), E2E + restart "
                               "com as wheels publicadas")


def hosted_ci(g, gates):
    hosted = json.load(open(f"{HOSTED}/HOSTED_CI_SUMMARY.json", encoding="utf-8"))
    finals = {s["repo"].split("/")[1]: s["ok"] for s in hosted if s["role"] == "final"}
    others = all(ok for repo, ok in finals.items() if repo != "stocks-predictor")
    ev = [f"{M}/RAW_LOGS/hosted-ci/collection-1/HOSTED_CI_SUMMARY.json", f"{HOSTED}/HOSTED_CI_SUMMARY.json",
          f"{M}/RAW_LOGS/hosted-ci/stocks-predictor_6f857b2_run36363108348.json",
          f"{M}/RAW_LOGS/hosted-ci/stocks-predictor_6f857b2_run36363108348_secrets_job.log", f"{M}/HOSTED_CI_REPORT.md"]
    if finals.get("stocks-predictor"):
        gates["HOSTED_CI"] = p("PASS" if others else "FAIL", ev, "runs de push nos SHAs exatos dos final_commits")
    else:
        gates["HOSTED_CI"] = p("NOT_RUN" if others else "FAIL", ev,
                               ("BLOCKED: " if others else "")
                               + "cain deccaaa e ecosystem 1304b20 com run de push verde no SHA exato"
                               + ("" if others else " (NÃO: ver resumo)")
                               + "; stocks-predictor 6f857b2 sem run de push (ci.yml só em main: IS-F004) e o run "
                               "workflow_dispatch 36363108348 no SHA exato com Quality 3.13/3.14 verdes e o job secrets "
                               "vermelho por falso positivo pré-existente no histórico do main (IS-F005); decisão do "
                               "dono pendente")


def soak(g, gates):
    gates["SOAK"] = p("PASS", [f"{R}/run.json", f"{R}/soak/SUMMARY.json", f"{R}/soak/commands.log",
                               f"{M}/QUALIFICATION_PROFILE_INTEGRATION_STOCKS_V1.json", f"{M}/SOAK_REPORT.md"],
                      "perfil V1 sem mudança, todos os pisos atingidos, tolerância zero, com as wheels finais")


def attestation(g, gates):
    gates["SHARED_DEPENDENCY_CLEAR"] = p("PASS", [f"{M}/RAW_LOGS/c0/c0_preflight_fd1fb5e.log",
                                                  "qualification/shared/SHARED_ISSUES.json"],
                                         "nenhum issue bloqueante para as wheels usadas (Ops 4.2.2rc1, Core 3.2.1)")
    gates["SECRETS_CLEAN"] = p("PASS", [f"{M}/RAW_LOGS/secrets/secrets_scan.json"],
                               "0 achados nos diffs da missão e nos arquivos da missão; o job secrets do CI do "
                               "stocks-predictor acusa só o falso positivo do main (IS-F005), fora desta branch")
    gates["EVIDENCE_CONSISTENCY"] = p("PASS", [f"{M}/EVIDENCE_NUMBERS.json", f"{M}/scripts/evidence_numbers.py",
                                               f"{M}/scripts/render_reports.py",
                                               f"{M}/RAW_LOGS/final-wheels/final_wheels_check_{RUN}.json"],
                                      "números dos relatórios gerados de RAW_LOGS por script versionado; final_wheels "
                                      "conferidas contra os assets e contra o instalado no run (C7.1 regra 4)")
    findings = json.load(open(f"{M}/FINDINGS.json", encoding="utf-8"))
    blocking = [f["id"] for f in findings["findings"]
                if f["status"] in ("OPEN", "OPEN_AWAITING_OWNER") and f["severity"] in ("P0", "P1")]
    gates["BLOCKERS_ZERO"] = p("FAIL" if blocking else "PASS", [f"{M}/FINDINGS.json"],
                               ("P0/P1 abertos: " + ", ".join(blocking)) if blocking else "nenhum P0/P1 aberto")
    g["final_result"] = ("QUALIFIED" if all(v["status"] == "PASS" for v in gates.values()) and not blocking
                         and g["domain_revalidation"]["status"] == "PASS" else "NOT_QUALIFIED")


PHASES = [("cleanroom-final", cleanroom_final), ("contract-revalidation", contract_revalidation), ("e2e", e2e),
          ("n-plus-1", n_plus_1), ("isolation-ids-contradiction", isolation),
          ("idempotency-failure", idempotency_failure), ("windows-smoke", windows_smoke), ("hosted-ci", hosted_ci),
          ("soak", soak), ("attestation", attestation)]


def main():
    target = sys.argv[1]
    names = [n for n, _ in PHASES]
    if target not in names:
        raise SystemExit(f"fase desconhecida: {target}")
    g = json.load(open(f"{M}/GATES.json", encoding="utf-8"))
    for name, apply in PHASES[: names.index(target) + 1]:
        apply(g, g["gates"])
        if name != "attestation" and name not in g["phases_completed"]:
            g["phases_completed"].append(name)
    open(f"{M}/GATES.json", "w", encoding="utf-8").write(json.dumps(g, indent=1, ensure_ascii=False) + "\n")
    print(target, {k: v["status"] for k, v in g["gates"].items() if v["status"] != "NOT_RUN" or "note" in v})
    print("final_result", g.get("final_result"))


if __name__ == "__main__":
    main()
