"""integration-stocks, CICLO 7 (C14, D-34, 2026-10-07 noite: adoção da cain rc16 na lock conjunta do ecosystem, ecosystem 0.2.2; wheels do
runtime inalteradas): cópia de update_gates_c6.py com as constantes do ciclo 7 (diretórios -c7). Texto original abaixo.

integration-stocks: ledger GATES.json (fonte única dos estados de gate para scripts/attest.py), por fase C8.

Adaptado de qualification/integration-crypto/scripts/update_gates.py (mesma forma: final_commits/final_wheels,
ambientes, estado + evidências + nota por gate). Aqui cada fase do runtime aplica só os gates que ela comprova, para
que cada ATTESTATION_PARTIAL_<fase>.json registre o ledger daquela fase (C8). As fases do runtime rodaram num só run
do GitHub Actions (Linux primário: todas; Windows secundário: E2E + restart).

Reemissão 1 (2026-09-28): decisão do dono sobre IS-F004/IS-F005, opção (b) ("aceita o run workflow_dispatch (b) e
reemite"). HOSTED_CI e C24.3 (f) passam a ler a conferência mecânica dessa decisão; as evidências novas ficam em
diretórios com sufixo -r1, e os raw logs citados pela attestation anterior não mudam. A attestation anterior fica
preservada em QUALIFICATION_ATTESTATION_superseded_<sha12>.json (SUPERSEDED).

Ciclo 2 (C14; decisões do dono de 2026-09-28: "Aprovo o ciclo novo", "Hipóteses para o LLM", IS-F008 "(a) Encadeada" e
"Seguir para a rc12"): as constantes abaixo apontam para as evidências do ciclo 2 (run na cain 0.4.13rc12, diretórios
-c2/-rc12); as do ciclo 1 ficam no histórico do git e em GATES.json → cycle1_evidence. PROTECTED_ARTIFACTS_UNCHANGED
aplica a decisão do IS-F008: cada item alterado só passa encadeado salto a salto até o sha256 protegido.

Ciclo 4 (C14; decisões do dono de 2026-09-28: D-26 "Somar as famílias do main", "Só o transporte" e "Calibrar
embedding" → só revisão): as constantes apontam para as evidências do ciclo 4 (run na cain 0.4.13rc13 com o transporte
0.1.0rc6, diretórios -c4/-rc13); as do ciclo 2 ficam no histórico do git e em GATES.json → cycle2_evidence. As fases
refeitas entram em phases_completed com o sufixo do ciclo (-c2, -c4).

Uso: python update_gates.py <fase>   (aplica, cumulativamente, todas as fases até ela, na ordem de PHASES)
"""

import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

M = "qualification/integration-stocks"
RUN = "RUN_C7"  # ciclo 7 (ciclo 6: run37698400981)
R = f"{M}/RAW_LOGS/runtime/{RUN}"
W = f"{M}/RAW_LOGS/runtime/{RUN}-windows"
RUN_SOAK = "RUN_C7"  # ciclo 7: soak no mesmo run
# ficar em 4/5 no run36649880023 (IS-F010: qwen2.5:0.5b no ollama 0.35.0 estourou num_predict em 2 de 6 tentativas)
RS = f"{M}/RAW_LOGS/runtime/{RUN_SOAK}"
FM = f"{R}/failure-matrix"
HOSTED = f"{M}/RAW_LOGS/hosted-ci/final-c7"  # ciclo 5: final-rc15
STATIC = f"{M}/RAW_LOGS/contract-revalidation-c7/static_checks.json"
HOSTED_STOCKS = f"{M}/RAW_LOGS/hosted-ci/final-rc13"  # o stocks-predictor não mudou (6f857b2): o aceite do dono e os runs dele são os do ciclo 4
ACCEPTANCE = f"{HOSTED_STOCKS}/stocks_dispatch_acceptance.json"
PREFLIGHT = f"{M}/RAW_LOGS/c0/c0_preflight_37a0e28.log"  # pré-voo do ciclo 4 (C0 desta sessão em RAW_LOGS/c0-c5)
SECRETS = f"{M}/RAW_LOGS/secrets-c7/secrets_scan.json"
PROTECTED = f"{M}/RAW_LOGS/protected-c7/protected_check.json"  # ciclo 5: protected-c5
# a mesma conferência roda também num snapshot do main (git archive), para valer no estado depois do merge mesmo que o
# main receba mudanças de outras missões depois da base da branch
MAIN_SNAPSHOT = "MAIN_C7"  # snapshot (git archive) da branch do ciclo 7 (ciclo 6: 713b89d)
PROTECTED_MAIN = f"{M}/RAW_LOGS/protected-c7/protected_check_main_{MAIN_SNAPSHOT}.json"
CORE = f"{M}/RAW_LOGS/core-identity-c7/core_identity.json"  # ciclo 5: core-identity-c5
SUPERSEDED = "SUPERSEDED_C7"  # a attestation do ciclo 4, preservada na reemissão
TARGETS = __import__("json").load(open(f"{M}/runtime_targets.json", encoding="utf-8"))



# ---------------------------------------------------------------- decisões do dono em qualification/DECISIONS.json
def decision_approved(decision_id):
    doc = json.load(open("qualification/DECISIONS.json", encoding="utf-8"))
    return any(d.get("decision_id") == decision_id and d.get("status") == "APPROVED" for d in doc["decisions"])


def pin_chained(pin_path, expected_sha256):
    """D-29: o pin novo da Etapa A encadeia ao conteúdo protegido (previous.commit e previous.wheel_sha256 iguais aos do
    conteúdo com o sha256 registrado, recuperado do histórico do main)."""
    import subprocess
    cur = json.load(open(pin_path, encoding="utf-8"))
    prev = cur.get("previous") or {}
    for commit in subprocess.run(["git", "log", "--format=%H", "--", pin_path], capture_output=True, text=True, check=True).stdout.split():
        blob = subprocess.run(["git", "show", f"{commit}:{pin_path}"], capture_output=True, check=True).stdout
        if hashlib.sha256(blob).hexdigest() == expected_sha256:
            old = json.loads(blob)
            ok = old.get("commit") == prev.get("commit") and old.get("wheel_sha256") == prev.get("wheel_sha256")
            return ok, commit, old.get("version"), cur.get("version")
    return False, None, None, cur.get("version")

def p(status, ev, note):
    return {"status": status, "evidence": ev, "note": note}


def python_of(env_log):
    return re.search(r"^python=Python (\S+)", open(env_log, encoding="utf-8").read(), re.M).group(1)


def cleanroom_final(g, gates):
    g["environments"] = [e for e in g["environments"] if e["os"] != "linux"] + [
        {"os": "linux", "python": python_of(f"{R}/env/runtime_env.log"), "role": "primary", "where": "github_actions",
         "result": "PASS", "evidence": [f"{R}/run.json", f"{R}/ci_runtime.log", f"{R}/env/runtime_env.log",
                                        f"{R}/e2e/SUMMARY.json"]}]
    gates["LOCK_INTEGRITY"] = p("PASS", [CORE, f"{R}/env/runtime_env.log",
                                         f"{M}/CORE_IDENTITY_REPORT.md"],
                                "runtimes só de uv.lock --require-hashes + wheels publicadas conferidas por sha256; lado do CAIN pelo registro STACK_WHEELS.json (D-32)")
    gates["CORE_IDENTITY"] = p("PASS", [CORE,
                                        f"{R}/cleanroom-final/cleanroom_final.log", f"{M}/CORE_IDENTITY_REPORT.md"],
                               "stocks: pyproject ↔ uv.sources ↔ uv.lock ↔ wheel ↔ instalado ↔ site-packages; cain rc16: pyproject ↔ STACK_WHEELS.json ↔ uv.lock ↔ "
                               "fetch ↔ instalado (D-32); Core 3.2.1 e Ops 4.2.2rc1 os mesmos da Etapa A do Stocks")
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
    static = json.load(open(STATIC, encoding="utf-8"))
    d = json.load(open(f"{R}/contract-revalidation/SUMMARY.json", encoding="utf-8"))
    tree = ET.parse(f"{R}/cleanroom-final/conformance.junit.xml").getroot()
    suites = [tree] if tree.tag == "testsuite" else list(tree.iter("testsuite"))
    conf_ok = (sum(int(s.get("tests", 0)) for s in suites) > 0
               and sum(int(s.get(k, 0)) for s in suites for k in ("failures", "errors")) == 0)
    ev = [STATIC, f"{R}/cleanroom-final/conformance.junit.xml", f"{R}/contract-revalidation/SUMMARY.json"]
    f_check = next(c for c in static["checks"] if c["check"].startswith("(f)"))
    ok = static["failed"] == 0 and d["failed"] == 0 and conf_ok
    via = f_check.get("via")
    if ok:
        note = ("C24.3 (a)–(f) verdes; (f) " + ("pelo run de push" if via == "push" else
                                                "pelo run workflow_dispatch aceito pelo dono (IS-F004/IS-F005 b)"))
        status = "PASS"
    elif [c for c in static["checks"] if not c["ok"]] == [f_check] and d["failed"] == 0 and conf_ok:
        note = ("BLOCKED: (a)–(e) verdes; (f) sem run que conte no SHA exato do final_commit (IS-F004/IS-F005); "
                "decisão do dono pendente")
        status = "NOT_RUN"
    else:
        note, status = "C24.3 com falha: ver static_checks.json e SUMMARY.json", "FAIL"
    gates["DOMAIN_CONTRACTS_PRESERVED"] = p(status, ev + ([ACCEPTANCE] if via and via != "push" else [])
                                            + [f"{M}/CONTRACT_REVALIDATION_REPORT.md"], note)
    g["domain_revalidation"] = {"status": status, "evidence": ev}
    prot = json.load(open(PROTECTED, encoding="utf-8"))
    domain_changed = [c for d in prot["domains"].values() for c in d["changed"]]
    changed = domain_changed + [s["path"] for s in prot["shared"] if not s["ok"]]
    note = (f"conjunto protegido do truth-map ({prot['items_total']} itens) igual no final_commit do stocks e no "
            "checkout do predictor-qualification")
    status = "PASS"
    if changed:
        # decisão do dono sobre IS-F008 (opção a): só itens encadeados salto a salto até o sha256 protegido
        f008 = {x["id"]: x for x in json.load(open(f"{M}/FINDINGS.json", encoding="utf-8"))["findings"]}["IS-F008"]
        decided = f008["status"] == "ACCEPTED_LIMITATION" and "owner_decision_taken" in f008
        main = json.load(open(PROTECTED_MAIN, encoding="utf-8"))
        main_changed = [c for d in main["domains"].values() for c in d["changed"]] + [
            s["path"] for s in main["shared"] if not s["ok"]]
        accepted = (decided and not domain_changed and prot.get("all_unchanged_or_chained") is True
                    and set(changed) <= set(prot.get("chained_items", []))
                    and main.get("all_unchanged_or_chained") is True
                    and set(main_changed) <= set(main.get("chained_items", [])))
        pin = "qualification/crypto/runtime_target.json"
        external_only = (not domain_changed and pin in changed
                         and set(changed) - {pin} <= set(prot.get("chained_items", []))
                         and set(main_changed) - {pin} <= set(main.get("chained_items", [])))
        status = "PASS" if accepted else ("NOT_RUN" if external_only else "FAIL")
        d29 = None
        if not accepted and external_only and decision_approved("D-29"):
            expected = next(s["expected"] for s in prot["shared"] if s["path"] == pin)
            chained, at_commit, old_v, new_v = pin_chained(pin, expected)
            d29 = {"chained": chained, "protected_content_commit": at_commit, "from": old_v, "to": new_v}
            if chained:
                status, accepted = "PASS", True
        note = (f"{prot['items_total'] - len(changed)} de {prot['items_total']} itens iguais; alterados: "
                + ", ".join(changed) + ". Cada um com os bytes protegidos preservados e encadeados salto a salto "
                "(cycle.supersedes nos congelados, supersedes_sha256 nas attestations; conferido no "
                f"protected_check.json da branch e no do snapshot do main {MAIN_SNAPSHOT}); "
                + (f"pin qualification/crypto/runtime_target.json aceito pela D-29: {d29['from']} → {d29['to']}, previous.commit e "
                   f"previous.wheel_sha256 iguais ao conteúdo protegido (commit {d29['protected_content_commit'][:7]} do main); os 4 itens do "
                   "IS-F008 aceitos pela decisão do dono (opção a)" if d29 and d29["chained"] else
                   "aceito pela decisão do dono sobre IS-F008 (opção a)" if accepted else
                   ("BLOCKED: o pin do alvo da Etapa A do crypto mudou pela reabertura V1.2 (D-27), fora desta missão; aceitar o pin novo "
                    "é decisão do dono (mesmo caminho da IS-F008/IC-F011)" if external_only else
                    "FAIL pela letra da C15.1" + ("" if decided else ", decisão do dono pendente (IS-F008)"))))
    gates["PROTECTED_ARTIFACTS_UNCHANGED"] = p(status,
                                               [PROTECTED, PROTECTED_MAIN,
                                                f"{M}/PROTECTED_SET.json", f"{M}/FINDINGS.json",
                                                f"{M}/PROTECTED_ARTIFACT_REPORT.md"], note)


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
                                 "política v2 (R01–R17, policy.py com os bytes congelados) e configuração do stocks do "
                                 "ciclo 4 (17 famílias congeladas pela D-26; 8 hipóteses só para o LLM); IS-F002 e "
                                 "IS-F003 corrigidos no cain#62 (17-collection ALLOW no N+1)")
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
    ev = [f"{HOSTED}/HOSTED_CI_SUMMARY.json",
          f"{HOSTED_STOCKS}/stocks-predictor_run36363108348.json", f"{HOSTED_STOCKS}/stocks-predictor_run35953418753.json",
          f"{HOSTED_STOCKS}/stocks-predictor_run36363108348_secrets_job.log", f"{HOSTED_STOCKS}/secrets_job_steps.json",
          f"{HOSTED_STOCKS}/tree_scan_local.log", f"{M}/HOSTED_CI_REPORT.md"]
    acc = json.load(open(ACCEPTANCE, encoding="utf-8")) if Path(ACCEPTANCE).is_file() else None
    if finals.get("stocks-predictor"):
        gates["HOSTED_CI"] = p("PASS" if others else "FAIL", ev, "runs de push nos SHAs exatos dos final_commits")
    elif acc is not None and acc["accepted"]:
        tree_ok = "RESULTADO PASS" in open(f"{HOSTED_STOCKS}/tree_scan_local.log", encoding="utf-8").read()
        gates["HOSTED_CI"] = p(
            "PASS" if others else "FAIL", [ACCEPTANCE] + ev,
            f"cain {TARGETS['cain']['commit'][:7]} e ecosystem {TARGETS['transport']['commit'][:7]}: run de push verde "
            "no SHA exato"
            + ("" if others else " (NÃO: ver resumo)")
            + "; stocks-predictor 6f857b2: run workflow_dispatch 36363108348 no SHA exato aceito pelo dono "
            "(\"aceita o run workflow_dispatch (b) e reemite\", IS-F004/IS-F005 ACCEPTED_LIMITATION), conferido: Quality "
            "3.13/3.14 verdes, secrets vermelho só por 1 vazamento de um commit fora da branch da missão; com o "
            "gitleaks vermelho, a varredura da árvore e o controle não rodaram no Actions e foram reproduzidos "
            "localmente como diagnóstico" + (" (PASS)" if tree_ok else " (FALHA)")
            + "; base 61fc017: run workflow_dispatch da Etapa A, verde. Ciclo 7: o stocks-predictor não mudou (6f857b2), o aceite e os runs dele são os do ciclo 4 (final-rc13); cain (rc16) e ecosystem (renomeado) recoletados em final-c7")
    else:
        gates["HOSTED_CI"] = p("NOT_RUN" if others else "FAIL", ev,
                               ("BLOCKED: " if others else "")
                               + f"cain {TARGETS['cain']['commit'][:7]} e ecosystem "
                               f"{TARGETS['transport']['commit'][:7]} com run de push verde no SHA exato"
                               + ("" if others else " (NÃO: ver resumo)")
                               + "; stocks-predictor 6f857b2 sem run de push (ci.yml só em main: IS-F004) e o run "
                               "workflow_dispatch 36363108348 no SHA exato com Quality 3.13/3.14 verdes e o job secrets "
                               "vermelho por falso positivo pré-existente no histórico do main (IS-F005); decisão do "
                               "dono pendente")


def soak(g, gates):
    summary = json.load(open(f"{RS}/soak/SUMMARY.json", encoding="utf-8"))
    ok = summary["failed"] == 0
    gates["SOAK"] = p("PASS" if ok else "FAIL",
                      [f"{RS}/run.json", f"{RS}/soak/SUMMARY.json", f"{RS}/soak/commands.log",
                       f"{M}/QUALIFICATION_PROFILE_INTEGRATION_STOCKS_V1.json", f"{M}/SOAK_REPORT.md"],
                      f"ciclo 7: perfil V1 sem mudança, com as wheels finais, no run {RUN_SOAK}: {summary['passed']} conferências OK, "
                      f"{summary['failed']} falhas, llm_proposals {summary['counters']['llm_proposals']}; tolerância zero")


def attestation(g, gates):
    gates["SHARED_DEPENDENCY_CLEAR"] = p("PASS", [PREFLIGHT, "qualification/shared/SHARED_ISSUES.json"],
                                         "nenhum issue bloqueante para as wheels usadas (Ops 4.2.2rc1, Core 3.2.1)")
    scan = json.load(open(SECRETS, encoding="utf-8"))
    gates["SECRETS_CLEAN"] = p("PASS" if scan["clean"] else "FAIL", [SECRETS, f"{HOSTED_STOCKS}/tree_scan_local.log"],
                               f"{len(scan['findings'])} achados nos diffs da missão e nos arquivos da missão; o job "
                               "secrets do CI do stocks-predictor acusa só 1 vazamento de um commit fora da branch da "
                               "missão (IS-F005); a árvore do final_commit com o .gitleaks.toml do repo está limpa "
                               "(reprodução local do passo pulado)")
    # ciclo 7: a attestation que a final substitui é a vigente (ciclo 6), preservada como superseded
    g["supersedes_sha256"] = hashlib.sha256(Path(M, "QUALIFICATION_ATTESTATION.json").read_bytes()).hexdigest()
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
    number = g.get("cycle", {}).get("number", 1)
    suffix = f"-c{number}" if number >= 2 else ""  # ciclo n ≥ 2: as fases refeitas entram com -c<n>
    for name, apply in PHASES[: names.index(target) + 1]:
        apply(g, g["gates"])
        if name != "attestation" and name + suffix not in g["phases_completed"]:
            g["phases_completed"].append(name + suffix)
    open(f"{M}/GATES.json", "w", encoding="utf-8").write(json.dumps(g, indent=1, ensure_ascii=False) + "\n")
    print(target, {k: v["status"] for k, v in g["gates"].items() if v["status"] != "NOT_RUN" or "note" in v})
    print("final_result", g.get("final_result"))


if __name__ == "__main__":
    main()
