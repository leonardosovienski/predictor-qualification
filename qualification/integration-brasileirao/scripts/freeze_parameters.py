"""integration-brasileirao, freeze-parameters (C15): grava FROZEN_PARAMETERS.json antes de qualquer execução de gate.

Tudo o que é número, lista ou identidade da missão sai daqui, com sha256 da fonte:
  * base do Brasileirão (runtime_target rc3, D-25 (1)); fontes da configuração da DecisionPolicy lidas com
    ``git show 25cdf4d9bb309d33f066fbc6a379f5d98c69f08a:<arquivo>`` (SHA completo; nada depois da base, D-25 (2)):
      - data/trials.json → trials com status ``refutada`` (lido como negativo/encerrado pelo PR #51 do cain:
        cain.findings.ingest.STATUS_KIND) = hipóteses encerradas;
  * contrato do Brasileirão no main: request_schema, handler_allowlist, protected_hypotheses_required (H8, H9, H14,
    H15, A1: a admission recusa, a política bloqueia), season_policy (2025 HOLDOUT_SEALED);
  * memória herdada (D-25 (2)): loop do PR #50 (ledger versionado no cain em deccaaa, só identidade e desfecho) e
    achados do PR #51 sobre os registros da base; pino das 22 fontes de tools/hypothesis_sources.json conferido
    (RAW_LOGS/freeze/hypothesis_sources_pin_check.log);
  * framework herdado da integration-stocks QUALIFIED (final_commits/final_wheels de cain e ecosystem-predictor);
  * ambientes (owner_linux e Windows local do PC 2), dado real privado, operador, plano de fases e gates.

Uso (ferramentas da missão): python freeze_parameters.py <raiz do predictor-qualification>
    <clone bare do brasileirao-predictor> <clone bare do cain>
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT, BR, CAIN = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
M = "qualification/integration-brasileirao"
MISSION = ROOT / M
BASE = "25cdf4d9bb309d33f066fbc6a379f5d98c69f08a"
MERGE = "d80a4edee94ca0219ec308911d56628499792885"
TREE = "88b1efa6167655b21b9603c144a423755ef8fb46"
CAIN_BASE = "deccaaa0a0e2cb2b5f292614659eb4bf2e943e50"
LOOP_EVIDENCE = ("docs/evidence/2026-09-24-prompt6-loop-pesquisa.md", "docs/evidence/2026-09-24-prompt6/ledger-events.jsonl")
LOOP_HYPOTHESIS = "brasileirao:CAIN-LOOP.BR-ELO-TUNING-DEV2022"
LOOP_FAMILY = "brasileirao-elo-1x2-dev2022"
DATA_SHA = "31f30a4dcf33867d1f3aa3d12337a9a66047e6bff10b9a3fa86aae9ef06c9e43"
DATASET_AS_OF = "2026-09-08T19:31:32Z"
QUAL = ["brasileirao:QUAL-SERVING-REAL-001", "brasileirao:QUAL-SERVING-REAL-002", "brasileirao:QUAL-SERVING-REAL-003"]


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def git(repo: Path, *args: str) -> bytes:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, check=True).stdout


def fsha(rel: str) -> dict:
    return {"path": rel, "sha256": sha((ROOT / rel).read_bytes())}


def load(rel: str):
    return json.loads((ROOT / rel).read_bytes())


def pinned(repo: Path, commit: str, path: str) -> tuple[bytes, dict]:
    raw = git(repo, "show", f"{commit}:{path}")
    return raw, {"path": path, "git_blob": git(repo, "rev-parse", f"{commit}:{path}").decode().strip(), "sha256": sha(raw)}


def main() -> int:
    if git(BR, "rev-parse", f"{BASE}^{{tree}}").decode().strip() != TREE:
        raise SystemExit("árvore da base diverge")
    if git(BR, "rev-parse", f"{MERGE}^{{tree}}").decode().strip() != TREE:
        raise SystemExit("árvore de d80a4ed diverge da base")
    trials_raw, trials_ref = pinned(BR, BASE, "data/trials.json")
    trials = json.loads(trials_raw)
    # identidade da linha como em cain.findings.ingest.ingest_trial_registry: trial_id ou name
    refuted = [str(t.get("trial_id") or t.get("name")) for t in trials if t.get("status") == "refutada"]
    if len(refuted) != 6:
        raise SystemExit(f"esperados 6 trials refutados na base, achados {len(refuted)}")
    statuses = sorted({t.get("status") for t in trials})
    loop_doc_raw, loop_doc_ref = pinned(CAIN, CAIN_BASE, LOOP_EVIDENCE[0])
    ledger_raw, ledger_ref = pinned(CAIN, CAIN_BASE, LOOP_EVIDENCE[1])
    loops = {}
    for line in ledger_raw.decode("utf-8").splitlines():
        event = json.loads(line)
        body, loop = event.get("body") or {}, event.get("loop_id") or event.get("stream")
        if event["kind"] == "loop.started":
            loops[loop] = {"hypothesis": body["hypothesis"], "world_id": body["world_id"]}
        elif event["kind"] == "loop.stopped":
            loops[loop].update(stop=body["reason"], attempts=body["attempts"])
        elif event["kind"] == "experiment.finished" and body.get("improved") and body.get("step_kind") != "baseline":
            loops[loop]["improved"] = True
    if sorted(loops) != ["loop:brasileirao-dev2022-1", "loop:brasileirao-dev2022-2"] or any(
            v.get("improved") or v["stop"] != "stagnation" for v in loops.values()):
        raise SystemExit(f"loops do PR #50 divergem do esperado: {loops}")
    if {v["world_id"] for v in loops.values()} != {LOOP_FAMILY}:
        raise SystemExit("world_id do loop diverge")
    contract_rel = "qualification/brasileirao/DOMAIN_RESEARCH_CONTRACT.json"
    contract = load(contract_rel)
    protected = contract["admission_policy"]["protected_hypotheses_required"]
    seasons = contract["admission_policy"]["season_policy"]
    if protected != ["brasileirao:H8", "brasileirao:H9", "brasileirao:H14", "brasileirao:H15", "brasileirao:A1"]:
        raise SystemExit(f"protegidas divergem: {protected}")
    if seasons.get("2025") != "HOLDOUT_SEALED":
        raise SystemExit("contrato não lacra 2025")
    closed = {f"brasileirao:{t}": "REFUTED (data/trials.json status refutada em 25cdf4d; PR #51: negativo)"
              for t in refuted}
    closed.update({h: "PROTECTED_BY_ADMISSION (contrato: protected_hypotheses_required)" for h in protected})
    closed[LOOP_HYPOTHESIS] = ("NO_IMPROVEMENT_OVER_BASELINE (loop do PR #50: 2 ciclos, estagnação; hipótese "
                               "CAIN-LOOP:BR-ELO-TUNING-DEV2022 do ledger, com ':' trocado por '.' para o padrão "
                               "brasileirao:<id>)")
    closed = dict(sorted(closed.items()))
    rt = load("qualification/brasileirao/runtime_target.json")
    ist = load("qualification/integration-stocks/QUALIFICATION_ATTESTATION.json")
    if ist["result"] != "QUALIFIED":
        raise SystemExit("integration-stocks não está QUALIFIED")
    fc = {c["repo"]: c["commit_sha"] for c in ist["final_commits"]}
    if fc["cain"] != CAIN_BASE:
        raise SystemExit("final_commit do cain diverge")
    framework = {w["name"]: w for w in ist["final_wheels"] if "/cain/" in w["url"] or "/ecosystem-predictor/" in w["url"]}
    decisions = load("qualification/DECISIONS.json")["decisions"]
    approved = [d["decision_id"] for d in decisions if d["status"] == "APPROVED"]
    if "D-25" not in approved:
        raise SystemExit("D-25 não está no main")
    references = {"dataset": ["real-20260908 1", "real-canary-20260908 1", "synthetic 1"],
                  "model": ["serving-baseline 1"], "features": ["elo-home-advantage 1"],
                  "baseline": ["climatology 1", "market 1"], "cost_model": ["close-slippage-tax 1"],
                  "odds": ["sofascore-close 1"]}
    brasileirao_config = {
        "source": {"repo": "brasileirao-predictor", "commit": BASE, "files": [trials_ref],
                   "trial_statuses_at_base": statuses, "contract": fsha(contract_rel),
                   "note": "leituras por git show com o SHA completo da base; d80a4ed (mesma árvore) não é usado aqui"},
        "allowed_request_types": sorted(contract["handler_allowlist"]),
        "closed_hypotheses": closed,
        "frozen_families": [LOOP_FAMILY],
        "proposable_hypotheses": sorted(["brasileirao:HQ-SERVING-BASELINE", *QUAL]),
        "allowed_symbols": [],
        "costs": {},
        "costs_note": "o request_schema do Brasileirão não tem parameters: nenhum custo entra pelo pedido; o modelo de "
                      "custo (odds de fechamento, slippage de 2% nos ganhos, IR de 15% sobre o lucro anual positivo) é "
                      "a referência cost_model close-slippage-tax 1 do operador (real_env.py da Etapa A)",
        "allowed_references": references,
        "max_priority_hint": "NORMAL",
        "budget": {"max_open_tasks": 1, "max_tasks_per_research": 64, "max_tasks_total": 512},
        "cooldown": {"after_consecutive_negative": 3, "episodes": 2,
                     "negative_result_states": ["NO_EDGE", "INCONCLUSIVE", "REFUTED", "CLOSED_INSUFFICIENT_SAMPLE",
                                                "INCONCLUSIVE_DATA_QUALITY"]},
        "contradiction_pairs": [["REFUTED", "SUPPORTED"]],
        "metrics_and_baselines": {
            "metrics": ["RPS (métrica primária; menor é melhor)", "Brier", "log-loss", "calibração",
                        "P&L líquido (economics do resultado, com o cost_model)"],
            "baselines": {"climatology 1": "CLIMATOLOGY_PIT", "market 1": "MARKET_CLOSE_SHIN (odds de mercado)"},
            "odds": "sofascore-close 1 (fechamento; só avaliação econômica ex post, nunca entra na previsão)",
            "rule": "o CAIN não lê métrica nenhuma para decidir: estados científico/econômico entram como registro, "
                    "nunca aumentam budget, prioridade ou escopo; nenhuma baseline de mercado financeiro",
        },
        "sealed_scopes": [
            {"field": "season", "any_of": [2025, 2026]},
            {"window": {"from": "events.kickoff_from", "to": "events.kickoff_to"},
             "intersects": ["2025-01-01T00:00:00Z", "2026-01-01T00:00:00Z"]},
            {"field": "events.fixtures[].kickoff_at", "within": ["2025-01-01T00:00:00Z", "2026-01-01T00:00:00Z"],
             "optional": True},
        ],
        "sealed_scopes_criterion": {
            "criterion": "D-25 (2): proposta que exigiria acesso ao holdout 2025 → REQUIRE_HUMAN (a admission do "
                         "domínio continua podendo recusar). Leitura conservadora: season 2025 ou 2026 (2026 treina com "
                         "resultados de 2025); janela [events.kickoff_from, events.kickoff_to) que intersecta "
                         "[2025-01-01T00:00:00Z, 2026-01-01T00:00:00Z); ou algum events.fixtures[].kickoff_at dentro "
                         "dela. Campo lacrado ausente ou mal formado retém o pedido (fail closed)",
            "rule": "R16 REQUIRE_HUMAN SEALED_SCOPE da política v2 do cain (cain#65), avaliada logo depois da R05",
            "materialized_in_cain_config": True,
            "cycle_1": "no ciclo 1 (base deccaaa, política v1) o critério não era materializável (IB-F002)",
        },
    }
    doc = {
        "schema": "integration-brasileirao/FROZEN_PARAMETERS/1",
        "phase": "freeze-parameters",
        "stage": "B",
        "branch": "integration-brasileirao",
        "code": "INTEGRATION_BR",
        "envelope_version": "V2",
        "common_baseline": fsha("qualification/shared/STACK_BASELINE_V2.0.json") | {"id": "STACK_BASELINE_V2.0"},
        "shown_to_owner": "mostrado ao dono antes de congelar: no PR da missão no predictor-qualification (primeiro "
                          "commit da fase) e no relatório da sessão. Aprovar = merge. Mudar qualquer valor depois = "
                          "novo ciclo da fase inteira (C14 'Parâmetro/vetor/perfil congelado').",
        "identity": {
            "common_core": fsha("qualification/COMMON_QUALIFICATION_CORE.md") | {"version": "2.3"},
            "attestation_schema": fsha("qualification/ATTESTATION_SCHEMA.json"),
            "mission_prompt": fsha("prompts/prompt_etapa_b_brasileirao_rev9.md"),
            "common_prompt": fsha("prompts/prompt_etapa_b_comum_rev9.md"),
            "auditor_principles": fsha("prompts/PRINCIPIOS_AUDITOR.md"),
            "decisions": fsha("qualification/DECISIONS.json"),
            "hygiene": fsha("qualification/HYGIENE.json"),
            "c0_logs": [fsha(f"{M}/RAW_LOGS/c0-20260928-pass/{p.name}")
                        for p in sorted((MISSION / "RAW_LOGS/c0-20260928-pass").glob("*.log"))],
        },
        "decisions_cited": {
            "approved_on_main": approved,
            "D-3": "Windows de qualificação local (Brasileirão)",
            "D-5": "um agente por missão, sem subagentes",
            "D-6": "conta do dono via gh; branches, PRs, workflows e pré-releases; sem merge nem push em main",
            "D-11": "repositório público; nada de segredo nem dado sem direito de redistribuição",
            "D-12": "Etapa B: domínio só nos adapter_paths; fora disso C24.4",
            "D-16": "Brasileirão: dado privado; E2E e SOAK no PC 2 sobre matches_source_copy.sqlite3 (31f30a4d…)",
            "D-19": "PC 2 = owner_linux, Linux primário só para dado real privado; PROVISION_RECEIPT.json como prova",
            "D-22": "terceira integração; reutiliza o framework da integration-crypto sem mudar",
            "D-25": "base 25cdf4d/0.3.0rc3 (d80a4ed igual); estado do CAIN só da base; memória herdada do PR #50/#51 só "
                    "como referência, resumo e hash; holdout 2025 → REQUIRE_HUMAN; WINDOWS_SMOKE no PC 2",
        },
        "base": {
            "brasileirao_runtime_target": {"commit": rt["commit"], "wheel_sha256": rt["wheel_sha256"],
                                           "sdist_sha256": rt.get("sdist_sha256"), "version": rt["version"],
                                           "tree": TREE, "same_tree_merge_pr80": MERGE,
                                           "stack": {k: {"version": v["version"], "sha256": v["sha256"]}
                                                     for k, v in rt["stack"].items()}},
            "brasileirao_stage_a_attestation": fsha("qualification/brasileirao/QUALIFICATION_ATTESTATION.json"),
            "brasileirao_contract": fsha(contract_rel),
            "envelope_freeze": fsha("qualification/shared/ENVELOPE_V2_FREEZE.json"),
            "framework_from_integration_stocks": {
                "attestation": fsha("qualification/integration-stocks/QUALIFICATION_ATTESTATION.json"),
                "decision_policy_reports": [fsha("qualification/integration-crypto/DECISION_POLICY_REPORT.md"),
                                            fsha("qualification/integration-stocks/DECISION_POLICY_REPORT.md")],
                "final_commits": {"cain": fc["cain"], "ecosystem-predictor": fc["ecosystem-predictor"]},
                "final_wheels": {name: {"version": w["version"], "url": w["url"], "sha256": w["sha256"]}
                                 for name, w in sorted(framework.items())},
                "mains_not_incorporated": "cain main 0e8ae79 (política v2 #59, 0.4.13rc8 não publicada) e "
                                          "ecosystem-predictor main 1fa9098 (mesma árvore): IB-F001",
            },
        },
        "memory_inheritance": {
            "rule": "D-25 (2): só referência, resumo e hash; nada do dado real; proposta equivalente (mesma hipótese, "
                    "mesma família ou mesmo conteúdo de pedido) → BLOCK (R05) ou DUPLICATE (R08), com receipt",
            "hypothesis_sources_pin": {
                "file": "cain deccaaa:tools/hypothesis_sources.json (reviewed_commit e540f97, 22 fontes do Brasileirão)",
                "check": fsha(f"{M}/RAW_LOGS/freeze/hypothesis_sources_pin_check.log"),
                "script": fsha(f"{M}/scripts/hypothesis_sources_pin_check.py"),
                "result": "22/22 byte a byte iguais entre e540f97 e 25cdf4d; 22/22 com o sha256 declarado na base",
                "pin_used": "25cdf4d9bb309d33f066fbc6a379f5d98c69f08a para toda leitura desta missão; e540f97 só "
                            "como equivalente comprovado do arquivo do cain",
            },
            "pr50_loop": {"source": {"repo": "cain", "commit": CAIN_BASE, "files": [loop_doc_ref, ledger_ref]},
                          "loops": loops, "closed_as": LOOP_HYPOTHESIS, "frozen_family": LOOP_FAMILY},
            "pr51_findings": {"source": {"repo": "brasileirao-predictor", "commit": BASE, "files": [trials_ref]},
                              "negative_closed": [f"brasileirao:{t}" for t in refuted],
                              "rows": len(trials), "statuses": statuses,
                              "identity_rule": "o identificador literal de um trial só entra na memória se passar no "
                                               "no_data_rows_check (nome de time do dado real ⇒ entra só o sha256 do "
                                               "identificador, com a referência de linha)"},
        },
        "repos": {
            "brasileirao-predictor": {"role": "só brasileirao_predictor/adapters/ + C24.3(a): versão pré-release e, se "
                                              "necessário, adapter_entrypoint em [project.scripts] e dependências "
                                              "predictor-research-*/cain-research", "base": BASE},
            "cain": {"role": "só configuração do Brasileirão: src/cain/orchestration/data/brasileirao.json, entrada "
                             "brasileirao em tools/build_domain_config.py, testes dela, versão e lock", "base": fc["cain"]},
            "ecosystem-predictor": {"role": "só a entrada brasileirao na allowlist fixa do transporte "
                                            "(packages/research-transport) + testes e versão; research-protocol não muda",
                                    "base": fc["ecosystem-predictor"]},
            "cripto-predictor": {"role": "não muda", "base": fc["cripto-predictor"]},
            "stocks-predictor": {"role": "não muda", "base": fc["stocks-predictor"]},
            "core-predictor": {"role": "congelado (wheel 3.2.1)", "base": fc["core-predictor"]},
            "predictor-ops": {"role": "congelado (wheel 4.2.2rc1)", "base": fc["predictor-ops"]},
        },
        "cycle": {
            "number": 3,
            "supersedes": {"path": f"{M}/FROZEN_PARAMETERS_cycle2_1c9e11bd702b.json",
                           "sha256_prefix": "1c9e11bd702b"},
            "release_name": "a release única da decisão do dono ('rc8' nos textos dos ciclos 2 e 3) foi publicada como "
                            "v0.4.13rc10 (tag → fb0e1dc; cain#70 só sobe a versão): a v0.4.13rc9 já existia (a "
                            "pré-release desta missão de 3e515fd, política v1); só o nome muda",
            "cycle_3": "a release única rc8 passa a levar também os PRs da sessão STOCKS (cain#67–#69: R04 por "
                       "hipótese, R17 DUPLICATE EQUIVALENT_REQUEST, justificativa do LLM conferida), mergeados pelo "
                       "dono antes da publicação; o rule_order congelado tem de nomear a política que roda. "
                       "brasileirao_config sem mudança; nenhum limiar, holdout, critério ou waiver muda; fases refeitas "
                       "a partir do cleanroom-final (C14)",
            "cycle_2_supersedes": {"path": f"{M}/FROZEN_PARAMETERS_cycle1_e5f254bd5d44.json",
                                   "sha256_prefix": "e5f254bd5d44"},
            "why": "decisão do dono no chat desta sessão, 2026-09-28 (pergunta com opções): 'Trocar para a rc8 "
                   "(Recommended)': a base do cain passa de deccaaa (rc7/rc9, política v1) para a release única "
                   "v0.4.13rc8 com a R16; C14 'Parâmetro/vetor/perfil congelado' ⇒ a fase inteira como novo ciclo e as "
                   "fases dependentes refeitas a partir do cleanroom-final",
            "unchanged": "base do Brasileirão (25cdf4d / rc3 → adapter rc4), contrato, dado, operador, ambientes, "
                         "matriz de falhas, conjunto protegido e todos os vetores fora do holdout",
        },
        "c14_other_integrations_cycle2": {
            "rule": "a release única rc8 muda o cain de todas as integrações; pela decisão do dono (sessões cripto e "
                    "STOCKS, 2026-09-28) cada sessão requalifica a sua integração na rc8; esta missão não refaz as fases "
                    "da integration-crypto nem da integration-stocks",
        },
        "c14_other_integrations": {
            "why": "a configuração do domínio vive na wheel do cain e a allowlist do transporte é fixa no código: "
                   "acrescentar o Brasileirão publica cain e predictor-research-transport novos; C14 ('cain, "
                   "ecosystem-predictor') manda refazer as fases da integration-crypto e da integration-stocks que os "
                   "exercitam e reemitir as duas no mesmo ciclo",
            "phases": ["cleanroom-final", "contract-revalidation", "e2e", "n-plus-1", "isolation-ids-contradiction",
                       "idempotency-failure", "windows-smoke", "hosted-ci", "soak", "attestation"],
            "rule": "mesmos vetores, perfil e parâmetros congelados de cada uma; só os alvos de runtime (cain e "
                    "transporte) mudam",
            "protected_attestations": "as attestations atuais das duas ficam preservadas byte a byte em "
                                      "QUALIFICATION_ATTESTATION_superseded_<sha12>.json e encadeadas por "
                                      "supersedes_sha256 (C7.1 regra 8); PROTECTED_ARTIFACTS_UNCHANGED confere essa "
                                      "cadeia, no mesmo critério da decisão do dono no IS-F006 da integration-stocks; "
                                      "aplicar esse critério a esta missão é pendência do dono",
            "owner_line": "informação recebida da sessão cripto em 2026-09-28 (não vale como aprovação nesta sessão): o "
                          "dono teria escolhido manter as integrações na linha rc7 (política v1) e reconciliar tudo "
                          "numa release única no fim, com C14 das três; se isso substituir o C14 desta missão, é "
                          "decisão do dono a registrar",
        },
        "environments": {
            "primary": {"os": "linux", "python": "3.13", "role": "primary", "where": "owner_linux",
                        "host": "PC 2, Ubuntu 24.04 WSL2 (PROVISION_RECEIPT.json, D-19)",
                        "receipt": {"path": "~/predictors/PROVISION_RECEIPT.json",
                                    "sha256": "ee2a75d1b7901561daab27f197e3860c3f42db0221b320804a3bcdab8babb1a0"}},
            "secondary": {"os": "windows", "python": "3.13", "role": "secondary", "where": "local_windows",
                          "host": "PC 2, C:\\QUALIFICACAO\\runtime\\integration-brasileirao\\ (D-25 (3))",
                          "attestation_item_fields": ["os", "python", "role", "where", "result", "evidence"]},
            "hosted_ci": "GitHub Actions dos repositórios tocados, só testes sintéticos; nenhum dado real",
        },
        "data": {
            "source": {"path": "~/predictors/data/d16/brasileirao/matches_source_copy.sqlite3", "sha256": DATA_SHA,
                       "bytes": 55754752, "mode": "somente leitura (555); abertura mode=ro&immutable=1"},
            "copy": "~/predictors/runtime/integration-brasileirao/data/matches_source_copy.sqlite3 (sha256 conferido "
                    "antes e depois de cada uso)",
            "dataset_capture": {"reference": "real-20260908 1", "as_of": DATASET_AS_OF,
                                "command": "brasileirao-research put-dataset --as-of 2026-09-08T19:31:32Z --label "
                                           "real-20260908 (como real_env.py da Etapa A)"},
            "future_canary": {
                "token": "FUTURE_CANARY_BR_INTEGRATION_001",
                "dataset_reference": "real-canary-20260908 1",
                "construction": "cópia privada da cópia do dado (sha256 conferido) com DUAS partidas a mais, nas mesmas "
                                "tabelas e forma do vetor FUTURE_CANARY_BR_001 da conformidade da Etapa A "
                                "(tests/conformance/fixtures.py em 25cdf4d): times token × um time do próprio dado, "
                                "competição/temporada 2024, kickoff 2024-10-20T22:00:00Z e 2024-10-27T22:00:00Z (depois "
                                "do data_cutoff 2024-10-01T00:00:00Z do pedido e antes do as_of do dataset), placares "
                                "17×0 e 0×17; capturada com o mesmo as_of; sha256 da cópia registrado; nada versionado",
                "expected": "resultado do pedido 03-canary igual ao do controle 04-canary-control (mesmas previsões, "
                            "métricas e estados; só referências, IDs e provenance diferem); token e as duas partidas "
                            "nunca na memória, no retrieval nem nos receipts do CAIN",
            },
            "private_outputs": "~/predictors/runtime/integration-brasileirao/priv/ (resultados show, commands.log, "
                               "qualquer saída com conteúdo por jogo); só sha256 e agregados vão para RAW_LOGS",
            "no_data_rows_check": fsha("qualification/brasileirao/scripts/no_data_rows_check.py"),
            "holdout_2025": "lacrado: nenhum pedido despachado com temporada ≥ 2025 ou janela em 2025; nunca usado "
                            "direta ou indiretamente para ajustar, escolher, validar, comparar ou depurar",
        },
        "operator_env": {
            "stage_a_reference": fsha("qualification/brasileirao/scripts/real_env.py"),
            "policy_id": "brasileirao-integration-qualification",
            "hypotheses": sorted(["brasileirao:HQ-SERVING-BASELINE", *QUAL]),
            "hypothesis_family": "brasileirao:serving-baseline",
            "references": references,
            "limits": "os da policy real da Etapa A (real_env.py): max_pending_requests 100, max_concurrency 1, "
                      "timeout 3600 s, max_retries 2, max_priority NORMAL",
            "research_id": "brasileirao:RESEARCH-INTEGRATION-QUALIFICATION",
            "seasons_requested": [2021, 2022, 2023, 2024],
        },
        "decision_policy": {
            "id": "cain-decision-policy", "version": 2,
            "framework": "release única do cain v0.4.13rc8 (decisão do dono de 2026-09-28): política v2 (cain#59, "
                         "R15), custos e semente do LLM pelas variantes do contrato (cain#62), configuração do "
                         "Brasileirão (cain#64 e o PR que materializa os sealed_scopes) e a regra genérica de escopo "
                         "lacrado R16 (cain#65); ciclo 3: tipo de pedido por hipótese proponível na R04 e no molde "
                         "do LLM (cain#67; configuração proposable_request_types, que para o Brasileirão é o único tipo "
                         "permitido), R17 DUPLICATE EQUIVALENT_REQUEST (cain#68) e a justificativa do LLM conferida "
                         "contra a visão (cain#69); o commit e a wheel da release vão para runtime_targets.json na "
                         "publicação",
            "rule_order": ["R01 BLOCK DOMAIN_MISMATCH", "R02 BLOCK SCHEMA_INVALID", "R03 BLOCK FORBIDDEN_FIELD",
                           "R04 BLOCK REQUEST_TYPE_NOT_ALLOWED (fora da allowlist, ou não o tipo fixado para a "
                           "hipótese proponível)", "R05 BLOCK HYPOTHESIS_CLOSED",
                           "R16 REQUIRE_HUMAN SEALED_SCOPE",
                           "R06 BLOCK SYMBOL_NOT_ALLOWED / COST_MODEL_MISMATCH / REFERENCE_NOT_ALLOWED / "
                           "PRIORITY_ABOVE_CAP", "R07 BLOCK REQUEST_ID_CONFLICT", "R08 DUPLICATE",
                           "R09 REQUIRE_HUMAN DOMAIN_RECONCILIATION_PENDING", "R10 REQUIRE_HUMAN CONTRADICTION_UNRESOLVED",
                           "R15 REQUIRE_HUMAN HYPOTHESIS_NOT_ADMITTED_BY_DOMAIN", "R11 REQUIRE_HUMAN NEW_HYPOTHESIS",
                           "R17 DUPLICATE EQUIVALENT_REQUEST",
                           "R12 ABSTAIN OPEN_TASK_PENDING / BUDGET_EXHAUSTED", "R13 COOLDOWN NEGATIVE_STREAK",
                           "R14 ALLOW"],
            "brasileirao_config": brasileirao_config,
            "framework_limits_found_before_freeze": [
                {"id": "holdout-require-human", "finding": "IB-F002",
                 "fact": "no ciclo 1 nenhuma regra R01–R14 lia season/events/data_cutoff (o holdout saía ALLOW, R14)",
                 "decision": "ciclo 2: resolvido pela R16 SEALED_SCOPE na release rc8 (decisão do dono); os vetores do "
                             "holdout esperam REQUIRE_HUMAN SEALED_SCOPE; nenhuma proposta de 2025+ é despachada"},
                {"id": "llm-placebo-seed",
                 "fact": "no ciclo 1 o caminho de LLM gravava parameters.placebo_seed (IS-F003); a rc8 inclui o cain#62 "
                         "(semente pelas variantes do contrato); o vetor n1/21-llm-shape (pedido com parameters) continua "
                         "SCHEMA_INVALID porque o request_schema do Brasileirão não tem parameters",
                 "decision": "as ≥ 5 propostas de LLM do soak passam pela mesma política e a decisão é a que ela der; "
                             "não são gate (C9)"},
            ],
        },
        "n_plus_1": {"processes": 3, "equality": "receipt byte a byte", "as_of": "2026-09-27T00:00:00Z",
                     "vectors": "FROZEN_VECTORS.json → n_plus_1",
                     "integrated_variant": "o mesmo N+1 roda no runtime integrado com resultados V2 reais do cripto e "
                                           "do stocks entregues ao spool do Brasileirão (recusados); os receipts têm de "
                                           "ser iguais aos do conjunto congelado",
                     "llm": "proibido no caminho do receipt (C9); LLM só no soak"},
        "isolation": {"crypto": "runtime integrado (cain com as três configurações + consumidores do cripto e do "
                                "Brasileirão no mesmo estado, dados reais de cada domínio)",
                      "stocks": "runtime integrado (idem, consumidor do stocks e painel público B3/CVM pelo pin do run)",
                      "h9_ids": ["crypto:H9", "stocks:H9", "brasileirao:H9"]},
        "failure_matrix": fsha(f"{M}/FAILURE_MATRIX.json"),
        "soak_profile": fsha(f"{M}/QUALIFICATION_PROFILE_INTEGRATION_BR_V1.json"),
        "frozen_vectors": fsha(f"{M}/FROZEN_VECTORS.json"),
        "protected_set_initial": {
            "rule": "C15.1: o conjunto só cresce; lista completa em PROTECTED_SET.json no fim de truth-map",
            "brasileirao_stage_a": [fsha("qualification/brasileirao/PROTECTED_SET.json"),
                                    fsha("qualification/brasileirao/FROZEN_VECTORS.json"),
                                    fsha("qualification/brasileirao/runtime_target.json"),
                                    fsha(contract_rel),
                                    fsha("qualification/brasileirao/QUALIFICATION_ATTESTATION.json")],
            "other_stage_a": [fsha("qualification/crypto/PROTECTED_SET.json"),
                              fsha("qualification/stocks/PROTECTED_SET.json")],
            "other_integrations_frozen": [fsha(f"qualification/integration-crypto/{n}") for n in
                                          ("FROZEN_PARAMETERS.json", "FROZEN_VECTORS.json", "FAILURE_MATRIX.json",
                                           "QUALIFICATION_PROFILE_INTEGRATION_CRYPTO_V1.json",
                                           "fixtures/v2/FIXTURES_MANIFEST.json")]
                                         + [fsha(f"qualification/integration-stocks/{n}") for n in
                                            ("FROZEN_PARAMETERS.json", "FROZEN_VECTORS.json", "FAILURE_MATRIX.json",
                                             "QUALIFICATION_PROFILE_INTEGRATION_STOCKS_V1.json")],
            "other_integrations_attestations": {
                "items": [fsha("qualification/integration-crypto/QUALIFICATION_ATTESTATION.json"),
                          fsha("qualification/integration-stocks/QUALIFICATION_ATTESTATION.json")],
                "rule": "reemissão pela C14 prevista em c14_other_integrations: os bytes atuais têm de continuar "
                        "disponíveis, iguais, em QUALIFICATION_ATTESTATION_superseded_<sha12>.json, apontados pelo "
                        "supersedes_sha256 da nova; qualquer outra mudança = FAIL",
            },
            "shared": [fsha("qualification/shared/ENVELOPE_V2_FREEZE.json"),
                       fsha("qualification/shared/STACK_BASELINE_V2.0.json"),
                       fsha("qualification/COMMON_QUALIFICATION_CORE.md"),
                       fsha("qualification/ATTESTATION_SCHEMA.json")],
            "mission": [fsha(f"{M}/FAILURE_MATRIX.json"),
                        fsha(f"{M}/QUALIFICATION_PROFILE_INTEGRATION_BR_V1.json"),
                        fsha(f"{M}/FROZEN_VECTORS.json")],
            "private_data": {"path": "~/predictors/data/d16/brasileirao/matches_source_copy.sqlite3", "sha256": DATA_SHA},
            "never_read": "nada de brasileirao-predictor depois de d80a4ed; holdout 2025 do domínio",
        },
        "gates_required": ["BLOCKERS_ZERO", "STACK_BASELINE_FROZEN", "LOCK_INTEGRITY", "CORE_IDENTITY",
                           "CLEANROOM_FINAL", "HOSTED_CI", "E2E", "IDEMPOTENCY", "RESTART_RECOVERY",
                           "FAILURE_INJECTION", "PROVENANCE", "AUTHORITY_SEPARATION", "FUTURE_CANARY",
                           "PROTECTED_ARTIFACTS_UNCHANGED", "SOAK", "WINDOWS_SMOKE", "SHARED_DEPENDENCY_CLEAR",
                           "EVIDENCE_CONSISTENCY", "SECRETS_CLEAN", "CAPITAL_FORBIDDEN", "ENVELOPE_V2_CONFORMANCE",
                           "CAIN_INGESTION", "CAIN_CONTAINMENT", "DECISION_POLICY", "N_PLUS_1_DETERMINISTIC",
                           "NEGATIVE_RESULT_NEUTRALITY", "CROSS_DOMAIN_ISOLATION", "DOMAIN_QUALIFIED_IDS",
                           "CONTRADICTION_PRESERVATION", "DOMAIN_CONTRACTS_PRESERVED"],
        "hosted_ci_rule": "prompt da sessão 10.3: só o run de evento push cujo SHA é exatamente o final_commit vale (C21)",
        "phases": ["freeze-parameters", "baseline", "truth-map", "cleanroom-baseline", "envelope-v2", "domain-adapter",
                   "cain-wiring-decision-policy", "publish-candidates", "cleanroom-final", "contract-revalidation", "e2e",
                   "n-plus-1", "isolation-ids-contradiction", "idempotency-failure", "windows-smoke", "hosted-ci",
                   "soak", "attestation"],
        "absolute": {"capital_permission": False, "training_started": False, "holdout_use": "nenhum",
                     "cain_operational_mode": "proibido", "betting_or_exchange_connection": "proibida"},
    }
    raw_doc = json.dumps(doc, indent=1, ensure_ascii=False).encode("utf-8") + b"\n"
    (MISSION / "FROZEN_PARAMETERS.json").write_bytes(raw_doc)
    print("FROZEN_PARAMETERS.json", sha(raw_doc))
    print(json.dumps({"closed": len(closed), "refuted": len(refuted), "loops": sorted(loops)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
