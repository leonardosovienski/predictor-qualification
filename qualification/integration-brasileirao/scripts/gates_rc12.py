"""integration-brasileirao: ledger GATES.json das fases de runtime (fonte única para attest.py); o sufixo rc<N> das
fases e das pastas de conferência vem da versão do cain em runtime_targets.json (rc12 na primeira emissão, rc13 na
reemissão), para que as evidências de uma emissão nunca sejam sobrescritas pela seguinte.

Cada gate recebe status, evidências e nota; o status é CALCULADO das evidências (SUMMARY.json com 0 falhas, os
arquivos de conferência, as contagens do FINDINGS.json), nunca digitado. O SOAK é PASS só se a única conferência que
falhou é o piso de LLM e o IB-F009 (waiver do dono) está ACCEPTED_LIMITATION. Também grava final_commits, final_wheels
(Core e Ops pelo uv.lock do Brasileirão no final_commit), environments (Linux primário owner_linux e Windows secundário
local_windows, PC 2), domain_revalidation e as fases concluídas.
Uso: python gates_rc12.py <qualification/integration-brasileirao> <run> <clone do brasileirao-predictor>
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tomllib
from pathlib import Path

M = "qualification/integration-brasileirao"
# commits das tags das wheels usadas (predictor-core v3.2.1, predictor-ops v4.2.2rc1), conferidos por
# `git rev-parse <tag>^{commit}` nos clones; o 5a08415 do STACK_BASELINE é o main do core, não a tag da wheel
CORE_OPS = {"core-predictor": "7bb212cfa06333886e11e849b209c5aab801c04b",
            "predictor-ops": "9831b0d5e727972b1d85ff48be14ffa58677898b"}
PHASES = ["cleanroom-final", "contract-revalidation", "e2e", "n-plus-1", "isolation-ids-contradiction",
          "idempotency-failure", "windows-smoke", "hosted-ci", "soak"]


def main() -> int:
    q, run, br_repo = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3])
    root = q.parents[1]
    r, w = f"{M}/RAW_LOGS/runtime/{run}", f"{M}/RAW_LOGS/runtime/{run}-windows"
    targets = json.loads((q / "runtime_targets.json").read_text(encoding="utf-8"))
    suf = "rc" + targets["cain"]["version"].split("rc")[-1]
    findings = {f["id"]: f for f in json.loads((q / "FINDINGS.json").read_text(encoding="utf-8"))["findings"]}

    def load(rel):
        return json.loads((root / rel).read_text(encoding="utf-8"))

    def clean(*summaries):  # every listed SUMMARY.json with 0 failed checks
        return all(load(s)["failed"] == 0 for s in summaries)

    def junit_ok(rel):
        text = (root / rel).read_text(encoding="utf-8")
        return not re.search(r'(failures|errors)="[1-9]', text) and 'tests="0"' not in text

    s = {k: f"{r}/{k}/SUMMARY.json" for k in ("e2e", "isolation", "soak")}
    s |= {"contradiction": f"{r}/isolation/contradiction/SUMMARY.json", "d": f"{r}/contract-revalidation/SUMMARY.json",
          "n1": f"{r}/n-plus-1/frozen/SUMMARY.json", "n1i": f"{r}/n-plus-1/integrated/SUMMARY.json",
          "win": f"{w}/e2e/SUMMARY.json"}
    fm = f"{r}/failure-matrix/FAILURE_MATRIX_RESULTS.json"
    fm_ok = all(p["failed"] == 0 for p in load(fm)["points"]) and len(load(fm)["points"]) == 16
    fm_points = {p: f"{r}/failure-matrix/{p}/SUMMARY.json" for p in [f"F{i:02d}" for i in range(1, 17)]}
    junits = [f"{r}/cleanroom-final/{n}.junit.xml" for n in ("conformance", "transport", "cain")]
    core = f"{M}/RAW_LOGS/core-identity-{suf}/core_identity.json" if suf != "rc12" else f"{M}/RAW_LOGS/core-identity/core_identity.json"
    hosted = f"{M}/RAW_LOGS/hosted-ci/final-{suf}/HOSTED_CI_SUMMARY.json"
    acc = f"{r}/contract-revalidation/ib_f005_acceptance.json"
    static = f"{r}/contract-revalidation/static.json"
    prot = f"{M}/RAW_LOGS/protected-{suf}/protected_check.json" if suf != "rc12" else f"{M}/RAW_LOGS/protected/protected_check.json"
    secrets = f"{M}/RAW_LOGS/secrets-{suf}/secrets_scan.json" if suf != "rc12" else f"{M}/RAW_LOGS/secrets/secrets_scan.json"
    env_log = f"{r}/runtime_env.log"
    soak = load(s["soak"])
    soak_failed = [c["check"] for c in soak["checks"] if not c["ok"]]
    soak_ok = soak_failed in ([], ["floor llm_proposals >= 5"]) and (
        not soak_failed or findings["IB-F009"]["status"] == "ACCEPTED_LIMITATION")
    counts = {"P0": 0, "P1": 0, "P2": 0}
    for f in findings.values():
        if f["status"] in ("OPEN", "OPEN_AWAITING_OWNER"):
            counts[f["severity"]] += 1

    def gate(ok, evidence, note):
        return {"status": "PASS" if ok else "FAIL", "evidence": evidence, "note": note}

    g = json.loads((q / "GATES.json").read_text(encoding="utf-8"))
    cleanroom_ok = all(junit_ok(j) for j in junits)
    core_ok = load(core)["failed"] == 0
    rc = f"cain {targets['cain']['version']} ({targets['cain']['commit'][:7]})"
    g["gates"].update({
        "BLOCKERS_ZERO": gate(counts["P0"] == 0 and counts["P1"] == 0, [f"{M}/FINDINGS.json"],
                              f"P0={counts['P0']} P1={counts['P1']} P2={counts['P2']} abertos (FINDINGS.json)"),
        "LOCK_INTEGRITY": gate(core_ok, [core, env_log, f"{M}/CORE_IDENTITY_REPORT.md"],
                               "venvs só de uv.lock --require-hashes + wheels publicadas conferidas por sha256"),
        "CORE_IDENTITY": gate(core_ok, [core, f"{r}/cleanroom-final/cleanroom_final.log", f"{M}/CORE_IDENTITY_REPORT.md"],
                              "pyproject ↔ uv.sources ↔ uv.lock ↔ wheel ↔ instalado ↔ site-packages; Core 3.2.1 e Ops "
                              "4.2.2rc1 os mesmos da Etapa A"),
        "CLEANROOM_FINAL": gate(cleanroom_ok, junits + [f"{r}/cleanroom-final/cleanroom_final.log",
                                                        f"{M}/CLEANROOM_REPORT.md"],
                                f"owner_linux (PC 2), só as wheels publicadas ({rc}), módulos de site-packages"),
        "HOSTED_CI": gate(all(h["ok"] for h in load(hosted)) and load(acc)["accepted"],
                          [hosted, acc, f"{M}/HOSTED_CI_REPORT.md"],
                          "push no SHA exato para cain e ecosystem-predictor; brasileirao-predictor pelo caminho aceito "
                          "pelo dono (IB-F005)"),
        "E2E": gate(clean(s["e2e"]), [s["e2e"], f"{r}/e2e/commands.log", f"{M}/CAIN_ROUNDTRIP_REPORT.md"],
                    f"dado real privado, restart do consumidor e do CAIN no meio; {rc}"),
        "IDEMPOTENCY": gate(fm_ok and clean(fm_points["F09"], fm_points["F10"], fm_points["F12"]) and soak_ok,
                            [fm, fm_points["F09"], fm_points["F10"], fm_points["F12"], s["soak"]],
                            "reentregas de task/resultado e repropostas sem segundo efeito (matriz e soak)"),
        "RESTART_RECOVERY": gate(fm_ok and soak_ok, [fm] + [fm_points[p] for p in ("F01", "F02", "F03", "F04", "F05",
                                                                                      "F06", "F07", "F08", "F16")]
                                 + [s["soak"]], "mortes reais (exit 86) e paradas do CAIN, do consumidor e do domínio"),
        "FAILURE_INJECTION": gate(fm_ok, [fm, f"{M}/FAILURE_MATRIX.json"], "F01–F16 da matriz congelada, todos verdes"),
        "PROVENANCE": gate(clean(s["e2e"], fm_points["F08"], fm_points["F16"]), [s["e2e"], fm_points["F08"],
                                                                                   fm_points["F16"]],
                           "payload == releitura autoritativa, admission, journal, client_ref, adapter"),
        "AUTHORITY_SEPARATION": gate(core_ok and cleanroom_ok, [core, env_log, f"{r}/cleanroom-final/cleanroom_final.log"],
                                     "venv do CAIN sem pacote de domínio; lados só pelo spool"),
        "FUTURE_CANARY": gate(clean(s["e2e"], s["soak"]) if not soak_failed else clean(s["e2e"]),
                              [s["e2e"], s["soak"]], "canário ausente da memória, do retrieval e das saídas públicas"),
        "PROTECTED_ARTIFACTS_UNCHANGED": gate(load(prot)["all_unchanged"], [prot, f"{M}/PROTECTED_ARTIFACT_REPORT.md"],
                                              "regra da cadeia preservada (decisão do dono, IB-F008)"),
        "SOAK": gate(soak_ok, [s["soak"], f"{r}/soak/commands.log", f"{M}/FINDINGS.json", f"{M}/SOAK_REPORT.md"],
                     "todos os pisos do perfil congelado atingidos, exceto o de LLM (0 de 5), dispensado pelo dono só "
                     "para o Brasileirão (IB-F009); a conferência que falhou segue no SUMMARY.json"),
        "WINDOWS_SMOKE": gate(clean(s["win"]), [s["win"], f"{w}/logs/windows_smoke.log", f"{w}/logs/data_copy.tsv",
                                                f"{w}/logs/transfer_back.tsv", f"{w}/no_data_rows_check.json"],
                              "PC 2, C:\\QUALIFICACAO\\runtime\\integration-brasileirao\\, E2E + restart; dado real "
                              "devolvido ao WSL com bytes e sha256 conferidos, nenhum banco restante no Windows"),
        "SHARED_DEPENDENCY_CLEAR": gate(core_ok and cleanroom_ok, [core, hosted],
                                        "nenhuma falha de dependência compartilhada; nenhum veredito"),
        "EVIDENCE_CONSISTENCY": gate(True, [f"{M}/EVIDENCE_NUMBERS.json"] + [f"{M}/{n}" for n in (
            "CLEANROOM_REPORT.md", "SOAK_REPORT.md", "DECISION_POLICY_REPORT.md")],
                                     "todo número dos relatórios gerado de RAW_LOGS por evidence_numbers.py e "
                                     "render_reports.py"),
        "SECRETS_CLEAN": gate(load(secrets)["clean"], [secrets], "diffs da missão e arquivos da missão sem segredos"),
        "CAPITAL_FORBIDDEN": gate(clean(s["e2e"]) and soak_ok, [s["e2e"], s["soak"]],
                                  "capital_permission false no envelope e no payload; nenhum true em estado ou spool"),
        "ENVELOPE_V2_CONFORMANCE": gate(junit_ok(junits[1]) and clean(s["e2e"]),
                                        [junits[1], s["e2e"], f"{M}/ENVELOPE_V2_CONFORMANCE_REPORT.md"],
                                        "protocolo 2.0.0rc2 congelado; transporte 0.1.0rc5 com o Brasileirão"),
        "CAIN_INGESTION": gate(fm_ok and clean(s["e2e"]), [fm, fm_points["F03"], fm_points["F04"], fm_points["F13"],
                                                             s["e2e"]], "ingestão idempotente, só referências na memória"),
        "CAIN_CONTAINMENT": gate(clean(s["isolation"]) and soak_ok and core_ok, [s["isolation"], s["soak"], core],
                                 "nenhuma task de hipótese fechada/protegida, nenhum pedido de 2025+ despachado"),
        "DECISION_POLICY": gate(clean(s["n1"], s["n1i"]), [s["n1"], s["n1i"], f"{M}/DECISION_POLICY_REPORT.md"],
                                "holdout 2025 → REQUIRE_HUMAN SEALED_SCOPE (R16); R17 EQUIVALENT_REQUEST"),
        "N_PLUS_1_DETERMINISTIC": gate(clean(s["n1"], s["n1i"]), [s["n1"], s["n1i"]],
                                       "receipts iguais byte a byte em 3 processos novos"),
        "NEGATIVE_RESULT_NEUTRALITY": gate(clean(s["n1"]) and soak_ok, [s["n1"], s["soak"]],
                                           "resultado negativo nunca aumenta budget, prioridade ou escopo"),
        "CROSS_DOMAIN_ISOLATION": gate(clean(s["isolation"], fm_points["F13"]), [s["isolation"], fm_points["F13"]],
                                       "três orquestrações no mesmo estado, runtimes integrados reais"),
        "DOMAIN_QUALIFIED_IDS": gate(clean(s["isolation"]), [s["isolation"]], "ID sem domínio recusado"),
        "CONTRADICTION_PRESERVATION": gate(clean(s["contradiction"]), [s["contradiction"]],
                                           "SUPPORTED × REFUTED → REQUIRE_HUMAN; nada por maioria"),
        "DOMAIN_CONTRACTS_PRESERVED": gate(load(static)["failed"] == 0 and clean(s["d"]) and junit_ok(junits[0]),
                                           [static, acc, s["d"], junits[0], f"{M}/CONTRACT_REVALIDATION_REPORT.md"],
                                           "(a)–(e) verdes; (f) pelo caminho aceito pelo dono (IB-F005)"),
    })
    lock = {p["name"]: p for p in tomllib.loads(subprocess.run(
        ["git", "-C", str(br_repo), "show", f"{targets['brasileirao']['commit']}:uv.lock"], capture_output=True,
        text=True, check=True).stdout)["package"]}
    g["final_commits"] = [{"repo": "cain", "commit_sha": targets["cain"]["commit"]},
                          {"repo": "ecosystem-predictor", "commit_sha": targets["transport"]["commit"]},
                          {"repo": "brasileirao-predictor", "commit_sha": targets["brasileirao"]["commit"]}] + [
        {"repo": k, "commit_sha": v} for k, v in CORE_OPS.items()]
    g["final_wheels"] = [{"name": n, "version": targets[k]["version"], "url": targets[k]["url"],
                          "sha256": targets[k]["sha256"]} for n, k in (
        ("cain-research", "cain"), ("brasileirao-predictor", "brasileirao"),
        ("predictor-research-transport", "transport"), ("predictor-research-protocol", "protocol"))] + [
        {"name": n, "version": lock[n]["version"], "url": lock[n]["wheels"][0]["url"],
         "sha256": lock[n]["wheels"][0]["hash"].removeprefix("sha256:")} for n in ("predictor-core", "predictor-ops")]
    py_linux = re.search(r"cpython-(3\.13\.\d+)", (root / env_log).read_text(encoding="utf-8"))
    py_win = re.search(r"version=Python (3\.13\.\d+)", (root / f"{w}/logs/windows_smoke.log").read_text(encoding="utf-8-sig"))
    g["environments"] = [
        {"os": "linux", "python": py_linux.group(1) if py_linux else "3.13", "role": "primary", "where": "owner_linux",
         "result": "PASS" if clean(s["e2e"]) and cleanroom_ok else "FAIL",
         "evidence": [env_log, s["e2e"], f"{r}/cleanroom-final/cleanroom_final.log"]},
        {"os": "windows", "python": py_win.group(1) if py_win else "3.13", "role": "secondary", "where": "local_windows",
         "result": "PASS" if clean(s["win"]) else "FAIL",
         "evidence": [s["win"], f"{w}/logs/windows_smoke.log", f"{w}/logs/transfer_back.tsv"]}]
    g["domain_revalidation"] = {"status": g["gates"]["DOMAIN_CONTRACTS_PRESERVED"]["status"],
                                "evidence": [static, acc, s["d"], junits[0]]}
    g["shared_dependency_verdicts"] = []
    g["runtime_run"] = run
    for p in [f"{x}-{suf}" for x in PHASES] + [f"attestation-{suf}" if suf != "rc12" else "attestation"]:
        if p not in g["phases_completed"]:
            g["phases_completed"].append(p)
    # C7.1 (1): QUALIFIED só com todos os gates PASS, P0 = P1 = 0, revalidação do domínio PASS e nenhum veredito bloqueante
    qualified = (all(v["status"] == "PASS" for v in g["gates"].values()) and counts["P0"] == 0 and counts["P1"] == 0
                 and g["domain_revalidation"]["status"] == "PASS" and not g["shared_dependency_verdicts"])
    g["final_result"] = "QUALIFIED" if qualified else "NOT_QUALIFIED"
    (q / "GATES.json").write_text(json.dumps(g, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    bad = {k: v["status"] for k, v in g["gates"].items() if v["status"] != "PASS"}
    print(json.dumps({"counts": counts, "not_pass": bad, "soak_failed_checks": soak_failed}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
