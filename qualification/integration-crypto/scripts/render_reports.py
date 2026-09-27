"""integration-crypto (C20): gera os relatórios da missão a partir de EVIDENCE_NUMBERS.json e dos JSON de evidência.

Nenhum número é digitado: cada tabela vem de um arquivo de RAW_LOGS/ (citado com sha256). Gera:
  CORE_IDENTITY_REPORT.md, CAIN_ROUNDTRIP_REPORT.md, CONTRACT_REVALIDATION_REPORT.md, HOSTED_CI_REPORT.md,
  PROTECTED_ARTIFACT_REPORT.md, SOAK_REPORT.md e a seção cleanroom-final do CLEANROOM_REPORT.md.
Uso: python render_reports.py <qualification/integration-crypto> <run do runtime> <run do soak>
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    m, run, soak = Path(sys.argv[1]), sys.argv[2], sys.argv[3]
    root = m.parent.parent
    raw = m / "RAW_LOGS"
    nums = json.loads((m / "EVIDENCE_NUMBERS.json").read_text(encoding="utf-8"))["numbers"]

    def n(key: str):
        return nums[key]["value"]

    def cite(path: Path) -> str:
        return f"`{path.relative_to(root).as_posix()}` (sha256 `{sha(path)[:16]}…`)"

    rt = raw / "runtime" / run
    sk = raw / "runtime" / soak
    # ---------------------------------------------------------------- CORE_IDENTITY
    ci = json.loads((raw / "core-identity" / "core_identity.json").read_text(encoding="utf-8"))
    rows = "\n".join(f"| {c['check']} | {'OK' if c['ok'] else 'FALHA'} |" for c in ci["checks"])
    (m / "CORE_IDENTITY_REPORT.md").write_text(
        "# integration-crypto — CORE_IDENTITY_REPORT\n\n"
        "Gates `LOCK_INTEGRITY` e `CORE_IDENTITY` (C4). Gerado por `scripts/render_reports.py`.\n\n"
        f"Fonte: {cite(raw / 'core-identity' / 'core_identity.json')}, produzido por `scripts/core_identity.py` a "
        f"partir dos `uv.lock` dos commits finais (git show, SHA completo) e dos logs do run `{run}`.\n\n"
        f"Resultado: **{ci['passed']} conferências OK, {ci['failed']} falhas**.\n\n"
        "| Conferência | Resultado |\n|---|---|\n" + rows + "\n\n"
        "Os runtimes (CAIN e consumidor) são instalados só com requisitos exportados dos `uv.lock` "
        "(`--require-hashes`) e com as wheels publicadas conferidas por sha256 antes de instalar "
        "(`scripts/runtime_env.sh`). Nenhum pacote do stack vem de índice público, de `vendor/` ou de checkout.\n",
        encoding="utf-8")
    # ---------------------------------------------------------------- CLEANROOM (final)
    report = (m / "CLEANROOM_REPORT.md").read_text(encoding="utf-8")
    head = report.split("## cleanroom-final")[0]
    junit = {name: n(f"runtime/{run}/cleanroom-final/{name}.junit.xml:junit") for name in ("conformance", "transport", "cain")}
    lines = "\n".join(f"| {name} | {v['tests']} | {v['failures']} | {v['errors']} | {v['skipped']} |" for name, v in junit.items())
    (m / "CLEANROOM_REPORT.md").write_text(
        head + "## cleanroom-final (gate CLEANROOM_FINAL; C24.3 c)\n\n"
        f"GitHub Actions ubuntu-latest × Python 3.13, run `{run}`, só as wheels publicadas de `runtime_targets.json` em "
        "venvs limpos fora dos checkouts (`scripts/cleanroom_final.sh`). Log: "
        f"{cite(rt / 'cleanroom-final' / 'cleanroom_final.log')}.\n\n"
        "| Suíte (instalada da wheel) | testes | falhas | erros | pulados |\n|---|--:|--:|--:|--:|\n" + lines + "\n\n"
        "- `conformance`: a suíte de conformidade congelada da Etapa A do cripto (`tests/conformance` do commit final), "
        "contra o `cripto-predictor` 1.2.0rc3 instalado com o protocolo e o transporte no mesmo venv (C24.3 c).\n"
        "- `transport`: testes do `predictor-research-transport` 0.1.0rc2 contra a wheel instalada.\n"
        "- `cain`: política, orquestração, cerco do loop e SHA completo, contra o `cain-research` 0.4.13rc5 instalado.\n",
        encoding="utf-8")
    # ---------------------------------------------------------------- CAIN_ROUNDTRIP
    def summary(rel: str) -> dict:
        return json.loads((rt / rel / "SUMMARY.json").read_text(encoding="utf-8"))

    e2e, n1, iso, contract = summary("e2e"), summary("n-plus-1"), summary("isolation"), summary("contract-revalidation")
    win = json.loads((raw / "windows-smoke" / "e2e" / "SUMMARY.json").read_text(encoding="utf-8"))
    fm = json.loads((rt / "failure-matrix" / "FAILURE_MATRIX_RESULTS.json").read_text(encoding="utf-8"))["points"]
    receipts = "\n".join(f"| {r['candidate']} | {r['decision']} | {r['reason_code']} | {r['rule']} | `{r['receipt_sha256'][:16]}…` |"
                         for r in n1["receipts"])
    points = "\n".join(f"| {p['point']} | {p['passed']} | {p['failed']} |" for p in fm)
    (m / "CAIN_ROUNDTRIP_REPORT.md").write_text(
        "# integration-crypto — CAIN_ROUNDTRIP_REPORT\n\n"
        "Gates `E2E`, `PROVENANCE`, `IDEMPOTENCY`, `RESTART_RECOVERY`, `FAILURE_INJECTION`, `AUTHORITY_SEPARATION`, "
        "`FUTURE_CANARY`, `CAIN_INGESTION`, `CAIN_CONTAINMENT`, `N_PLUS_1_DETERMINISTIC`, `CROSS_DOMAIN_ISOLATION`, "
        "`DOMAIN_QUALIFIED_IDS`, `CONTRADICTION_PRESERVATION`. Gerado por `scripts/render_reports.py`.\n\n"
        "Circuito: `cain research propose` → DecisionPolicy → TaskOutbox → spool → `predictor-research-consumer` → "
        "adapter → admission → Ops → Core → resultado → ResultInbox → memória do domínio → próxima decisão. Tudo pelos "
        "entrypoints instalados das wheels publicadas; os venvs do CAIN e do consumidor são separados (o CAIN não tem o "
        "domínio instalado; `runtime_env.sh` confere).\n\n"
        "| Cenário | Ambiente | Conferências OK | Falhas | Fonte |\n|---|---|--:|--:|---|\n"
        f"| E2E (dados reais, restart do consumidor e do CAIN, outros domínios intercalados, canário, N+1) | Linux primário, run `{run}` | {e2e['passed']} | {e2e['failed']} | {cite(rt / 'e2e' / 'SUMMARY.json')} |\n"
        f"| E2E + restart (WINDOWS_SMOKE) | Windows local do **PC 2** | {win['passed']} | {win['failed']} | {cite(raw / 'windows-smoke' / 'e2e' / 'SUMMARY.json')} |\n"
        f"| N+1 (3 processos, receipt byte a byte) | Linux primário | {n1['passed']} | {n1['failed']} | {cite(rt / 'n-plus-1' / 'SUMMARY.json')} |\n"
        f"| Isolamento, IDs com domínio, contradição | Linux primário | {iso['passed']} | {iso['failed']} | {cite(rt / 'isolation' / 'SUMMARY.json')} |\n"
        f"| Contrato C24.3 (d) | Linux primário | {contract['passed']} | {contract['failed']} | {cite(rt / 'contract-revalidation' / 'SUMMARY.json')} |\n\n"
        f"Decisões do E2E (em ordem): {', '.join(e2e['decisions'])}.\n\n"
        f"## N+1 (as_of `{n1['as_of']}`)\n\n| Candidata | Decisão | Motivo | Regra | receipt sha256 |\n|---|---|---|---|---|\n"
        + receipts + "\n\n## Matriz de falhas (FAILURE_MATRIX.json)\n\n| Ponto | OK | Falhas |\n|---|--:|--:|\n" + points
        + f"\n\nFonte: {cite(rt / 'failure-matrix' / 'FAILURE_MATRIX_RESULTS.json')}.\n\n"
        "## Parecer de contenção (CAIN_CONTAINMENT)\n\n"
        "- O CAIN só propõe: o pedido não carrega handler, comando, módulo, caminho, URL, budget, prioridade final nem "
        "capital (R03). O handler vem da `admission_policy` do domínio.\n"
        "- O CAIN nunca lê banco de domínio: ele só lê o spool (envelopes V2) e a própria memória. O venv do CAIN não tem "
        "o domínio instalado, e nenhum console script do `cain` alcança um pacote de domínio (`test_loop_fenced.py`).\n"
        "- O CAIN nunca executa código de avaliação fora do circuito. O loop do PR #50 ficou fora do runtime qualificado "
        "(ver DECISION_POLICY_REPORT.md §4).\n"
        "- PR #51 (`cain findings ingest-*`): lê arquivo versionado por `git show` num commit fixado, só leitura, sem "
        "efeito no domínio. Para o cripto, só com o SHA completo (teste `test_findings_pinned_sha.py`). A orquestração "
        "qualificada não chama esse comando: a configuração do domínio já vem da base congelada.\n",
        encoding="utf-8")
    # ---------------------------------------------------------------- CONTRACT_REVALIDATION
    static = json.loads((raw / "contract-revalidation" / "static_checks.json").read_text(encoding="utf-8"))
    srows = "\n".join(f"| {c['check']} | {'OK' if c['ok'] else 'FALHA'} |" for c in static["checks"])
    (m / "CONTRACT_REVALIDATION_REPORT.md").write_text(
        "# integration-crypto — CONTRACT_REVALIDATION_REPORT\n\n"
        "Gate `DOMAIN_CONTRACTS_PRESERVED` e `domain_attestations[0].revalidation` (C24.3), domínio crypto, entre o "
        f"final_commit da Etapa A (`{static['stage_a_final_commit']}`) e o desta missão (`{static['final_commit']}`, "
        "tag v1.2.0rc3).\n\n"
        f"Parte estática ({cite(raw / 'contract-revalidation' / 'static_checks.json')}):\n\n"
        "| Conferência | Resultado |\n|---|---|\n" + srows + "\n\n"
        f"(c) suíte de conformidade verde com as wheels da integração: {junit['conformance']['tests']} testes, "
        f"{junit['conformance']['failures']} falhas ({cite(rt / 'cleanroom-final' / 'conformance.junit.xml')}).\n\n"
        f"(d) vetor real da Etapa A pelo adapter: {contract['passed']} conferências OK, {contract['failed']} falhas "
        f"({cite(rt / 'contract-revalidation' / 'SUMMARY.json')}): hash canônico sem `client_ref` igual ao do vetor, "
        "`client_ref` devolvido igual, payload byte-idêntico ao `show` (adapter_api).\n",
        encoding="utf-8")
    # ---------------------------------------------------------------- HOSTED_CI
    lines = []
    for role in ("baseline", "final"):
        for s in json.loads((raw / "hosted-ci" / role / "HOSTED_CI_SUMMARY.json").read_text(encoding="utf-8")):
            runs = "; ".join(f"[{wf} {r['id']}]({r['url']}) {r['conclusion']}" for wf, r in s["runs"].items())
            lines.append(f"| {s['repo'].split('/')[1]} | {role} | `{s['commit'][:12]}` | {'verde' if s['ok'] else 'VERMELHO'} | {runs} | {s['non_success_jobs'] or ''} |")
    (m / "HOSTED_CI_REPORT.md").write_text(
        "# integration-crypto — HOSTED_CI_REPORT\n\n"
        "Gate `HOSTED_CI` (C21): só o run de **push** cujo SHA é exatamente o commit vale. Coletado por "
        "`scripts/hosted_ci.py`. Para cada workflow vale o run mais recente naquele SHA; os JSON brutos de todos os runs "
        "estão em `RAW_LOGS/hosted-ci/`. Core e Ops não mudaram: o CI deles é o da Etapa A (HERDADO).\n\n"
        "| Repo | Papel | Commit | Estado | Runs | Jobs não verdes |\n|---|---|---|---|---|---|\n" + "\n".join(lines) + "\n\n"
        "**ecosystem-predictor vermelho só pelo IC-F004.** O job `quality` falha em "
        "`test_real_registry_has_current_hash_verified_target_harness`: dois atestados de harness do cripto venceram em "
        "2026-09-27T02:02Z e continuam `ALIGNED`. É anterior a esta missão. No commit base, o run de push do main de "
        "2026-09-26 foi verde; um run posterior no mesmo SHA (tag do protocolo, 2026-09-27T21:02Z) já saiu vermelho. "
        "Depende de decisão do dono (FINDINGS IC-F004).\n",
        encoding="utf-8")
    # ---------------------------------------------------------------- PROTECTED
    prot = json.loads((raw / "protected" / "protected_check.json").read_text(encoding="utf-8"))
    prow = "\n".join(f"| {d} | {v['repo']} | `{v['commit'][:12]}` | {v['items']} | {len(v['changed'])} |" for d, v in prot["domains"].items())
    (m / "PROTECTED_ARTIFACT_REPORT.md").write_text(
        "# integration-crypto — PROTECTED_ARTIFACT_REPORT\n\n"
        "Gate `PROTECTED_ARTIFACTS_UNCHANGED` (C15.1). O conjunto veio do PROTECTED_SET.json de `truth-map` e foi "
        f"reconferido por `scripts/protected_check.py` ({cite(raw / 'protected' / 'protected_check.json')}).\n\n"
        "| Domínio | Repo | Commit conferido | Itens | Alterados |\n|---|---|---|--:|--:|\n" + prow + "\n\n"
        f"Artefatos compartilhados conferidos por sha256: {len(prot['shared'])}; alterados: "
        f"{sum(not s['ok'] for s in prot['shared'])}. Total de itens: {prot['items_total']}; tudo igual: "
        f"{'sim' if prot['all_unchanged'] else 'NÃO'}.\n",
        encoding="utf-8")
    # ---------------------------------------------------------------- SOAK
    soak_doc = json.loads((sk / "soak" / "SUMMARY.json").read_text(encoding="utf-8"))
    profile = json.loads((m / "QUALIFICATION_PROFILE_INTEGRATION_CRYPTO_V1.json").read_text(encoding="utf-8"))
    c = dict(soak_doc["counters"])
    per_class = profile["minimums"].get("runs_per_failure_class", 0)
    c["relevant_failure_classes"] = sum(v >= per_class for v in c["failure_runs"].values())
    c["runs_per_failure_class"] = min(c["failure_runs"].values())
    floors = "\n".join(f"| {k} | {v} | {c.get(k) if k in c else '-'} |" for k, v in profile["minimums"].items())
    zero = "\n".join(f"| {x['check']} | {'OK' if x['ok'] else 'FALHA'} |" for x in soak_doc["checks"])
    earlier = []
    for prev in sorted((raw / "runtime").glob("run*/soak/SUMMARY.json")):
        if prev.parent.parent.name == soak:
            continue
        doc = json.loads(prev.read_text(encoding="utf-8"))
        bad = "; ".join(f"`{x['check']}` (obtido: {json.dumps(x.get('got'), ensure_ascii=False)})"
                        for x in doc["checks"] if not x["ok"])
        cmds = prev.parent / "commands.log"
        refused = sorted({(int(a), int(b)) for a, b in re.findall(r"somam (\d+) bytes; limite configurado (\d+)",
                                                                  cmds.read_text(encoding="utf-8"))})
        earlier.append(f"- `{prev.parent.parent.name}`: {doc['passed']} OK, {doc['failed']} falhas — {bad or 'nenhuma'}. "
                       f"Fonte: {cite(prev)}. Recusas do cliente LLM no {cite(cmds)} (bytes de entrada, limite): "
                       f"{refused or 'nenhuma'}.")
    history = ("Execuções anteriores do soak, mantidas como evidência (não descartadas):\n\n" + "\n".join(earlier) +
               "\n\nA falha anterior foi de configuração do harness, não do produto: o `cain-llm.toml` do soak declarava "
               "`num_ctx = 4096`, e o orçamento de entrada do cliente LLM do cain é "
               "`min(max_input_bytes, num_ctx - num_predict - 256)` = min(6500, 4096 - 256 - 256), menor que o pedido "
               "de proposta com contexto (números da recusa acima, lidos do log). Cada proposta saiu `LLM_PROPOSAL_FAILED` (fail "
               "closed, nenhuma task emitida). O harness passou a declarar `num_ctx = 8192` e "
               "`max_input_bytes = 16000` (`scripts/soak.py`, commit `2319ed0`, cuja mensagem atribui o 3584 ao padrão "
               "do cain por engano: o padrão de `max_input_bytes` é 6500, e o limite vinha do `num_ctx` do harness). Perfil, pisos, "
               "parâmetros congelados e vetores não mudaram.\n\n") if earlier else ""
    (m / "SOAK_REPORT.md").write_text(
        "# integration-crypto — SOAK_REPORT\n\n"
        f"Gate `SOAK` (C10, perfil `QUALIFICATION_PROFILE_INTEGRATION_CRYPTO_V1.json`, lido e não alterado). Linux "
        f"primário, run `{soak}`, dados reais públicos, runtime só com wheels publicadas. Fonte: "
        f"{cite(sk / 'soak' / 'SUMMARY.json')}; comandos brutos em `RAW_LOGS/runtime/{soak}/soak/commands.log`.\n\n"
        f"Resultado: **{soak_doc['passed']} conferências OK, {soak_doc['failed']} falhas**.\n\n"
        "| Piso | Mínimo | Obtido |\n|---|--:|--:|\n" + floors + "\n\n"
        f"Execuções por classe de falha: {json.dumps(c['failure_runs'])}. Decisões: {json.dumps(c['decisions'])}.\n\n"
        "| Conferência (tolerância zero e fim) | Resultado |\n|---|---|\n" + zero + "\n\n" + history +
        "As propostas de LLM usam um modelo local (Ollama no runner; modelo e digest nos arquivos `*.audit.json` do "
        "artefato). São auditadas e passam pela mesma DecisionPolicy; não servem de prova de gate (C9).\n",
        encoding="utf-8")
    print("relatórios gerados")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
