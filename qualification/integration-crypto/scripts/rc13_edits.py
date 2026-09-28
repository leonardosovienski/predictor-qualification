"""integration-crypto na cain 0.4.13rc13 + transporte 0.1.0rc6 (C14): alvos, CI hospedado, segredos, relatórios, achados."""
import hashlib
import json
from pathlib import Path

M = Path("/home/superleo13/predictors/work/integration-crypto-predictor-qualification/qualification/integration-crypto")
CAIN_OLD, CAIN_NEW = "302a5c8c4c24a884773e327e0f5855dd98f94d08", "960fb25614709bd95ce607c8dfb80892d901d883"
ECO_OLD, ECO_NEW = "b11494ae211e79e2e5faaa4b874470f5b6ce15ec", "bac1f7b7b3ae687e4c75ff3849ccb1f458dca097"

# runtime_targets
p = M / "runtime_targets.json"
t = json.loads(p.read_text(encoding="utf-8"))
t["note"] = ("final_commits e final_wheels do runtime suportado desta missão (C3.1, C5); commit = o da tag da pré-release; "
             "C14 de 2026-09-28: cain 0.4.13rc13 (molde do LLM sem task recusada, allowed_requests, linter, findings v2; "
             "publicada pela sessão STOCKS) e predictor-research-transport 0.1.0rc6 (trava exclusiva por domínio no "
             "consumidor: CONSUMER_BUSY; corrige IC-F016 e IC-F017); congelados do ciclo 3 sem mudança")
t["cain"] = {"repo": "leonardosovienski/cain", "version": "0.4.13rc13", "tag": "v0.4.13rc13", "commit": CAIN_NEW,
             "url": "https://github.com/leonardosovienski/cain/releases/download/v0.4.13rc13/cain_research-0.4.13rc13-py3-none-any.whl",
             "sha256": "a1d94fd52762d6f8a9587f88064f53996aa46fcddad6be893272cb8079676854"}
t["transport"] = {"repo": "leonardosovienski/ecosystem-predictor", "version": "0.1.0rc6",
                  "tag": "predictor-research-transport-v0.1.0rc6", "commit": ECO_NEW,
                  "url": "https://github.com/leonardosovienski/ecosystem-predictor/releases/download/predictor-research-transport-v0.1.0rc6/predictor_research_transport-0.1.0rc6-py3-none-any.whl",
                  "sha256": "6c7e83c4d93d4802b7cdfbc569b0828cde34ccd2241b5a274003ff21c9daec33"}
p.write_text(json.dumps(t, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

(M / "hosted_ci_final_targets_rc13.json").write_text(
    f'[\n {{"repo": "leonardosovienski/cain", "commit": "{CAIN_NEW}", "role": "final"}},\n'
    f' {{"repo": "leonardosovienski/ecosystem-predictor", "commit": "{ECO_NEW}", "role": "final"}},\n'
    ' {"repo": "leonardosovienski/cripto-predictor", "commit": "ee3d3d17de0b76cf731808243ffa838a0f5ee8cc", "role": "final"}\n]\n',
    encoding="utf-8")

s = M / "scripts/secrets_scan.py"
x = s.read_text(encoding="utf-8")
for old, new in ((CAIN_OLD, CAIN_NEW), (ECO_OLD, ECO_NEW)):
    assert x.count(old) == 1, old
    x = x.replace(old, new)
s.write_text(x, encoding="utf-8")

r = M / "scripts/render_reports.py"
y = r.read_text(encoding="utf-8")
for old, new in (("sufixo (ex.: -c14, -c14s, -ciclo2, -ciclo3)", "sufixo (ex.: -c14, -c14s, -ciclo2, -ciclo3, -rc13)"),
                 ('"main também está verde). A "',
                  '"main também está verde). C14 da rc13: cain `960fb25` (0.4.13rc13) e ecosystem `bac1f7b` (transporte "\n'
                  '            "0.1.0rc6), com o run da tag e o do main. A "')):
    assert y.count(old) == 1, old
    y = y.replace(old, new)
r.write_text(y, encoding="utf-8")

d = M / "DECISION_POLICY_REPORT.md"
z = d.read_text(encoding="utf-8")
for old, new in (("ciclo 3 na 0.4.13rc12, com o `policy.py` byte a byte igual nas duas",
                  "ciclo 3 na 0.4.13rc12 e, pela C14, na 0.4.13rc13, com o `policy.py` byte a byte igual nas três"),
                 ("ciclo 3 (cain 0.4.13rc12, run", "ciclo 3 na cain 0.4.13rc13 com o transporte 0.1.0rc6 (run")):
    assert z.count(old) == 1, old
    z = z.replace(old, new)
d.write_text(z, encoding="utf-8")

e = M / "ENVELOPE_V2_CONFORMANCE_REPORT.md"
v = e.read_text(encoding="utf-8")
for old, new in (("  - `cain` 0.4.13rc12 (ciclo 3:", "  - `cain` 0.4.13rc13 (C14 da rc13; ciclo 3 desde a 0.4.13rc12:"),
                 ("  - `predictor-research-transport` 0.1.0rc5 (ciclo 2: entradas `stocks` e `brasileirao` na allowlist;",
                  "  - `predictor-research-transport` 0.1.0rc6 (trava exclusiva por domínio no consumidor, CONSUMER_BUSY; antes 0.1.0rc5 com as entradas `stocks` e `brasileirao` na allowlist;")):
    assert v.count(old) == 1, old
    v = v.replace(old, new)
e.write_text(v, encoding="utf-8")

# achados IC-F016 e IC-F017 corrigidos pelo transporte 0.1.0rc6
f = M / "FINDINGS.json"
doc = json.loads(f.read_text(encoding="utf-8"))


def ref(rel):
    return {"file": f"qualification/integration-crypto/{rel}", "sha256": hashlib.sha256((M / rel).read_bytes()).hexdigest()}


base = "RAW_LOGS/transport-rc6-disputa"
for item in doc["findings"]:
    if item["id"] in ("IC-F016", "IC-F017") and item["status"] != "FIXED":
        item["status"] = "FIXED"
        item["fix"] = ("predictor-research-transport 0.1.0rc6 (ecosystem-predictor#36, merge bac1f7b; publicada pela sessão "
                       "STOCKS, wheel 6c7e83c4…), decisão do dono na sessão STOCKS (\"Só o transporte\"): o consumidor "
                       "toma uma trava exclusiva por domínio (<spool>/<domínio>/.consumer.lock; msvcrt no Windows) antes "
                       "de ler o ledger ou chamar o domínio; o segundo sai com exit 6 CONSUMER_BUSY, sem publicar. Sem "
                       "mudança em código de domínio. Conferido pela sessão cripto com o código publicado: disputa 20/20 "
                       "no WSL e 20/20 no Windows (1 RESULT, 0 envelope falso, 0 queda); morte do dono da trava com "
                       "retomada 6/6 nos pontos before_domain e after_domain_before_result_write")
        item["evidence_refs"] = [f"qualification/integration-crypto/{base}/{p}" for p in
                                 ("linux/SUMMARY.json", "windows/SUMMARY.json", "morte-windows/SUMMARY.json")]
        item["fix_evidence"] = [ref(f"{base}/linux/SUMMARY.json"), ref(f"{base}/windows/SUMMARY.json"),
                                ref(f"{base}/morte-windows/SUMMARY.json")]
f.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print("ok")
