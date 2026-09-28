"""integration-stocks: autoteste de protected_check.chain() (cadeia sem limite fixo de saltos, 2026-09-28).

Monta cadeias sintéticas de congelados (cycle.supersedes) e de attestations (supersedes_sha256 +
QUALIFICATION_ATTESTATION_superseded_<sha12>.json) num diretório temporário e confere:
  * 7 saltos até o sha256 protegido: ok (até o ciclo 4, com o limite de 5, falhava);
  * attestation com 6 saltos: ok;
  * ponteiro para um arquivo com bytes diferentes: FAIL (bytes_differ);
  * ponteiro para um arquivo que não existe: FAIL (missing);
  * ciclo (A → B → A): FAIL (cycle), sem laço;
  * documento sem ponteiro antes do sha256 protegido: FAIL (no_pointer).
Uso: python protected_chain_selftest.py
"""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from protected_check import chain  # noqa: E402


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def write(path: Path, doc: dict) -> str:
    raw = (json.dumps(doc, indent=1) + "\n").encode()
    path.write_bytes(raw)
    return sha(raw)


def frozen_chain(d: Path, hops: int) -> tuple[Path, str]:
    """cycle1 (protegido) ← cycle2 ← … ← FROZEN_PARAMETERS.json (atual), com `hops` saltos."""
    protected = write(d / "FROZEN_PARAMETERS_cycle1_x.json", {"cycle": {"number": 1}})
    previous_name, previous_sha = "FROZEN_PARAMETERS_cycle1_x.json", protected
    for n in range(2, hops + 1):
        name = f"FROZEN_PARAMETERS_cycle{n}_x.json"
        previous_sha = write(d / name, {"cycle": {"number": n, "supersedes": {"file": previous_name,
                                                                                  "sha256": previous_sha}}})
        previous_name = name
    write(d / "FROZEN_PARAMETERS.json", {"cycle": {"number": hops + 1,
                                                   "supersedes": {"file": previous_name, "sha256": previous_sha}}})
    return d / "FROZEN_PARAMETERS.json", protected


def attestation_chain(d: Path, hops: int) -> tuple[Path, str]:
    protected_raw = b'{"n": 0}\n'
    protected = sha(protected_raw)
    (d / f"QUALIFICATION_ATTESTATION_superseded_{protected[:12]}.json").write_bytes(protected_raw)
    previous = protected
    for n in range(1, hops):
        raw = (json.dumps({"n": n, "supersedes_sha256": previous}) + "\n").encode()
        (d / f"QUALIFICATION_ATTESTATION_superseded_{sha(raw)[:12]}.json").write_bytes(raw)
        previous = sha(raw)
    (d / "QUALIFICATION_ATTESTATION.json").write_bytes((json.dumps({"n": hops, "supersedes_sha256": previous}) + "\n")
                                                        .encode())
    return d / "QUALIFICATION_ATTESTATION.json", protected


def main() -> int:
    results = {}
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "a").mkdir()
        current, protected = frozen_chain(root / "a", 7)
        out = chain(current, protected)
        results["frozen_7_hops"] = (out["ok"], out["stop"], len(out["hops"])) == (True, "protected_sha256", 7)

        (root / "b").mkdir()
        current, protected = attestation_chain(root / "b", 6)
        out = chain(current, protected)
        results["attestation_6_hops"] = (out["ok"], out["stop"], len(out["hops"])) == (True, "protected_sha256", 6)

        (root / "c").mkdir()
        current, protected = frozen_chain(root / "c", 4)
        (root / "c" / "FROZEN_PARAMETERS_cycle3_x.json").write_bytes(b'{"tampered": true}\n')
        out = chain(current, protected)
        results["bytes_differ_fails"] = (out["ok"], out["stop"]) == (False, "bytes_differ")

        (root / "d").mkdir()
        current, protected = frozen_chain(root / "d", 4)
        (root / "d" / "FROZEN_PARAMETERS_cycle2_x.json").unlink()
        out = chain(current, protected)
        results["missing_fails"] = (out["ok"], out["stop"]) == (False, "missing")

        (root / "e").mkdir()
        # A aponta para B com o sha256 certo de B; B aponta de volta para A (com ponteiros por sha256 um ciclo em que
        # todos os hashes batem não existe, então o ciclo real é este): para no segundo salto, sem laço
        b_sha = write(root / "e" / "B.json", {"cycle": {"number": 1, "supersedes": {"file": "A.json",
                                                                                        "sha256": "0" * 64}}})
        write(root / "e" / "A.json", {"cycle": {"number": 2, "supersedes": {"file": "B.json", "sha256": b_sha}}})
        out = chain(root / "e" / "A.json", "f" * 64)
        results["cycle_fails"] = (out["ok"], out["stop"], len(out["hops"])) == (False, "cycle", 1)

        (root / "g").mkdir()
        write(root / "g" / "FROZEN_PARAMETERS.json", {"cycle": {"number": 1}})
        out = chain(root / "g" / "FROZEN_PARAMETERS.json", "f" * 64)
        results["no_pointer_fails"] = (out["ok"], out["stop"], out["hops"]) == (False, "no_pointer", [])
    print(json.dumps({"results": results, "passed": sum(results.values()), "failed": sum(not v for v in results.values())}))
    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
