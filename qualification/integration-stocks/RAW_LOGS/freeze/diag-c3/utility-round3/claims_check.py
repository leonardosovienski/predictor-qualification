"""Rodada de utilidade, fase 6: leitura verificável — o linter do CAIN bloqueia um relatório com número sem proveniência?

Documento: a saída autoritativa do Stocks (`stocks-research show`) de um backtest real da rodada, gravada na memória
de claims do CAIN. Evidências: trechos literais dela. Relatórios:
  A honesto (números citados com [ev:…]) → publishable;
  B com um número inventado sem citação → blocked;
  C com número errado e citação presente → blocked;
  D afirmação qualitativa falsa, sem número → o linter é lexical e não julga (esperado: publishable; limite).
Uso: claims_check.py <show.json> <claims.sqlite> <out>
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def cain(*args) -> dict:
    done = subprocess.run([os.environ["CAIN_BIN"], *map(str, args)], capture_output=True, text=True)
    try:
        return {"exit": done.returncode, **json.loads(done.stdout)}
    except ValueError:
        return {"exit": done.returncode, "stdout": done.stdout[-400:], "stderr": done.stderr[-400:]}


def main() -> int:
    show, db, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    out.mkdir(parents=True, exist_ok=True)
    text = show.read_text(encoding="utf-8")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    doc = cain("memory", "--db", db, "add-document", "--cube", "stocks", "--title", "stocks-research show (backtest real)",
               "--published-at", now, "--source", f"stocks-research show {json.loads(text)['request_id']}", "--file", show)
    doc_id = doc.get("id") or doc.get("document_id")
    evidence = {}
    for name, quote in (("excess_net", '"excess_net_bps": 29'), ("periods", '"periods": 50'),
                        ("ci", '"excess_net_ci_bps": [-37, 94]')):
        start = text.find(quote)
        if start < 0:
            evidence[name] = {"error": f"quote not found: {quote}"}
            continue
        evidence[name] = cain("claims", "--db", db, "add-evidence", "--cube", "stocks", "--document-id", doc_id,
                              "--start", start, "--end", start + len(quote), "--quote", quote)
    ev = {k: (v.get("id") or v.get("evidence_id")) for k, v in evidence.items()}
    reports = {
        "A_honesto": (f"O backtest de momentum 12-1 no painel real teve excesso líquido de 29 bps por período "
                      f"[ev:{ev['excess_net']}], em 50 períodos [ev:{ev['periods']}]. O intervalo de 95% foi de -37 a "
                      f"94 bps [ev:{ev['ci']}], então o resultado é inconclusivo.\n", "publishable"),
        "B_numero_inventado": (f"O backtest teve excesso líquido de 29 bps por período [ev:{ev['excess_net']}]. "
                               "O índice de Sharpe anual foi 1,8.\n", "blocked"),
        "C_numero_errado_com_citacao": (f"O backtest teve excesso líquido de 92 bps por período [ev:{ev['excess_net']}].\n",
                                        "blocked"),
        "D_qualitativo_falso_sem_numero": ("O momentum mostrou vantagem clara e significativa sobre o universo.\n",
                                           "publishable"),
    }
    results = {}
    for name, (body, expected) in reports.items():
        path = out / f"report_{name}.md"
        path.write_text(body, encoding="utf-8")
        got = cain("claims", "--db", db, "lint", "--as-of", "now", "--cube", "stocks", path)
        results[name] = {"expected": expected, "status": got.get("status"), "ok": got.get("status") == expected,
                         "violations": got.get("violations"), "exit": got["exit"]}
    summary = {"document": doc, "evidence": evidence, "reports": results,
               "passed": sum(r["ok"] for r in results.values()), "failed": sum(not r["ok"] for r in results.values())}
    (out / "CLAIMS_CHECK.json").write_text(json.dumps(summary, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    for name, r in results.items():
        print(("OK  " if r["ok"] else "MISS"), name, "->", r["status"], json.dumps(r["violations"], ensure_ascii=False)[:250])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
