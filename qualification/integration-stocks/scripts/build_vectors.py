"""integration-stocks: vetores congelados das fases e2e, n-plus-1, isolation-ids-contradiction e soak (C15: antes).

Gera, de forma determinística, e grava FROZEN_VECTORS.json com o sha256 de cada arquivo:
  * fixtures/proposals/e2e/*.json      propostas cain-proposal/1 do E2E com dados reais públicos (B3/CVM). O pedido do
                                       Stocks exige ``as_of`` = ``data_cutoff`` do painel admitido, e cada run tem pin
                                       novo das fontes (D-16, D-21): o ``as_of`` destes modelos é o marcador
                                       AS_OF_MARKER e o harness o troca pelo ``data_cutoff`` do painel construído no
                                       run (REAL_ENV.json), sem tocar em mais nada; o arquivo efetivo vai para o log;
  * fixtures/proposals/n1/*.json       candidatas do N+1 (receipt em 3 processos novos, as_of congelado), sobre o
                                       resultado real da Etapa A do Stocks (fixture V2 congelada da integration-crypto);
  * fixtures/proposals/contradiction/  propostas da contradição e o par V2 derivado (SUPPORTED × REFUTED);
  * as fixtures V2 dos três domínios são as da integration-crypto (qualification/integration-crypto/fixtures/v2/,
    FIXTURES_MANIFEST.json), lidas por caminho + sha256, sem cópia e sem mudança.
Nada é escolhido olhando resultado.

Uso (ferramentas da missão: tools/uv.lock): python build_vectors.py <qualification/integration-stocks>
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
AS_OF_MARKER = "AS_OF:PINNED_PANEL_DATA_CUTOFF"
RESEARCH = "stocks:RESEARCH-INTEGRATION-QUALIFICATION"
REAL = ("stocks:QUAL-PIT-MOM-REAL-001", "stocks:QUAL-PIT-MOM-REAL-002", "stocks:QUAL-PIT-MOM-REAL-003")
REAL_REFS = {"dataset": ("b3-cvm-real", "v1"), "universe": ("real", "v1"), "features": ("momentum-12-1", "v1"),
             "model": ("quintile-real", "v1"), "baseline": ("ew-universe", "v1"), "cost_model": ("h1-frozen", "v1"),
             "readiness": ("matrix-20260921", "v1")}
N1_AS_OF = "2026-09-27T00:00:00Z"
# ciclo 2 (cain com R17: o mesmo experimento com outro ID não roda de novo): pedidos que precisam ser experimentos
# distintos levam um controle negativo com semente própria (parameters.negative_control, do request_schema do Stocks;
# o backtest real não tem semente). As hipóteses de qualificação só para o LLM têm, cada uma, o seu (overlay).
CONTROL_KIND = "SHUFFLED_LABELS"
LLM = tuple(f"stocks:QUAL-LLM-CTRL-{k:03d}" for k in range(1, 6))
LLM_SEED = {h: 9000 + k for k, h in enumerate(LLM, start=1)}
CYCLE1 = "FROZEN_VECTORS_cycle1_3ad4d197cb79.json"  # ciclo 1 preservado byte a byte (C15.1, encadeamento)


def control(request: dict, seed: int) -> dict:
    request["parameters"] = dict(request["parameters"], negative_control={"kind": CONTROL_KIND, "seed": seed})
    return request


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def real_request(request_id: str, hypothesis: str, *, dataset: str = "b3-cvm-real") -> dict:
    refs = {kind: {"name": name, "version": version} for kind, (name, version) in REAL_REFS.items()}
    refs["dataset"]["name"] = dataset
    return {"schema_version": "stocks-research-request/1", "request_id": request_id,
            "request_type": "BACKTEST_PIT_FACTOR", "research_id": RESEARCH, "hypothesis_id": hypothesis,
            "references": refs, "as_of": AS_OF_MARKER,
            "pit": {"availability_rule": "AVAILABLE_AT_LE_DECISION_TIME", "minimum_pit_class": "PIT_RECONSTRUCTED"},
            "parameters": {"target": "NEXT_REBALANCE_RETURN", "fee_bps": 3, "slippage_bps": 15, "max_securities": 5000,
                           "external_intelligence": {"mode": "NONE", "families": []}},
            "priority_hint": "NORMAL"}


def proposal(pid: str, req: dict, *, domain: str = "stocks", rationale: str = "", **extra) -> dict:
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
    brasileirao_h9 = fixture_request("brasileirao", "h9")
    # ------------------------------------------------------------------ E2E (dados reais)
    e2e = {
        "01-allow": (proposal("IS-E2E-01", real_request("stocks:REQ-IS-E2E-001", REAL[0]),
                              rationale="primeiro episódio"), "ALLOW", None),
        "02-allow-restarts": (proposal("IS-E2E-02", control(real_request("stocks:REQ-IS-E2E-002", REAL[1]), 2),
                                       rationale="consumidor morto depois do domínio; CAIN morto na ingestão"),
                              "ALLOW", None),
        "03-canary": (proposal("IS-E2E-03", real_request("stocks:REQ-IS-E2E-003", REAL[2], dataset="b3-cvm-real-canary"),
                               rationale="canário pós-cutoff"), "ALLOW", None),
        "04-duplicate": (proposal("IS-E2E-04", real_request("stocks:REQ-IS-E2E-001", REAL[0]),
                                  rationale="mesmo conteúdo do 01"), "DUPLICATE", "DUPLICATE_REQUEST"),
        "05-h9-closed": (proposal("IS-E2E-05", real_request("stocks:REQ-IS-E2E-005", "stocks:H9")), "BLOCK",
                         "HYPOTHESIS_CLOSED"),
        "06-crypto-h9": (proposal("IS-E2E-06", crypto_h9, domain="crypto"), "BLOCK", "DOMAIN_MISMATCH"),
        "07-frozen-family": (proposal("IS-E2E-07", real_request("stocks:REQ-IS-E2E-007", REAL[0]),
                                      hypothesis_family="momentum_12_1",
                                      rationale="família congelada da H1 com hipótese de qualificação"), "BLOCK",
                             "HYPOTHESIS_CLOSED"),
        "08-next": (proposal("IS-E2E-08", control(real_request("stocks:REQ-IS-E2E-008", REAL[0]), 8),
                             rationale="N+1 depois dos resultados"), "ALLOW", None),
    }
    plan = []
    for name, (value, expected, reason) in e2e.items():
        item = {"proposal": put(f"fixtures/proposals/e2e/{name}.json", value), "expected_decision": expected}
        if reason:
            item["expected_reason"] = reason
        plan.append(item)
    # ------------------------------------------------------------------ N+1 (fixture congelada da Etapa A)
    seed = fixture_request("stocks", "etapa-a")
    stocks_h9 = fixture_request("stocks", "h9")

    def variant(request_id: str, **changes) -> dict:
        value = copy.deepcopy(seed)
        value["request_id"] = request_id
        for key, val in changes.items():
            value[key] = val
        return value

    fee_zero = variant("stocks:REQ-IS-N1-010")
    fee_zero["parameters"]["fee_bps"] = 0
    llm_shape = variant("stocks:REQ-IS-N1-012")
    llm_shape["parameters"]["placebo_seed"] = 212
    other_ref = variant("stocks:REQ-IS-N1-014")
    other_ref["references"]["dataset"] = {"name": "b3-cvm-other", "version": "v1"}
    collection = {"schema_version": "stocks-research-request/1", "request_id": "stocks:REQ-IS-N1-011",
                  "request_type": "COLLECT_EXTERNAL_INTELLIGENCE", "research_id": "stocks:RESEARCH-D16-EI-COLLECTION",
                  "hypothesis_id": "stocks:QUAL-EI-COLLECTION-001",
                  "references": {"source": {"name": "vlmo-real", "version": "v1"},
                                 "readiness": {"name": "matrix-20260921", "version": "v1"}},
                  "as_of": "2026-09-24T03:00:00Z",
                  "pit": {"availability_rule": "AVAILABLE_AT_LE_DECISION_TIME", "minimum_pit_class": "PIT_STRICT"},
                  "parameters": {"collector": "cvm-vlmo", "period": "2026", "observed_at": "2026-09-24T03:00:00Z"},
                  "priority_hint": "NORMAL"}
    n1 = {
        "01-next": (control(variant("stocks:REQ-IS-N1-001"), 1), {}, "ALLOW", None),
        "02-duplicate": (copy.deepcopy(seed), {}, "DUPLICATE", "DUPLICATE_REQUEST"),
        "03-crypto-h9": (crypto_h9, {"domain": "crypto"}, "BLOCK", "DOMAIN_MISMATCH"),
        "04-stocks-h9": (stocks_h9, {}, "BLOCK", "HYPOTHESIS_CLOSED"),
        "05-brasileirao-h9": (brasileirao_h9, {"domain": "brasileirao"}, "BLOCK", "DOMAIN_MISMATCH"),
        "06-new-hypothesis": (variant("stocks:REQ-IS-N1-006", hypothesis_id="stocks:QUAL-NEW-001"), {},
                              "REQUIRE_HUMAN", "NEW_HYPOTHESIS"),
        "07-h1-momentum": (variant("stocks:REQ-IS-N1-007", hypothesis_id="stocks:H1"), {}, "BLOCK",
                           "HYPOTHESIS_CLOSED"),
        "08-h2-low-vol": (variant("stocks:REQ-IS-N1-008", hypothesis_id="stocks:H2"), {}, "BLOCK", "HYPOTHESIS_CLOSED"),
        "09-h14-52w-high": (variant("stocks:REQ-IS-N1-009", hypothesis_id="stocks:H14"), {}, "BLOCK",
                            "HYPOTHESIS_CLOSED"),
        "10-h15-volume": (variant("stocks:REQ-IS-N1-015", hypothesis_id="stocks:H15"), {}, "BLOCK",
                          "HYPOTHESIS_CLOSED"),
        "11-family-momentum": (variant("stocks:REQ-IS-N1-016"), {"hypothesis_family": "momentum_12_1"}, "BLOCK",
                               "HYPOTHESIS_CLOSED"),
        "12-family-low-vol": (variant("stocks:REQ-IS-N1-017"), {"hypothesis_family": "low_vol_252"}, "BLOCK",
                              "HYPOTHESIS_CLOSED"),
        "13-family-52w-high": (variant("stocks:REQ-IS-N1-018"), {"hypothesis_family": "near_52w_high"}, "BLOCK",
                               "HYPOTHESIS_CLOSED"),
        "14-family-volume": (variant("stocks:REQ-IS-N1-019"), {"hypothesis_family": "volume_surge"}, "BLOCK",
                             "HYPOTHESIS_CLOSED"),
        "15-watch-high-priority": (variant("stocks:REQ-IS-N1-020", priority_hint="HIGH"), {}, "BLOCK",
                                   "PRIORITY_ABOVE_CAP"),
        "16-cost-mismatch": (fee_zero, {}, "BLOCK", "COST_MODEL_MISMATCH"),
        # ciclo 2: a R06 só compara custos onde a variante do contrato os declara (cain#62; IS-F002)
        "17-collection": (collection, {}, "ALLOW", None),
        "18-llm-shape": (llm_shape, {}, "BLOCK", "SCHEMA_INVALID"),
        "19-unqualified-id": (variant("stocks:REQ-IS-N1-021", hypothesis_id="H9"), {}, "BLOCK", "DOMAIN_MISMATCH"),
        "20-reference-not-allowed": (other_ref, {}, "BLOCK", "REFERENCE_NOT_ALLOWED"),
    }
    n1_plan = []
    for number, (name, (req, extra, expected, reason)) in enumerate(n1.items(), start=1):
        extra = dict(extra)
        domain = extra.pop("domain", "stocks")
        rel = put(f"fixtures/proposals/n1/{name}.json", proposal(f"IS-N1-{number:02d}", req, domain=domain, **extra))
        item = {"proposal": rel, "expected_decision": expected}
        if reason:
            item["expected_reason"] = reason
        n1_plan.append(item)
    seed_rel = put("fixtures/proposals/n1/00-seed-etapa-a.json",
                   proposal("IS-N1-SEED", copy.deepcopy(seed), rationale="episódio 1 do estado do N+1"))
    # ------------------------------------------------------------------ contradição (derivada, declarada)
    stage_a = json.loads((CRYPTO_FIXTURES / "stocks/result-etapa-a.json").read_bytes())
    base_result = json.loads(stage_a["result"]["payload_canonical"])
    adapter = {"distribution": "stocks-predictor", "module": "fixture:contradicao-derivada", "version": "61fc017256ff"}
    previous = None
    contradiction = []
    for number, (label, state, scientific, economic) in enumerate(
        (("supported", "WATCH_NO_CAPITAL", "SUPPORTED", "WATCH"), ("refuted", "REFUTED", "REFUTED", "NO_EDGE"),
         ("refuted-again", "REFUTED", "REFUTED", "NO_EDGE")),
        start=1,
    ):
        req = variant(f"stocks:REQ-IS-CONTRA-00{number}")
        if number > 1:  # ciclo 2: cada resultado vem de um experimento distinto (senão a R17 barra o 2º)
            control(req, number)
        prop_rel = put(f"fixtures/proposals/contradiction/{number:02d}-{label}.json", proposal(f"IS-CONTRA-{number}", req))
        task = v2.build_task("stocks", req, episode_id=v2.episode_id_for("stocks", number),
                             proposal_id=f"cain:IS-CONTRA-{number}", created_at=N1_AS_OF, previous_task_id=previous)
        previous = task["task_id"]
        res = dict(copy.deepcopy(base_result), request_id=req["request_id"], result_state=state,
                   scientific_state=scientific, economic_state=economic,
                   result_id=f"stocks:RESULT-CONTRA{number:027d}", experiment_id=f"stocks:EXP-CONTRA{number:030d}")
        outcome = {"status": "RESULT", "exit_code": 0, "request_id": req["request_id"],
                   "client_ref": task["payload"]["client_ref"], "result": res}
        result = v2.build_result(task, outcome, adapter=adapter, produced_at=N1_AS_OF)
        for kind, raw in (("task", v2.dumps_task(task)), ("result", v2.dumps_result(result, task=task))):
            rel = f"fixtures/v2/stocks/contradiction-{label}-{kind}.json"
            (MISSION / rel).parent.mkdir(parents=True, exist_ok=True)
            (MISSION / rel).write_bytes(raw)
            files[rel] = {"sha256": sha(raw)}
        step = {"proposal": prop_rel, "expected_decision": "ALLOW",
                "result": f"fixtures/v2/stocks/contradiction-{label}-result.json"}
        if number == 3:
            step.update({"expected_decision": "REQUIRE_HUMAN", "expected_reason": "CONTRADICTION_UNRESOLVED",
                         "result_expected": "TASK_NOT_FOUND (nenhuma task emitida: a maioria não se forma)"})
        contradiction.append(step)
    contradiction.append({"proposal": put("fixtures/proposals/contradiction/04-after.json",
                                          proposal("IS-CONTRA-4", control(variant("stocks:REQ-IS-CONTRA-004"), 4),
                                                   rationale="depois de 1 SUPPORTED e 2 REFUTED")),
                          "expected_decision": "REQUIRE_HUMAN", "expected_reason": "CONTRADICTION_UNRESOLVED"})
    # ------------------------------------------------------------------ ciclo 2: hipóteses só para o LLM
    # cada uma é um experimento distinto (controle negativo com semente própria); a fixture fixa o tipo de pedido
    # (o tools/build_domain_config.py do cain lê o tipo daqui) e o experimento que o molde do CAIN monta
    # (último backtest emitido, sem controle, + o overlay da hipótese)
    llm = {}
    for number, hypothesis in enumerate(LLM, start=1):
        req = control(real_request(f"stocks:REQ-IS-LLM-{number:03d}", hypothesis), LLM_SEED[hypothesis])
        rel = put(f"fixtures/proposals/llm/{number:02d}-{hypothesis.split(':')[1].lower()}.json",
                  proposal(f"IS-LLM-{number:02d}", req, rationale="hipótese de qualificação só para o LLM"))
        llm[hypothesis] = {"fixture": rel,
                           "overlay": {"negative_control": {"kind": CONTROL_KIND, "seed": LLM_SEED[hypothesis]}}}
    crypto_files = {f"../integration-crypto/fixtures/v2/{rel}": {"sha256": e["sha256"]}
                    for rel, e in manifest["files"].items()}
    crypto_files["../integration-crypto/fixtures/v2/FIXTURES_MANIFEST.json"] = {"sha256": CRYPTO_MANIFEST_SHA256}
    doc = {
        "schema": "integration-stocks/FROZEN_VECTORS/1",
        "frozen_before": "fases e2e, n-plus-1, isolation-ids-contradiction, idempotency-failure, windows-smoke e soak",
        "identity": "sha256 dos bytes de cada arquivo (caminho relativo a qualification/integration-stocks/)",
        "as_of_marker": {
            "marker": AS_OF_MARKER,
            "rule": "nos modelos do E2E e do soak, request.as_of = marcador; o harness o substitui pelo data_cutoff "
                    "do painel real construído no run (REAL_ENV.json, pin novo por run: D-16, D-21) e muda só esse "
                    "campo; o arquivo efetivo e o seu sha256 vão para o log bruto",
        },
        "e2e_plan": plan,
        "n_plus_1": {
            "as_of": N1_AS_OF, "seed": seed_rel, "processes": 3,
            "state_results": ["../integration-crypto/fixtures/v2/stocks/result-etapa-a.json",
                              "../integration-crypto/fixtures/v2/stocks/result-h9.json",
                              "../integration-crypto/fixtures/v2/crypto/result-etapa-a.json",
                              "../integration-crypto/fixtures/v2/crypto/result-h9.json",
                              "../integration-crypto/fixtures/v2/brasileirao/result-etapa-a.json",
                              "../integration-crypto/fixtures/v2/brasileirao/result-h9.json"],
            "candidates": n1_plan,
        },
        "contradiction": {
            "derivation": "resultado real da Etapa A do Stocks (fixture V2 congelada) com result_state/scientific/"
                          "economic, request_id, result_id e experiment_id trocados; mesma hipótese "
                          "stocks:QUAL-PIT-MOM-001; não é resultado de domínio, é vetor do CAIN",
            "plan": contradiction, "as_of": N1_AS_OF,
            "why": "SUPPORTED × REFUTED na mesma hipótese: o CAIN para e pede humano; os dois fatos ficam na memória; "
                   "um terceiro resultado não entra e nada é decidido por maioria",
        },
        "soak_generator": {"hypotheses": list(REAL), "request_id": "stocks:REQ-IS-SOAK-<nnn>",
                           "template": "real_request(request_id, hypotheses[(n-1) % 3]) com as_of do painel do run",
                           "negative_control": {"kind": CONTROL_KIND, "seed": "n (o número do ciclo), a partir do 2º",
                                                "first_cycle": "o backtest real sem controle (como no ciclo 1)",
                                                "why": "ciclo 2: com a R17, sem semente o backtest real é um só "
                                                       "experimento e o soak não passaria do 3º ciclo; o 1º ciclo "
                                                       "sem controle deixa o experimento real emitido, e o molde "
                                                       "emprestado de uma hipótese proponível sem task própria e sem "
                                                       "overlay (stocks:QUAL-PIT-MOM-001, que o operador desta "
                                                       "integração não admite) repete esse experimento (R17)"},
                           "llm_hypotheses": list(LLM), "dataset": "b3-cvm-real v1", "cycles": 24},
        "llm_hypotheses": llm,
        "cycle": {"number": 2,
                  "supersedes": {"file": CYCLE1, "sha256": sha((MISSION / CYCLE1).read_bytes())},
                  "why": "decisão do dono (2026-09-28): ciclo novo dos congelados na release única do cain com a "
                         "política v2 (R15–R17, R04 por hipótese, custos e semente pelo contrato) e hipóteses de "
                         "qualificação só para o LLM (overlay com controle negativo)",
                  "changes": ["e2e/02-allow-restarts e e2e/08-next com controle negativo (sementes 2 e 8)",
                              "n1/01-next com controle negativo (semente 1); n1/17-collection → ALLOW",
                              "contradição 02–04 com controle negativo (sementes 2–4)",
                              "soak: 1º ciclo sem controle; do 2º em diante, controle negativo com semente = número do ciclo",
                              "5 hipóteses stocks:QUAL-LLM-CTRL-001..005 (sementes 9001–9005)"]},
        "files": dict(sorted({**files, **crypto_files}.items())),
    }
    raw = json.dumps(doc, indent=1, ensure_ascii=False).encode("utf-8") + b"\n"
    (MISSION / "FROZEN_VECTORS.json").write_bytes(raw)
    print("FROZEN_VECTORS.json", sha(raw), len(doc["files"]), "arquivos")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
