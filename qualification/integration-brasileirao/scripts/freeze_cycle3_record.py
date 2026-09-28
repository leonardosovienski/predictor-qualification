"""integration-brasileirao, ciclo 3 da freeze-parameters: registra o ciclo nos arquivos da missão (sem tocar em RAW_LOGS).

A release única da decisão do dono ("rc8") foi publicada como cain v0.4.13rc10 (tag → fb0e1dc) e passou a levar também
os PRs da sessão STOCKS (cain#67–#69: R04 por hipótese, R17 DUPLICATE EQUIVALENT_REQUEST, justificativa do LLM
conferida). O ciclo 3 (FROZEN_PARAMETERS e FROZEN_VECTORS, gerados por freeze_parameters.py e build_vectors.py,
conferidos por cycle3_check.py) é registrado aqui:
  * runtime_targets.json: cain → v0.4.13rc10 (commit da tag, URL e sha256 do asset publicado);
  * GATES.json: ciclo 3 (o ciclo 2 fica em cycle_history), fase freeze-parameters-c3, nota do DECISION_POLICY;
  * FINDINGS.json: IB-F001 FIXED (o main do cain é o commit da release única); IB-F002 com a release publicada (fecha
    quando os vetores do holdout derem REQUIRE_HUMAN SEALED_SCOPE no N+1 da rc10);
  * QUALIFICATION_CHANGELOG.md: seção do ciclo 3.
Uso: python freeze_cycle3_record.py <qualification/integration-brasileirao>
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

Q = Path(sys.argv[1])
M = "qualification/integration-brasileirao"
TAG, COMMIT = "v0.4.13rc10", "fb0e1dcb9003130c0b5d50ecd95f7d8d0829cf0c"
URL = "https://github.com/leonardosovienski/cain/releases/download/v0.4.13rc10/cain_research-0.4.13rc10-py3-none-any.whl"
WHEEL_SHA = "752de98d385528b0bd90c950d117c46af0522125a2274ea9a7064461786b85e5"
EVIDENCE = [f"{M}/RAW_LOGS/freeze/freeze_parameters_cycle3.log", f"{M}/RAW_LOGS/freeze/cycle3_check.log",
            f"{M}/RAW_LOGS/freeze/cycle3_check.json", f"{M}/RAW_LOGS/freeze/cain_rc10_release.log"]


def sub(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    assert text.count(old) == 1, (path.name, old[:80])
    path.write_text(text.replace(old, new), encoding="utf-8")


def load(name: str):
    return json.loads((Q / name).read_text(encoding="utf-8"))


def dump(name: str, value, indent: int) -> None:
    (Q / name).write_text(json.dumps(value, indent=indent, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    sub(Q / "runtime_targets.json",
        ' "cain": {"repo": "leonardosovienski/cain", "version": "0.4.13rc9", "tag": "v0.4.13rc9",\n'
        '          "commit": "3e515fdcc6c15d193367e48a9ebd942d1aeba641",\n'
        '          "url": "https://github.com/leonardosovienski/cain/releases/download/v0.4.13rc9/'
        'cain_research-0.4.13rc9-py3-none-any.whl",\n'
        '          "sha256": "6e0d31a18642bbb7adfb371618633c4a2a36195fc3a560225381bd7a14f1ff45"},',
        f' "cain": {{"repo": "leonardosovienski/cain", "version": "0.4.13rc10", "tag": "{TAG}",\n'
        f'          "commit": "{COMMIT}",\n'
        f'          "url": "{URL}",\n'
        f'          "sha256": "{WHEEL_SHA}",\n'
        '          "note": "release única da decisão do dono (\'rc8\' nos textos dos ciclos 2 e 3), publicada pela sessão '
        'cripto; ciclo 1 usou a v0.4.13rc9 (3e515fd, 6e0d31a1…, política v1)"},')
    gates = load("GATES.json")
    gates["cycle_history"] = gates.get("cycle_history", []) + [gates["cycle"]]
    gates["cycle"] = {"number": 3, "why": "a release única (publicada como cain v0.4.13rc10, fb0e1dc) leva também "
                      "cain#67–#69 (R04 por hipótese, R17 DUPLICATE EQUIVALENT_REQUEST, justificativa do LLM); "
                      "rule_order e dois vetores novos no ciclo 3; brasileirao_config sem mudança (cycle3_check 13/0); "
                      "fases a partir do cleanroom-final na rc10 (C14)"}
    gates["phases_completed"].append("freeze-parameters-c3")
    gates["gates"]["DECISION_POLICY"]["note"] = (
        "ciclo 3: rc10 (política v2 com R16 e R17); vetores do holdout esperam REQUIRE_HUMAN SEALED_SCOPE; "
        "n1/24-equivalent-request espera DUPLICATE EQUIVALENT_REQUEST; no ciclo 1 (política v1) o holdout saiu ALLOW "
        "(IB-F002)")
    gates["freeze_cycle3_evidence"] = EVIDENCE
    dump("GATES.json", gates, 1)
    findings = load("FINDINGS.json")
    for f in findings["findings"]:
        if f["id"] == "IB-F001":
            f["status"] = "FIXED"
            f["resolution"] = (f"o main do cain é {COMMIT[:7]} = tag {TAG}, a release única que esta missão usa como "
                               "final_commit do cain (ciclo 3); não há mais main à frente do commit qualificado")
            f["evidence"].append({"file": f"{M}/RAW_LOGS/freeze/cain_rc10_release.log"})
        if f["id"] == "IB-F002":
            f["cycle_3"] = {"release": TAG, "commit": COMMIT, "wheel_sha256": WHEEL_SHA,
                            "config": "brasileirao.json da wheel com os 3 sealed_scopes, byte a byte o regenerado de "
                                      "417024e (cycle3_check.json)",
                            "closes_when": "os 3 vetores do holdout derem REQUIRE_HUMAN SEALED_SCOPE (R16) no N+1 da "
                                           "rc10, sem despacho"}
            f["evidence"].append({"file": f"{M}/RAW_LOGS/freeze/cycle3_check.json"})
    root = Q.parents[1]
    for f in findings["findings"]:
        for e in f.get("evidence", []):
            e.setdefault("sha256", hashlib.sha256((root / e["file"]).read_bytes()).hexdigest())
    dump("FINDINGS.json", findings, 2)
    log = Q / "QUALIFICATION_CHANGELOG.md"
    log.write_text(log.read_text(encoding="utf-8").rstrip("\n") + "\n\n" + CHANGELOG, encoding="utf-8")
    print("ok")
    return 0


CHANGELOG = f"""## Ciclo 3 da freeze-parameters (release única publicada como cain v0.4.13rc10)

A release única da decisão do dono ("rc8" nos textos) foi publicada pela sessão cripto como **cain {TAG}**
(tag → `{COMMIT[:7]}`, wheel sha256 `{WHEEL_SHA[:12]}…`), já que a v0.4.13rc9 existia (pré-release desta missão, política
v1). Ela leva também os PRs da sessão STOCKS: cain#67 (tipo de pedido por hipótese: R04 e molde do LLM), cain#68
(**R17 DUPLICATE EQUIVALENT_REQUEST**: o mesmo pedido sem request_id, hypothesis_id, research_id e client_ref, já rodado
ou pendente, não gera task; avaliada antes da R12) e cain#69 (justificativa do LLM conferida). Todos foram mergeados pelo
dono, junto com o cain#66 (lacres do Brasileirão).

| Arquivo | Mudança |
|---|---|
| `FROZEN_PARAMETERS.json` | `rule_order` com a R17 entre R11 e R12 e a R04 por hipótese; framework e ciclo 3; `brasileirao_config` sem mudança |
| `FROZEN_VECTORS.json` | `n1/01-next` e `contradiction/02-refuted` passam ao alvo OU25 (eram o mesmo experimento da semente e do 01-supported e esperavam ALLOW); tasks e resultados da contradição reencadeados; vetor novo `n1/24-equivalent-request` (DUPLICATE EQUIVALENT_REQUEST) |
| `*_cycle2_<sha12>.json` | os arquivos do ciclo 2 preservados byte a byte |
| `runtime_targets.json` | cain → {TAG} |
| `GATES.json`, `FINDINGS.json` | ciclo 3; IB-F001 FIXED; IB-F002 com a release publicada |

Conferência mecânica (`scripts/cycle3_check.py`, 13/0): o `brasileirao_config` é igual ao de `417024e`; só mudaram
`rule_order`, framework, ciclo e os ponteiros para os vetores novos; os vetores mudaram só onde foi declarado; o
`brasileirao.json` da wheel publicada é, byte a byte, o que o `tools/build_domain_config.py` do commit da release gera a
partir de `417024e`. Nenhum limiar, holdout, critério ou waiver muda.
"""


if __name__ == "__main__":
    raise SystemExit(main())
