"""integration-crypto: vetores congelados das fases e2e, n-plus-1 e isolation-ids-contradiction (C15: antes da execução).

Gera, de forma determinística, e grava FROZEN_VECTORS.json com o sha256 de cada arquivo:
  * fixtures/proposals/e2e/*.json      propostas cain-proposal/1 do E2E (dados reais; decisão esperada anotada)
  * fixtures/proposals/n1/*.json       candidatas do N+1 (receipt em 3 processos novos, as_of congelado)
  * fixtures/v2/crypto/contradiction-* par V2 com estados científicos em conflito para a mesma hipótese
                                       (derivado do resultado real da Etapa A; derivação declarada)
  * as fixtures V2 da fase freeze-parameters (fixtures/v2/FIXTURES_MANIFEST.json), sem mudança.
O E2E, o N+1 e o soak leem só estes arquivos; nada é escolhido olhando resultado.

Uso: python build_vectors.py <qualification/integration-crypto>
"""

from __future__ import annotations

import copy
import hashlib
import json
import sys
from pathlib import Path

import research_protocol.v2 as v2

MISSION = Path(sys.argv[1])
REFS = {"protocol": {"name": "fixed-shadow", "version": "v1"},
        "dataset": {"name": "real-in-sample", "version": "v1"},
        "baseline": {"name": "flat", "version": "v1"},
        "cost_model": {"name": "v3-frozen", "version": "v1"},
        "evidence": {"name": "none", "version": "v1"}}
RESEARCH = "crypto:RESEARCH-INTEGRATION-QUALIFICATION"
N1_AS_OF = "2026-09-27T00:00:00Z"


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def request(request_id: str, hypothesis: str, seed: int, dataset: str = "real-in-sample") -> dict:
    refs = copy.deepcopy(REFS)
    refs["dataset"]["name"] = dataset
    return {"schema_version": "crypto-research-request/1", "request_id": request_id,
            "request_type": "BACKTEST_EXISTING_HYPOTHESIS", "research_id": RESEARCH, "hypothesis_id": hypothesis,
            "references": refs, "data_cutoff": "2026-08-31T00:00:00Z",
            "parameters": {"symbol": "BTCUSDT", "horizon_days": 7, "max_observations": 100, "fee_bps": 10,
                           "slippage_bps": 5, "placebo_seed": seed},
            "priority_hint": "NORMAL"}


def proposal(pid: str, req: dict, *, domain: str = "crypto", rationale: str = "", **extra) -> dict:
    return {"schema": "cain-proposal/1", "proposal_id": f"cain:{pid}", "domain": domain, "request": req,
            "based_on": [], "rationale": rationale, "source": "agenda", **extra}


def dump(path: Path, value: dict) -> bytes:
    raw = json.dumps(value, indent=1, ensure_ascii=False, sort_keys=True).encode("utf-8") + b"\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)
    return raw


def main() -> int:
    files: dict[str, dict] = {}
    fixtures = MISSION / "fixtures"
    stocks_task = json.loads((fixtures / "v2/stocks/task-h9.json").read_bytes())
    stocks_request = {k: v for k, v in stocks_task["payload"].items() if k != "client_ref"}
    e2e = {
        "01-allow": (proposal("E2E-01", request("crypto:REQ-IC-E2E-001", "crypto:QUAL-SHADOW-REAL-001", 101),
                              rationale="primeiro episódio"), "ALLOW"),
        "02-allow-restarts": (proposal("E2E-02", request("crypto:REQ-IC-E2E-002", "crypto:QUAL-SHADOW-REAL-002", 102),
                                       rationale="consumidor morto depois do domínio; CAIN morto na ingestão"), "ALLOW"),
        "03-canary": (proposal("E2E-03", request("crypto:REQ-IC-E2E-003", "crypto:QUAL-SHADOW-REAL-003", 103,
                                                 "real-future-canary"), rationale="canário pós-cutoff"), "ALLOW"),
        "04-duplicate": (proposal("E2E-04", request("crypto:REQ-IC-E2E-001", "crypto:QUAL-SHADOW-REAL-001", 101),
                                  rationale="mesmo conteúdo do 01"), "DUPLICATE"),
        "05-h9-closed": (proposal("E2E-05", request("crypto:REQ-IC-E2E-005", "crypto:H9", 105)), "BLOCK"),
        "06-stocks-h9": (proposal("E2E-06", stocks_request, domain="stocks"), "BLOCK"),
        "07-next": (proposal("E2E-07", request("crypto:REQ-IC-E2E-007", "crypto:QUAL-SHADOW-REAL-003", 107),
                             rationale="N+1 depois dos resultados"), "ALLOW"),
    }
    plan = []
    for name, (value, expected) in e2e.items():
        rel = f"fixtures/proposals/e2e/{name}.json"
        files[rel] = {"sha256": sha(dump(MISSION / rel, value))}
        plan.append({"proposal": rel, "expected_decision": expected})
    crypto_task = json.loads((fixtures / "v2/crypto/task-etapa-a.json").read_bytes())
    crypto_request = {k: v for k, v in crypto_task["payload"].items() if k != "client_ref"}
    brasileirao_task = json.loads((fixtures / "v2/brasileirao/task-h9.json").read_bytes())
    brasileirao_request = {k: v for k, v in brasileirao_task["payload"].items() if k != "client_ref"}
    n1_next = copy.deepcopy(crypto_request)
    n1_next["request_id"] = "crypto:REQ-IC-N1-001"
    n1_next["parameters"]["placebo_seed"] = 201
    n1 = {
        "01-next": (proposal("N1-01", n1_next, rationale="próximo passo depois do resultado congelado"), "ALLOW"),
        "02-duplicate": (proposal("N1-02", copy.deepcopy(crypto_request)), "DUPLICATE"),
        "03-crypto-h9": (proposal("N1-03", dict(copy.deepcopy(crypto_request), hypothesis_id="crypto:H9",
                                                request_id="crypto:REQ-IC-N1-003")), "BLOCK"),
        "04-stocks-h9": (proposal("N1-04", stocks_request, domain="stocks"), "BLOCK"),
        "05-brasileirao-h9": (proposal("N1-05", brasileirao_request, domain="brasileirao"), "BLOCK"),
        "06-new-hypothesis": (proposal("N1-06", dict(copy.deepcopy(n1_next), hypothesis_id="crypto:QUAL-NEW-001",
                                                     request_id="crypto:REQ-IC-N1-006")), "REQUIRE_HUMAN"),
    }
    n1_plan = []
    for name, (value, expected) in n1.items():
        rel = f"fixtures/proposals/n1/{name}.json"
        files[rel] = {"sha256": sha(dump(MISSION / rel, value))}
        n1_plan.append({"proposal": rel, "expected_decision": expected})
    seed_rel = "fixtures/proposals/n1/00-seed-etapa-a.json"
    files[seed_rel] = {"sha256": sha(dump(MISSION / seed_rel, proposal("N1-SEED", copy.deepcopy(crypto_request),
                                                                       rationale="episódio 1 do estado do N+1")))}
    # contradiction pair: Stage A crypto result with SUPPORTED and with REFUTED, same hypothesis
    stage_a = json.loads((fixtures / "v2/crypto/result-etapa-a.json").read_bytes())
    base_result = json.loads(stage_a["result"]["payload_canonical"])
    adapter = {"distribution": "cripto-predictor", "module": "fixture:contradicao-derivada", "version": "341d270e4d70"}
    previous = None
    for number, (label, state, scientific, economic) in enumerate(
        (("supported", "WATCH_NO_CAPITAL", "SUPPORTED", "WATCH"), ("refuted", "REFUTED", "REFUTED", "NO_EDGE"),
         ("refuted-again", "REFUTED", "REFUTED", "NO_EDGE")),
        start=1,
    ):
        req = dict(copy.deepcopy(crypto_request), request_id=f"crypto:REQ-IC-CONTRA-00{number}")
        req["parameters"]["placebo_seed"] = 300 + number
        prop_rel = f"fixtures/proposals/contradiction/{number:02d}-{label}.json"
        files[prop_rel] = {"sha256": sha(dump(MISSION / prop_rel, proposal(f"CONTRA-{number}", req)))}
        task = v2.build_task("crypto", req, episode_id=v2.episode_id_for("crypto", number),
                             proposal_id=f"cain:CONTRA-{number}", created_at=N1_AS_OF, previous_task_id=previous)
        previous = task["task_id"]
        res = dict(copy.deepcopy(base_result), request_id=req["request_id"], result_state=state,
                   scientific_state=scientific, economic_state=economic,
                   result_id=f"crypto:RESULT-CONTRA{number:027d}", experiment_id=f"crypto:EXP-CONTRA{number:030d}")
        outcome = {"status": "RESULT", "exit_code": 0, "request_id": req["request_id"],
                   "client_ref": task["payload"]["client_ref"], "result": res}
        result = v2.build_result(task, outcome, adapter=adapter, produced_at=N1_AS_OF)
        for kind, raw in (("task", v2.dumps_task(task)), ("result", v2.dumps_result(result, task=task))):
            rel = f"fixtures/v2/crypto/contradiction-{label}-{kind}.json"
            (MISSION / rel).write_bytes(raw)
            files[rel] = {"sha256": sha(raw)}
    after = dict(copy.deepcopy(crypto_request), request_id="crypto:REQ-IC-CONTRA-004")
    after["parameters"]["placebo_seed"] = 304
    after_rel = "fixtures/proposals/contradiction/04-after.json"
    files[after_rel] = {"sha256": sha(dump(MISSION / after_rel, proposal("CONTRA-4", after,
                                                                         rationale="depois de 1 SUPPORTED e 2 REFUTED")))}
    manifest_rel = "fixtures/v2/FIXTURES_MANIFEST.json"
    files[manifest_rel] = {"sha256": sha((MISSION / manifest_rel).read_bytes())}
    for rel, entry in json.loads((MISSION / manifest_rel).read_bytes())["files"].items():
        files[f"fixtures/v2/{rel}"] = {"sha256": entry["sha256"]}
    doc = {
        "schema": "integration-crypto/FROZEN_VECTORS/1",
        "frozen_before": "fases e2e, n-plus-1, isolation-ids-contradiction, idempotency-failure e soak",
        "identity": "sha256 dos bytes de cada arquivo em qualification/integration-crypto/",
        "e2e_plan": plan,
        "n_plus_1": {"as_of": N1_AS_OF, "seed": seed_rel,
                     "state_results": ["fixtures/v2/crypto/result-etapa-a.json", "fixtures/v2/crypto/result-h9.json",
                                       "fixtures/v2/stocks/result-etapa-a.json", "fixtures/v2/stocks/result-h9.json",
                                       "fixtures/v2/brasileirao/result-etapa-a.json",
                                       "fixtures/v2/brasileirao/result-h9.json"],
                     "candidates": n1_plan, "processes": 3},
        "contradiction": {"derivation": "resultado real da Etapa A do cripto com result_state/scientific/economic, "
                                        "request_id, result_id e experiment_id trocados; mesma hipótese "
                                        "crypto:QUAL-SHADOW-001; não é resultado de domínio, é vetor do CAIN",
                          "plan": [
                              {"proposal": "fixtures/proposals/contradiction/01-supported.json",
                               "expected_decision": "ALLOW", "result": "fixtures/v2/crypto/contradiction-supported-result.json"},
                              {"proposal": "fixtures/proposals/contradiction/02-refuted.json",
                               "expected_decision": "ALLOW", "result": "fixtures/v2/crypto/contradiction-refuted-result.json"},
                              {"proposal": "fixtures/proposals/contradiction/03-refuted-again.json",
                               "expected_decision": "REQUIRE_HUMAN", "expected_reason": "CONTRADICTION_UNRESOLVED",
                               "result": "fixtures/v2/crypto/contradiction-refuted-again-result.json",
                               "result_expected": "TASK_NOT_FOUND (nenhuma task emitida: a maioria não se forma)"},
                              {"proposal": "fixtures/proposals/contradiction/04-after.json",
                               "expected_decision": "REQUIRE_HUMAN", "expected_reason": "CONTRADICTION_UNRESOLVED"}],
                          "why": "SUPPORTED × REFUTED na mesma hipótese: o CAIN para e pede humano; os dois fatos "
                                 "ficam na memória; um terceiro resultado não entra e nada é decidido por maioria",
                          "as_of": N1_AS_OF},
        "soak_generator": {"hypotheses": ["crypto:QUAL-SHADOW-REAL-001", "crypto:QUAL-SHADOW-REAL-002",
                                          "crypto:QUAL-SHADOW-REAL-003"],
                           "request_id": "crypto:REQ-IC-SOAK-<nnn>", "placebo_seed": "1000 + n",
                           "dataset": "real-in-sample v1", "cycles": 24},
        "files": dict(sorted(files.items())),
    }
    raw = json.dumps(doc, indent=1, ensure_ascii=False).encode("utf-8") + b"\n"
    (MISSION / "FROZEN_VECTORS.json").write_bytes(raw)
    print("FROZEN_VECTORS.json", sha(raw), len(files), "arquivos")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
