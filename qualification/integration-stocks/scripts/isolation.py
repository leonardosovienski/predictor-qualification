"""integration-stocks, fase isolation-ids-contradiction (CROSS_DOMAIN_ISOLATION, DOMAIN_QUALIFIED_IDS,
CONTRADICTION_PRESERVATION).

Pelos entrypoints do CAIN e dos consumidores (runtime suportado) e pelo protocolo congelado instalado no venv do CAIN:
  1. envelope: resultado de cada domínio contra a task de cada domínio (fixtures V2 congeladas da integration-crypto):
     só o próprio domínio é aceito; o mesmo H9 nos três domínios gera tasks, episódios e IDs distintos; ID sem domínio é
     recusado;
  2. contra o cripto pelo runtime integrado (prompt do Stocks §4): UM estado do CAIN com as duas orquestrações; um ciclo
     real de cada domínio; o resultado real de cada um entregue no spool do outro é recusado (DOMAIN_MISMATCH); a task
     do cripto no spool do consumidor do Stocks é recusada sem chamar o domínio; o mesmo H9 é bloqueado em cada
     orquestração pelo motivo certo; a memória fica separada por cubo (nenhum fato de um domínio no cubo do outro);
  3. contra o brasileirao por fixtures V2 congeladas: resultado e proposta recusados; proposta do stocks na
     orquestração do brasileirao é BLOCK DOMAIN_MISMATCH, sem task; domínio fora do protocolo sem orquestração
     (CONFIG_INVALID) e sem efeito (ciclo 2, cain 0.4.13rc10+: os três domínios têm configuração, como na
     integration-crypto);
  4. contradição: SUPPORTED × REFUTED da mesma hipótese do Stocks → REQUIRE_HUMAN; os dois fatos ficam na memória; um
     terceiro resultado não entra (nenhuma task) e nada é decidido por maioria.

Uso (com o env.sh do runtime_env.sh, INTEGRATED=1): python isolation.py <qualification/integration-stocks> <work> <out>
"""

from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

from harness import Harness

PROBE = r'''
import json, sys
from pathlib import Path
from research_protocol import v2
m = Path(sys.argv[1])
load = lambda rel: (m / rel).read_bytes()
out = {}
tasks = {d: v2.loads_task(load(f"{d}/task-h9.json")) for d in ("crypto", "stocks", "brasileirao")}
results = {d: load(f"{d}/result-h9.json") for d in ("crypto", "stocks", "brasileirao")}
for rd in results:
    for td in tasks:
        try:
            v2.loads_result(results[rd], task=tasks[td]); out[f"{rd}->{td}"] = "ACCEPTED"
        except v2.V2Error as exc:
            out[f"{rd}->{td}"] = exc.code
out["task_ids"] = {d: t["task_id"] for d, t in tasks.items()}
out["episode_ids"] = {d: t["episode_id"] for d, t in tasks.items()}
out["hypothesis_ids"] = {d: t["hypothesis_id"] for d, t in tasks.items()}
bad = json.loads(load("stocks/task-h9.json"))
bad["hypothesis_id"] = "H9"
try:
    v2.validate_task(bad); out["unqualified"] = "ACCEPTED"
except v2.V2Error as exc:
    out["unqualified"] = exc.code
print(json.dumps(out, sort_keys=True))
'''
CUBES = r'''
import json, sys
from cain.orchestration.store import OrchestrationStore
store = OrchestrationStore(sys.argv[1])
head = store.memory_head()
out = {}
for cube in ("stocks", "crypto", "brasileirao"):
    facts = [] if head is None else store.memory.facts(as_of=head, cubes=[cube])
    out[cube] = sorted({f["subject"] for f in facts})
out["verify"] = store.memory.verify()["status"]
print(json.dumps(out, sort_keys=True))
'''


def main() -> int:
    mission, work, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    fixtures = mission.parent / "integration-crypto" / "fixtures" / "v2"
    crypto_props = mission.parent / "integration-crypto" / "fixtures" / "proposals"
    vectors = json.loads((mission / "FROZEN_VECTORS.json").read_text(encoding="utf-8"))
    h = Harness(out, work / "shared", mission, "isolation-ids-contradiction")
    # 1: envelope level, with the frozen protocol installed in the CAIN venv
    probe = work / "probe.py"
    probe.write_text(PROBE, encoding="utf-8")
    _code, lines, _ = h.run("protocol probe", [os.environ["CAIN_PY"], "-I", probe, fixtures])
    got = lines[0]
    for rd in ("crypto", "stocks", "brasileirao"):
        for td in ("crypto", "stocks", "brasileirao"):
            expected = "ACCEPTED" if rd == td else "DOMAIN_MISMATCH"
            h.check(f"result of {rd} against task of {td}: {expected}", got[f"{rd}->{td}"] == expected,
                    got=got[f"{rd}->{td}"])
    h.check("same H9 in three domains: distinct task_ids, episodes and qualified hypothesis IDs",
            len(set(got["task_ids"].values())) == 3 and len(set(got["episode_ids"].values())) == 3
            and sorted(got["hypothesis_ids"].values()) == ["brasileirao:H9", "crypto:H9", "stocks:H9"], got=got)
    h.check("ID without domain rejected by the envelope", got["unqualified"] == "ID_NOT_QUALIFIED",
            got=got["unqualified"])
    # 2: integrated runtime, one CAIN state with the two orchestrations
    x = Harness(out / "crypto", work / "shared", mission, "isolation-crypto-side", domain="crypto")
    x.dstate, x.ledger = work / "shared" / "crypto-domain-state", work / "shared" / "consumer" / "crypto-ledger.sqlite"
    x.propose("crypto: propose real", crypto_props / "e2e" / "01-allow.json")
    x.dispatch("crypto: dispatch"); x.consumer("crypto: consumer"); x.ingest("crypto: ingest")
    real = h.real_proposal("fixtures/proposals/e2e/01-allow.json", work / "effective" / "iso-01.json",
                           request_id="stocks:REQ-IS-ISO-001")
    _c, lines, _ = h.propose("stocks: propose real", real)
    h.check("stocks: real proposal ALLOW in the shared CAIN", lines and lines[0].get("decision") == "ALLOW", got=lines)
    h.dispatch("stocks: dispatch"); h.consumer("stocks: consumer"); h.ingest("stocks: ingest")
    (s_path, s_result), = h.results()
    (c_path, c_result), = x.results()
    h.check("one real result per domain", s_result["outcome"]["status"] == "RESULT"
            and c_result["outcome"]["status"] == "RESULT", stocks=s_result["outcome"], crypto=c_result["outcome"])
    h.provenance(s_result, h.task(s_result["task_id"]))
    shutil.copy(c_path, h.spool / "stocks" / "results" / "cross-crypto-real.json")
    shutil.copy(s_path, x.spool / "crypto" / "results" / "cross-stocks-real.json")
    _c, s_lines, _ = h.ingest("stocks: ingest the real crypto result")
    _c, c_lines, _ = x.ingest("crypto: ingest the real stocks result")
    h.check("real crypto result in the stocks spool: DOMAIN_MISMATCH, not ingested",
            {l["file"]: l.get("code") for l in s_lines if l.get("action") == "rejected"}
            == {"cross-crypto-real.json": "DOMAIN_MISMATCH"}, got=s_lines)
    h.check("real stocks result in the crypto spool: DOMAIN_MISMATCH, not ingested",
            {l["file"]: l.get("code") for l in c_lines if l.get("action") == "rejected"}
            == {"cross-stocks-real.json": "DOMAIN_MISMATCH"}, got=c_lines)
    crypto_task = next((x.spool / "crypto" / "tasks").glob("TASK-*.json"))
    shutil.copy(crypto_task, h.spool / "stocks" / "tasks" / crypto_task.name)
    _c, lines, _ = h.consumer("stocks consumer: a crypto task file in the stocks spool")
    h.check("crypto task in the stocks consumer spool: rejected, the stocks domain is never called",
            any(l.get("action") == "rejected" and l.get("code") == "DOMAIN_MISMATCH" for l in lines), got=lines)
    reasons = {}
    for label, harness, proposal in (
        ("crypto:H9 -> crypto", x, crypto_props / "e2e" / "05-h9-closed.json"),
        ("stocks:H9 -> crypto", x, crypto_props / "e2e" / "06-stocks-h9.json"),
        ("stocks:H9 -> stocks", h, mission / "fixtures/proposals/n1/04-stocks-h9.json"),
        ("crypto:H9 -> stocks", h, mission / "fixtures/proposals/n1/03-crypto-h9.json"),
        ("brasileirao:H9 -> stocks", h, mission / "fixtures/proposals/n1/05-brasileirao-h9.json"),
    ):
        _c, lines, _ = harness.propose(f"same H9: {label}", proposal)
        reasons[label] = (lines[0].get("decision"), lines[0].get("reason_code"), lines[0].get("task"))
    h.check("same H9 in the two integrated orchestrations: closed where it belongs, foreign elsewhere, no task", reasons == {
        "crypto:H9 -> crypto": ("BLOCK", "HYPOTHESIS_CLOSED", None),
        "stocks:H9 -> crypto": ("BLOCK", "DOMAIN_MISMATCH", None),
        "stocks:H9 -> stocks": ("BLOCK", "HYPOTHESIS_CLOSED", None),
        "crypto:H9 -> stocks": ("BLOCK", "DOMAIN_MISMATCH", None),
        "brasileirao:H9 -> stocks": ("BLOCK", "DOMAIN_MISMATCH", None)}, got=reasons)
    cubes = work / "cubes.py"
    cubes.write_text(CUBES, encoding="utf-8")
    _c, lines, _ = h.run("memory cubes", [os.environ["CAIN_PY"], "-I", cubes, h.state])
    mem = lines[0]
    h.check("memory separated by cube: stocks facts only in the stocks cube, crypto facts only in the crypto cube, no "
            "brasileirao cube", mem["verify"] == "intact" and mem["brasileirao"] == []
            and mem["stocks"] and all(s.startswith("stocks:") for s in mem["stocks"])
            and mem["crypto"] and all(s.startswith("crypto:") for s in mem["crypto"]), got=mem)
    # 3: brasileirao by frozen fixtures
    shutil.copy(fixtures / "brasileirao" / "result-etapa-a.json", h.spool / "stocks" / "results" / "brasileirao.json")
    _c, lines, _ = h.ingest("stocks: ingest a brasileirao result")
    h.check("brasileirao result in the stocks spool: DOMAIN_MISMATCH",
            any(l.get("file") == "brasileirao.json" and l.get("code") == "DOMAIN_MISMATCH" for l in lines), got=lines)
    code, lines, _ = h.cain("propose to an orchestration of a domain outside the protocol", "propose", "--domain",
                            "forex", "--state", work / "forex-state", "--proposal",
                            mission / "fixtures/proposals/n1/04-stocks-h9.json")
    h.check("no orchestration for a domain outside the protocol: CONFIG_INVALID, nothing written",
            code == 1 and lines[0].get("error") == "CONFIG_INVALID" and not (work / "forex-state").exists(),
            got=lines)
    code, lines, _ = h.cain("propose stocks H9 to the brasileirao orchestration", "propose", "--domain", "brasileirao",
                            "--state", work / "brasileirao-state", "--proposal",
                            mission / "fixtures/proposals/n1/04-stocks-h9.json")
    h.check("stocks proposal in the brasileirao orchestration: BLOCK DOMAIN_MISMATCH, no task",
            code == 0 and lines[0].get("decision") == "BLOCK" and lines[0].get("reason_code") == "DOMAIN_MISMATCH"
            and not lines[0].get("task"), got=lines)
    # 4: contradiction (fresh state)
    k = Harness(out / "contradiction", work / "contradiction", mission, "contradiction")
    spec = vectors["contradiction"]
    results_dir = k.spool / "stocks" / "results"
    for step in spec["plan"]:
        name = Path(step["proposal"]).stem
        _code, lines, _ = k.propose(f"propose {name}", step["proposal"], as_of=spec["as_of"])
        line = lines[0]
        ok = line.get("decision") == step["expected_decision"] and (
            "expected_reason" not in step or line.get("reason_code") == step["expected_reason"])
        k.check(f"contradiction {name}: {step['expected_decision']} {step.get('expected_reason', '')}".strip(), ok,
                got=line)
        if step.get("result"):
            if line.get("task"):
                k.dispatch(f"dispatch {name}")
            results_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy(mission / step["result"], results_dir / Path(step["result"]).name)
            _code, ingested, _ = k.ingest(f"ingest {name}")
            mine = [l for l in ingested if l["file"] == Path(step["result"]).name]
            expected = "TASK_NOT_FOUND" if "result_expected" in step else "ingested"
            k.check(f"contradiction {name}: result {expected}",
                    bool(mine) and (mine[0].get("code") or mine[0].get("action")) == expected, got=mine)
    episodes = k.episodes("episodes contradiction")
    raw = (k.state / "memory.sqlite").read_bytes()
    k.check("both conflicting facts preserved in memory (SUPPORTED and REFUTED), nothing superseded",
            raw.count(b'"scientific_state":"SUPPORTED"') >= 1 and raw.count(b'"scientific_state":"REFUTED"') >= 1
            and b'"supersedes":"fact:' not in raw and episodes["memory"]["status"] == "intact")
    k.check("no third result entered: exactly two contradiction results in the inbox",
            len(episodes["inbox"]) == 2, inbox=episodes["inbox"])
    status = 0
    for harness in (x, k):
        status |= harness.finish()
    status |= h.finish({"memory_cubes": mem})
    return status


if __name__ == "__main__":
    raise SystemExit(main())
