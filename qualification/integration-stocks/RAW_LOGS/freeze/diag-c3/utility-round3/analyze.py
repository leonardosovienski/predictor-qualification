"""Análise da rodada de utilidade: resultados do domínio, memória do CAIN × leitura autoritativa, justificativas.

Lê o spool, o REPORT.json da campanha e o commands.log. Consulta, por processos novos, `stocks-research show` (fonte
autoritativa do domínio) e `cain memory facts` (memória do CAIN). Grava ANALYSIS.json. Uso:
analyze.py <out da campanha> <work da campanha>
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from collections import Counter
from pathlib import Path


def run(argv: list) -> tuple[int, str]:
    done = subprocess.run([str(a) for a in argv], capture_output=True, text=True)
    return done.returncode, done.stdout


def main() -> int:
    out, work = Path(sys.argv[1]), Path(sys.argv[2])
    report = json.loads((out / "REPORT.json").read_text(encoding="utf-8"))
    cain, research = os.environ["CAIN_BIN"], os.environ["STOCKS_RESEARCH_BIN"]
    state, dstate = work / "cain-state", work / "domain-state"
    # ------------------------------------------------------------------ domain outcomes and authoritative re-read
    results = []
    for path in sorted((work / "spool" / "stocks" / "results").glob("TASK-*.json")):
        env = json.loads(path.read_bytes())
        row = {"file": path.name, "task_id": env["task_id"], "episode_id": env["episode_id"],
               "request_id": env["request_id"], "hypothesis_id": env["hypothesis_id"],
               "outcome": env["outcome"]}
        res = env.get("result")
        if res:
            row.update({k: res.get(k) for k in ("result_state", "scientific_state", "economic_state",
                                                "operational_state", "payload_sha256")})
            code, shown = run([research, "--state", dstate, "show", env["request_id"]])
            shown_doc = json.loads(shown.splitlines()[0]) if code == 0 and shown.strip() else {}
            row["authoritative_sha256"] = shown_doc.get("result_sha256")
            row["payload_equals_authoritative"] = shown_doc.get("result_sha256") == res.get("payload_sha256")
            payload = json.loads(res["payload_canonical"])
            row["payload_keys"] = sorted(payload)[:40]
            row["metrics"] = payload.get("metrics") or payload.get("summary") or payload.get("statistics")
        results.append(row)
    # ------------------------------------------------------------------ CAIN memory (whole stdout is one JSON)
    mem = state / "memory.sqlite"
    _c, facts_raw = run([cain, "memory", "--db", mem, "facts", "--as-of", "now", "--cube", "stocks"])
    facts = json.loads(facts_raw) if facts_raw.strip() else {}
    _c, crypto_raw = run([cain, "memory", "--db", mem, "facts", "--as-of", "now", "--cube", "crypto"])
    crypto = json.loads(crypto_raw) if crypto_raw.strip() else {}
    fact_rows = facts.get("facts", facts if isinstance(facts, list) else [])
    by_task = {}
    for f in fact_rows:
        obj = f.get("object") if isinstance(f.get("object"), dict) else {}
        key = obj.get("task_id") or f.get("subject")
        by_task[key] = {"predicate": f.get("predicate"), "status": f.get("status"), "object": obj}
    memory_vs_domain = []
    for r in results:
        m = by_task.get(r["task_id"])
        memory_vs_domain.append({"task_id": r["task_id"], "in_memory": m is not None,
                                 "memory_states": None if m is None else {k: m["object"].get(k) for k in
                                                                          ("status", "result_state", "scientific_state",
                                                                           "economic_state", "reason_code",
                                                                           "payload_sha256")},
                                 "domain_states": {k: r.get(k) for k in ("result_state", "scientific_state",
                                                                         "economic_state")},
                                 "domain_status": r["outcome"]["status"],
                                 "sha_matches": m is not None and m["object"].get("payload_sha256") in
                                 (None, r.get("payload_sha256"))})
    # ------------------------------------------------------------------ rationales
    rationales = []
    for c in report["cycles"]:
        if "rationale" in c:
            rationales.append({"cycle": c["cycle"], "hypothesis": c["hypothesis"], "rationale": c["rationale"],
                               "mentioned": c["rationale_check"]["mentioned"],
                               "without_evidence": c["rationale_check"]["without_evidence"]})
    # ------------------------------------------------------------------ timings from commands.log
    timings: dict[str, list] = {}
    for line in (out / "commands.log").read_text(encoding="utf-8").splitlines():
        if line.startswith('{"n": '):
            rec = json.loads(line)
            kind = rec["label"].split()[0] if not rec["label"].startswith("llm proposal") else "llm"
            timings.setdefault(kind, []).append(rec["seconds"])
    analysis = {
        "results": results,
        "outcome_counts": Counter(f"{r['hypothesis_id']} {r['outcome']['status']} {r.get('result_state')}"
                                  for r in results),
        "payload_equals_authoritative": sum(bool(r.get("payload_equals_authoritative")) for r in results
                                            if r.get("payload_sha256")),
        "results_with_payload": sum(1 for r in results if r.get("payload_sha256")),
        "memory_facts_stocks": len(fact_rows), "memory_facts_crypto": len(crypto.get("facts", crypto)
                                                                         if isinstance(crypto, (dict, list)) else []),
        "memory_vs_domain": memory_vs_domain,
        "rationales": rationales,
        "timings": {k: {"n": len(v), "median": sorted(v)[len(v) // 2], "max": max(v)} for k, v in timings.items()},
        "hypotheses_chosen": Counter(c.get("hypothesis") for c in report["cycles"]),
    }
    (out / "ANALYSIS.json").write_text(json.dumps(analysis, indent=1, ensure_ascii=False, default=str) + "\n",
                                       encoding="utf-8")
    print(json.dumps({k: analysis[k] for k in ("outcome_counts", "payload_equals_authoritative",
                                               "results_with_payload", "memory_facts_stocks", "memory_facts_crypto",
                                               "timings", "hypotheses_chosen")}, ensure_ascii=False, indent=1,
                     default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
