"""Marca um item de qualification/HYGIENE.json, calculando o sha256 da evidência.

Uso: python set_hygiene_status.py <HYG-0xx> <DONE|TODO> <evidence_file> <repo@commit> [...]
"""

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HYGIENE = ROOT / "qualification" / "HYGIENE.json"


def main(item_id: str, status: str, evidence: str, *commits: str) -> None:
    data = json.loads(HYGIENE.read_text(encoding="utf-8"))
    item = next(i for i in data["items"] if i["id"] == item_id)
    evidence_path = ROOT / evidence
    item["status"] = status
    item["evidence_file"] = evidence
    item["evidence_sha256"] = hashlib.sha256(evidence_path.read_bytes()).hexdigest()
    item["commits"] = list(commits)
    HYGIENE.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(item_id, status, item["evidence_sha256"])


if __name__ == "__main__":
    main(*sys.argv[1:])
