"""integration-brasileirao na cain 0.4.13rc13 + transporte 0.1.0rc6 (C14): troca os alvos do runtime.

Preparado em 2026-09-28 pela sessão de auditoria (nuvem). As fases de runtime desta missão rodam só no PC 2
(owner_linux, D-19: o dado real é privado), então este script NÃO foi executado aqui: ele é o primeiro passo da
sessão do PC 2 que refaz as fases pela C14 (cleanroom-final → contract-revalidation (d) → e2e → n-plus-1 →
isolation-ids-contradiction → idempotency-failure → windows-smoke → hosted-ci → soak → attestation).

Só o bloco do cain e o do transporte de runtime_targets.json mudam; cripto e stocks continuam nos finais
integrados deles (que já rodam na rc13/rc6). Evidência de que o brasileirao.json empacotado na rc13 é byte a byte o
da rc12 (f51ac735…, o mesmo regenerado conferido em RAW_LOGS/release-rc12/) e de que policy/service/store/config
não mudaram: RAW_LOGS/release-rc13/config_check_rc12_vs_rc13.log.

Uso: python scripts/rc13_edits.py <qualification/integration-brasileirao>
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

CAIN_NEW = "960fb25614709bd95ce607c8dfb80892d901d883"
ECO_NEW = "bac1f7b7b3ae687e4c75ff3849ccb1f458dca097"


def main(mission: Path) -> int:
    p = mission / "runtime_targets.json"
    t = json.loads(p.read_text(encoding="utf-8"))
    assert t["cain"]["version"] == "0.4.13rc12" and t["transport"]["version"] == "0.1.0rc5", "já adotado?"
    t["note"] = ("final_commits e final_wheels do runtime suportado desta missão (C3.1, C5); commit = o da tag da "
                 "pré-release; C14 de 2026-09-28: cain 0.4.13rc13 (molde do LLM sem task recusada, allowed_requests, "
                 "linter, findings v2; brasileirao.json byte a byte igual ao da rc12) e predictor-research-transport "
                 "0.1.0rc6 (trava exclusiva por domínio no consumidor: CONSUMER_BUSY); congelados do ciclo 4 sem "
                 "mudança. cripto e stocks = os finais integrados das integrações deles, usados no isolamento e nos "
                 "ciclos intercalados pelo runtime integrado, com o transporte desta missão")
    t["cain"] = {"repo": "leonardosovienski/cain", "version": "0.4.13rc13", "tag": "v0.4.13rc13", "commit": CAIN_NEW,
                 "url": "https://github.com/leonardosovienski/cain/releases/download/v0.4.13rc13/"
                        "cain_research-0.4.13rc13-py3-none-any.whl",
                 "sha256": "a1d94fd52762d6f8a9587f88064f53996aa46fcddad6be893272cb8079676854",
                 "note": "C14 da rc13 (2026-09-28); rc12 (302a5c8, 988a0fb9…) foi a release das fases de runtime "
                         "atestadas em run-20260928T145525Z-br12; rc11 e rc10 adotadas e trocadas antes (ver "
                         "QUALIFICATION_CHANGELOG.md)"}
    t["transport"] = {"repo": "leonardosovienski/ecosystem-predictor", "version": "0.1.0rc6",
                      "tag": "predictor-research-transport-v0.1.0rc6", "commit": ECO_NEW,
                      "url": "https://github.com/leonardosovienski/ecosystem-predictor/releases/download/"
                             "predictor-research-transport-v0.1.0rc6/"
                             "predictor_research_transport-0.1.0rc6-py3-none-any.whl",
                      "sha256": "6c7e83c4d93d4802b7cdfbc569b0828cde34ccd2241b5a274003ff21c9daec33"}
    p.write_text(json.dumps(t, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("runtime_targets.json: cain -> v0.4.13rc13", CAIN_NEW[:12], "| transport -> 0.1.0rc6", ECO_NEW[:12])
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1])))
