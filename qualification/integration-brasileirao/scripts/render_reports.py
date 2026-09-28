"""integration-brasileirao (C20, EVIDENCE_CONSISTENCY): gera os relatórios da missão a partir de EVIDENCE_NUMBERS.json.

Todo número vem de EVIDENCE_NUMBERS.json (gerado por evidence_numbers.py a partir de RAW_LOGS/), com o arquivo de
origem e os 12 primeiros hex do sha256 dele; os textos descritivos vêm de runtime_targets.json, FINDINGS.json e
FROZEN_PARAMETERS.json. Nenhum número é digitado à mão. Relatórios: ENVELOPE_V2_CONFORMANCE_REPORT.md,
DECISION_POLICY_REPORT.md, CAIN_ROUNDTRIP_REPORT.md, CONTRACT_REVALIDATION_REPORT.md, CORE_IDENTITY_REPORT.md,
CLEANROOM_REPORT.md, PROTECTED_ARTIFACT_REPORT.md, SOAK_REPORT.md, HOSTED_CI_REPORT.md.
Uso: python render_reports.py <qualification/integration-brasileirao> <run>
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    q, run = Path(sys.argv[1]), sys.argv[2]
    numbers = json.loads((q / "EVIDENCE_NUMBERS.json").read_text(encoding="utf-8"))["numbers"]
    targets = json.loads((q / "runtime_targets.json").read_text(encoding="utf-8"))
    findings = {f["id"]: f for f in json.loads((q / "FINDINGS.json").read_text(encoding="utf-8"))["findings"]}
    frozen = json.loads((q / "FROZEN_PARAMETERS.json").read_text(encoding="utf-8"))
    r = f"runtime/{run}"
    suf = "rc" + targets["cain"]["version"].split("rc")[-1]
    cdir = "core-identity" if suf == "rc12" else f"core-identity-{suf}"
    pdir = "protected" if suf == "rc12" else f"protected-{suf}"
    sdir = "secrets" if suf == "rc12" else f"secrets-{suf}"

    def n(key: str):
        return numbers[key]["value"]

    def src(key: str) -> str:
        e = numbers[key]
        return f"`{e['source']}` (sha256 `{e['sha256'][:12]}…`)"

    def cp(key: str) -> str:  # checks passed/failed of a SUMMARY.json
        return f"{n(key + ':checks_passed')} passaram, {n(key + ':checks_failed')} falharam — {src(key + ':checks_passed')}"

    def junit(name: str) -> str:
        v = n(f"{r}/cleanroom-final/{name}.junit.xml:junit")
        return (f"{v['tests']} testes, {v['failures']} falhas, {v['errors']} erros, {v['skipped']} pulados — "
                f"{src(f'{r}/cleanroom-final/{name}.junit.xml:junit')}")

    stack = "\n".join(f"| {k} | {targets[k]['version']} | `{targets[k]['commit'][:12]}` | `{targets[k]['sha256'][:12]}…` |"
                      for k in ("cain", "brasileirao", "transport", "protocol"))
    head = ("> Gerado por `scripts/render_reports.py` a partir de `EVIDENCE_NUMBERS.json` (C20). "
            f"Runtime suportado no PC 2 (owner_linux), run `{run}`.\n\n")
    reports = {}
    reports["CLEANROOM_REPORT.md"] = f"""# Cleanroom final — integration-brasileirao

{head}Venvs limpos só dos `uv.lock` (`--require-hashes`) e das wheels publicadas, fora de qualquer checkout (módulos de
`site-packages`).

| Pacote | Versão | Commit | sha256 da wheel |
|---|---|---|---|
{stack}

- Conformidade do domínio: {junit("conformance")}
- Transporte: {junit("transport")}
- CAIN (suíte da orquestração): {junit("cain")}
"""
    reports["CORE_IDENTITY_REPORT.md"] = f"""# Identidade das dependências (LOCK_INTEGRITY / CORE_IDENTITY)

{head}pyproject ↔ `tool.uv.sources` ↔ `uv.lock` ↔ wheel publicada ↔ versão instalada ↔ módulo em `site-packages`,
para o CAIN e o Brasileirão; Core 3.2.1 e Ops 4.2.2rc1 os mesmos da Etapa A.

- Conferências: {n(f"{cdir}/core_identity.json:checks")['passed']} passaram,
  {n(f"{cdir}/core_identity.json:checks")['failed']} falharam — {src(f"{cdir}/core_identity.json:checks")}
- Release do cain adotada: {n(f"release-{suf}/release_check.json:checks")['passed']} de
  {n(f"release-{suf}/release_check.json:checks")['passed'] + n(f"release-{suf}/release_check.json:checks")['failed']}
  conferências — {src(f"release-{suf}/release_check.json:checks")}
"""
    static = n(f"{r}/contract-revalidation/static.json:checks")
    acc = n(f"{r}/contract-revalidation/ib_f005_acceptance.json:accepted")
    reports["CONTRACT_REVALIDATION_REPORT.md"] = f"""# Revalidação do contrato do domínio (C24.3, DOMAIN_CONTRACTS_PRESERVED)

{head}- (a)(b)(e)(f) estáticas: {static['passed']} passaram, {static['failed']} falharam —
  {src(f"{r}/contract-revalidation/static.json:checks")}
- (f) pelo caminho aceito pelo dono (IB-F005, "{findings['IB-F005']['owner_decision_taken']['words']}"): aceito =
  {acc['accepted']} — {src(f"{r}/contract-revalidation/ib_f005_acceptance.json:accepted")}; runs: {', '.join(acc['runs'].values())}
- (c) conformidade no cleanroom-final: {junit("conformance")}
- (d) pelo runtime suportado: {cp(f"{r}/contract-revalidation")}
- Registro: a primeira execução estática, sem o arquivo de aceite, deu (f) FAIL; o arquivo de aceite confere a
  decisão do dono e os dois runs pelo `gh` (`scripts/ib_f005_acceptance.py`).
"""
    rec = n(f"{r}/n-plus-1/frozen:receipts")
    holdout = [x for x in rec if x.get("kind") == "holdout"]
    reports["DECISION_POLICY_REPORT.md"] = f"""# DecisionPolicy (DECISION_POLICY, N_PLUS_1_DETERMINISTIC, NEGATIVE_RESULT_NEUTRALITY)

{head}Política genérica v2 do cain {targets['cain']['version']} (sem mudança nesta missão), com a `rule_order` congelada
no FROZEN_PARAMETERS (ciclo {frozen['cycle']['number']}):

{chr(10).join('- ' + rule for rule in frozen['decision_policy']['rule_order'])}

- N+1 congelado: {cp(f"{r}/n-plus-1/frozen")}
- N+1 no runtime integrado (resultados V2 reais do cripto e do stocks no mesmo estado): {cp(f"{r}/n-plus-1/integrated")}
- Holdout 2025 (D-25 (2)), nunca despachado:
{chr(10).join(f"  - `{x.get('candidate')}`: {x.get('decision')} {x.get('reason_code')} ({x.get('rule')})" for x in holdout)}
- IB-F002 (holdout → REQUIRE_HUMAN): {findings['IB-F002']['status']}.
"""
    reports["ENVELOPE_V2_CONFORMANCE_REPORT.md"] = f"""# Conformidade do envelope V2 (ENVELOPE_V2_CONFORMANCE)

{head}Protocolo congelado `predictor-research-protocol` {targets['protocol']['version']} (sem mudança), transporte
{targets['transport']['version']} com o Brasileirão na allowlist fixa.

- Transporte no cleanroom-final: {junit("transport")}
- E2E com o dado real (tasks e resultados V2 pelo spool, restart do consumidor e do CAIN): {cp(f"{r}/e2e")}
- IDs qualificados e isolamento entre domínios: {cp(f"{r}/isolation")}
"""
    reports["CAIN_ROUNDTRIP_REPORT.md"] = f"""# Roundtrip CAIN ↔ Brasileirão (E2E, CAIN_INGESTION, PROVENANCE, FUTURE_CANARY, CROSS_DOMAIN_ISOLATION)

{head}- E2E no Linux primário: {cp(f"{r}/e2e")}; decisões: {', '.join(n(f"{r}/e2e:decisions"))}
- E2E no Windows secundário (PC 2): {cp(f"{r}-windows/e2e")}
- Isolamento, IDs e contradição: {cp(f"{r}/isolation")}; contradição: {cp(f"{r}/isolation/contradiction")}
- Matriz de falhas F01–F16: {', '.join(f"{p['point']} {p['passed']}/{p['passed'] + p['failed']}" for p in n(f"{r}/failure-matrix/FAILURE_MATRIX_RESULTS.json:points"))}
  — {src(f"{r}/failure-matrix/FAILURE_MATRIX_RESULTS.json:points")}
- Memória do CAIN: só referências, estados e hashes (nenhuma linha do dado real; no_data_rows_check em toda saída
  pública de cada cenário).
"""
    counters = n(f"{r}/soak:counters")
    profile = json.loads((q / "QUALIFICATION_PROFILE_INTEGRATION_BR_V1.json").read_text(encoding="utf-8"))
    floors = profile["minimums"]
    rows = "\n".join(f"| {k} | {counters[k]} | {floors[k]} |" for k in
                     ("cycles", "duplicates", "domain_restarts", "cain_restarts", "interleaved_cycles_other_domain",
                      "llm_proposals"))
    reports["SOAK_REPORT.md"] = f"""# Soak (SOAK)

{head}Perfil congelado `QUALIFICATION_PROFILE_INTEGRATION_BR_V1.json` (ciclo {profile['cycle']['number']}), uma hipótese de
qualificação por ciclo (decisão do dono, IB-F007).

- Conferências: {cp(f"{r}/soak")}
- Contadores: {json.dumps(counters, ensure_ascii=False)} — {src(f"{r}/soak:counters")}

| Piso | Obtido | Mínimo do perfil |
|---|---|---|
{rows}
| classes de falha com ≥ {floors['runs_per_failure_class']} execuções | {sum(v >= floors['runs_per_failure_class'] for v in counters['failure_runs'].values())} | {floors['relevant_failure_classes']} |

- Piso de propostas de LLM: {counters['llm_proposals']} (mínimo {floors['llm_proposals']}). **Dispensado pelo dono só para o Brasileirão**
  (IB-F009, "{findings['IB-F009']['owner_decision_taken']['words']}"): na cain {targets['cain']['version']} o CAIN não
  pergunta ao modelo para um domínio sem `parameters` (todo molde é um experimento já rodado, R17). A conferência que
  falhou continua registrada no SUMMARY.json.
"""
    hosted = n(f"hosted-ci/final-{suf}/HOSTED_CI_SUMMARY.json:hosted_ci")
    reports["HOSTED_CI_REPORT.md"] = f"""# CI hospedado (HOSTED_CI, C21)

{head}Só vale o run de `push` com `headSha` igual ao commit final.

{chr(10).join(f"- {h['repo']} `{h['commit'][:12]}`: ok = {h['ok']}; " + ', '.join(f"{w} {v['conclusion']}" for w, v in h['runs'].items()) for h in hosted)}
  — {src(f"hosted-ci/final-{suf}/HOSTED_CI_SUMMARY.json:hosted_ci")}
- brasileirao-predictor `{targets['brasileirao']['commit'][:12]}`: pelo caminho aceito pelo dono (IB-F005): aceito =
  {acc['accepted']} — {src(f"{r}/contract-revalidation/ib_f005_acceptance.json:accepted")}
"""
    prot = n(f"{pdir}/protected_check.json:protected")
    reports["PROTECTED_ARTIFACT_REPORT.md"] = f"""# Artefatos protegidos (PROTECTED_ARTIFACTS_UNCHANGED, C15.1)

{head}- Itens conferidos: {prot['items_total']}; inalterados (com a regra da cadeia preservada): {prot['all_unchanged']} —
  {src(f"{pdir}/protected_check.json:protected")}
- Regra: decisão do dono (IB-F008, "{findings['IB-F008']['owner_decision_taken']['words']}"): um artefato compartilhado
  alterado conta como inalterado só com os bytes do truth-map preservados (sha256 conferido) num `_cycle<N>_`/
  `_superseded_` do mesmo diretório; itens de código dos domínios sem exceção.
- Segredos: limpo = {n(f"{sdir}/secrets_scan.json:secrets")['clean']}, achados = {n(f"{sdir}/secrets_scan.json:secrets")['findings']}
  — {src(f"{sdir}/secrets_scan.json:secrets")}
"""
    for name, text in reports.items():
        (q / name).write_text(text, encoding="utf-8")
        print(name, len(text))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
