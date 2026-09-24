"""brasileirao / BR-F018: auditoria estrita (sem tolerância) dos 20 resultados reais em dois ambientes.

Complementa `compare_real_tolerance.py` (critério declarado, com tolerâncias). Compara o resultado `show` INTEIRO
(não só o conteúdo de domínio), campo a campo e sem tolerância, e procura números não finitos (NaN/inf) — o
comparador com tolerância trataria um NaN de um lado contra um número do outro como igual; esta auditoria mostra que
não há nenhum. A saída tem só nomes de campo e contagens (nenhum valor): os resultados carregam o dado privado e
ficam só no PC 2.

Uso: python strict_audit.py <dir a com result_*.json> <dir b com result_*.json>
"""

import json
import math
import re
import sys
from pathlib import Path


def load(d: Path, n: str) -> dict:
    return json.loads((d / n).read_text(encoding="utf-8"), parse_constant=lambda c: float(c))["result"]


def nonfinite(x, path: str, acc: set) -> None:
    if isinstance(x, dict):
        for k, v in x.items():
            nonfinite(v, f"{path}/{k}", acc)
    elif isinstance(x, list):
        for v in x:
            nonfinite(v, path + "[]", acc)
    elif isinstance(x, float) and not math.isfinite(x):
        acc.add(path)


def diff_paths(a, b, path: str, acc: set) -> None:
    if isinstance(a, dict) and isinstance(b, dict):
        for k in set(a) | set(b):
            if k not in a or k not in b:
                acc.add(f"{path}/{k} (chave só num lado)")
            else:
                diff_paths(a[k], b[k], f"{path}/{k}", acc)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            acc.add(path + " (tamanho)")
        else:
            for x, y in zip(a, b):
                diff_paths(x, y, path + "[]", acc)
    elif isinstance(a, float) or isinstance(b, float):
        if isinstance(a, bool) or isinstance(b, bool) or not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
            if a != b:
                acc.add(path + " (tipo)")
        elif (math.isnan(a) != math.isnan(b)) or (not math.isnan(a) and a != b):
            acc.add(path)
    elif a != b:
        acc.add(path)


def main() -> int:
    a, b = Path(sys.argv[1]), Path(sys.argv[2])
    names = sorted(p.name for p in a.glob("result_*.json"))
    top, dom, nf, diffs = set(), set(), set(), set()
    for n in names:
        ra, rb = load(a, n), load(b, n)
        top |= set(ra) | set(rb)
        dom |= set(ra.get("domain_facts", {})) | set(rb.get("domain_facts", {}))
        nonfinite(ra, "", nf)
        nonfinite(rb, "", nf)
        diff_paths(ra, rb, "", diffs)
    print("pedidos:", len(names), "| em b:", len(list(b.glob("result_*.json"))))
    print("chaves de result:", sorted(top))
    print("chaves de domain_facts:", sorted(dom))
    print("campos não finitos (NaN/inf):", sorted(nf) or "nenhum")
    fields = sorted({re.sub(r"\[\]", "[]", p) for p in diffs})
    print("campos com QUALQUER diferença (comparação exata, sem tolerância):", len(fields))
    for p in fields:
        print("  ", p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
