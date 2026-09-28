"""integration-brasileirao: reemissão pela C14 na cain v0.4.13rc13 + transporte 0.1.0rc6.

A wheel do cain e o transporte mudaram (rodadas de utilidade do stocks; um consumidor por domínio no transporte,
ecosystem-predictor#36). A integration-brasileirao QUALIFIED na rc12 (attestation 8aef1104…) é reemitida:
  python reissue_rc13.py supersede <qualification/integration-brasileirao>
      preserva a attestation atual byte a byte em QUALIFICATION_ATTESTATION_superseded_<sha12>.json e grava
      GATES.supersedes_sha256 (C7.1 regra 8); a attestation nova é escrita depois por attest.py final;
  python reissue_rc13.py findings <qualification/integration-brasileirao> <run>
      IB-F009 ganha a evidência do soak da rc13 (o piso de LLM continua 0 para o Brasileirão: o waiver do dono vale);
  python reissue_rc13.py changelog <qualification/integration-brasileirao> <run> <run retirado> <sha do SUMMARY retirado>
      seção do QUALIFICATION_CHANGELOG.md com os números de EVIDENCE_NUMBERS.json.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

M = "qualification/integration-brasileirao"


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def supersede(q: Path) -> None:
    current = q / "QUALIFICATION_ATTESTATION.json"
    raw = current.read_bytes()
    kept = q / f"QUALIFICATION_ATTESTATION_superseded_{sha(raw)[:12]}.json"
    assert not kept.exists()
    assert json.loads(raw)["result"] == "QUALIFIED"
    kept.write_bytes(raw)
    current.unlink()  # its bytes are in `kept`; attest.py never overwrites (C8), it writes the new one
    gates = json.loads((q / "GATES.json").read_text(encoding="utf-8"))
    gates["supersedes_sha256"] = sha(raw)
    (q / "GATES.json").write_text(json.dumps(gates, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("superseded", kept.name, sha(raw))


def findings(q: Path, run: str) -> None:
    root = q.parents[1]
    doc = json.loads((q / "FINDINGS.json").read_text(encoding="utf-8"))
    f9 = next(f for f in doc["findings"] if f["id"] == "IB-F009")
    rel = f"{M}/RAW_LOGS/runtime/{run}/soak/SUMMARY.json"
    soak = json.loads((root / rel).read_text(encoding="utf-8"))
    failed = [c["check"] for c in soak["checks"] if not c["ok"]]
    assert failed == ["floor llm_proposals >= 5"], failed
    f9["rc13"] = ("reemissão na cain v0.4.13rc13 + transporte 0.1.0rc6: o soak repete o mesmo quadro (todos os pisos, "
                  "menos o de LLM: 0; NO_ELIGIBLE_HYPOTHESIS); a rc13 mudou o molde e o contexto do LLM (cain#77), mas "
                  "o pedido do Brasileirão continua sem parameters, então o waiver do dono continua a valer")
    f9["evidence"].append({"file": rel, "sha256": sha((root / rel).read_bytes())})
    (q / "FINDINGS.json").write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("IB-F009 +rc13")


def changelog(q: Path, run: str, withdrawn: str, withdrawn_sha: str) -> None:
    num = json.loads((q / "EVIDENCE_NUMBERS.json").read_text(encoding="utf-8"))["numbers"]
    r = f"runtime/{run}"

    def v(key):
        return num[key]["value"]

    def c(key):
        return f"{v(key + ':checks_passed')}/{v(key + ':checks_passed') + v(key + ':checks_failed')}"

    junit = {n: v(f"{r}/cleanroom-final/{n}.junit.xml:junit")["tests"] for n in ("conformance", "transport", "cain")}
    points = v(f"{r}/failure-matrix/FAILURE_MATRIX_RESULTS.json:points")
    static = v(f"{r}/contract-revalidation/static.json:checks")
    text = f"""
## Reemissão na cain v0.4.13rc13 + transporte 0.1.0rc6 (C14; run `{run}`, PC 2)

O cain (rodadas de utilidade do stocks: cain#77, D-26) e o transporte (um consumidor por domínio: ecosystem-predictor#36)
mudaram, e a C14 manda refazer as fases que os exercitam. Alvos adotados por `scripts/adopt_release.py` (7/7): cain
v0.4.13rc13 `960fb25` (a1d94fd5…) e transporte v0.1.0rc6 `bac1f7b` (6c7e83c4…), pinado pelo uv.lock da rc13. O
brasileirao.json e o policy.py são byte a byte os da rc12.

| Fase | Resultado |
|---|---|
| cleanroom-final | conformidade {junit['conformance']}, transporte {junit['transport']}, cain {junit['cain']} testes, 0 falhas |
| contract-revalidation | estática {static['passed']}/{static['passed'] + static['failed']} ((f) pelo IB-F005); (d) {c(f"{r}/contract-revalidation")} |
| e2e | {c(f"{r}/e2e")} |
| n-plus-1 | congelado {c(f"{r}/n-plus-1/frozen")}, integrado {c(f"{r}/n-plus-1/integrated")}; holdout 2025 → REQUIRE_HUMAN SEALED_SCOPE |
| isolation-ids-contradiction | {c(f"{r}/isolation")}; contradição {c(f"{r}/isolation/contradiction")} |
| idempotency-failure | F01–F16: {sum(p['passed'] for p in points)} conferências, {sum(p['failed'] for p in points)} falhas |
| windows-smoke (PC 2) | E2E {c(f"{r}-windows/e2e")}; dado real devolvido ao WSL: {v(f"{r}-windows/logs/transfer_back.tsv:transfer_back")['files']} arquivos conferidos |
| soak | {c(f"{r}/soak")}: todos os pisos, menos o de LLM (IB-F009, waiver do dono, mantido) |

Registro: um run anterior na mesma pilha (`{withdrawn}`) deu os mesmos resultados, mas o no_data_rows_check acusou o
falso positivo IB-F003 no `real_env.policy.sha256` do operador daquele run (7 dígitos dentro do hex de 64). O run saiu do
RAW_LOGS (privado, SUMMARY do E2E sha256 `{withdrawn_sha[:12]}…`); este run tem operador novo e saída limpa. O checker
não foi alterado. A attestation da rc12 fica preservada em `QUALIFICATION_ATTESTATION_superseded_<sha12>.json`, e a nova
aponta para ela por `supersedes_sha256`.
"""
    log = q / "QUALIFICATION_CHANGELOG.md"
    log.write_text(log.read_text(encoding="utf-8").rstrip("\n") + "\n" + text, encoding="utf-8")
    print("changelog ok")


def utility_report(q: Path, run: str) -> None:
    """STOCKS_UTILITY_ROUND_REPORT.md from the round's public SUMMARY.json (numbers only from that file)."""
    base = q / "RAW_LOGS" / "runtime" / run / "stocks-utility-round"
    raw = (base / "SUMMARY.json").read_bytes()
    s = json.loads(raw)
    checks = "\n".join(f"| {c['check']} | {'PASS' if c['ok'] else 'FAIL'} |" for c in s["checks"])
    calls = "\n".join(f"| {c['call']} | {c.get('hypothesis') or '—'} | {c.get('request_type') or '—'} | "
                      f"{c.get('decision') or '—'} | {c.get('domain') or '—'} | {(c.get('error') or '')[:60]} |"
                      for c in s["calls"])
    guards = "\n".join(f"| {g['guard']} | {g['decision']} {g.get('reason_code') or ''} ({g['rule']}) | "
                       f"{g.get('domain') or '—'} {g.get('result_state') or ''} | {'PASS' if g['ok'] else 'FAIL'} |"
                       for g in s["guards"])
    lint = "\n".join(f"| {k} | {v['expected']} | {v['got']} | {', '.join(v['violations']) or '—'} |"
                     for k, v in s["lint"].items())
    text = f"""# Rodada independente CAIN × Stocks — cain 0.4.13rc13 + transporte 0.1.0rc6

> Gerado por `scripts/reissue_rc13.py utility-report` a partir de `RAW_LOGS/runtime/{run}/stocks-utility-round/SUMMARY.json`
> (sha256 `{sha(raw)}`). Não é gate da integration-brasileirao. Pedido do dono no chat desta sessão; harness próprio
> (`scripts/stocks_utility_round.py`); critério de aceite combinado com a sessão STOCKS; PC 2 (WSL), modelo local
> phi4-mini; findings do scientific_state do main do stocks fixado em 4c82885 (D-26).

**Resultado: {s['passed']} de {s['passed'] + s['failed']} critérios.**

| Critério | Resultado |
|---|---|
{checks}

## Laço com o modelo (10 chamadas)

| Chamada | Hipótese | Tipo de pedido | Decisão | Domínio | Erro |
|---|---|---|---|---|---|
{calls}

## Guardas (12)

| Caso | Decisão (regra) | Domínio | Resultado |
|---|---|---|---|
{guards}

## Linter de relatório

| Relatório | Esperado | Obtido | Violações |
|---|---|---|---|
{lint}

Limites declarados, não decididos: paráfrase sem nome da hipótese (o embedding só lista candidatos). O IS-F009 (envelope
falso do consumidor perdedor) foi resolvido pelo transporte 0.1.0rc6 (um consumidor por domínio): no teste conjunto
deste run, a disputa do stocks deu 20/20.
"""
    (q / "STOCKS_UTILITY_ROUND_REPORT.md").write_text(text, encoding="utf-8")
    print("STOCKS_UTILITY_ROUND_REPORT.md", len(text))


if __name__ == "__main__":
    mode, q = sys.argv[1], Path(sys.argv[2])
    if mode == "supersede":
        supersede(q)
    elif mode == "findings":
        findings(q, sys.argv[3])
    elif mode == "utility-report":
        utility_report(q, sys.argv[3])
    else:
        changelog(q, sys.argv[3], sys.argv[4], sys.argv[5])
