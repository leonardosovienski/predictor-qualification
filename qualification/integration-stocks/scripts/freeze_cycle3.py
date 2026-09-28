"""integration-stocks, ciclo 3 dos parâmetros congelados (C14: parâmetro congelado muda → a fase inteira, novo ciclo).

Parte do FROZEN_PARAMETERS.json do ciclo 2 (preservado byte a byte no arquivo de supersedes) e muda só o que o
ciclo 3 muda, pela decisão do dono "cain rc13 + ciclo 3 (Recomendado)":
  * stocks_config: 8 hipóteses só para o LLM (as 5 do ciclo 2 + QUAL-LLM-CTRL-006..008, sementes 9006–9008), com
    proposal_overlays e llm_hypotheses do FROZEN_VECTORS.json do ciclo 3 (folga no piso llm_proposals do soak);
  * operator_env: as 8 admitidas pelo operador;
  * decision_policy.framework e base.framework_cycle3: cain 0.4.13rc13 = rc12 (302a5c8) + cain#77 (correções da
    rodada de utilidade: molde sem task recusada, allowed_requests e refusal_mismatches no LLM, linter, findings v2)
    + stocks.json regenerado do merge deste ciclo + versão. A política (policy.py) continua com os bytes do ciclo 2
    (policy_module, conferido no commit do cain informado);
  * c14_cycle3, repos.cain, frozen_vectors, identity (sha256 atuais), decisões do dono citadas com as palavras;
  * cycle: número 3, supersedes (parâmetros e vetores do ciclo 2), autorização.
Nada mais muda: perfil de soak e pisos, dados, matriz de falhas, N+1, isolamento, gates, fases.

Uso: python freeze_cycle3.py <raiz do predictor-qualification> <clone do cain> <commit do cain com o cain#77>
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT, CAIN, CAIN_PR = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
MISSION = ROOT / "qualification/integration-stocks"
CYCLE2 = MISSION / "FROZEN_PARAMETERS_cycle2_11ad4cb7f255.json"
VECTORS2 = MISSION / "FROZEN_VECTORS_cycle2_efba834f780f.json"
NEW = tuple(f"stocks:QUAL-LLM-CTRL-{k:03d}" for k in range(6, 9))
OWNER = [
    {"date": "2026-09-28", "by": "dono", "channel": "chat da sessão integration-stocks (pergunta com opções)",
     "words": "cain rc13 + ciclo 3 (Recomendado)",
     "question": "Até onde eu vou para \"arrumar os 5\"?",
     "option_text": "No cain: molde que pula task recusada; contexto do LLM dizendo o que cada hipótese pede, com a "
                    "checagem pegando \"recusada\" falsa; linter aceitando % e fração e nomes como \"12-1\"; paráfrase "
                    "casando nome técnico e família, com candidatos por embedding só para revisão. No stocks: mais 3 "
                    "hipóteses só para o LLM, para dar folga ao piso do soak. Ciclo 3 dos congelados citando a rc13, "
                    "IS-F009 no FINDINGS e C14 nas três integrações (as outras sessões refazem as delas). Família "
                    "(D-24) e disputa no código do stocks ficam como estão."},
    {"date": "2026-09-28", "by": "dono", "channel": "chat da sessão integration-stocks (pergunta com opções)",
     "words": "Registrar + regra (Recomendado)",
     "question": "Na disputa (dois consumidores do stocks ao mesmo tempo sobre a mesma task, 20 repetições), não houve "
                 "efeito duplicado nem perda. Mas o consumidor perdedor sempre publica um aviso falso, e em 4 casos é "
                 "um RECONCILIATION_REQUIRED que trava o stocks no CAIN até alguém intervir. A causa é o stocks gravar "
                 "as referências antes da trava do Ops. No cripto você decidiu \"Registrar + regra\" (um consumidor por "
                 "domínio por vez). A attestation do stocks (9979d19b, QUALIFIED) já está no main. Como fica no stocks?"},
]


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def fsha(rel: str) -> dict:
    return {"path": rel, "sha256": sha((ROOT / rel).read_bytes())}


def cain(*args: str) -> bytes:
    return subprocess.run(["git", "-C", str(CAIN), *args], capture_output=True, check=True).stdout


def main() -> int:
    raw2 = CYCLE2.read_bytes()
    frozen = json.loads(raw2)
    if frozen["cycle"]["number"] != 2:
        raise SystemExit("esperava o ciclo 2")
    vectors = json.loads((MISSION / "FROZEN_VECTORS.json").read_bytes())
    if vectors["cycle"]["number"] != 3 or len(vectors["llm_hypotheses"]) != 8:
        raise SystemExit("FROZEN_VECTORS.json não é o do ciclo 3 (rode build_vectors.py antes)")
    policy = frozen["decision_policy"]
    commit = cain("rev-parse", f"{CAIN_PR}^{{commit}}").decode().strip()
    policy_now = sha(cain("show", f"{commit}:{policy['policy_module']['path']}"))
    if policy_now != policy["policy_module"]["sha256"]:
        raise SystemExit(f"policy.py em {commit} difere do congelado: {policy_now}")
    rc12 = cain("rev-parse", "v0.4.13rc12^{commit}").decode().strip()
    llm = vectors["llm_hypotheses"]
    config = policy["stocks_config"]
    config["proposable_hypotheses"] = sorted(set(config["proposable_hypotheses"]) | set(llm))
    config["proposal_overlays"] = {h: llm[h]["overlay"] for h in sorted(llm)}
    config["llm_hypotheses"]["hypotheses"] = sorted(llm)
    config["llm_hypotheses"]["fixtures"] = {h: llm[h]["fixture"] for h in sorted(llm)}
    config["llm_hypotheses"]["experiment"] = config["llm_hypotheses"]["experiment"].replace("9001–9005", "9001–9008")
    config["llm_hypotheses"]["cycle3"] = ("3 hipóteses a mais (QUAL-LLM-CTRL-006..008, sementes 9006–9008): no ciclo 2 "
                                          "o piso llm_proposals ≥ 5 do soak passou com exatamente 5, sem folga para "
                                          "falha do modelo")
    policy["framework"] = ("cain v0.4.13rc13: política v2, regras R01–R17 na ordem abaixo, com os mesmos bytes de "
                           "policy.py do ciclo 2 (policy_module); rc12 + cain#77 (molde do LLM sem task recusada, "
                           "allowed_requests e refusal_mismatches no LLM, linter de claims, findings-policy v2) + "
                           "stocks.json regenerado do merge deste ciclo + versão; runtime_targets.json fixa commit e wheel")
    policy["policy_module"]["checked_again_cycle3"] = {"cain_commit": commit, "sha256": policy_now}
    env = frozen["operator_env"]
    env["hypotheses"] = [h for h in env["hypotheses"] if h not in llm] + sorted(llm)
    env["llm_hypotheses"]["hypotheses"] = sorted(llm)
    frozen["base"]["framework_cycle3"] = {
        "cain": {"release_base": "v0.4.13rc12", "commit": rc12,
                 "wheel_sha256": "988a0fb9b5e9b00be95cbf48dbe8fdda2eec53dff86e384192a619888ef49394",
                 "framework_pr": {"pr": "leonardosovienski/cain#77", "commit": commit},
                 "next": "v0.4.13rc13 = rc12 + cain#77 + stocks.json regenerado por tools/build_domain_config.py a "
                         "partir do merge deste ciclo + versão; crypto.json e brasileirao.json iguais byte a byte; "
                         "policy.py igual (policy_module)"},
        "predictor-research-transport": frozen["base"]["framework_cycle2"]["predictor-research-transport"],
        "rule": "runtime_targets.json do ciclo 3 fixa commits e sha256 das wheels publicadas; nada instalado de branch",
    }
    frozen["repos"]["cain"] = {
        "role": "ciclo 3: cain#77 (llm.py, claims/lint.py, findings/archive.py e cli.py, findings-policy-v2.json, "
                "testes, docs) e o stocks.json regenerado, versão e lock; policy.py e as outras configurações sem mudança",
        "base": rc12}
    frozen["c14_cycle3"] = {
        "why": "a rc13 muda a wheel do cain: pela C14, as fases que exercitam o cain são refeitas nas três integrações; "
               "integration-crypto e integration-brasileirao nas sessões delas",
        "this_mission_phases": frozen["c14_cycle2"]["this_mission_phases"],
        "stocks_predictor": frozen["c14_cycle2"]["stocks_predictor"],
    }
    frozen["frozen_vectors"] = fsha("qualification/integration-stocks/FROZEN_VECTORS.json")
    frozen["shown_to_owner"] = ("ciclo 3: mostrado ao dono antes de rodar qualquer fase, no PR do ciclo 3 no "
                                "predictor-qualification. Aprovar = merge. O ciclo 2 fica byte a byte no arquivo de "
                                "supersedes (que aponta para o ciclo 1).")
    changed = []
    for key, value in frozen["identity"].items():
        if isinstance(value, dict) and "path" in value:
            now = fsha(value["path"]) | {k: v for k, v in value.items() if k not in ("path", "sha256")}
            if now["sha256"] != value["sha256"]:
                changed.append({"path": value["path"], "cycle2": value["sha256"], "cycle3": now["sha256"]})
            frozen["identity"][key] = now
    decisions = json.loads((ROOT / "qualification/DECISIONS.json").read_bytes())["decisions"]
    frozen["decisions_cited"]["approved_on_main"] = [d["decision_id"] for d in decisions if d["status"] == "APPROVED"]
    frozen["decisions_cited"]["owner_2026_09_28_cycle3"] = OWNER
    frozen["cycle"] = {
        "number": 3,
        "supersedes": {"file": CYCLE2.name, "sha256": sha(raw2)},
        "vectors_supersede": {"file": VECTORS2.name, "sha256": sha(VECTORS2.read_bytes())},
        "why": "C14: a configuração do Stocks muda (8 hipóteses só para o LLM) e o cain passa à rc13; a fase inteira, "
               "novo ciclo",
        "authorized_by": OWNER,
        "changes": ["stocks_config e operator_env com 8 hipóteses só para o LLM (sementes 9001–9008)",
                    "decision_policy.framework, base.framework_cycle3, repos.cain e c14_cycle3 na rc13",
                    "IS-F009 (disputa de consumidores, P2) no FINDINGS.json com a decisão do dono",
                    *vectors["cycle"]["changes"]],
        "identity_changed_since_cycle2": changed,
        "unchanged": "política (policy.py e rule_order), perfil de soak e pisos, dados, matriz de falhas, N+1, "
                     "isolamento, r8_d24, gates_required, phases, absolute e as demais chaves do ciclo 2",
        "cycle2": frozen["cycle"],
    }
    raw3 = (json.dumps(frozen, indent=1, ensure_ascii=False) + "\n").encode("utf-8")
    (MISSION / "FROZEN_PARAMETERS.json").write_bytes(raw3)
    print(json.dumps({"sha256": sha(raw3), "supersedes": sha(raw2), "cain_pr_commit": commit, "rc12": rc12,
                      "proposable": len(config["proposable_hypotheses"]), "identity_changed": changed},
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
