"""Declaração de MODE nos documentos de estado deste repositório (auditoria de fechamento, 2026-10-08).

Documento vivo declara exatamente um ``MODE: CURRENT_LIVING_STATE``; snapshot declara ``MODE: SNAPSHOT_IMMUTABLE`` com
AS_OF_DATE e SUPERSEDED_BY. Só confere a declaração, não o conteúdo. Uso: ``python check_modes.py`` na raiz do repo.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LIVING = ["README.md"]
SNAPSHOTS = ["qualification/shared/CICLO_D27_20260930.md", "qualification/shared/SUPPLY_CHAIN_20261007.md"]


def declarations(text: str) -> list[str]:
    return re.findall(r"^>? ?MODE: (SNAPSHOT_IMMUTABLE|CURRENT_LIVING_STATE)", text, flags=re.M)


def main() -> int:
    problems: list[str] = []
    for rel in LIVING:
        if declarations((ROOT / rel).read_text(encoding="utf-8")) != ["CURRENT_LIVING_STATE"]:
            problems.append(f"{rel}: deve declarar exatamente um MODE: CURRENT_LIVING_STATE")
    for rel in SNAPSHOTS:
        text = (ROOT / rel).read_text(encoding="utf-8")
        if declarations(text) != ["SNAPSHOT_IMMUTABLE"]:
            problems.append(f"{rel}: deve declarar exatamente um MODE: SNAPSHOT_IMMUTABLE")
        if not re.search(r"AS_OF_DATE: \d{4}-\d{2}-\d{2}", text) or not re.search(r"SUPERSEDED_BY: \S+", text):
            problems.append(f"{rel}: snapshot sem AS_OF_DATE ou SUPERSEDED_BY")
    for p in problems:
        print("  " + p)
    print("DOCUMENT_MODES = " + ("FAIL" if problems else "PASS"))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
