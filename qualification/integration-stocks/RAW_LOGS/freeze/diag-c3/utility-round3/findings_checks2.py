"""Rodada 2, "a ideia é nova?": o CAIN reconhece uma hipótese encerrada do Stocks?

Os casos da rodada 1 (findings_checks.py) e mais:
  * identidade pelo ID da hipótese, com e sem o domínio (`stocks:H1` e `H1`; o com domínio foi corrigido no cain#73);
  * as paráfrases sem identidade com `--rank-embedding` (qwen3-embedding:0.6b local): o embedding só ordena o que a
    regra léxica já achou, nunca decide; o caso mostra isso na prática.
Grava FINDINGS_CHECKS.json. Uso: findings_checks2.py <findings.sqlite> <out> <cain.toml do embedding>
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from findings_checks import CASES  # noqa: E402

EXTRA = [
    ("H1 com hypothesis-id qualificado (stocks:H1)", "closed",
     "Comprar as ações da B3 com maior retorno acumulado em 12 meses, excluindo o último mês, e rebalancear "
     "mensalmente", {"--hypothesis-id": "stocks:H1"}),
    ("H1 com hypothesis-id local (H1)", "closed",
     "Comprar as ações da B3 com maior retorno acumulado em 12 meses, excluindo o último mês, e rebalancear "
     "mensalmente", {"--hypothesis-id": "H1"}),
    ("H9 de outro domínio (crypto:H9) no stocks", "new",
     "Qualidade de alavancagem prevê retorno", {"--hypothesis-id": "crypto:H9"}),
]


def main() -> int:
    db, out, cfg = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    cain = os.environ["CAIN_BIN"]
    listed = subprocess.run([cain, "findings", "--db", db, "list", "--domain", "stocks", "--as-of", "now",
                             "--include-quarantine", "--kind", "negative"], capture_output=True, text=True)
    findings = json.loads(listed.stdout) if listed.stdout.strip() else {}
    rows = findings.get("findings", [])
    cases = [(n, e, s, i, False) for n, e, s, i in CASES + EXTRA]
    cases += [(n + " + rank-embedding", e, s, i, True) for n, e, s, i in CASES if "sem identidade" in n]
    results = []
    for name, expected, statement, identity, embed in cases:
        argv = [cain, "findings", "--db", db, "check", "--domain", "stocks", "--statement", statement, "--as-of", "now"]
        for k, v in identity.items():
            argv += [k, v]
        if embed:
            argv += ["--rank-embedding", "--config", cfg]
        done = subprocess.run([str(a) for a in argv], capture_output=True, text=True)
        doc = json.loads(done.stdout) if done.stdout.strip() else {}
        matches = doc.get("matches", [])
        got = "closed" if matches else "new"
        results.append({"case": name, "expected": expected, "got": got, "ok": got == expected, "exit": done.returncode,
                        "top": [{k: m.get(k) for k in ("finding_id", "same_identity", "similarity", "rank", "statement")}
                                for m in matches[:2]], "stderr": done.stderr[-300:]})
    doc = {"findings_negative": len(rows),
           "statement_sample": [{"statement": str(f.get("statement"))[:160], "identity": f.get("identity")}
                                for f in rows[:6]],
           "cases": results, "passed": sum(r["ok"] for r in results), "failed": sum(not r["ok"] for r in results)}
    out.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"negative_findings": len(rows), "passed": doc["passed"], "failed": doc["failed"]}))
    for r in results:
        print(("OK  " if r["ok"] else "MISS"), r["case"], "->", r["got"], "exit", r["exit"], r["stderr"][-120:] if r["exit"] else "")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
