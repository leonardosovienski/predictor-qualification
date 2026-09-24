"""stocks: FROZEN_VECTORS.json = identidade dos vetores que os gates usaram (C15 "vetores gerados têm hash próprio").

Não gera nem muda vetor: registra (1) blob git e sha256 de cada arquivo da suíte de conformidade do
stocks-predictor no final_commit (os vetores sintéticos congelados: painéis positive/case_a/case_b/insufficient/
future_canary, PIT-01..15, matriz de falhas), e se o blob é o mesmo no final_commit da rc1 (9a6c09a) — a C14 da
rc2 não mexeu nos vetores; (2) o sha256 do FROZEN_PARAMETERS.json, onde estão os vetores adversariais, a matriz
de falhas e as seeds dos controles; (3) os vetores reais da D-16: SOURCES.json, PROTOCOL_REAL.json e o sha256
do painel fixado.

Uso: python frozen_vectors.py --repo <clone do stocks-predictor> --commit <final_commit> --out FROZEN_VECTORS.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

QC = Path(__file__).resolve().parents[1]
RC1_FINAL = "9a6c09ae92991c8490be624f5693865bcbaeca26"


def git(repo: str, *args: str) -> bytes:
    return subprocess.run(["git", "-C", repo, *args], capture_output=True, check=True).stdout


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--commit", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    rc1 = {}
    for line in git(args.repo, "ls-tree", "-r", RC1_FINAL, "tests/conformance").decode().splitlines():
        meta, path = line.split("\t", 1)
        rc1[path] = meta.split()[2]
    items = []
    for line in git(args.repo, "ls-tree", "-r", args.commit, "tests/conformance").decode().splitlines():
        meta, path = line.split("\t", 1)
        if not path.endswith(".py"):
            continue
        raw = git(args.repo, "show", f"{args.commit}:{path}")
        blob = meta.split()[2]
        items.append({"path": path, "git_blob": blob, "sha256": hashlib.sha256(raw).hexdigest(),
                      "same_blob_in_rc1_final_commit": rc1.get(path) == blob})
    sources = json.loads((QC / "d16" / "SOURCES.json").read_text(encoding="utf-8"))
    doc = {
        "schema": "stocks/FROZEN_VECTORS/1",
        "repo": "stocks-predictor",
        "commit": args.commit,
        "identity": "hash do blob git no final_commit (e sha256 dos bytes)",
        "suite": "tests/conformance (fixtures.py: painéis positive, case_a, case_b, insufficient, future_canary; "
                 "canário FUTURE_CANARY_STOCKS_001; PIT-01..15; matriz de falhas F-*)",
        "frozen_parameters": {"file": "qualification/stocks/FROZEN_PARAMETERS.json",
                              "sha256": sha_file(QC / "FROZEN_PARAMETERS.json"),
                              "keys": ["pit_adversarial_vectors", "failure_injection_points", "universe_identity_checks",
                                       "future_canary", "negative_controls", "authority_cases", "idempotency"]},
        "real_data_vectors_d16": {
            "builder": "qualification/stocks/d16/build_real_panel.py",
            "sources": {"file": "qualification/stocks/d16/SOURCES.json", "sha256": sha_file(QC / "d16" / "SOURCES.json")},
            "protocol": {"file": "qualification/stocks/d16/PROTOCOL_REAL.json",
                         "sha256": sha_file(QC / "d16" / "PROTOCOL_REAL.json")},
            "panel_sha256": sources["expected"]["panel_sha256"],
            "data_cutoff": sources["expected"]["data_cutoff"],
            "negative_control_seeds": [101, 202, 303, 404, 505, 606, 707, 808, 909, 1010,
                                       1111, 1212, 1313, 1414, 1515, 1616, 1717, 1818, 1919, 2020],
        },
        "files": items,
    }
    with open(args.out, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(doc, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print(args.out, len(items), all(i["same_blob_in_rc1_final_commit"] for i in items))


if __name__ == "__main__":
    main()
