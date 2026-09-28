"""Teste conjunto do ecossistema (não é gate da integration-brasileirao): os três domínios reais no mesmo estado do CAIN.

Pedido do dono no chat da sessão cripto (2026-09-28), lista de conferências combinada com as sessões cripto e STOCKS;
roda no PC 2 pelo runtime integrado desta missão (runtime_env.sh INTEGRATED=1: cain 0.4.13rc12, consumidores do
Brasileirão, do cripto e do stocks, cada um com a sua wheel publicada, transporte 0.1.0rc5, protocolo 2.0.0rc2, Core
3.2.1, Ops 4.2.2rc1). Regras: D-25 (Brasileirão: dado real só no PC 2, diretório privado, holdout 2025 lacrado), D-23
(cripto: só as cópias públicas conferidas / build_real_dataset da Etapa A), D-24 (stocks: pin novo das fontes públicas,
wheel 0.3.0rc3, as_of pelo marcador → data_cutoff do painel do run, nada de 61fc017..main). Saída pública só com IDs,
estados e hashes; no_data_rows_check em toda ela (run_scenario.sh).

 1. identidade do stack: cada wheel com o sha256 publicado; Core/Ops pelos hashes do uv.lock; venv do CAIN sem domínio,
    cada consumidor só com o seu;
 2. um estado do CAIN, três orquestrações, um ciclo ALLOW real por domínio; payload == releitura autoritativa (show);
 3. entrega cruzada: resultado de X no inbox de Y → DOMAIN_MISMATCH sem fato; task de X no consumidor de Y → recusada,
    estado do domínio Y igual (sha256 antes e depois);
 4. o mesmo H9 nos três: task_id/episode_id distintos, hypothesis_id qualificado (protocolo); proposta de X em Y → R01;
    a H9 fechada onde a config fecha → R05;
 5. memória: fatos só no cubo do domínio, o view de cada domínio não vê os outros, memória intact;
 6. metrics só nos fatos do cripto, iguais ao que result_metrics lê do payload; stocks e brasileirao sem metrics;
 7. receipts: policy.code_sha256 igual nos três; config.sha256 == digest da config empacotada, distinto entre os três;
 8. os três consumidores em paralelo, dispatch e ingest intercalados: uma task por pedido, um experimento por pedido,
    nenhum resultado perdido;
 9. R16 do Brasileirão (pedidos de 2025 → REQUIRE_HUMAN, nunca despachados) e R15 do cripto (QUAL-SHADOW-001 recusada
    pelo domínio, depois REQUIRE_HUMAN);
10. LLM (opcional, modelo local): cripto e stocks chegam a uma decisão; brasileirao NO_ELIGIBLE_HYPOTHESIS (IB-F009);
11. nenhum capital_permission true no estado, no spool nem nos receipts.
Uso (env.sh do runtime integrado; SOAK_OLLAMA_URL/SOAK_OLLAMA_MODEL opcionais):
python ecosystem_joint.py <qualification/integration-brasileirao> <work> <out>
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from harness import Harness, now
from isolation import PROBE

DOMAINS = ("brasileirao", "crypto", "stocks")
PKG = {"brasileirao": "brasileirao-predictor", "crypto": "cripto-predictor", "stocks": "stocks-predictor"}
VENV = {"brasileirao": "consumer-venv", "crypto": "crypto-venv", "stocks": "stocks-venv"}
MEMORY = r'''
import json, sys
from cain.orchestration import config as dc
from cain.orchestration.store import OrchestrationStore
from research_protocol import v2
state, as_of = sys.argv[1], sys.argv[2]
store = OrchestrationStore(state)
head = store.memory_head()
out = {"verify": store.memory.verify()["status"], "cubes": {}, "views": {}, "metrics": {}, "receipts": {}, "configs": {}}
import sqlite3
db = sqlite3.connect(f"file:{state}/orchestration.sqlite?mode=ro", uri=True)
inbox = {r[0]: r[1] for r in db.execute("select task_id, raw from inbox where class='TERMINAL_RESULT'")}
for d in ("brasileirao", "crypto", "stocks"):
    facts = store.memory.facts(as_of=head, cubes=[d])
    out["cubes"][d] = sorted({f["subject"] for f in facts})
    cfg = dc.load(d)
    out["configs"][d] = dc.digest(cfg)
    rows = []
    for f in facts:
        o = f["object"]
        raw = inbox.get(o.get("task_id"))
        expected = {}
        if raw:
            body = json.loads(raw).get("result") or {}
            payload = json.loads(body.get("payload_canonical") or "{}")
            expected = dc.result_metrics(cfg, payload)
        rows.append({"task_id": o.get("task_id"), "metrics": o.get("metrics"), "expected": expected})
    out["metrics"][d] = rows
    with store.db() as con:
        view = store.view(con, d, as_of)
    out["views"][d] = sorted({r["hypothesis_id"].split(":")[0] for r in view["results"]}
                             | {t["hypothesis_id"].split(":")[0] for t in view["tasks"]})
    out["receipts"][d] = [{"decision": json.loads(r[0])["decision"], "policy": json.loads(r[0])["policy"],
                           "config": json.loads(r[0])["config"], "capital_permission": json.loads(r[0]).get("capital_permission")}
                          for r in db.execute("select receipt from episodes where domain=?", (d,))]
print(json.dumps(out, sort_keys=True))
'''


def sha_tree(path: Path) -> str:
    h = hashlib.sha256()
    for p in sorted(path.rglob("*")):
        if p.is_file():
            h.update(p.relative_to(path).as_posix().encode() + b"\0" + p.read_bytes())
    return h.hexdigest()


def main() -> int:
    mission, work, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    priv = Path(os.environ["CAIN_BIN"]).parents[2]
    targets = json.loads((mission / "runtime_targets.json").read_text(encoding="utf-8"))
    h = Harness(out, work / "shared", mission, "ecosystem-joint")
    side = {"brasileirao": h, "crypto": h.for_domain("crypto"), "stocks": h.for_domain("stocks")}
    props = work / "proposals"
    props.mkdir(parents=True, exist_ok=True)
    fixtures = mission.parent / "integration-crypto" / "fixtures" / "v2"
    crypto_props = mission.parent / "integration-crypto" / "fixtures" / "proposals"
    # ---------------------------------------------------------------- 1. identidade do stack
    wheels = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (priv / "wheels").glob("*.whl")}
    expected = {Path(targets[k]["url"]).name: targets[k]["sha256"]
                for k in ("cain", "brasileirao", "transport", "protocol", "cripto", "stocks")}
    h.check("1: every final wheel installed has the published sha256",
            all(wheels.get(n) == s for n, s in expected.items()), wheels={n: wheels.get(n, "")[:12] for n in expected})
    for d in DOMAINS:
        # uv export: "predictor-core @ <release url>" followed by its --hash lines
        req = (priv / f"{VENV[d]}.req.txt").read_text(encoding="utf-8")
        core = re.search(r"predictor-core @ \S*/predictor_core-3\.2\.1-py3-none-any\.whl[^@]*?--hash=sha256:10ef42f3",
                         req, re.S)
        ops = re.search(r"predictor-ops @ \S*/predictor_ops-4\.2\.2rc1-py3-none-any\.whl[^@]*?--hash=sha256:0be70bfb",
                        req, re.S)
        h.check(f"1: {d} consumer requirements pin Core 3.2.1 (10ef42f3…) and Ops 4.2.2rc1 (0be70bfb…) by hash",
                bool(core) and bool(ops))
    # what is really installed: the Name of every *.dist-info/METADATA in each venv's site-packages (read now), cross-
    # checked against the `uv pip freeze` that runtime_env.sh wrote when it built the venv (the uv venvs have no pip)
    freeze_file = {"cain-venv": "cain", "consumer-venv": "consumer", "crypto-venv": "crypto", "stocks-venv": "stocks"}
    freeze, uv_freeze = {}, {}
    for venv, name in freeze_file.items():
        site = next((priv / venv / "lib").glob("python3.*/site-packages"))
        names = set()
        for meta in site.glob("*.dist-info/METADATA"):
            m = re.search(r"^Name: (.+)$", meta.read_text(encoding="utf-8", errors="replace"), re.M)
            if m:
                names.add(re.sub(r"[-_.]+", "-", m.group(1).strip()).lower())
        freeze[venv] = names
        raw = (out.parent / f"pip_freeze_{name}.txt").read_text(encoding="utf-8")
        uv_freeze[venv] = {re.sub(r"[-_.]+", "-", re.split(r"==| @ ", line)[0].strip()).lower()
                           for line in raw.splitlines() if line.strip() and not line.startswith("#")}
    h.check("1: installed distributions read from each venv's dist-info (not empty) and equal to its uv pip freeze",
            all(freeze[v] and freeze[v] == uv_freeze[v] for v in freeze),
            sizes={k: len(v) for k, v in freeze.items()},
            differences={k: sorted(freeze[k] ^ uv_freeze[k]) for k in freeze if freeze[k] != uv_freeze[k]})
    h.check("1: the CAIN venv has no domain package", not freeze["cain-venv"] & set(PKG.values()),
            cain=sorted(freeze["cain-venv"] & set(PKG.values())))
    for d in DOMAINS:
        h.check(f"1: the {d} consumer venv has only its own domain",
                freeze[VENV[d]] & set(PKG.values()) == {PKG[d]}, got=sorted(freeze[VENV[d]] & set(PKG.values())))
    # ---------------------------------------------------------------- 2. um ciclo ALLOW real por domínio
    proposals = {
        "brasileirao": h.proposal_path("fixtures/proposals/e2e/01-allow.json", props / "br-01.json",
                                       "cain:ECO-BR-01", request_id="brasileirao:REQ-ECO-001"),
        "crypto": h.integrated_proposal("crypto", "fixtures/proposals/e2e/01-allow.json", props / "cr-01.json",
                                        "cain:ECO-CRYPTO-01", request_id="crypto:REQ-ECO-001"),
        "stocks": h.integrated_proposal("stocks", "fixtures/proposals/e2e/01-allow.json", props / "st-01.json",
                                        "cain:ECO-STOCKS-01", request_id="stocks:REQ-ECO-001"),
    }
    real = {}
    for d in DOMAINS:
        x = side[d]
        _c, lines, _ = x.propose(f"{d}: propose", proposals[d])
        h.check(f"2: {d} real proposal ALLOW", bool(lines) and lines[0].get("decision") == "ALLOW",
                got={k: lines[0].get(k) for k in ("decision", "reason_code", "rule")} if lines else None)
        x.dispatch(f"{d}: dispatch"); x.consumer(f"{d}: consumer"); x.ingest(f"{d}: ingest")
        res = x.results(d)
        ok = len(res) == 1 and res[0][1]["outcome"]["status"] == "RESULT"
        h.check(f"2: {d} one real RESULT ingested", ok, got=[r["outcome"]["status"] for _p, r in res])
        if ok:
            real[d] = res[0]
            code, shown = x.show(f"{d}: show", res[0][1]["request_id"])
            h.check(f"2: {d} payload == authoritative re-read of the domain (show, new process)",
                    code == 0 and shown.get("result_sha256") == res[0][1]["result"]["payload_sha256"],
                    payload_sha256=res[0][1]["result"]["payload_sha256"], show=shown.get("result_sha256"))
    # ---------------------------------------------------------------- 3. entrega cruzada nos dois sentidos
    for y in DOMAINS:
        for x_ in DOMAINS:
            if x_ != y and x_ in real:
                shutil.copy(real[x_][0], h.spool / y / "results" / f"cross-{x_}.json")
        _c, lines, _ = side[y].ingest(f"{y}: ingest the real results of the other domains")
        rejected = {l["file"]: l.get("code") for l in lines if l.get("action") == "rejected"}
        h.check(f"3: real results of the other domains in the {y} inbox → DOMAIN_MISMATCH, no fact",
                rejected == {f"cross-{x_}.json": "DOMAIN_MISMATCH" for x_ in DOMAINS if x_ != y and x_ in real},
                got=rejected)
    for y in DOMAINS:
        before = sha_tree(side[y].dstate)
        for x_ in DOMAINS:
            if x_ != y:
                task = next((h.spool / x_ / "tasks").glob("TASK-*.json"))
                shutil.copy(task, h.spool / y / "tasks" / f"cross-{x_}-{task.name}")
        _c, lines, _ = side[y].consumer(f"{y}: consumer with the other domains' tasks")
        refused = [l for l in lines if l.get("action") == "rejected" and l.get("code") == "DOMAIN_MISMATCH"]
        h.check(f"3: tasks of the other domains in the {y} consumer → refused; {y} domain state unchanged",
                len(refused) == 2 and sha_tree(side[y].dstate) == before,
                refused=len(refused), state_unchanged=sha_tree(side[y].dstate) == before)
    # ---------------------------------------------------------------- 4. o mesmo H9 nos três
    probe = work / "probe.py"
    probe.write_text(PROBE, encoding="utf-8")
    _c, lines, _ = h.run("protocol probe (same H9)", [os.environ["CAIN_PY"], "-I", probe, fixtures], public_stdout="full")
    got = lines[0]
    h.check("4: same H9 in the three domains: distinct task_id and episode_id, qualified hypothesis_id",
            len(set(got["task_ids"].values())) == 3 and len(set(got["episode_ids"].values())) == 3
            and sorted(got["hypothesis_ids"].values()) == ["brasileirao:H9", "crypto:H9", "stocks:H9"])
    h9 = {"crypto": crypto_props / "e2e" / "05-h9-closed.json",
          "stocks": mission.parent / "integration-stocks" / "fixtures/proposals/n1/04-stocks-h9.json",
          "brasileirao": mission / "fixtures/proposals/n1/04-brasileirao-h9.json"}
    got = {}
    for owner, path in h9.items():
        for orch in DOMAINS:
            _c, lines, _ = side[orch].propose(f"4: {owner}:H9 -> {orch}", path)
            got[f"{owner}->{orch}"] = (lines[0].get("decision"), lines[0].get("rule"), lines[0].get("task"))
    h.check("4: proposal of X in Y → BLOCK R01; closed H9 in its own orchestration → BLOCK R05; no task",
            got == {f"{o}->{t}": ("BLOCK", "R05" if o == t else "R01", None) for o in DOMAINS for t in DOMAINS}, got=got)
    # ---------------------------------------------------------------- 8. consumidores em paralelo
    second = {
        "brasileirao": h.proposal_path("fixtures/proposals/e2e/01-allow.json", props / "br-02.json",
                                       "cain:ECO-BR-02", request_id="brasileirao:REQ-ECO-002", season=2023,
                                       events={"kickoff_from": "2023-07-01T00:00:00Z",
                                               "kickoff_to": "2023-10-01T00:00:00Z"}),
    }
    cr = json.loads((mission.parent / "integration-crypto/fixtures/proposals/e2e/01-allow.json").read_text())["request"]
    second["crypto"] = h.integrated_proposal("crypto", "fixtures/proposals/e2e/01-allow.json", props / "cr-02.json",
                                             "cain:ECO-CRYPTO-02", request_id="crypto:REQ-ECO-002",
                                             hypothesis_id="crypto:QUAL-SHADOW-REAL-002",
                                             parameters=dict(cr["parameters"], placebo_seed=3002))
    st = json.loads((mission.parent / "integration-stocks/fixtures/proposals/e2e/01-allow.json").read_text())["request"]
    second["stocks"] = h.integrated_proposal("stocks", "fixtures/proposals/e2e/01-allow.json", props / "st-02.json",
                                             "cain:ECO-STOCKS-02", request_id="stocks:REQ-ECO-002",
                                             hypothesis_id="stocks:QUAL-PIT-MOM-REAL-002",
                                             parameters=dict(st["parameters"], max_securities=st["parameters"]["max_securities"] - 1))
    for d in DOMAINS:
        _c, lines, _ = side[d].propose(f"8: {d} second proposal", second[d])
        h.check(f"8: {d} second real proposal ALLOW", bool(lines) and lines[0].get("decision") == "ALLOW",
                got={k: lines[0].get(k) for k in ("decision", "reason_code", "rule")} if lines else None)
        side[d].dispatch(f"8: {d} dispatch")
    with ThreadPoolExecutor(max_workers=3) as pool:
        codes = list(pool.map(lambda d: side[d].consumer(f"8: {d} consumer (parallel)")[0], DOMAINS))
    h.check("8: the three consumers ran in parallel without error", codes == [0, 0, 0], exits=codes)
    for d in DOMAINS:
        side[d].ingest(f"8: {d} ingest")
    for d in DOMAINS:
        x = side[d]
        results = [r for _p, r in x.results(d)]
        tasks = list((h.spool / d / "tasks").glob("TASK-*.json"))
        journal = next(x.dstate.rglob("journal.sqlite"), None)
        per_request = None
        if journal:
            with x.ro(journal) as db:
                per_request = db.execute("SELECT max(c), count(*) FROM (SELECT count(*) c FROM experiments "
                                         "GROUP BY request_id)").fetchone()
        h.check(f"8: {d}: one task per request, one experiment per request, no result lost",
                len(tasks) == 2 and len({r["task_id"] for r in results if r["outcome"]["status"] == "RESULT"}) == 2
                and (per_request is None or per_request[0] == 1),
                tasks=len(tasks), results=len(results), experiments_per_request=per_request and per_request[0])
    # ---------------------------------------------------------------- 9. R16 do Brasileirão e R15 do cripto
    for rel in sorted((mission / "fixtures/proposals/holdout").glob("*.json")):
        _c, lines, _ = h.propose(f"9: holdout {rel.stem}", rel)
        h.check(f"9: brasileirao {rel.stem} → REQUIRE_HUMAN SEALED_SCOPE (R16), no task",
                (lines[0].get("decision"), lines[0].get("reason_code"), lines[0].get("task")) ==
                ("REQUIRE_HUMAN", "SEALED_SCOPE", None), got={k: lines[0].get(k) for k in ("decision", "reason_code")})
    x = side["crypto"]
    shadow = h.integrated_proposal("crypto", "fixtures/proposals/e2e/01-allow.json", props / "cr-shadow.json",
                                   "cain:ECO-CRYPTO-SHADOW", request_id="crypto:REQ-ECO-SHADOW",
                                   hypothesis_id="crypto:QUAL-SHADOW-001",
                                   parameters=dict(cr["parameters"], placebo_seed=3099))
    _c, first, _ = x.propose("9: crypto QUAL-SHADOW-001", shadow)
    x.dispatch("9: crypto dispatch shadow"); _c, cons, _ = x.consumer("9: crypto consumer shadow"); x.ingest("9: ingest")
    again = h.integrated_proposal("crypto", "fixtures/proposals/e2e/01-allow.json", props / "cr-shadow-2.json",
                                  "cain:ECO-CRYPTO-SHADOW-2", request_id="crypto:REQ-ECO-SHADOW-2",
                                  hypothesis_id="crypto:QUAL-SHADOW-001",
                                  parameters=dict(cr["parameters"], placebo_seed=3100))
    _c, second_try, _ = x.propose("9: crypto QUAL-SHADOW-001 again", again)
    # R15 fires only after the domain refused the hypothesis with HYPOTHESIS_NOT_ADMITTED (recorded in the CAIN)
    h.check("9: crypto QUAL-SHADOW-001 refused by the domain (REJECTED), then REQUIRE_HUMAN (R15)",
            first[0].get("decision") == "ALLOW" and any(l.get("status") == "REJECTED" for l in cons)
            and (second_try[0].get("decision"), second_try[0].get("rule"), second_try[0].get("reason_code"))
            == ("REQUIRE_HUMAN", "R15", "HYPOTHESIS_NOT_ADMITTED_BY_DOMAIN"),
            first=first[0].get("decision"), again={k: second_try[0].get(k) for k in ("decision", "reason_code", "rule")})
    # ---------------------------------------------------------------- 10. LLM (opcional)
    url, model = os.environ.get("SOAK_OLLAMA_URL"), os.environ.get("SOAK_OLLAMA_MODEL")
    llm = {}
    if url and model:
        cfg = work / "cain-llm.toml"
        cfg.write_text("\n".join(["[llm]", 'provider = "ollama"', f'model = "{model}"', f'base_url = "{url}"',
                                  "temperature = 0.0", "seed = 42", "timeout = 600.0", "num_ctx = 8192",
                                  "num_predict = 256", "max_input_bytes = 16000", "think = false", ""]), encoding="utf-8")
        for d in DOMAINS:
            out_file = props / f"llm-{d}.json"
            code, lines, _ = h.cain(f"10: llm {d}", "explain", "proximo experimento", "--propose-for-domain", d,
                                    "--state", h.state, "--proposal-out", out_file, "--proposal-id", f"cain:ECO-LLM-{d}",
                                    "--config", cfg)
            decision = None
            if code == 0 and out_file.exists():
                _c, dl, _ = side[d].propose(f"10: propose llm {d}", out_file)
                decision = dl[0].get("decision") if dl else None
            llm[d] = {"exit": code, "decision": decision, "error": (lines[0].get("detail", "")[:60] if lines else None)}
        h.check("10: LLM: crypto and stocks reach a decision; brasileirao NO_ELIGIBLE_HYPOTHESIS (IB-F009)",
                bool(llm["crypto"]["decision"]) and bool(llm["stocks"]["decision"])
                and "NO_ELIGIBLE_HYPOTHESIS" in (llm["brasileirao"]["error"] or ""), got=llm)
    # ---------------------------------------------------------------- 5, 6, 7 e 11
    script = work / "memory.py"
    script.write_text(MEMORY, encoding="utf-8")
    _c, lines, _ = h.run("memory, views, metrics and receipts", [os.environ["CAIN_PY"], "-I", script, h.state, now()],
                         public_stdout="none")
    mem = lines[0]
    h.check("5: facts only in the domain's own cube; memory intact", mem["verify"] == "intact" and all(
        mem["cubes"][d] and all(s.startswith(f"{d}:") for s in mem["cubes"][d]) for d in DOMAINS),
            cubes={d: len(v) for d, v in mem["cubes"].items()})
    h.check("5: the view of each domain sees only its own domain", all(mem["views"][d] == [d] for d in DOMAINS),
            views=mem["views"])
    crypto_rows = [r for r in mem["metrics"]["crypto"] if r["expected"]]
    h.check("6: metrics only in crypto facts, equal to what result_metrics reads from the payload",
            bool(crypto_rows) and all(r["metrics"] == r["expected"] for r in crypto_rows)
            and all(r["metrics"] is None for d in ("brasileirao", "stocks") for r in mem["metrics"][d]),
            crypto_facts_with_metrics=len(crypto_rows))
    codes = {r["policy"]["code_sha256"] for d in DOMAINS for r in mem["receipts"][d]}
    cfgs = {d: {r["config"]["sha256"] for r in mem["receipts"][d]} for d in DOMAINS}
    h.check("7: policy.code_sha256 equal in the three; config.sha256 == digest of the packaged config, distinct",
            len(codes) == 1 and all(cfgs[d] == {mem["configs"][d]} for d in DOMAINS)
            and len({mem["configs"][d] for d in DOMAINS}) == 3,
            policy=sorted(codes), configs={d: mem["configs"][d][:12] for d in DOMAINS})
    # ---------------------------------------------------------------- 12. Core/Ops em cada domínio
    for d in DOMAINS:
        x = side[d]
        payloads = [json.loads(r["result"]["payload_canonical"]) for _p, r in x.results(d)
                    if r["outcome"]["status"] == "RESULT" and r.get("result")]
        h.check(f"12: every {d} RESULT carries non-empty core_facts and ops_facts (admission → Ops → Core ran)",
                bool(payloads) and all(p.get("core_facts") and p.get("ops_facts") and p["ops_facts"].get("ops_run_id")
                                       for p in payloads), results=len(payloads))
        with x.ro(x.dstate / "admission.sqlite") as db:
            admitted = db.execute("SELECT count(DISTINCT request_id) FROM admissions WHERE decision='ACCEPTED'").fetchone()[0]
        with x.ro(x.dstate / "x" / "journal.sqlite") as db:
            per = db.execute("SELECT count(*), max(c) FROM (SELECT count(*) c FROM experiments GROUP BY request_id)").fetchone()
        h.check(f"12: {d} Ops journal: exactly one experiment per admitted request",
                per[0] == admitted and per[1] == 1, admitted=admitted, requests_with_experiments=per[0], max_per_request=per[1])
    lock = {}
    core_ops = {"predictor-core": ("3.2.1", "10ef42f34ace8bb2df5f83ff7de2ceec79b035a25ea0a690e8942bd60d2fb4e3",
                                   "https://github.com/leonardosovienski/core-predictor/releases/download/v3.2.1/"
                                   "predictor_core-3.2.1-py3-none-any.whl"),
                "predictor-ops": ("4.2.2rc1", "0be70bfbb2437dfb080baceb9af41043a09d03b15a358903b8bd7007f5f169b3",
                                  "https://github.com/leonardosovienski/predictor-ops/releases/download/v4.2.2rc1/"
                                  "predictor_ops-4.2.2rc1-py3-none-any.whl")}
    import urllib.request
    import zipfile
    for name, (version, digest, url) in core_ops.items():
        dest = priv / "wheels" / Path(url).name
        if not dest.exists():
            urllib.request.urlretrieve(url, dest)
        raw = dest.read_bytes()
        ok_sha = hashlib.sha256(raw).hexdigest() == digest
        with zipfile.ZipFile(dest) as z:
            record = next(n for n in z.namelist() if n.endswith(".dist-info/RECORD"))
            wheel_lines = {l for l in z.read(record).decode().splitlines() if l and not l.startswith(record)}
        lock[name] = {"wheel_sha256_ok": ok_sha}
        for d in DOMAINS:
            site = next((priv / VENV[d] / "lib").glob("python3.*/site-packages"))
            installed = site / Path(record)
            lines = set(installed.read_text(encoding="utf-8").splitlines()) if installed.exists() else set()
            h.check(f"12: {d} venv: installed {name} {version} is the published wheel (sha256 {digest[:8]}…; every "
                    "file of the wheel's RECORD, with its hash, in the installed RECORD)",
                    ok_sha and bool(wheel_lines) and wheel_lines <= lines, missing=len(wheel_lines - lines))
    # ---------------------------------------------------------------- 13. disputa da trava do Ops (SHARED-005)
    reps = int(os.environ.get("ECO_LOCK_REPS", "20"))
    # in-season windows only (a January–April window has few or no Série A games and the domain refuses it)
    windows = [(s, a, b, t) for s in (2021, 2022, 2023, 2024) for a, b in (("05", "08"), ("06", "09"), ("08", "11"))
               for t in ("1X2", "OU25")]
    lock_rows = {d: [] for d in DOMAINS}
    for d in DOMAINS:
        for i in range(1, reps + 1):
            k = Harness(out / "lock-contention", work / "lock" / d / f"{i:02d}", mission, f"lock-{d}")
            kd = k if d == "brasileirao" else k.for_domain(d)
            if d == "brasileirao":
                season, start, end, target = windows[(i - 1) % len(windows)]
                path = k.proposal_path("fixtures/proposals/e2e/01-allow.json", props / f"lock-br-{i:02d}.json",
                                       f"cain:ECO-LOCK-BR-{i:02d}", request_id=f"brasileirao:REQ-ECO-LOCK-{i:03d}",
                                       hypothesis_id=f"brasileirao:QUAL-SOAK-{(i - 1) % 24 + 1:03d}", season=season,
                                       target=target, events={"kickoff_from": f"{season}-{start}-01T00:00:00Z",
                                                              "kickoff_to": f"{season}-{end}-01T00:00:00Z"})
            elif d == "crypto":
                path = k.integrated_proposal("crypto", "fixtures/proposals/e2e/01-allow.json", props / f"lock-cr-{i:02d}.json",
                                             f"cain:ECO-LOCK-CR-{i:02d}", request_id=f"crypto:REQ-ECO-LOCK-{i:03d}",
                                             parameters=dict(cr["parameters"], placebo_seed=4000 + i))
            else:
                path = k.integrated_proposal("stocks", "fixtures/proposals/e2e/01-allow.json", props / f"lock-st-{i:02d}.json",
                                             f"cain:ECO-LOCK-ST-{i:02d}", request_id=f"stocks:REQ-ECO-LOCK-{i:03d}",
                                             parameters=dict(st["parameters"], max_securities=st["parameters"]["max_securities"] - 10 - i))
            _c, lines, _ = kd.propose(f"13: {d} {i} propose", path)
            if not lines or lines[0].get("decision") != "ALLOW":
                lock_rows[d].append({"rep": i, "allow": False})
                continue
            kd.dispatch(f"13: {d} {i} dispatch")
            with ThreadPoolExecutor(max_workers=2) as pool:
                runs = list(pool.map(lambda n, kd=kd, d=d, i=i: kd.consumer(f"13: {d} {i} consumer {n}"), (1, 2)))
            exits = [r[0] for r in runs]
            text = "".join(r[2] for r in runs)
            with kd.ro(kd.dstate / "x" / "journal.sqlite") as db:
                experiments = db.execute("SELECT count(*) FROM experiments").fetchone()[0]
            # every V2 result line the two consumers printed for this task (the loser may publish a non-terminal
            # OPS_FAILED_RETRYABLE for a task the winner completed: recorded, not a failure — cripto session, rc12)
            statuses = sorted(l.get("status") for r in runs for l in r[1] if l.get("status") and l.get("action") != "skipped")
            # the loser's publication: whatever is not the single RESULT (none, OPS_FAILED_RETRYABLE,
            # RECONCILIATION_REQUIRED, …); a process "died" if it exited non-zero or raised PermissionError
            rest = list(statuses)
            if "RESULT" in rest:
                rest.remove("RESULT")
            busy = sum(l.get("action") == "busy" and l.get("code") == "CONSUMER_BUSY" for r in runs for l in r[1])
            # transport ≥ 0.1.0rc6 (ecosystem-predictor#36): one consumer per domain; the loser exits 6 with one
            # "busy" line and publishes nothing. Exit 6 with that line is not a death.
            lock_rows[d].append({"rep": i, "allow": True, "exits": sorted(exits), "busy": busy,
                                 "experiments": experiments, "statuses": statuses,
                                 "loser_published": rest[0] if rest else "none",
                                 "died": any(e not in (0, 6) for e in exits) or "PermissionError" in text,
                                 "permission_error": "PermissionError" in text})

        def good(r):
            # exactly one delivery (RESULT) and one busy consumer that published nothing, one experiment
            return (r["allow"] and r["exits"] == [0, 6] and r["busy"] == 1 and not r["permission_error"]
                    and r["experiments"] == 1 and r["statuses"] == ["RESULT"])

        rows = lock_rows[d]
        h.check(f"13: {d}: {reps} races of two consumers on the same spool/ledger/state: one delivers (exit 0, one "
                "RESULT), the other is busy (exit 6, CONSUMER_BUSY) and publishes nothing; one experiment per task; no "
                "death, no PermissionError",
                len(rows) == reps and all(good(r) for r in rows), reps=len(rows),
                failures=[r for r in rows if not good(r)],
                loser_published={s: sum(r.get("loser_published") == s for r in rows)
                                 for s in sorted({r.get("loser_published") for r in rows if r["allow"]})},
                died=sum(bool(r.get("died")) for r in rows))
    capital = [r for d in DOMAINS for r in mem["receipts"][d] if r.get("capital_permission") not in (False, None)]
    files = [p for p in list(h.state.iterdir()) + list(h.spool.rglob("*.json")) if p.is_file()]
    h.check("11: no capital_permission true in state, spool or receipts", not capital and all(
        b'"capital_permission":true' not in p.read_bytes().replace(b" ", b"") for p in files))
    return h.finish({"llm": llm, "memory": {"cubes": {d: len(v) for d, v in mem["cubes"].items()},
                                            "configs": mem["configs"], "policy": sorted(codes)},
                     "core_ops_wheels": lock, "lock_contention": lock_rows})


if __name__ == "__main__":
    raise SystemExit(main())
