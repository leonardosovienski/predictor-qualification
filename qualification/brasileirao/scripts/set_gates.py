"""brasileirao: estados dos gates depois das fases até soak (fonte do GATES.json, via ledger.py).

Cada entrada: gate, status, nota e arquivos de evidência (o ledger recusa arquivo inexistente).
DOMAIN_CONTRACT e BLOCKERS_ZERO são fechados na fase contract-sign-off/attestation.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
Q = "qualification/brasileirao"
C = f"{Q}/RAW_LOGS/cleanroom-final/run35963501898"
W = f"{Q}/RAW_LOGS/windows-smoke/rc2"
GA = f"{Q}/RAW_LOGS/temporal-suite/gate_tests_rc2_actions.json"
GW = f"{Q}/RAW_LOGS/temporal-suite/gate_tests_rc2_windows_local.json"
CL = f"{C}/brasileirao-runtime-linux-primary/conformance.junit.xml"
CWL = f"{C}/brasileirao-runtime-windows-latest/conformance.junit.xml"
CW = f"{W}/conformance.junit.xml"
RC = f"{Q}/RAW_LOGS/temporal-suite/real_corroboration/REAL_CORROBORATION.json"
CONF = [GA, GW, CL, CWL, CW]

GATES = [
    ("LOCK_INTEGRITY", "PASS", "uv lock --check exit 0 em 04b42c9; instalação só pelo lock com --require-hashes no Linux primário, windows-latest e Windows local; o lock mudou só na versão do Ops (4.2.2rc1) e do próprio pacote.",
     [f"{Q}/RAW_LOGS/cleanroom-final/lock_check_04b42c9.log", f"{Q}/CORE_IDENTITY_REPORT.md", f"{W}/install.log"]),
    ("CORE_IDENTITY", "PASS", "pyproject, tool.uv.sources, uv.lock, asset da release, instalação, metadata e módulo em site-packages apontam a mesma wheel: core 3.2.1 (10ef42f3) e ops 4.2.2rc1 (0be70bfb), nos 3 runtimes; nenhum editable, vendor ou checkout.",
     [f"{Q}/CORE_IDENTITY_REPORT.md", f"{C}/brasileirao-runtime-linux-primary/core_identity.json", f"{C}/brasileirao-runtime-windows-latest/core_identity.json", f"{W}/core_identity_windows_local.json", f"{C}/brasileirao-runtime-linux-primary/runtime_trace.log"]),
    ("CLEANROOM_FINAL", "PASS", "Só wheels publicadas (brasileirao 0.3.0rc2 70344f22, core 3.2.1, ops 4.2.2rc1), árvore sem os pacotes-fonte: conformidade 89/89 no Linux primário, windows-latest e Windows local; suíte completa 2315 casos, 46 da classe T (BR-F017, leem o checkout).",
     [f"{Q}/CLEANROOM_REPORT.md", CL, CWL, CW, f"{C}/brasileirao-runtime-linux-primary/env.log", f"{Q}/EVIDENCE_NUMBERS.json"]),
    ("HOSTED_CI", "PASS", "ci.yml e publication-validation.yml verdes em e14f339 (baseline) e 04b42c9 (final); core 5a08415 e ops 9831b0d/31d3939 verdes; nenhum job pulado.",
     [f"{Q}/HOSTED_CI_REPORT.md", f"{Q}/RAW_LOGS/baseline/hosted_ci/run_35824710652.json", f"{Q}/RAW_LOGS/baseline/hosted_ci/run_35824710697.json", f"{Q}/RAW_LOGS/hosted-ci/br_final_35965123063.json", f"{Q}/RAW_LOGS/hosted-ci/br_final_35963505773.json", f"{Q}/RAW_LOGS/baseline/hosted_ci/run_35823003554.json", f"{Q}/RAW_LOGS/baseline/hosted_ci/run_35905678198.json"]),
    ("E2E", "NOT_RUN", "BLOCKED: D-16 pendente (FROZEN_PARAMETERS.d16_dependency_rule): exige dados reais no Linux primário. Diagnóstico: E2E pela wheel no Linux e no windows-latest com vetores sintéticos 26/26 checagens cada; E2E com dado real no Windows local 25/25 (processo, término, processo novo relê o mesmo resultado; cadeia de provenance).",
     [f"{Q}/E2E_EVIDENCE/linux-primary-synthetic/E2E_SUMMARY.json", f"{Q}/E2E_EVIDENCE/windows-latest-synthetic/E2E_SUMMARY.json", f"{Q}/E2E_EVIDENCE/windows-local-real/E2E_SUMMARY.json"]),
    ("IDEMPOTENCY", "PASS", "Pela wheel: mesma key e conteúdo dão 1 experimento, 1 SUCCEEDED do Ops, 1 resultado (DUPLICATE devolve o client_ref da submissão); conteúdo diferente dá CONFLICT; duplicata após mudança de policy devolve o resultado guardado; 2 processos concorrentes dão 1 efeito; fora de ordem dá os mesmos resultados. Linux, windows-latest e Windows local.", CONF),
    ("RESTART_RECOVERY", "PASS", "Morte real do processo nos 9 pontos da FAILURE_MATRIX: reenvio em processo novo produz exatamente 1 efeito, 1 SUCCEEDED, 1 resultado, reconcile limpo; backup/restore em raiz nova relê os mesmos bytes. Nos 3 ambientes.",
     [f"{Q}/FAILURE_MATRIX.json", *CONF]),
    ("FAILURE_INJECTION", "PASS", "Matriz congelada (24 casos) injetada na borda sem mock de Core/Ops: crash, timeout (exit 124, termination timeout) e lentidão do job do Ops, orçamento de retries, lock do Ops, DB lock, DB x FS divergentes, artefato ausente/corrompido/alterado, snapshot com hash divergente. Linux primário, windows-latest e Windows local, pela wheel 4.2.2rc1 do Ops.",
     [f"{Q}/FAILURE_MATRIX.json", *CONF]),
    ("PROVENANCE", "PASS", "Cadeia pedido, admission (recibo SQLite, policy_hash), experimento (journal), worker-request, job do Ops (jobs file v3, run_id, strict/VALIDATED), efeito (sha256), trial do TrialRegistryV2 e resultado conferida contra as fontes primárias no E2E (Linux e windows-latest sintético, Windows real).",
     [f"{Q}/E2E_EVIDENCE/windows-local-real/E2E_SUMMARY.json", f"{Q}/E2E_EVIDENCE/linux-primary-synthetic/E2E_SUMMARY.json", f"{Q}/OPS_MAPPING_REPORT.md"]),
    ("AUTHORITY_SEPARATION", "PASS", "validate_result impõe: Ops não SUCCEEDED implica NOT_EVALUATED/FAILED_OPERATIONAL; WATCH exige SUPPORTED; WATCH_NO_CAPITAL exige WATCH; FORECAST_ONLY sem afirmação; capital false. Crash e retries esgotados nunca viram resultado científico. Dado real: SUPPORTED contra a climatologia e NO_EDGE (ciência não virou edge).",
     [GA, GW, f"{Q}/DOMAIN_RESEARCH_CONTRACT.json", f"{Q}/EVIDENCE_NUMBERS.json"]),
    ("FUTURE_CANARY", "PASS", "FUTURE_CANARY_BR_001 só depois do cutoff: resultado idêntico com e sem canário e token ausente de efeitos, trials, resultados, outcomes, jobs e eventos do Ops (vetor congelado, 3 ambientes); corroborado com o dado real no Windows; soak sintético com 5 ciclos.",
     [f"{Q}/FUTURE_CANARY_REPORT.md", GA, GW, RC]),
    ("PROTECTED_ARTIFACTS_UNCHANGED", "PASS", "1877/1877 blobs iguais entre truth-map (e14f339) e final_commit (04b42c9); nada retunado; H8/H9/H14/H15/A1 recusadas; 2025 nunca alvo.",
     [f"{Q}/PROTECTED_ARTIFACT_REPORT.md", f"{Q}/PROTECTED_SET.json", f"{Q}/RAW_LOGS/attestation/protected_check_04b42c9.json"]),
    ("SOAK", "NOT_RUN", "BLOCKED: D-16 pendente (FROZEN_PARAMETERS.d16_dependency_rule): exige dados reais no Linux primário. Diagnóstico sintético no Linux (perfil BR_V1 congelado): 71 chamadas, 49 resultados, 0 perdidos, duplicados ou violações, reconcile limpo, tolerância zero ok.",
     [f"{Q}/SOAK_REPORT.md", f"{Q}/QUALIFICATION_PROFILE_BR_V1.json", f"{C}/brasileirao-runtime-linux-primary/soak.jsonl"]),
    ("WINDOWS_SMOKE", "PASS", "C:\\QUALIFICACAO\\runtime\\brasileirao\\ com as final_wheels (--require-hashes): E2E, restart e releitura com dado real 25/25; 20 pedidos reais; conformidade 89/89 pela wheel instalada.",
     [f"{W}/install.log", f"{W}/core_identity_windows_local.json", f"{Q}/E2E_EVIDENCE/windows-local-real/E2E_SUMMARY.json", CW, f"{W}/real/runs.json"]),
    ("SHARED_DEPENDENCY_CLEAR", "PASS", "Ops 4.2.2rc1: SHARED-003 e SHARED-004 test_only não bloqueantes; SHARED-005 resolvida (não bloqueante para 0be70bfb). Nesta missão o timeout, o crash e o lock do job real do Ops passaram pela wheel 4.2.2rc1 no Linux, windows-latest e Windows local.",
     ["qualification/shared/SHARED-003/SHARED_DEPENDENCY_VERDICT_4.2.2rc1.json", "qualification/shared/SHARED-004/SHARED_DEPENDENCY_VERDICT_4.2.2rc1.json", "qualification/shared/SHARED-005/RESOLUTION_4.2.2rc1.json", GA, GW]),
    ("EVIDENCE_CONSISTENCY", "PASS", "Números dos relatórios tirados dos logs brutos por scripts versionados (evidence_numbers.py, gate_tests.py, protected_check.py, probe_inprogress_leak.py); logs brutos preservados byte a byte (.gitattributes -text).",
     [f"{Q}/EVIDENCE_NUMBERS.json", f"{Q}/scripts/evidence_numbers.py", f"{Q}/scripts/gate_tests.py", GA, GW]),
    ("SECRETS_CLEAN", "PASS", "scan_secrets.py na evidência, no workflow e no diff e14f339..04b42c9 do brasileirao-predictor (linhas e mensagens): 1 alerta, revisado: o marcador público do canário em FROZEN_PARAMETERS.json (chave token). Nenhum segredo.",
     [f"{Q}/RAW_LOGS/secrets/scan_evidence_and_br_diff.json", f"{Q}/scripts/scan_secrets.py"]),
    ("CAPITAL_FORBIDDEN", "PASS", "capital_permission=false no contrato (validate_result recusa true), no jobs file (FORECAST_GENERATION, nunca EXECUTION), em todo resultado e outcome; research/economic_decision.py, shadow_portfolio.py e bet_log não alcançáveis do entrypoint (import closure).",
     [GA, GW, f"{Q}/DOMAIN_RESEARCH_CONTRACT.json"]),
    ("ADMISSION", "PASS", "Pelo entrypoint: comando, handler, módulo, SQL, path, URL, capital, tipo desconhecido, ID sem domínio, cutoff sem Z, lead fora dos limites, alvo inválido, hipótese protegida ou não admitida, temporada 2025 ou fora da policy, janela fora da temporada, referência desconhecida, JSON duplicado/NaN/oversize: REJECTED antes de qualquer execução (22 casos, 3 ambientes).", CONF),
    ("OPS_RUNTIME", "PASS", "Job real pelo mesmo mecanismo da sombra (jobs file v3 + python -m predictor_ops run): run_id, economic_lock_id, heartbeat, attempt/retry_count, timeout (kill da árvore, exit 124), lock_not_acquired, idempotência e eventos terminais produzidos pela wheel 4.2.2rc1; o circuito não importa run_job.",
     [f"{Q}/OPS_MAPPING_REPORT.md", f"{Q}/E2E_EVIDENCE/windows-local-real/ops/events.jsonl", f"{Q}/E2E_EVIDENCE/windows-local-real/ops/ops-job.1.json", GA, GW]),
    ("CORE_PARTICIPATION", "PASS", "Core no circuito: replay/LookaheadError dirige a linha do tempo; rps/brier/log_loss e bootstrap_ci (cluster por kickoff) nas métricas e IC; trial_v2 dataset_fingerprint e TrialRegistryV2 com o estado científico relido do registro; request, experiment, trial, core facts e result correlacionados no E2E.",
     [f"{Q}/E2E_EVIDENCE/windows-local-real/show_2.stdout.json", f"{Q}/E2E_EVIDENCE/windows-local-real/E2E_SUMMARY.json", GA]),
    ("TEMPORAL_INTEGRITY", "PASS", "available_at(i) < cutoff(t) imposto pelo replay do Core em todo estado (Elo, refit mensal, climatologia, caches, rótulos, odds); o handler lê só o snapshot com hash (escrita na origem depois da captura não muda o resultado); vazamento pré-existente BR-F004 corrigido; dado real: gap máximo -1800 s nos 20 pedidos e corroboração 7/7.",
     [f"{Q}/TEMPORAL_INTEGRITY_REPORT.md", GA, GW, RC, f"{Q}/EVIDENCE_NUMBERS.json"]),
    ("BR_OPS_REUSE", "PASS", "Nenhum executor paralelo: o mesmo mecanismo real da sombra (jobs file validado pelo Ops + python -m predictor_ops run --job --config), com o job de pesquisa mais rígido em provenance_mode, expected_artifact, economic_key, job_type e exit_statuses; mapeamento campo a campo e prova em runtime.",
     [f"{Q}/OPS_MAPPING_REPORT.md", f"{Q}/E2E_EVIDENCE/windows-local-real/ops/ops-job.1.json", f"{Q}/E2E_EVIDENCE/windows-local-real/ops/events.jsonl"]),
    ("BR_KICKOFF_ORDERING", "PASS", "Pela wheel: arquivo fora de ordem (5 permutações), mesma data, mesmo kickoff, jogo em andamento, rodadas inconsistentes e jogo adiado e remarcado (superseded fora; remarcado no kickoff real; kickoff antigo = KICKOFF_MISMATCH), fixture duplicada = recusa. Prova do revert do a51a68d: falha com o hunk de ordenação revertido, passa restaurado, worktree apagado, wheel publicada inalterada.",
     [GA, GW, f"{Q}/RAW_LOGS/temporal-suite/kickoff_revert_proof.log"]),
    ("BR_TIMEZONE_INTEGRITY", "PASS", "Sedes America/Sao_Paulo, Manaus, Cuiaba e Rio_Branco (offsets -03/-04/-05) normalizam para os mesmos instantes; horário de verão antes de 2019 com offset explícito correto; hora local sem fuso (inclusive a repetida e a inexistente) rejeitada; kickoff sem fuso no dataset dá TEMPORAL_INTEGRITY_VIOLATION. Inventário de todos os pontos que leem datas no truth-map.",
     [GA, GW, f"{Q}/RAW_LOGS/truth-map/date_sites_e14f339.json"]),
    ("BR_SAME_KICKOFF_ISOLATION", "PASS", "Resultado do jogo A não muda a previsão do jogo B de mesmo kickoff (nem do jogo seguinte que começa com A em andamento), byte a byte; o teste enxerga a mudança num jogo posterior. Dado real: par de mesmo kickoff de 2024 com o mesmo resultado.",
     [f"{Q}/SAME_KICKOFF_REPORT.md", GA, GW, RC]),
    ("BR_METAMORPHIC", "PASS", "5 permutações congeladas (seeds 11, 23, 37, 41, 53) da ordem das linhas: resultado idêntico pelo comparador congelado nos 3 ambientes; soak 5 ciclos; dado real 1 permutação idêntica.",
     [f"{Q}/METAMORPHIC_REPORT.md", f"{Q}/FROZEN_VECTORS.json", GA, GW, RC]),
    ("BR_CACHE_STATE", "PASS", "Caches do momento da captura (envenenados) nunca lidos; histórico em processo novo igual ao histórico depois de rodar uma data futura no mesmo estado (processos novos) e no mesmo processo (memo de refit compartilhado); dado real com caches envenenados idêntico.",
     [f"{Q}/CACHE_STATE_REPORT.md", GA, GW, RC]),
    ("BR_FUTURE_INJECTION", "PASS", "Placar de jogo que não poderia ter terminado antes do as_of injetado no banco: TEMPORAL_INTEGRITY_VIOLATION pelo caminho real (entrypoint, Ops, handler), sem resultado; data_cutoff depois do as_of recusado; jogo em andamento excluído; kickoff sem fuso rejeitado.",
     [f"{Q}/FUTURE_CANARY_REPORT.md", GA, GW]),
]


def main() -> None:
    ledger = HERE / "ledger.py"
    for gate, status, note, evidence in GATES:
        subprocess.run([sys.executable, str(ledger), "gate", gate, status, note, *evidence], check=True)
    print(len(GATES), "gates")


if __name__ == "__main__":
    main()
