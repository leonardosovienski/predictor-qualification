"""stocks: estado dos gates por fase (fonte de GATES.json) e emissão dos parciais que faltam (C8).

Cada gate recebe estado, evidências (caminhos; o attest.py calcula sha256) e nota, na fase em que ficou
conhecido. Os parciais são emitidos em ordem, cada um com o estado acumulado até a sua fase; parciais já
existentes nunca são reescritos.

Uso: python gates_state.py [--emit]
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

QC = Path(__file__).resolve().parents[1]
R = "qualification/stocks/RAW_LOGS"
CF = f"{R}/cleanroom-final/run35949779357"
L, W = f"{CF}/stocks-runtime-linux-primary", f"{CF}/stocks-runtime-windows-latest"
SUITE = f"{R}/contract-admission-ops-entrypoint/run35948598839"
D16 = "BLOCKED: D-16 pendente (FROZEN_PARAMETERS.d16_dependency_rule): exige dado real no Linux primário/Actions."

PHASES = [
    ("dependency-identity-baseline", {
        "LOCK_INTEGRITY@": None,
    }),
    ("cleanroom-baseline", {}),
    ("contract-admission-ops-entrypoint", {}),
    ("dependency-identity-final", {
        "LOCK_INTEGRITY": ("PASS", ["qualification/stocks/CORE_IDENTITY_REPORT.md", f"{L}/uv_lock_check.log",
                                    f"{L}/core_identity.json", f"{L}/requirements.locked.txt", f"{SUITE}/stocks-suite-linux-primary/uv_lock_check.log"],
                           "uv lock --check exit 0 no final_commit 9a6c09a; instalação só pelo lock exportado (--require-hashes) e uv sync --locked; nenhuma dependência fora do lock."),
        "CORE_IDENTITY": ("PASS", ["qualification/stocks/CORE_IDENTITY_REPORT.md", f"{L}/core_identity.json", f"{W}/core_identity.json"],
                          "pyproject ↔ tool.uv.sources (release) ↔ uv.lock ↔ instalação ↔ sha256 da wheel ↔ metadata ↔ módulo em site-packages: Core 10ef42f3…, Ops 0be70bfb…, Stocks 3cc4e04a…, Linux e windows-latest; nada editable, vendor ou checkout."),
        "STOCKS_CORE_PIN": ("PASS", ["qualification/stocks/CORE_IDENTITY_REPORT.md", f"{L}/core_identity.json", f"{W}/core_identity.json"],
                            "range >=3.2.1,<4 (D-7), fonte release v3.2.1, lock 3.2.1 10ef42f3…, wheel instalada 10ef42f3… nos dois runtimes; baseline idem."),
    }),
    ("publish-candidates", {}),
    ("cleanroom-final", {
        "CLEANROOM_FINAL": ("PASS", ["qualification/stocks/CLEANROOM_REPORT.md", f"{L}/env.log", f"{L}/conformance.junit.xml",
                                     f"{W}/env.log", f"{W}/conformance.junit.xml", f"{L}/pip_freeze.txt"],
                            "Só wheels publicadas (stocks v0.3.0rc1 3cc4e04a…, Core 3.2.1, Ops 4.2.2rc1), fora do checkout: conformidade 87/87 no Linux e no windows-latest; pip check limpo. Suíte legada não coleta sem a pasta-fonte (ST-F004, P2)."),
    }),
    ("e2e", {
        "E2E": ("NOT_RUN", [f"{L}/e2e/E2E_SUMMARY.json", f"{W}/e2e/E2E_SUMMARY.json"],
                D16 + " Diagnóstico pela wheel com fixture sintética congelada: 24/24 checagens no Linux e 24/24 no windows-latest (processo → término → processo novo relê o mesmo resultado byte a byte)."),
        "PROVENANCE": ("PASS", [f"{L}/e2e/E2E_SUMMARY.json", f"{W}/e2e/E2E_SUMMARY.json", "qualification/stocks/E2E_EVIDENCE/linux-primary/outcome_file.json"],
                       "Cadeia pedido → recibo de admission (SQLite) → experimento (journal) → attempt/ops_run (eventos do predictor_ops) → trial (TrialRegistryV2) → efeito (sha256) → resultado, conferida contra as fontes primárias pelo entrypoint instalado; identidades das wheels no resultado."),
        "AUTHORITY_SEPARATION": ("PASS", [f"{L}/e2e/E2E_SUMMARY.json", f"{W}/e2e/E2E_SUMMARY.json", f"{L}/conformance.junit.xml"],
                                 "Invariantes em validate_result e casos A (Ops ok/Core INCONCLUSIVE/NO_EDGE), B (bruto SUPPORTED/líquido NO_EDGE) e C (Ops FAILED → NOT_EVALUATED) 3× cada pela wheel nos dois runtimes: Ops ok ⇏ ciência ⇏ edge ⇏ capital."),
        "CAPITAL_FORBIDDEN": ("PASS", [f"{L}/e2e/E2E_SUMMARY.json", f"{L}/soak.jsonl", "qualification/stocks/DOMAIN_RESEARCH_CONTRACT.json"],
                              "capital_permission=false no contrato (validate_result recusa outro valor), no JobConfig do Ops (SHADOW_DECISION/MARKET_COLLECTION) e em todo resultado (E2E e soak); nenhum caminho concede capital."),
        "OPS_RUNTIME": ("PASS", [f"{L}/e2e/E2E_SUMMARY.json", f"{L}/conformance.junit.xml", f"{W}/conformance.junit.xml"],
                        "Handler roda como job real do predictor_ops 4.2.2rc1: run_id, economic_lock_id, heartbeat, attempt/retry_count, timeout com kill (ops_worker_hang), eventos terminais e idempotência econômica usados na reconciliação."),
        "CORE_PARTICIPATION": ("PASS", [f"{L}/e2e/E2E_SUMMARY.json", f"{L}/conformance.junit.xml"],
                               "Trial registrada no TrialRegistryV2 (dataset_fingerprint do Core) e estado científico relido dele; validação temporal por predictor_core.measurement.replay; IC por bootstrap_ci; max_drawdown; o Core não decide universo, ranking nem capital."),
    }),
    ("pit-universe-canary-negative", {
        "FUTURE_CANARY": ("PASS", ["qualification/stocks/PIT_ADVERSARIAL_REPORT.md", f"{L}/conformance.junit.xml", f"{W}/conformance.junit.xml", f"{L}/e2e/E2E_SUMMARY.json"],
                          "FUTURE_CANARY_STOCKS_001 só depois do cutoff: falha fechada por LookaheadError do Core (exit 4), sem efeito/trial/resultado; ausente de efeito, trial, results.sqlite e outcomes de pedidos legítimos (vetores sintéticos congelados, prompt §4)."),
        "TEMPORAL_INTEGRITY": ("PASS", ["qualification/stocks/PIT_ADVERSARIAL_REPORT.md", f"{L}/conformance.junit.xml", f"{W}/conformance.junit.xml"],
                               "Cutoff/PIT em todo estado que afeta a previsão: snapshot (available_at ≤ as_of pelo replay do Core), cada decisão (available_at ≤ decision_at), barras (≥ fechamento), as_of divergente → exit 4."),
        "STOCKS_PIT_ADVERSARIAL": ("PASS", ["qualification/stocks/PIT_ADVERSARIAL_REPORT.md", f"{L}/conformance.junit.xml", f"{W}/conformance.junit.xml"],
                                   "15/15 casos congelados (PIT-01..15), incluindo o obrigatório (PIT_STRICT declarado × HISTORICAL_ONLY efetivo), pela wheel no Linux e no windows-latest; nenhuma violação."),
        "STOCKS_UNIVERSE_IDENTITY": ("PASS", ["qualification/stocks/UNIVERSE_IDENTITY_REPORT.md", f"{L}/e2e/E2E_SUMMARY.json", f"{W}/e2e/E2E_SUMMARY.json", f"{L}/conformance.junit.xml"],
                                     "Mesmo pedido em 3 raízes/processos novos = mesmos hashes de universo em todos os rebalances; entradas/saídas só por eventos disponíveis; deslistado presente enquanto existia; ticker e CNPJ trocados preservam a identidade."),
        "STOCKS_EXTERNAL_INTELLIGENCE_AXES": ("PASS", ["qualification/stocks/EXTERNAL_INTELLIGENCE_READINESS.json", f"{L}/science/external_intelligence_readiness.json", "qualification/stocks/COLLECTION_ONLY_REPORT.md"],
                                              "7 famílias em 8 eixos independentes pela wheel; elegibilidade só pelo campo readiness (0 READY); PIT efetivo da matriz (B3_LENDING, VLMO, BUYBACK rebaixados para HISTORICAL_ONLY efetivo); nenhum eixo promove outro."),
        "STOCKS_COLLECTION_MODE": ("PASS", ["qualification/stocks/COLLECTION_ONLY_REPORT.md", f"{L}/e2e/E2E_SUMMARY.json", f"{L}/soak.jsonl", f"{L}/conformance.junit.xml"],
                                   "COLLECTION_ONLY coleta, valida, persiste e monitora como job do Ops e nunca alimenta trial/ranking/carteira/capital; TRIAL_CONSUMPTION de família não READY → NOT_READY sem trial; 0 trials elegíveis (0 famílias READY); zero consumo de dado inelegível."),
        "STOCKS_NEGATIVE_CONTROLS": ("NOT_RUN", ["qualification/stocks/NEGATIVE_CONTROLS_REPORT.md", f"{L}/science/NEGATIVE_CONTROLS_SUMMARY.json"],
                                     D16 + " Diagnóstico com fixture sintética pela wheel: labels embaralhados 0/20 SUPPORTED, ranking aleatório 2/20, perturbação de universo 20/20 estável; critérios congelados atendidos na fixture."),
    }),
    ("idempotency-failure", {
        "IDEMPOTENCY": ("PASS", [f"{L}/conformance.junit.xml", f"{W}/conformance.junit.xml", f"{L}/soak.jsonl"],
                        "Pela wheel: mesma idempotency_key (request_id) e conteúdo → 1 experimento, 1 efeito, 1 SUCCEEDED do Ops, 1 trial, 1 resultado, client_ref próprio devolvido; conteúdo diferente → CONFLICT; duplicata após mudança de policy → mesmo resultado."),
        "RESTART_RECOVERY": ("PASS", ["qualification/stocks/FAILURE_MATRIX.json", f"{L}/conformance.junit.xml", f"{W}/conformance.junit.xml"],
                             "Morte real do processo nos 9 pontos + host do Ops morto durante o job: reexecução produz exatamente 1 resultado, relido por processo novo; reconcile sem achados."),
        "FAILURE_INJECTION": ("PASS", ["qualification/stocks/FAILURE_MATRIX.json", f"{L}/conformance.junit.xml", f"{W}/conformance.junit.xml"],
                              "Matriz congelada (19 linhas: admission, materialização, Ops crash/timeout/host, artefato parcial, resultado, duplicado, fora de ordem, schema, corrupção, DB lock, disco cheio) injetada na borda, sem mock de Core/Ops: 19/19 PASS no Linux e no windows-latest; zero duplicata, zero perda, zero mudança em congelado."),
    }),
    ("windows-smoke", {
        "WINDOWS_SMOKE": ("NOT_RUN", [f"{W}/e2e/E2E_SUMMARY.json", f"{W}/conformance.junit.xml"],
                          D16 + " O E2E no windows-latest (D-1) também roda no Actions. Diagnóstico com as final wheels: E2E + restart + releitura 24/24, conformidade 87/87."),
    }),
    ("hosted-ci", {
        "HOSTED_CI": ("PASS", ["qualification/stocks/HOSTED_CI_REPORT.md",
                               f"{R}/hosted-ci/run_stocks-predictor_35822899971_baseline_4e98a67.json",
                               f"{R}/hosted-ci/run_stocks-predictor_35950266341_final_9a6c09a_dispatch.json",
                               f"{R}/hosted-ci/run_core-predictor_35823003554_core_5a08415.json",
                               f"{R}/hosted-ci/run_predictor-ops_35905678198_ops_9831b0d_push.json"],
                      "CI de push/PR verde com uv sync --locked no baseline (stocks 4e98a67, core 5a08415, ops 9831b0d) e nos final_commits (stocks 9a6c09a no SHA exato por workflow_dispatch e no PR #95); nenhum job pulado."),
        "SECRETS_CLEAN": ("PASS", [f"{R}/secrets/run35950519783/stocks-secrets/evidence_tree.log", f"{R}/secrets/run35950519783/stocks-secrets/stocks_diff.log",
                                   f"{R}/secrets/run35950519783/stocks-secrets/gitleaks_checksum.log",
                                   f"{R}/hosted-ci/run_stocks-predictor_35950266341_final_9a6c09a_dispatch.json"],
                          "gitleaks 8.24.3 (checksum conferido): árvore qualification/stocks e os 7 commits 4e98a67..9a6c09a sem achados; job secrets do CI do repo (árvore inteira + controle sintético) verde no final_commit."),
    }),
    ("soak", {
        "SOAK": ("NOT_RUN", ["qualification/stocks/SOAK_REPORT.md", f"{L}/soak.jsonl", "qualification/stocks/QUALIFICATION_PROFILE_STOCKS_V1.json"],
                 D16 + " Diagnóstico com fixture pela wheel no Linux: 73 chamadas, 17 falhas injetadas, 48 resultados, 0 perdidos/duplicados/violações PIT, 0 trials elegíveis, tolerância zero OK."),
        "SHARED_DEPENDENCY_CLEAR": ("PASS", ["qualification/shared/SHARED-003/SHARED_DEPENDENCY_VERDICT_4.2.2rc1.json",
                                             "qualification/shared/SHARED-004/SHARED_DEPENDENCY_VERDICT_4.2.2rc1.json",
                                             "qualification/shared/SHARED-005/RESOLUTION_4.2.2rc1.json", f"{L}/core_identity.json"],
                                    "Wheel instalada predictor-ops 4.2.2rc1 (0be70bfb…): SHARED-003 e SHARED-004 test_only não bloqueantes (missão crypto); SHARED-005 resolvida (D-17). Nenhuma falha nova de Core/Ops reproduzida nesta missão."),
        "PROTECTED_ARTIFACTS_UNCHANGED": ("PASS", ["qualification/stocks/PROTECTED_ARTIFACT_REPORT.md", "qualification/stocks/PROTECTED_SET.json",
                                                   f"{R}/protected/protected_check_9a6c09a.json", f"{R}/protected/immutable_data_sha256_final.txt",
                                                   f"{R}/truth-map/immutable_data_sha256.txt"],
                                          "81/81 blobs iguais entre truth-map (4e98a67) e final_commit (9a6c09a), 0 itens novos; 3698/3698 arquivos de dados imutáveis com o mesmo sha256 (re-hash somente leitura)."),
        "BLOCKERS_ZERO": ("PASS", ["qualification/stocks/FINDINGS.json"],
                          "P0=0, P1=0 abertos: ST-F001 (P1, tzdata no Windows) corrigido com teste e provado no windows-latest. Abertos só P2: ST-F002 (branches remotas), ST-F003 (scripts extras presos a outra máquina), ST-F004 (suíte legada só roda contra o checkout)."),
        "EVIDENCE_CONSISTENCY": ("PASS", ["qualification/stocks/EVIDENCE_NUMBERS.json", "qualification/stocks/scripts/evidence_numbers.py",
                                          "qualification/stocks/scripts/write_reports.py"],
                                 "Todo número dos relatórios sai dos logs brutos (junit, pytest.log, soak.jsonl, E2E_SUMMARY, NEGATIVE_CONTROLS_SUMMARY, core_identity) por scripts versionados; nenhum log editado."),
    }),
]


EXTRA = {
    "publish-candidates": {
        "final_commits": [
            {"repo": "stocks-predictor", "commit_sha": "9a6c09ae92991c8490be624f5693865bcbaeca26"},
            {"repo": "core-predictor", "commit_sha": "5a0841509f091ea0aa95bde0d3d65e2a1a9e984d"},
            {"repo": "predictor-ops", "commit_sha": "9831b0d5e727972b1d85ff48be14ffa58677898b"},
        ],
        "final_wheels": [
            {"name": "stocks-predictor", "version": "0.3.0rc1",
             "url": "https://github.com/leonardosovienski/stocks-predictor/releases/download/v0.3.0rc1/stocks_predictor-0.3.0rc1-py3-none-any.whl",
             "sha256": "3cc4e04a04967efb11e16000815b8c632cf9659e2703b097a1277dabf5639467"},
            {"name": "predictor-core", "version": "3.2.1",
             "url": "https://github.com/leonardosovienski/core-predictor/releases/download/v3.2.1/predictor_core-3.2.1-py3-none-any.whl",
             "sha256": "10ef42f34ace8bb2df5f83ff7de2ceec79b035a25ea0a690e8942bd60d2fb4e3"},
            {"name": "predictor-ops", "version": "4.2.2rc1",
             "url": "https://github.com/leonardosovienski/predictor-ops/releases/download/v4.2.2rc1/predictor_ops-4.2.2rc1-py3-none-any.whl",
             "sha256": "0be70bfbb2437dfb080baceb9af41043a09d03b15a358903b8bd7007f5f169b3"},
        ],
    },
    "windows-smoke": {
        "environments": [
            {"os": "linux", "python": "3.13", "role": "primary", "where": "github_actions", "result": "NOT_RUN",
             "evidence": [f"{L}/env.log", f"{L}/conformance.junit.xml", f"{L}/soak.jsonl"]},
            {"os": "windows", "python": "3.13", "role": "secondary", "where": "github_actions", "result": "NOT_RUN",
             "evidence": [f"{W}/env.log", f"{W}/conformance.junit.xml", f"{W}/e2e/E2E_SUMMARY.json"]},
        ],
    },
    "soak": {
        "shared_dependency_verdicts": [
            {"issue_id": "SHARED-003", "dependency": "predictor-ops",
             "wheel_sha256": "0be70bfbb2437dfb080baceb9af41043a09d03b15a358903b8bd7007f5f169b3",
             "classification": "test_only", "blocking": False,
             "verdict_file": "qualification/shared/SHARED-003/SHARED_DEPENDENCY_VERDICT_4.2.2rc1.json"},
            {"issue_id": "SHARED-004", "dependency": "predictor-ops",
             "wheel_sha256": "0be70bfbb2437dfb080baceb9af41043a09d03b15a358903b8bd7007f5f169b3",
             "classification": "test_only", "blocking": False,
             "verdict_file": "qualification/shared/SHARED-004/SHARED_DEPENDENCY_VERDICT_4.2.2rc1.json"},
        ],
    },
}


def main() -> None:
    ledger = json.loads((QC / "GATES.json").read_text(encoding="utf-8"))
    emit = "--emit" in sys.argv
    for phase, updates in PHASES:
        for gate, value in updates.items():
            if value is None or gate.endswith("@"):
                continue
            status, evidence, note = value
            ledger["gates"][gate] = {"status": status, "evidence": evidence, "note": note}
        for key, value in EXTRA.get(phase, {}).items():
            ledger[key] = value
        if phase not in ledger["phases_completed"]:
            ledger["phases_completed"].append(phase)
        (QC / "GATES.json").write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
        if emit and not (QC / f"ATTESTATION_PARTIAL_{phase}.json").exists():
            subprocess.run([sys.executable, str(QC / "scripts" / "attest.py"), "partial", phase, "--no-schema"], check=True)
    print(ledger["phases_completed"])


if __name__ == "__main__":
    main()
