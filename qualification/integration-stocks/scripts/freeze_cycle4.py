"""integration-stocks, ciclo 4 dos parâmetros congelados (C14: parâmetro congelado muda → a fase inteira, novo ciclo).

Parte do FROZEN_PARAMETERS.json do ciclo 3 (preservado byte a byte no arquivo de supersedes) e muda só o que o ciclo 4
muda, pelas decisões do dono de 2026-09-28 ("arruma os não resolvidos"):
  * D-26 ("Somar as famílias do main"): stocks_config.frozen_families = base ∪ frozen_families do
    research/scientific_state.json do stocks-predictor em 4c82885 (blob e sha256 conferidos), com
    stocks_config.additional_frozen_families para o builder do cain (cain#78); protected_set_initial.never_read diz a
    exceção;
  * "Só o transporte": predictor-research-transport 0.1.0rc6 (um consumidor por domínio; ecosystem-predictor#36,
    publicado e conferido) no framework, em base.framework_cycle4 e em repos.ecosystem-predictor;
  * "Calibrar embedding": a medição do cain#78 recomenda manter o embedding só para revisão; a findings-policy continua
    na v2, e a decisão do número fica com o dono (nada muda na política aqui);
  * decision_policy.framework, policy_module.checked_again_cycle4, base.framework_cycle4, repos.cain, c14_cycle4,
    identity (sha256 atuais), decisões citadas com as palavras, cycle (número 4, supersedes, autorização).
Os vetores (FROZEN_VECTORS.json do ciclo 3) não mudam. A agenda de pesquisa ("todas") não entra neste ciclo: cada
hipótese pede fator novo no código do stocks e reabertura da Etapa A (C24.4).

Uso: python freeze_cycle4.py <raiz do predictor-qualification> <clone do cain> <merge do cain#78 no main> <clone do stocks>
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT, CAIN, CAIN_PR, STOCKS = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3], Path(sys.argv[4])
MISSION = ROOT / "qualification/integration-stocks"
LATER = {"commit": "4c82885eddab233f2b57442046875fdc2c8f0932", "path": "research/scientific_state.json",
         "git_blob": "3fc34e5e24778cc2501a78d5832c369486e06155",
         "sha256": "1f7eeff798a1ac378393e9f9225f5708004d5cd54c6d912d1547c4bc390c6ec7"}
ADDED = ["quality_net_margin", "quality_roe_leverage_double_filter"]
TRANSPORT = {"release": "predictor-research-transport-v0.1.0rc6", "commit": "bac1f7b7b3ae687e4c75ff3849ccb1f458dca097",
             "wheel_sha256": "6c7e83c4d93d4802b7cdfbc569b0828cde34ccd2241b5a274003ff21c9daec33",
             "pr": "leonardosovienski/ecosystem-predictor#36 (dae4e57)"}
CHANNEL = "chat da sessão integration-stocks (pergunta com opções)"
OWNER = [
    {"date": "2026-09-28", "by": "dono", "channel": CHANNEL, "words": "Somar as famílias do main (Recomendado)",
     "question": "Famílias do stocks que o CAIN não conhece: a D-24 manda o estado do CAIN vir só da base 61fc017, e o "
                 "main do stocks tem 2 nomes de família a mais. Mudo?",
     "option_text": "Nova decisão sobre a D-24, só para a lista de famílias congeladas: o CAIN bloqueia também as "
                    "famílias do scientific_state.json do main do stocks (só acrescenta, nunca tira). O resto do estado "
                    "continua da base. Entra no stocks.json da rc13, com ciclo 4 dos congelados.",
     "recorded_as": "D-26 em qualification/DECISIONS.json"},
    {"date": "2026-09-28", "by": "dono", "channel": CHANNEL, "words": "Só o transporte (Recomendado)",
     "question": "Na disputa, a trava por domínio no consumidor do transporte resolve os dois sintomas: aviso falso e "
                 "RECONCILIATION_REQUIRED falso. Ela também resolve os do cripto, sem tocar em código de domínio e sem "
                 "reabrir a Etapa A. Ainda quer também a correção dentro do stocks (gravação atômica das referências), "
                 "como defesa extra?",
     "option_text": "Trava exclusiva por domínio no predictor-research-transport (release 0.1.0rc6). O consumidor que "
                    "não pega a trava sai sem publicar nada. A regra \"um consumidor por domínio\" vira código. Testo "
                    "com a disputa de 20 repetições no WSL, e o cripto testa no Windows. Nenhum domínio muda.",
     "before": "na mesma rodada, o dono tinha escolhido \"Corrigir stocks + transporte (Recomendado)\"; a pergunta foi "
               "refeita com a trava por domínio já medida, e ele escolheu esta"},
    {"date": "2026-09-28", "by": "dono", "channel": CHANNEL, "words": "Calibrar embedding (Recomendado)",
     "question": "Paráfrase (ideia encerrada escrita sem o nome passa como \"nova\"): como resolver?",
     "option_text": "Enriqueço os enunciados das hipóteses encerradas com a descrição delas e meço o embedding local num "
                    "conjunto rotulado (paráfrases × ideias novas). Te mostro a separação e um limiar; você aprova o "
                    "número com o merge da política v3, e aí o embedding passa a decidir.",
     "result": "cain#78, docs/evidence/2026-09-28-findings-calibration: pela regra fixada antes de medir, "
               "KEEP_REVIEW_ONLY (validação 11/33 encerradas pegas em t* = 0,650, 0/15 novas bloqueadas); nenhuma "
               "findings-policy v3 proposta; o número fica para o dono decidir"},
]


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def fsha(rel: str) -> dict:
    return {"path": rel, "sha256": sha((ROOT / rel).read_bytes())}


def git(repo: Path, *args: str) -> bytes:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, check=True).stdout


def main() -> int:
    cycle3_files = sorted(MISSION.glob("FROZEN_PARAMETERS_cycle3_*.json"))
    if len(cycle3_files) != 1:
        raise SystemExit("esperava um FROZEN_PARAMETERS_cycle3_<sha12>.json (git mv do ciclo 3 antes)")
    cycle3 = cycle3_files[0]
    raw3 = cycle3.read_bytes()
    if cycle3.name != f"FROZEN_PARAMETERS_cycle3_{sha(raw3)[:12]}.json":
        raise SystemExit("nome do arquivo do ciclo 3 não bate com o sha256")
    frozen = json.loads(raw3)
    if frozen["cycle"]["number"] != 3:
        raise SystemExit("esperava o ciclo 3")
    vectors = json.loads((MISSION / "FROZEN_VECTORS.json").read_bytes())
    if vectors["cycle"]["number"] != 3 or frozen["frozen_vectors"]["sha256"] != fsha(
            "qualification/integration-stocks/FROZEN_VECTORS.json")["sha256"]:
        raise SystemExit("FROZEN_VECTORS.json não é o do ciclo 3")
    policy = frozen["decision_policy"]
    commit = git(CAIN, "rev-parse", f"{CAIN_PR}^{{commit}}").decode().strip()
    policy_now = sha(git(CAIN, "show", f"{commit}:{policy['policy_module']['path']}"))
    if policy_now != policy["policy_module"]["sha256"]:
        raise SystemExit(f"policy.py em {commit} difere do congelado: {policy_now}")
    state_raw = git(STOCKS, "show", f"{LATER['commit']}:{LATER['path']}")
    blob = git(STOCKS, "rev-parse", f"{LATER['commit']}:{LATER['path']}").decode().strip()
    if (blob, sha(state_raw)) != (LATER["git_blob"], LATER["sha256"]):
        raise SystemExit("blob ou sha256 do scientific_state.json do main do stocks diverge")
    config = policy["stocks_config"]
    base_families = list(config["frozen_families"])
    later = json.loads(state_raw)["frozen_families"]
    added = sorted(set(later) - set(base_families))
    if added != ADDED:
        raise SystemExit(f"famílias acrescentadas divergem: {added}")
    config["frozen_families"] = sorted(set(base_families) | set(later))
    config["additional_frozen_families"] = {"decision": "D-26", "repository": "leonardosovienski/stocks-predictor",
                                            **LATER, "key": "frozen_families", "added": added}
    config["frozen_families_cycle4"] = {
        "base": base_families,
        "rule": "D-26: famílias da base (trials_v2.json/trials.json em 61fc017, closed_hypotheses_families) somadas "
                "às de frozen_families do scientific_state.json fixado; nenhuma sai; do arquivo só entra essa lista",
    }
    frozen["protected_set_initial"]["never_read"] = (
        frozen["protected_set_initial"]["never_read"] + "; exceção da D-26 (ciclo 4): de research/scientific_state.json "
        f"em {LATER['commit']} só a lista frozen_families, com blob e sha256 fixados")
    policy["framework"] = (
        "cain v0.4.13rc13: política v2, regras R01–R17 na ordem abaixo, com os mesmos bytes de policy.py do ciclo 2 "
        "(policy_module); rc12 + cain#77 (molde do LLM sem task recusada, allowed_requests e refusal_mismatches no LLM, "
        "linter de claims, findings-policy v2) + cain#78 (famílias do main pela D-26 no builder, ingest-state "
        "--describe e a calibração que manteve o embedding só para revisão, transporte 0.1.0rc6 no lock) + stocks.json "
        "regenerado do merge deste ciclo + versão; predictor-research-transport 0.1.0rc6 (um consumidor por domínio); "
        "runtime_targets.json fixa commits e wheels")
    policy["policy_module"]["checked_again_cycle4"] = {"cain_commit": commit, "sha256": policy_now}
    rc12 = git(CAIN, "rev-parse", "v0.4.13rc12^{commit}").decode().strip()
    pr77 = frozen["base"]["framework_cycle3"]["cain"]["framework_pr"]
    frozen["base"]["framework_cycle4"] = {
        "cain": {"release_base": "v0.4.13rc12", "commit": rc12,
                 "wheel_sha256": frozen["base"]["framework_cycle3"]["cain"]["wheel_sha256"],
                 "framework_prs": [pr77, {"pr": "leonardosovienski/cain#78", "commit": commit,
                                          "note": "merge do cain#78 no main (mergeado pelo dono antes deste ciclo); "
                                                  "árvore igual à do head da PR, 201a1bd"}],
                 "next": "v0.4.13rc13 = main do cain com cain#77 e cain#78 + stocks.json regenerado por "
                         "tools/build_domain_config.py a partir do merge deste ciclo (17 famílias) + versão; "
                         "crypto.json e brasileirao.json iguais byte a byte; policy.py igual (policy_module)"},
        "predictor-research-transport": TRANSPORT,
        "rule": "runtime_targets.json do ciclo 4 fixa commits e sha256 das wheels publicadas; nada instalado de branch",
    }
    frozen["repos"]["cain"] = {
        "role": "ciclo 4: cain#77 e cain#78 (tools/build_domain_config.py, findings/ingest.py e cli.py, "
                "tools/calibrate_findings_embedding.py, evidência da calibração, pyproject e uv.lock com o transporte "
                "rc6, testes, docs) e o stocks.json regenerado, versão e lock; policy.py e as outras configurações "
                "sem mudança",
        "base": rc12}
    frozen["repos"]["ecosystem-predictor"] = {
        "role": "ciclo 4: predictor-research-transport 0.1.0rc6 (ecosystem-predictor#36: trava exclusiva por domínio "
                "no consumidor; protocolo e allowlist iguais aos da rc5)",
        "base": TRANSPORT["commit"]}
    frozen["c14_cycle4"] = {
        "why": "a rc13 muda a wheel do cain e o transporte passa à 0.1.0rc6: pela C14, as fases que exercitam o cain e o "
               "transporte são refeitas nas três integrações; integration-crypto e integration-brasileirao nas sessões "
               "delas",
        "this_mission_phases": frozen["c14_cycle3"]["this_mission_phases"],
        "stocks_predictor": frozen["c14_cycle3"]["stocks_predictor"],
        "is_f009": "a disputa de consumidores (race.py, 20 repetições) é refeita nas wheels publicadas; com 0 envelopes "
                   "falsos, IS-F009 passa a FIXED na reemissão (a decisão \"Registrar + regra\" virou código)",
        "not_in_cycle4": "a agenda de pesquisa do stocks escolhida pelo dono (\"todas\": H18 E/P + H19 B/M, insiders "
                         "CVM VLMO, aluguel de ações B3, dividend yield B3) pede fator novo no código do stocks, "
                         "ingestão de dado novo e reabertura da Etapa A (C24.4); fica para uma missão própria",
    }
    frozen["shown_to_owner"] = ("ciclo 4: mostrado ao dono antes de rodar qualquer fase, no PR do ciclo 4 no "
                                "predictor-qualification. Aprovar = merge. O ciclo 3 fica byte a byte no arquivo de "
                                "supersedes (que aponta para o ciclo 2).")
    changed = []
    for key, value in frozen["identity"].items():
        if isinstance(value, dict) and "path" in value:
            now = fsha(value["path"]) | {k: v for k, v in value.items() if k not in ("path", "sha256")}
            if now["sha256"] != value["sha256"]:
                changed.append({"path": value["path"], "cycle3": value["sha256"], "cycle4": now["sha256"]})
            frozen["identity"][key] = now
    decisions = json.loads((ROOT / "qualification/DECISIONS.json").read_bytes())["decisions"]
    d26 = [d for d in decisions if d["decision_id"] == "D-26"]
    if not d26 or d26[0]["status"] != "APPROVED":
        raise SystemExit("D-26 não está no DECISIONS.json (rode owner_decision_d26.py antes)")
    frozen["decisions_cited"]["approved_on_main"] = [d["decision_id"] for d in decisions if d["status"] == "APPROVED"]
    frozen["decisions_cited"]["D-26"] = ("famílias congeladas do stocks = base ∪ frozen_families do "
                                         "scientific_state.json do main fixado (4c82885); só acrescenta; o resto da "
                                         "D-24 continua")
    frozen["decisions_cited"]["owner_2026_09_28_cycle4"] = OWNER
    frozen["cycle"] = {
        "number": 4,
        "supersedes": {"file": cycle3.name, "sha256": sha(raw3)},
        "vectors": "FROZEN_VECTORS.json do ciclo 3, sem mudança",
        "why": "C14: a configuração do Stocks muda (17 famílias congeladas, D-26), o cain passa à rc13 com o cain#78 e "
               "o transporte à 0.1.0rc6; a fase inteira, novo ciclo",
        "authorized_by": OWNER,
        "changes": ["stocks_config.frozen_families com as 2 famílias do main (D-26) e additional_frozen_families",
                    "protected_set_initial.never_read com a exceção da D-26",
                    "decision_policy.framework, base.framework_cycle4, repos.cain, repos.ecosystem-predictor e "
                    "c14_cycle4 na rc13 com o cain#78 e o transporte 0.1.0rc6",
                    "D-26 no qualification/DECISIONS.json"],
        "identity_changed_since_cycle3": changed,
        "unchanged": "política (policy.py e rule_order), findings-policy v2, hipóteses encerradas e proponíveis, "
                     "overlays e 8 hipóteses só para o LLM, operador, perfil de soak e pisos, dados, matriz de falhas, "
                     "N+1, isolamento, vetores, r8_d24, gates_required, phases, absolute e as demais chaves do ciclo 3",
        "cycle3": frozen["cycle"],
    }
    raw4 = (json.dumps(frozen, indent=1, ensure_ascii=False) + "\n").encode("utf-8")
    (MISSION / "FROZEN_PARAMETERS.json").write_bytes(raw4)
    print(json.dumps({"sha256": sha(raw4), "supersedes": sha(raw3), "cain_pr_commit": commit, "rc12": rc12,
                      "frozen_families": len(config["frozen_families"]), "added": added,
                      "identity_changed": changed}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
