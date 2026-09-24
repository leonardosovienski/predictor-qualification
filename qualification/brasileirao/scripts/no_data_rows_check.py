"""brasileirao: a evidência não carrega registros do dado privado (D-11/D-16).

Abre a cópia do dado real SÓ em leitura (mode=ro&immutable=1) e tira marcadores que identificam linhas
das tabelas: nomes de times (sofascore_matches, matches), nomes de jogadores (sofascore_player_ratings, se
houver coluna de nome) e event_id (sofascore_matches). Procura esses marcadores, com fronteira de palavra,
em todo arquivo de texto dos caminhos dados; também recusa arquivo SQLite (cabeçalho) e extensões de dado
(.sqlite, .sqlite3, .db, .csv, .parquet). A saída tem SÓ contagens por arquivo e categoria: nenhum
marcador é escrito, nem na saída nem no terminal.

Uso: python no_data_rows_check.py --dataset <cópia> --paths <dir|arquivo>... --out <json>
Exit 1 se houver qualquer ocorrência.
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
from contextlib import closing
from pathlib import Path

DATA_SUFFIX = {".sqlite", ".sqlite3", ".db", ".csv", ".parquet"}


def markers(dataset: Path) -> dict[str, set[str]]:
    out: dict[str, set[str]] = {"team": set(), "player": set(), "event_id": set()}
    with closing(sqlite3.connect(f"{dataset.resolve().as_uri()}?mode=ro&immutable=1", uri=True)) as db:
        for table in ("sofascore_matches", "matches"):
            for home, away in db.execute(f"SELECT home_team, away_team FROM {table}"):
                out["team"].update(t for t in (home, away) if isinstance(t, str) and len(t) >= 4)
        for (event_id,) in db.execute("SELECT event_id FROM sofascore_matches"):
            if event_id is not None and len(str(event_id)) >= 6:
                out["event_id"].add(str(event_id))
        columns = [r[1] for r in db.execute("PRAGMA table_info(sofascore_player_ratings)")]
        name_col = next((c for c in ("player_name", "name", "player") if c in columns), None)
        if name_col:
            for (name,) in db.execute(f'SELECT DISTINCT "{name_col}" FROM sofascore_player_ratings'):
                if isinstance(name, str) and len(name) >= 6 and " " in name:
                    out["player"].add(name)
    return out


def compile_markers(values: set[str], numeric: bool) -> re.Pattern | None:
    if not values:
        return None
    body = "|".join(re.escape(v) for v in sorted(values, key=len, reverse=True))
    return re.compile(rf"(?<![0-9]){body}(?![0-9])" if numeric else rf"(?<!\w)(?:{body})(?!\w)")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", type=Path, required=True)
    ap.add_argument("--paths", nargs="+", required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    found = markers(args.dataset)
    patterns = {kind: compile_markers(values, kind == "event_id") for kind, values in found.items()}
    files, hits, refused = 0, [], []
    for root in args.paths:
        root = Path(root)
        for path in [root] if root.is_file() else sorted(p for p in root.rglob("*") if p.is_file()):
            if path.resolve() == args.out.resolve():
                continue
            raw = path.read_bytes()
            if path.suffix.lower() in DATA_SUFFIX or raw.startswith(b"SQLite format 3"):
                refused.append(path.as_posix())
                continue
            files += 1
            text = raw.decode("utf-8", errors="replace")
            counts = {kind: len(p.findall(text)) for kind, p in patterns.items() if p is not None}
            if any(counts.values()):
                hits.append({"file": path.as_posix(), "counts": counts})
    doc = {
        "schema": "brasileirao/NO_DATA_ROWS_CHECK/1",
        "dataset_opened": "mode=ro&immutable=1",
        "marker_counts": {kind: len(values) for kind, values in found.items()},
        "files_scanned": files,
        "files_with_hits": len(hits),
        "hits": hits,
        "refused_data_files": refused,
        "clean": not hits and not refused,
    }
    args.out.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: doc[k] for k in ("marker_counts", "files_scanned", "files_with_hits", "clean")}))
    return 0 if doc["clean"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
