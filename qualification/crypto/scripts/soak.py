"""crypto / fase soak: executa QUALIFICATION_PROFILE_CRYPTO_V1 pelo entrypoint instalado.

Roda no runtime suportado (venv limpo só com as final_wheels). Usa os vetores congelados
da suíte de conformidade do final_commit (tests/conformance/fixtures.py, passado por
--tests), cada chamada ao `cripto-research` num processo novo. Um JSON por linha no log
bruto; ao fim, as checagens de tolerância zero.

Uso: python soak.py --tests <árvore tests/ do final_commit> --work <dir> --log <soak.jsonl>
     [--real <dir do real_env.py>]   dados reais (D-16): pedidos sobre o dataset real in-sample;
                                     o caso B continua só com o vetor sintético congelado (case_b)

Classes de falha do perfil (plan.failure_classes), 3 execuções cada, no mesmo --state dos
ciclos normais (o timeout usa um --state próprio, com timeout de 5 s): crash do worker,
timeout do Ops, host do Ops morto durante o job (ops_worker_slow + kill externo depois do
heartbeat.json, como na FAILURE_MATRIX), morte antes do commit da admission, morte durante a
gravação do resultado e corrupção (research-result.json alterado depois de gravado: show e
reexecução falham fechado com exit 5, sem reparo; o reconcile acusa só as corrupções injetadas).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import subprocess
import sys
import time
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tests", type=Path, required=True)
    ap.add_argument("--work", type=Path, required=True)
    ap.add_argument("--log", type=Path, required=True)
    ap.add_argument("--real", type=Path)
    args = ap.parse_args()
    sys.path.insert(0, str(args.tests))
    from conformance.fixtures import (
        build,
        child_environment,
        cli,
        console_script,
        experiments,
        ops_runtime,
        request,
        write_request,
    )

    from GarimpoInvestimentos.research_faults import PROCESS_DEATH_POINTS

    log = args.log.open("a", encoding="utf-8")

    def record(kind: str, **fields) -> dict:
        row = {"at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "kind": kind, **fields}
        log.write(json.dumps(row, sort_keys=True) + "\n")
        log.flush()
        return row

    if args.real:
        import importlib.util

        spec = importlib.util.spec_from_file_location("real_env", Path(__file__).with_name("real_env.py"))
        real_env = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(real_env)
        policy = json.loads((args.real / "policy.json").read_text(encoding="utf-8"))
        hang_policy = args.work / "hang-policy.json"
        args.work.mkdir(parents=True, exist_ok=True)
        hang_policy.write_text(json.dumps(policy | {"limits": policy["limits"] | {"timeout_seconds": 5}}), encoding="utf-8")
        (args.work / "requests").mkdir(exist_ok=True)
        env = {"root": args.work, "policy": args.real / "policy.json", "objects": args.real / "objects",
               "state": args.work / "s", "requests": args.work / "requests"}
        hang_env = dict(env, policy=hang_policy, state=args.work / "h")
        synthetic_request = request

        def request(rid, dataset="positive", **kw):  # noqa: F811 - real-data variant
            if dataset in ("positive", "case_a"):
                return real_env.request(rid, "real-in-sample") | kw
            return synthetic_request(rid, dataset=dataset, **kw)
        record("mode", data="real", dataset="real-in-sample", note="caso B só com o vetor sintético congelado")
    else:
        env = build(args.work / "main")
        hang_env = build(args.work / "hang", timeout_seconds=5)
    expected_results: dict[str, str] = {}  # request_id -> result_id
    corrupted: dict[str, dict] = {}  # request_id -> ids do resultado alterado de propósito
    violations: list[str] = []

    def run(e, name: str, value: dict, *, fault: str | None = None) -> tuple[int, dict]:
        path = write_request(e, name, value)
        code, lines = cli(e, "process", str(path), fault=fault)
        outcome = lines[0] if lines else {}
        record("process", request_id=value["request_id"], fault=fault, exit=code,
               status=outcome.get("status"), result_id=outcome.get("result_id"),
               operational_state=outcome.get("operational_state"),
               scientific_state=outcome.get("scientific_state"), economic_state=outcome.get("economic_state"))
        return code, outcome

    def kill_host_during_job(e, name: str, value: dict) -> bool:
        """Mata de fora o processo que hospeda o Ops enquanto o worker (ops_worker_slow) roda."""
        path = write_request(e, name, value)
        jobs = lambda: {p.parent.name for p in ops_runtime(e).glob("crypto-research-*/heartbeat.json")}  # noqa: E731
        before = jobs()
        command = [console_script(), "--state", str(e["state"]), "process", "--policy", str(e["policy"]),
                   "--objects", str(e["objects"]), str(path)]
        host = subprocess.Popen(command, env=child_environment(CRIPTO_RESEARCH_FAULT="ops_worker_slow"),
                                cwd=e["root"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        deadline = time.monotonic() + 60
        started = False
        while host.poll() is None and time.monotonic() < deadline:
            if jobs() - before:
                started = True
                break
            time.sleep(0.05)
        if started:
            time.sleep(0.5)
        host.kill()
        host.wait(30)
        record("process", request_id=value["request_id"], fault="host_killed_during_ops_job", exit=host.returncode,
               killed_during_job=started)
        return started

    def result_file(e, rid: str) -> Path | None:
        for work in experiments(e).iterdir():
            path = work / "research-result.json"
            if path.exists() and json.loads(path.read_text(encoding="utf-8")).get("request_id") == rid:
                return path
        return None

    # 20 ciclos normais, intercalados com duplicatas, restarts e falhas
    for i in range(20):
        rid = f"crypto:REQ-SOAK-N-{i:03d}"
        code, outcome = run(env, f"n{i}", request(rid))
        if code != 0 or outcome.get("status") != "RESULT":
            violations.append(f"normal {rid}: {code} {outcome.get('status')}")
        expected_results[rid] = outcome.get("result_id")
        if i % 4 == 0 and i // 4 < 5:  # 5 duplicatas
            dup = request(f"crypto:REQ-SOAK-N-{i:03d}", client_ref={"dup": i})
            code, outcome = run(env, f"d{i}", dup)
            if code != 0 or outcome.get("status") != "DUPLICATE" or outcome.get("client_ref") != {"dup": i}:
                violations.append(f"duplicate {rid}: {code} {outcome.get('status')}")
        if i % 4 == 1 and i // 4 < 5:  # 5 restarts em pontos de morte do processo, em rodízio
            point = PROCESS_DEATH_POINTS[(i // 4) % len(PROCESS_DEATH_POINTS)]
            rrid = f"crypto:REQ-SOAK-R-{i:03d}"
            code, _ = run(env, f"r{i}", request(rrid), fault=point)
            code2, outcome = run(env, f"r{i}", request(rrid))
            if code != 86 or code2 != 0 or outcome.get("status") not in {"RESULT", "DUPLICATE"}:
                violations.append(f"restart {point}: {code}/{code2} {outcome.get('status')}")
            expected_results[rrid] = outcome.get("result_id")

    # classes de falha relevantes, 3 execuções cada
    for k in range(3):
        rid = f"crypto:REQ-SOAK-CRASH-{k}"
        code, outcome = run(env, f"c{k}", request(rid), fault="ops_worker_crash")
        if code != 3 or outcome.get("scientific_state") != "NOT_EVALUATED":
            violations.append(f"crash {rid}: {code}")
        code, outcome = run(env, f"c{k}", request(rid))
        expected_results[rid] = outcome.get("result_id")
        rid = f"crypto:REQ-SOAK-HANG-{k}"
        code, outcome = run(hang_env, f"h{k}", request(rid), fault="ops_worker_hang")
        if code != 3 or outcome.get("operational_state") != "TIMEOUT":
            violations.append(f"hang {rid}: {code} {outcome.get('operational_state')}")
        code, outcome = run(hang_env, f"h{k}", request(rid))
        if code != 0:
            violations.append(f"hang retry {rid}: {code}")
        rid = f"crypto:REQ-SOAK-ADM-{k}"
        code, _ = run(env, f"a{k}", request(rid), fault="before_admission_commit")
        code2, outcome = run(env, f"a{k}", request(rid))
        if code != 86 or code2 != 0:
            violations.append(f"before_admission_commit {rid}: {code}/{code2}")
        expected_results[rid] = outcome.get("result_id")
        rid = f"crypto:REQ-SOAK-WRITE-{k}"
        code, _ = run(env, f"w{k}", request(rid), fault="during_result_write")
        code2, outcome = run(env, f"w{k}", request(rid))
        if code != 86 or code2 != 0:
            violations.append(f"during_result_write {rid}: {code}/{code2}")
        expected_results[rid] = outcome.get("result_id")
        rid = f"crypto:REQ-SOAK-HOSTKILL-{k}"
        killed = kill_host_during_job(env, f"hk{k}", request(rid))
        code, outcome = run(env, f"hk{k}", request(rid))
        if not killed or code != 0 or outcome.get("status") != "RESULT":
            violations.append(f"host_killed_during_ops_job {rid}: killed={killed} {code} {outcome.get('status')}")
        expected_results[rid] = outcome.get("result_id")
        time.sleep(12)  # órfão do worker no Linux (ops_worker_slow = 8 s) termina antes de seguir
        code, outcome = run(env, f"hk{k}", request(rid))
        if code != 0 or outcome.get("status") != "DUPLICATE":
            violations.append(f"host_killed_during_ops_job duplicate {rid}: {code} {outcome.get('status')}")
        rid = f"crypto:REQ-SOAK-CORRUPT-{k}"
        code, outcome = run(env, f"x{k}", request(rid))
        if code != 0 or outcome.get("status") != "RESULT":
            violations.append(f"corruption setup {rid}: {code} {outcome.get('status')}")
        expected_results[rid] = outcome.get("result_id")
        target = result_file(env, rid)
        if target is None:
            violations.append(f"corruption {rid}: research-result.json ausente")
            continue
        stored_bytes = target.read_bytes()
        altered = stored_bytes.replace(b'"NO_EDGE"', b'"WATCH"').replace(b'"WATCH_NO_CAPITAL"', b'"NO_EDGE"')
        if altered == stored_bytes:
            altered = stored_bytes + b" "
        target.write_bytes(altered)
        ids = json.loads(stored_bytes)
        corrupted[rid] = {"result_id": ids.get("result_id"), "experiment_id": ids.get("experiment_id")}
        show_code, lines = cli(env, "show", rid)
        code, outcome = run(env, f"x{k}", request(rid))
        untouched = target.read_bytes() == altered
        record("corruption", request_id=rid, show_exit=show_code, show_status=(lines[0].get("status") if lines else None),
               retry_exit=code, retry_status=outcome.get("status"), file_not_repaired=untouched)
        if show_code != 5 or code != 5 or not untouched:
            violations.append(f"corruption {rid}: show={show_code} retry={code} not_repaired={untouched}")

    # casos A, B e C (C = crash/hang acima), 3 ciclos cada
    for k in range(3):
        cases = (("A", "case_a", ("INCONCLUSIVE", "NO_EDGE")), ("B", "case_b", ("SUPPORTED", "NO_EDGE")))
        for case, dataset, want in (cases[:1] if args.real else cases):
            rid = f"crypto:REQ-SOAK-CASE{case}-{k}"
            code, outcome = run(env, f"k{case}{k}", request(rid, dataset=dataset))
            if (outcome.get("scientific_state"), outcome.get("economic_state")) != want:
                violations.append(f"case {case} {rid}: {outcome.get('scientific_state')}/{outcome.get('economic_state')}")
            expected_results[rid] = outcome.get("result_id")

    # checagens de tolerância zero
    results_db = env["state"] / "results.sqlite"
    with sqlite3.connect(results_db) as db:
        rows = db.execute("SELECT request_id,result_id,content_hash FROM results").fetchall()
    stored = {r: res for r, res, _ in rows}
    lost = [r for r, res in expected_results.items() if stored.get(r) != res]
    extra = [r for r in stored if r not in expected_results]
    effects = list(experiments(env).rglob("domain-effect.json"))
    per_experiment_success = {}
    for events in ops_runtime(env).glob("crypto-research-*/events.jsonl"):
        n = sum(1 for line in events.read_text(encoding="utf-8").splitlines()
                if line.strip() and json.loads(line).get("run_status") == "SUCCEEDED")
        per_experiment_success[events.parent.name] = n
    reread_mismatch = []
    for rid in expected_results:
        code, lines = cli(env, "show", rid)
        if rid in corrupted:  # resultado alterado de propósito: show tem de continuar falhando fechado
            if code != 5 or (lines and lines[0].get("result") is not None):
                violations.append(f"corrupted result served by show {rid}: {code}")
            continue
        result = lines[0].get("result") if lines else None
        blob = None
        with sqlite3.connect(results_db) as db:
            row = db.execute("SELECT result FROM results WHERE request_id=?", (rid,)).fetchone()
            blob = bytes(row[0]) if row else None
        from GarimpoInvestimentos.research_contract import canonical

        if code != 0 or result is None or blob is None or canonical(result) != blob:
            reread_mismatch.append(rid)
        if result is not None and (result.get("capital_permission") is not False
                                   or not all(str(result.get(f, "")).startswith("crypto:")
                                              for f in ("request_id", "result_id", "experiment_id", "admission_id"))):
            violations.append(f"authority/ids {rid}")
    code, lines = cli(env, "reconcile")
    findings = (lines[0].get("findings") if lines else None) or []
    injected = {i for c in corrupted.values() for i in c.values() if i}

    def refers(finding: dict, ids: set) -> bool:
        return bool({finding.get("experiment_id"), finding.get("result_id")} & ids)

    foreign_findings = [f for f in findings if not refers(f, injected)]
    missed_corruptions = [rid for rid, c in corrupted.items() if not any(refers(f, set(c.values())) for f in findings)]
    reconcile_ok = code == (5 if corrupted else 0) and not foreign_findings and not missed_corruptions
    summary = record(
        "summary",
        requests_with_result=len(expected_results),
        stored_results=len(stored),
        lost=lost,
        unexpected=extra,
        domain_effects=len(effects),
        ops_success_per_job_max=max(per_experiment_success.values()) if per_experiment_success else 0,
        ops_jobs=len(per_experiment_success),
        reread_mismatch=reread_mismatch,
        reconcile_exit=code,
        reconcile_findings=(lines[0].get("findings") if lines else None),
        corrupted=sorted(corrupted),
        reconcile_foreign_findings=foreign_findings,
        reconcile_missed_corruptions=missed_corruptions,
        violations=violations,
        effects_sha256=sorted(hashlib.sha256(p.read_bytes()).hexdigest()[:16] for p in effects)[:5],
    )
    ok = (not lost and not extra and not reread_mismatch and not violations and reconcile_ok
          and summary["ops_success_per_job_max"] == 1 and len(effects) == len(stored))
    record("verdict", zero_tolerance_ok=ok)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
