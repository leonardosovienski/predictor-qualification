"""Validação prática CAIN × cripto na rc10 (adaptada da campanha v4) dentro do escopo liberado (diagnóstico no WSL, fora dos repositórios).

Rodada 0: proposta manual congelada (01-allow) para o CAIN ter um pedido-modelo. Rodadas 1..N: o CAIN pede ao modelo
local (Ollama, GPU) o próximo experimento (`cain research explain --propose-for-domain`), a DecisionPolicy decide
(`cain research propose`) e, se ALLOW, a task vai pelo spool ao cripto (consumidor → adapter → admission/Ops/Core) e o
resultado volta para a memória (`ingest`). Tudo com as wheels publicadas; dados reais até o corte de 2026-08-31.
Saídas: out/campaign.jsonl (uma linha por rodada), out/commands.log, propostas e auditorias do LLM em out/proposals.
Uso: python campaign.py <rodadas> <modelo>
"""

import json
import os
import subprocess
import sys
import time
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

C = Path("/home/superleo13/predictors/runtime/integration-crypto/pratica-rc10/loop")
FIX = Path("/home/superleo13/predictors/runtime/integration-crypto/pratica-rc10/"
           "qualification/integration-crypto/fixtures/proposals/e2e")
W, OUT = C / "walk", C / "out"
S, SP, DS, L = W / "cain-state", W / "spool", W / "domain-state", W / "consumer" / "ledger.sqlite"
PROPS = OUT / "proposals"
for d in (L.parent, PROPS):
    d.mkdir(parents=True, exist_ok=True)
CAIN, CONSUMER = os.environ["CAIN_BIN"], os.environ["CONSUMER_BIN"]
LOG = (OUT / "commands.log").open("a", encoding="utf-8")
ROUNDS, MODEL = int(sys.argv[1]), sys.argv[2]
START = int(sys.argv[3]) if len(sys.argv) > 3 else 0
URL = "http://127.0.0.1:11434"


def now():
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def run(label, argv):
    t0 = time.time()
    done = subprocess.run([str(a) for a in argv], capture_output=True, text=True, timeout=1800)
    LOG.write(f"### {label} ({time.time() - t0:.1f}s)\n$ {' '.join(map(str, argv))}\n--- stdout\n{done.stdout}"
              f"--- stderr\n{done.stderr[-4000:]}--- exit {done.returncode}\n\n")
    LOG.flush()
    lines = []
    for line in done.stdout.splitlines():
        try:
            lines.append(json.loads(line))
        except ValueError:
            pass
    return done.returncode, lines, round(time.time() - t0, 1)


def gpu():
    try:
        with urllib.request.urlopen(URL + "/api/ps", timeout=5) as r:
            return [{"name": m["name"], "size_vram": m.get("size_vram"), "size": m.get("size")}
                    for m in json.load(r).get("models", [])]
    except OSError as exc:
        return str(exc)


def execute(request_id):
    run("dispatch", [CAIN, "research", "dispatch", "--domain", "crypto", "--state", S, "--spool", SP])
    run("consumer", [CONSUMER, "--domain", "crypto", "--spool", SP, "--ledger", L, "--state", DS,
                     "--policy", os.environ["OP_POLICY"], "--objects", os.environ["OP_OBJECTS"]])
    run("ingest", [CAIN, "research", "ingest", "--domain", "crypto", "--state", S, "--spool", SP])
    for path in sorted((SP / "crypto" / "results").glob("TASK-*.json")):
        r = json.loads(path.read_bytes())
        if r.get("request_id") != request_id:
            continue
        if not (r.get("result") or {}).get("payload_canonical"):
            return {"status": r.get("status"), "outcome": r.get("outcome")}
        p = json.loads(r["result"]["payload_canonical"])
        m = p.get("domain_facts", {}).get("metrics", {})
        return {"status": r.get("status"), "scientific_state": p.get("scientific_state"),
                "economic_state": p.get("economic_state"),
                "net_return_bps": m.get("net_return_bps"), "net_ci_bps": [m.get("net_ci_low_bps"), m.get("net_ci_high_bps")],
                "gross_return_bps": m.get("gross_return_bps"), "sample_size": m.get("sample_size"),
                "long": m.get("long_observations"), "short": m.get("short_observations"),
                "max_drawdown_bps": m.get("max_drawdown_bps"),
                "vs_baseline": p.get("domain_facts", {}).get("baseline_comparison", {}).get("outcome"),
                "capital_permission": p.get("capital_permission")}
    return {"status": "NO_RESULT"}


def record(row):
    with (OUT / "campaign.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(json.dumps({k: row.get(k) for k in ("round", "hypothesis_id", "placebo_seed", "decision", "rule", "reason_code",
                                             "llm_seconds")}, ensure_ascii=False),
          json.dumps(row.get("result"), ensure_ascii=False)[:260], flush=True)


cfg = OUT / "cain-llm.toml"
cfg.write_text("\n".join(["[llm]", 'provider = "ollama"', f'model = "{MODEL}"', f'base_url = "{URL}"',
                          "temperature = 0.0", "seed = 42", "timeout = 900.0", "num_ctx = 8192", "num_predict = 512",
                          "max_input_bytes = 16000", "think = false", ""]), encoding="utf-8")

# rodada 0: pedido-modelo
if START == 0:
    proposal = json.loads((FIX / "01-allow.json").read_text(encoding="utf-8"))
    code, out, _ = run("propose r0", [CAIN, "research", "propose", "--domain", "crypto", "--state", S, "--proposal",
                                      FIX / "01-allow.json", "--as-of", now()])
    d = out[0] if out else {}
    row = {"round": 0, "source": "fixture", "hypothesis_id": proposal["request"]["hypothesis_id"],
           "placebo_seed": proposal["request"]["parameters"]["placebo_seed"], "rationale": proposal["rationale"],
           "decision": d.get("decision"), "rule": d.get("rule"), "reason_code": d.get("reason_code")}
    if d.get("decision") == "ALLOW":
        row["result"] = execute(proposal["request"]["request_id"])
    record(row)

for i in range(max(1, START), ROUNDS + 1):
    pid = f"cain:CAMP-{i:02d}"
    pfile = PROPS / f"camp-{i:02d}.json"
    code, out, secs = run(f"llm r{i}", [CAIN, "research", "explain", "proximo experimento de pesquisa do cripto",
                                        "--propose-for-domain", "crypto", "--state", S, "--proposal-out", pfile,
                                        "--proposal-id", pid, "--config", cfg])
    row = {"round": i, "source": "llm", "llm_exit": code, "llm_seconds": secs, "gpu": gpu() if i == 1 else None}
    if code != 0 or not pfile.exists():
        row["error"] = (out[0] if out else None)
        record(row)
        continue
    prop = json.loads(pfile.read_text(encoding="utf-8"))
    row.update(hypothesis_id=prop["request"]["hypothesis_id"], placebo_seed=prop["request"]["parameters"]["placebo_seed"],
               rationale=prop["rationale"])
    code, out, _ = run(f"propose r{i}", [CAIN, "research", "propose", "--domain", "crypto", "--state", S, "--proposal",
                                         pfile, "--as-of", now()])
    d = out[0] if out else {}
    row.update(decision=d.get("decision"), rule=d.get("rule"), reason_code=d.get("reason_code"))
    if d.get("decision") == "ALLOW":
        row["result"] = execute(prop["request"]["request_id"])
    record(row)

code, out, _ = run("episodes", [CAIN, "research", "episodes", "--domain", "crypto", "--state", S])
(OUT / "episodes_final.json").write_text(json.dumps(out[0] if out else {}, ensure_ascii=False, indent=1), encoding="utf-8")
print("memória:", json.dumps((out[0] if out else {}).get("memory"), ensure_ascii=False))
