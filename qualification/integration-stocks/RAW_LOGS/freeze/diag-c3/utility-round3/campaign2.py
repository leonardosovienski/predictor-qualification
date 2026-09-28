"""Rodada 2 de utilidade prática do CAIN com o Stocks, na cain 0.4.13rc12 publicada (não é qualificação).

Pergunta do dono: o CAIN tem as informações do Stocks e funciona na prática? Mesmo método da rodada 1 (campaign.py),
agora com o runtime qualificado do ciclo 2 (wheels publicadas: cain rc12, stocks rc3, transporte rc5) e mais casos:
  0. o que o CAIN sabe do Stocks: a configuração empacotada na wheel × o estado científico atual do Stocks (main);
  1. semente: backtest real proposto pelo operador;
  2. laço com o modelo local (`explain --propose-for-domain`), N ciclos, com a justificativa conferida pelo CAIN;
  3. guardas no uso: encerrada, família, nova, coleta, duplicata, o mesmo experimento com outro ID (R17), hipótese
     não admitida pelo operador (recusa do domínio e depois R15), canário do futuro, domínio estrangeiro, custo e
     prioridade;
  4. memória × leitura autoritativa (`stocks-research show`), busca, cubo, verify;
  5. `research explain` sem proposta (o que ele responde sobre o Stocks).
Cada comando é um processo novo e vai bruto para commands.log. Grava REPORT.json.
Uso: campaign2.py <out> <work> <qualification/integration-stocks> <ciclos> <modelo> <clone do stocks-predictor>
"""

from __future__ import annotations

import copy
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

MISSION = Path(sys.argv[3]).resolve()
sys.path.insert(0, str(MISSION / "scripts"))
from harness import Harness, now  # noqa: E402

QUESTION = ("Qual é o próximo experimento mais informativo para o Stocks, considerando o que já foi testado, os "
            "resultados e as recusas?")


def main() -> int:
    out, work, cycles, model, stocks = Path(sys.argv[1]), Path(sys.argv[2]), int(sys.argv[4]), sys.argv[5], Path(sys.argv[6])
    h = Harness(out, work, MISSION, "cain-utility-stocks-rc12")
    props = out / "proposals"
    props.mkdir(parents=True, exist_ok=True)
    report: dict = {"model": model, "cycles": [], "guards": [], "seed": None}

    def decide(label: str, proposal: Path) -> tuple[dict, float]:
        t0 = time.time()
        _c, lines, _ = h.propose(label, proposal, as_of=now())
        return (lines[0] if lines else {}), round(time.time() - t0, 3)

    def execute(label: str) -> dict:
        t0 = time.time()
        h.dispatch(f"dispatch {label}")
        _c, consumed, _ = h.consumer(f"consumer {label}")
        _c, ingested, _ = h.ingest(f"ingest {label}")
        return {"seconds": round(time.time() - t0, 3),
                "consumer": [c for c in consumed if c.get("action") != "skipped"], "ingest": ingested}

    # ------------------------------------------------------------------ 0. what the CAIN knows about the Stocks
    code = ("import json, importlib.resources as r; "
            "print(r.files('cain.orchestration').joinpath('data','stocks.json').read_text())")
    packaged = json.loads(subprocess.run([os.environ["CAIN_PY"], "-I", "-c", code], capture_output=True, text=True,
                                         check=True).stdout)
    main_sha = subprocess.run(["git", "-C", str(stocks), "rev-parse", "origin/main"], capture_output=True, text=True,
                              check=True).stdout.strip()
    state = json.loads(subprocess.run(["git", "-C", str(stocks), "show", f"{main_sha}:research/scientific_state.json"],
                                      capture_output=True, text=True, check=True).stdout)
    cfg_closed = {k.split(":", 1)[1]: v for k, v in packaged["closed_hypotheses"].items()}
    main_hyp = state["hypotheses"]
    report["knowledge"] = {
        "packaged_source": packaged["source"]["commit"], "stocks_main": main_sha,
        "closed_in_cain": len(cfg_closed), "hypotheses_in_main": len(main_hyp),
        "same_status": sorted(k for k in main_hyp if cfg_closed.get(k) == main_hyp[k]),
        "different_status": {k: {"cain": cfg_closed.get(k), "stocks_main": main_hyp[k]}
                             for k in sorted(set(main_hyp) | set(cfg_closed), key=lambda x: int(x[1:]))
                             if cfg_closed.get(k) != main_hyp.get(k)},
        "frozen_families_cain": packaged["frozen_families"], "frozen_families_main": state["frozen_families"],
        "families_only_in_main": sorted(set(state["frozen_families"]) - set(packaged["frozen_families"])),
        "families_only_in_cain": sorted(set(packaged["frozen_families"]) - set(state["frozen_families"])),
        "proposable": packaged["proposable_hypotheses"], "costs": packaged["costs"],
        "overlays": sorted(packaged.get("proposal_overlays", {})), "frozen_parameters": packaged["frozen_parameters"],
    }
    # ------------------------------------------------------------------ 1. seed
    seed = h.real_proposal("fixtures/proposals/e2e/01-allow.json", props / "seed.json")
    line, secs = decide("propose seed", seed)
    report["seed"] = {"decision": line, "decide_seconds": secs}
    if line.get("decision") == "ALLOW":
        report["seed"]["execution"] = execute("seed")
    # ------------------------------------------------------------------ 2. local-model loop
    cfg = work / "cain-llm.toml"
    cfg.write_text("\n".join(["[llm]", 'provider = "ollama"', f'model = "{model}"', 'base_url = "http://127.0.0.1:11434"',
                              "temperature = 0.0", "seed = 42", "timeout = 600.0", "num_ctx = 8192",
                              "num_predict = 256", "max_input_bytes = 16000", "think = false", ""]), encoding="utf-8")

    def llm_cycle(tag: str) -> dict:
        row: dict = {"cycle": tag}
        pf = props / f"llm-{tag}.json"
        t0 = time.time()
        code, lines, stdout = h.cain(f"llm proposal {tag}", "explain", QUESTION, "--propose-for-domain", "stocks",
                                     "--state", h.state, "--proposal-out", pf, "--proposal-id", f"cain:UTIL2-LLM-{tag}",
                                     "--config", cfg)
        row["model_seconds"] = round(time.time() - t0, 3)
        row["explain_exit"] = code
        if code != 0 or not pf.exists():
            row["explain_output"] = (stdout or "")[-700:]
            return row
        audit = json.loads(pf.with_suffix(".audit.json").read_text(encoding="utf-8"))
        proposal = json.loads(pf.read_text(encoding="utf-8"))
        request = proposal["request"]
        row.update({"hypothesis": request["hypothesis_id"], "request_type": request["request_type"],
                    "negative_control": request.get("parameters", {}).get("negative_control"),
                    "placebo_seed_in_request": "placebo_seed" in request.get("parameters", {}),
                    "eligible": sorted(k for k, v in audit["eligibility"].items() if v["decision"] == "ALLOW"),
                    "held": {k: f"{v['decision']} {v['reason_code']}" for k, v in audit["eligibility"].items()
                             if v["decision"] != "ALLOW"},
                    "rationale": proposal["rationale"], "rationale_check": audit["rationale_check"],
                    "audit_schema": audit.get("schema"), "model": audit["model"]})
        line, secs = decide(f"propose llm {tag}", pf)
        row["decision"] = {k: line.get(k) for k in ("decision", "reason_code", "rule", "task")}
        row["decide_seconds"] = secs
        if line.get("decision") == "ALLOW":
            row["execution"] = execute(f"llm {tag}")
        return row

    for i in range(1, cycles + 1):
        report["cycles"].append(llm_cycle(str(i)))
    # ------------------------------------------------------------------ 3. guards in practical use
    seed_doc = json.loads(seed.read_text(encoding="utf-8"))

    def variant(name: str, **request_changes) -> Path:
        doc = copy.deepcopy(seed_doc)
        doc["proposal_id"] = f"cain:UTIL2-{name}"
        params = request_changes.pop("parameters", None)
        doc["request"].update(request_changes)
        if params is not None:
            doc["request"]["parameters"] = params
        path = props / f"guard-{name}.json"
        path.write_text(json.dumps(doc), encoding="utf-8")
        return path

    control = lambda seed_n: dict(seed_doc["request"]["parameters"],  # noqa: E731
                                  negative_control={"kind": "SHUFFLED_LABELS", "seed": seed_n})
    guards = [
        ("closed hypothesis H1 (momentum)", h.real_proposal("fixtures/proposals/n1/07-h1-momentum.json",
                                                           props / "guard-07-h1.json")),
        ("frozen family momentum_12_1", h.real_proposal("fixtures/proposals/n1/11-family-momentum.json",
                                                       props / "guard-11-family.json")),
        ("new hypothesis outside the configuration", h.real_proposal("fixtures/proposals/n1/06-new-hypothesis.json",
                                                                    props / "guard-06-new.json")),
        ("External Intelligence collection", h.real_proposal("fixtures/proposals/n1/17-collection.json",
                                                             props / "guard-17-collection.json")),
        ("same content as the seed (duplicate)", h.real_proposal("fixtures/proposals/e2e/04-duplicate.json",
                                                                props / "guard-04-duplicate.json")),
        ("same experiment as the seed under another ID (R17)",
         variant("equivalent", request_id="stocks:REQ-UTIL2-EQUIV-1", hypothesis_id="stocks:QUAL-PIT-MOM-REAL-002")),
        ("hypothesis the operator does not admit (1st: domain refuses)",
         variant("not-admitted-1", request_id="stocks:REQ-UTIL2-NA-1", hypothesis_id="stocks:QUAL-PIT-MOM-001",
                 parameters=control(701))),
        ("same hypothesis again, other experiment (R15)",
         variant("not-admitted-2", request_id="stocks:REQ-UTIL2-NA-2", hypothesis_id="stocks:QUAL-PIT-MOM-001",
                 parameters=control(702))),
        ("future canary dataset", h.real_proposal("fixtures/proposals/e2e/03-canary.json", props / "guard-03-canary.json")),
        ("crypto proposal in the stocks orchestration", h.real_proposal("fixtures/proposals/n1/03-crypto-h9.json",
                                                                        props / "guard-03-crypto.json")),
        ("costs differ from the frozen cost model", h.real_proposal("fixtures/proposals/n1/16-cost-mismatch.json",
                                                                   props / "guard-16-cost.json")),
        ("priority above the cap", h.real_proposal("fixtures/proposals/n1/15-watch-high-priority.json",
                                                  props / "guard-15-priority.json")),
    ]
    for name, target in guards:
        line, secs = decide(f"propose guard {name}", target)
        row = {"guard": name, "proposal": target.name,
               "decision": {k: line.get(k) for k in ("decision", "reason_code", "rule", "detail", "task")},
               "decide_seconds": secs}
        if line.get("decision") == "ALLOW":
            row["execution"] = execute(f"guard {name}")
        report["guards"].append(row)
    # one more model call after the guards: what is still offered
    report["after_guards"] = llm_cycle("after-guards")
    # ------------------------------------------------------------------ 4. memory × authoritative domain
    mem = h.state / "memory.sqlite"
    cain = os.environ["CAIN_BIN"]
    _c, facts, _ = h.run("memory facts stocks", [cain, "memory", "--db", mem, "facts", "--as-of", "now", "--cube", "stocks"])
    _c, crypto, _ = h.run("memory facts crypto", [cain, "memory", "--db", mem, "facts", "--as-of", "now", "--cube", "crypto"])
    _c, search, _ = h.run("memory search momentum", [cain, "memory", "--db", mem, "search", "momentum", "--as-of", "now",
                                                     "--cube", "stocks", "--limit", "20"])
    vcode, verify, _ = h.run("memory verify", [cain, "memory", "--db", mem, "verify"])
    report["memory"] = {"facts_stocks": facts, "facts_crypto": crypto, "search_momentum": search,
                        "verify_exit": vcode, "verify": verify}
    compared = []
    for _path, result in h.results():
        if result.get("status") in ("RESULT", "DUPLICATE") and result.get("result"):
            code, shown = h.show(f"show {result['request_id']}", result["request_id"])
            compared.append({"request_id": result["request_id"], "status": result["status"],
                             "envelope_payload_sha256": result["result"]["payload_sha256"],
                             "show_sha256": shown.get("result_sha256"), "show_exit": code})
    report["authoritative"] = compared
    report["episodes"] = h.episodes("episodes final")
    h.no_canary("utility-rc12")
    report["canary_checks"] = [c for c in h.checks if "canary" in c["check"].lower() or "future" in c["check"].lower()]
    # ------------------------------------------------------------------ 5. research explain without a proposal
    probe_db = work / "research-probe.sqlite"
    code, lines, stdout = h.run("research explain (no proposal)",
                                [cain, "research", "--db", probe_db, "explain", "O que se sabe sobre momentum no Stocks?",
                                 "--domain", "stocks"])
    report["explain_no_proposal"] = {"exit": code, "output": stdout[-1500:]}
    (out / "REPORT.json").write_text(json.dumps(report, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    for f in props.glob("llm-*.json"):
        if not (out / f.name).exists():
            shutil.copy(f, out / f.name)
    print(json.dumps({"cycles": len(report["cycles"]), "guards": len(report["guards"]),
                      "results_compared": len(compared)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
