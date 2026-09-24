"""brasileirao / temporal-suite: corroboração com o DADO REAL (Windows local), pelo entrypoint instalado.

Variantes de CÓPIAS do snapshot real (nunca a fonte): canário FUTURE_CANARY_BR_001 depois do cutoff,
ordem física das linhas permutada (seed 11), caches do momento da captura envenenados, e placar
trocado de um jogo que divide o kickoff com outro. O mesmo pedido (temporada 2024, 1X2, climatologia)
roda sobre cada variante; o conteúdo comparável do resultado tem de ser idêntico ao da base, exceto
onde a mudança é legítima (o jogo do placar trocado só pode mudar o que vem depois dele).

Uso: python real_corroboration.py --script <brasileirao-research.exe> --dataset <cópia real> --work <dir curto> --out <dir>
     --policy <policy.json do run real> --objects-from <object store do run real>
"""

from __future__ import annotations

import argparse
import json
import random
import shutil
import sqlite3
import subprocess
from contextlib import closing
from pathlib import Path

CANARY = "FUTURE_CANARY_BR_001"
AS_OF = "2026-09-08T19:31:32Z"
DATA_CUTOFF = "2025-01-01T00:00:00Z"


def run(cmd: list[str], log: Path) -> subprocess.CompletedProcess:
    done = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
    with log.open("a", encoding="utf-8") as fh:
        fh.write(f"$ {' '.join(cmd)}\n[exit {done.returncode}]\n{done.stdout}\n{done.stderr[-3000:]}\n")
    return done


def variant(base: Path, target: Path, kind: str) -> dict:
    shutil.copyfile(base, target)
    info = {"kind": kind}
    with closing(sqlite3.connect(target)) as db, db:
        if kind == "canary":
            db.execute(
                "INSERT INTO sofascore_matches (event_id, competition, season, date, kickoff_at, home_team, away_team, home_score, away_score) "
                "VALUES (99000001, 'Brasileirão Série A 2025', '2025', '2025-02-10', '2025-02-10T22:00:00+00:00', ?, 'Flamengo', 17, 0)", (CANARY,))
            db.execute("INSERT INTO matches (event_id, date, home_team, away_team, home_score, away_score, tournament, neutral) "
                       "VALUES (99000001, '2025-02-10', ?, 'Flamengo', 17, 0, 'Brasileirão Série A', 0)", (CANARY,))
            db.execute("INSERT OR REPLACE INTO current_elo VALUES (?, 99999.0)", (CANARY,))
        elif kind == "caches":
            db.execute("UPDATE current_elo SET elo = elo * 3")
            db.execute("UPDATE model_parameters SET param_a = 9.0, param_b = 9.0")
        elif kind == "same_kickoff":
            row = db.execute(
                "SELECT s.kickoff_at, min(s.event_id), max(s.event_id) FROM sofascore_matches s JOIN matches m ON m.event_id = s.event_id "
                "WHERE s.season = '2024' AND s.kickoff_at IS NOT NULL GROUP BY s.kickoff_at HAVING count(*) >= 2 ORDER BY s.kickoff_at LIMIT 1 OFFSET 40").fetchone()
            kickoff, a, b = row
            db.execute("UPDATE matches SET home_score = 9, away_score = 0 WHERE event_id = ?", (a,))
            db.execute("UPDATE sofascore_matches SET home_score = 9, away_score = 0 WHERE event_id = ?", (a,))
            info.update(kickoff=kickoff, changed_event=a, sibling_event=b)
    if kind == "permuted":
        tmp = target.with_suffix(".perm")
        with closing(sqlite3.connect(target)) as src, closing(sqlite3.connect(tmp)) as dst:
            schema = [r[0] for r in src.execute("SELECT sql FROM sqlite_master WHERE type='table' AND sql IS NOT NULL")]
            for ddl in schema:
                dst.execute(ddl)
            for (table,) in src.execute("SELECT name FROM sqlite_master WHERE type='table'"):
                rows = src.execute(f'SELECT * FROM "{table}"').fetchall()
                random.Random(11).shuffle(rows)
                if rows:
                    dst.executemany(f'INSERT INTO "{table}" VALUES ({",".join("?" * len(rows[0]))})', rows)
            dst.commit()
        tmp.replace(target)
        info["seed"] = 11
    return info


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--script", required=True)
    ap.add_argument("--dataset", required=True, type=Path)
    ap.add_argument("--work", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--policy", required=True, type=Path, help="policy.json do run real (registry dos objetos JSON)")
    ap.add_argument("--objects-from", required=True, type=Path, help="object store do run real")
    args = ap.parse_args()
    args.work.mkdir(parents=True, exist_ok=False)
    args.out.mkdir(parents=True, exist_ok=True)
    log = args.out / "commands.log"
    objects = args.work / "obj"
    registry = []
    src_policy = json.loads(args.policy.read_text(encoding="utf-8"))
    # Reuse the JSON reference objects of the real run (same hashes), re-provisioned into this store.
    real_objects = args.objects_from
    for entry in src_policy["registry"]:
        if entry["kind"] == "dataset":
            continue
        path = real_objects / entry["content_hash"][:2] / entry["content_hash"]
        done = run([args.script, "put-object", "--objects", str(objects), str(path)], log)
        assert done.returncode == 0 and json.loads(done.stdout)["object_hash"] == entry["content_hash"], done.stderr
        registry.append(entry)
    variants = {"base": None, "canary": "canary", "permuted": "permuted", "caches": "caches", "same_kickoff": "same_kickoff"}
    infos = {}
    for name, kind in variants.items():
        copy = args.work / f"{name}.sqlite3"
        infos[name] = variant(args.dataset, copy, kind) if kind else (shutil.copyfile(args.dataset, copy) and {"kind": "base"})
        done = run([args.script, "put-dataset", "--objects", str(objects), "--source", str(copy), "--as-of", AS_OF, "--label", f"real-{name}"], log)
        assert done.returncode == 0, done.stderr
        registry.append({"kind": "dataset", "name": f"real-{name}", "version": "1", "revision_id": f"real-{name}-r1",
                         "content_hash": json.loads(done.stdout)["manifest_hash"]})
    policy = src_policy | {"registry": registry, "policy_id": "brasileirao-research-real-corroboration"}
    (args.work / "policy.json").write_text(json.dumps(policy), encoding="utf-8")
    results = {}
    for name in variants:
        request = {
            "schema_version": "brasileirao-research-request/1", "request_id": f"brasileirao:REQ-CORR-{name}",
            "request_type": "WALKFORWARD_FORECAST_EVALUATION", "research_id": "brasileirao:R-REAL-CORROBORATION",
            "hypothesis_id": "brasileirao:HQ-SERVING-BASELINE", "competition": "Brasileirão Série A", "season": 2024, "target": "1X2",
            "events": {"kickoff_from": "2024-01-01T00:00:00Z", "kickoff_to": DATA_CUTOFF}, "data_cutoff": DATA_CUTOFF,
            "decision_lead_minutes": 60,
            "references": {"dataset": {"name": f"real-{name}", "version": "1"}, "model": {"name": "serving-baseline", "version": "1"},
                           "features": {"name": "elo-home-advantage", "version": "1"}, "baseline": {"name": "climatology", "version": "1"},
                           "cost_model": {"name": "close-slippage-tax", "version": "1"}, "odds": {"name": "sofascore-close", "version": "1"}},
            "priority_hint": "NORMAL",
        }
        path = args.work / f"req-{name}.json"
        path.write_text(json.dumps(request, ensure_ascii=False), encoding="utf-8")
        done = run([args.script, "--state", str(args.work / "s"), "process", "--policy", str(args.work / "policy.json"), "--objects", str(objects), str(path)], log)
        shown = run([args.script, "--state", str(args.work / "s"), "show", request["request_id"]], log)
        (args.out / f"result_{name}.json").write_text(shown.stdout, encoding="utf-8")
        results[name] = json.loads(shown.stdout)["result"]

    def comparable(result: dict) -> dict:
        d = result["domain_facts"]
        return {"predictions": [{k: v for k, v in p.items() if k != "information_fingerprint"} for p in d["predictions"]],
                "evaluation": d["evaluation"], "economics": d["economics"], "states": [result["result_state"], result["scientific_state"], result["economic_state"]]}

    base = comparable(results["base"])
    checks = {
        "canary_identical": comparable(results["canary"]) == base,
        "canary_token_absent": all(CANARY.encode() not in p.read_bytes() for p in (args.work / "s").rglob("*") if p.is_file() and p.suffix in {".json", ".jsonl", ".sqlite"}),
        "permuted_identical": comparable(results["permuted"]) == base,
        "poisoned_caches_identical": comparable(results["caches"]) == base,
    }
    sk = infos["same_kickoff"]
    before = {p["event_id"]: p for p in results["base"]["domain_facts"]["predictions"]}
    after = {p["event_id"]: p for p in results["same_kickoff"]["domain_facts"]["predictions"]}
    checks["same_kickoff_sibling_identical"] = before.get(sk["sibling_event"]) == after.get(sk["sibling_event"]) and sk["sibling_event"] in before
    later = [e for e, p in before.items() if p["kickoff"] > sk["kickoff"].replace("+00:00", "Z")]
    checks["same_kickoff_change_seen_later"] = any(before[e]["information_fingerprint"] != after[e]["information_fingerprint"] for e in later)
    checks["max_used_minus_cutoff_negative"] = all(r["core_facts"]["temporal_validation"]["max_used_minus_cutoff_seconds"] < 0 for r in results.values())
    summary = {"variants": infos, "checks": checks, "all_ok": all(checks.values()),
               "n_predictions": len(results["base"]["domain_facts"]["predictions"])}
    (args.out / "REAL_CORROBORATION.json").write_text(json.dumps(summary, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
