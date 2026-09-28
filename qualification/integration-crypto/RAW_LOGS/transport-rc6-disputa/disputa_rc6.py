"""Disputa da trava com o transporte 0.1.0rc6 (trava exclusiva por domínio no consumidor, ecosystem-predictor#36).

Dois consumidores do cripto, iniciados ao mesmo tempo sobre a mesma task, spool, ledger e estado, N repetições.
Esperado em cada uma: nenhum processo morre; um sai com a task entregue, o outro com exit 6 e a linha
{"action":"busy","code":"CONSUMER_BUSY"} sem publicar nada (ou, se o primeiro já tiver terminado, sai 0 sem nada a
fazer); exatamente um arquivo de resultado (RESULT); uma admissão, um experimento e um RESULT terminal no CAIN.
Só stdlib. Uso: python disputa_rc6.py <cain> <consumidor> <fixture 01-allow> <policy> <objects> <saída> <N>
"""

import json
import sqlite3
import subprocess
import sys
import time
from pathlib import Path

CAIN, CONSUMER, FIX, POLICY, OBJECTS, OUT = (Path(a) for a in sys.argv[1:7])
N = int(sys.argv[7])
OUT.mkdir(parents=True, exist_ok=True)
LOG = (OUT / "commands.log").open("a", encoding="utf-8")


def run(label, argv):
    done = subprocess.run([str(a) for a in argv], capture_output=True, text=True)
    LOG.write(f"### {label}\n$ {' '.join(map(str, argv))}\n{done.stdout}{done.stderr[-2000:]}--- exit {done.returncode}\n")
    return done.returncode, done.stdout


def ro(path):
    return sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)


rows = []
for i in range(1, N + 1):
    w = OUT / f"it{i:02d}"
    state, spool, dstate, ledger = w / "cain", w / "spool", w / "domain", w / "consumer" / "ledger.sqlite"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    _, out = run(f"{i} propose", [CAIN, "research", "propose", "--domain", "crypto", "--state", state, "--proposal",
                                  FIX, "--as-of", "2026-09-29T12:00:00Z"])
    decision = json.loads(out.splitlines()[0]).get("decision") if out.strip() else None
    run(f"{i} dispatch", [CAIN, "research", "dispatch", "--domain", "crypto", "--state", state, "--spool", spool])
    argv = [str(a) for a in [CONSUMER, "--domain", "crypto", "--spool", spool, "--ledger", ledger, "--state", dstate,
                             "--policy", POLICY, "--objects", OBJECTS]]
    procs = [subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) for _ in range(2)]
    outs = [p.communicate() for p in procs]
    codes = [p.returncode for p in procs]
    for k, (so, se) in enumerate(outs):
        LOG.write(f"### {i} consumer {k}\n{so}{se[-3000:]}--- exit {codes[k]}\n")
    crashed = [k for k, (so, se) in enumerate(outs) if "Traceback" in se]
    busy = [k for k, (so, se) in enumerate(outs) if codes[k] == 6 and '"CONSUMER_BUSY"' in so]
    run(f"{i} ingest", [CAIN, "research", "ingest", "--domain", "crypto", "--state", state, "--spool", spool])
    _, ep = run(f"{i} episodes", [CAIN, "research", "episodes", "--domain", "crypto", "--state", state])
    ep = json.loads(ep.splitlines()[0])
    with ro(dstate / "admission.sqlite") as db:
        admitted = db.execute("SELECT count(*) FROM admissions WHERE decision='ACCEPTED'").fetchone()[0]
    with ro(dstate / "x" / "journal.sqlite") as db:
        experiments = db.execute("SELECT count(*) FROM experiments").fetchone()[0]
    statuses = sorted(json.loads(f.read_text(encoding="utf-8"))["outcome"]["status"]
                      for f in (spool / "crypto" / "results").glob("TASK-*.json"))
    terminal = [r for r in ep["inbox"] if r["class"] == "TERMINAL_RESULT"]
    others_ok = all(codes[k] in (0, 6) for k in range(2))
    ok = (decision == "ALLOW" and not crashed and others_ok and statuses == ["RESULT"] and admitted == 1
          and experiments == 1 and len(terminal) == 1 and len(ep["inbox"]) == 1 and ep["memory"]["status"] == "intact")
    rows.append({"iteration": i, "ok": ok, "consumer_exits": codes, "busy": busy, "crashed": crashed,
                 "result_statuses": statuses, "admitted": admitted, "experiments": experiments,
                 "inbox": len(ep["inbox"]), "terminal_results": len(terminal)})
    print(json.dumps(rows[-1]), flush=True)
summary = {"scenario": "consumer-lock-contention", "transport": "0.1.0rc6 (ecosystem-predictor#36, dae4e57)",
           "iterations": N, "passed": sum(r["ok"] for r in rows), "failed": sum(not r["ok"] for r in rows),
           "busy_exits": sum(len(r["busy"]) for r in rows), "crashes": sum(bool(r["crashed"]) for r in rows),
           "rows": rows}
(OUT / "SUMMARY.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
print(json.dumps({k: summary[k] for k in ("scenario", "iterations", "passed", "failed", "busy_exits", "crashes")}))
