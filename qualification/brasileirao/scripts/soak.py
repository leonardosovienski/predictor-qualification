"""brasileirao / fase soak: executa QUALIFICATION_PROFILE_BR_V1 pelo entrypoint instalado.

Roda no runtime suportado (venv limpo só com as final_wheels). Usa os vetores congelados da suíte
de conformidade do final_commit (tests/conformance/fixtures.py, passado por --tests); cada chamada
ao `brasileirao-research` é um processo novo. Um JSON por linha no log bruto; ao fim, as checagens
de tolerância zero. Com vetores sintéticos é DIAGNÓSTICO enquanto a D-16 não for decidida.

Uso: python soak.py --tests <árvore tests/ do final_commit> --work <dir> --log <soak.jsonl>
         [--real-dataset <cópia do dado real> --real-dataset-sha256 <hex> --real-as-of <T>]

Modo dado real (D-16, PC 2): mesmo perfil, mesmas classes de falha, mesmas seeds de permutação, mesmo
canário, mesmos comparadores, mesma política e mesmos objetos JSON congelados (fixtures.py); muda só o
dataset: a base é a CÓPIA byte a byte do dado real (sha256 conferido) e as variantes (canário depois do
cutoff, permutações da ordem física das linhas com as seeds congeladas) são cópias derivadas dela, nunca
a fonte. Os pares de mesmo kickoff saem do próprio dado real, com os filtros do worker. Nada do dado vai
para o log: só ids de pedido, estados, contagens e sha256.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import shutil
import sqlite3
from contextlib import closing
from datetime import UTC, datetime, timedelta
import sys
import time
from pathlib import Path

PROFILE = {
    "normal_cycles": 20,
    "restarts": 5,
    "duplicate_requests": 5,
    "runs_per_relevant_failure_class": 3,
    "same_kickoff_cycles": 5,
    "out_of_order_dataset_cycles": 5,
    "future_canary_cycles": 5,
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _insert(db: sqlite3.Connection, table: str, row: dict) -> None:
    columns = ",".join(f'"{c}"' for c in row)
    db.execute(f'INSERT INTO "{table}" ({columns}) VALUES ({",".join("?" * len(row))})', list(row.values()))


def real_variant(source: Path, target: Path, fixtures, *, canary: bool = False, permutation_seed: int | None = None) -> None:
    """Cópia derivada do dado real, como build_dataset faz com o sintético (a base é byte a byte)."""
    shutil.copyfile(source, target)
    if canary:
        # Duas partidas FUTURE_CANARY_BR_001 depois do cutoff (fixtures.CANARY_KICKOFF e +7 dias), 17-0 e 0-17 contra
        # times reais, copiando o resto das colunas de um jogo-modelo de 2023 (como o sintético); cache current_elo
        # envenenado para o canário. Nada é lido de volta para o log.
        with closing(sqlite3.connect(target)) as db, db:
            db.row_factory = sqlite3.Row
            template = db.execute(
                "SELECT * FROM sofascore_matches WHERE season = '2023' AND superseded_by_event_id IS NULL "
                "AND kickoff_at IS NOT NULL AND event_id IN (SELECT event_id FROM matches) ORDER BY event_id LIMIT 1"
            ).fetchone()
            teams: list[str] = []
            for (team,) in db.execute("SELECT home_team FROM sofascore_matches WHERE season = '2023' ORDER BY event_id"):
                if team not in teams:
                    teams.append(team)
                if len(teams) == 2:
                    break
            match_row = db.execute("SELECT * FROM matches WHERE event_id = ?", (template["event_id"],)).fetchone()
            lines = db.execute("SELECT * FROM odds_lines WHERE event_id = ?", (template["event_id"],)).fetchall()
            base = db.execute("SELECT max(event_id) FROM sofascore_matches").fetchone()[0]
            for offset, (home, away, hs, as_, days) in enumerate(
                ((fixtures.CANARY, teams[0], 17, 0, 0), (teams[1], fixtures.CANARY, 0, 17, 7)), 1
            ):
                kickoff = fixtures.CANARY_KICKOFF + timedelta(days=days)
                event_id = base + offset
                day = kickoff.date().isoformat()
                row = dict(template) | {"event_id": event_id, "date": day, "kickoff_at": kickoff.isoformat(timespec="seconds"),
                                        "home_team": home, "away_team": away, "home_score": hs, "away_score": as_,
                                        "superseded_by_event_id": None}
                _insert(db, "sofascore_matches", row)
                _insert(db, "matches", dict(match_row) | {"event_id": event_id, "date": day, "home_team": home,
                                                          "away_team": away, "home_score": hs, "away_score": as_})
                for line in lines:
                    _insert(db, "odds_lines", dict(line) | {"event_id": event_id})
            db.execute("INSERT OR REPLACE INTO current_elo VALUES (?, 99999.0)", (fixtures.CANARY,))
    if permutation_seed is not None:
        # Mesmo esquema (tabelas, índices, gatilhos), mesmas linhas, ordem física de inserção embaralhada pela seed.
        tmp = target.with_suffix(".perm")
        with closing(sqlite3.connect(target)) as src, closing(sqlite3.connect(tmp)) as dst:
            objects = src.execute("SELECT type, name, sql FROM sqlite_master WHERE sql IS NOT NULL AND name NOT LIKE 'sqlite_%'").fetchall()
            for kind, _name, ddl in objects:
                if kind == "table":
                    dst.execute(ddl)
            for kind, name, _ddl in objects:
                if kind != "table":
                    continue
                rows = src.execute(f'SELECT * FROM "{name}"').fetchall()
                random.Random(permutation_seed).shuffle(rows)
                if rows:
                    dst.executemany(f'INSERT INTO "{name}" VALUES ({",".join("?" * len(rows[0]))})', rows)
            for kind, _name, ddl in objects:
                if kind != "table":
                    dst.execute(ddl)
            dst.commit()
        tmp.replace(target)


def real_lab(source: Path, as_of: str, variants: dict[str, dict], fixtures, **limits):
    """standard_lab com os mesmos objetos JSON e a mesma política congelados; datasets = variantes do dado real."""
    from conformance.harness import Lab, short_root

    lab = Lab(short_root())
    lab.put_json("model", "serving-baseline", fixtures.MODEL_CONFIG)
    lab.put_json("features", "elo-home-advantage", fixtures.FEATURES)
    lab.put_json("baseline", "climatology", fixtures.BASELINE_CLIM)
    lab.put_json("baseline", "market", fixtures.BASELINE_MARKET)
    lab.put_json("cost_model", "close-slippage-tax", fixtures.COST_MODEL)
    lab.put_json("odds", "sofascore-close", fixtures.ODDS)
    for name, options in variants.items():
        target = lab.root / "src" / f"{name}.sqlite3"
        target.parent.mkdir(parents=True, exist_ok=True)
        real_variant(source, target, fixtures, **options)
        lab.put_dataset(name, target, as_of=as_of)
        target.unlink()
    lab.write_policy(**limits)
    return lab


def real_same_kickoff_pairs(source: Path, fixtures, count: int) -> list[list[dict]]:
    """Pares de jogos reais de 2023 (jun-set) com o mesmo kickoff, pelos filtros do worker (temporada, competição,
    kickoff presente, não substituído, na janela do pedido padrão); os dois menores event_id de cada kickoff."""
    window_from = datetime.fromisoformat("2023-06-01T00:00:00+00:00")
    window_to = datetime.fromisoformat(fixtures.DATA_CUTOFF.replace("Z", "+00:00"))
    groups: dict[datetime, list[int]] = {}
    with closing(sqlite3.connect(f"{source.resolve().as_uri()}?mode=ro&immutable=1", uri=True)) as db:
        for event_id, competition, kickoff_text in db.execute(
            "SELECT event_id, competition, kickoff_at FROM sofascore_matches WHERE season = '2023' "
            "AND kickoff_at IS NOT NULL AND superseded_by_event_id IS NULL ORDER BY event_id"
        ):
            if not str(competition or "").startswith("Brasileirão Série A"):
                continue
            kickoff = datetime.fromisoformat(kickoff_text).astimezone(UTC)
            if window_from <= kickoff < window_to and 6 <= kickoff.month <= 9:
                groups.setdefault(kickoff, []).append(int(event_id))
    pairs = []
    for kickoff in sorted(groups):
        if len(groups[kickoff]) >= 2:
            pairs.append([{"event_id": e, "kickoff_at": kickoff.strftime("%Y-%m-%dT%H:%M:%SZ")} for e in sorted(groups[kickoff])[:2]])
    return pairs[:count]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tests", type=Path, required=True)
    ap.add_argument("--work", type=Path, required=True)
    ap.add_argument("--log", type=Path, required=True)
    ap.add_argument("--real-dataset", type=Path)
    ap.add_argument("--real-dataset-sha256")
    ap.add_argument("--real-as-of")
    args = ap.parse_args()
    sys.path.insert(0, str(args.tests))
    from conformance import fixtures
    from conformance.harness import cli, comparable, outcomes, standard_lab

    from brasileirao_predictor.research_runtime.contract import canonical
    from brasileirao_predictor.research_runtime.faults import FAULT_ENV, FAULT_EXIT, PROCESS_DEATH_POINTS

    real = args.real_dataset is not None
    if real and (not args.real_dataset_sha256 or not args.real_as_of):
        raise SystemExit("--real-dataset exige --real-dataset-sha256 e --real-as-of")
    if real and sha256_file(args.real_dataset) != args.real_dataset_sha256:
        raise SystemExit("cópia do dado real com sha256 diferente do registrado")
    args.work.mkdir(parents=True, exist_ok=True)
    log = args.log.open("a", encoding="utf-8")

    def record(kind: str, **fields) -> dict:
        row = {"at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "kind": kind, **fields}
        log.write(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n")
        log.flush()
        return row

    record("profile", **PROFILE)
    seeds = (11, 23, 37, 41, 53)
    base_name = "real" if real else "synthetic"
    variants = {base_name: {}, "canary": {"canary": True}, **{f"perm-{s}": {"permutation_seed": s} for s in seeds}}
    if real:
        lab = real_lab(args.real_dataset, args.real_as_of, variants, fixtures)
        hang = real_lab(args.real_dataset, args.real_as_of, {base_name: {}}, fixtures, timeout_seconds=3)
        record("dataset", mode="real", source_sha256=args.real_dataset_sha256, as_of=args.real_as_of,
               snapshots={name: stored["sqlite_sha256"] for name, stored in lab.datasets.items()},
               manifests={name: stored["manifest_hash"] for name, stored in lab.datasets.items()},
               tables={name: stored["manifest"]["tables"] for name, stored in lab.datasets.items()},
               hang_snapshot=hang.datasets[base_name]["sqlite_sha256"])
    else:
        lab = standard_lab(variants)
        hang = standard_lab(timeout_seconds=3)

    class _Fixtures:
        """fixtures.request com o dataset base do modo (o sintético continua idêntico)."""

        @staticmethod
        def request(request_id: str, **kw) -> dict:
            kw.setdefault("dataset", base_name)
            return fixtures.request(request_id, **kw)

    requests = _Fixtures if real else fixtures
    expected: dict[str, str] = {}
    violations: list[str] = []

    def run(target_lab, value: dict, *, fault: str | None = None) -> tuple[int, dict]:
        env = {FAULT_ENV: fault} if fault else None
        code, lines, _stderr = target_lab.process(target_lab.request_file(value), env=env)
        outcome = lines[-1] if lines else {}
        record("process", request_id=value["request_id"], fault=fault, exit=code, status=outcome.get("status"),
               result_id=outcome.get("result_id"), operational_state=outcome.get("operational_state"),
               scientific_state=outcome.get("scientific_state"), economic_state=outcome.get("economic_state"),
               reason=outcome.get("reason"))
        return code, outcome

    def shown(target_lab, rid: str) -> dict:
        code, payload = target_lab.show(rid)
        return payload.get("result") if code == 0 else {}

    windows = [("2023-06-01T00:00:00Z", "2023-07-01T00:00:00Z"), ("2023-07-01T00:00:00Z", "2023-08-01T00:00:00Z"),
               ("2023-08-01T00:00:00Z", fixtures.DATA_CUTOFF), ("2023-06-01T00:00:00Z", fixtures.DATA_CUTOFF)]
    # normal cycles, with duplicates and restarts interleaved
    for i in range(PROFILE["normal_cycles"]):
        rid = f"brasileirao:REQ-SOAK-N-{i:03d}"
        start, end = windows[i % len(windows)]
        target = "1X2" if i % 2 == 0 else "OU25"
        value = requests.request(rid, target=target, kickoff_from=start, kickoff_to=end)
        code, outcome = run(lab, value)
        if code != 0 or outcome.get("status") != "RESULT":
            violations.append(f"normal {rid}: {code} {outcome.get('status')}")
        expected[rid] = outcome.get("result_id")
        if i % 4 == 0 and i // 4 < PROFILE["duplicate_requests"]:
            code, dup = run(lab, value | {"client_ref": {"dup": i}})
            if code != 0 or dup.get("status") != "DUPLICATE" or dup.get("client_ref") != {"dup": i} or dup.get("result_id") != expected[rid]:
                violations.append(f"duplicate {rid}: {code} {dup.get('status')}")
        if i % 4 == 1 and i // 4 < PROFILE["restarts"]:
            point = PROCESS_DEATH_POINTS[(i // 4) * 2 % len(PROCESS_DEATH_POINTS)]
            rrid = f"brasileirao:REQ-SOAK-R-{i:03d}"
            restart = requests.request(rrid, target=target, kickoff_from=start, kickoff_to=end)
            code, _ = run(lab, restart, fault=point)
            code2, outcome = run(lab, restart)
            if code != FAULT_EXIT or code2 != 0 or outcome.get("status") not in {"RESULT", "DUPLICATE"}:
                violations.append(f"restart {point}: {code}/{code2} {outcome.get('status')}")
            expected[rrid] = outcome.get("result_id")

    # relevant failure classes, 3 runs each: worker crash, Ops timeout, death before the admission
    # commit, death during the result write
    for k in range(PROFILE["runs_per_relevant_failure_class"]):
        rid = f"brasileirao:REQ-SOAK-CRASH-{k}"
        code, outcome = run(lab, requests.request(rid), fault="ops_worker_crash")
        if code != 3 or outcome.get("scientific_state") != "NOT_EVALUATED" or outcome.get("operational_state") != "FAILED":
            violations.append(f"crash {rid}: {code}")
        code, outcome = run(lab, requests.request(rid))
        expected[rid] = outcome.get("result_id")
        if code != 0:
            violations.append(f"crash retry {rid}: {code}")
        rid = f"brasileirao:REQ-SOAK-HANG-{k}"
        code, outcome = run(hang, requests.request(rid), fault="ops_worker_hang")
        if code != 3 or outcome.get("operational_state") != "TIMEOUT" or outcome.get("scientific_state") != "NOT_EVALUATED":
            violations.append(f"hang {rid}: {code} {outcome.get('operational_state')}")
        rid = f"brasileirao:REQ-SOAK-ADM-{k}"
        code, _ = run(lab, requests.request(rid), fault="before_admission_commit")
        code2, outcome = run(lab, requests.request(rid))
        if code != FAULT_EXIT or code2 != 0:
            violations.append(f"before_admission_commit {rid}: {code}/{code2}")
        expected[rid] = outcome.get("result_id")
        rid = f"brasileirao:REQ-SOAK-WRITE-{k}"
        code, _ = run(lab, requests.request(rid), fault="during_result_write")
        code2, outcome = run(lab, requests.request(rid))
        if code != FAULT_EXIT or code2 != 0:
            violations.append(f"during_result_write {rid}: {code}/{code2}")
        expected[rid] = outcome.get("result_id")

    base = comparable(shown(lab, "brasileirao:REQ-SOAK-N-003"))  # 2023-06-01 → cutoff, 1X2? (i=3: OU25)
    # same-kickoff cycles: listed pairs of games that share a kickoff
    if real:
        same_listed = real_same_kickoff_pairs(args.real_dataset, fixtures, PROFILE["same_kickoff_cycles"])
    else:
        pairs = {}
        for e in fixtures.fixtures():
            if e["season"] == 2023 and 6 <= e["kickoff"].month <= 9 and e["superseded_by"] is None and e["slot"] in (0, 1):
                pairs.setdefault(e["kickoff"], []).append(e)
        same = [v for v in pairs.values() if len(v) == 2][: PROFILE["same_kickoff_cycles"]]
        same_listed = [[{"event_id": x["event_id"], "kickoff_at": x["kickoff"].strftime("%Y-%m-%dT%H:%M:%SZ")} for x in (a, b)]
                       for a, b in same]
    if len(same_listed) < PROFILE["same_kickoff_cycles"]:
        violations.append(f"same kickoff: only {len(same_listed)} pairs for {PROFILE['same_kickoff_cycles']} cycles")
    for k, listed in enumerate(same_listed):
        rid = f"brasileirao:REQ-SOAK-SAMEKO-{k}"
        code, outcome = run(lab, requests.request(rid, fixtures_list=listed, odds=False))
        result = shown(lab, rid)
        preds = result.get("domain_facts", {}).get("predictions", [])
        if code != 0 or len(preds) != 2 or preds[0]["information_fingerprint"] != preds[1]["information_fingerprint"]:
            violations.append(f"same kickoff {rid}: information sets differ or missing")
        expected[rid] = outcome.get("result_id")
    # out-of-order dataset cycles: 5 insertion-order permutations must give the same result
    reference = comparable(shown(lab, "brasileirao:REQ-SOAK-N-003"))
    for seed in seeds[: PROFILE["out_of_order_dataset_cycles"]]:
        rid = f"brasileirao:REQ-SOAK-PERM-{seed}"
        start, end = windows[3]
        code, outcome = run(lab, requests.request(rid, target="OU25", kickoff_from=start, kickoff_to=end, dataset=f"perm-{seed}"))
        if code != 0 or comparable(shown(lab, rid)) != reference:
            violations.append(f"permutation {seed}: result differs")
        expected[rid] = outcome.get("result_id")
    # future canary cycles
    for k in range(PROFILE["future_canary_cycles"]):
        rid = f"brasileirao:REQ-SOAK-CANARY-{k}"
        start, end = windows[3]
        code, outcome = run(lab, requests.request(rid, target="OU25", kickoff_from=start, kickoff_to=end, dataset="canary"))
        if code != 0 or comparable(shown(lab, rid)) != reference:
            violations.append(f"canary {rid}: result differs from the canary-free reference")
        expected[rid] = outcome.get("result_id")
    del base
    leaked = [str(p) for p in lab.state.rglob("*") if p.is_file() and p.suffix in {".json", ".jsonl", ".sqlite"}
              and fixtures.CANARY.encode() in p.read_bytes()]
    if leaked:
        violations.append(f"FUTURE_CANARY found in {leaked[:5]}")

    # zero-tolerance checks
    with closing(sqlite3.connect(lab.state / "results.sqlite")) as db, db:
        rows = db.execute("SELECT request_id,result_id,content_hash,result FROM results").fetchall()
    stored = {r: res for r, res, _h, _b in rows}
    lost = [r for r, res in expected.items() if stored.get(r) != res]
    extra = [r for r in stored if r not in expected]
    effects = list((lab.state / "x" / "e").rglob("domain-effect.json"))
    per_job_success = {}
    for events in (lab.state / "x" / "o").glob("brasileirao-research-*/events.jsonl"):
        per_job_success[events.parent.name] = sum(
            1 for line in events.read_text(encoding="utf-8").splitlines() if line.strip() and json.loads(line).get("run_status") == "SUCCEEDED"
        )
    reread_mismatch = []
    blobs = {r: bytes(b) for r, _res, _h, b in rows}
    for rid in expected:
        result = shown(lab, rid)
        if not result or canonical(result) != blobs.get(rid):
            reread_mismatch.append(rid)
        if result and (result.get("capital_permission") is not False or not all(
            str(result.get(f, "")).startswith("brasileirao:") for f in ("request_id", "result_id", "experiment_id", "admission_id"))):
            violations.append(f"authority/ids {rid}")
    reconcile = cli("--state", str(lab.state), "reconcile")
    summary = record(
        "summary",
        requests_with_result=len(expected),
        stored_results=len(stored),
        lost=lost,
        unexpected=extra,
        domain_effects=len(effects),
        ops_success_per_job_max=max(per_job_success.values()) if per_job_success else 0,
        ops_jobs=len(per_job_success),
        reread_mismatch=reread_mismatch,
        reconcile_exit=reconcile.returncode,
        reconcile_findings=json.loads(reconcile.stdout).get("findings") if reconcile.stdout.startswith("{") else reconcile.stdout[-500:],
        violations=violations,
        effects_sha256=sorted(hashlib.sha256(p.read_bytes()).hexdigest()[:16] for p in effects)[:5],
    )
    ok = (not lost and not extra and not reread_mismatch and not violations and reconcile.returncode == 0
          and summary["ops_success_per_job_max"] == 1 and len(effects) == len(stored))
    record("verdict", zero_tolerance_ok=ok)
    del outcomes
    lab.cleanup()
    hang.cleanup()
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
