"""integration-brasileirao, fase isolation-ids-contradiction (CROSS_DOMAIN_ISOLATION, DOMAIN_QUALIFIED_IDS,
CONTRADICTION_PRESERVATION).

Adaptado de qualification/integration-stocks/scripts/isolation.py. Pelos entrypoints do CAIN e dos consumidores
(runtime suportado) e pelo protocolo congelado instalado no venv do CAIN:
  1. envelope: resultado de cada domínio contra a task de cada domínio (fixtures V2 congeladas da integration-crypto):
     só o próprio domínio é aceito; o mesmo H9 nos três domínios gera tasks, episódios e IDs distintos; ID sem domínio é
     recusado;
  2. contra o cripto E o stocks pelos runtimes integrados (prompt do Brasileirão §5): UM estado do CAIN com as três
     orquestrações; um ciclo real de cada domínio (Brasileirão com o dado real privado); o resultado real de cada um
     entregue no spool dos outros dois é recusado (DOMAIN_MISMATCH); a task do cripto no spool do consumidor do
     Brasileirão é recusada sem chamar o domínio; o mesmo H9 é bloqueado em cada orquestração pelo motivo certo; a
     memória fica separada por cubo (nenhum fato de um domínio no cubo de outro);
  3. contradição: SUPPORTED × REFUTED da mesma hipótese do Brasileirão → REQUIRE_HUMAN; os dois fatos ficam na
     memória; um terceiro resultado não entra (nenhuma task) e nada é decidido por maioria.
Todo o estado (CAIN, spools, domínios) fica no diretório de trabalho privado; a saída pública tem só decisões, códigos,
IDs e hashes (no_data_rows_check no run_scenario.sh).

Uso (com o env.sh do runtime_env.sh, INTEGRATED=1): python isolation.py <qualification/integration-brasileirao> <work> <out>
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
bad = json.loads(load("brasileirao/task-h9.json"))
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
for cube in ("brasileirao", "crypto", "stocks"):
    facts = [] if head is None else store.memory.facts(as_of=head, cubes=[cube])
    out[cube] = sorted({f["subject"] for f in facts})
out["verify"] = store.memory.verify()["status"]
print(json.dumps(out, sort_keys=True))
'''
DOMAINS = ("brasileirao", "crypto", "stocks")


def main() -> int:
    mission, work, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    fixtures = mission.parent / "integration-crypto" / "fixtures" / "v2"
    crypto_props = mission.parent / "integration-crypto" / "fixtures" / "proposals"
    vectors = json.loads((mission / "FROZEN_VECTORS.json").read_text(encoding="utf-8"))
    h = Harness(out, work / "shared", mission, "isolation-ids-contradiction")
    # 1: envelope level, with the frozen protocol installed in the CAIN venv
    probe = work / "probe.py"
    probe.write_text(PROBE, encoding="utf-8")
    _code, lines, _ = h.run("protocol probe", [os.environ["CAIN_PY"], "-I", probe, fixtures], public_stdout="full")
    got = lines[0]
    for rd in DOMAINS:
        for td in DOMAINS:
            expected = "ACCEPTED" if rd == td else "DOMAIN_MISMATCH"
            h.check(f"result of {rd} against task of {td}: {expected}", got[f"{rd}->{td}"] == expected,
                    got=got[f"{rd}->{td}"])
    h.check("same H9 in three domains: distinct task_ids, episodes and qualified hypothesis IDs",
            len(set(got["task_ids"].values())) == 3 and len(set(got["episode_ids"].values())) == 3
            and sorted(got["hypothesis_ids"].values()) == ["brasileirao:H9", "crypto:H9", "stocks:H9"], got=got)
    h.check("ID without domain rejected by the envelope", got["unqualified"] == "ID_NOT_QUALIFIED",
            got=got["unqualified"])
    # 2: integrated runtimes, one CAIN state with the three orchestrations
    side = {"crypto": h.for_domain("crypto"), "stocks": h.for_domain("stocks"), "brasileirao": h}
    proposals = {"crypto": crypto_props / "e2e" / "01-allow.json",
                 "stocks": h.integrated_proposal("stocks", "fixtures/proposals/e2e/01-allow.json",
                                                 work / "effective" / "stocks-iso-01.json"),
                 "brasileirao": h.proposal_path("fixtures/proposals/e2e/01-allow.json",
                                                work / "effective" / "br-iso-01.json",
                                                request_id="brasileirao:REQ-IB-ISO-001")}
    for domain in DOMAINS:
        x = side[domain]
        _c, lines, _ = x.propose(f"{domain}: propose real", proposals[domain])
        h.check(f"{domain}: real proposal ALLOW in the shared CAIN", bool(lines) and lines[0].get("decision") == "ALLOW",
                got={k: lines[0].get(k) for k in ("decision", "reason_code")} if lines else None)
        x.dispatch(f"{domain}: dispatch")
        x.consumer(f"{domain}: consumer")
        x.ingest(f"{domain}: ingest")
    real = {}
    for domain in DOMAINS:
        found = side[domain].results(domain)
        h.check(f"{domain}: one real RESULT", len(found) == 1 and found[0][1]["outcome"]["status"] == "RESULT",
                got=[r["outcome"]["status"] for _p, r in found])
        real[domain] = found[0][0]
    (b_path, b_result), = h.results()
    h.provenance(b_result, h.task(b_result["task_id"]))
    for target in DOMAINS:
        for source in DOMAINS:
            if source != target:
                shutil.copy(real[source], h.spool / target / "results" / f"cross-{source}-real.json")
        _c, lines, _ = side[target].ingest(f"{target}: ingest the real results of the other two domains")
        rejected = {l["file"]: l.get("code") for l in lines if l.get("action") == "rejected"}
        expected = {f"cross-{s}-real.json": "DOMAIN_MISMATCH" for s in DOMAINS if s != target}
        h.check(f"real results of the other domains in the {target} spool: DOMAIN_MISMATCH, not ingested",
                rejected == expected, got=rejected)
    crypto_task = next((h.spool / "crypto" / "tasks").glob("TASK-*.json"))
    shutil.copy(crypto_task, h.spool / "brasileirao" / "tasks" / crypto_task.name)
    _c, lines, _ = h.consumer("brasileirao consumer: a crypto task file in the brasileirao spool")
    h.check("crypto task in the brasileirao consumer spool: rejected, the brasileirao domain is never called",
            any(l.get("action") == "rejected" and l.get("code") == "DOMAIN_MISMATCH" for l in lines),
            got=[{k: l.get(k) for k in ("action", "code", "file")} for l in lines])
    reasons = {}
    # the frozen proposals unchanged (as in the stocks isolation): the orchestration is chosen by --domain
    same_h9 = {"crypto": crypto_props / "e2e" / "05-h9-closed.json",
               "stocks": mission.parent / "integration-stocks" / "fixtures/proposals/n1/04-stocks-h9.json",
               "brasileirao": mission / "fixtures/proposals/n1/04-brasileirao-h9.json"}
    for owner, proposal in same_h9.items():
        for orchestration in DOMAINS:
            _c, lines, _ = side[orchestration].propose(f"same H9: {owner}:H9 -> {orchestration}", proposal)
            reasons[f"{owner}:H9 -> {orchestration}"] = (lines[0].get("decision"), lines[0].get("reason_code"),
                                                         lines[0].get("task"))
    expected = {f"{o}:H9 -> {t}": ("BLOCK", "HYPOTHESIS_CLOSED" if o == t else "DOMAIN_MISMATCH", None)
                for o in DOMAINS for t in DOMAINS}
    h.check("same H9 in the three integrated orchestrations: closed where it belongs, foreign elsewhere, no task",
            reasons == expected, got=reasons)
    cubes = work / "cubes.py"
    cubes.write_text(CUBES, encoding="utf-8")
    _c, lines, _ = h.run("memory cubes", [os.environ["CAIN_PY"], "-I", cubes, h.state], public_stdout="full")
    mem = lines[0]
    h.check("memory separated by cube: each domain's facts only in its own cube",
            mem["verify"] == "intact" and all(mem[d] and all(s.startswith(f"{d}:") for s in mem[d]) for d in DOMAINS),
            got=mem)
    # 3: contradiction (fresh state)
    k = Harness(out / "contradiction", work / "contradiction", mission, "contradiction")
    spec = vectors["contradiction"]
    results_dir = k.spool / "brasileirao" / "results"
    for step in spec["plan"]:
        name = Path(step["proposal"]).stem
        _code, lines, _ = k.propose(f"propose {name}", step["proposal"], as_of=spec["as_of"])
        line = lines[0]
        ok = line.get("decision") == step["expected_decision"] and (
            "expected_reason" not in step or line.get("reason_code") == step["expected_reason"])
        k.check(f"contradiction {name}: {step['expected_decision']} {step.get('expected_reason', '')}".strip(), ok,
                got={kk: line.get(kk) for kk in ("decision", "reason_code", "rule")})
        if step.get("result"):
            if line.get("task"):
                k.dispatch(f"dispatch {name}")
            results_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy(mission / step["result"], results_dir / Path(step["result"]).name)
            _code, ingested, _ = k.ingest(f"ingest {name}")
            mine = [l for l in ingested if l["file"] == Path(step["result"]).name]
            expected_state = "TASK_NOT_FOUND" if "result_expected" in step else "ingested"
            k.check(f"contradiction {name}: result {expected_state}",
                    bool(mine) and (mine[0].get("code") or mine[0].get("action")) == expected_state, got=mine)
    episodes = k.episodes("episodes contradiction")
    raw = (k.state / "memory.sqlite").read_bytes()
    k.check("both conflicting facts preserved in memory (SUPPORTED and REFUTED), nothing superseded",
            raw.count(b'"scientific_state":"SUPPORTED"') >= 1 and raw.count(b'"scientific_state":"REFUTED"') >= 1
            and b'"supersedes":"fact:' not in raw and episodes["memory"]["status"] == "intact")
    k.check("no third result entered: exactly two contradiction results in the inbox",
            len(episodes["inbox"]) == 2, inbox=len(episodes["inbox"]))
    status = k.finish()
    status |= h.finish({"memory_cubes": mem})
    return status


if __name__ == "__main__":
    raise SystemExit(main())
