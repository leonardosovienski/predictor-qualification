"""integration-crypto, fase freeze-parameters (C15): grava FROZEN_PARAMETERS.json.

Todos os números e listas do prompt da missão, da parte comum da Etapa B e das decisões do dono; os hashes dos
arquivos citados são calculados aqui a partir de um checkout do predictor-qualification (ref do C0) e dos
clones dos repositórios (só `git show`/`rev-parse`, com SHA completo). Nada é executado dos repositórios.

Uso: python freeze_parameters.py --qualification <checkout no ref do C0> --mission-dir <qualification/integration-crypto>
                                 --repos <dir dos clones> --c0-ref <sha> --out <FROZEN_PARAMETERS.json>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

CRYPTO_BASE = "341d270e4d709150c581c3cd93f4518d483009eb"
OTHER_BASES = {
    "stocks-predictor": "61fc017256ffea815ae96bbe02b847dccdb395cc",
    "brasileirao-predictor": "25cdf4d9bb309d33f066fbc6a379f5d98c69f08a",
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=True).stdout.strip()


def blob(repo: Path, commit: str, path: str) -> dict:
    raw = subprocess.run(["git", "-C", str(repo), "show", f"{commit}:{path}"], capture_output=True, check=True).stdout
    return {"path": path, "git_blob": git(repo, "rev-parse", f"{commit}:{path}"),
            "sha256": hashlib.sha256(raw).hexdigest()}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--qualification", type=Path, required=True)
    ap.add_argument("--mission-dir", type=Path, required=True)
    ap.add_argument("--repos", type=Path, required=True)
    ap.add_argument("--c0-ref", required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    q, m = a.qualification, a.mission_dir
    manifest = dict(reversed(line.split("  ", 1)) for line in (q / "MANIFEST.sha256").read_text().splitlines() if line)
    decisions = json.loads((q / "qualification/DECISIONS.json").read_text(encoding="utf-8"))["decisions"]
    decision_ids = [d["decision_id"] for d in decisions if d["status"] == "APPROVED"]
    freeze = json.loads((q / "qualification/shared/ENVELOPE_V2_FREEZE.json").read_text(encoding="utf-8"))
    target = json.loads((q / "qualification/crypto/runtime_target.json").read_text(encoding="utf-8"))
    crypto_repo = a.repos / "cripto-predictor"
    state_blob = blob(crypto_repo, CRYPTO_BASE, "charters/scientific_state.json")
    state = json.loads(subprocess.run(["git", "-C", str(crypto_repo), "show",
                                       f"{CRYPTO_BASE}:charters/scientific_state.json"],
                                      capture_output=True, check=True).stdout)
    costs_blob = blob(crypto_repo, CRYPTO_BASE, "GarimpoInvestimentos/v3/costs.py")
    fixtures = m / "fixtures/v2"
    fixture_manifest = json.loads((fixtures / "FIXTURES_MANIFEST.json").read_text(encoding="utf-8"))

    def mission_file(name: str) -> dict:
        return {"path": f"qualification/integration-crypto/{name}", "sha256": sha256_file(m / name)}

    def qual_file(rel: str) -> dict:
        return {"path": rel, "sha256": sha256_file(q / rel)}

    frozen = {
        "schema": "integration-crypto/FROZEN_PARAMETERS/1",
        "phase": "freeze-parameters",
        "stage": "B",
        "branch": "integration-crypto",
        "code": "INTEGRATION_CRYPTO",
        "envelope_version": "V2",
        "common_baseline": {"id": "STACK_BASELINE_V2.0",
                            "sha256": sha256_file(q / "qualification/shared/STACK_BASELINE_V2.0.json")},
        "shown_to_owner": "mostrado ao dono antes de congelar: no PR da missão no predictor-qualification (este arquivo é o "
                          "primeiro commit) e no relatório da sessão. Aprovar = merge. Mudar qualquer valor depois = "
                          "novo ciclo da fase inteira (C14 'Parâmetro/vetor/perfil congelado').",
        "identity": {
            "evidence_main_at_c0": a.c0_ref,
            "common_core_version": "2.3",
            "common_core_sha256": sha256_file(q / "qualification/COMMON_QUALIFICATION_CORE.md"),
            "attestation_schema_sha256": manifest["qualification/ATTESTATION_SCHEMA.json"],
            "mission_prompt": qual_file("prompts/prompt_etapa_b_crypto_rev9.md"),
            "common_prompt": qual_file("prompts/prompt_etapa_b_comum_rev9.md"),
            "auditor_principles": qual_file("prompts/PRINCIPIOS_AUDITOR.md"),
            "decisions_json_sha256": sha256_file(q / "qualification/DECISIONS.json"),
            "hygiene_json_sha256": sha256_file(q / "qualification/HYGIENE.json"),
            "c0_log": {"path": "qualification/integration-crypto/RAW_LOGS/c0/c0_preflight.log",
                       "sha256": sha256_file(m / "RAW_LOGS/c0/c0_preflight.log")},
        },
        "decisions_cited": {
            "approved_on_main_at_c0": decision_ids,
            "D-3": "Windows secundário local do cripto (a pasta desta missão vem da D-23)",
            "D-5": "um agente por missão, sem subagentes",
            "D-6": "conta do dono via gh; branches, PRs, workflows e pré-releases; sem merge nem push em main",
            "D-9": "Linux primário = GitHub Actions ubuntu-latest × 3.13",
            "D-11": "repositório de evidência público; nada de segredo nem dado sem direito de redistribuição",
            "D-12": "Etapa B: domínio só nos adapter_paths; fora disso C24.4",
            "D-13": "integração V1 extinta",
            "D-15": "jobs de CI fora de lock fora do push/PR",
            "D-16": "cripto: dados públicos da Binance no Actions, conferidos pelo .CHECKSUM, nunca versionados",
            "D-22": "Etapa B em três missões; esta é a primeira e cria o framework no cain",
            "D-23": {
                "status_at_freeze": "PENDENTE DE MERGE (predictor-qualification PR #56); decisão explícita do dono no "
                                    "prompt da sessão, 2026-09-27",
                "rule": "a attestation só cita a D-23 depois que ela estiver no origin/main",
                "content": "base 341d270/1.2.0rc2 (main do cripto não é base nem runtime; nada de #128–#134); estado "
                           "do CAIN só de 341d270 (SHA completo) e do contrato no main; WINDOWS_SMOKE no PC 2 em "
                           "C:\\Cripto\\qualificacao\\runtime\\integration-crypto\\",
            },
        },
        "base": {
            "crypto_runtime_target": {"commit": target["commit"], "version": target["version"],
                                      "wheel_url": target["wheel_url"], "wheel_sha256": target["wheel_sha256"],
                                      "tree": git(crypto_repo, "rev-parse", f"{CRYPTO_BASE}^{{tree}}"),
                                      "squash_on_main_same_tree": "174573df4884b5455f9b38ecc933bf48c67ff4df",
                                      "stack": target["stack"]},
            "adapter_worktree_start": "174573df4884b5455f9b38ecc933bf48c67ff4df (mesma árvore de 341d270; D-23)",
            "envelope_freeze": qual_file("qualification/shared/ENVELOPE_V2_FREEZE.json"),
            "protocol": {k: freeze["protocol"][k] for k in ("package", "version", "tag", "tag_commit")}
                        | {"wheel_url": freeze["protocol"]["wheel"]["url"],
                           "wheel_sha256": freeze["protocol"]["wheel"]["sha256"]},
            "stage_a_attestation_crypto": qual_file("qualification/crypto/QUALIFICATION_ATTESTATION.json"),
            "domain_contract_crypto": qual_file("qualification/crypto/DOMAIN_RESEARCH_CONTRACT.json"),
        },
        "repos": {
            "cain": {"role": "muda (framework genérico + configuração do cripto)",
                     "base": "f343701937a7a798d66e11d2d8aa18e24395e215"},
            "ecosystem-predictor": {"role": "muda (transporte + consumidor); packages/research-protocol não muda",
                                    "base": "49ffb16380d2e91eb7e4a2a936e63ba779c29033"},
            "cripto-predictor": {"role": "só GarimpoInvestimentos/adapters/ + exceções C24.3(a) (versão pré-release)",
                                 "base": CRYPTO_BASE},
            "core-predictor": {"role": "congelado (wheel 3.2.1)", "base": "5a0841509f091ea0aa95bde0d3d65e2a1a9e984d"},
            "predictor-ops": {"role": "congelado (wheel 4.2.2rc1)", "base": "9831b0d5e727972b1d85ff48be14ffa58677898b"},
            "stocks-predictor": {"role": "não muda", "base": OTHER_BASES["stocks-predictor"]},
            "brasileirao-predictor": {"role": "não muda", "base": OTHER_BASES["brasileirao-predictor"]},
        },
        "design_constraints_found_before_freeze": [
            {"id": "sem-console-script-no-dominio",
             "rule": "SPEC_V2 §9 (congelada): o adapter não ganha console script no cripto; o consumidor do "
                     "transporte (ecosystem) carrega o adapter pelo nome do módulo",
             "evidence": {"path": "qualification/integration-crypto/RAW_LOGS/diag-import-closure/probe_adapter_entrypoint.log",
                          "sha256": sha256_file(m / "RAW_LOGS/diag-import-closure/probe_adapter_entrypoint.log")},
             "why": "tests/conformance/test_import_closure.py::test_no_entrypoint_reaches_envelope_cain_or_adapter_paths "
                    "(congelado) falha com cripto-research-adapter → adapters (C24.3 c)"},
            {"id": "adapter-sem-dependencia-do-protocolo",
             "rule": "o cripto não ganha dependência predictor-research-protocol: o adapter usa só stdlib + adapter_api; "
                     "a validação e a embalagem V2 (validate_task/build_result) ficam no consumidor do transporte",
             "why": "tests/test_shared_wheel_download_hashes.py::test_lock_pins_stack_wheels_by_release_url_and_sha256 e "
                    "scripts/verify_installed_wheels.py (CI do domínio, C24.3 f) exigem predictor-research-protocol e "
                    "cain-research fora do uv.lock do cripto"},
            {"id": "loop-pr50",
             "rule": "prompt comum §4 opção (b): `cain loop` (execução direta do avaliador) sai dos entrypoints e vira "
                     "ferramenta de laboratório (`python -m cain.loop`), com teste de fecho de imports",
             "why": "a opção (a) exigiria tipos de pedido que o contrato do cripto não tem (só "
                    "BACKTEST_EXISTING_HYPOTHESIS); mudar contrato ou protocolo é C24.4/C14"},
        ],
        "environments": {
            "primary": {"os": "linux", "python": "3.13", "where": "github_actions", "host": "ubuntu-latest (D-9, D-16)"},
            "secondary": {"os": "windows", "python": "3.13", "where": "local_windows",
                          "host": "PC 2 do dono, C:\\Cripto\\qualificacao\\runtime\\integration-crypto\\ (D-23)",
                          "tools": "uv e Python 3.13 gerenciados dentro da pasta; zip do uv conferido contra o .sha256"},
            "diagnostic_only": "WSL Ubuntu 24.04 do PC 2 (não é owner_linux nesta missão; nunca PROVEN)",
        },
        "data": {
            "source": "Binance data.vision futures/um BTCUSDT (klines 1d + fundingRate), públicos",
            "builder": qual_file("qualification/crypto/scripts/build_real_dataset.py"),
            "integrity": ".CHECKSUM publicado de cada zip (falha fechada); nunca versionados nem publicados como artefato",
            "in_sample": {"start": "2025-09-01T00:00:00Z", "data_cutoff": "2026-08-31T00:00:00Z"},
            "future_canary": {"token": "FUTURE_CANARY_CRYPTO_001", "end": "2026-09-21T00:00:00Z",
                              "dataset_reference": "real-future-canary v1"},
            "windows_copies": "~/predictors/data/d16/cripto/ (SHA256SUMS.txt, CRLF lido com tr -d '\\r'), copiadas para a "
                              "pasta Windows por PowerShell, sha256 conferido antes e depois",
            "binance_api": "proibida (nenhuma conta, chave ou conexão operacional)",
        },
        "operator_env": {
            "note": "policy de operador da qualificação (fronteira do operador do domínio), igual à da Etapa A "
                    "(qualification/crypto/scripts/real_env.py) com três hipóteses de qualificação no lugar de uma",
            "stage_a_reference": qual_file("qualification/crypto/scripts/real_env.py"),
            "hypotheses": ["crypto:QUAL-SHADOW-REAL-001", "crypto:QUAL-SHADOW-REAL-002", "crypto:QUAL-SHADOW-REAL-003"],
            "hypothesis_family": "crypto-qualification-fixed-shadow",
            "references": {"protocol": "fixed-shadow v1", "dataset": ["real-in-sample v1", "real-future-canary v1"],
                           "baseline": "flat v1 (gross/net 0 bps)", "cost_model": "v3-frozen v1 (fee 10, slippage 5)",
                           "evidence": "none v1"},
            "limits": {"max_pending_requests": 1000, "max_request_bytes": 16384, "max_parameter_bytes": 1024,
                       "max_concurrency": 1, "cpu_seconds": 120, "memory_mb": 512, "disk_mb": 256,
                       "timeout_seconds": 120, "max_retries": 2, "max_priority": "NORMAL"},
            "request_parameters": {"symbol": "BTCUSDT", "horizon_days": 7, "max_observations": 100, "fee_bps": 10,
                                   "slippage_bps": 5, "placebo_seed": "0..999 (distingue pedidos; nunca escolhido "
                                   "olhando resultado)"},
            "research_id": "crypto:RESEARCH-INTEGRATION-QUALIFICATION",
        },
        "decision_policy": {
            "id": "cain-decision-policy",
            "version": 1,
            "decisions": ["ALLOW", "BLOCK", "ABSTAIN", "REQUIRE_HUMAN", "DUPLICATE", "COOLDOWN"],
            "deterministic": "sem LLM, sem relógio: entradas = proposta canônica + configuração do domínio + estado do "
                             "domínio no as_of (memória, outbox, inbox, episódios); receipt = JSON canônico com id e sha256 "
                             "do código e da configuração",
            "rule_order": [
                "BLOCK DOMAIN_MISMATCH: proposta, pedido ou algum ID de outro domínio, ou ID sem domínio (C18)",
                "BLOCK SCHEMA_INVALID: pedido inválido contra o request_schema do contrato (validador do protocolo congelado)",
                "BLOCK FORBIDDEN_FIELD: proposta com campo fora do formato (handler, comando, módulo, caminho, URL, budget, "
                "prioridade final, capital)",
                "BLOCK REQUEST_TYPE_NOT_ALLOWED: request_type fora das chaves da handler_allowlist do contrato",
                "BLOCK HYPOTHESIS_CLOSED: hipótese crypto:H1..crypto:H9 (estado científico em 341d270, inclusive H7/H8 "
                "REGISTERED_NOT_ACTIVATED) ou família congelada funding_oi_hmm_v3",
                "BLOCK COST_MODEL_MISMATCH / SYMBOL_NOT_ALLOWED / PRIORITY_ABOVE_CAP / REFERENCE_NOT_ALLOWED",
                "BLOCK REQUEST_ID_CONFLICT: mesmo request_id com outro conteúdo já no outbox do domínio",
                "DUPLICATE: mesmo conteúdo de pedido já emitido no domínio (qualquer episódio)",
                "REQUIRE_HUMAN DOMAIN_RECONCILIATION_PENDING: algum resultado REQUIRES_HUMAN do domínio sem resolução",
                "REQUIRE_HUMAN CONTRADICTION_UNRESOLVED: resultados terminais da mesma hipótese com estados científicos "
                "em conflito (SUPPORTED × REFUTED); nunca decidido por maioria",
                "REQUIRE_HUMAN NEW_HYPOTHESIS: hipótese fora da lista de hipóteses propostas da configuração",
                "ABSTAIN OPEN_TASK_PENDING / BUDGET_EXHAUSTED",
                "COOLDOWN NEGATIVE_STREAK: depois de N resultados negativos seguidos da mesma hipótese, K episódios sem "
                "nova task dela",
                "ALLOW",
            ],
            "crypto_config": {
                "source": {"repo": "cripto-predictor", "commit": CRYPTO_BASE,
                           "files": [state_blob, costs_blob],
                           "contract": qual_file("qualification/crypto/DOMAIN_RESEARCH_CONTRACT.json")},
                "allowed_request_types": ["BACKTEST_EXISTING_HYPOTHESIS"],
                "closed_hypotheses": {f"crypto:{k}": v for k, v in state["hypotheses"].items()},
                "frozen_families": state["frozen_families"],
                "proposable_hypotheses": ["crypto:QUAL-SHADOW-REAL-001", "crypto:QUAL-SHADOW-REAL-002",
                                          "crypto:QUAL-SHADOW-REAL-003", "crypto:QUAL-SHADOW-001"],
                "allowed_symbols": ["BTCUSDT"],
                "costs": {"fee_bps": 10, "slippage_bps": 5,
                          "source": "GarimpoInvestimentos/v3/costs.py em 341d270 (taker 10 bps, slippage 5 bps)"},
                "baselines": ["flat v1"],
                "allowed_references": {
                    "protocol": ["fixed-shadow v1"], "dataset": ["real-in-sample v1", "real-future-canary v1",
                                                                 "positive v1", "future-canary v1"],
                    "baseline": ["flat v1"], "cost_model": ["v3-frozen v1"], "evidence": ["none v1"]},
                "max_priority_hint": "NORMAL",
                "budget": {"max_open_tasks": 1, "max_tasks_per_research": 64, "max_tasks_total": 512},
                "cooldown": {"after_consecutive_negative": 3, "episodes": 2,
                             "negative_result_states": ["NO_EDGE", "INCONCLUSIVE", "REFUTED", "CLOSED_INSUFFICIENT_SAMPLE",
                                                        "INCONCLUSIVE_DATA_QUALITY"]},
                "economic_signal": "nenhum: QUALIFIED da Etapa A e WATCH/WATCH_NO_CAPITAL nunca aumentam budget, prioridade, "
                                   "escopo nem capital (prompt do cripto §5)",
            },
        },
        "n_plus_1": {
            "processes": 3,
            "equality": "receipt byte a byte",
            "as_of": "2026-09-27T00:00:00Z",
            "fixture": {"path": "qualification/integration-crypto/fixtures/v2/FIXTURES_MANIFEST.json",
                        "sha256": sha256_file(fixtures / "FIXTURES_MANIFEST.json"),
                        "files": fixture_manifest["files"]},
            "llm": "proibido no caminho do receipt (C9); LLM só no soak",
        },
        "isolation": {
            "other_domains": ["stocks", "brasileirao"],
            "mode": "fixtures V2 congeladas (prompt do cripto §4), mesmo H9 nos três",
            "h9_ids": ["crypto:H9", "stocks:H9", "brasileirao:H9"],
        },
        "failure_matrix": mission_file("FAILURE_MATRIX.json"),
        "soak_profile": mission_file("QUALIFICATION_PROFILE_INTEGRATION_CRYPTO_V1.json"),
        "protected_set_initial": {
            "rule": "C15.1: o conjunto só cresce; lista completa em PROTECTED_SET.json no fim de truth-map",
            "crypto_stage_a": [qual_file("qualification/crypto/PROTECTED_SET.json"),
                               qual_file("qualification/crypto/FROZEN_VECTORS.json")],
            "stocks_stage_a": [qual_file("qualification/stocks/PROTECTED_SET.json"),
                               qual_file("qualification/stocks/FROZEN_VECTORS.json")],
            "brasileirao_stage_a": [qual_file("qualification/brasileirao/PROTECTED_SET.json"),
                                    qual_file("qualification/brasileirao/FROZEN_VECTORS.json")],
            "shared": [qual_file("qualification/shared/ENVELOPE_V2_FREEZE.json"),
                       qual_file("qualification/shared/STACK_BASELINE_V2.0.json"),
                       qual_file("qualification/COMMON_QUALIFICATION_CORE.md"),
                       qual_file("qualification/ATTESTATION_SCHEMA.json"),
                       qual_file("qualification/crypto/runtime_target.json")],
            "mission": [mission_file("FAILURE_MATRIX.json"),
                        mission_file("QUALIFICATION_PROFILE_INTEGRATION_CRYPTO_V1.json"),
                        {"path": "qualification/integration-crypto/fixtures/v2/FIXTURES_MANIFEST.json",
                         "sha256": sha256_file(fixtures / "FIXTURES_MANIFEST.json")}],
            "never_read": "nada de 174573d..main do cripto (D-23): nenhum arquivo dessa faixa entra neste conjunto",
        },
        "gates_required": [
            "BLOCKERS_ZERO", "STACK_BASELINE_FROZEN", "LOCK_INTEGRITY", "CORE_IDENTITY", "CLEANROOM_FINAL", "HOSTED_CI",
            "E2E", "IDEMPOTENCY", "RESTART_RECOVERY", "FAILURE_INJECTION", "PROVENANCE", "AUTHORITY_SEPARATION",
            "FUTURE_CANARY", "PROTECTED_ARTIFACTS_UNCHANGED", "SOAK", "WINDOWS_SMOKE", "SHARED_DEPENDENCY_CLEAR",
            "EVIDENCE_CONSISTENCY", "SECRETS_CLEAN", "CAPITAL_FORBIDDEN", "ENVELOPE_V2_CONFORMANCE", "CAIN_INGESTION",
            "CAIN_CONTAINMENT", "DECISION_POLICY", "N_PLUS_1_DETERMINISTIC", "NEGATIVE_RESULT_NEUTRALITY",
            "CROSS_DOMAIN_ISOLATION", "DOMAIN_QUALIFIED_IDS", "CONTRADICTION_PRESERVATION", "DOMAIN_CONTRACTS_PRESERVED",
        ],
        "hosted_ci_rule": "só o run de push cujo SHA é exatamente o final_commit vale (C21); run de pull_request testa outro SHA",
        "phases": ["freeze-parameters", "baseline", "truth-map", "cleanroom-baseline", "envelope-v2", "domain-adapter",
                   "cain-wiring-decision-policy", "publish-candidates", "cleanroom-final", "contract-revalidation", "e2e",
                   "n-plus-1", "isolation-ids-contradiction", "idempotency-failure", "windows-smoke", "hosted-ci",
                   "soak", "attestation"],
        "absolute": {"capital_permission": False, "training_started": False, "holdout_use": "nenhum",
                     "cain_operational_mode": "proibido", "exchange_connection": "proibida"},
    }
    raw = json.dumps(frozen, indent=1, ensure_ascii=False).encode("utf-8") + b"\n"
    a.out.write_bytes(raw)
    print(a.out, hashlib.sha256(raw).hexdigest())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
