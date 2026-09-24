"""brasileirao: mesmo dado real, mesma wheel, SO diferente -> mesmo resultado? (Windows local x PC 2 Linux)

1) métricas por pedido (evidence_numbers.py `metrics`): chave A x chave B, campo a campo (menos `file`);
2) conteúdo comparável dos resultados `show` (opcional, --a-results/--b-results): previsões por jogo (com o
   information_fingerprint), avaliação, economia, qualidade de dado e estados, igualdade exata do JSON canônico;
3) captura do dataset (dataset_capture.json): sqlite_sha256 e contagem de linhas por tabela.
A saída tem só nomes de pedido, booleanos, contagens e nomes de campo divergentes; nenhum valor por jogo.

Uso: python compare_real_metrics.py --a <json> --a-key <k> --b <json> --b-key <k>
         [--a-results <dir> --b-results <dir>] [--a-capture <json> --b-capture <json>] --out <json>
Exit 1 se houver diferença.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def canonical(value) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def comparable(result: dict) -> dict:
    d = result["domain_facts"]
    return {"states": [result["result_state"], result["scientific_state"], result["economic_state"]],
            "predictions": d["predictions"], "evaluation": d["evaluation"], "economics": d["economics"],
            "data_quality": d["data_quality"], "target": d["target"], "data_cutoff": d["data_cutoff"],
            "dataset_as_of": d["dataset_as_of"]}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", type=Path, required=True)
    ap.add_argument("--a-key", required=True)
    ap.add_argument("--b", type=Path, required=True)
    ap.add_argument("--b-key", required=True)
    ap.add_argument("--a-results", type=Path)
    ap.add_argument("--b-results", type=Path)
    ap.add_argument("--a-capture", type=Path)
    ap.add_argument("--b-capture", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    rows_a = {r["request"]: r for r in json.loads(args.a.read_text(encoding="utf-8"))["metrics"][args.a_key]["requests"]}
    rows_b = {r["request"]: r for r in json.loads(args.b.read_text(encoding="utf-8"))["metrics"][args.b_key]["requests"]}
    metric_rows = []
    for name in sorted(set(rows_a) | set(rows_b)):
        a, b = rows_a.get(name), rows_b.get(name)
        if a is None or b is None:
            metric_rows.append({"request": name, "equal": False, "missing_in": "a" if a is None else "b"})
            continue
        diff = sorted(k for k in set(a) | set(b) if k != "file" and a.get(k) != b.get(k))
        metric_rows.append({"request": name, "equal": not diff, "different_fields": diff})
    doc: dict = {"schema": "brasileirao/COMPARE_REAL_METRICS/1", "a": f"{args.a.as_posix()}#{args.a_key}",
                 "b": f"{args.b.as_posix()}#{args.b_key}", "metrics": {
                     "requests": len(metric_rows), "equal": sum(r["equal"] for r in metric_rows), "rows": metric_rows}}
    ok = all(r["equal"] for r in metric_rows)
    if args.a_results and args.b_results:
        result_rows = []
        for path_a in sorted(args.a_results.glob("result_*.json")):
            path_b = args.b_results / path_a.name
            if not path_b.is_file():
                result_rows.append({"file": path_a.name, "equal": False, "missing_in": "b"})
                continue
            ca = comparable(json.loads(path_a.read_text(encoding="utf-8"))["result"])
            cb = comparable(json.loads(path_b.read_text(encoding="utf-8"))["result"])
            diff = sorted(k for k in ca if canonical(ca[k]) != canonical(cb[k]))
            result_rows.append({"file": path_a.name, "equal": not diff, "different_parts": diff,
                                "n_predictions": [len(ca["predictions"]), len(cb["predictions"])]})
        extra_b = sorted({p.name for p in args.b_results.glob("result_*.json")} - {p.name for p in args.a_results.glob("result_*.json")})
        doc["results"] = {"files": len(result_rows), "equal": sum(r["equal"] for r in result_rows),
                          "only_in_b": extra_b, "rows": result_rows}
        # agregado por previsão (mesmo event_id nos dois lados): só contagens e máximos, nenhum valor por jogo
        total = fp_equal = status_equal = states_equal = 0
        fields: dict[str, list] = {}
        for path_a in sorted(args.a_results.glob("result_*.json")):
            path_b = args.b_results / path_a.name
            if not path_b.is_file():
                continue
            ra = json.loads(path_a.read_text(encoding="utf-8"))["result"]
            rb = json.loads(path_b.read_text(encoding="utf-8"))["result"]
            states_equal += [ra["result_state"], ra["scientific_state"], ra["economic_state"]] == \
                [rb["result_state"], rb["scientific_state"], rb["economic_state"]]
            by_id = {p["event_id"]: p for p in rb["domain_facts"]["predictions"]}
            for p in ra["domain_facts"]["predictions"]:
                q = by_id.get(p["event_id"], {})
                total += 1
                fp_equal += p.get("information_fingerprint") == q.get("information_fingerprint")
                status_equal += p.get("status") == q.get("status")
                for key, value in p.items():
                    other = q.get(key)
                    if key == "information_fingerprint" or value == other:
                        continue
                    entry = fields.setdefault(key, [0, 0.0])
                    entry[0] += 1
                    if isinstance(value, (int, float)) and isinstance(other, (int, float)):
                        entry[1] = max(entry[1], abs(value - other))
                    elif isinstance(value, list) and isinstance(other, list) and len(value) == len(other):
                        entry[1] = max([entry[1]] + [abs(x - y) for x, y in zip(value, other)
                                                     if isinstance(x, (int, float)) and isinstance(y, (int, float))])
                    else:
                        entry[1] = None
        doc["predictions"] = {"compared": total, "information_fingerprint_equal": fp_equal, "status_equal": status_equal,
                              "result_states_equal": f"{states_equal}/{len(result_rows)}",
                              "differing_fields": {k: {"predictions": c, "max_abs_diff": m} for k, (c, m) in sorted(fields.items())}}
        ok = ok and all(r["equal"] for r in result_rows) and not extra_b
    if args.a_capture and args.b_capture:
        ma = json.loads(args.a_capture.read_text(encoding="utf-8"))["manifest"]
        mb = json.loads(args.b_capture.read_text(encoding="utf-8"))["manifest"]
        cap = {"sqlite_sha256_equal": ma["sqlite_sha256"] == mb["sqlite_sha256"], "tables_equal": ma["tables"] == mb["tables"],
               "as_of_equal": ma["as_of"] == mb["as_of"], "sqlite_sha256": mb["sqlite_sha256"]}
        doc["dataset_capture"] = cap
        ok = ok and cap["sqlite_sha256_equal"] and cap["tables_equal"] and cap["as_of_equal"]
    doc["identical"] = ok
    args.out.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"identical": ok, "metrics_equal": f"{doc['metrics']['equal']}/{doc['metrics']['requests']}",
                      "results_equal": f"{doc.get('results', {}).get('equal')}/{doc.get('results', {}).get('files')}",
                      "dataset_capture": doc.get("dataset_capture")}, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
