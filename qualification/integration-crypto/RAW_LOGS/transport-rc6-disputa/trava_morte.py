"""Morte do dono da trava do consumidor (transporte 0.1.0rc6) e retomada, no Windows (msvcrt) e no POSIX.

Para cada ponto de falha do transporte (PREDICTOR_RESEARCH_TRANSPORT_FAULT → os._exit(86)): um consumidor morre com a
trava na mão; outro consumidor, logo depois, tem de pegar a trava (sem CONSUMER_BUSY), terminar a task com um único
experimento no domínio, e o CAIN ingere um único resultado terminal. Só stdlib.
Uso: python trava_morte.py <cain> <consumidor> <fixture> <policy> <objects> <saída> <repetições por ponto>
"""

import json
import os
import sqlite3
import subprocess
import sys
from pathlib import Path

CAIN, CONSUMER, FIX, POLICY, OBJECTS, OUT = (Path(a) for a in sys.argv[1:7])
N = int(sys.argv[7])
POINTS = ("before_domain", "after_domain_before_result_write", "after_result_write")
OUT.mkdir(parents=True, exist_ok=True)
LOG = (OUT / "commands.log").open("a", encoding="utf-8")


def run(label, argv, fault=None):
    env = dict(os.environ)
    env.pop("PREDICTOR_RESEARCH_TRANSPORT_FAULT", None)
    if fault:
        env["PREDICTOR_RESEARCH_TRANSPORT_FAULT"] = fault
    done = subprocess.run([str(a) for a in argv], capture_output=True, text=True, env=env)
    LOG.write(f"### {label} fault={fault}\n{done.stdout}{done.stderr[-2000:]}--- exit {done.returncode}\n")
    return done.returncode, done.stdout


def ro(path):
    return sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)


rows = []
for p, point in enumerate(POINTS, 1):
    for i in range(1, N + 1):
        w = OUT / f"p{p}-{i}"  # curto: o cripto recusa estado com mais de 120 caracteres no Windows (MAX_PATH)
        state, spool, dstate, ledger = w / "cain", w / "spool", w / "domain", w / "consumer" / "ledger.sqlite"
        ledger.parent.mkdir(parents=True, exist_ok=True)
        run("propose", [CAIN, "research", "propose", "--domain", "crypto", "--state", state, "--proposal", FIX,
                        "--as-of", "2026-09-29T12:00:00Z"])
        run("dispatch", [CAIN, "research", "dispatch", "--domain", "crypto", "--state", state, "--spool", spool])
        argv = [CONSUMER, "--domain", "crypto", "--spool", spool, "--ledger", ledger, "--state", dstate,
                "--policy", POLICY, "--objects", OBJECTS]
        died, _ = run(f"{point} {i} consumer A", argv, fault=point)
        code_b, out_b = run(f"{point} {i} consumer B", argv)
        run("ingest", [CAIN, "research", "ingest", "--domain", "crypto", "--state", state, "--spool", spool])
        _, ep = run("episodes", [CAIN, "research", "episodes", "--domain", "crypto", "--state", state])
        ep = json.loads(ep.splitlines()[0])
        with ro(dstate / "x" / "journal.sqlite") as db:
            experiments = db.execute("SELECT count(*) FROM experiments").fetchone()[0]
        statuses = sorted(json.loads(f.read_text(encoding="utf-8"))["outcome"]["status"]
                          for f in (spool / "crypto" / "results").glob("TASK-*.json"))
        terminal = [r for r in ep["inbox"] if r["class"] == "TERMINAL_RESULT"]
        ok = (died == 86 and code_b == 0 and "CONSUMER_BUSY" not in out_b and experiments == 1
              and len(terminal) == 1 and ep["memory"]["status"] == "intact"
              and all(s in ("RESULT", "DUPLICATE") for s in statuses))
        rows.append({"point": point, "iteration": i, "ok": ok, "a_exit": died, "b_exit": code_b,
                     "b_busy": "CONSUMER_BUSY" in out_b, "experiments": experiments, "result_statuses": statuses,
                     "terminal_results": len(terminal)})
        print(json.dumps(rows[-1]), flush=True)
summary = {"scenario": "consumer-lock-holder-death", "platform": sys.platform, "runs": len(rows),
           "passed": sum(r["ok"] for r in rows), "failed": sum(not r["ok"] for r in rows), "rows": rows}
(OUT / "SUMMARY.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
print(json.dumps({k: summary[k] for k in ("scenario", "platform", "runs", "passed", "failed")}))
