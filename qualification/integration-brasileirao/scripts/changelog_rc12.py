"""integration-brasileirao: seção do QUALIFICATION_CHANGELOG.md das fases de runtime na cain v0.4.13rc12.

Os números vêm de EVIDENCE_NUMBERS.json (C20); só a narrativa é texto.
Uso: python changelog_rc12.py <qualification/integration-brasileirao> <run>
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    q, run = Path(sys.argv[1]), sys.argv[2]
    num = json.loads((q / "EVIDENCE_NUMBERS.json").read_text(encoding="utf-8"))["numbers"]
    r = f"runtime/{run}"

    def v(key):
        return num[key]["value"]

    def c(key):
        return f"{v(key + ':checks_passed')}/{v(key + ':checks_passed') + v(key + ':checks_failed')}"

    junit = {n: v(f"{r}/cleanroom-final/{n}.junit.xml:junit")["tests"] for n in ("conformance", "transport", "cain")}
    points = v(f"{r}/failure-matrix/FAILURE_MATRIX_RESULTS.json:points")
    text = f"""
## Fases de runtime na cain v0.4.13rc12 (run `{run}`, PC 2)

A release que as três integrações usam é a **cain v0.4.13rc12** (tag → `302a5c8`, adotada por
`scripts/adopt_release.py`, 7/7). As rc10 e rc11 foram adotadas antes e trocadas pela C14: a rc11 levou o brasileirao.json
do ciclo 4 e a correção do LLM (cain#72, IB-F006); a rc12, o contexto do LLM dentro do orçamento (cain#75). O
cleanroom-final da rc11 (`run-20260928T142258Z-br11`) ficou como registro. Configurações da rc12 iguais às da rc11.

| Fase | Resultado |
|---|---|
| cleanroom-final | conformidade {junit['conformance']}, transporte {junit['transport']}, cain {junit['cain']} testes, 0 falhas |
| contract-revalidation | estática {v(f"{r}/contract-revalidation/static.json:checks")['passed']}/{v(f"{r}/contract-revalidation/static.json:checks")['passed'] + v(f"{r}/contract-revalidation/static.json:checks")['failed']} ((f) pelo IB-F005, conferido por `ib_f005_acceptance.py`); (d) {c(f"{r}/contract-revalidation")} |
| e2e | {c(f"{r}/e2e")} |
| n-plus-1 | congelado {c(f"{r}/n-plus-1/frozen")}, integrado {c(f"{r}/n-plus-1/integrated")}; holdout 2025 → REQUIRE_HUMAN SEALED_SCOPE (IB-F002 FIXED) |
| isolation-ids-contradiction | {c(f"{r}/isolation")}; contradição {c(f"{r}/isolation/contradiction")} |
| idempotency-failure | F01–F16: {sum(p['passed'] for p in points)} conferências, {sum(p['failed'] for p in points)} falhas |
| windows-smoke (PC 2) | E2E {c(f"{r}-windows/e2e")}; dado real devolvido ao WSL: {v(f"{r}-windows/logs/transfer_back.tsv:transfer_back")['files']} arquivos conferidos |
| soak | {c(f"{r}/soak")}: todos os pisos, menos o de LLM (IB-F009, waiver do dono) |

Decisões do dono neste trecho (chat da sessão, perguntas com opções):
- "Cadeia preservada (Recommended)": PROTECTED_ARTIFACTS_UNCHANGED com a regra da cadeia preservada (IB-F008).
- "Waiver do piso de LLM (Recommended)": o piso de ≥ 5 propostas de LLM dispensado só para o Brasileirão (IB-F009). O
  dono decidiu depois de saber que a alternativa (rc13 com sobreposição de campos do pedido) obrigaria o cripto e o stocks,
  já QUALIFIED na rc12, a refazer as fases.

Registro no Windows do PC 2: o console da primeira execução do `windows_smoke.ps1` foi gravado em `%TEMP%`, fora da pasta
autorizada. Só havia mensagens do script e o resumo do E2E, sem linha do dado. O arquivo foi movido para o diretório privado
do runtime no WSL (sha256 conferido) e removido do `%TEMP%`. A pasta `C:\\QUALIFICACAO\\runtime\\integration-brasileirao\\`
ficou sem nenhum banco do dado real fora de tools/venv.
"""
    log = q / "QUALIFICATION_CHANGELOG.md"
    log.write_text(log.read_text(encoding="utf-8").rstrip("\n") + "\n" + text, encoding="utf-8")
    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
