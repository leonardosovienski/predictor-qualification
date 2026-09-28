"""integration-stocks (C20): gera os relatórios da missão a partir dos JSON de evidência em RAW_LOGS/.

Adaptado de qualification/integration-crypto/scripts/render_reports.py. Nenhum número é digitado: cada tabela vem de
um arquivo de RAW_LOGS/ (citado com sha256). Gera CORE_IDENTITY_REPORT.md, CLEANROOM_REPORT.md,
CAIN_ROUNDTRIP_REPORT.md, CONTRACT_REVALIDATION_REPORT.md, HOSTED_CI_REPORT.md, PROTECTED_ARTIFACT_REPORT.md,
SOAK_REPORT.md, ENVELOPE_V2_CONFORMANCE_REPORT.md e DECISION_POLICY_REPORT.md.
Ciclo 2: a política é a v2 do cain (rule_order e configuração lidas do FROZEN_PARAMETERS.json), o conjunto protegido
mostra as cadeias do IS-F008 e o soak descreve as hipóteses só para o LLM.
Uso: python render_reports.py <qualification/integration-stocks> <run do Linux> <run do Windows> <coleta do hosted-ci>
     [<dir da parte estática do C24.3 em RAW_LOGS, padrão contract-revalidation>
      [<dir do protected_check em RAW_LOGS, padrão protected> [<dir do core_identity em RAW_LOGS, padrão core-identity>]]]
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def junit(path: Path) -> dict:
    tree = ET.parse(path).getroot()
    suites = [tree] if tree.tag == "testsuite" else list(tree.iter("testsuite"))
    return {k: sum(int(s.get(k, 0)) for s in suites) for k in ("tests", "failures", "errors", "skipped")}


def main() -> int:
    m, run, win, hosted = Path(sys.argv[1]), sys.argv[2], sys.argv[3], sys.argv[4]
    static_dir = sys.argv[5] if len(sys.argv) > 5 else "contract-revalidation"
    protected_dir = sys.argv[6] if len(sys.argv) > 6 else "protected"
    core_dir = sys.argv[7] if len(sys.argv) > 7 else "core-identity"
    root = m.parent.parent
    raw = m / "RAW_LOGS"
    rt, wt = raw / "runtime" / run, raw / "runtime" / win

    def cite(path: Path) -> str:
        return f"`{path.relative_to(root).as_posix()}` (sha256 `{sha(path)[:16]}…`)"

    def load(path: Path) -> dict:
        return json.loads(path.read_text(encoding="utf-8"))

    targets = load(m / "runtime_targets.json")
    # ---------------------------------------------------------------- CORE_IDENTITY
    ci = load(raw / core_dir / "core_identity.json")
    rows = "\n".join(f"| {c['check']} | {'OK' if c['ok'] else 'FALHA'} |" for c in ci["checks"])
    (m / "CORE_IDENTITY_REPORT.md").write_text(
        "# integration-stocks — CORE_IDENTITY_REPORT\n\n"
        "Gates `LOCK_INTEGRITY` e `CORE_IDENTITY` (C4). Gerado por `scripts/render_reports.py`.\n\n"
        f"Fonte: {cite(raw / core_dir / 'core_identity.json')}, produzido por `scripts/core_identity.py` a partir dos "
        f"`uv.lock` dos commits finais (git show, SHA completo) e dos logs do run `{run}`.\n\n"
        f"Resultado: **{ci['passed']} conferências OK, {ci['failed']} falhas**.\n\n"
        "| Conferência | Resultado |\n|---|---|\n" + rows + "\n\n"
        "Os runtimes (CAIN e consumidor do Stocks) são instalados só com requisitos exportados dos `uv.lock` "
        "(`--require-hashes`) e com as wheels publicadas conferidas por sha256 antes de instalar (`scripts/runtime_env.sh`). "
        "Nenhum pacote do stack vem de índice público, de `vendor/` ou de checkout.\n", encoding="utf-8")
    # ---------------------------------------------------------------- CLEANROOM
    base_log = raw / "cleanroom-baseline" / "cleanroom_baseline.log"
    base_j = junit(raw / "cleanroom-baseline" / "conformance.junit.xml")
    finals = {n: junit(rt / "cleanroom-final" / f"{n}.junit.xml") for n in ("conformance", "adapters", "transport", "cain")}
    lines = "\n".join(f"| {n} | {v['tests']} | {v['failures']} | {v['errors']} | {v['skipped']} |" for n, v in finals.items())
    text = base_log.read_text(encoding="utf-8")
    (m / "CLEANROOM_REPORT.md").write_text(
        "# integration-stocks — CLEANROOM_REPORT\n\n"
        "## cleanroom-baseline (DIAGNÓSTICO, sem valor de gate; C5)\n\n"
        f"WSL do PC 2 (diagnóstico). Script `scripts/cleanroom_baseline.sh`; log {cite(base_log)}.\n\n"
        f"- domínio: stocks-predictor 0.3.0rc2 (wheel da release) + protocolo 2.0.0rc2 + transporte 0.1.0rc3 num venv "
        f"limpo; conformidade da Etapa A contra o pacote instalado: {base_j['tests']} testes, {base_j['failures']} "
        f"falhas ({cite(raw / 'cleanroom-baseline' / 'conformance.junit.xml')});\n"
        f"- consumidor `--domain stocks`: `{'ADAPTER_UNAVAILABLE' if 'ADAPTER_UNAVAILABLE' in text else '?'}` (allowlist "
        "do transporte só com crypto);\n"
        f"- `cain research propose --domain stocks` (cain 0.4.13rc6): `{'CONFIG_INVALID' if 'CONFIG_INVALID' in text else '?'}`, "
        "sem estado gravado (só `crypto.json` empacotado).\n\n"
        "## cleanroom-final (gate CLEANROOM_FINAL; C24.3 b/c)\n\n"
        f"GitHub Actions ubuntu-latest × Python 3.13, run `{run}`, só as wheels publicadas de `runtime_targets.json` em "
        f"venvs limpos fora dos checkouts (`scripts/cleanroom_final.sh`). Log: {cite(rt / 'cleanroom-final' / 'cleanroom_final.log')}.\n\n"
        "| Suíte (instalada da wheel) | testes | falhas | erros | pulados |\n|---|--:|--:|--:|--:|\n" + lines + "\n\n"
        f"- `conformance`: suíte de conformidade congelada da Etapa A (`tests/conformance` do commit final) contra o "
        f"`stocks-predictor` {targets['stocks']['version']} instalado com o protocolo e o transporte no mesmo venv (C24.3 c), "
        "inclusive `test_import_closure.py` (regras de adapter_paths, C24.3 b);\n"
        "- `adapters`: testes novos do adapter (D-24 (4a)) contra a mesma wheel;\n"
        f"- `transport`: testes do `predictor-research-transport` {targets['transport']['version']} contra a wheel instalada;\n"
        f"- `cain`: política, configuração do Stocks, orquestração, cerco do loop e SHA completo, contra o `cain-research` "
        f"{targets['cain']['version']} instalado.\n", encoding="utf-8")
    # ---------------------------------------------------------------- CAIN_ROUNDTRIP
    e2e = load(rt / "e2e" / "SUMMARY.json")
    wine = load(wt / "e2e" / "SUMMARY.json")
    n1f, n1i = load(rt / "n-plus-1" / "frozen" / "SUMMARY.json"), load(rt / "n-plus-1" / "integrated" / "SUMMARY.json")
    iso, con = load(rt / "isolation" / "SUMMARY.json"), load(rt / "isolation" / "contradiction" / "SUMMARY.json")
    cd = load(rt / "contract-revalidation" / "SUMMARY.json")
    fm = load(rt / "failure-matrix" / "FAILURE_MATRIX_RESULTS.json")["points"]
    receipts = "\n".join(f"| {r['candidate']} | {r['decision']} | {r['reason_code']} | {r['rule']} | `{r['receipt_sha256'][:16]}…` |"
                         for r in n1f["receipts"])
    same = [a["receipt_sha256"] for a in n1f["receipts"]] == [b["receipt_sha256"] for b in n1i["receipts"]]
    points = "\n".join(f"| {p['point']} | {p['passed']} | {p['failed']} |" for p in fm)
    states = "\n".join(f"| {k} | {v['operational_state']} | {v['result_state']} | {v['scientific_state']} | {v['economic_state']} |"
                       for k, v in sorted(e2e["domain_states"].items()))
    (m / "CAIN_ROUNDTRIP_REPORT.md").write_text(
        "# integration-stocks — CAIN_ROUNDTRIP_REPORT\n\n"
        "Gates `E2E`, `PROVENANCE`, `IDEMPOTENCY`, `RESTART_RECOVERY`, `FAILURE_INJECTION`, `AUTHORITY_SEPARATION`, "
        "`FUTURE_CANARY`, `CAIN_INGESTION`, `CAIN_CONTAINMENT`, `N_PLUS_1_DETERMINISTIC`, `CROSS_DOMAIN_ISOLATION`, "
        "`DOMAIN_QUALIFIED_IDS`, `CONTRADICTION_PRESERVATION`, `WINDOWS_SMOKE`. Gerado por `scripts/render_reports.py`.\n\n"
        "Circuito: `cain research propose` → DecisionPolicy → TaskOutbox → spool → `predictor-research-consumer` → adapter "
        "do Stocks → `Circuit.submit_request` (admission → Ops → Core) → resultado → ResultInbox → memória do domínio "
        "`stocks` → próxima decisão. Tudo pelos entrypoints instalados das wheels publicadas; os venvs do CAIN e do "
        "consumidor são separados (o CAIN não tem domínio instalado; `runtime_env.sh` confere).\n\n"
        f"Dados reais: painel B3/CVM do pin do run (`data/SOURCES.json`), data_cutoff `{e2e['real_env']['data_cutoff']}`, "
        f"painel `{e2e['real_env']['panel_sha256'][:16]}…`, dataset `{e2e['real_env']['dataset_version']}`.\n\n"
        "| Cenário | Ambiente | Conferências OK | Falhas | Fonte |\n|---|---|--:|--:|---|\n"
        f"| E2E (dados reais, restart do consumidor e do CAIN, outros domínios intercalados, canário, N+1) | Linux primário, run `{run}` | {e2e['passed']} | {e2e['failed']} | {cite(rt / 'e2e' / 'SUMMARY.json')} |\n"
        f"| E2E + restart (WINDOWS_SMOKE) | GitHub Actions windows-latest, run `{win}` | {wine['passed']} | {wine['failed']} | {cite(wt / 'e2e' / 'SUMMARY.json')} |\n"
        f"| N+1 congelado (3 processos, receipt byte a byte) | Linux primário | {n1f['passed']} | {n1f['failed']} | {cite(rt / 'n-plus-1' / 'frozen' / 'SUMMARY.json')} |\n"
        f"| N+1 integrado (resultado real do cripto no spool) | Linux primário | {n1i['passed']} | {n1i['failed']} | {cite(rt / 'n-plus-1' / 'integrated' / 'SUMMARY.json')} |\n"
        f"| Isolamento e IDs (cripto integrado; brasileirao por fixture) | Linux primário | {iso['passed']} | {iso['failed']} | {cite(rt / 'isolation' / 'SUMMARY.json')} |\n"
        f"| Contradição | Linux primário | {con['passed']} | {con['failed']} | {cite(rt / 'isolation' / 'contradiction' / 'SUMMARY.json')} |\n"
        f"| Contrato C24.3 (d) | Linux primário | {cd['passed']} | {cd['failed']} | {cite(rt / 'contract-revalidation' / 'SUMMARY.json')} |\n\n"
        f"Decisões do E2E (em ordem): {', '.join(e2e['decisions'])}.\n\n"
        "Estados do domínio nos resultados reais do E2E (copiados como vieram; nenhum é promovido; C22: QUALIFIED não é edge):\n\n"
        "| Episódio | Operacional | Resultado | Científico | Econômico |\n|---|---|---|---|---|\n" + states + "\n\n"
        f"Memória por cubo no estado compartilhado do isolamento: {json.dumps(iso.get('memory_cubes'), ensure_ascii=False)}.\n\n"
        f"## N+1 (as_of `{n1f['as_of']}`)\n\n| Candidata | Decisão | Motivo | Regra | receipt sha256 |\n|---|---|---|---|---|\n"
        + receipts + f"\n\nReceipts da variante integrada iguais aos da congelada: **{'sim' if same else 'NÃO'}**.\n\n"
        "## Matriz de falhas (FAILURE_MATRIX.json)\n\n| Ponto | OK | Falhas |\n|---|--:|--:|\n" + points
        + f"\n\nFonte: {cite(rt / 'failure-matrix' / 'FAILURE_MATRIX_RESULTS.json')}.\n\n"
        "## Parecer de contenção (CAIN_CONTAINMENT)\n\n"
        "- O CAIN só propõe: o pedido não carrega handler, comando, módulo, caminho, URL, budget, prioridade final nem "
        "capital (R03). O handler vem da `admission_policy` do Stocks (allowlist compilada).\n"
        "- O CAIN nunca lê banco de domínio: ele só lê o spool (envelopes V2) e a própria memória. O venv do CAIN não tem "
        "domínio instalado, e nenhum console script do `cain` alcança um pacote de domínio (`test_loop_fenced.py`).\n"
        "- O CAIN nunca executa código de avaliação fora do circuito: o loop do PR #50 continua fora do runtime qualificado "
        "(`python -m cain.loop`, ferramenta de laboratório; nenhum console script o alcança).\n"
        "- PR #51 (`cain findings ingest-*`): leitura de arquivo versionado por `git show` num commit fixado, só leitura. A "
        "orquestração qualificada do Stocks não chama esse comando: a configuração do domínio vem de 61fc017 (SHA completo) "
        "pelo `tools/build_domain_config.py` e fica empacotada (`data/stocks.json`).\n", encoding="utf-8")
    # ---------------------------------------------------------------- CONTRACT_REVALIDATION
    static = load(raw / static_dir / "static_checks.json")
    srows = "\n".join(f"| {c['check']} | {'OK' if c['ok'] else 'FALHA'} |" for c in static["checks"])
    a_changed = next(c for c in static["checks"] if c["check"].startswith("(a) outside adapter_paths only"))
    diff_rows = "\n".join(f"| `{p}` | {s} |" for p, s in sorted(a_changed["changed"].items()))
    (m / "CONTRACT_REVALIDATION_REPORT.md").write_text(
        "# integration-stocks — CONTRACT_REVALIDATION_REPORT\n\n"
        "Gate `DOMAIN_CONTRACTS_PRESERVED` e `domain_attestations[0].revalidation` (C24.3), domínio stocks, entre o "
        f"final_commit da Etapa A (`{static['stage_a_final_commit']}`) e o desta missão (`{static['final_commit']}`, tag "
        "v0.3.0rc3).\n\n"
        "## C24.3 (a) — diff completo do domínio\n\n"
        "| Arquivo | Estado |\n|---|---|\n" + diff_rows + "\n\n"
        "Fora de `stocks_predictor/adapters/` só entram:\n\n"
        "- C24.3(a): a linha `version` do `pyproject.toml` e a linha da versão do projeto no `uv.lock` (pré-release);\n"
        "- **autorizados pela D-24 (4)** (decisão do dono, resposta ao conflito C19 entre a regra local R8 e C24.3(a)): "
        "arquivos NOVOS em `tests/adapters/`, os dois recibos R8 novos (só `.json`) em "
        "`docs/engineering/2026-09-27-integration-stocks/evidence/` e o selo `docs/engineering/current-operational-evidence.json`.\n\n"
        f"Parte estática ({cite(raw / static_dir / 'static_checks.json')}):\n\n"
        "| Conferência | Resultado |\n|---|---|\n" + srows + "\n\n"
        f"(c) suíte de conformidade verde com as wheels da integração: {finals['conformance']['tests']} testes, "
        f"{finals['conformance']['failures']} falhas ({cite(rt / 'cleanroom-final' / 'conformance.junit.xml')}).\n\n"
        f"(d) vetor congelado da Etapa A pelo adapter: {cd['passed']} conferências OK, {cd['failed']} falhas "
        f"({cite(rt / 'contract-revalidation' / 'SUMMARY.json')}): hash canônico sem `client_ref` igual ao do vetor "
        f"(`{cd['vector_sha256'][:16]}…`, o mesmo conferido contra o resultado real da Etapa A), `client_ref` devolvido igual, "
        "payload byte-idêntico ao `show` (adapter_api).\n\n"
        "(f) CI do domínio: ver `HOSTED_CI_REPORT.md` (IS-F004, IS-F005 e a decisão do dono, quando houver).\n",
        encoding="utf-8")
    # ---------------------------------------------------------------- HOSTED_CI
    lines, all_ok = [], True
    for s in load(raw / "hosted-ci" / hosted / "HOSTED_CI_SUMMARY.json"):
        all_ok &= s["ok"]
        runs = "; ".join(f"[{wf} {r['id']}]({r['url']}) {r['conclusion']}" for wf, r in s["runs"].items()) or "nenhum run de push"
        lines.append(f"| {s['repo'].split('/')[1]} | {s['role']} | `{s['commit'][:12]}` | {'verde' if s['ok'] else 'SEM PUSH VERDE'} | {runs} | {s['non_success_jobs'] or ''} |")
    dispatch = load(raw / "hosted-ci" / "stocks-predictor_6f857b2_run36363108348.json")
    djobs = ", ".join(f"{j['name']}={j['conclusion']}" for j in dispatch["jobs"])
    acc_path = raw / "hosted-ci" / hosted / "stocks_dispatch_acceptance.json"
    if acc_path.is_file():
        acc = load(acc_path)
        leak = next(c for c in acc["checks"] if "vazamento não" in c["check"])["leaks"]
        tree_log = raw / "hosted-ci" / hosted / "tree_scan_local.log"
        tree = tree_log.read_text(encoding="utf-8")
        stocks_text = (
            "O `ci.yml` do stocks-predictor dispara `push` só em `main` (intocável pela D-24 (4c)): nem a base `61fc017` "
            "nem o final_commit `6f857b2` têm run de push (IS-F004).\n\n"
            f"**Decisão do dono** (chat da sessão, 2026-09-28: \"{acc['decision_words']}\"; IS-F004 e IS-F005 "
            "`ACCEPTED_LIMITATION`): só para o stocks-predictor, o run `workflow_dispatch` do CI Pipeline no SHA exato "
            "vale como o run de C21 / prompt 9.3 e de C24.3 (f), com o job `secrets` vermelho só pelo falso positivo "
            "pré-existente fora da branch da missão.\n\n"
            f"Conferência mecânica da decisão ({cite(acc_path)}): **{acc['passed']} OK, {acc['failed']} falhas**, "
            f"aceito: {'sim' if acc['accepted'] else 'NÃO'}.\n\n"
            "| Conferência | Resultado |\n|---|---|\n"
            + "\n".join(f"| {c['check']} | {'OK' if c['ok'] else 'FALHA'} |" for c in acc["checks"]) + "\n\n"
            f"- final_commit: run [{dispatch['databaseId']}]({acc['final_run']}): {djobs}.\n"
            f"- base: run [{acc['base_run'].rsplit('/', 1)[1]}]({acc['base_run']}) (Etapa A), todos os jobs verdes.\n"
            + "".join(f"- vazamento acusado: commit `{x['commit'][:12]}` (branches {', '.join(x['remote_branches_containing'])}), "
                      f"`{x['path']}`:{x['line']} ({x['rule']}), ancestral do final_commit: "
                      f"{'sim' if x['ancestor_of_final_commit'] else 'não'}.\n" for x in leak)
            + f"- com o gitleaks vermelho, não rodaram no Actions: {', '.join(acc['skipped_after_gitleaks'])}. "
            "Reproduzidos localmente (diagnóstico, WSL do PC 2, NÃO é CI hospedado), com o mesmo gitleaks 8.24.3 "
            f"conferido pelo sha256 da release e os mesmos comandos do `ci.yml` ({cite(tree_log)}): "
            + ("varredura da árvore sem achados e controle detectou o token sintético (PASS)."
               if "RESULTADO PASS" in tree else "FALHA (ver o log).") + "\n")
    else:
        stocks_text = (
            "O `ci.yml` do stocks-predictor dispara `push` só em `main` (intocável pela D-24 (4c)): nem a base `61fc017` "
            "nem o final_commit `6f857b2` têm run de push (IS-F004). No SHA exato do final_commit há o run "
            f"`workflow_dispatch` [{dispatch['databaseId']}]({dispatch['url']}): {dispatch['conclusion']} — {djobs} "
            f"({cite(raw / 'hosted-ci' / 'stocks-predictor_6f857b2_run36363108348.json')}). O job `secrets` falha por um "
            "falso positivo pré-existente fora desta branch "
            f"({cite(raw / 'hosted-ci' / 'stocks-predictor_6f857b2_run36363108348_secrets_job.log')}; IS-F005). Decisão "
            "do dono pendente; o gate fica `NOT_RUN` com BLOCKED e não é relaxado pelo agente.\n")
    (m / "HOSTED_CI_REPORT.md").write_text(
        "# integration-stocks — HOSTED_CI_REPORT\n\n"
        "Gate `HOSTED_CI` (C21; prompt da sessão 9.3: só o run de **push** cujo SHA é exatamente o commit vale). Coletado "
        f"por `scripts/hosted_ci.py` ({cite(raw / 'hosted-ci' / hosted / 'HOSTED_CI_SUMMARY.json')}). Core e Ops não mudaram "
        "(CI da Etapa A, HERDADO).\n\n"
        "| Repo | Papel | Commit | Estado | Runs de push | Jobs não verdes |\n|---|---|---|---|---|---|\n" + "\n".join(lines) + "\n\n"
        "## stocks-predictor\n\n" + stocks_text, encoding="utf-8")
    # ---------------------------------------------------------------- PROTECTED
    prot = load(raw / protected_dir / "protected_check.json")
    f008 = {x["id"]: x for x in load(m / "FINDINGS.json")["findings"]}.get("IS-F008", {})
    f008_text = ("Conflito entre a C14 (novo ciclo) e a C15.1 (IS-F008): "
                 + (f"decidido pelo dono em {f008['owner_decision_taken']['date']} (\"{f008['owner_decision_taken']['words']}\": "
                    f"{f008['owner_decision_taken']['option_text']})"
                    if f008.get("status") == "ACCEPTED_LIMITATION" else "decisão do dono pendente."))

    def chain_text(s: dict) -> str:
        if "chain" not in s:
            return ""
        hops = " → ".join(f"`{h['file']}` (ponteiro `{h['pointer_sha256'][:16]}…`, arquivo "
                          f"`{(h['file_sha256'] or 'ausente')[:16]}…`)" for h in s["chain"]["hops"])
        return (f" Cadeia: {hops}; chega ao sha256 protegido com cada salto conferido: "
                f"**{'sim' if s['chain']['ok'] else 'NÃO'}**.")
    prow = "\n".join(f"| {d} | {v['repo']} | `{v['commit'][:12]}` | {v['items']} | {len(v['changed'])} |" for d, v in prot["domains"].items())
    (m / "PROTECTED_ARTIFACT_REPORT.md").write_text(
        "# integration-stocks — PROTECTED_ARTIFACT_REPORT\n\n"
        "Gate `PROTECTED_ARTIFACTS_UNCHANGED` (C15.1). O conjunto veio do PROTECTED_SET.json de `truth-map` e foi "
        f"reconferido por `scripts/protected_check.py` ({cite(raw / protected_dir / 'protected_check.json')}).\n\n"
        "| Domínio | Repo | Commit conferido | Itens | Alterados |\n|---|---|---|--:|--:|\n" + prow + "\n\n"
        f"Artefatos compartilhados conferidos por sha256: {len(prot['shared'])}; alterados: "
        f"{sum(not s['ok'] for s in prot['shared'])}. Total de itens: {prot['items_total']}; tudo igual (a letra da "
        f"C15.1): {'sim' if prot['all_unchanged'] else 'NÃO'}; tudo igual ou encadeado: "
        f"{'sim' if prot.get('all_unchanged_or_chained') else 'NÃO'}.\n\n" + f008_text + "\n"
        + "".join(f"\n- `{s['path']}`: esperado `{s['expected'][:16]}…`, atual `{s['current'][:16]}…`." + chain_text(s)
                  + "\n" for s in prot["shared"] if not s["ok"]), encoding="utf-8")
    # ---------------------------------------------------------------- SOAK
    soak = load(rt / "soak" / "SUMMARY.json")
    profile = load(m / "QUALIFICATION_PROFILE_INTEGRATION_STOCKS_V1.json")
    c = dict(soak["counters"])
    per_class = profile["minimums"].get("runs_per_failure_class", 0)
    c["relevant_failure_classes"] = sum(v >= per_class for v in c["failure_runs"].values())
    c["runs_per_failure_class"] = min(c["failure_runs"].values())
    floors = "\n".join(f"| {k} | {v} | {c.get(k, '-')} |" for k, v in profile["minimums"].items())
    zero = "\n".join(f"| {x['check']} | {'OK' if x['ok'] else 'FALHA'} |" for x in soak["checks"])
    llm = sorted((rt / "soak").glob("llm-*.audit.json"), key=lambda a: int(re.search(r"llm-(\d+)", a.name).group(1)))
    llm_cfg = load(m / "FROZEN_PARAMETERS.json")["decision_policy"]["stocks_config"]["llm_hypotheses"]
    # decisão de cada proposta: a saída do comando "propose llm <i>" no commands.log do soak
    soak_log = (rt / "soak" / "commands.log").read_text(encoding="utf-8")
    decided = {int(i): json.loads(out) for i, out in re.findall(
        r'"label": "propose llm (\d+)".*\n--- stdout\n(\{.*\})\n--- stderr', soak_log)}
    llm_rows = []
    for a in llm:
        doc = load(a)
        prop = load(a.with_name(a.name.replace(".audit.json", ".json")))
        got = decided.get(int(re.search(r"llm-(\d+)", a.name).group(1)), {})
        llm_rows.append(f"| `{prop['proposal_id']}` | {prop['request']['hypothesis_id']} | "
                        f"{doc['model'].get('model')} | `{str(doc['model'].get('digest'))[:16]}` | "
                        f"{got.get('decision')} {got.get('reason_code')} ({got.get('rule')}) | "
                        f"{'nenhuma' if got.get('task') is None else got.get('task')} |")
    (m / "SOAK_REPORT.md").write_text(
        "# integration-stocks — SOAK_REPORT\n\n"
        "Gate `SOAK` (C10, perfil `QUALIFICATION_PROFILE_INTEGRATION_STOCKS_V1.json`, lido e não alterado). Linux primário, "
        f"run `{run}`, dados reais públicos, runtime só com wheels publicadas. Fonte: {cite(rt / 'soak' / 'SUMMARY.json')}; "
        f"comandos brutos em `RAW_LOGS/runtime/{run}/soak/commands.log`.\n\n"
        f"Resultado: **{soak['passed']} conferências OK, {soak['failed']} falhas**.\n\n"
        "| Piso | Mínimo | Obtido |\n|---|--:|--:|\n" + floors + "\n\n"
        f"Execuções por classe de falha: {json.dumps(c['failure_runs'])}. Decisões: {json.dumps(c['decisions'])}.\n\n"
        "| Conferência (tolerância zero e fim) | Resultado |\n|---|---|\n" + zero + "\n\n"
        "## Propostas de LLM (auditadas; não são gate, C9)\n\n"
        "Modelo local (Ollama no runner). Cada proposta passa pela mesma DecisionPolicy (`cain research propose "
        "--proposal`); a decisão e a task vêm da saída desse comando no `commands.log`. Hipóteses só para o LLM (ciclo 2, "
        f"`FROZEN_PARAMETERS.json` → `stocks_config.llm_hypotheses`): {', '.join(llm_cfg['hypotheses'])}. "
        f"{llm_cfg['experiment']}.\n\n"
        "| Proposta | Hipótese escolhida | Modelo | Digest | Decisão | Task |\n|---|---|---|---|---|---|\n"
        + "\n".join(llm_rows) + "\n", encoding="utf-8")
    # ---------------------------------------------------------------- ENVELOPE_V2_CONFORMANCE
    fmx = {p["point"]: p for p in fm}
    (m / "ENVELOPE_V2_CONFORMANCE_REPORT.md").write_text(
        "# integration-stocks — ENVELOPE_V2_CONFORMANCE_REPORT\n\n"
        "Gate `ENVELOPE_V2_CONFORMANCE`. Protocolo V2 consumido da release congelada `predictor-research-protocol` "
        f"{targets['protocol']['version']} (`{targets['protocol']['sha256'][:16]}…`, ENVELOPE_V2_FREEZE.json), sem mudança; "
        f"transporte `predictor-research-transport` {targets['transport']['version']} (só a entrada stocks na allowlist).\n\n"
        "| Propriedade | Evidência |\n|---|---|\n"
        f"| adapter só pela `adapter_api` (`Circuit.submit_request/show`), sem console script, só stdlib | cleanroom-final `adapters` "
        f"({finals['adapters']['tests']} testes) e `conformance` ({finals['conformance']['tests']}), {cite(rt / 'cleanroom-final' / 'cleanroom_final.log')} |\n"
        f"| pedido V2 → `stocks-research-request/1` com `client_ref`; hash canônico sem `client_ref` = vetor da Etapa A | "
        f"C24.3 (d): {cd['passed']}/{cd['passed'] + cd['failed']} |\n"
        f"| payload de domínio byte-idêntico ao `show` em todo RESULT/DUPLICATE | E2E {e2e['passed']}/{e2e['passed'] + e2e['failed']}, "
        f"Windows {wine['passed']}/{wine['passed'] + wine['failed']} |\n"
        f"| versão errada, mesmo ID com outro payload, envelope válido da task errada | F11 {fmx['F11']['passed']} OK, F12 "
        f"{fmx['F12']['passed']} OK, F13 {fmx['F13']['passed']} OK |\n"
        f"| resultado de outro domínio nunca aceito | isolamento {iso['passed']}/{iso['passed'] + iso['failed']} |\n",
        encoding="utf-8")
    # ---------------------------------------------------------------- DECISION_POLICY
    cfg_rows = "\n".join(f"| {r['candidate']} | {r['decision']} | {r['reason_code']} | {r['rule']} |" for r in n1f["receipts"])
    # configuração do Stocks: lida do FROZEN_PARAMETERS.json congelado (nenhum valor digitado aqui)
    frozen = m / "FROZEN_PARAMETERS.json"
    dp = load(frozen)["decision_policy"]
    sc = dp["stocks_config"]
    closed = sorted(sc["closed_hypotheses"], key=lambda h: int(h.split(":H")[1]))
    closed_by_state = {}
    for h in closed:
        closed_by_state.setdefault(sc["closed_hypotheses"][h], []).append(h.split(":")[1])
    cfg_text = (
        f"Fonte: {cite(frozen)}, chave `decision_policy.stocks_config`.\n\n"
        f"- fontes: {sc['source']['repo']} `{sc['source']['commit']}` (SHA completo): "
        + ", ".join(f"`{f['path']}`" for f in sc["source"]["files"])
        + f"; contrato `{sc['source']['contract']['path']}` (`{sc['source']['contract']['sha256'][:16]}…`);\n"
        f"- tipos de pedido: {', '.join(sc['allowed_request_types'])};\n"
        f"- hipóteses que a política nunca reabre ({len(closed)}, {closed[0].split(':')[1]}..{closed[-1].split(':')[1]}): "
        + "; ".join(f"{k} {', '.join(v)}" for k, v in closed_by_state.items()) + ";\n"
        f"- famílias congeladas ({len(sc['frozen_families'])}): {', '.join(sc['frozen_families'])};\n"
        f"- hipóteses propostas pela missão: {', '.join(sc['proposable_hypotheses'])};\n"
        "- sobreposição de parâmetros no molde do LLM (`proposal_overlays`): "
        + "; ".join(f"{h} {json.dumps(o, sort_keys=True)}" for h, o in sc.get("proposal_overlays", {}).items()) + ";\n"
        f"- custos: fee {sc['costs']['fee_bps']} bps + slippage {sc['costs']['slippage_bps']} bps ({sc['costs']['source']});\n"
        f"- prioridade máxima {sc['max_priority_hint']}; budget {json.dumps(sc['budget'])}; cooldown "
        f"{json.dumps({k: v for k, v in sc['cooldown'].items() if k != 'negative_result_states'})};\n"
        + "".join(f"- {k}: {v}\n" for k, v in sc["known_cautions"].items()))
    (m / "DECISION_POLICY_REPORT.md").write_text(
        "# integration-stocks — DECISION_POLICY_REPORT\n\n"
        f"Gate `DECISION_POLICY` (C12). Política `{dp['id']}` versão {dp['version']} do `cain-research` "
        f"{targets['cain']['version']} (`{dp['policy_module']['path']}`, sha256 `{dp['policy_module']['sha256'][:16]}…`, "
        f"conferido em `{dp['policy_module']['cain_commit'][:12]}`), receipt `cain-decision-receipt/1`; configuração do "
        "Stocks empacotada em `src/cain/orchestration/data/stocks.json`.\n\n"
        "## Regras, na ordem de avaliação (FROZEN_PARAMETERS.json → decision_policy.rule_order)\n\n"
        + "\n".join(f"{i}. {r}" for i, r in enumerate(dp["rule_order"], start=1)) + "\n\n"
        "## Configuração do Stocks (FROZEN_PARAMETERS.json → decision_policy.stocks_config)\n\n" + cfg_text + "\n"
        "## Decisões do N+1 (receipt em 3 processos novos, byte a byte)\n\n"
        f"Fonte: {cite(rt / 'n-plus-1' / 'frozen' / 'SUMMARY.json')}.\n\n"
        "| Candidata | Decisão | Motivo | Regra |\n|---|---|---|---|\n" + cfg_rows + "\n\n"
        "## Limites do framework achados antes dos congelados (FROZEN_PARAMETERS.json → stocks_config)\n\n"
        + "".join(f"- {x['id']}: {x['fact']} Estado: {x.get('cycle2_status', x['decision'])}\n"
                  for x in sc["framework_limits_found_before_freeze"])
        + "".join(f"- {x['id']}: {x['fact']} Decisão: {x['decision']}\n"
                  for x in sc.get("framework_limits_found_before_cycle2", [])), encoding="utf-8")
    print("relatórios gerados")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
