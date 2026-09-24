"""brasileirao / BR-F018: os 20 pedidos reais dão o mesmo resultado em dois ambientes, pelas tolerâncias declaradas?

Critério `cross_os_real_data` de qualification/brasileirao/BR_F018_FIX_PLAN.json (declarado antes de medir,
commit 497715f): em cada pedido, comparando o conteúdo de domínio do resultado `show`:
  * números de ponto flutuante sob "params" (parâmetros do refit por previsão): |Δ| <= 1e-6;
  * todo outro número de ponto flutuante (probabilidades, lambdas, Elo, climatologia, scores, Δ, IC, ROI,
    líquido, hit_rate, frações de qualidade): |Δ| <= 1e-9;
  * inteiros, textos, booleanos, nulos e estrutura (estados, n, n_bets, status, information_fingerprint,
    kickoff, cutoff, refit_at, data_quality...): exatamente iguais.
Não entram (mudam a cada execução por construção): ids do resultado, `effect_sha256`, `identity` e `references`
(hashes de manifesto com o instante de captura). Um pedido passa se não houver nenhuma violação; o critério
da missão é 20/20.

A saída tem só nomes de pedido, contagens, máximos e caminhos de campo (sem valores por jogo): os resultados
comparados carregam o dado privado e ficam só no PC 2.

Uso: python compare_real_tolerance.py --a <dir result_*.json> --a-label L --b <dir> --b-label L --out <json>
Exit 1 se algum pedido violar.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

PARAM_ATOL = 1e-6
FLOAT_ATOL = 1e-9
DOMAIN_KEYS = ("data_cutoff", "data_quality", "dataset_as_of", "economics", "evaluation", "handler", "predictions", "target")
STATE_KEYS = ("result_state", "scientific_state", "economic_state", "operational_state", "capital_permission")


def _generic(path: str) -> str:
    return re.sub(r"\[\d+\]", "[]", path)


def walk(a, b, path: str, in_params: bool, acc: dict) -> None:
    if isinstance(a, dict) and isinstance(b, dict):
        if set(a) != set(b):
            acc["violations"].append({"field": _generic(path), "why": "chaves diferentes"})
            return
        for key in sorted(a):
            walk(a[key], b[key], f"{path}/{key}", in_params or key == "params", acc)
        return
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            acc["violations"].append({"field": _generic(path), "why": f"tamanhos {len(a)} x {len(b)}"})
            return
        for index, (x, y) in enumerate(zip(a, b, strict=True)):
            walk(x, y, f"{path}[{index}]", in_params, acc)
        return
    if (isinstance(a, float) or isinstance(b, float)) and not isinstance(a, bool) and not isinstance(b, bool) \
            and isinstance(a, (int, float)) and isinstance(b, (int, float)):
        kind = "params" if in_params else "float"
        gap = abs(float(a) - float(b))
        stat = acc[kind]
        stat["compared"] += 1
        stat["differing"] += gap > 0.0
        stat["max_abs_diff"] = max(stat["max_abs_diff"], gap)
        if gap > (PARAM_ATOL if in_params else FLOAT_ATOL):
            acc["violations"].append({"field": _generic(path), "why": f"|Δ| = {gap:.3e}"})
        return
    acc["exact"]["compared"] += 1
    if a != b:
        acc["exact"]["differing"] += 1
        acc["violations"].append({"field": _generic(path), "why": "valor discreto diferente"})


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", type=Path, required=True)
    ap.add_argument("--a-label", required=True)
    ap.add_argument("--b", type=Path, required=True)
    ap.add_argument("--b-label", required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    names = sorted(p.name for p in args.a.glob("result_*.json"))
    rows = []
    for name in names:
        path_b = args.b / name
        if not path_b.is_file():
            rows.append({"request": name, "pass": False, "why": f"ausente em {args.b_label}"})
            continue
        ra = json.loads((args.a / name).read_text(encoding="utf-8"))["result"]
        rb = json.loads(path_b.read_text(encoding="utf-8"))["result"]
        acc = {"params": {"compared": 0, "differing": 0, "max_abs_diff": 0.0},
               "float": {"compared": 0, "differing": 0, "max_abs_diff": 0.0},
               "exact": {"compared": 0, "differing": 0}, "violations": []}
        walk({k: ra.get(k) for k in STATE_KEYS}, {k: rb.get(k) for k in STATE_KEYS}, "", False, acc)
        walk({k: ra["domain_facts"].get(k) for k in DOMAIN_KEYS}, {k: rb["domain_facts"].get(k) for k in DOMAIN_KEYS},
             "/domain_facts", False, acc)
        fields = sorted({v["field"] for v in acc["violations"]})
        rows.append({"request": name.removeprefix("result_").removesuffix(".json"), "pass": not acc["violations"],
                     "violations": len(acc["violations"]), "violating_fields": fields[:15],
                     "params": acc["params"], "float": acc["float"], "exact": acc["exact"]})
    extra = sorted({p.name for p in args.b.glob("result_*.json")} - set(names))
    passed = sum(1 for r in rows if r["pass"])
    summary = {
        "schema": "brasileirao/COMPARE_REAL_TOLERANCE/1",
        "criterion": "BR_F018_FIX_PLAN.json cross_os_real_data (params |Δ|<=1e-6; demais floats |Δ|<=1e-9; discretos iguais)",
        "a": args.a_label, "b": args.b_label,
        "requests": len(rows), "passed": passed, "only_in_b": extra,
        "max_abs_diff": {"params": max((r["params"]["max_abs_diff"] for r in rows if "params" in r), default=0.0),
                         "float": max((r["float"]["max_abs_diff"] for r in rows if "float" in r), default=0.0)},
        "all_pass": passed == len(rows) and not extra and len(rows) > 0,
        "rows": rows,
    }
    args.out.write_text(json.dumps(summary, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: summary[k] for k in ("a", "b", "requests", "passed", "max_abs_diff", "all_pass")}, ensure_ascii=False))
    return 0 if summary["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
