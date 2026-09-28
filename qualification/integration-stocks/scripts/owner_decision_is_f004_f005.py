"""Registra no FINDINGS.json a decisão do dono sobre IS-F004 e IS-F005 (opção b) e as correções de fato.

Palavras do dono no chat da sessão (2026-09-28): "aceita o run workflow_dispatch (b) e reemite".
  * IS-F004 e IS-F005 passam a ACCEPTED_LIMITATION, com a decisão e o que ela cobre.
  * IS-F005, correção: o commit acusado pelo gitleaks é 9f7cce3, da branch evidence/prompt1-segredos-20260924, não o
    28f17d2 do main (PR #99). O conteúdo é o mesmo e continua fora da branch da missão. O registro anterior também
    omitia que, com o passo do gitleaks vermelho, os passos seguintes do job secrets não rodaram (varredura da árvore
    do commit com o .gitleaks.toml e controle do token sintético).
  * IS-F001, atualização: depois do merge do stocks-predictor#107 pelo dono, o main declara 0.3.0rc3 com código
    diferente da wheel rc3 (6f857b2); a mesma situação do achado, agora na rc3.
Os demais achados não mudam.
Uso: python owner_decision_is_f004_f005.py <raiz do predictor-qualification>
"""
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
path = root / "qualification/integration-stocks/FINDINGS.json"
doc = json.loads(path.read_text(encoding="utf-8"))
f = {x["id"]: x for x in doc["findings"]}
assert f["IS-F004"]["status"] == "OPEN_AWAITING_OWNER" and f["IS-F005"]["status"] == "OPEN_AWAITING_OWNER"

decision = {"date": "2026-09-28", "by": "dono", "channel": "chat da sessão",
            "words": "aceita o run workflow_dispatch (b) e reemite"}
f["IS-F004"]["status"] = "ACCEPTED_LIMITATION"
f["IS-F004"]["owner_decision_taken"] = {
    **decision,
    "applied": "só para o stocks-predictor, o run workflow_dispatch do CI Pipeline no SHA exato do final_commit "
               "(36363108348, 6f857b2) vale como o run de C21 / prompt 9.3 e de C24.3 (f); na base, o run "
               "workflow_dispatch da Etapa A (35953418753, 61fc017), como na Etapa A",
    "evidence": "qualification/integration-stocks/RAW_LOGS/hosted-ci/final-r1/stocks_dispatch_acceptance.json"}
f["IS-F005"]["status"] = "ACCEPTED_LIMITATION"
f["IS-F005"]["owner_decision_taken"] = {
    **decision,
    "applied": "opção (b): aceito o run workflow_dispatch com Quality 3.13/3.14 verdes e o job secrets vermelho só "
               "pelo falso positivo pré-existente fora da branch da missão; nada mudou no stocks-predictor",
    "evidence": "qualification/integration-stocks/RAW_LOGS/hosted-ci/final-r1/stocks_dispatch_acceptance.json"}
f["IS-F005"]["correction_2026_09_28"] = (
    "O commit acusado pelo gitleaks é 9f7cce367817fe0f91bcac779b2abacd7005a8ce, da branch "
    "evidence/prompt1-segredos-20260924, não o 28f17d2 do main. A fingerprint é "
    "9f7cce36…:docs/evidence/2026-09-24-prompt1-segredos.md:generic-api-key:57. O 28f17d2 (PR #99) tem o mesmo "
    "conteúdo no main. Nenhum dos dois é ancestral de 6f857b2. O registro anterior também omitia que, com o gitleaks "
    "vermelho, os passos seguintes do job secrets ficaram pulados: a varredura da árvore completa do commit com o "
    ".gitleaks.toml do repo e o controle do token sintético. O upload final falhou por falta dos arquivos deles. "
    "Esses dois passos foram reproduzidos localmente, como diagnóstico e não como CI hospedado, com o mesmo gitleaks "
    "8.24.3 (RAW_LOGS/hosted-ci/final-r1/tree_scan_local.log).")
f["IS-F001"]["update_2026_09_28"] = (
    "O dono mergeou o stocks-predictor#107 (48088bd), resolvendo o conflito com um merge do main na branch (1dad4d8). "
    "O main agora declara 0.3.0rc3, com o código do v2 (#99–#106) e o selo R8 combinado. A wheel rc3 publicada é "
    "6f857b2. É a mesma situação do achado, agora na rc3; o runtime qualificado continua fixado pela wheel.")
path.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print("IS-F004, IS-F005 -> ACCEPTED_LIMITATION; correção IS-F005; atualização IS-F001")
