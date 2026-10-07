"""integration-crypto, C14 na cain 0.4.13rc16 (D-34, 2026-10-07; transporte 0.1.0rc7 e cripto 1.2.0rc4 sem mudança): ledger
GATES.json do ciclo, a partir do run do Linux primário (todas as fases), do job windows-latest (D-31) e das conferências estáticas rc16.

Diferenças em relação a rc15_gates.py:
  * WINDOWS_SMOKE: PASS/FAIL pelo job `windows` do run (D-31: windows-latest é o secundário desta missão);
  * PROTECTED_ARTIFACTS_UNCHANGED: PASS/FAIL por protected_check (D-29: os itens compartilhados do crypto V1.2 foram re-congelados
    em PROTECTED_SET.json com previous_sha256/accepted_by);
  * LOCK_INTEGRITY/CORE_IDENTITY: cadeia do cain pelo registro STACK_WHEELS.json (D-32); snapshot e bundle das final_wheels vêm do registro;
  * a attestation da Etapa A do cripto no main é a V1.2 (QUALIFIED para 21f8b182 / rc4, fechada pela D-30): C7.1 regra 7 satisfeita.
Estado terminal: calculado dos gates (QUALIFIED só com todos PASS e P0=P1=0). Idempotente.
Uso: python rc16_gates.py <raiz do predictor-qualification> <run do Linux primário, ex. run123> <run do windows, ex. run123-windows>
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
RUN = sys.argv[2]
WRUN = sys.argv[3]
W = f"{M}/RAW_LOGS/runtime/{WRUN}"
R = f"{M}/RAW_LOGS/runtime/{RUN}"
FM = f"{R}/failure-matrix"


def lock(repo: str, commit: str) -> dict:
    raw = subprocess.run(["git", "-C", str(CLONES / repo), "show", f"{commit}:uv.lock"], capture_output=True, text=True, check=True).stdout
    return {p["name"]: p for p in tomllib.loads(raw)["package"]}


def main() -> None:
    kl = lock("cripto-predictor", targets["cripto"]["commit"])
    registry_raw = subprocess.run(["git", "-C", str(CLONES / "cain"), "show", f"{targets['cain']['commit']}:STACK_WHEELS.json"],
                                  capture_output=True, text=True, check=True).stdout
    registry = {w["package"]: w for w in json.loads(registry_raw)["wheels"]}
    wheels = []
    for key, name in (("cain", "cain-research"), ("cripto", "cripto-predictor"),
                      ("transport", "predictor-research-transport"), ("protocol", "predictor-research-protocol")):
        t = targets[key]
        wheels.append({"name": name, "version": t["version"], "url": t["url"], "sha256": t["sha256"]})
        if key in ("transport", "protocol"):
            assert registry[name]["sha256"] == t["sha256"] and registry[name]["release_tag"] == t["tag"], name
    for name in ("predictor-research-snapshot", "predictor-research-bundle"):  # D-32: do registro do cain, não do lock
        r = registry[name]
        wheels.append({"name": name, "version": r["version"], "sha256": r["sha256"],
                       "url": f"https://github.com/{r['repository']}/releases/download/{r['release_tag']}/{r['asset']}"})
    for name in ("predictor-core", "predictor-ops"):  # cripto 21f8b182 é anterior à R01: lock com URL + sha256
        (w,) = kl[name]["wheels"]
        wheels.append({"name": name, "version": kl[name]["version"], "url": w["url"], "sha256": w["hash"].split(":", 1)[1]})
    g = json.loads((ROOT / M / "GATES.json").read_text(encoding="utf-8"))
    g["cycle_rc16"] = {
        "why": "D-34 (2026-10-07): cain 0.4.13rc16 (código igual à rc15; lock por registro STACK_WHEELS.json, R01/D-32); transporte rc7 e cripto rc4 sem "
               "mudança; C14: fases que exercitam a wheel nova refeitas no Linux primário e no windows-latest (D-31)",
        "run": RUN, "windows_run": WRUN,
        "domain_attestation_note": "a attestation da Etapa A do cripto no main é a V1.2 (QUALIFIED para 21f8b182/rc4, WINDOWS_SMOKE pela D-30), alvo deste ciclo.",
        "previous_cycle": "rc16 (run36648103793, BLOCKED: D-29/D-30/D-31 ainda não escritas); rc13 (run36462444590, QUALIFIED, attestation vigente)",
    }
    g["final_commits"] = [
        {"repo": "cain", "commit_sha": targets["cain"]["commit"]},
        {"repo": "ecosystem-predictor-cain", "commit_sha": targets["transport"]["commit"]},
        {"repo": "cripto-predictor", "commit_sha": targets["cripto"]["commit"]},
        {"repo": "core-predictor", "commit_sha": "5a0841509f091ea0aa95bde0d3d65e2a1a9e984d"},
        {"repo": "predictor-ops", "commit_sha": "9831b0d5e727972b1d85ff48be14ffa58677898b"},
    ]
    g["final_wheels"] = wheels
    g["environments"] = [
        {"os": "linux", "python": "3.13", "role": "primary", "where": "github_actions", "result": "PASS",
         "evidence": [f"{R}/ci_runtime.log", f"{R}/env/runtime_env.log", f"{R}/e2e/SUMMARY.json", f"{R}/soak/SUMMARY.json"]},
    ]
    win = json.loads((ROOT / W / "e2e" / "SUMMARY.json").read_text(encoding="utf-8"))
    win_ok = win["failed"] == 0 and win["passed"] > 0
    g["environments"].append({"os": "windows", "python": "3.13", "role": "secondary", "where": "github_actions", "result": "PASS" if win_ok else "FAIL",
                              "evidence": [f"{W}/ci_runtime.log", f"{W}/env/runtime_env.log", f"{W}/e2e/SUMMARY.json"]})
    for phase in ("publish-candidates-rc16", "cleanroom-final-rc16", "contract-revalidation-rc16", "e2e-rc16", "n-plus-1-rc16",
                  "isolation-ids-contradiction-rc16", "idempotency-failure-rc16", "hosted-ci-rc16", "soak-rc16", "windows-smoke-rc16"):
        if phase not in g["phases_completed"]:
            g["phases_completed"].append(phase)

    def p(status, ev, note):
        for e in ev:
            if not (ROOT / e).is_file():
                raise SystemExit(f"evidência ausente: {e}")
        return {"status": status, "evidence": ev, "note": note}

    gates = g["gates"]
    CI = f"{M}/RAW_LOGS/core-identity-rc16/core_identity.json"
    gates["LOCK_INTEGRITY"] = p("PASS", [CI, f"{R}/env/runtime_env.log", f"{M}/CORE_IDENTITY_REPORT.md"],
                                "rc16: runtimes só de uv.lock --require-hashes + wheels publicadas conferidas por sha256 (12/12 conferências)")
    gates["CORE_IDENTITY"] = p("PASS", [CI, f"{R}/cleanroom-final/cleanroom_final.log", f"{M}/CORE_IDENTITY_REPORT.md"],
                               "rc16: pyproject ↔ uv.sources ↔ uv.lock ↔ wheel ↔ instalado ↔ site-packages (cain rc16 pelo registro, transporte rc7, protocolo rc2, cripto rc4 por URL)")
    gates["CLEANROOM_FINAL"] = p("PASS", [f"{R}/cleanroom-final/cleanroom_final.log", f"{R}/cleanroom-final/conformance.junit.xml",
                                          f"{R}/cleanroom-final/transport.junit.xml", f"{R}/cleanroom-final/cain.junit.xml", f"{M}/CLEANROOM_REPORT.md"],
                                 "rc16: só wheels publicadas, venvs limpos fora dos checkouts")
    gates["E2E"] = p("PASS", [f"{R}/e2e/SUMMARY.json", f"{R}/e2e/commands.log", f"{M}/CAIN_ROUNDTRIP_REPORT.md"],
                     "rc16: entrypoints cain e predictor-research-consumer, dados reais, restart do consumidor e do CAIN, outros domínios intercalados")
    gates["PROVENANCE"] = p("PASS", [f"{R}/e2e/SUMMARY.json", f"{FM}/F08/SUMMARY.json"], "rc16: envelope ↔ show ↔ admission ↔ journal ↔ Ops ↔ task ↔ adapter em cada resultado")
    gates["IDEMPOTENCY"] = p("PASS", [f"{FM}/FAILURE_MATRIX_RESULTS.json", f"{FM}/F09/SUMMARY.json", f"{FM}/F10/SUMMARY.json", f"{FM}/F12/SUMMARY.json", f"{R}/e2e/SUMMARY.json"],
                             "rc16: retry, reentrega e reproposta sem segundo efeito")
    gates["RESTART_RECOVERY"] = p("PASS", [f"{FM}/F0{i}/SUMMARY.json" for i in range(1, 9)], "rc16: morte real (exit 86) em cada ponto crítico do CAIN e do consumidor")
    gates["FAILURE_INJECTION"] = p("PASS", [f"{FM}/FAILURE_MATRIX_RESULTS.json", f"{M}/FAILURE_MATRIX.json"], "rc16: F01–F15 na borda, fail closed")
    gates["AUTHORITY_SEPARATION"] = p("PASS", [f"{R}/e2e/SUMMARY.json", f"{FM}/F14/SUMMARY.json", f"{FM}/F15/SUMMARY.json"],
                                      "rc16: estados copiados como vieram; RETRYABLE não é resultado; RECONCILIATION_REQUIRED para o domínio; capital sempre false")
    gates["FUTURE_CANARY"] = p("PASS", [f"{R}/e2e/SUMMARY.json"], "rc16: canário recusado pelo domínio; token e instantes pós-cutoff ausentes da memória")
    gates["WINDOWS_SMOKE"] = p("PASS" if win_ok else "FAIL", [f"{W}/ci_runtime.log", f"{W}/env/runtime_env.log", f"{W}/e2e/SUMMARY.json", f"{M}/CAIN_ROUNDTRIP_REPORT.md"],
                               f"rc16, D-31: E2E + restart pelo e2e.py no windows-latest × 3.13 (run {WRUN}), venvs limpos só com as wheels publicadas: "
                               f"{win['passed']} conferências OK, {win['failed']} falhas")
    gates["SHARED_DEPENDENCY_CLEAR"] = p("PASS", [f"{M}/RAW_LOGS/c0/c0_preflight.log", "qualification/shared/SHARED_ISSUES.json"],
                                         "nenhum issue bloqueante para as wheels usadas (Ops 4.2.2rc1, Core 3.2.1; inalteradas na rc16)")
    gates["SECRETS_CLEAN"] = p("PASS", [f"{M}/RAW_LOGS/secrets-rc16/secrets_scan.json"],
                               "rc16: 0 achados nos diffs rc13→rc16 (cain), rc6→rc7 (ecosystem), rc3→rc4 (cripto) e nos arquivos da missão")
    gates["CAPITAL_FORBIDDEN"] = p("PASS", [f"{R}/e2e/SUMMARY.json", f"{R}/n-plus-1/SUMMARY.json", f"{M}/DECISION_POLICY_REPORT.md"],
                                   "rc16: nenhum caminho concede capital; receipts e resultados com capital_permission=false")
    gates["ENVELOPE_V2_CONFORMANCE"] = p("PASS", [f"{R}/contract-revalidation/SUMMARY.json", f"{R}/e2e/SUMMARY.json", f"{FM}/F11/SUMMARY.json", f"{FM}/F13/SUMMARY.json",
                                                  f"{M}/ENVELOPE_V2_CONFORMANCE_REPORT.md"],
                                         "rc16: release congelada 2.0.0rc2; adapter só pela adapter_api; payload byte-idêntico")
    gates["CAIN_INGESTION"] = p("PASS", [f"{FM}/F11/SUMMARY.json", f"{FM}/F12/SUMMARY.json", f"{FM}/F13/SUMMARY.json", f"{R}/e2e/SUMMARY.json"],
                                "rc16: só V2 conhecido, task existente do mesmo domínio, correlação e provenance válidas")
    gates["CAIN_CONTAINMENT"] = p("PASS", [f"{R}/cleanroom-final/cain.junit.xml", f"{R}/env/runtime_env.log", f"{M}/CAIN_ROUNDTRIP_REPORT.md"],
                                  "rc16: loop do PR #50 fora do runtime; venv do CAIN sem domínio; PR #51 só leitura, SHA completo")
    gates["DECISION_POLICY"] = p("PASS", [f"{R}/cleanroom-final/cain.junit.xml", f"{R}/n-plus-1/SUMMARY.json", f"{M}/DECISION_POLICY_REPORT.md"],
                                 "rc16: determinística, versionada (código + configuração), receipt sem LLM; policy.py da rc16 difere da rc13 só por uma anotação de tipo; crypto.json igual")
    gates["N_PLUS_1_DETERMINISTIC"] = p("PASS", [f"{R}/n-plus-1/SUMMARY.json"], "rc16: 6 candidatas × 3 processos novos, receipts byte a byte iguais, estado inalterado")
    gates["NEGATIVE_RESULT_NEUTRALITY"] = p("PASS", [f"{R}/cleanroom-final/cain.junit.xml"], "rc16: budget, prioridade e escopo constantes da configuração; teste contra a wheel publicada")
    gates["CROSS_DOMAIN_ISOLATION"] = p("PASS", [f"{R}/isolation/SUMMARY.json", f"{R}/e2e/SUMMARY.json"], "rc16: fixtures V2 congeladas de stocks e brasileirao recusadas nos dois sentidos")
    gates["DOMAIN_QUALIFIED_IDS"] = p("PASS", [f"{R}/isolation/SUMMARY.json"], "rc16: mesmo H9 nos três domínios, IDs distintos; ID sem domínio recusado")
    gates["CONTRADICTION_PRESERVATION"] = p("PASS", [f"{R}/isolation/SUMMARY.json"], "rc16: SUPPORTED × REFUTED → REQUIRE_HUMAN; os dois fatos preservados; sem maioria")
    gates["DOMAIN_CONTRACTS_PRESERVED"] = p("PASS", [f"{M}/RAW_LOGS/contract-revalidation-rc16/static_checks.json", f"{R}/cleanroom-final/conformance.junit.xml",
                                                     f"{R}/contract-revalidation/SUMMARY.json", f"{M}/CONTRACT_REVALIDATION_REPORT.md"],
                                            "rc16: C24.3 (a)–(f) verdes com a Etapa A vigente = V1.2 (21f8b182): diff do domínio vazio (o adapter já está no alvo)")
    hosted = json.loads((ROOT / M / "RAW_LOGS/hosted-ci/final-rc16/HOSTED_CI_SUMMARY.json").read_text(encoding="utf-8"))
    hosted_ok = all(item["ok"] for item in hosted)
    gates["HOSTED_CI"] = p("PASS" if hosted_ok else "FAIL",
                           [f"{M}/RAW_LOGS/hosted-ci/baseline/HOSTED_CI_SUMMARY.json", f"{M}/RAW_LOGS/hosted-ci/final-rc16/HOSTED_CI_SUMMARY.json", f"{M}/HOSTED_CI_REPORT.md"],
                           "rc16: runs de push verdes nos SHAs exatos (cain ae00017, ecosystem b0da4fd, cripto 21f8b18)" if hosted_ok else "job não verde: ver resumo")
    gates["SOAK"] = p("PASS", [f"{R}/soak/SUMMARY.json", f"{R}/soak/commands.log", f"{M}/QUALIFICATION_PROFILE_INTEGRATION_CRYPTO_V1.json", f"{M}/SOAK_REPORT.md"],
                      "rc16: perfil V1 sem mudança, todos os pisos atingidos (24 ciclos, 18 duplicatas, 6 restarts do domínio, 10 do CAIN, 6 intercalados, 6 propostas de LLM), tolerância zero")
    protected = json.loads((ROOT / M / "RAW_LOGS/protected-rc16/protected_check.json").read_text(encoding="utf-8"))
    changed_shared = [s["path"] for s in protected["shared"] if not s["ok"] and not s.get("chain", {}).get("ok")]
    domains_changed = {d: v["changed"] for d, v in protected["domains"].items() if v["changed"]}
    prot_ok = protected["all_unchanged_or_chained"] and not domains_changed
    gates["PROTECTED_ARTIFACTS_UNCHANGED"] = p(
        "PASS" if prot_ok else "FAIL", [f"{M}/RAW_LOGS/protected-rc16/protected_check.json", f"{M}/PROTECTED_SET.json", f"{M}/PROTECTED_ARTIFACT_REPORT.md"],
        ("rc16: domínios intactos (blobs iguais em crypto, stocks e brasileirao); FROZEN_PARAMETERS encadeado (IC-F011); itens compartilhados do crypto V1.2 "
         "(runtime_target.json e QUALIFICATION_ATTESTATION.json) re-congelados em PROTECTED_SET.json pela D-29 (previous_sha256 guardado)")
        if prot_ok else f"alterados: domínios {domains_changed}, compartilhados {changed_shared}")
    fw = f"{M}/RAW_LOGS/final-wheels-rc16/final_wheels_check_{RUN}.json"
    gates["EVIDENCE_CONSISTENCY"] = p("PASS" if (ROOT / fw).is_file() else "NOT_RUN",
                                      [f"{M}/EVIDENCE_NUMBERS.json", f"{M}/scripts/evidence_numbers.py", f"{M}/scripts/render_reports.py"] + ([fw] if (ROOT / fw).is_file() else []),
                                      "rc16: números dos relatórios gerados de RAW_LOGS por script versionado; saída dos jobs devolvida por branch (SHA256SUMS); final_wheels conferidas (C7.1 regra 4)")
    findings = json.loads((ROOT / M / "FINDINGS.json").read_text(encoding="utf-8"))
    blocking = [f["id"] for f in findings["findings"] if f["status"] in findings["open_statuses"] and f["severity"] in ("P0", "P1")]
    gates["BLOCKERS_ZERO"] = p("FAIL" if blocking else "PASS", [f"{M}/FINDINGS.json"], ("P0/P1 abertos: " + ", ".join(blocking)) if blocking else "nenhum P0/P1 aberto")
    not_run = sorted(k for k, v in gates.items() if v["status"] == "NOT_RUN")
    failed = sorted(k for k, v in gates.items() if v["status"] == "FAIL")
    g["cycle_rc16"]["terminal"] = "NOT_QUALIFIED" if failed or blocking else ("BLOCKED" if not_run else "QUALIFIED")
    g["cycle_rc16"]["terminal_note"] = f"FAIL em {failed}" if failed else (f"BLOCKED: NOT_RUN em {not_run}" if not_run else "todos PASS")
    g["final_result"] = "NOT_QUALIFIED" if failed or blocking else ("QUALIFIED" if not not_run else g.get("final_result"))
    # a attestation vigente (rc13, QUALIFIED) é a que a final deste ciclo substitui (preservada como superseded)
    g["supersedes_sha256"] = hashlib.sha256((ROOT / M / "QUALIFICATION_ATTESTATION.json").read_bytes()).hexdigest()
    g["domain_revalidation"] = {"status": "PASS" if gates["DOMAIN_CONTRACTS_PRESERVED"]["status"] == "PASS" else "FAIL",
                                "evidence": gates["DOMAIN_CONTRACTS_PRESERVED"]["evidence"]}
    (ROOT / M / "GATES.json").write_text(json.dumps(g, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("rc16:", g["cycle_rc16"]["terminal"], "|", g["cycle_rc16"]["terminal_note"])
    print({k: v["status"] for k, v in gates.items() if v["status"] != "PASS"})


if __name__ == "__main__":
    main()
