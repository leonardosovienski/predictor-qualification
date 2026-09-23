"""SHARED-003: sonda do timeout do predictor_ops (run_job), uma execução por chamada.

Roda no interpretador do ambiente sob teste (venv com a wheel 4.2.1 ou checkout do Ops).
Nada de mock: chama predictor_ops.run_job de verdade e imprime um JSON por linha.

Cenários:
  test-exact   o cenário de tests_v2/test_runner.py::test_timeout_and_truncation
               (print('x'*1000); sleep(5); timeout 0.2 s; max_output_bytes 20)
  startup      latência de partida do interpretador filho: Popen → primeiro byte
               (mesmo comando e flags de criação do run_job, sem job object), em s
  real-tree    job real: o filho cria um neto que grava o próprio PID e trava; timeout 3 s;
               confere se filho e neto morreram e se a saída foi truncada
  a-b-delay    intervenção B: mesmo cenário, mesmo prazo de 0.2 s, mas o filho parte
               com `python -S -E` (sem site/.pth e sem variáveis PYTHON*), o que só
               encurta a partida do interpretador; o run_job é o mesmo

Uso: python ops_timeout_probe.py <cenário> <tmpdir>
"""

from __future__ import annotations

import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path

import predictor_ops
from predictor_ops import JobConfig, run_job
from predictor_ops.models import RuntimeConfig


def alive(pid: int) -> bool:
    if os.name == "nt":
        raw = subprocess.run(["tasklist", "/FI", f"PID eq {pid}", "/NH", "/FO", "CSV"], capture_output=True).stdout
        return f'"{pid}"' in raw.decode("ascii", errors="replace")
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def job(tmp: Path, code: str, **kw) -> JobConfig:
    return JobConfig(id=kw.pop("id", "probe"), command=[sys.executable, *kw.pop("flags", []), "-c", code],
                     runtime=RuntimeConfig(root=tmp / "runtime"), **kw)


def summary(result) -> dict:
    rec = result.record
    return {"exit_code": result.exit_code, "run_status": str(result.run_status.value),
            "termination": rec.get("termination"), "output_bytes": rec["output"]["bytes"],
            "output_truncated": rec["output"]["truncated"], "duration_ms": rec.get("duration_ms"),
            "error": rec.get("error")}


def main() -> None:
    scenario, tmp = sys.argv[1], Path(sys.argv[2])
    tmp.mkdir(parents=True, exist_ok=True)
    env = {"python": sys.version.split()[0], "platform": platform.platform(),
           "predictor_ops_file": predictor_ops.__file__}
    out: dict = {"scenario": scenario, "env": env}
    if scenario == "test-exact":
        r = run_job(job(tmp, "import time; print('x'*1000, flush=True); time.sleep(5)",
                        timeout_seconds=0.2, max_output_bytes=20))
        s = summary(r)
        s["test_assertions_pass"] = (s["exit_code"] == 124 and s["run_status"] == "FAILED"
                                     and (s["termination"] or {}).get("reason") == "timeout"
                                     and s["output_truncated"] and s["output_bytes"] == 20)
        out.update(s)
    elif scenario == "a-b-delay":
        r = run_job(job(tmp, "import time; print('x'*1000, flush=True); time.sleep(5)",
                        flags=["-S", "-E"], timeout_seconds=0.2, max_output_bytes=20))
        s = summary(r)
        s["test_assertions_pass"] = (s["exit_code"] == 124 and (s["termination"] or {}).get("reason") == "timeout"
                                     and s["output_truncated"] and s["output_bytes"] == 20)
        out.update(s)
    elif scenario == "startup":
        flags = {}
        if os.name == "nt":
            flags["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP | getattr(subprocess, "CREATE_NO_WINDOW", 0)
        else:
            flags["start_new_session"] = True
        t0 = time.monotonic()
        p = subprocess.Popen([sys.executable, "-c", "import time; print('x'*1000, flush=True); time.sleep(5)"],
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT, **flags)
        first = p.stdout.read(1)
        t1 = time.monotonic()
        p.kill()
        p.wait()
        out.update({"first_byte_seconds": round(t1 - t0, 4), "got_byte": bool(first)})
    elif scenario in ("slow-start", "ample"):
        # A/B causal de H2: a saída só existe se o filho escrever antes do prazo.
        # slow-start: mesmo prazo de 0.2 s, filho importa módulos pesados antes do print.
        # ample: mesmo filho do teste, prazo de 3 s (diagnóstico; o teste não é alterado).
        if scenario == "slow-start":
            code = ("import asyncio, email.mime.multipart, http.server, xml.dom.minidom, decimal, "
                    "unittest, argparse, json, sqlite3; print('x'*1000, flush=True); import time; time.sleep(5)")
            timeout = 0.2
        else:
            code = "import time; print('x'*1000, flush=True); time.sleep(5)"
            timeout = 3
        r = run_job(job(tmp, code, id=f"probe-{scenario}", timeout_seconds=timeout, max_output_bytes=20))
        s = summary(r)
        s["timeout_seconds"] = timeout
        s["killed_by_timeout"] = s["exit_code"] == 124 and (s["termination"] or {}).get("reason") == "timeout"
        s["test_assertions_pass"] = s["killed_by_timeout"] and s["output_truncated"] and s["output_bytes"] == 20
        out.update(s)
    elif scenario == "real-tree":
        pidfile = tmp / "grandchild.pid"
        grandchild = tmp / "grandchild.py"
        grandchild.write_text(
            "import os, sys, time\n"
            "open(sys.argv[1], 'w').write(str(os.getpid()))\n"
            "time.sleep(120)\n", encoding="utf-8")
        parent = tmp / "parent.py"
        parent.write_text(
            "import subprocess, sys, time\n"
            "subprocess.Popen([sys.executable, sys.argv[1], sys.argv[2]])\n"
            "print('y' * 5000, flush=True)\n"
            "time.sleep(120)\n", encoding="utf-8")
        cfg = JobConfig(id="probe-tree", command=[sys.executable, str(parent), str(grandchild), str(pidfile)],
                        runtime=RuntimeConfig(root=tmp / "runtime"), timeout_seconds=3, max_output_bytes=100)
        r = run_job(cfg)
        time.sleep(1)
        s = summary(r)
        child_pid = r.record.get("pid")
        grand = int(pidfile.read_text()) if pidfile.exists() else None
        s.update({"child_pid": child_pid, "child_alive_after": alive(child_pid) if child_pid else None,
                  "grandchild_pid": grand, "grandchild_alive_after": alive(grand) if grand else None})
        s["real_job_killed_tree_and_truncated"] = (s["exit_code"] == 124 and s["child_alive_after"] is False
                                                    and s["grandchild_alive_after"] is False
                                                    and s["output_truncated"] and s["output_bytes"] == 100)
        out.update(s)
    else:
        raise SystemExit(f"cenário desconhecido: {scenario}")
    print(json.dumps(out, sort_keys=True))


if __name__ == "__main__":
    main()
