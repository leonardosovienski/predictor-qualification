"""integration-brasileirao: helpers comuns dos cenários (e2e, contract-revalidation, n-plus-1, isolamento, falhas, soak,
Windows).

Adaptado de qualification/integration-stocks/scripts/harness.py (mesma lógica; domínio brasileirao). Tudo roda pelos
entrypoints instalados no runtime suportado (C2 PROVEN): ``cain`` (venv do CAIN) e
``predictor-research-consumer``/``brasileirao-research`` (venv do consumidor). Cada comando é um processo novo.

Dado real privado (D-11, D-16, D-25): o estado do CAIN, o spool e o estado do domínio ficam no diretório de trabalho
PRIVADO (<work>, em ~/predictors/runtime/integration-brasileirao/priv/…). Cada comando grava:
  * no log privado <work>/commands.private.log: argv, exit, stdout e stderr sem edição;
  * no log público <out>/commands.log (RAW_LOGS): argv, exit, duração, sha256 e tamanho do stdout/stderr, e o stdout
    só dos comandos do CAIN (IDs, estados, hashes, receipts) e do consumidor com o campo livre ``reason`` trocado pelo
    sha256; o stdout do `brasileirao-research` (payload por jogo) nunca vai para o log público.
As conferências do lado do domínio leem os bancos do Brasileirão só em modo leitura (URI ``mode=ro``) e registram
só booleanos, contagens, IDs e hashes. Toda saída pública passa pelo no_data_rows_check antes de virar evidência.
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

DOMAIN = "brasileirao"
CANARY = "FUTURE_CANARY_BR_INTEGRATION_001"
FAULT_VARS = ("CAIN_ORCHESTRATION_FAULT", "PREDICTOR_RESEARCH_TRANSPORT_FAULT", "BRASILEIRAO_RESEARCH_FAULT",
              "STOCKS_RESEARCH_FAULT", "CRIPTO_RESEARCH_FAULT")
PREFIX = {"brasileirao": "", "crypto": "CRYPTO_", "stocks": "STOCKS_"}
RESEARCH_BIN = {"brasileirao": "BRASILEIRAO_RESEARCH_BIN", "crypto": "CRIPTO_RESEARCH_BIN",
                "stocks": "STOCKS_RESEARCH_BIN"}
DOMAIN_FAULT = {"brasileirao": "BRASILEIRAO_RESEARCH_FAULT", "crypto": "CRIPTO_RESEARCH_FAULT",
                "stocks": "STOCKS_RESEARCH_FAULT"}


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def real_env() -> dict:
    return json.loads(Path(os.environ["REAL_ENV"]).read_text(encoding="utf-8"))


def redact(value):
    """Public copy of a consumer/CAIN JSON line: free-text ``reason``/``detail`` of the domain replaced by its sha256."""
    if isinstance(value, dict):
        return {k: ({"sha256": sha(str(v).encode("utf-8"))} if k in ("reason", "stderr") else redact(v))
                for k, v in value.items()}
    if isinstance(value, list):
        return [redact(v) for v in value]
    return value


class Harness:
    def __init__(self, out: Path, work: Path, mission: Path, name: str, *, domain: str = DOMAIN):
        self.out, self.work, self.mission, self.name, self.domain = Path(out), Path(work), Path(mission), name, domain
        self.out.mkdir(parents=True, exist_ok=True)
        self.work.mkdir(parents=True, exist_ok=True)
        self.state, self.spool = self.work / "cain-state", self.work / "spool"
        self.ledger = self.work / f"consumer-{domain}" / "ledger.sqlite"
        self.dstate = self.work / f"domain-state-{domain}"
        prefix = PREFIX[domain]
        self.bin = {"CAIN_BIN": os.environ["CAIN_BIN"], "CONSUMER_BIN": os.environ[prefix + "CONSUMER_BIN"],
                    "RESEARCH_BIN": os.environ[RESEARCH_BIN[domain]]}
        self.op = {"policy": os.environ[prefix + "OP_POLICY"], "objects": os.environ[prefix + "OP_OBJECTS"]}
        self.domain_fault_var = DOMAIN_FAULT[domain]
        self.log = (self.out / "commands.log").open("a", encoding="utf-8")
        self.private = (self.work / "commands.private.log").open("a", encoding="utf-8")
        self.checks: list[dict] = []
        self.counter = [0]  # shared with for_domain(): one numbering per public log

    def for_domain(self, domain: str) -> "Harness":
        """Same CAIN state and spool, another domain's consumer (runtime integrado)."""
        other = Harness.__new__(Harness)
        other.__dict__.update(self.__dict__)
        other.domain = domain
        other.ledger = self.work / f"consumer-{domain}" / "ledger.sqlite"
        other.dstate = self.work / f"domain-state-{domain}"
        prefix = PREFIX[domain]
        other.bin = {"CAIN_BIN": os.environ["CAIN_BIN"], "CONSUMER_BIN": os.environ[prefix + "CONSUMER_BIN"],
                     "RESEARCH_BIN": os.environ[RESEARCH_BIN[domain]]}
        other.op = {"policy": os.environ[prefix + "OP_POLICY"], "objects": os.environ[prefix + "OP_OBJECTS"]}
        other.domain_fault_var = DOMAIN_FAULT[domain]
        return other

    # ------------------------------------------------------------------ processes
    def run(self, label: str, argv: list, extra_env: dict | None = None, *, public_stdout: str = "none"):
        """public_stdout: 'full' (CAIN), 'redacted' (consumidor: reason → sha256) ou 'none' (domínio)."""
        self.counter[0] += 1
        env = {k: v for k, v in os.environ.items() if k not in FAULT_VARS}
        env.update(extra_env or {})
        started = time.time()
        done = subprocess.run([str(a) for a in argv], capture_output=True, env=env, timeout=3600)
        stdout = done.stdout.decode("utf-8", "replace")
        stderr = done.stderr.decode("utf-8", "replace")
        head = {"n": self.counter[0], "domain": self.domain, "label": label, "at": now(), "seconds": round(time.time() - started, 3),
                "argv": [str(a) for a in argv], "fault_env": extra_env or {}, "exit": done.returncode,
                "stdout_sha256": sha(done.stdout), "stdout_bytes": len(done.stdout),
                "stderr_sha256": sha(done.stderr), "stderr_bytes": len(done.stderr)}
        self.private.write(json.dumps(head, ensure_ascii=False) + "\n--- stdout\n" + stdout + "--- stderr\n"
                           + stderr[-20000:] + "--- end\n")
        self.private.flush()
        lines = []
        for line in stdout.splitlines():
            try:
                lines.append(json.loads(line))
            except ValueError:
                lines.append({"raw": line})
        if public_stdout == "full":
            shown = stdout
        elif public_stdout == "redacted":
            shown = "".join(json.dumps(redact(v), ensure_ascii=False, sort_keys=True) + "\n" for v in lines)
        else:
            shown = "(stdout do domínio só no log privado)\n"
        self.log.write(json.dumps(head, ensure_ascii=False) + "\n--- stdout\n" + shown + "--- end\n")
        self.log.flush()
        return done.returncode, lines, stdout

    def cain(self, label: str, *args, fault: str | None = None):
        env = {"CAIN_ORCHESTRATION_FAULT": fault} if fault else None
        return self.run(label, [self.bin["CAIN_BIN"], "research", *args], env, public_stdout="full")

    def proposal_path(self, template: str | Path, dest: Path | None = None, proposal_id: str | None = None, /,
                      **request_changes) -> Path:
        """The frozen proposal (path relative to the mission); with changes, an effective copy logged by sha256, with
        its own proposal_id when given (one CAIN state records each proposal_id once). The paths are positional-only,
        so request fields (e.g. the Brasileirão ``target``) never collide with them."""
        source = self.mission / template
        if not request_changes and not proposal_id:
            return source
        value = json.loads(source.read_text(encoding="utf-8"))
        value["request"].update(request_changes)
        if proposal_id:
            value["proposal_id"] = proposal_id
        dest = dest or self.work / "effective" / Path(template).name
        dest.parent.mkdir(parents=True, exist_ok=True)
        raw = json.dumps(value, ensure_ascii=False, indent=1).encode("utf-8")
        dest.write_bytes(raw)
        self.log.write(json.dumps({"effective_proposal": str(dest), "template": str(template), "sha256": sha(raw),
                                   "changes": sorted(request_changes)}) + "\n")
        return dest

    def integrated_proposal(self, domain: str, template: str, dest: Path, proposal_id: str | None = None, /,
                            **request_changes) -> Path:
        """A frozen proposal of the crypto/stocks integration (path relative to qualification/integration-<domain>),
        with the stocks as_of marker replaced by the data_cutoff of this run's stocks panel (their FROZEN_VECTORS
        rule) and, when given, its own proposal_id (one CAIN state records each proposal_id once); the effective copy
        is logged by sha256."""
        other = self.mission.parent / f"integration-{domain}"
        value = json.loads((other / template).read_text(encoding="utf-8"))
        if proposal_id:
            value["proposal_id"] = proposal_id
        marker = json.loads((other / "FROZEN_VECTORS.json").read_text(encoding="utf-8")).get("as_of_marker")
        if marker and value["request"].get("as_of") == marker["marker"]:
            value["request"]["as_of"] = json.loads(Path(os.environ["STOCKS_REAL_ENV"]).read_text())["data_cutoff"]
        value["request"].update(request_changes)
        dest.parent.mkdir(parents=True, exist_ok=True)
        raw = json.dumps(value, ensure_ascii=False, indent=1).encode("utf-8")
        dest.write_bytes(raw)
        self.log.write(json.dumps({"effective_proposal": str(dest), "template": f"integration-{domain}/{template}",
                                   "sha256": sha(raw), "changes": sorted(request_changes)}) + "\n")
        return dest

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
                                "--objects", self.op["objects"]], env or None, public_stdout="redacted")

    def show(self, label: str, request_id: str) -> tuple[int, dict]:
        code, lines, _ = self.run(label, [self.bin["RESEARCH_BIN"], "--state", self.dstate, "show", request_id])
        return code, lines[0] if lines else {}

    # ------------------------------------------------------------------ evidence
    def check(self, name: str, ok: bool, **detail) -> bool:
        # public SUMMARY.json: free-text reason/stderr of the domain replaced by its sha256, as in the public log
        self.checks.append({"check": name, "ok": bool(ok), **redact(detail)})
        return bool(ok)

    def ro(self, path: Path) -> sqlite3.Connection:
        db = sqlite3.connect(Path(path).resolve().as_uri() + "?mode=ro", uri=True)
        db.row_factory = sqlite3.Row
        return db

    def results(self, domain: str | None = None) -> list[tuple[Path, dict]]:
        out = []
        for path in sorted((self.spool / (domain or self.domain) / "results").glob("TASK-*.json")):
            out.append((path, json.loads(path.read_bytes())))
        return out

    def task(self, task_id: str, domain: str | None = None) -> dict:
        path = self.spool / (domain or self.domain) / "tasks" / (task_id.split(":", 1)[1] + ".json")
        return json.loads(path.read_bytes())

    def provenance(self, result: dict, task: dict) -> None:
        """Every RESULT/DUPLICATE: envelope ↔ authoritative re-read ↔ admission ↔ journal ↔ task ↔ adapter."""
        payload = json.loads(result["result"]["payload_canonical"])
        rid = result["request_id"]
        code, shown = self.show(f"show {rid}", rid)
        self.check(f"{rid}: payload byte-identical to `brasileirao-research show` (new process)",
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
                   result["adapter"]["distribution"] == "brasileirao-predictor"
                   and result["adapter"]["module"] == "brasileirao_predictor.adapters.research_v2",
                   adapter=result["adapter"])
        self.check(f"{rid}: capital_permission false in envelope and payload",
                   result["result"]["capital_permission"] is False and payload["capital_permission"] is False)

    def no_canary(self, label: str) -> None:
        mem = (self.state / "memory.sqlite").read_bytes()
        for marker in real_env()["canary_markers"]:
            self.check(f"{label}: canary marker absent from CAIN memory (retrieval source)",
                       marker.encode() not in mem, marker_sha256=sha(marker.encode()))
        every = b"".join(p.read_bytes() for p in self.state.rglob("*") if p.is_file())
        self.check(f"{label}: canary token absent from every CAIN state file (memory, episodes, outbox, inbox)",
                   CANARY.encode() not in every)
        public = b"".join(p.read_bytes() for p in self.out.rglob("*") if p.is_file())
        self.check(f"{label}: canary token absent from the public outputs of this scenario",
                   CANARY.encode() not in public)

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
