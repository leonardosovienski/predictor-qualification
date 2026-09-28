"""integration-stocks: helpers comuns dos cenários (e2e, n-plus-1, isolamento, falhas, soak, Windows).

Adaptado de qualification/integration-crypto/scripts/harness.py (mesma lógica; domínio stocks). Tudo roda pelos
entrypoints instalados no runtime suportado (C2 PROVEN): ``cain`` (venv do CAIN) e
``predictor-research-consumer``/``stocks-research`` (venv do consumidor). Cada comando é um processo novo; o comando,
as variáveis de falha, o exit code, o stdout e o stderr vão sem edição para ``commands.log`` (log bruto, C20). As
conferências do lado do domínio leem os bancos do Stocks só em modo leitura (URI ``mode=ro``).

O ``as_of`` dos modelos de proposta com dados reais é o marcador de FROZEN_VECTORS.json → as_of_marker; ``real_proposal``
o troca pelo data_cutoff do painel do run (REAL_ENV.json) e grava o arquivo efetivo no diretório do cenário.
"""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import subprocess
import time
from datetime import UTC, datetime
from pathlib import Path

DOMAIN = "stocks"
CANARY = "FUTURE_CANARY_STOCKS_INTEGRATION_001"
CANARY_CLOSE = b"987.654321"
FAULT_VARS = ("CAIN_ORCHESTRATION_FAULT", "PREDICTOR_RESEARCH_TRANSPORT_FAULT", "STOCKS_RESEARCH_FAULT",
              "CRIPTO_RESEARCH_FAULT")


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def real_env() -> dict:
    return json.loads(Path(os.environ["REAL_ENV"]).read_text(encoding="utf-8"))


class Harness:
    def __init__(self, out: Path, work: Path, mission: Path, name: str, *, domain: str = DOMAIN):
        self.out, self.work, self.mission, self.name, self.domain = Path(out), Path(work), Path(mission), name, domain
        self.out.mkdir(parents=True, exist_ok=True)
        self.work.mkdir(parents=True, exist_ok=True)
        self.state, self.spool = self.work / "cain-state", self.work / "spool"
        self.ledger, self.dstate = self.work / "consumer" / "ledger.sqlite", self.work / "domain-state"
        prefix = "" if domain == DOMAIN else "CRYPTO_"
        self.bin = {"CAIN_BIN": os.environ["CAIN_BIN"], "CONSUMER_BIN": os.environ[prefix + "CONSUMER_BIN"],
                    "RESEARCH_BIN": os.environ["STOCKS_RESEARCH_BIN" if domain == DOMAIN else "CRIPTO_RESEARCH_BIN"]}
        self.op = {"policy": os.environ[prefix + "OP_POLICY"], "objects": os.environ[prefix + "OP_OBJECTS"]}
        self.domain_fault_var = "STOCKS_RESEARCH_FAULT" if domain == DOMAIN else "CRIPTO_RESEARCH_FAULT"
        self.log = (self.out / "commands.log").open("a", encoding="utf-8")
        self.checks: list[dict] = []
        self.counter = 0

    # ------------------------------------------------------------------ processes
    def run(self, label: str, argv: list, extra_env: dict | None = None) -> tuple[int, list, str]:
        self.counter += 1
        env = {k: v for k, v in os.environ.items() if k not in FAULT_VARS}
        env.update(extra_env or {})
        started = time.time()
        done = subprocess.run([str(a) for a in argv], capture_output=True, env=env, timeout=3600)
        stdout = done.stdout.decode("utf-8", "replace")
        stderr = done.stderr.decode("utf-8", "replace")
        self.log.write(json.dumps({"n": self.counter, "label": label, "at": now(), "seconds": round(time.time() - started, 3),
                                   "argv": [str(a) for a in argv], "fault_env": extra_env or {},
                                   "exit": done.returncode}, ensure_ascii=False) + "\n")
        self.log.write("--- stdout\n" + stdout + "--- stderr\n" + stderr[-20000:] + "--- end\n")
        self.log.flush()
        lines = []
        for line in stdout.splitlines():
            try:
                lines.append(json.loads(line))
            except ValueError:
                lines.append({"raw": line})
        return done.returncode, lines, stdout

    def cain(self, label: str, *args, fault: str | None = None):
        env = {"CAIN_ORCHESTRATION_FAULT": fault} if fault else None
        return self.run(label, [self.bin["CAIN_BIN"], "research", *args], env)

    def real_proposal(self, template: str | Path, target: Path, **request_changes) -> Path:
        """The frozen proposal template with as_of := data_cutoff of this run's real panel (FROZEN_VECTORS rule)."""
        vectors = json.loads((self.mission / "FROZEN_VECTORS.json").read_text(encoding="utf-8"))
        value = json.loads((self.mission / template).read_text(encoding="utf-8"))
        if value["request"].get("as_of") == vectors["as_of_marker"]["marker"]:
            value["request"]["as_of"] = real_env()["data_cutoff"]
        value["request"].update(request_changes)
        target.parent.mkdir(parents=True, exist_ok=True)
        raw = json.dumps(value, ensure_ascii=False, indent=1).encode("utf-8")
        target.write_bytes(raw)
        self.log.write(json.dumps({"effective_proposal": str(target), "template": str(template),
                                   "sha256": sha(raw)}) + "\n")
        return target

    def propose(self, label: str, proposal: str | Path, *, as_of: str | None = None, fault: str | None = None):
        path = Path(proposal)
        path = path if path.is_absolute() else self.mission / path
        return self.cain(label, "propose", "--domain", self.domain, "--state", self.state, "--proposal", path,
                         "--as-of", as_of or now(), fault=fault)

    def dispatch(self, label: str, *, resend: bool = False, fault: str | None = None):
        extra = ["--resend"] if resend else []
        return self.cain(label, "dispatch", "--domain", self.domain, "--state", self.state, "--spool", self.spool,
                         *extra, fault=fault)

    def ingest(self, label: str, *, fault: str | None = None):
        return self.cain(label, "ingest", "--domain", self.domain, "--state", self.state, "--spool", self.spool,
                         fault=fault)

    def episodes(self, label: str) -> dict:
        _code, lines, _ = self.cain(label, "episodes", "--domain", self.domain, "--state", self.state)
        return lines[0]

    def consumer(self, label: str, *, fault: str | None = None, domain_fault: str | None = None):
        env = {}
        if fault:
            env["PREDICTOR_RESEARCH_TRANSPORT_FAULT"] = fault
        if domain_fault:
            env[self.domain_fault_var] = domain_fault
        self.ledger.parent.mkdir(parents=True, exist_ok=True)
        return self.run(label, [self.bin["CONSUMER_BIN"], "--domain", self.domain, "--spool", self.spool,
                                "--ledger", self.ledger, "--state", self.dstate, "--policy", self.op["policy"],
                                "--objects", self.op["objects"]], env or None)

    def show(self, label: str, request_id: str) -> tuple[int, dict]:
        code, lines, _ = self.run(label, [self.bin["RESEARCH_BIN"], "--state", self.dstate, "show", request_id])
        return code, lines[0] if lines else {}

    # ------------------------------------------------------------------ evidence
    def check(self, name: str, ok: bool, **detail) -> bool:
        self.checks.append({"check": name, "ok": bool(ok), **detail})
        return bool(ok)

    def ro(self, path: Path) -> sqlite3.Connection:
        db = sqlite3.connect(Path(path).resolve().as_uri() + "?mode=ro", uri=True)
        db.row_factory = sqlite3.Row
        return db

    def results(self) -> list[tuple[Path, dict]]:
        out = []
        for path in sorted((self.spool / self.domain / "results").glob("TASK-*.json")):
            out.append((path, json.loads(path.read_bytes())))
        return out

    def task(self, task_id: str) -> dict:
        path = self.spool / self.domain / "tasks" / (task_id.split(":", 1)[1] + ".json")
        return json.loads(path.read_bytes())

    def provenance(self, result: dict, task: dict) -> None:
        """Every RESULT/DUPLICATE: envelope ↔ authoritative re-read ↔ admission ↔ journal ↔ task ↔ adapter."""
        payload = json.loads(result["result"]["payload_canonical"])
        rid = result["request_id"]
        code, shown = self.show(f"show {rid}", rid)
        self.check(f"{rid}: payload byte-identical to `stocks-research show` (new process)",
                   code == 0 and shown.get("result_sha256") == result["result"]["payload_sha256"],
                   payload_sha256=result["result"]["payload_sha256"], show_sha256=shown.get("result_sha256"))
        self.check(f"{rid}: request content hash of the domain == task payload_sha256 (C24.3 d)",
                   payload["provenance"]["request_content_hash"] == task["payload_sha256"],
                   request_content_hash=payload["provenance"]["request_content_hash"])
        self.check(f"{rid}: client_ref echoed unchanged", result["client_ref"] == task["payload"]["client_ref"])
        with self.ro(self.dstate / "admission.sqlite") as db:
            adm = db.execute("SELECT admission_id, policy_hash, content_hash FROM admissions WHERE request_id=? AND "
                             "decision='ACCEPTED'", (rid,)).fetchall()
        self.check(f"{rid}: one ACCEPTED admission linked to the result", len(adm) == 1
                   and adm[0]["admission_id"] == payload["admission_id"]
                   and adm[0]["policy_hash"] == payload["provenance"]["admission_policy_hash"]
                   and adm[0]["content_hash"] == task["payload_sha256"], admissions=len(adm))
        with self.ro(self.dstate / "x" / "journal.sqlite") as db:
            exp = db.execute("SELECT experiment_id, state, ops_run_id FROM experiments WHERE request_id=?",
                             (rid,)).fetchall()
            attempts = db.execute("SELECT attempt_id FROM attempts WHERE experiment_id=?",
                                  (payload["experiment_id"],)).fetchall()
        self.check(f"{rid}: one COMPLETED experiment, Ops run and attempts linked", len(exp) == 1
                   and exp[0]["experiment_id"] == payload["experiment_id"] and exp[0]["state"] == "COMPLETED"
                   and exp[0]["ops_run_id"] == payload["ops_facts"]["ops_run_id"]
                   and sorted(a["attempt_id"] for a in attempts) == sorted(payload["ops_facts"]["attempt_ids"]),
                   experiments=len(exp))
        self.check(f"{rid}: adapter identity is the installed domain distribution",
                   result["adapter"]["distribution"] == "stocks-predictor"
                   and result["adapter"]["module"] == "stocks_predictor.adapters.research_v2",
                   adapter=result["adapter"])
        self.check(f"{rid}: capital_permission false in envelope and payload",
                   result["result"]["capital_permission"] is False and payload["capital_permission"] is False)

    def no_canary(self, label: str) -> None:
        mem = (self.state / "memory.sqlite").read_bytes()
        self.check(f"{label}: canary token absent from CAIN memory", CANARY.encode() not in mem)
        self.check(f"{label}: canary price absent from CAIN memory", CANARY_CLOSE not in mem)
        env = real_env()
        for marker in env.get("canary_markers", []):
            self.check(f"{label}: post-cutoff instant {marker} absent from CAIN memory", marker.encode() not in mem)

    def finish(self, extra: dict | None = None) -> int:
        summary = {"scenario": self.name, "finished_at": now(), "checks": self.checks,
                   "passed": sum(c["ok"] for c in self.checks), "failed": sum(not c["ok"] for c in self.checks),
                   **(extra or {})}
        (self.out / "SUMMARY.json").write_text(json.dumps(summary, indent=1, ensure_ascii=False) + "\n",
                                               encoding="utf-8")
        print(json.dumps({k: summary[k] for k in ("scenario", "passed", "failed")}))
        for c in self.checks:
            if not c["ok"]:
                print("FAILED:", json.dumps(c, ensure_ascii=False))
        return 0 if summary["failed"] == 0 else 1
