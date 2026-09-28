"""integration-stocks, fase n-plus-1 (N_PLUS_1_DETERMINISTIC, C9; DECISION_POLICY; NEGATIVE_RESULT_NEUTRALITY parcial).

Estado congelado: episódio 1 do Stocks (proposta semente = pedido real da Etapa A, fixture V2 congelada) + resultado V2
congelado da Etapa A ingerido; resultados dos outros dois domínios e o H9 do Stocks chegam ao mesmo spool e são
recusados. Para cada candidata congelada (FROZEN_VECTORS.json → n_plus_1.candidates), `cain research
decision-receipt` roda em 3 processos novos, cada um sobre uma cópia nova do mesmo estado, com o mesmo as_of: os três
receipts têm de ser idênticos byte a byte, a decisão (e o motivo) tem de ser a esperada e o estado não pode mudar. Sem
LLM, sem domínio (o receipt é do CAIN).

Variante integrada (prompt do Stocks §4, contra o cripto pelo runtime integrado; só quando o env.sh tem o cripto): um
ciclo real do cripto roda no mesmo job; o resultado V2 real dele entra no spool do Stocks antes de congelar o estado e
é recusado (DOMAIN_MISMATCH); os receipts de todas as candidatas têm de ser os mesmos bytes da variante congelada.

Uso (com o env.sh do runtime_env.sh): python n_plus_1.py <qualification/integration-stocks> <work> <out>
"""

from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

from harness import Harness, sha

EXPECTED_STATE = {"fixtures-v2-stocks-result-etapa-a.json": "ingested",
                  "fixtures-v2-stocks-result-h9.json": "TASK_NOT_FOUND",
                  "fixtures-v2-crypto-result-etapa-a.json": "DOMAIN_MISMATCH",
                  "fixtures-v2-crypto-result-h9.json": "DOMAIN_MISMATCH",
                  "fixtures-v2-brasileirao-result-etapa-a.json": "DOMAIN_MISMATCH",
                  "fixtures-v2-brasileirao-result-h9.json": "DOMAIN_MISMATCH"}


def crypto_real_result(mission: Path, work: Path, out: Path) -> Path | None:
    """One real crypto cycle in the integrated runtime; returns its V2 result file (None without the crypto side)."""
    if "CRYPTO_CONSUMER_BIN" not in os.environ:
        return None
    x = Harness(out / "crypto-cycle", work / "crypto-cycle", mission, "crypto-cycle", domain="crypto")
    proposal = mission.parent / "integration-crypto" / "fixtures" / "proposals" / "e2e" / "01-allow.json"
    x.propose("crypto propose", proposal)
    x.dispatch("crypto dispatch")
    x.consumer("crypto consumer")
    x.ingest("crypto ingest")
    results = x.results()
    x.check("integrated crypto cycle produced one real V2 result", len(results) == 1
            and results[0][1]["outcome"]["status"] in ("RESULT", "DUPLICATE"), got=[r["outcome"] for _p, r in results])
    x.finish()
    return results[0][0] if results else None


def run_variant(h: Harness, mission: Path, work: Path, spec: dict, extra: Path | None, tag: str) -> list[dict]:
    as_of = spec["as_of"]
    code, lines, _ = h.propose(f"{tag}: propose seed", spec["seed"], as_of=as_of)
    h.check(f"{tag}: seed episode ALLOW", code == 0 and lines[0].get("decision") == "ALLOW", got=lines)
    h.dispatch(f"{tag}: dispatch seed")
    results_dir = h.spool / "stocks" / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    for rel in spec["state_results"]:
        name = rel.replace("../integration-crypto/", "").replace("/", "-")
        shutil.copy(mission / rel, results_dir / name)
    expected = dict(EXPECTED_STATE)
    if extra is not None:
        shutil.copy(extra, results_dir / "integrated-crypto-real-result.json")
        expected["integrated-crypto-real-result.json"] = "DOMAIN_MISMATCH"
    _code, lines, _ = h.ingest(f"{tag}: ingest frozen results")
    actions = {l["file"]: l.get("code") or l.get("action") for l in lines}
    h.check(f"{tag}: frozen state: stocks Stage A result ingested; stocks H9 (no task), crypto and brasileirao "
            f"rejected", actions == expected, got=actions)
    frozen = work / f"{tag}-frozen-state"
    shutil.copytree(h.state, frozen)
    state_digest = {p.name: sha(p.read_bytes()) for p in sorted(frozen.iterdir()) if p.is_file()}
    receipts_dir = h.out / f"receipts-{tag}"
    receipts_dir.mkdir(parents=True, exist_ok=True)
    table, unchanged = [], []
    for candidate in spec["candidates"]:
        name = Path(candidate["proposal"]).stem
        outputs = []
        for run in range(1, spec["processes"] + 1):
            copy = work / f"{tag}-state-{name}-{run}"
            shutil.copytree(frozen, copy)
            code, _lines, stdout = h.cain(f"{tag}: decision-receipt {name} process {run}", "decision-receipt",
                                          "--domain", "stocks", "--state", copy, "--proposal",
                                          mission / candidate["proposal"], "--as-of", as_of)
            raw = stdout.encode("utf-8")
            (receipts_dir / f"{name}.{run}.json").write_bytes(raw)
            outputs.append((code, raw))
            unchanged.append({p.name: sha(p.read_bytes()) for p in sorted(copy.iterdir()) if p.is_file()} == state_digest)
        identical = len({raw for _c, raw in outputs}) == 1 and all(c == 0 for c, _r in outputs)
        receipt = json.loads(outputs[0][1])
        h.check(f"{tag}: {name}: receipts byte-identical in {spec['processes']} new processes", identical,
                sha256=[sha(r) for _c, r in outputs])
        want = candidate["expected_decision"], candidate.get("expected_reason", receipt["reason_code"])
        h.check(f"{tag}: {name}: decision {want[0]} {candidate.get('expected_reason', '')}".strip(),
                (receipt["decision"], receipt["reason_code"]) == want, got=receipt["decision"],
                reason=receipt["reason_code"], rule=receipt["rule"])
        h.check(f"{tag}: {name}: receipt names policy (id, version, code sha256) and configuration sha256",
                receipt["policy"]["id"] == "cain-decision-policy" and len(receipt["policy"]["code_sha256"]) == 64
                and len(receipt["config"]["sha256"]) == 64 and receipt["config"]["domain"] == "stocks"
                and receipt["capital_permission"] is False)
        table.append({"candidate": name, "decision": receipt["decision"], "reason_code": receipt["reason_code"],
                      "rule": receipt["rule"], "receipt_sha256": sha(outputs[0][1])})
    h.check(f"{tag}: decision-receipt never changed the state it read (every copy byte-identical afterwards)",
            bool(unchanged) and all(unchanged), runs=len(unchanged))
    return table


def main() -> int:
    mission, work, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    spec = json.loads((mission / "FROZEN_VECTORS.json").read_text(encoding="utf-8"))["n_plus_1"]
    frozen = Harness(out / "frozen", work / "frozen", mission, "n-plus-1")
    table = run_variant(frozen, mission, work / "frozen", spec, None, "frozen")
    extra = {"as_of": spec["as_of"], "receipts": table}
    crypto_result = crypto_real_result(mission, work, out)
    status = frozen.finish(extra)
    if crypto_result is not None:
        integrated = Harness(out / "integrated", work / "integrated", mission, "n-plus-1-integrated")
        table2 = run_variant(integrated, mission, work / "integrated", spec, crypto_result, "integrated")
        integrated.check("integrated receipts are the same bytes as the frozen-fixture receipts",
                         [r["receipt_sha256"] for r in table2] == [r["receipt_sha256"] for r in table],
                         frozen=[r["receipt_sha256"] for r in table], integrated=[r["receipt_sha256"] for r in table2])
        status |= integrated.finish({"as_of": spec["as_of"], "receipts": table2})
    return status


if __name__ == "__main__":
    raise SystemExit(main())
