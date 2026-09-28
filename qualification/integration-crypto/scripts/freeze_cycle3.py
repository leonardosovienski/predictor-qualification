"""integration-crypto, ciclo 3 dos parâmetros congelados (C14: parâmetro congelado muda → a fase inteira, novo ciclo).

Parte do FROZEN_PARAMETERS.json do ciclo 2 e muda só uma coisa: decision_policy.crypto_config ganha
``result_metrics``, as métricas do resultado do cripto que o CAIN guarda nos fatos da memória e mostra ao modelo no modo
de proposta (validação prática de 2026-09-28: a memória e o contexto do LLM só tinham rótulos de estado). Cada entrada
é nome → caminho pontilhado no payload canônico do resultado (crypto-research-result/1); só números entram.
A config do cain (tools/build_domain_config.py) copia a chave para o crypto.json. Hipóteses propunháveis, referências,
custos, política e vetores não mudam (o dono decidiu manter QUAL-SHADOW-001 e os datasets da Etapa A: os vetores de
N+1 e contradição partem deles).

Uso: python freeze_cycle3.py <FROZEN_PARAMETERS ciclo 2> <saída>
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

RESULT_METRICS = {
    "net_return_bps": "domain_facts.metrics.net_return_bps",
    "net_ci_low_bps": "domain_facts.metrics.net_ci_low_bps",
    "net_ci_high_bps": "domain_facts.metrics.net_ci_high_bps",
    "sample_size": "domain_facts.metrics.sample_size",
}
AUTHORIZATION = ("dono, 2026-09-28, chat da sessão cripto, depois da validação prática CAIN × cripto na rc10: "
                 "\"Código + config\" (métricas do resultado na memória e no contexto do modelo; ID qualificado no "
                 "findings check) e, sobre a config, \"Manter e registrar\" (QUAL-SHADOW-001 e os datasets da Etapa A "
                 "ficam; o desalinhamento com a admissão do domínio fica registrado, contido pela R15). Este ciclo 3 "
                 "foi mostrado ao dono antes de congelar (C15), com o ciclo 2 preservado byte a byte e encadeado como "
                 "no ciclo 2; resposta: \"Aprovo\"")


def main() -> int:
    cycle2_path, out = Path(sys.argv[1]), Path(sys.argv[2])
    raw2 = cycle2_path.read_bytes()
    frozen = json.loads(raw2)
    if frozen.get("cycle", {}).get("number") != 2 or frozen["decision_policy"]["version"] != 2:
        raise SystemExit("esperava o ciclo 2 (política v2)")
    crypto = frozen["decision_policy"]["crypto_config"]
    if "result_metrics" in crypto:
        raise SystemExit("result_metrics já existe")
    crypto["result_metrics"] = RESULT_METRICS
    sha2 = hashlib.sha256(raw2).hexdigest()
    previous = frozen["cycle"]
    frozen["cycle"] = {
        "number": 3,
        "supersedes": {"file": f"FROZEN_PARAMETERS_cycle2_{sha2[:12]}.json", "sha256": sha2},
        "chain": [previous["supersedes"]],
        "why": ("C14: a configuração do cripto no cain ganha result_metrics (parâmetro congelado); a fase inteira, "
                "novo ciclo, na release cain 0.4.13rc11"),
        "changed": ["decision_policy.crypto_config.result_metrics"],
        "authorized_by": AUTHORIZATION,
        "unchanged": ("decision_policy.version e rule_order, hipóteses propunháveis, referências, custos, n_plus_1, "
                      "isolation, failure_matrix, soak_profile, gates_required e demais chaves do ciclo 2"),
    }
    raw3 = (json.dumps(frozen, indent=1, ensure_ascii=False) + "\n").encode("utf-8")
    out.write_bytes(raw3)
    print(json.dumps({"out": str(out), "sha256": hashlib.sha256(raw3).hexdigest(), "supersedes": sha2}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
