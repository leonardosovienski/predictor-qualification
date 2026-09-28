"""integration-crypto, fase isolation-ids-contradiction (CROSS_DOMAIN_ISOLATION, DOMAIN_QUALIFIED_IDS,
CONTRADICTION_PRESERVATION).

Pelos entrypoints do CAIN (runtime suportado) e pelo protocolo congelado instalado no venv do CAIN, com as fixtures V2
congeladas dos três domínios (FROZEN_VECTORS.json):
  1. isolamento: resultado de stocks/brasileirao nunca satisfaz task do cripto (DOMAIN_MISMATCH no inbox) e resultado
     do cripto nunca satisfaz task de outro domínio (validação do envelope contra a task deles); o CAIN não tem
     orquestração de domínio fora do protocolo e recusa (CONFIG_INVALID), sem efeito; proposta do stocks na
     orquestração do brasileirao é BLOCK DOMAIN_MISMATCH, sem task (ciclo 2, cain 0.4.13rc10: os três domínios têm
     configuração, então o domínio sem configuração passa a ser um fora do protocolo, e a proposta estrangeira é
     conferida numa orquestração configurada de outro domínio);
  2. IDs: o mesmo H9 nos três domínios gera tasks, episódios e resultados distintos; ID sem domínio é recusado;
  3. contradição: SUPPORTED × REFUTED da mesma hipótese → REQUIRE_HUMAN; os dois fatos ficam na memória; um
     terceiro resultado não entra (nenhuma task) e nada é decidido por maioria.

Uso (com o env.sh do runtime_env.sh): python isolation.py <qualification/integration-crypto> <work> <out>
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
tasks = {d: v2.loads_task(load(f"fixtures/v2/{d}/task-h9.json")) for d in ("crypto", "stocks", "brasileirao")}
results = {d: load(f"fixtures/v2/{d}/result-h9.json") for d in ("crypto", "stocks", "brasileirao")}
for rd in results:
    for td in tasks:
        try:
            v2.loads_result(results[rd], task=tasks[td]); out[f"{rd}->{td}"] = "ACCEPTED"
        except v2.V2Error as exc:
            out[f"{rd}->{td}"] = exc.code
out["task_ids"] = {d: t["task_id"] for d, t in tasks.items()}
out["episode_ids"] = {d: t["episode_id"] for d, t in tasks.items()}
out["hypothesis_ids"] = {d: t["hypothesis_id"] for d, t in tasks.items()}
bad = json.loads(load("fixtures/v2/crypto/task-h9.json"))
bad["hypothesis_id"] = "H9"
try:
    v2.validate_task(bad); out["unqualified"] = "ACCEPTED"
except v2.V2Error as exc:
    out["unqualified"] = exc.code
print(json.dumps(out, sort_keys=True))
'''


def main() -> int:
    mission, work, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    h = Harness(out, work, mission, "isolation-ids-contradiction")
    vectors = json.loads((mission / "FROZEN_VECTORS.json").read_text(encoding="utf-8"))
    # 1 + 2: envelope level, with the frozen protocol installed in the CAIN venv
    probe = work / "probe.py"
    probe.write_text(PROBE, encoding="utf-8")
    _code, lines, _ = h.run("protocol probe", [os.environ["CAIN_PY"], "-I", probe, mission])
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
    # CAIN: a domain outside the protocol has no orchestration; a proposal of one domain is blocked in another
    stocks_prop = mission / "fixtures/proposals/e2e/06-stocks-h9.json"
    code, lines, _ = h.cain("propose to an orchestration of a domain outside the protocol", "propose", "--domain",
                            "forex", "--state", work / "forex-state", "--proposal", stocks_prop)
    h.check("no orchestration for a domain outside the protocol: CONFIG_INVALID, nothing written",
            code == 1 and lines[0].get("error") == "CONFIG_INVALID" and not (work / "forex-state").exists(),
            got=lines)
    code, lines, _ = h.cain("propose stocks H9 to the brasileirao orchestration", "propose", "--domain",
                            "brasileirao", "--state", work / "brasileirao-state", "--proposal", stocks_prop)
    h.check("stocks proposal in the brasileirao orchestration: BLOCK DOMAIN_MISMATCH, no task",
            code == 0 and lines[0].get("decision") == "BLOCK" and lines[0].get("reason_code") == "DOMAIN_MISMATCH"
            and not lines[0].get("task"), got=lines)
    # 3: contradiction
    spec = vectors["contradiction"]
    results_dir = h.spool / "crypto" / "results"
    for step in spec["plan"]:
        name = Path(step["proposal"]).stem
        code, lines, _ = h.propose(f"propose {name}", step["proposal"], as_of=spec["as_of"])
        line = lines[0]
        ok = line.get("decision") == step["expected_decision"] and (
            "expected_reason" not in step or line.get("reason_code") == step["expected_reason"])
        h.check(f"contradiction {name}: {step['expected_decision']} {step.get('expected_reason', '')}".strip(), ok,
                got=line)
        if step.get("result"):
            if line.get("task"):
                h.dispatch(f"dispatch {name}")
            results_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy(mission / step["result"], results_dir / Path(step["result"]).name)
            _code, ingested, _ = h.ingest(f"ingest {name}")
            mine = [l for l in ingested if l["file"] == Path(step["result"]).name]
            expected = "TASK_NOT_FOUND" if "result_expected" in step else "ingested"
            h.check(f"contradiction {name}: result {expected}",
                    bool(mine) and (mine[0].get("code") or mine[0].get("action")) == expected, got=mine)
    episodes = h.episodes("episodes contradiction")
    facts_file = h.state / "memory.sqlite"
    raw = facts_file.read_bytes()
    h.check("both conflicting facts preserved in memory (SUPPORTED and REFUTED), nothing superseded",
            raw.count(b'"scientific_state":"SUPPORTED"') >= 1 and raw.count(b'"scientific_state":"REFUTED"') >= 1
            and b'"supersedes":"fact:' not in raw and episodes["memory"]["status"] == "intact")
    h.check("no third result entered: exactly two contradiction results in the inbox",
            len(episodes["inbox"]) == 2, inbox=episodes["inbox"])
    return h.finish()


if __name__ == "__main__":
    raise SystemExit(main())
