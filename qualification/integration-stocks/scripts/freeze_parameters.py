"""integration-stocks, freeze-parameters (C15): grava FROZEN_PARAMETERS.json antes de qualquer execução de gate.

Tudo o que é número, lista ou identidade da missão sai daqui, com sha256 da fonte:
  * base do Stocks (runtime_target, D-24) e as fontes da configuração da DecisionPolicy do Stocks, lidas com
    ``git show 61fc017256ffea815ae96bbe02b847dccdb395cc:<arquivo>`` (SHA completo; nada depois da base, D-24):
      - stocks_predictor/research_admission.py → closed_hypotheses() (H1..H22, estado preservado como o repo grava);
      - trials_v2.json (hypothesis_family) e trials.json (<hn>_factor.name, só onde trials_v2 diz UNKNOWN) → famílias
        das hipóteses encerradas (congeladas: nunca reabertas);
      - config.yaml [H1-FROZEN] execution.b3_fee_pct / spread_slippage_pct → custos 3 / 15 bps;
      - EXTERNAL_INTELLIGENCE_TRIAL_READINESS_MATRIX.json → famílias de External Intelligence e prontidão;
  * contrato do Stocks e framework herdado da integration-crypto (final_commits/final_wheels da attestation QUALIFIED);
  * ambientes, dados, operador, plano de fases e gates.

Uso (ferramentas da missão): python freeze_parameters.py <raiz do predictor-qualification> <clone do stocks-predictor>
"""

from __future__ import annotations

import ast
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT, STOCKS = Path(sys.argv[1]), Path(sys.argv[2])
MISSION = ROOT / "qualification/integration-stocks"
BASE = "61fc017256ffea815ae96bbe02b847dccdb395cc"
PR96 = "36081a66004a464d5e9c5ea4bc6e208d0fcb582e"
TREE = "bea6dce6adea5cc2c0d917b5e2265507ec64708d"
SOURCE_FILES = ("stocks_predictor/research_admission.py", "trials_v2.json", "trials.json", "config.yaml",
                "EXTERNAL_INTELLIGENCE_TRIAL_READINESS_MATRIX.json")


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def git(*args: str) -> bytes:
    return subprocess.run(["git", "-C", str(STOCKS), *args], capture_output=True, check=True).stdout


def fsha(rel: str) -> dict:
    raw = (ROOT / rel).read_bytes()
    return {"path": rel, "sha256": sha(raw)}


def load(rel: str):
    return json.loads((ROOT / rel).read_bytes())


def closed_hypotheses(source: str) -> dict:
    """Evaluate only closed_hypotheses() of research_admission.py at the base (literals and comprehensions)."""
    tree = ast.parse(source)
    function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "closed_hypotheses")
    namespace: dict = {}
    exec(compile(ast.Module(body=[function], type_ignores=[]), "research_admission.py", "exec"), namespace)  # noqa: S102
    return namespace["closed_hypotheses"]()


def main() -> int:
    if git("rev-parse", f"{BASE}^{{tree}}").decode().strip() != TREE:
        raise SystemExit("árvore da base diverge")
    raw = {path: git("show", f"{BASE}:{path}") for path in SOURCE_FILES}
    files = [{"path": p, "git_blob": git("rev-parse", f"{BASE}:{p}").decode().strip(), "sha256": sha(raw[p])}
             for p in SOURCE_FILES]
    closed = dict(sorted(closed_hypotheses(raw["stocks_predictor/research_admission.py"].decode()).items(),
                         key=lambda kv: int(kv[0].split(":H")[1])))
    trials_v2, trials = json.loads(raw["trials_v2.json"]), json.loads(raw["trials.json"])
    families = {}
    for legacy, modern in zip(trials, trials_v2, strict=True):
        hyp = f"stocks:{modern['hypothesis_id']}"
        family = modern["hypothesis_family"]
        derived = "trials_v2.json hypothesis_family"
        if family == "UNKNOWN":
            key = f"{modern['hypothesis_id'].lower()}_factor.name"
            family = legacy["params"][key]
            derived = f"trials.json params['{key}'] (trials_v2.json diz UNKNOWN)"
        families[hyp] = {"family": family, "derived_from": derived, "status": closed[hyp]}
    config_yaml = raw["config.yaml"].decode()
    fee = float(re.search(r"^\s*b3_fee_pct:\s*([0-9.]+)\s*# \[H1-FROZEN\]", config_yaml, re.M).group(1))
    slip = float(re.search(r"^\s*spread_slippage_pct:\s*([0-9.]+)\s*# \[H1-FROZEN\]", config_yaml, re.M).group(1))
    costs = {"fee_bps": round(fee * 10000), "slippage_bps": round(slip * 10000)}
    if costs != {"fee_bps": 3, "slippage_bps": 15}:
        raise SystemExit(f"custos da base divergem: {costs}")
    matrix = json.loads(raw["EXTERNAL_INTELLIGENCE_TRIAL_READINESS_MATRIX.json"])
    contract_rel = "qualification/stocks/DOMAIN_RESEARCH_CONTRACT.json"
    contract = load(contract_rel)
    ic = load("qualification/integration-crypto/QUALIFICATION_ATTESTATION.json")
    if ic["result"] != "QUALIFIED":
        raise SystemExit("integration-crypto não está QUALIFIED")
    framework = {w["name"]: w for w in ic["final_wheels"] if "/cain/" in w["url"] or "/ecosystem-predictor/" in w["url"]}
    fc = {c["repo"]: c["commit_sha"] for c in ic["final_commits"]}
    rt = load("qualification/stocks/runtime_target.json")
    decisions = load("qualification/DECISIONS.json")["decisions"]
    approved = [d["decision_id"] for d in decisions if d["status"] == "APPROVED"]
    frozen_families = sorted({v["family"] for v in families.values()})
    stocks_config = {
        "source": {"repo": "stocks-predictor", "commit": BASE, "files": files,
                   "contract": fsha(contract_rel),
                   "note": "leituras por git show com o SHA completo da base; 36081a6 (mesma árvore) não é usado aqui"},
        "allowed_request_types": sorted(contract["handler_allowlist"]),
        "closed_hypotheses": closed,
        "closed_hypotheses_families": families,
        "frozen_families": frozen_families,
        "proposable_hypotheses": sorted(["stocks:QUAL-PIT-MOM-001", "stocks:QUAL-PIT-MOM-REAL-001",
                                         "stocks:QUAL-PIT-MOM-REAL-002", "stocks:QUAL-PIT-MOM-REAL-003",
                                         "stocks:QUAL-EI-COLLECTION-001"]),
        "allowed_symbols": [],
        "costs": dict(costs, source="config.yaml [H1-FROZEN] execution.b3_fee_pct 0.0003 e spread_slippage_pct "
                                    "0.0015 em 61fc017 (os mesmos do cost_model h1-frozen do contrato)"),
        "baselines": ["ew-universe v1"],
        "allowed_references": {
            "dataset": ["b3-cvm-real v1", "b3-cvm-real-canary v1", "positive v1"],
            "universe": ["real v1", "conformance v1"],
            "features": ["momentum-12-1 v1", "momentum v1"],
            "model": ["quintile-real v1", "quintile v1"],
            "baseline": ["ew-universe v1"],
            "cost_model": ["h1-frozen v1"],
            "readiness": ["matrix-20260921 v1"],
            "source": ["vlmo-real v1"],
        },
        "max_priority_hint": "NORMAL",
        "budget": {"max_open_tasks": 1, "max_tasks_per_research": 64, "max_tasks_total": 512},
        "cooldown": {"after_consecutive_negative": 3, "episodes": 2,
                     "negative_result_states": ["NO_EDGE", "INCONCLUSIVE", "REFUTED", "NOT_READY",
                                                "CLOSED_INSUFFICIENT_SAMPLE", "INCONCLUSIVE_DATA_QUALITY"]},
        "signal_families": {
            "momentum": [h for h, v in families.items() if v["family"].startswith("momentum")],
            "near_52w_high": [h for h, v in families.items() if v["family"] == "near_52w_high"],
            "low_volatility": [h for h, v in families.items() if v["family"] == "low_vol_252"],
            "volume": [h for h, v in families.items() if v["family"] == "volume_surge"],
            "external_intelligence": {
                "matrix": "EXTERNAL_INTELLIGENCE_TRIAL_READINESS_MATRIX.json (61fc017)",
                "rule": "elegibilidade só pelo campo readiness da matriz; TRIAL_CONSUMPTION de família não READY ⇒ "
                        "NOT_READY pelo domínio; a DecisionPolicy não promove família nenhuma",
                "families": sorted(set(re.findall(r'"(B3_[A-Z_]+|CVM_[A-Z_]+)"', json.dumps(matrix)))),
            },
            "note": "famílias das hipóteses encerradas = frozen_families (R05 bloqueia proposta que as declare); as "
                    "sondas de qualificação stocks:QUAL-PIT-MOM-* são de outra família "
                    "(stocks-qualification-momentum-12-1-pit, Etapa A) e reusam declaradamente o protocolo 12-1 sem "
                    "reabrir a H1",
        },
        "known_cautions": {
            "ST-F007": "rebalance a cada 21 pregões (universe.rebalance_every_sessions = 21, o que o handler compilado "
                       "aceita), nunca 'fim de mês' (D-21)",
            "ST-F008": "painel público só-preço com lacunas de eventos (D-21): a DecisionPolicy não lê métrica "
                       "nenhuma; estados científico/econômico só entram como registro e nunca aumentam budget, "
                       "prioridade ou escopo",
            "C22": "QUALIFIED da Etapa A não é edge econômico; WATCH/WATCH_NO_CAPITAL nunca viram sinal nem capital",
        },
        "framework_limits_found_before_freeze": [
            {"id": "R06-custos-em-todo-pedido",
             "fact": "policy.decide compara config.costs com parameters de todo pedido; COLLECT_EXTERNAL_INTELLIGENCE "
                     "não tem fee_bps/slippage_bps ⇒ sempre BLOCK COST_MODEL_MISMATCH (n1/17-collection)",
             "decision": "não mudar o framework (6.4 do prompt da sessão; mudança = C14 do cripto); registrado como "
                         "achado; o CAIN desta missão não propõe coleta"},
            {"id": "llm-placebo-seed",
             "fact": "cain.orchestration.llm grava parameters.placebo_seed (parâmetro do cripto); o request_schema do "
                     "Stocks recusa campo extra ⇒ proposta de LLM do Stocks = BLOCK SCHEMA_INVALID (n1/18-llm-shape)",
             "decision": "não mudar o framework; as ≥ 5 propostas de LLM do soak são geradas, auditadas e passam pela "
                         "mesma política (não são gate, C9); registrado como achado"},
        ],
    }
    doc = {
        "schema": "integration-stocks/FROZEN_PARAMETERS/1",
        "phase": "freeze-parameters",
        "stage": "B",
        "branch": "integration-stocks",
        "code": "INTEGRATION_STOCKS",
        "envelope_version": "V2",
        "common_baseline": fsha("qualification/shared/STACK_BASELINE_V2.0.json") | {"id": "STACK_BASELINE_V2.0"},
        "shown_to_owner": "mostrado ao dono antes de congelar: no PR da missão no predictor-qualification (primeiro "
                          "commit da fase) e no relatório da sessão. Aprovar = merge. Mudar qualquer valor depois = "
                          "novo ciclo da fase inteira (C14 'Parâmetro/vetor/perfil congelado').",
        "identity": {
            "common_core": fsha("qualification/COMMON_QUALIFICATION_CORE.md") | {"version": "2.3"},
            "attestation_schema": fsha("qualification/ATTESTATION_SCHEMA.json"),
            "mission_prompt": fsha("prompts/prompt_etapa_b_stocks_rev9.md"),
            "common_prompt": fsha("prompts/prompt_etapa_b_comum_rev9.md"),
            "auditor_principles": fsha("prompts/PRINCIPIOS_AUDITOR.md"),
            "decisions": fsha("qualification/DECISIONS.json"),
            "hygiene": fsha("qualification/HYGIENE.json"),
            "c0_logs": [fsha(f"qualification/integration-stocks/RAW_LOGS/c0/{p.name}")
                        for p in sorted((MISSION / "RAW_LOGS/c0").glob("*.log"))],
        },
        "decisions_cited": {
            "approved_on_main": approved,
            "D-1": "WINDOWS_SMOKE do Stocks no GitHub Actions windows-latest × 3.13; nada no Windows local",
            "D-5": "um agente por missão, sem subagentes",
            "D-6": "conta do dono via gh; branches, PRs, workflows e pré-releases; sem merge nem push em main",
            "D-9": "Linux primário = GitHub Actions ubuntu-latest × 3.13",
            "D-11": "repositório público; nada de segredo nem dado sem direito de redistribuição",
            "D-12": "Etapa B: domínio só nos adapter_paths; fora disso C24.4",
            "D-16": "Stocks: só dados públicos B3/CVM por URL + sha256 fixados antes de cada execução",
            "D-18": "precedente dos recibos R8 como evidência de engenharia da regra local",
            "D-21": "ST-F007, ST-F008 aceitos; COTAHIST por snapshot fixado",
            "D-22": "segunda integração; reutiliza o framework da integration-crypto",
            "D-24": "base 61fc017/0.3.0rc2; estado do CAIN só da base; WINDOWS_SMOKE no Actions; R8 × C24.3(a)",
        },
        "base": {
            "stocks_runtime_target": {"commit": rt["commit"], "wheel_url": rt["wheel_url"],
                                      "wheel_sha256": rt["wheel_sha256"], "version": "0.3.0rc2", "tree": TREE,
                                      "same_tree_merge_pr96": PR96,
                                      "stack": {"predictor-core": {"version": "3.2.1",
                                                                   "sha256": contract["implementation"]["core"]["sha256"]},
                                                "predictor-ops": {"version": "4.2.2rc1",
                                                                  "sha256": contract["implementation"]["ops"]["sha256"]}}},
            "stocks_stage_a_attestation": fsha("qualification/stocks/QUALIFICATION_ATTESTATION.json"),
            "stocks_contract": fsha(contract_rel),
            "envelope_freeze": fsha("qualification/shared/ENVELOPE_V2_FREEZE.json"),
            "framework_from_integration_crypto": {
                "attestation": fsha("qualification/integration-crypto/QUALIFICATION_ATTESTATION.json"),
                "decision_policy_report": fsha("qualification/integration-crypto/DECISION_POLICY_REPORT.md"),
                "final_commits": {"cain": fc["cain"], "ecosystem-predictor": fc["ecosystem-predictor"]},
                "final_wheels": {name: {"version": w["version"], "url": w["url"], "sha256": w["sha256"]}
                                 for name, w in sorted(framework.items())},
            },
        },
        "repos": {
            "stocks-predictor": {"role": "só stocks_predictor/adapters/ + C24.3(a) (versão pré-release) + D-24 (4): "
                                         "tests/adapters/ novos e arquivos do procedimento R8", "base": BASE},
            "cain": {"role": "só configuração do Stocks: src/cain/orchestration/data/stocks.json, entrada stocks em "
                             "tools/build_domain_config.py, testes dela, versão e lock", "base": fc["cain"]},
            "ecosystem-predictor": {"role": "só a entrada stocks na allowlist fixa do transporte "
                                            "(packages/research-transport) + testes e versão; research-protocol não muda",
                                    "base": fc["ecosystem-predictor"]},
            "cripto-predictor": {"role": "não muda", "base": fc["cripto-predictor"]},
            "brasileirao-predictor": {"role": "não muda"},
            "core-predictor": {"role": "congelado (wheel 3.2.1)", "base": fc["core-predictor"]},
            "predictor-ops": {"role": "congelado (wheel 4.2.2rc1)", "base": fc["predictor-ops"]},
        },
        "c14_integration_crypto": {
            "why": "a configuração do domínio vive na wheel do cain (importlib.resources) e a allowlist do transporte é "
                   "fixa no código: acrescentar o Stocks publica cain e predictor-research-transport novos; C14 "
                   "('cain, ecosystem-predictor') e o §3.3 do prompt do Stocks mandam refazer as fases da "
                   "integration-crypto que os exercitam (E2E, N+1, isolamento) e reemitir a attestation dela no mesmo "
                   "ciclo",
            "phases": ["cleanroom-final", "contract-revalidation", "e2e", "n-plus-1", "isolation-ids-contradiction",
                       "idempotency-failure", "windows-smoke", "hosted-ci", "soak", "attestation"],
            "rule": "mesmos vetores, perfil e parâmetros congelados da integration-crypto; só runtime_targets.json muda",
        },
        "environments": {
            "primary": {"os": "linux", "python": "3.13", "where": "github_actions", "host": "ubuntu-latest (D-9, D-16)"},
            "secondary": {"os": "windows", "python": "3.13", "where": "github_actions",
                          "host": "windows-latest (D-1, D-24)",
                          "attestation_item_fields": ["os", "python", "role", "where", "result", "evidence"]},
            "diagnostic_only": "WSL Ubuntu 24.04 do PC 2: desenvolvimento, diagnóstico e recibos R8 (não é owner_linux; "
                               "nunca PROVEN)",
        },
        "data": {
            "gate_data": "só públicos B3/CVM, baixados no job pela URL oficial e conferidos pelo sha256 fixado antes do "
                         "run; nunca versionados nem publicados como artefato (D-11, D-16)",
            "builder": fsha("qualification/stocks/d16/build_real_panel.py"),
            "builder_use": "reuso sem mudança: `pin` grava qualification/integration-stocks/data/SOURCES-<run>.json "
                           "(commit antes do run); `build` confere cada hash e falha fechado",
            "prefilter_verifier": fsha("qualification/stocks/d16/verify_prefilter.py"),
            "protocol_real": fsha("qualification/stocks/d16/PROTOCOL_REAL.json"),
            "future_canary": {
                "token": "FUTURE_CANARY_STOCKS_INTEGRATION_001",
                "dataset_reference": "b3-cvm-real-canary v1",
                "construction": "cópia do painel real do run com dataset_version + '-canary' e UMA barra a mais: o "
                                "primeiro security_id (ordem lexicográfica) com barra no último pregão, sessão = "
                                "data do data_cutoff + 3 dias, close 987.654321, volume_fin 123456789.0, available_at = "
                                "sessão + 1 dia 03:00:00Z, e 'canary' = {token, security_id, session, close} (a mesma "
                                "regra do vetor future_canary da conformidade da Etapa A); data_cutoff igual",
                "expected": "TEMPORAL_INTEGRITY_VIOLATION (LookaheadError), nenhum resultado autoritativo; token e "
                            "instante pós-cutoff nunca na memória nem no retrieval do CAIN",
            },
            "r8_only": "~/predictors/data/d16/stocks/COTAHIST_A2026.ZIP (sha256 34b774681cbd201ef197fb98af8d431e4d7302e8"
                       "01f58b66e54036d2935dc4f4, 55.986 linhas) só no procedimento R8 da D-24, nunca em gate",
        },
        "operator_env": {
            "note": "fronteira do operador do Stocks (não do CAIN): mesmos objetos da D-16 (PROTOCOL_REAL.json, painel "
                    "do construtor, matriz de prontidão do final_commit, fonte VLMO) + o painel canário; três "
                    "hipóteses de qualificação no lugar de uma (rodízio exigido pelo cooldown da política)",
            "stage_a_reference": fsha("qualification/stocks/d16/real_env.py"),
            "policy_id": "stocks-integration-qualification",
            "hypotheses": ["stocks:QUAL-PIT-MOM-REAL-001", "stocks:QUAL-PIT-MOM-REAL-002",
                           "stocks:QUAL-PIT-MOM-REAL-003", "stocks:QUAL-EI-COLLECTION-001"],
            "hypothesis_family": "stocks-qualification-momentum-12-1-pit",
            "references": {"dataset": ["b3-cvm-real v1", "b3-cvm-real-canary v1"], "universe": "real v1",
                           "features": "momentum-12-1 v1", "model": "quintile-real v1", "baseline": "ew-universe v1",
                           "cost_model": "h1-frozen v1", "readiness": "matrix-20260921 v1", "source": "vlmo-real v1"},
            "limits": "PROTOCOL_REAL.json policy.limits, sem mudança",
            "research_id": "stocks:RESEARCH-INTEGRATION-QUALIFICATION",
            "request_parameters": {"target": "NEXT_REBALANCE_RETURN", "fee_bps": 3, "slippage_bps": 15,
                                   "max_securities": 5000, "external_intelligence": {"mode": "NONE", "families": []}},
        },
        "decision_policy": {
            "id": "cain-decision-policy", "version": 1,
            "framework": "sem mudança (integration-crypto); regras R01–R14 do DECISION_POLICY_REPORT.md herdado",
            "stocks_config": stocks_config,
        },
        "n_plus_1": {"processes": 3, "equality": "receipt byte a byte", "as_of": "2026-09-27T00:00:00Z",
                     "vectors": "FROZEN_VECTORS.json → n_plus_1",
                     "integrated_variant": "além do conjunto congelado (C9), o mesmo N+1 roda no job integrado com um "
                                           "resultado V2 real do cripto entregue ao spool do Stocks (recusado); os "
                                           "receipts têm de ser iguais aos do conjunto congelado",
                     "llm": "proibido no caminho do receipt (C9); LLM só no soak"},
        "isolation": {"crypto": "runtime integrado (cain com as duas configurações + consumidores do cripto e do Stocks "
                                "no mesmo job, dados reais de cada domínio)",
                      "brasileirao": "fixtures V2 congeladas (integration-crypto/fixtures/v2, FIXTURES_MANIFEST.json)",
                      "h9_ids": ["crypto:H9", "stocks:H9", "brasileirao:H9"]},
        "failure_matrix": fsha("qualification/integration-stocks/FAILURE_MATRIX.json"),
        "soak_profile": fsha("qualification/integration-stocks/QUALIFICATION_PROFILE_INTEGRATION_STOCKS_V1.json"),
        "frozen_vectors": fsha("qualification/integration-stocks/FROZEN_VECTORS.json"),
        "r8_d24": {
            "source": "~/predictors/data/d16/stocks/COTAHIST_A2026.ZIP",
            "source_sha256": "34b774681cbd201ef197fb98af8d431e4d7302e801f58b66e54036d2935dc4f4",
            "rows": 55986,
            "receipt": "docs/research/2026-09-10-r6/evidence/acquisitions.json entrada [3] (a confirmar)",
            "capacity_rows": 250000,
            "output_dir": "docs/engineering/<AAAA-MM-DD>-integration-stocks/evidence/ (só .json)",
            "seal": "tools/materialize_current_operational_evidence.py → docs/engineering/current-operational-evidence.json",
            "coverage_floor": 77,
            "status": "evidência de engenharia da regra local (D-18, D-24), nunca evidência de gate",
        },
        "protected_set_initial": {
            "rule": "C15.1: o conjunto só cresce; lista completa em PROTECTED_SET.json no fim de truth-map",
            "stocks_stage_a": [fsha("qualification/stocks/PROTECTED_SET.json"),
                               fsha("qualification/stocks/FROZEN_VECTORS.json"),
                               fsha("qualification/stocks/runtime_target.json"),
                               fsha("qualification/stocks/DOMAIN_RESEARCH_CONTRACT.json")],
            "integration_crypto": [fsha("qualification/integration-crypto/QUALIFICATION_ATTESTATION.json"),
                                   fsha("qualification/integration-crypto/FROZEN_VECTORS.json"),
                                   fsha("qualification/integration-crypto/fixtures/v2/FIXTURES_MANIFEST.json"),
                                   fsha("qualification/integration-crypto/FAILURE_MATRIX.json"),
                                   fsha("qualification/integration-crypto/QUALIFICATION_PROFILE_INTEGRATION_CRYPTO_V1.json")],
            "shared": [fsha("qualification/shared/ENVELOPE_V2_FREEZE.json"),
                       fsha("qualification/shared/STACK_BASELINE_V2.0.json"),
                       fsha("qualification/COMMON_QUALIFICATION_CORE.md"),
                       fsha("qualification/ATTESTATION_SCHEMA.json")],
            "mission": [fsha("qualification/integration-stocks/FAILURE_MATRIX.json"),
                        fsha("qualification/integration-stocks/QUALIFICATION_PROFILE_INTEGRATION_STOCKS_V1.json"),
                        fsha("qualification/integration-stocks/FROZEN_VECTORS.json")],
            "never_read": "nada de 61fc017..main do stocks-predictor (D-24): research/scientific_state.json, "
                          "policy/stocks-evaluation-policy-v1.json, stocks_predictor/v2, holdout selado do v2",
        },
        "gates_required": ["BLOCKERS_ZERO", "STACK_BASELINE_FROZEN", "LOCK_INTEGRITY", "CORE_IDENTITY",
                           "CLEANROOM_FINAL", "HOSTED_CI", "E2E", "IDEMPOTENCY", "RESTART_RECOVERY",
                           "FAILURE_INJECTION", "PROVENANCE", "AUTHORITY_SEPARATION", "FUTURE_CANARY",
                           "PROTECTED_ARTIFACTS_UNCHANGED", "SOAK", "WINDOWS_SMOKE", "SHARED_DEPENDENCY_CLEAR",
                           "EVIDENCE_CONSISTENCY", "SECRETS_CLEAN", "CAPITAL_FORBIDDEN", "ENVELOPE_V2_CONFORMANCE",
                           "CAIN_INGESTION", "CAIN_CONTAINMENT", "DECISION_POLICY", "N_PLUS_1_DETERMINISTIC",
                           "NEGATIVE_RESULT_NEUTRALITY", "CROSS_DOMAIN_ISOLATION", "DOMAIN_QUALIFIED_IDS",
                           "CONTRADICTION_PRESERVATION", "DOMAIN_CONTRACTS_PRESERVED"],
        "hosted_ci_rule": {
            "rule": "prompt da sessão 9.3: só o run de evento push cujo SHA é exatamente o final_commit vale (C21)",
            "stocks_predictor_constraint": "o ci.yml do stocks-predictor (intocável pela D-24 (4c)) só dispara push em "
                                           "main; um final_commit de branch nunca tem run de push. A Etapa A usou "
                                           "workflow_dispatch no SHA exato. Pendência do dono; não é relaxado aqui",
        },
        "phases": ["freeze-parameters", "baseline", "truth-map", "cleanroom-baseline", "envelope-v2", "domain-adapter",
                   "cain-wiring-decision-policy", "publish-candidates", "cleanroom-final", "contract-revalidation", "e2e",
                   "n-plus-1", "isolation-ids-contradiction", "idempotency-failure", "windows-smoke", "hosted-ci",
                   "soak", "attestation"],
        "absolute": {"capital_permission": False, "training_started": False, "holdout_use": "nenhum",
                     "cain_operational_mode": "proibido", "broker_or_exchange_connection": "proibida"},
    }
    raw_doc = json.dumps(doc, indent=1, ensure_ascii=False).encode("utf-8") + b"\n"
    (MISSION / "FROZEN_PARAMETERS.json").write_bytes(raw_doc)
    print("FROZEN_PARAMETERS.json", sha(raw_doc))
    print(json.dumps({"closed": len(closed), "frozen_families": frozen_families}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
