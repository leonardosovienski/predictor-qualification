"""Missão crypto: fecha os 5 gates da D-16 a partir da evidência bruta de d16_linux.sh
e emite a attestation final (C7.1 regra 8: a anterior é preservada byte a byte).

Pré-requisitos: D-16 APPROVED no DECISIONS.json; saída de d16_linux.sh copiada, sem
edição, para qualification/crypto/RAW_LOGS/d16/<id>/ (um run do Actions ou da máquina Linux).

Critérios (congelados em FROZEN_PARAMETERS / AUTHORITY_STATE_MATRIX / QUALIFICATION_PROFILE):
  E2E                         e2e_real/E2E_SUMMARY.json all_ok (entrypoint, restart, releitura, provenance)
  SOAK                        soak_real.jsonl verdict zero_tolerance_ok  e  cada classe de falha do perfil
                              (plan.failure_classes, nomes da FAILURE_MATRIX) executada ≥ minimums do perfil
  CRYPTO_UNCOMFORTABLE_CASES  e2e_cases (A, B, C ×3) all_ok  e  soak real (A ×3, C ×3) sem violações
  CRYPTO_ECONOMIC_METRICS     science: bruto e líquido separados, cada um com IC
  CRYPTO_NEGATIVE_CONTROLS    science: injeção de futuro 0, ablação 0, placebo SUPPORTED ≤ 10/100
Qualquer critério não atendido = FAIL (nunca PASS por pressuposto).

Uso: python d16_finalize.py <dir relativo: qualification/crypto/RAW_LOGS/d16/<id>>
Depois: python attest.py check qualification/crypto/QUALIFICATION_ATTESTATION.json
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
QC = ROOT / "qualification" / "crypto"
# as 6 classes de QUALIFICATION_PROFILE_CRYPTO_V1.plan.failure_classes, pelo nome da falha no log do soak
SOAK_FAILURE_CLASSES = ("ops_worker_crash", "ops_worker_hang", "host_killed_during_ops_job",
                        "before_admission_commit", "during_result_write", "result_file_corruption")


def main() -> None:
    rel = sys.argv[1].rstrip("/")
    d = ROOT / rel
    decisions = json.loads((ROOT / "qualification" / "DECISIONS.json").read_text(encoding="utf-8"))["decisions"]
    if not any(x["decision_id"] == "D-16" and x["status"] == "APPROVED" for x in decisions):
        raise SystemExit("D-16 não está APPROVED")
    env = (d / "env.log").read_text(encoding="utf-8")
    if "done " not in env or "SETUP FAIL" in env or "BLOCKED" in env:
        raise SystemExit("execução d16 incompleta ou bloqueada")
    target = json.loads((QC / "runtime_target.json").read_text(encoding="utf-8"))
    if f"commit={target['commit']}" not in env or target["wheel_sha256"] not in env:
        raise SystemExit("a execução não corresponde ao runtime_target.json atual")

    e2e = json.loads((d / "e2e_real" / "E2E_SUMMARY.json").read_text(encoding="utf-8"))
    cases = json.loads((d / "e2e_cases" / "E2E_SUMMARY.json").read_text(encoding="utf-8"))
    science = json.loads((d / "science" / "SCIENCE_REAL.json").read_text(encoding="utf-8"))
    soak = [json.loads(l) for l in (d / "soak_real.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    soak_summary = next(r for r in soak if r["kind"] == "summary")
    soak_verdict = next(r for r in soak if r["kind"] == "verdict")["zero_tolerance_ok"]
    profile = json.loads((QC / "QUALIFICATION_PROFILE_CRYPTO_V1.json").read_text(encoding="utf-8"))
    if len(profile["plan"]["failure_classes"]) != len(SOAK_FAILURE_CLASSES):
        raise SystemExit("perfil do soak com classes de falha diferentes das conferidas aqui")
    minimum = profile["minimums"]["runs_per_relevant_failure_class"]
    class_runs = {c: 0 for c in SOAK_FAILURE_CLASSES}
    for r in soak:
        name = "result_file_corruption" if r["kind"] == "corruption" else r.get("fault") if r["kind"] == "process" else None
        if name in class_runs:
            class_runs[name] += 1
    soak_ok = soak_verdict and all(n >= minimum for n in class_runs.values())
    junit = ET.parse(d / "conformance.junit.xml").getroot()
    suite = junit if junit.tag == "testsuite" else junit[0]
    conformance_ok = int(suite.get("failures", 1)) == 0 and int(suite.get("errors", 1)) == 0 and int(suite.get("skipped", 1)) == 0
    conformance_n = int(suite.get("tests", 0))

    econ = science["economic_metrics"]
    controls = science["negative_controls"]
    results = {
        "E2E": (e2e["all_ok"] and conformance_ok,
                ["e2e_real/E2E_SUMMARY.json", "conformance.junit.xml", "core_identity.json", "data_MANIFEST.json"],
                f"Linux primário, dados reais (D-16): {len(e2e['checks'])} checagens de E2E/restart/releitura/provenance "
                f"{'todas OK' if e2e['all_ok'] else 'COM FALHA'}; conformidade {conformance_n} testes {'verdes' if conformance_ok else 'COM FALHA'}."),
        "SOAK": (soak_ok, ["soak_real.jsonl"],
                 f"Perfil V1 com dados reais: {soak_summary['requests_with_result']} resultados, perdidos {len(soak_summary['lost'])}, "
                 f"violações {len(soak_summary['violations'])}, zero_tolerance_ok={soak_verdict}; execuções por classe de "
                 f"falha (mínimo {minimum}): {class_runs}."),
        "CRYPTO_UNCOMFORTABLE_CASES": (cases["all_ok"] and soak_ok, ["e2e_cases/E2E_SUMMARY.json", "soak_real.jsonl"],
                 "Casos A, B, C ×3 no runtime Linux (B com o vetor sintético congelado); A ×3 e C ×3 também sobre dados reais no soak."),
        "CRYPTO_ECONOMIC_METRICS": (bool(econ["separated_with_ci"]), ["science/SCIENCE_REAL.json"],
                 f"Dados reais, Linux: bruto {econ['gross_return_bps']} bps IC {econ['gross_ci_bps']}; líquido {econ['net_return_bps']} bps IC "
                 f"{econ['net_ci_bps']}; custos congelados; {econ['scientific_state']}/{econ['economic_state']}. Descritivo, sem edge nem capital."),
        "CRYPTO_NEGATIVE_CONTROLS": (all(c["pass"] for c in controls.values()) and science["future_canary"]["pass"],
                 ["science/SCIENCE_REAL.json"],
                 f"Injeção de futuro {controls['future_injection']['accepted_results']} aceitos; ablação {controls['temporal_ablation']['accepted_results']}; "
                 f"placebo SUPPORTED {controls['shuffled_labels']['supported']}/100 (≤10); vazamentos do canário {len(science['future_canary']['leaks'])}."),
    }
    ledger_path = QC / "GATES.json"
    g = json.loads(ledger_path.read_text(encoding="utf-8"))
    for gate, (ok, ev, note) in results.items():
        g["gates"][gate] = {"status": "PASS" if ok else "FAIL", "evidence": [f"{rel}/{e}" for e in ev], "note": note}
    linux_ok = all(ok for ok, _, _ in results.values())
    for envd in g["environments"]:
        if envd["role"] == "primary":
            envd.update(where="github_actions" if "d16 where=github_actions" in env else "cloud_vm",
                        result="PASS" if linux_ok else "FAIL",
                        evidence=[f"{rel}/env.log", f"{rel}/e2e_real/E2E_SUMMARY.json", f"{rel}/soak_real.jsonl"])
    if "d16" not in g["phases_completed"]:
        g["phases_completed"].append("d16")

    previous = QC / "QUALIFICATION_ATTESTATION.json"
    prev_sha = hashlib.sha256(previous.read_bytes()).hexdigest()
    kept = QC / f"QUALIFICATION_ATTESTATION_superseded_{prev_sha[:12]}.json"
    subprocess.run(["git", "-C", str(ROOT), "mv", str(previous), str(kept)], check=True)
    if hashlib.sha256(kept.read_bytes()).hexdigest() != prev_sha:
        raise SystemExit("preservação da attestation anterior falhou")
    g["supersedes_sha256"] = prev_sha
    all_pass = all(v["status"] == "PASS" for v in g["gates"].values())
    g["note"] = f"D-16 executada ({rel}); gates fechados por d16_finalize.py a partir da evidência bruta."
    g["final_result"] = "QUALIFIED" if all_pass else "NOT_QUALIFIED"
    ledger_path.write_text(json.dumps(g, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: g["gates"][k]["status"] for k in results}, ensure_ascii=False), "->", g["final_result"])
    print("agora: attest.py final  (emite QUALIFICATION_ATTESTATION.json com supersedes", prev_sha[:12] + "...)")


if __name__ == "__main__":
    main()
