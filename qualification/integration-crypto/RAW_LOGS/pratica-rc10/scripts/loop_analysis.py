"""Análise do ciclo prático: decisões, execução, memória × spool, justificativas do LLM."""
import json, sqlite3, statistics, sys
from collections import Counter
from pathlib import Path
L = Path(sys.argv[1])
rows = [json.loads(x) for x in (L / "out/campaign.jsonl").read_text().splitlines()]
res = [r for r in rows if isinstance(r.get("result"), dict) and r["result"].get("net_return_bps") is not None]
rej = [r for r in rows if isinstance(r.get("result"), dict) and (r["result"].get("outcome") or {}).get("status") == "REJECTED"]
print("rodadas", len(rows), "decisões", Counter(f"{r.get('decision')} {r.get('rule')}" for r in rows))
print("hipóteses", Counter(r.get("hypothesis_id") for r in rows))
print("backtests com resultado", len(res), "recusados pelo domínio", len(rej), [r["hypothesis_id"] for r in rej])
seeds = [r.get("placebo_seed") for r in rows if r.get("placebo_seed") is not None]
print("sementes", len(seeds), "distintas", len(set(seeds)))
print("estados", Counter(f"{r['result']['scientific_state']}/{r['result']['economic_state']}" for r in res))
net = [r["result"]["net_return_bps"] for r in res]
print("líquido bps: média %.1f dp %.1f min %s max %s; IC contém 0: %d/%d" % (
    statistics.mean(net), statistics.pstdev(net), min(net), max(net),
    sum(1 for r in res if r["result"]["net_ci_bps"][0] <= 0 <= r["result"]["net_ci_bps"][1]), len(res)))
print("capital_permission true:", sum(1 for r in res if r["result"].get("capital_permission")))
chk = Counter()
bad = []
for a in sorted((L / "out/proposals").glob("*.audit.json")):
    d = json.loads(a.read_text())
    c = d["rationale_check"]
    for k in ("without_evidence", "count_mismatches", "eligibility_mismatches"):
        if c.get(k):
            chk[k] += 1; bad.append((a.name, k, c[k]))
    chk["audits"] += 1
    p = json.loads(d["prompt"])
    for key in ("metrics", "net_return_bps", "costs", "closed_hypotheses"):
        if key in d["prompt"]:
            chk["prompt_has_" + key] += 1
print("justificativas:", dict(chk))
for b in bad[:6]:
    print("  ", b[0], b[1], json.dumps(b[2], ensure_ascii=False)[:300])
ep = json.loads((L / "out/episodes_final.json").read_text())
print("memória:", ep.get("memory"))
db = sqlite3.connect((L / "walk/cain-state/memory.sqlite").resolve().as_uri() + "?mode=ro", uri=True)
cols = [r[1] for r in db.execute("PRAGMA table_info(memory_events)")]
row = db.execute("SELECT * FROM memory_events ORDER BY seq DESC LIMIT 1").fetchone()
ev = dict(zip(cols, row))
blob = next((v for v in ev.values() if isinstance(v, (str, bytes)) and "scientific_state" in (v if isinstance(v, str) else v.decode("utf-8", "replace"))), None)
txt = blob if isinstance(blob, str) else (blob or b"").decode("utf-8", "replace")
print("fato mais recente guarda métricas?", any(k in txt for k in ("net_return_bps", "net_ci_low_bps", "sample_size")))
print("chaves do fato:", txt[:700])
