"""integration-stocks, ciclo 2 dos parâmetros congelados (C14: parâmetro congelado muda → a fase inteira, novo ciclo).

Parte do FROZEN_PARAMETERS.json do ciclo 1 (preservado byte a byte no arquivo de supersedes) e muda só o que o ciclo 2
muda, como o freeze_cycle2.py da integration-crypto:
  * decision_policy: versão 2 do cain (release única v0.4.13rc10, fb0e1dc) com a rule_order da docstring de
    src/cain/orchestration/policy.py daquele commit (sha256 conferido), mais a chave opcional proposal_overlays da rc11;
  * decision_policy.stocks_config: as cinco hipóteses só para o LLM (proponíveis, com overlay de controle negativo de
    semente própria) e o estado dos limites de framework achados antes do ciclo 1;
  * operator_env: as cinco hipóteses admitidas pelo operador;
  * base/repos: framework do ciclo 2 (cain fb0e1dc + proposal_overlays → rc11; transporte 0.1.0rc5 b11494a);
  * c14_cycle2: a rc11 muda a wheel do cain → C14 das três integrações; o que esta missão refaz;
  * hosted_ci_rule: a decisão do dono no IS-F004/IS-F005 (b);
  * frozen_vectors: o FROZEN_VECTORS.json do ciclo 2 (o do ciclo 1 preservado);
  * identity: sha256 atual de cada arquivo de identidade (os que mudaram desde o ciclo 1 ficam listados no bloco cycle);
  * cycle: número, supersedes (parâmetros e vetores), commit do cain, autorização do dono com as palavras.
Nada mais muda: perfil de soak (pisos), dados, matriz de falhas, N+1 (as_of), isolamento, gates, fases.

Uso: python freeze_cycle2.py <raiz do predictor-qualification> <clone do cain>
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT, CAIN = Path(sys.argv[1]), Path(sys.argv[2])
MISSION = ROOT / "qualification/integration-stocks"
CYCLE1 = MISSION / "FROZEN_PARAMETERS_cycle1_771b8a23e9b9.json"
VECTORS1 = MISSION / "FROZEN_VECTORS_cycle1_3ad4d197cb79.json"
CAIN_SHORT = "fb0e1dc"  # merge do cain#70, publicado como v0.4.13rc10
CAIN_TAG = "v0.4.13rc10"
POLICY_PATH = "src/cain/orchestration/policy.py"
LLM = tuple(f"stocks:QUAL-LLM-CTRL-{k:03d}" for k in range(1, 6))
RULE_ORDER = [
    "R01 BLOCK DOMAIN_MISMATCH: proposta, pedido ou evidência de outro domínio, ou ID sem domínio (C18)",
    "R02 BLOCK SCHEMA_INVALID: forma da proposta ou pedido fora do request_schema congelado do Stocks",
    "R03 BLOCK FORBIDDEN_FIELD: campo fora de cain-proposal/1 (handler, comando, módulo, caminho, URL, budget, "
    "prioridade final, capital …) ou client_ref que o envelope controla",
    "R04 BLOCK REQUEST_TYPE_NOT_ALLOWED: request_type fora da handler_allowlist do contrato, ou diferente do tipo que a "
    "configuração fixa para a hipótese proponível (proposable_request_types, cain#67; no Stocks as fixtures de "
    "proposta congeladas decidem: coleta nunca vai como backtest)",
    "R05 BLOCK HYPOTHESIS_CLOSED: hipótese encerrada do estado científico (stocks:H1..H22) ou família congelada",
    "R16 REQUIRE_HUMAN SEALED_SCOPE: pedido que tocaria um escopo lacrado da configuração (sealed_scopes); Stocks: "
    "nenhum lacre (lista vazia)",
    "R06 BLOCK SYMBOL_NOT_ALLOWED / COST_MODEL_MISMATCH / REFERENCE_NOT_ALLOWED / PRIORITY_ABOVE_CAP: custos comparados "
    "só quando a variante de parameters do request_schema declara fee_bps/slippage_bps (cain#62, IS-F002): o backtest "
    "declara, a coleta não",
    "R07 BLOCK REQUEST_ID_CONFLICT: request_id já emitido com outro conteúdo",
    "R08 DUPLICATE DUPLICATE_REQUEST: o mesmo conteúdo já emitido no domínio",
    "R09 REQUIRE_HUMAN DOMAIN_RECONCILIATION_PENDING: desfecho REQUIRES_HUMAN do domínio sem resolução",
    "R10 REQUIRE_HUMAN CONTRADICTION_UNRESOLVED: estados científicos em conflito para a hipótese (nunca por maioria)",
    "R15 REQUIRE_HUMAN HYPOTHESIS_NOT_ADMITTED_BY_DOMAIN: o domínio já recusou a hipótese com HYPOTHESIS_NOT_ADMITTED",
    "R11 REQUIRE_HUMAN NEW_HYPOTHESIS: hipótese fora da lista proponível",
    "R17 DUPLICATE EQUIVALENT_REQUEST: o mesmo experimento (o pedido sem request_id, hypothesis_id, research_id e "
    "client_ref) já rodou ou está aberto no domínio com outro ID (cain#68); tarefa recusada pelo domínio não conta",
    "R12 ABSTAIN OPEN_TASK_PENDING / BUDGET_EXHAUSTED",
    "R13 COOLDOWN NEGATIVE_STREAK: N resultados negativos seguidos da hipótese → K episódios sem task nova",
    "R14 ALLOW",
]
OWNER = [
    {"date": "2026-09-28", "by": "dono", "channel": "chat da sessão integration-stocks (pergunta com opções)",
     "words": "Aprovo o ciclo novo",
     "question": "Aprova o ciclo novo de parâmetros congelados da integration-stocks na cain v0.4.13rc10? Com o "
                 "transporte 0.1.0rc5 e a política nova (R15–R17, R04 por hipótese, custos pelo contrato), mudam as "
                 "decisões esperadas congeladas. Proponho: (1) 17-collection passa de BLOCK para ALLOW; (2) as 4 "
                 "fixtures de contradição viram experimentos distintos (hoje a R17 barra a 2ª por ser o mesmo); (3) "
                 "vetores do N+1 recalculados para a política nova; (4) as hipóteses REAL-001/002/003 passam a ser "
                 "experimentos distintos, senão a R17 barra o rodízio. Perfil de soak, dados, pisos e os demais "
                 "parâmetros ficam iguais. Eu gravo o FROZEN_PARAMETERS novo e te mostro antes de rodar qualquer fase."},
    {"date": "2026-09-28", "by": "dono", "channel": "chat da sessão integration-stocks (pergunta com opções)",
     "words": "Hipóteses para o LLM",
     "question": "Com a rc10, o soak do Stocks não chega ao piso da C10 de ≥ 5 propostas de LLM. Em todas as "
                 "tentativas, depois da semente, o CAIN não pergunta ao modelo (NO_ELIGIBLE_HYPOTHESIS), porque toda "
                 "hipótese disponível já rodou aquele mesmo experimento (R17). Isso está correto como comportamento, "
                 "mas deixa o piso inatingível. Como seguir?",
     "option_text": "No ciclo 2, 5 hipóteses de qualificação novas só para o LLM, cada uma um experimento distinto "
                    "(controle negativo com semente própria), admitidas pelo operador. Exige mudar a configuração do "
                    "stocks no cain (nova release rc11) e refazer a C14 das três integrações."},
]


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def fsha(rel: str) -> dict:
    return {"path": rel, "sha256": sha((ROOT / rel).read_bytes())}


def cain(*args: str) -> bytes:
    return subprocess.run(["git", "-C", str(CAIN), *args], capture_output=True, check=True).stdout


def main() -> int:
    raw1 = CYCLE1.read_bytes()
    frozen = json.loads(raw1)
    if frozen["decision_policy"]["version"] != 1 or "cycle" in frozen:
        raise SystemExit("esperava o ciclo 1 (política v1, sem bloco cycle)")
    commit = cain("rev-parse", f"{CAIN_TAG}^{{commit}}").decode().strip()
    if not commit.startswith(CAIN_SHORT):
        raise SystemExit(f"{CAIN_TAG} aponta para {commit}, não para {CAIN_SHORT}")
    policy_raw = cain("show", f"{commit}:{POLICY_PATH}")
    docstring = policy_raw.decode("utf-8").split('"""')[1]
    order_in_code = [m.group(1) for m in (re.match(r"  (R\d\d) ", line) for line in docstring.splitlines()) if m]
    if order_in_code != [rule.split()[0] for rule in RULE_ORDER]:
        raise SystemExit(f"rule_order difere da docstring de {POLICY_PATH} em {commit}: {order_in_code}")
    stocks_json = cain("show", f"{commit}:src/cain/orchestration/data/stocks.json")
    vectors = json.loads((MISSION / "FROZEN_VECTORS.json").read_bytes())
    llm = vectors["llm_hypotheses"]
    if tuple(llm) != LLM or vectors["cycle"]["number"] != 2:
        raise SystemExit("FROZEN_VECTORS.json não é o do ciclo 2 (rode build_vectors.py antes)")

    policy = frozen["decision_policy"]
    policy["version"] = 2
    policy["framework"] = (f"cain {CAIN_TAG} ({commit[:7]}): política v2, regras R01–R17 na ordem abaixo; mais a chave "
                           "opcional proposal_overlays da configuração (o molde de pedido do LLM aplica o overlay da "
                           "hipótese), publicada como v0.4.13rc11; runtime_targets.json do ciclo 2 fixa commit e wheel")
    policy["policy_module"] = {"cain_commit": commit, "path": POLICY_PATH, "sha256": sha(policy_raw),
                               "rule": "a rc11 tem de ter estes mesmos bytes (proposal_overlays não toca a política)"}
    policy["rule_order"] = RULE_ORDER
    config = policy["stocks_config"]
    config["proposable_hypotheses"] = sorted([*config["proposable_hypotheses"], *LLM])
    config["proposal_overlays"] = {h: llm[h]["overlay"] for h in LLM}
    config["llm_hypotheses"] = {
        "hypotheses": list(LLM),
        "fixtures": {h: llm[h]["fixture"] for h in LLM},
        "why": "com a R17, o molde de pedido do LLM de cada hipótese do rodízio repete um experimento já emitido: o "
               "CAIN não chega a perguntar ao modelo (NO_ELIGIBLE_HYPOTHESIS) e o piso da C10 (≥ 5 propostas de LLM "
               "no soak) fica inatingível; decisão do dono: cinco hipóteses de qualificação só para o LLM",
        "experiment": "o mesmo protocolo das hipóteses REAL (backtest 12-1 no painel real do run) com "
                      "parameters.negative_control SHUFFLED_LABELS de semente própria (9001–9005): um controle "
                      "negativo real do domínio, nunca uma hipótese científica; cada uma roda no máximo uma vez (a "
                      "segunda proposta da mesma hipótese é o mesmo experimento → R17)",
        "template": "cain rc11: sem task própria, o molde é a última task do mesmo tipo sem as chaves de overlay, com o "
                    "overlay da hipótese; com task própria, a própria task (→ R17, inelegível)",
        "not_overlaid": "fee_bps, slippage_bps e placebo_seed nunca vêm de overlay (config.py do cain)",
    }
    limits = config["framework_limits_found_before_freeze"]
    status = {
        "R06-custos-em-todo-pedido": "ciclo 2: corrigido no cain#62 (d8b8061, IS-F002), na release única rc10; "
                                     "n1/17-collection passa a ALLOW",
        "llm-placebo-seed": "ciclo 2: corrigido no cain#62 (d8b8061, IS-F003), na release única rc10: a semente do "
                            "LLM só entra onde a variante do contrato a declara",
    }
    for item in limits:
        item["cycle2_status"] = status[item["id"]]
    config["framework_limits_found_before_cycle2"] = [
        {"id": "R17-llm-floor",
         "fact": "no cain rc10 (R17 + molde por hipótese, cain#67/#68), depois do primeiro ciclo nenhuma hipótese "
                 "proponível tem molde que não repita um experimento emitido: o LLM não é chamado e o piso "
                 "llm_proposals da C10 não é atingível (diagnóstico local na rc10; não é gate)",
         "decision": "dono, 2026-09-28: \"Hipóteses para o LLM\" (proposal_overlays no cain → rc11; C14 das três "
                     "integrações)"},
    ]

    env = frozen["operator_env"]
    env["hypotheses"] = [*env["hypotheses"], *LLM]
    env["llm_hypotheses"] = {"hypotheses": list(LLM), "hypothesis_family": env["hypothesis_family"],
                             "purpose": "LLM-only qualification probe: negative control of the same protocol on real "
                                        "B3/CVM data; not a scientific hypothesis",
                             "admitted_by": "scripts/operator_env.py (fronteira do operador do Stocks)"}
    env["request_parameters_cycle2"] = ("parameters.negative_control {kind SHUFFLED_LABELS, seed} nos pedidos que "
                                        "precisam ser outro experimento (FROZEN_VECTORS.json → cycle.changes); os "
                                        "demais parâmetros iguais")

    frozen["base"]["framework_cycle2"] = {
        "cain": {"release": CAIN_TAG, "commit": commit,
                 "stocks_json_sha256": sha(stocks_json),
                 "wheel_sha256": "752de98d385528b0bd90c950d117c46af0522125a2274ea9a7064461786b85e5",
                 "next": "v0.4.13rc11 = este commit + cain#72 (proposal_overlays: config.py, llm.py, builder, "
                         "testes, docs; e a correção do llm.py para pedido sem parameters, relatada pela "
                         "integration-brasileirao) + cain#71 (brasileirao.json da integration-brasileirao) + o PR da "
                         "integration-crypto (result_metrics opcional, findings check; crypto.json do ciclo dela) + "
                         "stocks.json regenerado por tools/build_domain_config.py a partir do merge deste ciclo e "
                         "a versão; policy.py igual (policy_module); cada integração confere a própria configuração"},
        "predictor-research-transport": {"release": "predictor-research-transport-v0.1.0rc5",
                                         "commit": "b11494ae211e79e2e5faaa4b874470f5b6ce15ec",
                                         "wheel_sha256": "408d73c2b991eb009806702121ed187f273aa6521979ed89bbe9491e58cff79f"},
        "rule": "runtime_targets.json do ciclo 2 fixa commits e sha256 das wheels publicadas; nada instalado de branch",
    }
    frozen["repos"]["cain"] = {
        "role": "ciclo 2: a chave opcional proposal_overlays (src/cain/orchestration/config.py e llm.py, "
                "tools/build_domain_config.py, testes, docs/ORCHESTRATION_V2.md) e a correção do llm.py para pedido "
                "sem parameters (cain#72); stocks.json regenerado, versão e lock; política (policy.py) sem mudança; "
                "crypto.json e brasileirao.json só pelos PRs das outras integrações",
        "base": commit}
    frozen["repos"]["ecosystem-predictor"] = {
        "role": "não muda no ciclo 2 (o transporte 0.1.0rc5 da release única já tem a entrada stocks)",
        "base": "b11494ae211e79e2e5faaa4b874470f5b6ce15ec"}
    frozen["c14_cycle2"] = {
        "why": "a rc11 muda a wheel do cain: pela C14 ('cain, ecosystem-predictor'), as fases que exercitam o cain são "
               "refeitas nas três integrações; integration-crypto e integration-brasileirao nas sessões delas "
               "(avisadas com a tag, o SHA e o sha256 da wheel)",
        "this_mission_phases": ["publish-candidates", "cleanroom-final", "contract-revalidation", "e2e", "n-plus-1",
                                "isolation-ids-contradiction", "idempotency-failure", "windows-smoke", "hosted-ci",
                                "soak", "attestation"],
        "stocks_predictor": "não muda: final_commit 6f857b2 (0.3.0rc3) e o run workflow_dispatch aceito pelo dono "
                            "(IS-F004/IS-F005 (b))",
    }
    frozen["hosted_ci_rule"]["owner_decision_is_f004_f005"] = (
        "dono, 2026-09-28: \"aceita o run workflow_dispatch (b) e reemite\": só para o stocks-predictor, o run "
        "workflow_dispatch do CI Pipeline no SHA exato do final_commit vale como o run de C21 / prompt 9.3; cain e "
        "ecosystem-predictor continuam só com run de push no SHA exato")
    frozen["frozen_vectors"] = fsha("qualification/integration-stocks/FROZEN_VECTORS.json")
    frozen["shown_to_owner"] = ("ciclo 2: mostrado ao dono antes de rodar qualquer fase, no PR do ciclo 2 no "
                                "predictor-qualification e no relatório da sessão. Aprovar = merge. O ciclo 1 fica byte "
                                "a byte no arquivo de supersedes.")
    identity_changed = []
    for key, value in frozen["identity"].items():
        if isinstance(value, dict) and "path" in value:
            now = fsha(value["path"]) | {k: v for k, v in value.items() if k not in ("path", "sha256")}
            if now["sha256"] != value["sha256"]:
                identity_changed.append({"path": value["path"], "cycle1": value["sha256"], "cycle2": now["sha256"]})
            frozen["identity"][key] = now
    decisions = json.loads((ROOT / "qualification/DECISIONS.json").read_bytes())["decisions"]
    frozen["decisions_cited"]["approved_on_main"] = [d["decision_id"] for d in decisions if d["status"] == "APPROVED"]
    frozen["decisions_cited"]["D-25"] = "integration-brasileirao (base rc3, estado do Brasileirão no CAIN, " \
                                        "WINDOWS_SMOKE no PC 2); nada nesta missão"
    frozen["decisions_cited"]["owner_2026_09_28_cycle2"] = OWNER
    frozen["cycle"] = {
        "number": 2,
        "supersedes": {"file": CYCLE1.name, "sha256": sha(raw1)},
        "vectors_supersede": {"file": VECTORS1.name, "sha256": sha(VECTORS1.read_bytes())},
        "why": "C14: a DecisionPolicy (v1 → v2) e a configuração do Stocks mudaram (parâmetro congelado); a fase "
               "inteira, novo ciclo",
        "authorized_by": OWNER,
        "changes": [
            "decision_policy v2 (rule_order R01–R17, policy_module), stocks_config com as hipóteses só para o LLM e "
            "proposal_overlays",
            "operator_env: as cinco hipóteses do LLM admitidas pelo operador",
            "base.framework_cycle2, repos.cain, repos.ecosystem-predictor, c14_cycle2",
            "hosted_ci_rule com a decisão do dono no IS-F004/IS-F005",
            *vectors["cycle"]["changes"],
        ],
        "identity_changed_since_cycle1": identity_changed,
        "unchanged": "perfil de soak e pisos, dados, matriz de falhas, n_plus_1 (as_of), isolation, r8_d24, "
                     "protected_set_initial, gates_required, phases, absolute e as demais chaves do ciclo 1",
    }
    raw2 = (json.dumps(frozen, indent=1, ensure_ascii=False) + "\n").encode("utf-8")
    (MISSION / "FROZEN_PARAMETERS.json").write_bytes(raw2)
    print(json.dumps({"sha256": sha(raw2), "supersedes": sha(raw1), "cain": commit, "rules": len(RULE_ORDER),
                      "proposable": len(config["proposable_hypotheses"]), "identity_changed": identity_changed},
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
