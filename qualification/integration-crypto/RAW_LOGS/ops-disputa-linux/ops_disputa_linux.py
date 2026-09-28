"""Mesma disputa da trava do Ops (ops_disputa.py), no Linux (WSL), com o runtime da bateria rc12."""
import json, re, sqlite3, subprocess, sys, time
from pathlib import Path
P, N = Path(sys.argv[1]), int(sys.argv[2])
ENV = dict(re.findall(r'export (\w+)="([^"]*)"', (P / "rt/env.sh").read_text()))
FIX = P / "qualification/integration-crypto/fixtures/proposals/e2e/01-allow.json"
OUT = P / "out/ops-disputa-linux"; OUT.mkdir(parents=True, exist_ok=True)
LOG = (OUT / "commands.log").open("a")
def run(argv):
    d = subprocess.run([str(a) for a in argv], capture_output=True, text=True); LOG.write(d.stdout + d.stderr[-2000:]); return d.stdout
def ro(p): return sqlite3.connect(p.resolve().as_uri() + "?mode=ro", uri=True)
rows = []
for i in range(1, N + 1):
    w = OUT / f"it{i:02d}"; st, sp, ds, lg = w / "cain", w / "spool", w / "domain", w / "consumer/ledger.sqlite"
    lg.parent.mkdir(parents=True, exist_ok=True)
    run([ENV["CAIN_BIN"], "research", "propose", "--domain", "crypto", "--state", st, "--proposal", FIX, "--as-of", "2026-09-29T12:00:00Z"])
    run([ENV["CAIN_BIN"], "research", "dispatch", "--domain", "crypto", "--state", st, "--spool", sp])
    argv = [str(a) for a in [ENV["CONSUMER_BIN"], "--domain", "crypto", "--spool", sp, "--ledger", lg, "--state", ds,
                             "--policy", ENV["OP_POLICY"], "--objects", ENV["OP_OBJECTS"]]]
    ps = [subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) for _ in range(2)]
    outs = [p.communicate() for p in ps]; codes = [p.returncode for p in ps]
    for so, se in outs: LOG.write(so + se[-3000:])
    crashed = [k for k, (so, se) in enumerate(outs) if "Traceback" in se]
    run([ENV["CAIN_BIN"], "research", "ingest", "--domain", "crypto", "--state", st, "--spool", sp])
    ep = json.loads(run([ENV["CAIN_BIN"], "research", "episodes", "--domain", "crypto", "--state", st]).splitlines()[0])
    with ro(ds / "x/journal.sqlite") as db: exp = db.execute("SELECT count(*) FROM experiments").fetchone()[0]
    statuses = sorted(json.loads(f.read_text())["outcome"]["status"] for f in (sp / "crypto/results").glob("TASK-*.json"))
    rows.append({"it": i, "codes": codes, "crashed": crashed, "experiments": exp, "statuses": statuses,
                 "terminal": sum(1 for r in ep["inbox"] if r["class"] == "TERMINAL_RESULT")})
tally = {}
for r in rows: tally["+".join(r["statuses"])] = tally.get("+".join(r["statuses"]), 0) + 1
summary = {"iterations": N, "crashes": sum(bool(r["crashed"]) for r in rows), "one_experiment": sum(r["experiments"] == 1 for r in rows),
           "one_terminal": sum(r["terminal"] == 1 for r in rows), "result_statuses": tally}
(OUT / "SUMMARY.json").write_text(json.dumps({**summary, "rows": rows}, indent=1))
print(json.dumps(summary))
