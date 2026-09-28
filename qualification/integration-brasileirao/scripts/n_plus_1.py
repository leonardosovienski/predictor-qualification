"""integration-brasileirao, fase n-plus-1 (N_PLUS_1_DETERMINISTIC, C9; DECISION_POLICY; NEGATIVE_RESULT_NEUTRALITY parcial).

Adaptado de qualification/integration-stocks/scripts/n_plus_1.py. Estado congelado: episódio 1 do Brasileirão (proposta
semente = pedido da Etapa A, fixture V2 congelada, dataset sintético) + resultado V2 congelado da Etapa A ingerido;
resultados dos outros dois domínios e o H9 do Brasileirão chegam ao mesmo spool e são recusados. Para cada candidata
congelada (FROZEN_VECTORS.json → n_plus_1.candidates) e cada proposta do holdout (→ holdout.plan, D-25 (2)), `cain research
decision-receipt` roda em 3 processos novos, cada um sobre uma cópia nova do mesmo estado, com o mesmo as_of: os três
receipts têm de ser idênticos byte a byte, a decisão (e o motivo) tem de ser a esperada e o estado não pode mudar. Sem
LLM, sem domínio (o receipt é do CAIN); nada é despachado.

Holdout: a decisão congelada é REQUIRE_HUMAN (D-25 (2)); a política qualificada não tem regra que leia a temporada
(IB-F002). O resultado é registrado como veio (a checagem falha enquanto a regra não existir) e vai para o gate
DECISION_POLICY, separado da determinação do N+1.

Variante integrada (prompt do Brasileirão §5, contra o cripto e o stocks pelos runtimes integrados; só quando o env.sh
os tem): um ciclo real de cada um roda no mesmo estado do CAIN; os resultados V2 reais deles entram no spool do
Brasileirão antes de congelar o estado e são recusados (DOMAIN_MISMATCH); os receipts de todas as candidatas têm de ser
os mesmos bytes da variante congelada.

Uso (com o env.sh do runtime_env.sh): python n_plus_1.py <qualification/integration-brasileirao> <work> <out>
"""

from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

from harness import Harness, sha

EXPECTED_STATE = {"fixtures-v2-brasileirao-result-etapa-a.json": "ingested",
                  "fixtures-v2-brasileirao-result-h9.json": "TASK_NOT_FOUND",
                  "fixtures-v2-crypto-result-etapa-a.json": "DOMAIN_MISMATCH",
                  "fixtures-v2-crypto-result-h9.json": "DOMAIN_MISMATCH",
                  "fixtures-v2-stocks-result-etapa-a.json": "DOMAIN_MISMATCH",
                  "fixtures-v2-stocks-result-h9.json": "DOMAIN_MISMATCH"}
OTHER = {"crypto": ("CRYPTO_CONSUMER_BIN", "integration-crypto/fixtures/proposals/e2e/01-allow.json"),
         "stocks": ("STOCKS_CONSUMER_BIN", "integration-stocks/fixtures/proposals/e2e/01-allow.json")}


def other_real_results(mission: Path, work: Path, out: Path) -> dict[str, Path]:
    """One real cycle of each other domain in the integrated runtime (same CAIN code, its own state and spool)."""
    found = {}
    for domain, (var, proposal) in OTHER.items():
        if var not in os.environ:
            continue
        x = Harness(out / f"{domain}-cycle", work / f"{domain}-cycle", mission, f"{domain}-cycle", domain=domain)
        path = mission.parent / proposal
        if domain == "stocks":  # the stocks proposal template carries the as_of marker of its own mission
            value = json.loads(path.read_text(encoding="utf-8"))
            value["request"]["as_of"] = json.loads(Path(os.environ["STOCKS_REAL_ENV"]).read_text())["data_cutoff"]
            path = x.work / "stocks-01-allow.json"
            path.write_text(json.dumps(value), encoding="utf-8")
        x.propose(f"{domain} propose", path)
        x.dispatch(f"{domain} dispatch")
        x.consumer(f"{domain} consumer")
        x.ingest(f"{domain} ingest")
        results = x.results()
        x.check(f"integrated {domain} cycle produced one real V2 result", len(results) == 1
                and results[0][1]["outcome"]["status"] in ("RESULT", "DUPLICATE"),
                got=[r["outcome"]["status"] for _p, r in results])
        x.finish()
        if results:
            found[domain] = results[0][0]
    return found


def receipts(h: Harness, mission: Path, work: Path, frozen: Path, state_digest: dict, spec_list: list, processes: int,
             as_of: str, tag: str, kind: str) -> tuple[list[dict], list[bool]]:
    receipts_dir = h.out / f"receipts-{tag}"
    receipts_dir.mkdir(parents=True, exist_ok=True)
    table, unchanged = [], []
    for candidate in spec_list:
        name = Path(candidate["proposal"]).stem
        outputs = []
        for run in range(1, processes + 1):
            copy = work / f"{tag}-state-{kind}-{name}-{run}"
            shutil.copytree(frozen, copy)
            code, _lines, stdout = h.cain(f"{tag}: decision-receipt {kind} {name} process {run}", "decision-receipt",
                                          "--domain", "brasileirao", "--state", copy, "--proposal",
                                          mission / candidate["proposal"], "--as-of", as_of)
            raw = stdout.encode("utf-8")
            (receipts_dir / f"{kind}-{name}.{run}.json").write_bytes(raw)
            outputs.append((code, raw))
            unchanged.append({p.name: sha(p.read_bytes()) for p in sorted(copy.iterdir()) if p.is_file()} == state_digest)
        identical = len({raw for _c, raw in outputs}) == 1 and all(c == 0 for c, _r in outputs)
        receipt = json.loads(outputs[0][1])
        h.check(f"{tag}: {kind} {name}: receipts byte-identical in {processes} new processes", identical,
                sha256=[sha(r) for _c, r in outputs])
        want = candidate["expected_decision"], candidate.get("expected_reason", receipt["reason_code"])
        h.check(f"{tag}: {kind} {name}: decision {want[0]} {candidate.get('expected_reason', '')}".strip(),
                (receipt["decision"], receipt["reason_code"]) == want, got=receipt["decision"],
                reason=receipt["reason_code"], rule=receipt["rule"], gate="DECISION_POLICY" if kind == "holdout"
                else "N_PLUS_1_DETERMINISTIC")
        h.check(f"{tag}: {kind} {name}: receipt names policy (id, version, code sha256) and configuration sha256",
                receipt["policy"]["id"] == "cain-decision-policy" and len(receipt["policy"]["code_sha256"]) == 64
                and len(receipt["config"]["sha256"]) == 64 and receipt["config"]["domain"] == "brasileirao"
                and receipt["capital_permission"] is False)
        table.append({"kind": kind, "candidate": name, "decision": receipt["decision"],
                      "reason_code": receipt["reason_code"], "rule": receipt["rule"],
                      "expected": candidate["expected_decision"], "receipt_sha256": sha(outputs[0][1])})
    return table, unchanged


def run_variant(h: Harness, mission: Path, work: Path, vectors: dict, extra: dict[str, Path], tag: str) -> list[dict]:
    spec = vectors["n_plus_1"]
    as_of = spec["as_of"]
    code, lines, _ = h.propose(f"{tag}: propose seed", spec["seed"], as_of=as_of)
    h.check(f"{tag}: seed episode ALLOW", code == 0 and lines[0].get("decision") == "ALLOW",
            got={k: lines[0].get(k) for k in ("decision", "reason_code")} if lines else None)
    h.dispatch(f"{tag}: dispatch seed")
    results_dir = h.spool / "brasileirao" / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    for rel in spec["state_results"]:
        name = rel.replace("../integration-crypto/", "").replace("/", "-")
        shutil.copy(mission / rel, results_dir / name)
    expected = dict(EXPECTED_STATE)
    for domain, path in extra.items():
        shutil.copy(path, results_dir / f"integrated-{domain}-real-result.json")
        expected[f"integrated-{domain}-real-result.json"] = "DOMAIN_MISMATCH"
    _code, lines, _ = h.ingest(f"{tag}: ingest frozen results")
    actions = {l["file"]: l.get("code") or l.get("action") for l in lines}
    h.check(f"{tag}: frozen state: brasileirao Stage A result ingested; brasileirao H9 (no task), crypto and stocks "
            f"rejected", actions == expected, got=actions)
    frozen = work / f"{tag}-frozen-state"
    shutil.copytree(h.state, frozen)
    state_digest = {p.name: sha(p.read_bytes()) for p in sorted(frozen.iterdir()) if p.is_file()}
    table, unchanged = receipts(h, mission, work, frozen, state_digest, spec["candidates"], spec["processes"], as_of,
                                tag, "n1")
    holdout, unchanged2 = receipts(h, mission, work, frozen, state_digest, vectors["holdout"]["plan"],
                                   spec["processes"], vectors["holdout"]["as_of"], tag, "holdout")
    h.check(f"{tag}: decision-receipt never changed the state it read (every copy byte-identical afterwards)",
            bool(unchanged) and all(unchanged + unchanged2), runs=len(unchanged) + len(unchanged2))
    return table + holdout


def main() -> int:
    mission, work, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    vectors = json.loads((mission / "FROZEN_VECTORS.json").read_text(encoding="utf-8"))
    frozen = Harness(out / "frozen", work / "frozen", mission, "n-plus-1")
    table = run_variant(frozen, mission, work / "frozen", vectors, {}, "frozen")
    status = frozen.finish({"as_of": vectors["n_plus_1"]["as_of"], "receipts": table})
    others = other_real_results(mission, work, out)
    if others:
        integrated = Harness(out / "integrated", work / "integrated", mission, "n-plus-1-integrated")
        table2 = run_variant(integrated, mission, work / "integrated", vectors, others, "integrated")
        integrated.check("integrated receipts are the same bytes as the frozen-fixture receipts",
                         [r["receipt_sha256"] for r in table2] == [r["receipt_sha256"] for r in table],
                         frozen=[r["receipt_sha256"] for r in table], integrated=[r["receipt_sha256"] for r in table2])
        status |= integrated.finish({"as_of": vectors["n_plus_1"]["as_of"], "receipts": table2,
                                     "integrated_domains": sorted(others)})
    return status


if __name__ == "__main__":
    raise SystemExit(main())
