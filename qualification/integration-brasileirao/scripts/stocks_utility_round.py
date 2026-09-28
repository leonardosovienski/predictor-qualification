"""Rodada independente CAIN × Stocks na cain 0.4.13rc13 (não é gate da integration-brasileirao; harness próprio).

Pedido do dono no chat desta sessão ("preciso que o stocks esteja funcionando com relação ao cain; como vai fazer é com
você"). Critério de aceite combinado com a sessão STOCKS (rodada 3, 10 chamadas ao modelo local):
  1. toda proposta ALLOW é um experimento distinto (digest do experimento da política);
  2. 0 moldes vindos de task recusada pelo domínio;
  3. tipo de pedido certo por hipótese (proposable_request_types da configuração empacotada);
  4. o laço esgota as hipóteses só do LLM (proposal_overlays da configuração) e para em NO_ELIGIBLE_HYPOTHESIS;
  5. guardas 12/12 (a lista da sessão STOCKS, fixtures congeladas da integration-stocks);
  6. memória = fonte autoritativa 100% (payload_sha256 == result_sha256 do `stocks-research show`; estados do fato ==
     estados do payload);
  7. `momentum 12-1` reconhecido como encerrado pelo `findings check` (fonte: scientific_state do main do stocks fixado
     em 4c82885, D-26);
  8. relatório honesto com `momentum 12-1` e 95% publicável; A0 (sem crases), B (Sharpe sem citação), C (número errado
     com citação) e E (`29` entre crases sem citação) bloqueados;
  9. refusal_mismatches acusa as recusas falsas que aparecerem (conferido contra as recusas reais do domínio).
Limites declarados (não decididos): paráfrase sem nome; IS-F009 (resolvido pelo transporte 0.1.0rc6, um consumidor
por domínio). Regras D-24/D-26: pin novo das fontes públicas; wheel stocks 0.3.0rc3; as_of pelo data_cutoff do painel.
Saída pública só com IDs, estados, hashes e os números agregados do backtest que o relatório cita.
Uso (env.sh do runtime integrado; SOAK_OLLAMA_URL/SOAK_OLLAMA_MODEL): python stocks_utility_round.py <mission> <work> <out>
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

from harness import Harness, now


def after() -> str:
    """An as_of strictly after what was just recorded (now() has one-second resolution: a query in the same second
    does not see a fact, finding or evidence recorded in that second)."""
    time.sleep(1.1)
    return now()

STATES = ("result_state", "scientific_state", "economic_state")
FINDINGS_SOURCE = ("4c82885eddab233f2b57442046875fdc2c8f0932", "research/scientific_state.json")
POLICY = r'''
import json, sys
from cain.orchestration import config as dc, policy
from research_protocol import v2
import sqlite3
state = sys.argv[1]
cfg = dc.load("stocks")
db = sqlite3.connect(f"file:{state}/orchestration.sqlite?mode=ro", uri=True)
tasks = []
for task_id, raw in db.execute("select task_id, raw from outbox where domain='stocks' order by episode"):
    p = v2.loads_task(bytes(raw))["payload"]
    tasks.append({"task_id": task_id, "hypothesis_id": p["hypothesis_id"], "request_type": p["request_type"],
                  "digest": policy.experiment_digest(p)})
inbox = {r[0]: r[1] for r in db.execute("select task_id, class from inbox where domain='stocks'")}
print(json.dumps({"tasks": tasks, "classes": inbox, "types": cfg["proposable_request_types"],
                  "llm_only": sorted(cfg.get("proposal_overlays", {})), "proposable": cfg["proposable_hypotheses"]}))
'''


def main() -> int:
    mission, work, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    base = Harness(out, work, mission, "stocks-utility")
    s = base.for_domain("stocks")
    props = work / "proposals"
    props.mkdir(parents=True, exist_ok=True)
    st = "fixtures/proposals"
    sreq = json.loads((mission.parent / "integration-stocks" / st / "e2e/01-allow.json").read_text())["request"]

    def prop(rel, name, **changes):
        return base.integrated_proposal("stocks", f"{st}/{rel}", props / f"{name}.json", f"cain:SU-{name}", **changes)

    def cycle(label, path):
        _c, lines, _ = s.propose(f"{label}: propose", path)
        line = lines[0] if lines else {}
        status = state = None
        if line.get("decision") == "ALLOW":
            s.dispatch(f"{label}: dispatch")
            _c, cons, _ = s.consumer(f"{label}: consumer")
            status = next((l.get("status") for l in cons if l.get("action") == "delivered"), None)
            s.ingest(f"{label}: ingest")
            task_id = (line.get("task") or {}).get("task_id")
            env = next((e for _p, e in s.results("stocks") if e["task_id"] == task_id), None)
            if env and env.get("result"):  # the domain's own result_state (e.g. COLLECTION_RECORDED)
                state = json.loads(env["result"]["payload_canonical"]).get("result_state")
        return line, status, state

    # ---------------------------------------------------------------- semente real (operador)
    seed_line, seed_status, _st = cycle("seed", prop("e2e/01-allow.json", "seed", request_id="stocks:REQ-SU-SEED"))
    base.check("seed: real backtest ALLOW and executed", seed_line.get("decision") == "ALLOW" and seed_status == "RESULT",
               got={"decision": seed_line.get("decision"), "status": seed_status})
    # ---------------------------------------------------------------- 5. guardas (12)
    guards = [
        ("01 H1 closed", prop("n1/07-h1-momentum.json", "g01"), ("BLOCK", "HYPOTHESIS_CLOSED", "R05"), None),
        ("02 family momentum_12_1", prop("n1/11-family-momentum.json", "g02"), ("BLOCK", "HYPOTHESIS_CLOSED", "R05"), None),
        ("03 new hypothesis", prop("n1/06-new-hypothesis.json", "g03"), ("REQUIRE_HUMAN", "NEW_HYPOTHESIS", "R11"), None),
        ("04 EI collection", prop("n1/17-collection.json", "g04"), ("ALLOW", None, "R14"), "COLLECTION_RECORDED"),
        ("05 exact duplicate of the seed", prop("e2e/01-allow.json", "g05", request_id="stocks:REQ-SU-SEED"),
         ("DUPLICATE", "DUPLICATE_REQUEST", "R08"), None),
        ("06 same experiment, other ID (REAL-002)", prop("e2e/01-allow.json", "g06", request_id="stocks:REQ-SU-G06",
                                                          hypothesis_id="stocks:QUAL-PIT-MOM-REAL-002"),
         ("DUPLICATE", "EQUIVALENT_REQUEST", "R17"), None),
        ("07 QUAL-PIT-MOM-001 negative control 701", prop(
            "e2e/01-allow.json", "g07", request_id="stocks:REQ-SU-G07", hypothesis_id="stocks:QUAL-PIT-MOM-001",
            parameters=dict(sreq["parameters"], negative_control={"kind": "SHUFFLED_LABELS", "seed": 701})),
         ("ALLOW", None, "R14"), "REJECTED"),
        ("08 the same hypothesis again, seed 702", prop(
            "e2e/01-allow.json", "g08", request_id="stocks:REQ-SU-G08", hypothesis_id="stocks:QUAL-PIT-MOM-001",
            parameters=dict(sreq["parameters"], negative_control={"kind": "SHUFFLED_LABELS", "seed": 702})),
         ("REQUIRE_HUMAN", "HYPOTHESIS_NOT_ADMITTED_BY_DOMAIN", "R15"), None),
        ("09 future canary", prop("e2e/03-canary.json", "g09"), ("ALLOW", None, "R14"), "TEMPORAL_INTEGRITY_VIOLATION"),
        ("10 crypto proposal", prop("n1/03-crypto-h9.json", "g10"), ("BLOCK", "DOMAIN_MISMATCH", "R01"), None),
        ("11 cost mismatch", prop("n1/16-cost-mismatch.json", "g11"), ("BLOCK", "COST_MODEL_MISMATCH", "R06"), None),
        ("12 priority above cap", prop("n1/15-watch-high-priority.json", "g12"), ("BLOCK", "PRIORITY_ABOVE_CAP", "R06"), None),
    ]
    guard_rows = []
    for name, path, (decision, reason, rule), domain_status in guards:
        line, status, state = cycle(f"guard {name}", path)
        ok = line.get("decision") == decision and line.get("rule") == rule and (reason is None or line.get("reason_code") == reason)
        if domain_status:
            ok &= domain_status in (status, state)
        guard_rows.append({"guard": name, "ok": ok, "decision": line.get("decision"),
                           "reason_code": line.get("reason_code"), "rule": line.get("rule"), "domain": status,
                           "result_state": state})
    base.check("5: guards 12/12", sum(r["ok"] for r in guard_rows) == 12, guards=guard_rows)
    mem = (s.state / "memory.sqlite").read_bytes()
    base.check("5: canary token absent from the CAIN memory", b"FUTURE_CANARY_STOCKS_INTEGRATION_001" not in mem)
    # ---------------------------------------------------------------- laço do LLM (10 chamadas)
    url, model = os.environ.get("SOAK_OLLAMA_URL"), os.environ.get("SOAK_OLLAMA_MODEL")
    cfg = work / "cain-llm.toml"
    cfg.write_text("\n".join(["[llm]", 'provider = "ollama"', f'model = "{model}"', f'base_url = "{url}"',
                              "temperature = 0.0", "seed = 42", "timeout = 600.0", "num_ctx = 8192", "num_predict = 256",
                              "max_input_bytes = 16000", "think = false", ""]), encoding="utf-8")
    calls = []
    for i in range(1, 11):
        out_file = props / f"llm-{i:02d}.json"
        code, lines, _ = base.cain(f"llm {i}", "explain", "proximo experimento do stocks", "--propose-for-domain", "stocks",
                                   "--state", s.state, "--proposal-out", out_file, "--proposal-id", f"cain:SU-LLM-{i:02d}",
                                   "--config", cfg)
        row = {"call": i, "exit": code, "error": (lines[0].get("detail", "")[:80] if lines and code else None)}
        if code == 0 and out_file.exists():
            proposal = json.loads(out_file.read_text(encoding="utf-8"))
            audit = json.loads(out_file.with_suffix(".audit.json").read_text(encoding="utf-8"))
            line, status, _st = cycle(f"llm {i}", out_file)
            row |= {"hypothesis": proposal["request"]["hypothesis_id"], "request_type": proposal["request"]["request_type"],
                    "decision": line.get("decision"), "reason_code": line.get("reason_code"), "domain": status,
                    "rationale": proposal.get("rationale", "")[:400], "rationale_check": audit.get("rationale_check")}
            (out / f"llm-{i:02d}.audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=1), encoding="utf-8")
        calls.append(row)
    script = work / "policy.py"
    script.write_text(POLICY, encoding="utf-8")
    _c, lines, _ = base.run("tasks, digests, types", [os.environ["CAIN_PY"], "-I", script, s.state], public_stdout="full")
    view = lines[0]
    by_task = {t["task_id"]: t for t in view["tasks"]}
    llm_tasks = [t for t in view["tasks"] if any(c.get("hypothesis") == t["hypothesis_id"] and c.get("decision") == "ALLOW"
                                                   for c in calls)]
    allow_digests = [t["digest"] for t in view["tasks"]]
    base.check("1: every ALLOW task is a distinct experiment", len(allow_digests) == len(set(allow_digests)),
               tasks=len(allow_digests))
    refused_digests = {by_task[t]["digest"] for t, k in view["classes"].items() if k == "TERMINAL_REFUSAL" and t in by_task}
    base.check("2: no LLM proposal reuses the request of a task the domain refused",
               not any(t["digest"] in refused_digests for t in llm_tasks), refused=len(refused_digests))
    base.check("3: every LLM proposal has the request type the configuration fixes for its hypothesis",
               all(c["request_type"] == view["types"].get(c["hypothesis"]) for c in calls if c.get("hypothesis")),
               got=[(c.get("hypothesis"), c.get("request_type")) for c in calls if c.get("hypothesis")])
    llm_allowed = {c["hypothesis"] for c in calls if c.get("decision") == "ALLOW"}
    stopped = [c for c in calls if c["exit"] != 0 and "NO_ELIGIBLE_HYPOTHESIS" in (c.get("error") or "")]
    base.check("4: the loop exhausts the LLM-only hypotheses and stops at NO_ELIGIBLE_HYPOTHESIS",
               set(view["llm_only"]) <= llm_allowed and bool(stopped) and calls[-1]["exit"] != 0,
               llm_only=len(view["llm_only"]), allowed=sorted(llm_allowed), stopped_calls=[c["call"] for c in stopped])
    # ---------------------------------------------------------------- 6. memória = fonte
    rows = []
    for _p, env in s.results("stocks"):
        if env["outcome"]["status"] in ("RESULT", "DUPLICATE") and env.get("result"):
            code, shown = s.show(f"show {env['request_id']}", env["request_id"])
            payload = json.loads(env["result"]["payload_canonical"])
            rows.append({"request_id": env["request_id"], "same_bytes": code == 0 and shown.get("result_sha256")
                         == env["result"]["payload_sha256"], "states": {k: payload.get(k) for k in STATES}})
    facts_script = work / "facts.py"
    facts_script.write_text("import json,sys\nfrom cain.orchestration.store import OrchestrationStore\n"
                            "s=OrchestrationStore(sys.argv[1]);h=s.memory_head()\n"
                            "print(json.dumps([f['object'] for f in s.memory.facts(as_of=h,cubes=['stocks'])]))\n",
                            encoding="utf-8")
    _c, lines, _ = base.run("stocks facts", [os.environ["CAIN_PY"], "-I", facts_script, s.state], public_stdout="none")
    facts = {f.get("task_id"): f for f in lines[0]}
    envs = {env["task_id"]: env for _p, env in s.results("stocks")}
    state_ok = all({k: facts[t].get(k) for k in STATES} == {k: json.loads(envs[t]["result"]["payload_canonical"]).get(k)
                                                             for k in STATES}
                   for t in facts if t in envs and envs[t].get("result"))
    base.check("6: memory = authoritative source (payload == show re-read; fact states == payload states)",
               rows and all(r["same_bytes"] for r in rows) and state_ok, results=len(rows))
    # ---------------------------------------------------------------- 7. findings (D-26, 4c82885)
    fdb = work / "findings.sqlite"
    repo = Path.home() / "predictors/repos/stocks-predictor"
    base.run("findings ingest-state (4c82885)", [os.environ["CAIN_BIN"], "findings", "--db", fdb, "ingest-state",
                                                 "--domain", "stocks", "--repo", repo, "--commit", FINDINGS_SOURCE[0],
                                                 "--path", FINDINGS_SOURCE[1]], public_stdout="full")
    _c, lines, raw = base.run("findings check momentum 12-1", [os.environ["CAIN_BIN"], "findings", "--db", fdb, "check",
                                                               "--domain", "stocks", "--statement",
                                                               "momentum 12-1 cross-sectional long-only B3",
                                                               "--as-of", after()], public_stdout="full")
    try:  # the CLI prints indented JSON (several lines)
        verdict = json.loads(raw)
    except ValueError:
        verdict = {}
    text = json.dumps(verdict).lower()
    base.check("7: `momentum 12-1` recognized as closed by findings check",
               bool(verdict) and ("momentum" in text) and bool(verdict.get("equivalent") or verdict.get("matches")
                                                              or verdict.get("same_identity")),
               verdict={k: verdict.get(k) for k in list(verdict)[:6]})
    # ---------------------------------------------------------------- 8. linter
    _c, _l, show_raw = s.run("show seed (private evidence file)", [s.bin["RESEARCH_BIN"], "--state", s.dstate, "show",
                                                                   "stocks:REQ-SU-SEED"])
    show_file = work / "seed-show.json"
    show_file.write_text(show_raw, encoding="utf-8")
    cdb = work / "claims.sqlite"
    doc = json.loads(subprocess.run([os.environ["CAIN_BIN"], "memory", "--db", cdb, "add-document", "--cube", "stocks",
                                     "--title", "stocks-research show seed", "--published-at", now(), "--source",
                                     "stocks-research show stocks:REQ-SU-SEED", "--file", show_file],
                                    capture_output=True, text=True).stdout)
    doc_id = doc.get("id") or doc.get("document_id")
    # the literal quote as it appears in the `show` text: a scalar number or a flat list of numbers
    quotes = {k: re.search(rf'"{k}":\s*(\[[^\]\n]*\]|[-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?)', show_raw) for k in
              ("excess_net_bps", "periods", "excess_net_ci_bps", "confidence")}
    ev = {}
    for k, m in quotes.items():
        if m:
            q = m.group(0)
            r = json.loads(subprocess.run([os.environ["CAIN_BIN"], "claims", "--db", cdb, "add-evidence", "--cube", "stocks",
                                           "--document-id", str(doc_id), "--start", str(m.start()), "--end", str(m.end()),
                                           "--quote", q], capture_output=True, text=True).stdout or "{}")
            ev[k] = {"id": r.get("id") or r.get("evidence_id"), "value": json.loads(m.group(1))}
    have = all(ev.get(k, {}).get("id") for k in quotes)
    lint = {}
    if have:
        x, n, ci, conf = (ev[k]["value"] for k in ("excess_net_bps", "periods", "excess_net_ci_bps", "confidence"))
        e = {k: ev[k]["id"] for k in ev}
        pct = f"{round(conf * 100)}%"
        reports = {
            "A": (f"O `momentum 12-1` real teve excesso líquido de {x} bps por período [ev:{e['excess_net_bps']}], em {n} "
                  f"períodos [ev:{e['periods']}]. O intervalo de {pct} [ev:{e['confidence']}] foi de {ci[0]} a {ci[1]} bps "
                  f"[ev:{e['excess_net_ci_bps']}].\n", "publishable"),
            "A0": (f"O momentum 12-1 real teve excesso líquido de {x} bps por período [ev:{e['excess_net_bps']}].\n", "blocked"),
            "B": ("O `momentum 12-1` teve Sharpe 1,8 no período.\n", "blocked"),
            "C": (f"O `momentum 12-1` real teve excesso líquido de {x + 63} bps por período [ev:{e['excess_net_bps']}].\n",
                  "blocked"),
            "E": (f"O `momentum 12-1` real teve excesso líquido de `{x}` bps por período.\n", "blocked"),
        }
        for name, (text_, expected) in reports.items():
            path = work / f"report-{name}.md"
            path.write_text(text_, encoding="utf-8")
            r = subprocess.run([os.environ["CAIN_BIN"], "claims", "--db", cdb, "lint", "--as-of", after(), "--cube", "stocks",
                                path], capture_output=True, text=True)
            got = json.loads(r.stdout or "{}")
            verdict_ = "publishable" if got.get("publishable") or (r.returncode == 0 and not got.get("violations")) else "blocked"
            lint[name] = {"expected": expected, "got": verdict_, "exit": r.returncode,
                          "violations": [v.get("code") for v in got.get("violations", [])]}
    base.check("8: honest report publishable; A0, B, C and E blocked",
               have and all(v["expected"] == v["got"] for v in lint.values()), lint=lint, evidence=sorted(ev))
    # ---------------------------------------------------------------- 9. refusal_mismatches
    refused_h = {by_task[t]["hypothesis_id"] for t, k in view["classes"].items() if k == "TERMINAL_REFUSAL" and t in by_task}
    claim = re.compile(r"\b(?:recusad[ao]s?|rejeitad[ao]s?|refused|rejected)\b", re.I)
    audited = []
    for c in calls:
        if c.get("rationale") and claim.search(c["rationale"]):
            named = {h for h in view["proposable"] if h.split(":", 1)[1] in c["rationale"]}
            false_claim = bool(named) and not named & refused_h
            flagged = bool((c.get("rationale_check") or {}).get("refusal_mismatches"))
            audited.append({"call": c["call"], "false_claim": false_claim, "flagged": flagged})
    base.check("9: refusal_mismatches flags every false refusal claim that appeared",
               all(a["flagged"] for a in audited if a["false_claim"]), audited=audited)
    return base.finish({"calls": [{k: c.get(k) for k in ("call", "exit", "hypothesis", "request_type", "decision",
                                                          "reason_code", "domain", "error")} for c in calls],
                        "guards": guard_rows, "lint": lint, "refusal_audit": audited})


if __name__ == "__main__":
    raise SystemExit(main())
