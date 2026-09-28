"""integration-stocks, ciclo 4: estado do achado que o ciclo 4 fecha com evidência (C6).

IS-F009 (disputa de dois consumidores do stocks na mesma task) ficou ACCEPTED_LIMITATION no ciclo 3 pela decisão do dono
"Registrar + regra (Recomendado)". Depois o dono escolheu "Só o transporte (Recomendado)": a regra "um consumidor por
domínio por vez" virou código no predictor-research-transport 0.1.0rc6 (ecosystem-predictor#36). O ciclo 4 roda com
essa release, e o status só muda se a disputa refeita nas wheels publicadas (race.py, runtime do runtime_env.sh com
runtime_targets.json) confirmar, repetição a repetição:
  * as 20 repetições ok, sem exceção e sem nenhum envelope não terminal falso ao lado do RESULT;
  * em cada repetição, 1 experimento, só RESULT ingerido, e um dos dois consumidores saiu com o código 6 (CONSUMER_BUSY);
  * o transporte instalado no runtime é a 0.1.0rc6 com o sha256 de runtime_targets.json.
Falha fechado se a evidência não confirmar. Idempotente: só muda o achado se ele ainda estiver ACCEPTED_LIMITATION.
Uso: python cycle4_findings.py <raiz do predictor-qualification> <dir da disputa em RAW_LOGS> <pip freeze do consumidor>
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT, RACE_DIR, FREEZE = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
M = ROOT / "qualification/integration-stocks"


def ref(path: Path) -> dict:
    return {"file": path.resolve().relative_to(ROOT.resolve()).as_posix(),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def main() -> int:
    targets = json.loads((M / "runtime_targets.json").read_text(encoding="utf-8"))
    transport = targets["transport"]
    race = json.loads((RACE_DIR / "RACE.json").read_text(encoding="utf-8"))
    rows = race["rows"]
    frozen = FREEZE.read_text(encoding="utf-8")
    checks = {
        "transport_target_rc6": transport["version"] == "0.1.0rc6",
        "transport_installed": f"predictor_research_transport-0.1.0rc6-py3-none-any.whl#sha256={transport['sha256']}"
                               in frozen,
        "reps_20_ok": ({k: race[k] for k in ("reps", "ok", "with_exception", "false_non_terminal")}
                       == {"reps": 20, "ok": 20, "with_exception": 0, "false_non_terminal": 0} and len(rows) == 20),
        "each_one_experiment_one_result": all(
            r["ok"] and r["experiments"] == 1 and r["admissions_accepted"] == 1
            and [x["status"] for x in r["results_in_spool"]] == ["RESULT"] for r in rows),
        "each_loser_busy_exit_6": all(
            sorted(c["exit"] for c in r["consumers"]) == [0, 6]
            and any(line["action"] == "busy" for c in r["consumers"] if c["exit"] == 6 for line in c["lines"])
            for r in rows),
    }
    if not all(checks.values()):
        raise SystemExit(f"evidência não confirma: {checks}")
    path = M / "FINDINGS.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    changed = []
    for finding in doc["findings"]:
        if finding["id"] == "IS-F009" and finding["status"] == "ACCEPTED_LIMITATION":
            finding["status"] = "FIXED"
            finding["fix_cycle4"] = {
                "date": "2026-09-28",
                "owner_decision": {"by": "dono", "channel": "chat da sessão integration-stocks (pergunta com opções)",
                                   "words": "Só o transporte (Recomendado)"},
                "fix": ("predictor-research-transport 0.1.0rc6 (ecosystem-predictor#36, bac1f7b; wheel "
                        f"{transport['sha256'][:8]}…): trava exclusiva por domínio no consumidor; o segundo consumidor "
                        "sai com código 6 (CONSUMER_BUSY) sem ler o ledger, sem chamar o domínio e sem publicar. Na "
                        "disputa refeita nas wheels publicadas do ciclo 4 (cain 0.4.13rc13, transporte 0.1.0rc6, "
                        "stocks-predictor 0.3.0rc3): 20/20, exits (0, 6) em todas, 1 experimento e só RESULT em cada, "
                        "0 envelopes falsos (ciclo 3, transporte 0.1.0rc5: 16× OPS_FAILED_RETRYABLE e 4× "
                        "RECONCILIATION_REQUIRED falsos)"),
                "evidence": [ref(RACE_DIR / "RACE.json"), ref(RACE_DIR / "race.log"), ref(FREEZE),
                             ref(M / "scripts/race.py")],
            }
            changed.append("IS-F009")
    path.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"fixed": changed, "checks": checks}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
