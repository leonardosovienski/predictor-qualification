"""Rodada 3, linter: o relatório honesto passa quando o nome vai entre crases e o 95% é citado da fonte (0.95)?

Mesmo método de claims_check.py (documento = `stocks-research show` de um backtest real; evidências = trechos
literais), com os relatórios:
  A honesto (nome `momentum 12-1` entre crases; 29, 50, −37, 94 e 95% citados) → publishable;
  A0 o mesmo texto sem crases → blocked (fora das crases, "12" e "1" pedem fonte);
  B número inventado sem citação → blocked;  C número errado com citação → blocked;
  E número "escondido" entre crases (`29`) sem citação → blocked.
Uso: claims_check3.py <show.json> <claims.sqlite> <out>
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from claims_check import cain  # noqa: E402


def main() -> int:
    show, db, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    out.mkdir(parents=True, exist_ok=True)
    text = show.read_text(encoding="utf-8")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    doc = cain("memory", "--db", db, "add-document", "--cube", "stocks", "--title", "stocks-research show (backtest real)",
               "--published-at", now, "--source", f"stocks-research show {json.loads(text)['request_id']}", "--file", show)
    doc_id = doc.get("id") or doc.get("document_id")
    ev = {}
    for name, quote in (("net", '"excess_net_bps": 29'), ("periods", '"periods": 50'),
                        ("ci", '"excess_net_ci_bps": [-37, 94]'), ("conf", '"confidence": 0.95')):
        start = text.find(quote)
        got = cain("claims", "--db", db, "add-evidence", "--cube", "stocks", "--document-id", doc_id,
                   "--start", start, "--end", start + len(quote), "--quote", quote) if start >= 0 else {}
        ev[name] = got.get("id") or got.get("evidence_id")
    honest = (f"O backtest de `momentum 12-1` no painel real teve excesso líquido de 29 bps por período [ev:{ev['net']}], "
              f"em 50 períodos [ev:{ev['periods']}]. O intervalo de 95% [ev:{ev['conf']}] foi de -37 a 94 bps "
              f"[ev:{ev['ci']}], então o resultado é inconclusivo.\n")
    reports = {
        "A_honesto_com_crases": (honest, "publishable"),
        "A0_mesmo_texto_sem_crases": (honest.replace("`momentum 12-1`", "momentum 12-1"), "blocked"),
        "B_numero_inventado": (f"O backtest teve excesso líquido de 29 bps por período [ev:{ev['net']}]. "
                               "O índice de Sharpe anual foi 1,8.\n", "blocked"),
        "C_numero_errado_com_citacao": (f"O backtest teve excesso líquido de 92 bps por período [ev:{ev['net']}].\n",
                                        "blocked"),
        "E_numero_escondido_em_crases": ("O backtest teve excesso líquido de `29` bps por período.\n", "blocked"),
    }
    results = {}
    for name, (body, expected) in reports.items():
        path = out / f"report_{name}.md"
        path.write_text(body, encoding="utf-8")
        got = cain("claims", "--db", db, "lint", "--as-of", "now", "--cube", "stocks", path)
        results[name] = {"expected": expected, "status": got.get("status"), "ok": got.get("status") == expected,
                         "violations": got.get("violations"), "exit": got["exit"]}
    summary = {"document": doc, "evidence": ev, "reports": results,
               "passed": sum(r["ok"] for r in results.values()), "failed": sum(not r["ok"] for r in results.values())}
    (out / "CLAIMS_CHECK.json").write_text(json.dumps(summary, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    for name, r in results.items():
        print(("OK  " if r["ok"] else "MISS"), name, "->", r["status"], json.dumps(r["violations"], ensure_ascii=False)[:200])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
