"""integration-crypto, fase n-plus-1 (N_PLUS_1_DETERMINISTIC, C9; DECISION_POLICY; NEGATIVE_RESULT_NEUTRALITY parcial).

Estado congelado: episódio 1 do cripto (proposta semente = pedido da Etapa A) + resultado V2 congelado da Etapa A
ingerido; resultados dos outros dois domínios e o H9 do cripto chegam ao mesmo spool e são recusados. Para cada
candidata congelada (FROZEN_VECTORS.json → n_plus_1.candidates), `cain research decision-receipt` roda em 3 processos
novos, cada um sobre uma cópia nova do mesmo estado, com o mesmo as_of: os três receipts têm de ser idênticos byte a
byte, a decisão tem de ser a esperada e o estado não pode mudar. Sem LLM, sem domínio (o receipt é do CAIN).

Uso (com o env.sh do runtime_env.sh): python n_plus_1.py <qualification/integration-crypto> <work> <out>
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

from harness import Harness, sha


def main() -> int:
    mission, work, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    h = Harness(out, work, mission, "n-plus-1")
    spec = json.loads((mission / "FROZEN_VECTORS.json").read_text(encoding="utf-8"))["n_plus_1"]
    as_of = spec["as_of"]
    code, lines, _ = h.propose("propose seed", spec["seed"], as_of=as_of)
    h.check("seed episode ALLOW", code == 0 and lines[0].get("decision") == "ALLOW", got=lines)
    h.dispatch("dispatch seed")
    results_dir = h.spool / "crypto" / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    for rel in spec["state_results"]:
        shutil.copy(mission / rel, results_dir / rel.replace("/", "-"))
    _code, lines, _ = h.ingest("ingest frozen results")
    actions = {l["file"]: l.get("code") or l.get("action") for l in lines}
    h.check("frozen state: crypto Stage A result ingested; crypto H9 (no task), stocks and brasileirao rejected",
            actions == {"fixtures-v2-crypto-result-etapa-a.json": "ingested",
                        "fixtures-v2-crypto-result-h9.json": "TASK_NOT_FOUND",
                        "fixtures-v2-stocks-result-etapa-a.json": "DOMAIN_MISMATCH",
                        "fixtures-v2-stocks-result-h9.json": "DOMAIN_MISMATCH",
                        "fixtures-v2-brasileirao-result-etapa-a.json": "DOMAIN_MISMATCH",
                        "fixtures-v2-brasileirao-result-h9.json": "DOMAIN_MISMATCH"}, got=actions)
    frozen = work / "frozen-state"
    shutil.copytree(h.state, frozen)
    state_digest = {p.name: sha(p.read_bytes()) for p in sorted(frozen.iterdir()) if p.is_file()}
    receipts_dir = out / "receipts"
    receipts_dir.mkdir(parents=True, exist_ok=True)
    table, unchanged = [], []
    for candidate in spec["candidates"]:
        name = Path(candidate["proposal"]).stem
        outputs = []
        for run in range(1, spec["processes"] + 1):
            copy = work / f"state-{name}-{run}"
            shutil.copytree(frozen, copy)
            code, _lines, stdout = h.cain(f"decision-receipt {name} process {run}", "decision-receipt", "--domain",
                                          "crypto", "--state", copy, "--proposal", mission / candidate["proposal"],
                                          "--as-of", as_of)
            raw = stdout.encode("utf-8")
            (receipts_dir / f"{name}.{run}.json").write_bytes(raw)
            outputs.append((code, raw))
            unchanged.append({p.name: sha(p.read_bytes()) for p in sorted(copy.iterdir()) if p.is_file()} == state_digest)
        identical = len({raw for _c, raw in outputs}) == 1 and all(c == 0 for c, _r in outputs)
        receipt = json.loads(outputs[0][1])
        h.check(f"{name}: receipts byte-identical in {spec['processes']} new processes", identical,
                sha256=[sha(r) for _c, r in outputs])
        h.check(f"{name}: decision {candidate['expected_decision']}",
                receipt["decision"] == candidate["expected_decision"], got=receipt["decision"],
                reason=receipt["reason_code"], rule=receipt["rule"])
        h.check(f"{name}: receipt names policy (id, version, code sha256) and configuration sha256",
                receipt["policy"]["id"] == "cain-decision-policy" and len(receipt["policy"]["code_sha256"]) == 64
                and len(receipt["config"]["sha256"]) == 64 and receipt["capital_permission"] is False)
        table.append({"candidate": name, "decision": receipt["decision"], "reason_code": receipt["reason_code"],
                      "rule": receipt["rule"], "receipt_sha256": sha(outputs[0][1])})
    h.check("decision-receipt never changed the state it read (every copy byte-identical afterwards)",
            bool(unchanged) and all(unchanged), runs=len(unchanged))
    return h.finish({"as_of": as_of, "receipts": table})


if __name__ == "__main__":
    raise SystemExit(main())
