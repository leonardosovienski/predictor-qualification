"""integration-stocks, fase idempotency-failure (IDEMPOTENCY, RESTART_RECOVERY, FAILURE_INJECTION; CAIN_INGESTION).

Executa cada ponto de FAILURE_MATRIX.json (F01–F15) num diretório novo, pelo runtime suportado, com injeção na borda
(morte real do processo com exit 86, parada de um lado, arquivos de spool adulterados/duplicados/fora de ordem/de outra
versão, falha do Ops do domínio, corrupção do resultado autoritativo do domínio). Depois de cada falha confere a
recuperação: nada perdido, nada duplicado (spool, inbox, memória, admission e experimentos do domínio).
Adaptado de qualification/integration-crypto/scripts/failure_matrix.py (mesmos pontos e conferências; domínio
stocks; falhas do domínio por STOCKS_RESEARCH_FAULT).
Uso (com o env.sh do runtime_env.sh): python failure_matrix.py <qualification/integration-stocks> <work> <out> [F01 ...]
"""

from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

from harness import Harness, now

TAMPER = r'''
import json, sys
from pathlib import Path
from research_protocol import v2
mode, task_path, result_path, out_path = sys.argv[1:5]
task = v2.loads_task(Path(task_path).read_bytes())
result = v2.loads_result(Path(result_path).read_bytes(), task=task)
if mode == "other-payload":
    payload = json.loads(result["result"]["payload_canonical"])
    payload["domain_facts"] = dict(payload["domain_facts"], tampered=True)
    outcome = {"status": "RESULT", "exit_code": 0, "request_id": task["request_id"],
               "client_ref": task["payload"]["client_ref"], "result": payload}
    raw = v2.dumps_result(v2.build_result(task, outcome, adapter=result["adapter"], produced_at=result["produced_at"]),
                          task=task)
elif mode == "other-episode":
    doc = json.loads(Path(result_path).read_bytes()); doc["episode_id"] = "stocks:episode-99"; raw = v2.canonical(doc)
elif mode == "wrong-version":
    doc = json.loads(Path(result_path).read_bytes()); doc["schema"] = "research-result/1"; raw = v2.canonical(doc)
elif mode == "task-v3":
    doc = json.loads(Path(task_path).read_bytes()); doc["schema"] = "research-task/3"; raw = v2.canonical(doc)
Path(out_path).write_bytes(raw)
print(json.dumps({"mode": mode, "bytes": len(raw)}))
'''


class Point:
    def __init__(self, fid: str, root: Path, mission: Path, out: Path, n: int):
        self.h = Harness(out / fid, root / fid, mission, fid)
        self.mission, self.n, self.fid = mission, n, fid
        self.props = root / fid / "proposals"
        self.props.mkdir(parents=True, exist_ok=True)

    def proposal(self, k: int, hypothesis: str = "stocks:QUAL-PIT-MOM-REAL-001") -> Path:
        path = self.h.real_proposal("fixtures/proposals/e2e/01-allow.json", self.props / f"{k}.json",
                                    request_id=f"stocks:REQ-IS-FM-{self.fid}-{k}", hypothesis_id=hypothesis)
        value = json.loads(path.read_text(encoding="utf-8"))
        value["proposal_id"] = f"cain:FM-{self.fid}-{k}"
        if k > 1:  # ciclo 2 (R17): a proposta seguinte do ponto é outro experimento, com controle negativo de semente k
            kind = json.loads((self.mission / "FROZEN_VECTORS.json").read_text(encoding="utf-8"))["soak_generator"][
                "negative_control"]["kind"]
            value["request"]["parameters"] = dict(value["request"]["parameters"],
                                                  negative_control={"kind": kind, "seed": k})
        path.write_text(json.dumps(value), encoding="utf-8")
        return path

    def propose(self, k: int, **kw):
        return self.h.propose(f"propose {k}", self.proposal(k), **kw)

    def cycle(self, k: int) -> dict:
        code, lines, _ = self.propose(k)
        self.h.dispatch(f"dispatch {k}")
        self.h.consumer(f"consumer {k}")
        self.h.ingest(f"ingest {k}")
        return lines[0]

    def counts(self, label: str) -> dict:
        ep = self.h.episodes(label)
        with self.h.ro(self.h.dstate / "admission.sqlite") as db:
            admissions = db.execute("SELECT count(*) FROM admissions WHERE decision='ACCEPTED'").fetchone()[0]
        with self.h.ro(self.h.dstate / "x" / "journal.sqlite") as db:
            experiments = db.execute("SELECT count(*) FROM experiments").fetchone()[0]
        tasks = len(list((self.h.spool / "stocks" / "tasks").glob("*.json")))
        return {"episodes": len(ep["episodes"]), "allow": sum(e["decision"] == "ALLOW" for e in ep["episodes"]),
                "inbox": len(ep["inbox"]), "facts": sum(1 for r in ep["inbox"] if r["fact_id"]),
                "spool_tasks": tasks, "admissions": admissions, "experiments": experiments,
                "memory": ep["memory"]["status"]}

    def tamper(self, mode: str, task_id: str, result_file: Path, out_file: Path) -> None:
        script = self.h.work / "tamper.py"
        script.write_text(TAMPER, encoding="utf-8")
        task_file = self.h.spool / "stocks" / "tasks" / (task_id.split(":", 1)[1] + ".json")
        self.h.run(f"tamper {mode}", [os.environ["CAIN_PY"], "-I", script, mode, task_file, result_file, out_file])


def run_point(fid: str, p: Point) -> None:
    h = p.h
    expect_one = {"allow": 1, "inbox": 1, "facts": 1, "spool_tasks": 1, "admissions": 1, "experiments": 1,
                  "memory": "intact"}

    def one(label: str, extra: dict | None = None) -> None:
        got = p.counts(label)
        want = dict(expect_one, **(extra or {}))
        h.check(f"{fid}: {label}", all(got[k] == v for k, v in want.items()), got=got, want=want)

    if fid == "F01":
        code, _, _ = p.propose(1, fault="after_outbox_commit")
        h.check("F01: died after the outbox commit (86)", code == 86)
        h.check("F01: task pending in the outbox, spool empty",
                not list((h.spool / "stocks" / "tasks").glob("*.json")) if (h.spool / "stocks").exists() else True)
        h.dispatch("dispatch after restart"); h.consumer("consumer"); h.ingest("ingest")
        one("recovered exactly once")
    elif fid == "F02":
        p.propose(1)
        code, _, _ = h.dispatch("dispatch (fault)", fault="after_spool_write_before_ack")
        h.check("F02: died after the spool write, before the ack (86)", code == 86)
        _c, lines, _ = h.dispatch("dispatch after restart")
        h.check("F02: re-dispatch writes the same bytes (EXISTS)", lines and lines[0].get("spool") == "EXISTS", got=lines)
        h.consumer("consumer"); h.ingest("ingest")
        one("domain saw one request")
    elif fid == "F03":
        p.propose(1); h.dispatch("dispatch"); h.consumer("consumer")
        code, _, _ = h.ingest("ingest (fault)", fault="after_inbox_commit_before_memory")
        h.check("F03: died after the inbox commit, before memory (86)", code == 86)
        one("inbox without fact before recovery", {"facts": 0})
        h.ingest("ingest after restart")
        one("memory completed once")
    elif fid == "F04":
        p.propose(1); h.dispatch("dispatch"); h.consumer("consumer")
        code, _, _ = h.ingest("ingest (fault)", fault="after_memory_commit")
        h.check("F04: died after the memory commit (86)", code == 86)
        _c, lines, _ = h.ingest("ingest after restart")
        h.check("F04: re-ingestion is DUPLICATE", [l.get("action") for l in lines] == ["duplicate"], got=lines)
        one("nothing new")
    elif fid == "F05":
        as_of = now()
        code, _, _ = p.propose(1, as_of=as_of, fault="after_decision_before_episode_commit")
        h.check("F05: died during the decision (86)", code == 86)
        h.check("F05: no episode recorded", p.h.episodes("episodes after death")["episodes"] == [])
        _c, lines, _ = p.propose(1, as_of=as_of)
        clean = Harness(h.out.parent / "F05-reference", h.work.parent / "F05-reference", h.mission, "F05-reference")
        _c2, ref, _ = clean.propose("reference propose", p.props / "1.json", as_of=as_of)
        h.check("F05: same receipt bytes as a run without failure",
                lines[0]["receipt_sha256"] == ref[0]["receipt_sha256"], got=lines[0], reference=ref[0])
        h.dispatch("dispatch"); h.consumer("consumer"); h.ingest("ingest")
        one("one episode, one task")
    elif fid == "F06":
        p.propose(1); h.dispatch("dispatch")
        h.consumer("consumer while CAIN is stopped")
        h.check("F06: result waits in the spool while the CAIN is out", len(h.results()) == 1)
        h.ingest("CAIN back: ingest")
        one("nothing lost")
    elif fid == "F07":
        p.propose(1); h.dispatch("dispatch"); h.ingest("ingest while consumer is out")
        _c, lines, _ = p.propose(2)
        h.check("F07: next proposal waits for the open task (ABSTAIN)", lines[0].get("reason_code") == "OPEN_TASK_PENDING",
                got=lines)
        h.consumer("consumer back"); h.ingest("ingest")
        one("processed once", {"episodes": 2})
    elif fid == "F08":
        p.propose(1); h.dispatch("dispatch")
        code, _, _ = h.consumer("consumer (fault)", fault="after_domain_before_result_write")
        h.check("F08: consumer died after the domain, before the V2 result (86)", code == 86)
        _c, lines, _ = h.consumer("consumer restart")
        h.check("F08: resent through the adapter_api, domain answered DUPLICATE",
                lines and lines[0].get("status") == "DUPLICATE", got=lines)
        h.ingest("ingest")
        (path, result), = h.results()
        h.provenance(result, h.task(result["task_id"]))
        one("one domain result")
    elif fid == "F09":
        p.cycle(1)
        (path, _r), = h.results()
        shutil.copy(path, path.with_name("redelivered-" + path.name))
        _c, lines, _ = h.ingest("ingest redelivery")
        h.check("F09: redelivered result is DUPLICATE", [l.get("action") for l in lines] == ["duplicate", "duplicate"],
                got=lines)
        one("no second fact")
    elif fid == "F10":
        p.cycle(1)
        (first_path, _r), = h.results()
        p.propose(2); h.dispatch("dispatch 2"); h.consumer("consumer 2")
        shutil.copy(first_path, first_path.with_name("00-late-" + first_path.name))
        _c, lines, _ = h.ingest("ingest out of order")
        h.check("F10: late copy of episode 1 is DUPLICATE, episode 2 ingested against its own task",
                sorted(l.get("action") for l in lines) == ["duplicate", "duplicate", "ingested"], got=lines)
        ep = h.episodes("episodes")
        h.check("F10: chain intact", [e["decision"] for e in ep["episodes"]] == ["ALLOW", "ALLOW"])
        one("two tasks, two results", {"allow": 2, "inbox": 2, "facts": 2, "spool_tasks": 2, "admissions": 2,
                                       "experiments": 2})
    elif fid == "F11":
        p.cycle(1)
        (path, result), = h.results()
        p.tamper("wrong-version", result["task_id"], path, path.with_name("wrong-version.json"))
        p.tamper("task-v3", result["task_id"], path, h.spool / "stocks" / "tasks" / "task-v3.json")
        _c, lines, _ = h.ingest("ingest wrong version")
        h.check("F11: research-result/1 rejected VERSION_UNSUPPORTED",
                any(l.get("code") == "VERSION_UNSUPPORTED" for l in lines), got=lines)
        _c, lines, _ = h.consumer("consumer wrong version")
        h.check("F11: research-task/3 rejected VERSION_UNSUPPORTED, nothing executed",
                any(l.get("code") == "VERSION_UNSUPPORTED" for l in lines), got=lines)
        one("nothing executed or ingested", {"spool_tasks": 2})
    elif fid == "F12":
        p.cycle(1)
        (path, result), = h.results()
        p.tamper("other-payload", result["task_id"], path, path.with_name("other-payload.json"))
        _c, lines, _ = h.ingest("ingest other payload")
        h.check("F12: same task, other domain payload: CONFLICT", any(l.get("code") == "CONFLICT" for l in lines),
                got=lines)
        task_file = next((h.spool / "stocks" / "tasks").glob("TASK-*.json"))
        original = task_file.read_bytes()
        task_file.write_bytes(original.replace(b'"producer":"cain"', b'"producer":"cain" '))
        code, lines, _ = h.dispatch("re-dispatch over tampered spool file", resend=True)
        h.check("F12: spool file with other bytes under the same task_id: CONFLICT, nothing overwritten",
                code == 2 and lines[0].get("error") == "CONFLICT" and task_file.read_bytes() != original, got=lines)
        task_file.write_bytes(original)
        one("original kept")
    elif fid == "F13":
        p.cycle(1)
        (path, result), = h.results()
        p.tamper("other-episode", result["task_id"], path, path.with_name("other-episode.json"))
        fixtures = h.mission.parent / "integration-crypto" / "fixtures" / "v2"
        shutil.copy(fixtures / "crypto" / "result-h9.json", path.with_name("crypto.json"))
        shutil.copy(fixtures / "stocks" / "result-h9.json", path.with_name("stocks-h9.json"))
        _c, lines, _ = h.ingest("ingest wrong tasks")
        codes = sorted(l.get("code") for l in lines if l.get("action") == "rejected")
        h.check("F13: valid envelopes of the wrong task/episode/domain rejected",
                codes == ["CORRELATION_MISMATCH", "DOMAIN_MISMATCH", "TASK_NOT_FOUND"], got=codes)
        one("nothing ingested")
    elif fid == "F14":
        p.propose(1); h.dispatch("dispatch")
        _c, lines, _ = h.consumer("consumer with Ops worker crash", domain_fault="ops_worker_crash")
        h.check("F14: domain answered OPS_FAILED_RETRYABLE", lines and lines[0].get("status") == "OPS_FAILED_RETRYABLE",
                got=lines)
        _c, lines, _ = h.ingest("ingest retryable")
        _c, lines, _ = p.propose(2)
        h.check("F14: retryable is not a result; the task stays open (ABSTAIN)",
                lines[0].get("reason_code") == "OPEN_TASK_PENDING", got=lines)
        task_id = p.h.episodes("episodes")["episodes"][0]["task_id"]
        h.cain("retry", "retry", "--domain", "stocks", "--state", h.state, "--spool", h.spool, "--task-id", task_id)
        h.consumer("consumer after retry"); h.ingest("ingest after retry")
        one("one RESULT after the retry", {"episodes": 2, "inbox": 2})
    elif fid == "F15":
        p.propose(1); h.dispatch("dispatch")
        code, _, _ = h.consumer("consumer (fault)", fault="after_domain_before_result_write")
        h.check("F15: consumer died after the domain (86)", code == 86)
        files = [f for f in h.dstate.rglob("research-result.json")]
        h.check("F15: one authoritative result file in the domain", len(files) == 1, files=[str(f) for f in files])
        data = files[0].read_bytes()
        files[0].chmod(0o644)
        files[0].write_bytes(data.replace(b'"capital_permission":false', b'"capital_permission":false '))
        _c, lines, _ = h.consumer("consumer restart over corrupted domain result")
        h.check("F15: domain answered RECONCILIATION_REQUIRED (never repaired in silence)",
                lines and lines[0].get("status") == "RECONCILIATION_REQUIRED", got=lines)
        h.ingest("ingest")
        _c, lines, _ = p.propose(2)
        h.check("F15: CAIN stops the domain (REQUIRE_HUMAN DOMAIN_RECONCILIATION_PENDING)",
                lines[0].get("reason_code") == "DOMAIN_RECONCILIATION_PENDING", got=lines)


def main() -> int:
    mission, work, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    matrix = json.loads((mission / "FAILURE_MATRIX.json").read_text(encoding="utf-8"))
    wanted = sys.argv[4:] or [pt["id"] for pt in matrix["points"]]
    failed = 0
    table = []
    for n, fid in enumerate(wanted, start=1):
        point = Point(fid, work, mission, out, n)
        try:
            run_point(fid, point)
        except Exception as exc:  # noqa: BLE001 - registered as a failed check, never hidden
            point.h.check(f"{fid}: scenario raised {type(exc).__name__}", False, detail=str(exc)[:500])
        failed += point.h.finish() != 0
        table.append({"point": fid, "passed": sum(c["ok"] for c in point.h.checks),
                      "failed": sum(not c["ok"] for c in point.h.checks)})
    (out / "FAILURE_MATRIX_RESULTS.json").write_text(json.dumps({"points": table}, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(table))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
