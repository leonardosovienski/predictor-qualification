"""Rodada de utilidade, fase 5: o CAIN reconhece uma ideia "nova" que já é uma hipótese encerrada do Stocks?

Casos (o esperado vem do research/scientific_state.json do Stocks lido pelo CAIN, não de mim):
  * paráfrases de hipóteses encerradas SEM identidade (é como uma ideia nova chega): momentum 12-1 (H1), máxima de
    52 semanas (H14), baixa volatilidade (H2);
  * as mesmas COM identidade (família congelada / trial id), como a política de equivalência pede;
  * ideias de fato fora do estado científico (não devem casar).
Grava FINDINGS_CHECKS.json. Uso: findings_checks.py <findings.sqlite> <out>
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

CASES = [
    ("H1 paráfrase sem identidade", "closed",
     "Comprar as ações da B3 com maior retorno acumulado em 12 meses, excluindo o último mês, e rebalancear "
     "mensalmente", {}),
    ("H1 com família congelada", "closed",
     "Comprar as ações da B3 com maior retorno acumulado em 12 meses, excluindo o último mês, e rebalancear "
     "mensalmente", {"--hypothesis-family": "momentum_12_1"}),
    ("H1 nome técnico sem identidade", "closed", "momentum 12-1 cross-sectional long-only B3", {}),
    ("H14 paráfrase sem identidade", "closed",
     "Ações negociando perto da máxima de 52 semanas continuam subindo nos meses seguintes", {}),
    ("H14 com trial id", "closed",
     "Ações negociando perto da máxima de 52 semanas continuam subindo nos meses seguintes",
     {"--trial-id": "h14-near-52w-high"}),
    ("H2 paráfrase sem identidade", "closed",
     "Carteira das ações de menor volatilidade dos últimos 252 pregões supera o índice", {}),
    ("H2 com família congelada", "closed",
     "Carteira das ações de menor volatilidade dos últimos 252 pregões supera o índice",
     {"--hypothesis-family": "low_vol_252"}),
    ("nova: recompra de ações", "new",
     "Retorno das ações nos 5 pregões seguintes a um anúncio de programa de recompra registrado na CVM", {}),
    ("nova: aluguel de ações", "new",
     "Aumento da taxa de aluguel de ações na B3 antecede retorno negativo no mês seguinte", {}),
]


def main() -> int:
    db, out = Path(sys.argv[1]), Path(sys.argv[2])
    cain = os.environ["CAIN_BIN"]
    listed = subprocess.run([cain, "findings", "--db", db, "list", "--domain", "stocks", "--as-of", "now",
                             "--include-quarantine", "--kind", "negative"], capture_output=True, text=True)
    findings = json.loads(listed.stdout) if listed.stdout.strip() else {}
    rows = findings.get("findings", findings if isinstance(findings, list) else [])
    sample = [{"finding_id": f.get("finding_id"), "statement": str(f.get("statement"))[:200],
               "identity": f.get("identity")} for f in rows[:6]]
    results = []
    for name, expected, statement, identity in CASES:
        argv = [cain, "findings", "--db", db, "check", "--domain", "stocks", "--statement", statement, "--as-of", "now"]
        for k, v in identity.items():
            argv += [k, v]
        done = subprocess.run([str(a) for a in argv], capture_output=True, text=True)
        doc = json.loads(done.stdout) if done.stdout.strip() else {}
        matches = doc.get("matches", doc if isinstance(doc, list) else [])
        got = "closed" if matches else "new"
        results.append({"case": name, "expected": expected, "got": got, "ok": got == expected, "exit": done.returncode,
                        "top": [{k: m.get(k) for k in ("finding_id", "same_identity", "similarity", "statement")}
                                for m in matches[:2]], "stderr": done.stderr[-300:]})
    doc = {"findings_negative": len(rows), "statement_sample": sample, "cases": results,
           "passed": sum(r["ok"] for r in results), "failed": sum(not r["ok"] for r in results)}
    out.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"negative_findings": len(rows), "passed": doc["passed"], "failed": doc["failed"]}))
    for r in results:
        print(("OK  " if r["ok"] else "MISS"), r["case"], "->", r["got"], r["top"][:1])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
