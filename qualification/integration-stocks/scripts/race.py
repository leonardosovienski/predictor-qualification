"""Disputa: dois consumidores do Stocks ao mesmo tempo sobre a mesma task (sugestão da sessão cripto; não é gate; rodado com o runtime do runtime_env.sh da missão).

Em cada repetição (estado novo): a semente (backtest real) é proposta e despachada; dois processos
`predictor-research-consumer` idênticos começam juntos; depois o CAIN ingere. Confere:
  * um experimento só no journal do domínio e uma admissão aceita para o request_id (sem efeito duplicado);
  * pelo menos um resultado terminal ingerido para a task (nada perdido);
  * saída de cada consumidor (ação, status) e se algum morreu com exceção (PermissionError etc.);
  * se o perdedor publicou um envelope não terminal falso (ex.: OPS_FAILED_RETRYABLE) ao lado do RESULT.
Uso: race.py <out> <work> <qualification/integration-stocks> <repetições>
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

MISSION = Path(sys.argv[3]).resolve()
sys.path.insert(0, str(MISSION / "scripts"))
from harness import Harness, now  # noqa: E402


def main() -> int:
    out, work, reps = Path(sys.argv[1]), Path(sys.argv[2]), int(sys.argv[4])
    rows = []
    for rep in range(1, reps + 1):
        h = Harness(out / f"rep{rep:02d}", work / f"rep{rep:02d}", MISSION, f"race-{rep}")
        seed = h.real_proposal("fixtures/proposals/e2e/01-allow.json", h.work / "seed.json")
        _c, lines, _ = h.propose("propose seed", seed, as_of=now())
        h.dispatch("dispatch")
        h.ledger.parent.mkdir(parents=True, exist_ok=True)
        argv = [h.bin["CONSUMER_BIN"], "--domain", "stocks", "--spool", str(h.spool), "--ledger", str(h.ledger),
                "--state", str(h.dstate), "--policy", h.op["policy"], "--objects", h.op["objects"]]
        t0 = time.time()
        procs = [subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE) for _ in range(2)]
        outs = [p.communicate(timeout=900) for p in procs]
        seconds = round(time.time() - t0, 3)
        consumers = []
        for i, (p, (so, se)) in enumerate(zip(procs, outs)):
            text_out, text_err = so.decode("utf-8", "replace"), se.decode("utf-8", "replace")
            (h.out / f"consumer{i}.stdout").write_text(text_out, encoding="utf-8")
            (h.out / f"consumer{i}.stderr").write_text(text_err, encoding="utf-8")
            parsed = []
            for line in text_out.splitlines():
                try:
                    parsed.append(json.loads(line))
                except ValueError:
                    parsed.append({"raw": line[:200]})
            consumers.append({"exit": p.returncode,
                              "lines": [{k: x.get(k) for k in ("action", "class", "status", "result_write")} for x in parsed],
                              "exception": next((l for l in text_err.splitlines()
                                                 if "Error" in l or "Exception" in l), None)})
        _c, ingested, _ = h.ingest("ingest")
        with h.ro(h.dstate / "x" / "journal.sqlite") as db:
            experiments = db.execute("SELECT count(*) FROM experiments").fetchone()[0]
        with h.ro(h.dstate / "admission.sqlite") as db:
            accepted = db.execute("SELECT count(*) FROM admissions WHERE decision='ACCEPTED'").fetchone()[0]
        results = [{"file": p.name, "status": r.get("outcome", {}).get("status") if isinstance(r.get("outcome"), dict)
                    else r.get("status")} for p, r in h.results()]
        episodes = h.episodes("episodes")
        terminal = [r for r in episodes["inbox"] if r["class"] == "TERMINAL_RESULT"]
        rows.append({"rep": rep, "seconds": seconds, "decision": (lines[0] if lines else {}).get("decision"),
                     "consumers": consumers, "results_in_spool": results, "ingest": ingested,
                     "experiments": experiments, "admissions_accepted": accepted,
                     "terminal_results": len(terminal),
                     "inbox_classes": sorted(r["class"] for r in episodes["inbox"]),
                     "ok": experiments == 1 and accepted == 1 and len(terminal) >= 1
                     and all(c["exception"] is None for c in consumers)})
        print(json.dumps({"rep": rep, "ok": rows[-1]["ok"], "experiments": experiments,
                          "results": [r["status"] for r in results],
                          "exits": [c["exit"] for c in consumers],
                          "exceptions": [c["exception"] for c in consumers]}), flush=True)
    summary = {"reps": reps, "ok": sum(r["ok"] for r in rows),
               "with_exception": sum(any(c["exception"] for c in r["consumers"]) for r in rows),
               "false_non_terminal": sum(any(x["status"] not in ("RESULT", "DUPLICATE") for x in r["results_in_spool"])
                                         for r in rows),
               "rows": rows}
    (out / "RACE.json").write_text(json.dumps(summary, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({k: summary[k] for k in ("reps", "ok", "with_exception", "false_non_terminal")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
