"""integration-crypto, ciclo 2 dos parâmetros congelados (C14: parâmetro congelado muda → a fase inteira, novo ciclo).

Parte do FROZEN_PARAMETERS.json do ciclo 1 e muda só o que a política v2 do cain mudou, lendo a configuração do
cripto no commit do cain que vai para a release única:
  * decision_policy.version 1 → 2; rule_order na ordem do cain v0.4.13rc10: R04 por hipótese (#67), R16
    (SEALED_SCOPE, depois da R05), R15 (HYPOTHESIS_NOT_ADMITTED_BY_DOMAIN, depois da R10), R17 (EQUIVALENT_REQUEST,
    depois da R11) e a linha de custos com a regra do #62 (compara só quando a variante declara custos);
  * decision_policy.crypto_config: acrescenta as chaves novas da configuração do cain (sealed_scopes e o que mais o
    commit trouxer), com os valores do crypto.json daquele commit;
  * cycle: número, arquivo e sha256 do ciclo 1 preservado, commit do cain, sha256 do crypto.json e a autorização.
Nada mais muda (N+1, isolamento, matriz de falhas, soak, gates).

Uso: python freeze_cycle2.py <FROZEN_PARAMETERS ciclo 1> <clone do cain> <commit do cain> <saída>
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

CYCLE1_CONFIG_KEYS = {
    "schema", "domain", "config_version", "source", "contract", "frozen_parameters", "allowed_request_types",
    "closed_hypotheses", "frozen_families", "proposable_hypotheses", "allowed_symbols", "costs",
    "allowed_references", "max_priority_hint", "budget", "cooldown", "negative_result_states", "contradiction_pairs",
}
R16 = ("REQUIRE_HUMAN SEALED_SCOPE (R16): pedido que tocaria um escopo lacrado da configuração (sealed_scopes: valor, "
       "janela ou instante); campo lacrado ausente ou malformado também retém. Cripto: nenhum lacre")
R15 = ("REQUIRE_HUMAN HYPOTHESIS_NOT_ADMITTED_BY_DOMAIN (R15): o domínio já recusou a hipótese com o código "
       "HYPOTHESIS_NOT_ADMITTED; nova proposta dela não vira task")
R04 = ("BLOCK REQUEST_TYPE_NOT_ALLOWED: request_type fora das chaves da handler_allowlist do contrato, ou diferente "
       "do tipo que a configuração fixa para a hipótese (proposable_request_types, cain#67)")
R17 = ("DUPLICATE EQUIVALENT_REQUEST (R17): o mesmo experimento (o pedido sem request_id, hypothesis_id, research_id "
       "e client_ref) já rodou ou está aberto no domínio com outro ID (cain#68); tarefa recusada pelo domínio não conta")
COSTS = ("BLOCK COST_MODEL_MISMATCH / SYMBOL_NOT_ALLOWED / PRIORITY_ABOVE_CAP / REFERENCE_NOT_ALLOWED (custos comparados "
         "quando a variante de parameters do request_schema declara as chaves de custo, cain#62; no cripto a única "
         "variante declara)")
AUTHORIZATION = ("dono, 2026-09-28, chat da sessão cripto: (1) release única do cain e requalificação C14 das três "
                 "integrações nela (respostas \"Reconciliar no fim\" e \"Planejado + molde por hipótese\"): política v2 "
                 "com R15, #62, configuração do Brasileirão, R16, molde de pedido por hipótese e, pela sessão STOCKS, "
                 "R17 e justificativa conferida, publicada como v0.4.13rc10; (2) este ciclo 2, mostrado ao dono antes "
                 "de congelar (C15), aprovado com reemissão encadeada (resposta \"Aprovo; reemissão encadeada\"): o "
                 "ciclo 1 fica byte a byte no arquivo de supersedes")


def main() -> int:
    cycle1_path, cain, commit, out = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3], Path(sys.argv[4])
    raw1 = cycle1_path.read_bytes()
    frozen = json.loads(raw1)
    policy = frozen["decision_policy"]
    if policy["version"] != 1 or len(policy["rule_order"]) != 14:
        raise SystemExit("esperava o ciclo 1 (política v1, 14 regras)")
    crypto_raw = subprocess.run(["git", "-C", str(cain), "show", f"{commit}:src/cain/orchestration/data/crypto.json"],
                                capture_output=True, check=True).stdout
    crypto = json.loads(crypto_raw)
    order = list(policy["rule_order"])
    order[next(i for i, r in enumerate(order) if r.startswith("BLOCK REQUEST_TYPE_NOT_ALLOWED"))] = R04
    closed = next(i for i, r in enumerate(order) if r.startswith("BLOCK HYPOTHESIS_CLOSED"))
    costs = next(i for i, r in enumerate(order) if r.startswith("BLOCK COST_MODEL_MISMATCH"))
    order[costs] = COSTS
    order.insert(closed + 1, R16)
    contradiction = next(i for i, r in enumerate(order) if r.startswith("REQUIRE_HUMAN CONTRADICTION_UNRESOLVED"))
    order.insert(contradiction + 1, R15)
    new_hypothesis = next(i for i, r in enumerate(order) if r.startswith("REQUIRE_HUMAN NEW_HYPOTHESIS"))
    order.insert(new_hypothesis + 1, R17)
    policy["version"] = 2
    policy["rule_order"] = order
    new_keys = sorted(set(crypto) - CYCLE1_CONFIG_KEYS)
    for key in new_keys:
        policy["crypto_config"][key] = crypto[key]
    sha1 = hashlib.sha256(raw1).hexdigest()
    frozen["cycle"] = {
        "number": 2,
        "supersedes": {"file": f"FROZEN_PARAMETERS_cycle1_{sha1[:12]}.json", "sha256": sha1},
        "why": "C14: a DecisionPolicy e a configuração do cripto mudaram (parâmetro congelado); a fase inteira, novo ciclo",
        "cain": {"commit": commit, "crypto_config_sha256": hashlib.sha256(crypto_raw).hexdigest(),
                 "new_config_keys": new_keys},
        "authorized_by": AUTHORIZATION,
        "unchanged": "n_plus_1, isolation, failure_matrix, soak_profile, gates_required e demais chaves do ciclo 1",
    }
    raw2 = (json.dumps(frozen, indent=1, ensure_ascii=False) + "\n").encode("utf-8")
    out.write_bytes(raw2)
    print(json.dumps({"out": str(out), "sha256": hashlib.sha256(raw2).hexdigest(), "supersedes": sha1,
                      "new_config_keys": new_keys, "rules": len(order)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
