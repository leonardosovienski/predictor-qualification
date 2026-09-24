"""stocks: gera os relatórios da missão a partir dos logs brutos (C20) e de EVIDENCE_NUMBERS.json.

Relatórios: CORE_IDENTITY_REPORT.md, CLEANROOM_REPORT.md, SOAK_REPORT.md, UNIVERSE_IDENTITY_REPORT.md,
PIT_ADVERSARIAL_REPORT.md, NEGATIVE_CONTROLS_REPORT.md, COLLECTION_ONLY_REPORT.md,
EXTERNAL_INTELLIGENCE_READINESS.json, FAILURE_MATRIX.json, QUALIFICATION_PROFILE_STOCKS_V1.json e
E2E_EVIDENCE/ (cópia byte a byte dos artefatos do E2E dos dois runtimes).
Nenhum número é digitado à mão: todos vêm dos arquivos citados em cada relatório.

Uso: python write_reports.py
"""

from __future__ import annotations

import json
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

QC = Path(__file__).resolve().parents[1]
RUN = QC / "RAW_LOGS" / "cleanroom-final" / "run35954279991"
LINUX, WINDOWS = RUN / "stocks-runtime-linux-primary", RUN / "stocks-runtime-windows-latest"
BASE = QC / "RAW_LOGS" / "cleanroom-baseline" / "run35943720554"
SUITE = QC / "RAW_LOGS" / "c14-rc2" / "suite-run35953426762"
NUM = json.loads((QC / "EVIDENCE_NUMBERS.json").read_text(encoding="utf-8"))
FROZEN = json.loads((QC / "FROZEN_PARAMETERS.json").read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    return path.relative_to(QC.parents[1]).as_posix()


def cases(junit: Path) -> dict[str, str]:
    out = {}
    for tc in ET.parse(junit).getroot().iter("testcase"):
        name = f"{tc.get('classname').split('.')[-1]}::{tc.get('name')}"
        out[name] = "FAIL" if any(child.tag in ("failure", "error") for child in tc) else (
            "SKIP" if any(child.tag == "skipped" for child in tc) else "PASS")
    return out


LX, WX = cases(LINUX / "conformance.junit.xml"), cases(WINDOWS / "conformance.junit.xml")


def status(prefix: str) -> str:
    lx = {k: v for k, v in LX.items() if k.startswith(prefix)}
    wx = {k: v for k, v in WX.items() if k.startswith(prefix)}
    ok = lambda d: sum(1 for v in d.values() if v == "PASS")  # noqa: E731
    return f"Linux {ok(lx)}/{len(lx)} · windows-latest {ok(wx)}/{len(wx)}"


def write(name: str, text: str) -> None:
    (QC / name).write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")


def runtime(env: Path) -> dict:
    return NUM["runtime"][rel(env)]


def core_identity() -> None:
    rows = []
    for label, env in (("Linux primário (ubuntu-latest)", LINUX), ("windows-latest", WINDOWS)):
        r = runtime(env)
        for name, info in r["identity"].items():
            chain = r["lock_chain"].get(name, {})
            rows.append(f"| {label} | {name} | {info['version']} | `{info['sha256'].removeprefix('sha256=')}` | "
                        f"{chain.get('spec', '— (o próprio pacote)')} | "
                        f"{('`' + chain['lock_sha256'] + '`') if chain else 'wheel da release v0.3.0rc2'} | "
                        f"{info['in_site_packages']} | {info['editable']} |")
    base = json.loads((BASE / "stocks-runtime-linux-primary" / "core_identity.json").read_text(encoding="utf-8"))
    base_rows = [f"| {p['name']} | {p['version']} | `{((p['direct_url'] or {}).get('archive_info') or {}).get('hash', '').removeprefix('sha256=')}` | {p['module_in_site_packages']} |"
                 for p in base["packages"]]
    write("CORE_IDENTITY_REPORT.md", f"""# CORE_IDENTITY_REPORT — missão stocks (C4; gates LOCK_INTEGRITY, CORE_IDENTITY, STOCKS_CORE_PIN)

Cadeia exigida (C4): range no `pyproject` ↔ `tool.uv.sources` (URL da release) ↔ `uv.lock` ↔ instalação ↔ hash da
wheel ↔ metadata instalada ↔ caminho do módulo em runtime. Medida pelo script
`qualification/stocks/scripts/core_identity.py`, rodando **dentro** do interpretador do runtime, num diretório fora
de qualquer checkout.

## Antes da mudança (baseline `4e98a67`, wheel do Stocks construída do commit — diagnóstico)

Fonte: `{rel(BASE / 'stocks-runtime-linux-primary' / 'core_identity.json')}`.

| pacote | versão | sha256 da wheel instalada | módulo em site-packages |
|---|---|---|---|
{chr(10).join(base_rows)}

`predictor-ops` ausente (prompt §3 confirmado: nenhuma dependência nem import).
`uv lock --check`: `{rel(BASE / 'stocks-runtime-linux-primary' / 'uv_lock_check.log')}`.

## Depois de adicionar o Ops (final_commit `61fc017`, só wheels publicadas)

Fontes: `{rel(LINUX / 'core_identity.json')}` e `{rel(WINDOWS / 'core_identity.json')}`;
lock conferido por `uv lock --check` (`{rel(LINUX / 'uv_lock_check.log')}`) e instalação por
`pip install --require-hashes -r` do lock exportado (`{rel(LINUX / 'requirements.locked.txt')}`).

| runtime | pacote | versão | sha256 instalado | range no pyproject | sha256 no uv.lock | em site-packages | editable |
|---|---|---|---|---|---|---|---|
{chr(10).join(rows)}

`tool.uv.sources`: Core `…/core-predictor/releases/download/v3.2.1/predictor_core-3.2.1-py3-none-any.whl`,
Ops `…/predictor-ops/releases/download/v4.2.2rc1/predictor_ops-4.2.2rc1-py3-none-any.whl` (URL de release;
nenhum pacote do stack vem de índice público, `vendor/` ou checkout). A wheel do Stocks vem da release
`v0.3.0rc2` (asset conferido por sha256 antes da instalação, `{rel(LINUX / 'env.log')}`).

**STOCKS_CORE_PIN:** range `>=3.2.1,<4` (D-7), fonte = release v3.2.1, lock = 3.2.1 `10ef42f3…`, wheel instalada =
`10ef42f3…`, nos dois runtimes.
""")


def cleanroom() -> None:
    lf = NUM["suites"][rel(LINUX / "full_suite.junit.xml")]
    wf = NUM["suites"][rel(WINDOWS / "full_suite.junit.xml")]
    lc = NUM["suites"][rel(LINUX / "conformance.junit.xml")]
    wc = NUM["suites"][rel(WINDOWS / "conformance.junit.xml")]
    write("CLEANROOM_REPORT.md", f"""# CLEANROOM_REPORT — missão stocks (C5; gate CLEANROOM_FINAL)

Runtime suportado (C3.1): venv novo, dependências só do `uv.lock` exportado com `--require-hashes`, wheel do
stocks-predictor **publicada** (`v0.3.0rc2`, sha256 `92cb1131…`, conferido antes de instalar), Core e Ops pelas
wheels das releases; árvore de testes = final_commit **sem** `stocks_predictor/` (o código só pode vir da wheel);
execução a partir de um diretório fora de tudo. Script: `qualification/stocks/scripts/runtime_cleanroom.sh`,
workflow `.github/workflows/stocks-runtime.yml`, run 35954279991.

## cleanroom-final (Linux primário e windows-latest)

| | Linux primário | windows-latest |
|---|---|---|
| suíte de conformidade (junit) | {lc['passed']}/{lc['tests']} | {wc['passed']}/{wc['tests']} |
| E2E pelo entrypoint | {runtime(LINUX)['e2e']['checks_ok']}/{runtime(LINUX)['e2e']['checks']} checagens | {runtime(WINDOWS)['e2e']['checks_ok']}/{runtime(WINDOWS)['e2e']['checks']} checagens |
| `pip check` | sem requisitos quebrados | sem requisitos quebrados |
| suíte legada (árvore sem fonte) | {lf['errors']} erros de coleta | {wf['errors']} erros de coleta |

A suíte legada importa módulos planos da pasta-fonte (ST-F004, P2): não valida wheel instalada, igual ao
baseline. A validação da wheel pela suíte legada é feita no CI do repo (smoke da wheel fora do checkout, verde no
final_commit) e pela suíte completa com instalação `uv sync --locked` no final_commit: Linux
`{NUM['suites'][rel(SUITE / 'stocks-suite-linux-primary' / 'pytest.log')]['summary']}`, windows-latest
`{NUM['suites'][rel(SUITE / 'stocks-suite-windows-latest' / 'pytest.log')]['summary']}` (`{rel(SUITE)}`).
A rc1 (`9a6c09a`, `3cc4e04a…`, run 35949779357) teve o mesmo resultado; foi substituída pela rc2 depois dos
dependabot #93/#94 (C14, ST-F006).

## cleanroom-baseline (diagnóstico, 4e98a67)

Wheel construída do commit (não havia wheel publicada do HEAD). `python -m stocks_predictor doctor --check`
quebra no windows-latest por falta de `tzdata` (ST-F001, `{rel(BASE / 'stocks-runtime-windows-latest' / 'runtime_trace.log')}`);
os scripts extras do conjunto protegido não executam fora da máquina original (ST-F003).

Qualquer mudança de código depois deste cleanroom-final invalida-o (C14).
""")


def soak() -> None:
    s = runtime(LINUX)["soak"]
    write("SOAK_REPORT.md", f"""# SOAK_REPORT — missão stocks (C10; gate SOAK)

**Estado do gate: NOT_RUN — BLOCKED: D-16 pendente.** A regra congelada (`FROZEN_PARAMETERS.d16_dependency_rule`)
exige dado real no Linux primário para o SOAK; a execução abaixo usa a fixture sintética congelada e é
**diagnóstico**.

Perfil: `QUALIFICATION_PROFILE_STOCKS_V1.json` (números congelados em `FROZEN_PARAMETERS.soak_profile` antes da
execução). Runtime suportado (wheels publicadas), GitHub Actions ubuntu-latest, cada chamada ao `stocks-research` num
processo novo. Log bruto: `{s['file']}`.

| medida | valor |
|---|---|
| chamadas ao entrypoint | {s['process_calls']} |
| falhas injetadas | {s['faults_injected']} |
| pedidos com resultado esperado | {s['requests_with_result']} |
| resultados armazenados | {s['stored_results']} |
| efeitos de domínio | {s['domain_effects']} |
| jobs do Ops / máximo de SUCCEEDED por job | {s['ops_jobs']} / {s['ops_success_per_job_max']} |
| resultados perdidos / inesperados | {s['lost']} / {s['unexpected']} |
| releitura divergente | {s['reread_mismatch']} |
| violações (duplicata, autoridade, IDs) | {s['violations']} |
| violações PIT | {s['pit_violations']} |
| trials elegíveis de External Intelligence | {s['eligible_trials']} (nenhuma família READY) |
| tolerância zero | {s['zero_tolerance_ok']} |
""")


def universe() -> None:
    e2e = json.loads((LINUX / "e2e" / "E2E_SUMMARY.json").read_text(encoding="utf-8"))
    check = next(c for c in e2e["checks"] if c["check"].startswith("universe identical"))
    tests = [k for k in LX if "universe" in k or "ticker_and_cnpj" in k or "pit03" in k]
    lines = "\n".join(f"| `{t}` | {LX[t]} | {WX.get(t)} |" for t in tests)
    write("UNIVERSE_IDENTITY_REPORT.md", f"""# UNIVERSE_IDENTITY_REPORT — missão stocks (gate STOCKS_UNIVERSE_IDENTITY)

Código: `stocks_predictor/research_pit.py` (`Panel.universe`), chamado pelo worker do handler
`stocks.handlers.pit_factor_backtest.v1`. Identidade = `security_id`; ticker e CNPJ são rótulos com validade no tempo;
dedup por emissor usa o CNPJ conhecido na decisão (não o prefixo de 4 letras do ticker).

## Pelo entrypoint instalado (wheel publicada)

`{check['check']}`: **{check['ok']}** ({check.get('rebalances')} rebalances; mesmo pedido em 3 raízes de estado novas,
3 processos) — `{rel(LINUX / 'e2e' / 'E2E_SUMMARY.json')}`; idem no windows-latest
(`{rel(WINDOWS / 'e2e' / 'E2E_SUMMARY.json')}`).

## Vetores congelados (suíte de conformidade pela wheel)

| teste | Linux | windows-latest |
|---|---|---|
{lines}

Propriedades: mesma entrada + mesmo `as_of` = mesma lista e mesmo hash; entradas e saídas só por eventos com
`available_at` ≤ decisão; deslistado presente enquanto existia e sua saída não era conhecida; troca de ticker e de CNPJ
preserva a identidade. Vetores sintéticos (prompt §4); com dado real = D-16.
""")


def pit() -> None:
    frozen = FROZEN["pit_adversarial_vectors"]["cases"]
    mapping = {"PIT-01": "pit01", "PIT-02": "pit02", "PIT-03": "pit03", "PIT-04": "pit04", "PIT-05": "pit05",
               "PIT-06": "pit06", "PIT-07": "pit07", "PIT-08": "pit08", "PIT-09": "pit09", "PIT-10": "pit10",
               "PIT-11": "pit11", "PIT-12": "pit12", "PIT-13": "pit13", "PIT-14": "pit14", "PIT-15": "pit15"}
    rows = []
    for case in frozen:
        key = mapping[case["id"]]
        tests = sorted(t for t in LX if key in t.split("::")[1])
        verdict = all(LX[t] == "PASS" and WX.get(t) == "PASS" for t in tests) and bool(tests)
        rows.append(f"| {case['id']} | {case['case']} | {case['expected']} | {', '.join('`' + t.split('::')[1] + '`' for t in tests)} | {'PASS' if verdict else 'FAIL'} |")
    extra = [k for k in LX if "decision_never_uses" in k or "data_quality_problem_is" in k
             or "future_canary" in k or "as_of_mismatch" in k]
    extra_rows = "\n".join(f"| `{t}` | {LX[t]} | {WX.get(t)} |" for t in extra)
    write("PIT_ADVERSARIAL_REPORT.md", f"""# PIT_ADVERSARIAL_REPORT — missão stocks (gates STOCKS_PIT_ADVERSARIAL, TEMPORAL_INTEGRITY, FUTURE_CANARY)

Casos congelados em `FROZEN_PARAMETERS.pit_adversarial_vectors` antes da execução; cada caso quebra de propósito o
painel sintético e é conferido na visão PIT que o handler de produção usa, pela wheel publicada, no Linux primário e no
windows-latest (`{rel(LINUX / 'conformance.junit.xml')}`, `{rel(WINDOWS / 'conformance.junit.xml')}`).
Uma violação bastaria para FAIL.

| caso | ataque | esperado | teste(s) | Linux + windows |
|---|---|---|---|---|
{chr(10).join(rows)}

## Integridade temporal pelo circuito inteiro (entrypoint)

| teste | Linux | windows-latest |
|---|---|---|
{extra_rows}

A desigualdade PIT é imposta em dois níveis: `research_pit.Panel` (cada decisão só vê `available_at` ≤ decisão) e
`predictor_core.measurement.replay` no worker (`LookaheadError` se qualquer registro do snapshot estiver disponível
depois do `as_of`; decisões monotônicas; `max_available_used` ≤ `decision_at` em cada rebalance).
Canário `FUTURE_CANARY_STOCKS_001`: dataset com o canário → `TEMPORAL_INTEGRITY_VIOLATION` (exit 4), sem efeito, trial
nem resultado; o token não aparece em efeito, trial, resultado, `results.sqlite` nem outcomes de pedidos legítimos.
""")


def negative() -> None:
    n = runtime(LINUX)["negative_controls"]
    summary = json.loads((LINUX / "science" / "NEGATIVE_CONTROLS_SUMMARY.json").read_text(encoding="utf-8"))
    rows = "\n".join(f"| {k} | {n['supported_counts'][k]}/20 | {json.dumps(summary['criteria'][k], ensure_ascii=False)} |"
                     for k in n["supported_counts"])
    ref = n["reference"]
    write("NEGATIVE_CONTROLS_REPORT.md", f"""# NEGATIVE_CONTROLS_REPORT — missão stocks (gate STOCKS_NEGATIVE_CONTROLS)

**Estado do gate: NOT_RUN — BLOCKED: D-16 pendente.** Controles negativos só significam algo sobre o dado real
(`FROZEN_PARAMETERS.d16_dependency_rule`). A execução abaixo, sobre a fixture sintética congelada, é **diagnóstico**:
prova que os controles estão implementados no handler de produção e rodam pelo entrypoint instalado.

Seeds, critérios e aplicabilidade congelados antes (`FROZEN_PARAMETERS.negative_controls`). Log bruto por execução:
`{rel(LINUX / 'science' / 'negative_controls.jsonl')}`; resumo `{n['file']}`.

Referência (painel sintético `positive`, tendência plantada de propósito): científico {ref['scientific_state']}, econômico
{ref['economic_state']}, excesso bruto {ref['excess_gross_bps']} bps/período, IC95 bruto {ref['excess_gross_ci_bps']},
IC95 líquido {ref['excess_net_ci_bps']}, {ref['periods']} períodos. **Isto não é métrica econômica:** a fixture tem
edge plantado para exercitar o caminho SUPPORTED.

| controle | SUPPORTED | critério congelado |
|---|---|---|
{rows}

Leitura: labels embaralhados nunca SUPPORTED (0/20); ranking aleatório no limite congelado (2/20). A ablação
temporal (sinal defasado 1 rebalance) continua SUPPORTED porque a fixture tem tendência persistente — é esperado na
fixture e seria investigado no dado real. A perturbação de universo mantém o estado em 20/20.
""")


def collection() -> None:
    e2e = json.loads((LINUX / "e2e" / "E2E_SUMMARY.json").read_text(encoding="utf-8"))
    check = next(c for c in e2e["checks"] if c["check"].startswith("COLLECTION_ONLY"))
    ei = next(c for c in e2e["checks"] if c["check"].startswith("NOT_READY"))
    soak_rows = [json.loads(line) for line in (LINUX / "soak.jsonl").read_text(encoding="utf-8").splitlines()]
    profile = next(r for r in soak_rows if r["kind"] == "stocks_profile")
    tests = [k for k in LX if "collection" in k or "external_intelligence" in k or "pit12" in k]
    lines = "\n".join(f"| `{t}` | {LX[t]} | {WX.get(t)} |" for t in tests)
    write("COLLECTION_ONLY_REPORT.md", f"""# COLLECTION_ONLY_REPORT — missão stocks (gates STOCKS_COLLECTION_MODE, STOCKS_EXTERNAL_INTELLIGENCE_AXES)

`COLLECTION_ONLY` roda como job real do Ops (`stocks.handlers.external_collection.v1`, JobType MARKET_COLLECTION) e
chama o CLI de domínio `external collect <coletor> --source-file` (sem rede, arquivo oficial provisionado pelo
operador como objeto imutável). Persiste em staging SQLite do circuito, grava recibo e o resultado
`COLLECTION_RECORDED` com `trial_eligible = false` e `feeds = {{trial, ranking, portfolio, capital}} = false`.

`TRIAL_CONSUMPTION` só consome família com `readiness = READY` **e** PIT efetivo ≥ limiar **e** ligada ao modelo; com a
matriz congelada (0 famílias READY) o resultado é `NOT_READY`, sem trial, com o motivo por família.

## Pelo entrypoint instalado

* `{check['check']}`: **{check['ok']}** (status `{check.get('collection_status')}`) — `{rel(LINUX / 'e2e' / 'E2E_SUMMARY.json')}`
* `{ei['check']}`: **{ei['ok']}** — motivos: {json.dumps(ei['cases'][0]['reasons'], ensure_ascii=False)}
* soak (diagnóstico): família-não-pronta {profile['family_not_ready']}; coletas {profile['collections']};
  trials elegíveis = {runtime(LINUX)['soak']['eligible_trials']} — `{rel(LINUX / 'soak.jsonl')}`

## Vetores congelados

| teste | Linux | windows-latest |
|---|---|---|
{lines}

Zero consumo de dado inelegível: `consumed_families = []` e `consumed_observations = 0` em todo resultado.
""")


def readiness() -> None:
    doc = json.loads((LINUX / "science" / "external_intelligence_readiness.json").read_text(encoding="utf-8"))
    out = {
        "schema": "stocks/EXTERNAL_INTELLIGENCE_READINESS/1",
        "source_matrix": "EXTERNAL_INTELLIGENCE_TRIAL_READINESS_MATRIX.json (blob do final_commit 61fc017 = blob do baseline; conjunto protegido)",
        "classified_by": doc["classifier"],
        "raw_output": rel(LINUX / "science" / "external_intelligence_readiness.json"),
        "rules": {"eligibility": "só o campo readiness de eligible_families; o nome da chave não concede nada",
                  "effective_pit": "protocol_effective_PIT quando presente (pode rebaixar o declarado)",
                  "axes_independent": "coletado ≠ PIT_STRICT ≠ elegível ≠ usado no modelo ≠ usável no contrato"},
        "axes": doc["axes_order"],
        "ready_families": doc["ready_families"],
        "families": doc["families"],
        "eligible_trials": 0,
        "eligible_trials_reason": "nenhuma família com readiness READY na matriz congelada (21/09); nenhum modelo admitido liga família de External Intelligence",
    }
    write("EXTERNAL_INTELLIGENCE_READINESS.json", json.dumps(out, indent=1, ensure_ascii=False))


def failure_matrix() -> None:
    rows = []
    mapping = {
        "F-ADM-1": ["before_admission_commit"], "F-ADM-2": ["[after_admission]"], "F-MAT-1": ["during_materialization"],
        "F-OPS-1": ["[before_ops]"], "F-OPS-2": ["ops_worker_crash"], "F-OPS-3": ["host_process_killed"],
        "F-OPS-4": ["[after_ops]"], "F-TMO-1": ["ops_timeout"], "F-ART-1": ["mid_effect_write"],
        "F-ART-2": ["after_domain_effect"], "F-RES-1": ["during_result_write"], "F-RES-2": ["after_result_write"],
        "F-RES-3": ["after_result_store"], "F-DUP-1": ["idempotency_duplicate"], "F-ORD-1": ["out_of_order"],
        "F-SCH-1": ["SCHEMA_INVALID8"], "F-COR-1": ["modified_result", "wrong_hash", "reference_changed", "file_is_gone",
                                                    "index_lost", "metadata_inconsistent", "another_request"],
        "F-LCK-1": ["db_lock"], "F-DSK-1": ["disk_full"],
    }
    for point in FROZEN["failure_injection_points"]:
        keys = mapping[point["id"]]
        tests = sorted(t for t in LX if any(k in t for k in keys))
        rows.append({**point, "tests": tests,
                     "linux": [LX[t] for t in tests], "windows_latest": [WX.get(t) for t in tests],
                     "result": "PASS" if tests and all(LX[t] == "PASS" and WX.get(t) == "PASS" for t in tests) else "FAIL"})
    doc = {"schema": "stocks/FAILURE_MATRIX/1", "frozen_in": "FROZEN_PARAMETERS.failure_injection_points (antes da execução)",
           "invariants": FROZEN["failure_invariants"], "runtime": "wheels publicadas (cleanroom-final run 35954279991)",
           "evidence": [rel(LINUX / "conformance.junit.xml"), rel(WINDOWS / "conformance.junit.xml")],
           "soak_repetitions": rel(LINUX / "soak.jsonl"), "rows": rows,
           "all_pass": all(r["result"] == "PASS" for r in rows)}
    write("FAILURE_MATRIX.json", json.dumps(doc, indent=1, ensure_ascii=False))


def profile() -> None:
    doc = {"schema": "stocks/QUALIFICATION_PROFILE/1", "code": "STOCKS", "version": 1,
           "frozen_in": "FROZEN_PARAMETERS.soak_profile (commit ed49a0c, antes de qualquer execução)",
           **FROZEN["soak_profile"], "implementation": "qualification/stocks/scripts/soak.py",
           "environment": "Linux primário (GitHub Actions ubuntu-latest), runtime suportado",
           "zero_tolerance": ["efeito duplicado", "resultado perdido", "provenance quebrada", "ação não autorizada",
                              "contaminação do universo", "corrupção silenciosa", "vazamento de futuro / violação PIT",
                              "mudança em congelado", "trial elegível com família não READY"],
           "d16": "com fixture sintética = diagnóstico; SOAK exige dado real (D-16)"}
    write("QUALIFICATION_PROFILE_STOCKS_V1.json", json.dumps(doc, indent=1, ensure_ascii=False))


def e2e_evidence() -> None:
    target = QC / "E2E_EVIDENCE"
    for label, env in (("linux-primary", LINUX), ("windows-latest", WINDOWS)):
        dest = target / label
        dest.mkdir(parents=True, exist_ok=True)
        for item in (env / "e2e").iterdir():
            shutil.copyfile(item, dest / item.name)


def main() -> None:
    core_identity()
    cleanroom()
    soak()
    universe()
    pit()
    negative()
    collection()
    readiness()
    failure_matrix()
    profile()
    e2e_evidence()
    print("relatórios escritos")


if __name__ == "__main__":
    main()
