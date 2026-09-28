"""Disputa da trava do Ops no Windows (cenário da SHARED-005), pelo runtime suportado do cripto na cain rc12.

Em cada repetição, num diretório novo: o CAIN permite e despacha uma task real do cripto, e dois processos de consumidor
(predictor-research-consumer → admissão → Ops → Core) são iniciados ao mesmo tempo sobre o mesmo spool, ledger e estado
do domínio. Esperado: nenhum processo morre (sem PermissionError/Traceback), exatamente uma admissão e um experimento
para a task, um único resultado no spool, e o CAIN ingere um desfecho terminal. Só stdlib; roda com o python do venv do
consumidor. Uso: python ops_disputa.py <raiz autorizada> <repetições>
"""

import json
import sqlite3
import subprocess
import sys
import time
from pathlib import Path

ROOT, N = Path(sys.argv[1]), int(sys.argv[2])
CAIN = ROOT / "venv-cain" / "Scripts" / "cain.exe"
CONSUMER = ROOT / "venv-consumer" / "Scripts" / "predictor-research-consumer.exe"
FIX = ROOT / "stage-ciclo3b" / "mission" / "fixtures" / "proposals" / "e2e" / "01-allow.json"
OP = ROOT / "w" / "op"
OUT = ROOT / "ops-disputa"
OUT.mkdir(exist_ok=True)
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
    code, out = run(f"{i} propose", [CAIN, "research", "propose", "--domain", "crypto", "--state", state,
                                     "--proposal", FIX, "--as-of", "2026-09-29T12:00:00Z"])
    decision = json.loads(out.splitlines()[0]).get("decision") if out.strip() else None
    run(f"{i} dispatch", [CAIN, "research", "dispatch", "--domain", "crypto", "--state", state, "--spool", spool])
    argv = [str(a) for a in [CONSUMER, "--domain", "crypto", "--spool", spool, "--ledger", ledger, "--state", dstate,
                             "--policy", OP / "policy.json", "--objects", OP / "objects"]]
    t0 = time.time()
    procs = [subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) for _ in range(2)]
    outs = [p.communicate() for p in procs]
    codes = [p.returncode for p in procs]
    for k, (so, se) in enumerate(outs):
        LOG.write(f"### {i} consumer {k}\n{so}{se[-3000:]}--- exit {codes[k]}\n")
    crashed = [k for k, (so, se) in enumerate(outs) if "Traceback" in se or "PermissionError" in se]
    run(f"{i} ingest", [CAIN, "research", "ingest", "--domain", "crypto", "--state", state, "--spool", spool])
    _, ep = run(f"{i} episodes", [CAIN, "research", "episodes", "--domain", "crypto", "--state", state])
    ep = json.loads(ep.splitlines()[0])
    with ro(dstate / "admission.sqlite") as db:
        admitted = db.execute("SELECT count(*) FROM admissions WHERE decision='ACCEPTED'").fetchone()[0]
    with ro(dstate / "x" / "journal.sqlite") as db:
        experiments = db.execute("SELECT count(*) FROM experiments").fetchone()[0]
    results = list((spool / "crypto" / "results").glob("TASK-*.json"))
    terminal = [r for r in ep["inbox"] if r["class"] == "TERMINAL_RESULT"]
    ok = (decision == "ALLOW" and not crashed and all(c == 0 for c in codes) and admitted == 1 and experiments == 1
          and len(results) == 1 and len(terminal) == 1 and ep["memory"]["status"] == "intact")
    rows.append({"iteration": i, "ok": ok, "decision": decision, "consumer_exits": codes, "crashed": crashed,
                 "admitted": admitted, "experiments": experiments, "result_files": len(results),
                 "terminal_results": len(terminal), "seconds": round(time.time() - t0, 1)})
    print(json.dumps(rows[-1]), flush=True)
summary = {"scenario": "ops-lock-contention-windows", "host": "PC 2 (Windows local)", "iterations": N,
           "passed": sum(r["ok"] for r in rows), "failed": sum(not r["ok"] for r in rows), "rows": rows}
(OUT / "SUMMARY.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
print(json.dumps({k: summary[k] for k in ("scenario", "iterations", "passed", "failed")}))
