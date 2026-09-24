"""brasileirao: resumo SEM DADO do REAL_CORROBORATION.json de real_corroboration.py.

O arquivo completo cita, na variante de mesmo kickoff, o kickoff e os event_id de jogos reais (registros do dado
privado, D-11/D-16): ele fica só no PC 2. Na evidência entram as checagens, o total de previsões, o tipo (e a seed)
de cada variante e o sha256 do arquivo privado.

Uso: python corroboration_summary.py --private <REAL_CORROBORATION.json> --out <json>
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--private", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    raw = args.private.read_bytes()
    doc = json.loads(raw)
    summary = {
        "schema": "brasileirao/REAL_CORROBORATION_SUMMARY/1",
        "private_file_sha256": hashlib.sha256(raw).hexdigest(),
        "variants": {name: {k: v for k, v in variant.items() if k in ("kind", "seed")} for name, variant in doc["variants"].items()},
        "checks": doc["checks"],
        "all_ok": doc["all_ok"],
        "n_predictions": doc["n_predictions"],
    }
    args.out.write_text(json.dumps(summary, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: summary[k] for k in ("all_ok", "n_predictions")} | {"checks": summary["checks"]}))
    return 0 if summary["all_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
