"""integration-brasileirao: vetores congelados das fases e2e, n-plus-1, isolation-ids-contradiction e soak (C15: antes).

Gera, de forma determinística, e grava FROZEN_VECTORS.json com o sha256 de cada arquivo:
  * fixtures/proposals/e2e/*.json      propostas cain-proposal/1 do E2E com o dado real privado (o pedido só nomeia
                                       as referências do operador; nenhum valor do dado entra no arquivo). Só
                                       temporadas 2021–2024: 2025 é HOLDOUT_SEALED e 2026 treina com resultados de
                                       2025 (leitura conservadora da D-25 (2)); nenhuma proposta de 2025+ é despachada;
  * fixtures/proposals/n1/*.json       candidatas do N+1 (receipt em 3 processos novos, as_of congelado), sobre o
                                       resultado da Etapa A do Brasileirão (fixture V2 congelada da integration-crypto,
                                       dataset sintético da conformidade);
  * fixtures/proposals/holdout/*.json  propostas que exigiriam o holdout 2025 (e 2026): só decision-receipt, nunca
                                       despachadas; a decisão congelada é a do dono (D-25 (2)): REQUIRE_HUMAN;
  * fixtures/proposals/contradiction/  propostas da contradição e o par V2 derivado (SUPPORTED × REFUTED);
  * as fixtures V2 dos três domínios são as da integration-crypto (qualification/integration-crypto/fixtures/v2/,
    FIXTURES_MANIFEST.json), lidas por caminho + sha256, sem cópia e sem mudança.
Nada é escolhido olhando resultado; nenhum valor do dado real é lido por este script.

Uso (ferramentas da missão: tools/uv.lock): python build_vectors.py <qualification/integration-brasileirao>
"""

from __future__ import annotations

import copy
import hashlib
import json
import sys
from pathlib import Path

import research_protocol.v2 as v2

MISSION = Path(sys.argv[1])
CRYPTO_FIXTURES = MISSION.parent / "integration-crypto" / "fixtures" / "v2"
CRYPTO_MANIFEST_SHA256 = "064673a1ffac074b09596369c28e63b2b0ab1f93a15ec56f7e1c6abc92650721"
RESEARCH = "brasileirao:RESEARCH-INTEGRATION-QUALIFICATION"
REAL = ("brasileirao:QUAL-SERVING-REAL-001", "brasileirao:QUAL-SERVING-REAL-002", "brasileirao:QUAL-SERVING-REAL-003")
DATASET_AS_OF = "2026-09-08T19:31:32Z"
REAL_REFS = {"dataset": ("real-20260908", "1"), "model": ("serving-baseline", "1"),
             "features": ("elo-home-advantage", "1"), "baseline": ("market", "1"),
             "cost_model": ("close-slippage-tax", "1"), "odds": ("sofascore-close", "1")}
N1_AS_OF = "2026-09-27T00:00:00Z"
LOOP_HYPOTHESIS = "brasileirao:CAIN-LOOP.BR-ELO-TUNING-DEV2022"
LOOP_FAMILY = "brasileirao-elo-1x2-dev2022"
REFUTED_TRIALS = ("h1-ou25-edge-2-15-walkforward", "H4_DIXON_COLES_CALIBRATED", "h11-refit-cadence-rodada-vs-100jogos",
                  "market-03-edge-ordering-sofascore-diagnostic", "market-04-ou25-btts-resolution-and-ordering",
                  "market-06-ou25-dev-only-ordering-triage")
PROTECTED = ("H8", "H9", "H14", "H15", "A1")
SOAK_SEASONS = (2021, 2022, 2023, 2024)


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def real_request(request_id: str, hypothesis: str, *, season: int, target: str, baseline: str = "market",
                 window: tuple[str, str] | None = None, data_cutoff: str = DATASET_AS_OF,
                 dataset: str = "real-20260908") -> dict:
    refs = {kind: {"name": name, "version": version} for kind, (name, version) in REAL_REFS.items()}
    refs["dataset"]["name"] = dataset
    refs["baseline"]["name"] = baseline
    start, end = window or (f"{season}-01-01T00:00:00Z", f"{season + 1}-01-01T00:00:00Z")
    return {"schema_version": "brasileirao-research-request/1", "request_id": request_id,
            "request_type": "WALKFORWARD_FORECAST_EVALUATION", "research_id": RESEARCH, "hypothesis_id": hypothesis,
            "competition": "Brasileirão Série A", "season": season, "target": target,
            "events": {"kickoff_from": start, "kickoff_to": end}, "data_cutoff": data_cutoff,
            "decision_lead_minutes": 60, "references": refs, "priority_hint": "NORMAL"}


def proposal(pid: str, req: dict, *, domain: str = "brasileirao", rationale: str = "", **extra) -> dict:
    return {"schema": "cain-proposal/1", "proposal_id": f"cain:{pid}", "domain": domain, "request": req,
            "based_on": [], "rationale": rationale, "source": "agenda", **extra}


def dump(path: Path, value: dict) -> bytes:
    raw = json.dumps(value, indent=1, ensure_ascii=False, sort_keys=True).encode("utf-8") + b"\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)
    return raw


def fixture_request(domain: str, label: str) -> dict:
    task = json.loads((CRYPTO_FIXTURES / domain / f"task-{label}.json").read_bytes())
    return {k: v for k, v in task["payload"].items() if k != "client_ref"}


def soak_schedule() -> list[dict]:
    """24 pedidos distintos, determinísticos: temporada × alvo × baseline × janela (temporada inteira ou 2º semestre)."""
    combos = []
    for window in ("season", "second-half"):
        for baseline in ("market", "climatology"):
            for target in ("1X2", "OU25"):
                for season in SOAK_SEASONS:
                    combos.append({"season": season, "target": target, "baseline": baseline, "window": window})
    return combos[:24]


def main() -> int:
    manifest_raw = (CRYPTO_FIXTURES / "FIXTURES_MANIFEST.json").read_bytes()
    if sha(manifest_raw) != CRYPTO_MANIFEST_SHA256:
        raise SystemExit("FIXTURES_MANIFEST.json da integration-crypto diverge do sha256 congelado")
    manifest = json.loads(manifest_raw)
    for rel, entry in manifest["files"].items():
        if sha((CRYPTO_FIXTURES / rel).read_bytes()) != entry["sha256"]:
            raise SystemExit(f"fixture {rel} diverge do FIXTURES_MANIFEST.json")
    files: dict[str, dict] = {}

    def put(rel: str, value: dict) -> str:
        files[rel] = {"sha256": sha(dump(MISSION / rel, value))}
        return rel

    crypto_h9 = fixture_request("crypto", "h9")
    stocks_h9 = fixture_request("stocks", "h9")
    brasileirao_h9 = fixture_request("brasileirao", "h9")
    # ------------------------------------------------------------------ E2E (dado real, só 2021–2024)
    canary_window = ("2024-07-01T00:00:00Z", "2024-10-01T00:00:00Z")
    e2e = {
        "01-allow": (proposal("IB-E2E-01", real_request("brasileirao:REQ-IB-E2E-001", REAL[0], season=2024,
                                                         target="OU25", window=canary_window),
                              rationale="primeiro episódio"), "ALLOW", None),
        "02-allow-restarts": (proposal("IB-E2E-02", real_request("brasileirao:REQ-IB-E2E-002", REAL[1], season=2023,
                                                                  target="1X2", baseline="climatology"),
                                       rationale="consumidor morto depois do domínio; CAIN morto na ingestão"),
                              "ALLOW", None),
        "03-canary": (proposal("IB-E2E-03", real_request("brasileirao:REQ-IB-E2E-003", REAL[2], season=2024,
                                                          target="1X2", window=canary_window,
                                                          data_cutoff="2024-10-01T00:00:00Z",
                                                          dataset="real-canary-20260908"),
                               rationale="canário FUTURE_CANARY_BR_INTEGRATION_001 depois do data_cutoff"),
                      "ALLOW", None),
        "04-canary-control": (proposal("IB-E2E-04", real_request("brasileirao:REQ-IB-E2E-004", REAL[2], season=2024,
                                                                  target="1X2", window=canary_window,
                                                                  data_cutoff="2024-10-01T00:00:00Z"),
                                       rationale="controle do canário: mesmo pedido sobre o dataset real sem canário"),
                              "ALLOW", None),
        "05-duplicate": (proposal("IB-E2E-05", real_request("brasileirao:REQ-IB-E2E-001", REAL[0], season=2024,
                                                             target="OU25", window=canary_window),
                                  rationale="mesmo conteúdo do 01"), "DUPLICATE", "DUPLICATE_REQUEST"),
        "06-h9-protected": (proposal("IB-E2E-06", real_request("brasileirao:REQ-IB-E2E-006", "brasileirao:H9",
                                                                season=2024, target="OU25")),
                            "BLOCK", "HYPOTHESIS_CLOSED"),
        "07-crypto-h9": (proposal("IB-E2E-07", crypto_h9, domain="crypto"), "BLOCK", "DOMAIN_MISMATCH"),
        "08-stocks-h9": (proposal("IB-E2E-08", stocks_h9, domain="stocks"), "BLOCK", "DOMAIN_MISMATCH"),
        "09-frozen-family": (proposal("IB-E2E-09", real_request("brasileirao:REQ-IB-E2E-009", REAL[0], season=2022,
                                                                 target="1X2"),
                                      hypothesis_family=LOOP_FAMILY,
                                      rationale="família congelada do loop do PR #50 com hipótese de qualificação"),
                             "BLOCK", "HYPOTHESIS_CLOSED"),
        "10-next": (proposal("IB-E2E-10", real_request("brasileirao:REQ-IB-E2E-010", REAL[0], season=2022,
                                                        target="1X2"),
                             rationale="N+1 depois dos resultados"), "ALLOW", None),
    }
    plan = []
    for name, (value, expected, reason) in e2e.items():
        item = {"proposal": put(f"fixtures/proposals/e2e/{name}.json", value), "expected_decision": expected}
        if reason:
            item["expected_reason"] = reason
        plan.append(item)
    # ------------------------------------------------------------------ N+1 (fixture congelada da Etapa A, sintética)
    seed = fixture_request("brasileirao", "etapa-a")

    def variant(request_id: str, **changes) -> dict:
        value = copy.deepcopy(seed)
        value["request_id"] = request_id
        for key, val in changes.items():
            value[key] = val
        return value

    llm_shape = variant("brasileirao:REQ-IB-N1-021")
    llm_shape["parameters"] = {"placebo_seed": 212}
    other_ref = variant("brasileirao:REQ-IB-N1-020")
    other_ref["references"]["dataset"] = {"name": "real-other", "version": "1"}
    n1 = {
        "01-next": (variant("brasileirao:REQ-IB-N1-001"), {}, "ALLOW", None),
        "02-duplicate": (copy.deepcopy(seed), {}, "DUPLICATE", "DUPLICATE_REQUEST"),
        "03-crypto-h9": (crypto_h9, {"domain": "crypto"}, "BLOCK", "DOMAIN_MISMATCH"),
        "04-brasileirao-h9": (brasileirao_h9, {}, "BLOCK", "HYPOTHESIS_CLOSED"),
        "05-stocks-h9": (stocks_h9, {"domain": "stocks"}, "BLOCK", "DOMAIN_MISMATCH"),
        "06-new-hypothesis": (variant("brasileirao:REQ-IB-N1-006", hypothesis_id="brasileirao:QUAL-NEW-001"), {},
                              "REQUIRE_HUMAN", "NEW_HYPOTHESIS"),
    }
    for number, name in enumerate(PROTECTED, start=7):
        n1[f"{number:02d}-protected-{name.lower()}"] = (
            variant(f"brasileirao:REQ-IB-N1-{number:03d}", hypothesis_id=f"brasileirao:{name}"), {}, "BLOCK",
            "HYPOTHESIS_CLOSED")
    for number, trial in enumerate(REFUTED_TRIALS, start=12):
        n1[f"{number:02d}-refuted-{number - 11}"] = (
            variant(f"brasileirao:REQ-IB-N1-{number:03d}", hypothesis_id=f"brasileirao:{trial}"), {}, "BLOCK",
            "HYPOTHESIS_CLOSED")
    n1.update({
        "18-loop-hypothesis": (variant("brasileirao:REQ-IB-N1-018", hypothesis_id=LOOP_HYPOTHESIS), {}, "BLOCK",
                               "HYPOTHESIS_CLOSED"),
        "19-loop-family": (variant("brasileirao:REQ-IB-N1-019"), {"hypothesis_family": LOOP_FAMILY}, "BLOCK",
                           "HYPOTHESIS_CLOSED"),
        "20-reference-not-allowed": (other_ref, {}, "BLOCK", "REFERENCE_NOT_ALLOWED"),
        "21-llm-shape": (llm_shape, {}, "BLOCK", "SCHEMA_INVALID"),
        "22-high-priority": (variant("brasileirao:REQ-IB-N1-022", priority_hint="HIGH"), {}, "BLOCK",
                             "PRIORITY_ABOVE_CAP"),
        "23-unqualified-id": (variant("brasileirao:REQ-IB-N1-023", hypothesis_id="H9"), {}, "BLOCK",
                              "DOMAIN_MISMATCH"),
    })
    n1_plan = []
    for number, (name, (req, extra, expected, reason)) in enumerate(n1.items(), start=1):
        extra = dict(extra)
        domain = extra.pop("domain", "brasileirao")
        rel = put(f"fixtures/proposals/n1/{name}.json", proposal(f"IB-N1-{number:02d}", req, domain=domain, **extra))
        item = {"proposal": rel, "expected_decision": expected}
        if reason:
            item["expected_reason"] = reason
        n1_plan.append(item)
    seed_rel = put("fixtures/proposals/n1/00-seed-etapa-a.json",
                   proposal("IB-N1-SEED", copy.deepcopy(seed), rationale="episódio 1 do estado do N+1"))
    # ------------------------------------------------------------------ holdout (D-25 (2)): só receipt, nunca despachado
    holdout = {
        "01-season-2025": variant("brasileirao:REQ-IB-HOLDOUT-001", season=2025,
                                  events={"kickoff_from": "2025-01-01T00:00:00Z", "kickoff_to": "2026-01-01T00:00:00Z"},
                                  data_cutoff=DATASET_AS_OF),
        "02-window-into-2025": variant("brasileirao:REQ-IB-HOLDOUT-002", season=2024,
                                       events={"kickoff_from": "2024-10-01T00:00:00Z",
                                               "kickoff_to": "2025-03-01T00:00:00Z"},
                                       data_cutoff=DATASET_AS_OF),
        "03-season-2026": variant("brasileirao:REQ-IB-HOLDOUT-003", season=2026,
                                  events={"kickoff_from": "2026-01-01T00:00:00Z", "kickoff_to": DATASET_AS_OF},
                                  data_cutoff=DATASET_AS_OF),
    }
    holdout_plan = []
    for number, (name, req) in enumerate(holdout.items(), start=1):
        rel = put(f"fixtures/proposals/holdout/{name}.json",
                  proposal(f"IB-HOLDOUT-{number:02d}", req, rationale="exigiria o holdout 2025 (D-25 (2))"))
        holdout_plan.append({"proposal": rel, "expected_decision": "REQUIRE_HUMAN", "dispatch": "nunca"})
    # ------------------------------------------------------------------ contradição (derivada, declarada)
    stage_a = json.loads((CRYPTO_FIXTURES / "brasileirao/result-etapa-a.json").read_bytes())
    base_result = json.loads(stage_a["result"]["payload_canonical"])
    adapter = {"distribution": "brasileirao-predictor", "module": "fixture:contradicao-derivada",
               "version": "25cdf4d9bb30"}
    previous = None
    contradiction = []
    for number, (label, state, scientific, economic) in enumerate(
        (("supported", "WATCH_NO_CAPITAL", "SUPPORTED", "WATCH"), ("refuted", "REFUTED", "REFUTED", "NO_EDGE"),
         ("refuted-again", "REFUTED", "REFUTED", "NO_EDGE")),
        start=1,
    ):
        req = variant(f"brasileirao:REQ-IB-CONTRA-00{number}")
        prop_rel = put(f"fixtures/proposals/contradiction/{number:02d}-{label}.json",
                       proposal(f"IB-CONTRA-{number}", req))
        task = v2.build_task("brasileirao", req, episode_id=v2.episode_id_for("brasileirao", number),
                             proposal_id=f"cain:IB-CONTRA-{number}", created_at=N1_AS_OF, previous_task_id=previous)
        previous = task["task_id"]
        res = dict(copy.deepcopy(base_result), request_id=req["request_id"], result_state=state,
                   scientific_state=scientific, economic_state=economic,
                   result_id=f"brasileirao:RESULT-CONTRA{number:027d}",
                   experiment_id=f"brasileirao:EXP-CONTRA{number:030d}")
        outcome = {"status": "RESULT", "exit_code": 0, "request_id": req["request_id"],
                   "client_ref": task["payload"]["client_ref"], "result": res}
        result = v2.build_result(task, outcome, adapter=adapter, produced_at=N1_AS_OF)
        for kind, raw in (("task", v2.dumps_task(task)), ("result", v2.dumps_result(result, task=task))):
            rel = f"fixtures/v2/brasileirao/contradiction-{label}-{kind}.json"
            (MISSION / rel).parent.mkdir(parents=True, exist_ok=True)
            (MISSION / rel).write_bytes(raw)
            files[rel] = {"sha256": sha(raw)}
        step = {"proposal": prop_rel, "expected_decision": "ALLOW",
                "result": f"fixtures/v2/brasileirao/contradiction-{label}-result.json"}
        if number == 3:
            step.update({"expected_decision": "REQUIRE_HUMAN", "expected_reason": "CONTRADICTION_UNRESOLVED",
                         "result_expected": "TASK_NOT_FOUND (nenhuma task emitida: a maioria não se forma)"})
        contradiction.append(step)
    contradiction.append({"proposal": put("fixtures/proposals/contradiction/04-after.json",
                                          proposal("IB-CONTRA-4", variant("brasileirao:REQ-IB-CONTRA-004"),
                                                   rationale="depois de 1 SUPPORTED e 2 REFUTED")),
                          "expected_decision": "REQUIRE_HUMAN", "expected_reason": "CONTRADICTION_UNRESOLVED"})
    crypto_files = {f"../integration-crypto/fixtures/v2/{rel}": {"sha256": e["sha256"]}
                    for rel, e in manifest["files"].items()}
    crypto_files["../integration-crypto/fixtures/v2/FIXTURES_MANIFEST.json"] = {"sha256": CRYPTO_MANIFEST_SHA256}
    doc = {
        "schema": "integration-brasileirao/FROZEN_VECTORS/1",
        "frozen_before": "fases e2e, n-plus-1, isolation-ids-contradiction, idempotency-failure, windows-smoke e soak",
        "identity": "sha256 dos bytes de cada arquivo (caminho relativo a qualification/integration-brasileirao/)",
        "real_data_rule": "os pedidos só nomeiam referências do operador (dataset real-20260908 / real-canary-20260908 "
                          "capturados no runtime privado); nenhum valor do dado real está nestes arquivos",
        "e2e_plan": plan,
        "n_plus_1": {
            "as_of": N1_AS_OF, "seed": seed_rel, "processes": 3,
            "state_results": ["../integration-crypto/fixtures/v2/brasileirao/result-etapa-a.json",
                              "../integration-crypto/fixtures/v2/brasileirao/result-h9.json",
                              "../integration-crypto/fixtures/v2/crypto/result-etapa-a.json",
                              "../integration-crypto/fixtures/v2/crypto/result-h9.json",
                              "../integration-crypto/fixtures/v2/stocks/result-etapa-a.json",
                              "../integration-crypto/fixtures/v2/stocks/result-h9.json"],
            "candidates": n1_plan,
        },
        "holdout": {
            "rule": "D-25 (2): proposta que exigiria acesso ao holdout 2025 resulta em REQUIRE_HUMAN; leitura "
                    "conservadora: temporada 2025, janela de kickoff que entra em 2025 ou temporada 2026 (treina com "
                    "resultados de 2025). Só decision-receipt no estado do N+1; nunca despachadas. Gate DECISION_POLICY",
            "as_of": N1_AS_OF, "plan": holdout_plan,
        },
        "contradiction": {
            "derivation": "resultado da Etapa A do Brasileirão (fixture V2 congelada, dataset sintético) com "
                          "result_state/scientific/economic, request_id, result_id e experiment_id trocados; mesma "
                          "hipótese brasileirao:HQ-SERVING-BASELINE; não é resultado de domínio, é vetor do CAIN",
            "plan": contradiction, "as_of": N1_AS_OF,
            "why": "SUPPORTED × REFUTED na mesma hipótese: o CAIN para e pede humano; os dois fatos ficam na memória; "
                   "um terceiro resultado não entra e nada é decidido por maioria",
        },
        "future_canary": {
            "token": "FUTURE_CANARY_BR_INTEGRATION_001",
            "vector": "fixtures/proposals/e2e/03-canary.json, com o controle fixtures/proposals/e2e/04-canary-control.json",
        },
        "soak_generator": {"hypotheses": list(REAL), "request_id": "brasileirao:REQ-IB-SOAK-<nnn>",
                           "template": "real_request(request_id, hypotheses[(n-1) % 3], **schedule[n-1]); window "
                                       "'season' = temporada inteira, 'second-half' = <season>-07-01 a <season+1>-01-01",
                           "schedule": soak_schedule(), "dataset": "real-20260908 1", "cycles": 24},
        "files": dict(sorted({**files, **crypto_files}.items())),
    }
    raw = json.dumps(doc, indent=1, ensure_ascii=False).encode("utf-8") + b"\n"
    (MISSION / "FROZEN_VECTORS.json").write_bytes(raw)
    print("FROZEN_VECTORS.json", sha(raw), len(doc["files"]), "arquivos")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
