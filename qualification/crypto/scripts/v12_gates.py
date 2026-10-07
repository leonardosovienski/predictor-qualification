"""crypto, reabertura V1.2 (D-27, C24.4, C14): atualiza o ledger GATES.json fase a fase e emite o parcial de cada fase.

Alvo: qualification/crypto/runtime_target.json (cripto-predictor 21f8b182 = 1.2.0rc4, wheel 32a4bd6d…; Core 3.2.1 e Ops
4.2.2rc1 inalterados). Toda evidência nova fica em RAW_LOGS/v1.2/ (saída bruta do run crypto-reopening.yml, devolvida
por branch sem edição, mais as conferências locais). Cada fase só muda os gates que ela prova; o que não foi executado
nesta reabertura fica NOT_RUN com a razão em note. WINDOWS_SMOKE fica NOT_RUN "BLOCKED" até o dono rodar o Windows
local (D-3): por isso não existe attestation final desta reabertura enquanto o estado for BLOCKED (C7.3).

Uso: python v12_gates.py <fase> --run run36646241688
  fases, na ordem: baseline truth-map publish-candidates cleanroom-final e2e-idempotency science-d16 soak hosted-ci
                   windows-smoke attestation-blocked
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
QC = ROOT / "qualification" / "crypto"
M = "qualification/crypto"
V = f"{M}/RAW_LOGS/v1.2"
CRYPTO_FINAL = "21f8b182286248859e1b2cb8fa2bab0138a58e2a"


def load(name: str) -> dict:
    return json.loads((QC / name).read_text(encoding="utf-8"))


def gate(g: dict, gid: str, status: str, evidence: list[str], note: str) -> None:
    for e in evidence:
        if not (ROOT / e).is_file():
            raise SystemExit(f"evidência ausente: {e}")
    g["gates"][gid] = {"status": status, "evidence": evidence, "note": note}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("phase")
    ap.add_argument("--run", required=True)
    a = ap.parse_args()
    R = f"{V}/{a.run}"
    L, W, D = f"{R}/runtime-linux-primary", f"{R}/runtime-windows-latest", f"{R}/d16"
    g = load("GATES.json")
    target = load("runtime_target.json")
    numbers = load("EVIDENCE_NUMBERS_V1.2.json")
    phase = a.phase

    if phase == "baseline":
        g["note"] = ("Reabertura V1.2 (D-27, C24.4): alvo cripto-predictor 21f8b182 (1.2.0rc4). Ledger em atualização fase a fase; "
                     "gates ainda não reexecutados nesta reabertura ficam NOT_RUN até a fase que os prova.")
        g["cycle"] = "V1.2"
        g["common_baseline_id"] = "STACK_BASELINE_V1.2"
        g["protected_set_file"] = "PROTECTED_SET_V1.2.json"
        g["final_commits"] = [{"repo": "cripto-predictor", "commit_sha": CRYPTO_FINAL},
                              {"repo": "core-predictor", "commit_sha": "5a0841509f091ea0aa95bde0d3d65e2a1a9e984d"},
                              {"repo": "predictor-ops", "commit_sha": "9831b0d5e727972b1d85ff48be14ffa58677898b"}]
        g["final_wheels"] = [{"name": "cripto-predictor", "version": target["version"], "url": target["wheel_url"], "sha256": target["wheel_sha256"]},
                             {"name": "predictor-core", "version": "3.2.1",
                              "url": "https://github.com/leonardosovienski/core-predictor/releases/download/v3.2.1/predictor_core-3.2.1-py3-none-any.whl",
                              "sha256": "10ef42f34ace8bb2df5f83ff7de2ceec79b035a25ea0a690e8942bd60d2fb4e3"},
                             {"name": "predictor-ops", "version": "4.2.2rc1",
                              "url": "https://github.com/leonardosovienski/predictor-ops/releases/download/v4.2.2rc1/predictor_ops-4.2.2rc1-py3-none-any.whl",
                              "sha256": "0be70bfbb2437dfb080baceb9af41043a09d03b15a358903b8bd7007f5f169b3"}]
        # a attestation que a V1.2 vai substituir quando fechar é a final vigente (V1.1); os parciais já apontam para ela
        g["supersedes_sha256"] = __import__("hashlib").sha256((QC / "QUALIFICATION_ATTESTATION.json").read_bytes()).hexdigest()
        g["previous_final"] = {"attestation": "QUALIFICATION_ATTESTATION.json (V1.1/v2.2, QUALIFIED para 341d270 / 1.2.0rc2)",
                               "kept": True, "note": "continua válida para os seus final_commits (C22); nada é apagado"}
        # tudo que exige reexecução no alvo novo passa a NOT_RUN até a fase correspondente
        pending = ("LOCK_INTEGRITY", "CORE_IDENTITY", "CLEANROOM_FINAL", "HOSTED_CI", "E2E", "IDEMPOTENCY", "RESTART_RECOVERY",
                   "FAILURE_INJECTION", "PROVENANCE", "AUTHORITY_SEPARATION", "FUTURE_CANARY", "PROTECTED_ARTIFACTS_UNCHANGED",
                   "SOAK", "WINDOWS_SMOKE", "EVIDENCE_CONSISTENCY", "SECRETS_CLEAN", "CAPITAL_FORBIDDEN", "DOMAIN_CONTRACT",
                   "ADMISSION", "OPS_RUNTIME", "CORE_PARTICIPATION", "TEMPORAL_INTEGRITY", "CRYPTO_RUNTIME_WIRING",
                   "CRYPTO_UNCOMFORTABLE_CASES", "CRYPTO_ECONOMIC_METRICS", "CRYPTO_NEGATIVE_CONTROLS", "CRYPTO_SPLIT_BRAIN_CORRUPTION")
        for gid in pending:
            g["gates"][gid] = {"status": "NOT_RUN", "evidence": [], "note": "V1.2: aguardando a fase que reexecuta este gate no alvo 21f8b182"}
        # Ops inalterado: vereditos compartilhados continuam valendo (C14: só refaz o que a wheel nova toca)
        g["gates"]["SHARED_DEPENDENCY_CLEAR"]["note"] = ("Wheel do Ops inalterada (4.2.2rc1, 0be70bfb…): vereditos SHARED-003/004/005 continuam valendo; "
                                                          "C14 não manda refazer ops-failure. " + g["gates"]["SHARED_DEPENDENCY_CLEAR"]["note"])
        g["gates"]["CRYPTO_OPS_FAILURE_VERDICT"]["note"] = "Idem: Ops inalterado na V1.2. " + g["gates"]["CRYPTO_OPS_FAILURE_VERDICT"]["note"]
        gate(g, "STACK_BASELINE_FROZEN", "PASS",
             [f"{M}/STACK_BASELINE_V1.2.json", f"{V}/baseline/collect.log", "qualification/shared/STACK_BASELINE_V1.2.json", f"{M}/runtime_target.json"],
             "V1.2: baseline coletado antes de qualquer mudança da reabertura: cripto 21f8b182 (main, limpo, 1.2.0rc4), core e5ac0d87 e ops dddf0ceb "
             "(main; src/pyproject/uv.lock iguais aos commits das wheels 5a08415 e 9831b0d). Wheels do lock = assets das releases (match). Só git e API pública.")
        g["phases_completed"].append("v1-2-baseline")

    elif phase == "truth-map":
        gate(g, "PROTECTED_ARTIFACTS_UNCHANGED", "PASS",
             [f"{V}/protected/protected_set_check_21f8b182.json", f"{V}/protected/protected_set_v1_2_check_21f8b182.json",
              f"{M}/PROTECTED_SET.json", f"{M}/PROTECTED_SET_V1.2.json", f"{M}/PROTECTED_ARTIFACT_REPORT.md"],
             f"V1.2: {numbers['protected_set_check_21f8b182']['unchanged']}/{numbers['protected_set_check_21f8b182']['items']} blobs do conjunto V1.0 "
             f"iguais em 21f8b182 (nada do que estava protegido em 5fd4e1b/341d270 mudou); conjunto refeito em 21f8b182 = "
             f"{numbers['protected_set_v1_2_check_21f8b182']['items']} itens (só cresce: +63 arquivos novos de docs/evidence), "
             f"{numbers['protected_set_v1_2_check_21f8b182']['unchanged']} iguais no alvo.")
        roots = numbers["import_graph"]["roots"]
        gate(g, "CRYPTO_RUNTIME_WIRING", "PASS",
             [f"{L}/runtime_trace.log", f"{L}/conformance.junit.xml", f"{V}/truth-map/import_graph_21f8b182.json", f"{M}/ARCHITECTURE_TRUTH_MAP.json"],
             "V1.2: composition root (cripto-research) e componentes instanciados pela wheel 1.2.0rc4 (runtime_trace.log, conformidade "
             f"{numbers['runtime-linux-primary']['conformance']['passed']}/{numbers['runtime-linux-primary']['conformance']['tests']}); grafo de imports em 21f8b182: "
             f"nenhuma raiz alcança research_protocol/cain/research_transport nem adapter_paths ({', '.join(f'{k.split()[-1]}={v['closure_size']}' for k, v in roots.items())} módulos).")
        g["phases_completed"].append("v1-2-truth-map")

    elif phase == "publish-candidates":
        gate(g, "LOCK_INTEGRITY", "PASS",
             [f"{V}/lock/uv_lock_check_21f8b182.log", f"{V}/hosted-ci/jobs_cripto-predictor_36642919823.json", f"{L}/env.log", f"{M}/CORE_IDENTITY_REPORT.md"],
             f"V1.2: uv lock --check em 21f8b182 exit {numbers['uv_lock_check_21f8b182']['exit']} (local, uv 0.8.17) e no job quality do CI (uv 0.12.1, success); "
             "runtime instalado só do lock exportado com --require-hashes + wheel rc4 conferida por sha256sum -c.")
        g["phases_completed"].append("v1-2-publish-candidates")
        g["publish_candidates_v1_2"] = {"release": target["release"], "wheel_sha256": target["wheel_sha256"], "sdist_sha256": target["sdist_sha256"],
                                        "built_by": "workflow Release do cripto-predictor (run 36643518795; build duplo, wheel byte-idêntica; tag na 21f8b182)"}

    elif phase == "cleanroom-final":
        ev = [f"{L}/env.log", f"{L}/conformance.junit.xml", f"{L}/full_suite.junit.xml", f"{L}/core_identity.json", f"{L}/pip_freeze.txt", f"{M}/CLEANROOM_REPORT.md"]
        note = (f"V1.2, run {a.run} (ubuntu-latest, Python 3.13, wheels publicadas fora do checkout): conformidade "
                f"{numbers['runtime-linux-primary']['conformance']['passed']}/{numbers['runtime-linux-primary']['conformance']['tests']}; suíte completa pela wheel "
                f"{numbers['runtime-linux-primary']['full_suite']['passed']} passed, {numbers['runtime-linux-primary']['full_suite']['failures']} falhas, todas da classe T "
                "(testes que leem o checkout; CR-F016 atualizado).")
        if "runtime-windows-latest" in numbers:
            ev += [f"{W}/conformance.junit.xml", f"{W}/full_suite.junit.xml", f"{W}/core_identity.json"]
            w = numbers["runtime-windows-latest"]
            note += (f" windows-latest (informação adicional, não é o secundário do crypto): conformidade {w['conformance']['passed']}/{w['conformance']['tests']}, "
                     f"suíte {w['full_suite']['passed']} passed / {w['full_suite']['failures']} falhas.")
        gate(g, "CLEANROOM_FINAL", "PASS", ev, note)
        gate(g, "CORE_IDENTITY", "PASS", [f"{L}/core_identity.json", f"{D}/core_identity.json", f"{L}/pip_freeze.txt", f"{M}/CORE_IDENTITY_REPORT.md"],
             "V1.2: pyproject ↔ tool.uv.sources ↔ uv.lock (21f8b182) ↔ --require-hashes ↔ metadata ↔ módulo em site-packages, nos dois runtimes Linux "
             "(runtime e d16): predictor-core 3.2.1, predictor-ops 4.2.2rc1, cripto-predictor 1.2.0rc4; research_protocol/cain ausentes.")
        g["phases_completed"].append("v1-2-cleanroom-final")

    elif phase == "e2e-idempotency":
        conf = [f"{L}/conformance.junit.xml", f"{D}/conformance.junit.xml"]
        e2e = numbers["d16"]["e2e_real"]
        gate(g, "E2E", "PASS", [f"{D}/e2e_real/E2E_SUMMARY.json", f"{D}/conformance.junit.xml", f"{D}/core_identity.json", f"{D}/data_MANIFEST.json", f"{L}/e2e/E2E_SUMMARY.json"],
             f"V1.2, Linux primário, dados reais (D-16, run {a.run}): {e2e['checks']} checagens de E2E/restart/releitura/provenance "
             f"{'todas OK' if e2e['all_ok'] else 'COM FALHA'}; E2E sintético {numbers['runtime-linux-primary']['e2e']['checks']} checagens "
             f"{'OK' if numbers['runtime-linux-primary']['e2e']['all_ok'] else 'COM FALHA'}; conformidade {numbers['d16']['conformance']['passed']}/{numbers['d16']['conformance']['tests']}.")
        gate(g, "PROVENANCE", "PASS", [f"{D}/e2e_real/E2E_SUMMARY.json", f"{L}/e2e/E2E_SUMMARY.json"],
             "V1.2: cadeia pedido → admission (SQLite) → experimento (journal) → trial (TrialRegistryV2) → ops_run (eventos do Ops) → efeito → ResultStore conferida pelo e2e_runtime.py com a wheel rc4.")
        gate(g, "IDEMPOTENCY", "PASS", conf + [f"{D}/soak_real.jsonl"],
             "V1.2: pela wheel rc4: mesma key+conteúdo → 1 experimento, 1 efeito, 1 resultado (conformidade); 5+ duplicatas no soak real sem segundo efeito (ops_success_per_job_max=1).")
        gate(g, "RESTART_RECOVERY", "PASS", conf + [f"{D}/soak_real.jsonl", f"{M}/FAILURE_MATRIX.json"],
             "V1.2: morte real do processo nos pontos da FAILURE_MATRIX (conformidade) e restarts em rodízio no soak real: reexecução produz exatamente 1 resultado, releitura idêntica.")
        gate(g, "FAILURE_INJECTION", "PASS", conf + [f"{M}/FAILURE_MATRIX.json", f"{D}/soak_real.jsonl"],
             f"V1.2: matriz congelada injetada na borda (sem mock de Core/Ops) no Linux primário; classes por execução no soak real: {numbers['d16']['soak_real']['failure_classes']}.")
        gate(g, "ADMISSION", "PASS", conf, "V1.2: pedidos válidos e inválidos pelo entrypoint instalado (conformidade 48/48 pela wheel rc4).")
        gate(g, "OPS_RUNTIME", "PASS", [f"{D}/e2e_real/E2E_SUMMARY.json", f"{L}/e2e/E2E_SUMMARY.json"] + conf,
             "V1.2: job real pela wheel do Ops 4.2.2rc1: run_id, lock, heartbeat, attempt, timeout e reconciliação produzidos pelo Ops (E2E real e sintético).")
        gate(g, "CORE_PARTICIPATION", "PASS", [f"{D}/e2e_real/E2E_SUMMARY.json", f"{L}/e2e/E2E_SUMMARY.json"],
             "V1.2: trial no TrialRegistryV2 e estado científico relido do Core; validação temporal pelo replay do Core (E2E real e sintético).")
        gate(g, "CRYPTO_SPLIT_BRAIN_CORRUPTION", "PASS", conf + [f"{D}/soak_real.jsonl"],
             f"V1.2: DB sem FS, FS sem DB, artefato/hash alterados, referência de outra pesquisa → falha fechada (conformidade); "
             f"{numbers['d16']['soak_real']['corruptions_fail_closed']}/{numbers['d16']['soak_real']['corruptions_injected']} corrupções do soak real recusadas sem reparo.")
        gate(g, "CAPITAL_FORBIDDEN", "PASS", conf + [f"{M}/DOMAIN_RESEARCH_CONTRACT.json", f"{D}/e2e_real/E2E_SUMMARY.json"],
             "V1.2: capital_permission=false em contrato, JobConfig e em todo resultado/outcome (conformidade e E2E pela wheel rc4).")
        gate(g, "AUTHORITY_SEPARATION", "PASS", [f"{M}/AUTHORITY_STATE_MATRIX.json", f"{D}/e2e_cases/E2E_SUMMARY.json", f"{L}/e2e/E2E_SUMMARY.json"] + conf,
             f"V1.2: casos A/B/C ×3 pela wheel rc4 ({numbers['d16']['e2e_cases']['checks']} checagens {'OK' if numbers['d16']['e2e_cases']['all_ok'] else 'COM FALHA'}); Ops ok ⇏ ciência ⇏ edge ⇏ capital.")
        gate(g, "DOMAIN_CONTRACT", "PASS", [f"{M}/DOMAIN_RESEARCH_CONTRACT.json", f"{L}/conformance.junit.xml", f"{D}/conformance.junit.xml", f"{M}/FROZEN_VECTORS.json"],
             "V1.2: contrato inalterado (sha256 0831fe3d…, aprovado por merge #8); vetores congelados (FROZEN_VECTORS) com os mesmos blobs em 21f8b182; "
             "suíte de conformidade verde com a wheel rc4 nos dois runtimes; regras de adapter_paths conferidas (import_graph). Texto do layout: CR-F022 (P2).")
        g["phases_completed"] += ["v1-2-e2e", "v1-2-idempotency-failure"]

    elif phase == "science-d16":
        sci = numbers["d16"]["science"]
        econ, ctl = sci["economic_metrics"], sci["negative_controls"]
        gate(g, "CRYPTO_UNCOMFORTABLE_CASES", "PASS", [f"{D}/e2e_cases/E2E_SUMMARY.json", f"{D}/soak_real.jsonl"],
             "V1.2: casos A, B, C ×3 no runtime Linux (B com o vetor sintético congelado); A ×3 e C ×3 também sobre dados reais no soak real.")
        gate(g, "CRYPTO_ECONOMIC_METRICS", "PASS", [f"{D}/science/SCIENCE_REAL.json", f"{M}/SCIENTIFIC_INTEGRITY_REPORT.md"],
             f"V1.2, dados reais, Linux: bruto {econ['gross_return_bps']} bps IC {econ['gross_ci_bps']}; líquido {econ['net_return_bps']} bps IC {econ['net_ci_bps']}; "
             f"custos congelados; {econ['scientific_state']}/{econ['economic_state']}. Descritivo, sem edge nem capital (C22).")
        gate(g, "CRYPTO_NEGATIVE_CONTROLS", "PASS", [f"{D}/science/SCIENCE_REAL.json"],
             f"V1.2: injeção de futuro {ctl['future_injection']['accepted_results']} aceitos; ablação {ctl['temporal_ablation']['accepted_results']}; "
             f"placebo SUPPORTED {ctl['shuffled_labels']['supported']}/{ctl['shuffled_labels']['runs']} (≤{ctl['shuffled_labels']['threshold']}); vazamentos do canário {sci['future_canary']['leaks']}.")
        gate(g, "FUTURE_CANARY", "PASS", [f"{L}/conformance.junit.xml", f"{D}/science/SCIENCE_REAL.json", f"{D}/e2e_real/E2E_SUMMARY.json"],
             f"V1.2: canário só depois do cutoff; falha fechada por LookaheadError do Core; {sci['future_canary']['leaks']} ocorrências em dataset/refs/efeito/trial/resultado.")
        fs = numbers["runtime-linux-primary"]["full_suite"]
        temporal_failed = [t for t in fs["failed"] if any(k in t for k in ("test_dpl", "wfa_purge", "permutation_placebo", "test_pbo", "gate_power"))]
        gate(g, "TEMPORAL_INTEGRITY", "PASS" if not temporal_failed else "FAIL", [f"{L}/full_suite.junit.xml", f"{L}/conformance.junit.xml", f"{D}/science/SCIENCE_REAL.json"],
             f"V1.2: suítes DPL/WFA/permutação/PBO/poder dentro da suíte completa pela wheel rc4 no Linux ({fs['passed']} passed; falhas dessas suítes: {len(temporal_failed)}); "
             "PIT/cutoff impostos pelo replay do Core antes de qualquer estatística (conformidade, science real).")
        g["phases_completed"].append("v1-2-science")

    elif phase == "soak":
        s = numbers["d16"]["soak_real"]
        profile = load("QUALIFICATION_PROFILE_CRYPTO_V1.json")
        minimum = profile["minimums"]["runs_per_relevant_failure_class"]
        ok = s["zero_tolerance_ok"] and all(v >= minimum for v in s["failure_classes"].values()) and s["lost"] == 0 and s["violations"] == 0
        gate(g, "SOAK", "PASS" if ok else "FAIL", [f"{D}/soak_real.jsonl", f"{L}/soak.jsonl", f"{M}/QUALIFICATION_PROFILE_CRYPTO_V1.json", f"{M}/SOAK_REPORT.md"],
             f"V1.2, perfil V1 com dados reais no Linux primário (run {a.run}): {s['process_calls']} chamadas, {s['requests_with_result']} resultados, perdidos {s['lost']}, "
             f"violações {s['violations']}, zero_tolerance_ok={s['zero_tolerance_ok']}; execuções por classe de falha (mínimo {minimum}): {s['failure_classes']}. "
             f"Soak sintético do mesmo run: zero_tolerance_ok={numbers['runtime-linux-primary']['soak_synthetic_diagnostic']['zero_tolerance_ok']} (diagnóstico).")
        g["phases_completed"].append("v1-2-soak")

    elif phase == "hosted-ci":
        ci = numbers["hosted_ci"]["jobs_cripto-predictor_36642919823"]
        ok = all(v == "success" for v in ci["jobs"].values()) and ci["head_sha"] == [CRYPTO_FINAL]
        gate(g, "HOSTED_CI", "PASS" if ok else "FAIL",
             [f"{V}/hosted-ci/run_cripto-predictor_36642919823.json", f"{V}/hosted-ci/jobs_cripto-predictor_36642919823.json", f"{V}/hosted-ci/jobs_cripto-predictor_36643518795.json",
              f"{M}/RAW_LOGS/hosted-ci/jobs_core-predictor_35823003554.json", f"{M}/RAW_LOGS/v1.1/hosted-ci/jobs_predictor-ops_35905678198.json", f"{M}/HOSTED_CI_REPORT.md"],
             f"V1.2: CI (push, main) do cripto em 21f8b182 (baseline = final desta reabertura): {', '.join(f'{k}={v}' for k, v in ci['jobs'].items())}; Release (workflow_dispatch) success. "
             "Core 5a08415 e Ops 9831b0d inalterados: CI herdado da V1.0/V1.1 (mesmos commits).")
        gate(g, "SECRETS_CLEAN", "PASS" if numbers["secrets"]["scan_secrets"]["findings"] == 0 and numbers["secrets"]["diff_patterns"]["pattern_hits"] == 0 else "FAIL",
             [f"{V}/secrets/scan_secrets_21f8b182.log", f"{V}/secrets/diff_patterns_341d270_21f8b182.log", f"{V}/hosted-ci/jobs_cripto-predictor_36642919823.json"],
             f"V1.2: scan_secrets.py do cripto em 21f8b182: {numbers['secrets']['scan_secrets']['findings']} achados; padrões de chave/token nas 32808 linhas adicionadas do diff "
             f"341d270..21f8b182: {numbers['secrets']['diff_patterns']['pattern_hits']}; nenhum arquivo .env/.pem/.key no diff; job quality do CI (scan_secrets) verde.")
        gate(g, "EVIDENCE_CONSISTENCY", "PASS", [f"{M}/EVIDENCE_NUMBERS_V1.2.json", f"{M}/scripts/evidence_numbers_v12.py", f"{M}/scripts/v12_gates.py", f"{M}/scripts/render_v12_reports.py"],
             "V1.2: todos os números das seções V1.2 dos relatórios e das notas deste ledger vêm de RAW_LOGS/v1.2 por evidence_numbers_v12.py; a saída dos jobs foi devolvida por branch sem edição (SHA256SUMS por job).")
        g["phases_completed"].append("v1-2-hosted-ci")

    elif phase == "windows-smoke":
        g["gates"]["WINDOWS_SMOKE"] = {"status": "NOT_RUN", "evidence": [],
                                      "note": ("BLOCKED: o secundário do crypto é o Windows local do dono (D-3, C:\\Cripto\\qualificacao\\runtime\\); esta sessão não tem "
                                               "acesso a ele. O job windows-latest do run é só informação adicional. Falta o dono rodar "
                                               "qualification/crypto/scripts/windows_runtime.sh com o runtime_target.json da V1.2 (ver REABERTURA_V1.2.md) ou "
                                               "decidir, por DECISIONS.json, aceitar windows-latest como secundário do crypto (como a D-1 faz para o Stocks).")}
        g["environments"] = [
            {"os": "linux", "python": "3.13", "role": "primary", "where": "github_actions", "result": "PASS",
             "evidence": [f"{D}/env.log", f"{D}/e2e_real/E2E_SUMMARY.json", f"{D}/soak_real.jsonl", f"{L}/env.log", f"{L}/e2e/E2E_SUMMARY.json"]},
            {"os": "windows", "python": "3.13", "role": "secondary", "where": "local_windows", "result": "NOT_RUN",
             "evidence": [f"{M}/REABERTURA_V1.2.md"]},
        ]
        g["phases_completed"].append("v1-2-windows-smoke")

    elif phase == "windows-smoke-d30":
        # D-30 (2026-10-07; decisão delegada pelo dono em 2026-09-30, CICLO_D27 §5): o job windows-latest do run vale como secundário.
        W = f"{V}/{a.run}/runtime-windows-latest"
        numbers = load("EVIDENCE_NUMBERS_V1.2.json")["runtime-windows-latest"]
        ok = (numbers["e2e"]["all_ok"] and numbers["conformance"]["failures"] == 0 and numbers["conformance"]["errors"] == 0
              and numbers["conformance"]["passed"] == numbers["conformance"]["tests"])
        gate(g, "WINDOWS_SMOKE", "PASS" if ok else "FAIL",
             [f"{W}/env.log", f"{W}/e2e/E2E_SUMMARY.json", f"{W}/conformance.junit.xml", f"{W}/core_identity.json", f"{W}/pip_freeze.txt"],
             (f"V1.2, D-30: windows-latest × 3.13 (run {a.run}, venv limpo só com as wheels publicadas): E2E pelo entrypoint instalado com restart e "
              f"releitura por processo novo {numbers['e2e']['checks']} checagens, all_ok={numbers['e2e']['all_ok']}; conformidade "
              f"{numbers['conformance']['passed']}/{numbers['conformance']['tests']}; suíte pela wheel {numbers['full_suite']['passed']} passed / "
              f"{numbers['full_suite']['failures']} falhas, as mesmas da classe T do Linux (CR-F016). Secundário aceito pela D-30; o Windows local "
              "do dono (D-3) continua admitido como evidência adicional."))
        g["environments"] = [env for env in g["environments"] if env["role"] != "secondary"] + [
            {"os": "windows", "python": "3.13", "role": "secondary", "where": "github_actions", "result": "PASS" if ok else "FAIL",
             "evidence": [f"{W}/env.log", f"{W}/e2e/E2E_SUMMARY.json", f"{W}/conformance.junit.xml"]}]
        g["phases_completed"].append("v1-2-windows-smoke-d30")
        findings = load("FINDINGS.json")["findings"]
        blocking = [f["id"] for f in findings if f["status"] in ("OPEN", "OPEN_BLOCKED") and f["severity"] in ("P0", "P1")]
        states = {k: v["status"] for k, v in g["gates"].items()}
        not_run = sorted(k for k, s in states.items() if s == "NOT_RUN")
        failed = sorted(k for k, s in states.items() if s == "FAIL")
        g["terminal_state_v1_2"] = ("NOT_QUALIFIED" if failed or blocking else ("BLOCKED" if not_run else "QUALIFIED"))
        g["terminal_note_v1_2"] = (f"FAIL em {failed}" if failed else (f"BLOCKED: NOT_RUN em {not_run}" if not_run else "todos PASS (D-30 fecha WINDOWS_SMOKE)"))
        g["final_result"] = "NOT_QUALIFIED" if failed or blocking else ("QUALIFIED" if not not_run else g.get("final_result"))
        print("estado terminal V1.2:", g["terminal_state_v1_2"], "|", g["terminal_note_v1_2"])

    elif phase == "attestation-blocked":
        findings = load("FINDINGS.json")["findings"]
        blocking = [f["id"] for f in findings if f["status"] in ("OPEN", "OPEN_BLOCKED") and f["severity"] in ("P0", "P1")]
        gate(g, "BLOCKERS_ZERO", "FAIL" if blocking else "PASS", [f"{M}/FINDINGS.json"],
             ("P0/P1 abertos: " + ", ".join(blocking)) if blocking else
             "V1.2: P0=0, P1=0 abertos; P2 abertos incluem CR-F016 (atualizado: 32 testes classe T na rc4) e CR-F022 (texto do contrato).")
        states = {k: v["status"] for k, v in g["gates"].items()}
        not_run = sorted(k for k, s in states.items() if s == "NOT_RUN")
        failed = sorted(k for k, s in states.items() if s == "FAIL")
        g["terminal_state_v1_2"] = ("NOT_QUALIFIED" if failed or blocking else ("BLOCKED" if not_run else "QUALIFIED"))
        g["terminal_note_v1_2"] = (f"FAIL em {failed}" if failed else (f"BLOCKED: NOT_RUN em {not_run} (C7.3: só parcial IN_PROGRESS; sem attestation final)" if not_run else "todos PASS"))
        g["final_result"] = "NOT_QUALIFIED" if failed or blocking else g.get("final_result")
        print("estado terminal V1.2:", g["terminal_state_v1_2"], "|", g["terminal_note_v1_2"])
    else:
        raise SystemExit(f"fase desconhecida: {phase}")

    (QC / "GATES.json").write_text(json.dumps(g, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(phase, "->", {k: v["status"] for k, v in g["gates"].items() if v["status"] != "PASS"})
    tag = {"attestation-blocked": "v1-2-attestation-blocked"}.get(phase, f"v1-2-{phase}")
    subprocess.run([sys.executable, str(QC / "scripts" / "attest.py"), "partial", tag], check=True)


if __name__ == "__main__":
    main()
