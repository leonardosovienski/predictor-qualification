"""Fuzz do consumidor do transporte com arquivos de task mutados + custo de memory.verify() em escala.

Roda com o venv do cain (uv run --locked --no-sync python <este arquivo>), a partir de /home/user/cain, com o domínio
substituto de tests/integration/test_orchestration.py. Saída: só contagens e códigos.
"""
import copy
import json
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, "/home/user/cain/tests/integration")
from test_orchestration import AS_OF, StandInDomain, cycle, proposal  # noqa: E402
from research_protocol import v2  # noqa: E402
from research_transport.consumer import Consumer  # noqa: E402
from research_transport.spool import Spool  # noqa: E402
from cain.orchestration.service import Orchestrator  # noqa: E402

import research_transport  # noqa: E402

print("research_transport", research_transport.__file__)
tmp = Path(tempfile.mkdtemp())


class W:
    pass


w = W()
w.domain = StandInDomain()
w.spool = Spool(tmp / "spool")
w.orch = Orchestrator("crypto", tmp / "state")
w.consumer = Consumer("crypto", w.spool, tmp / "consumer.sqlite", w.domain, {"state": "unused"})
w.orch.config["budget"]["max_tasks_total"] = 100000
t0 = time.time()
for i in range(1, 401):
    cycle(w, i, as_of=f"2030-01-01T{(i // 60) % 24:02d}:{i % 60:02d}:00Z", research_id=f"crypto:RESEARCH-{i // 50}")
print("build 400 cycles seconds", round(time.time() - t0, 1))
t0 = time.time()
v = w.orch.store.memory.verify()
print("memory.verify entries", v["entries"], "status", v["status"], "seconds", round(time.time() - t0, 3))

w2 = W()
w2.domain = StandInDomain()
w2.spool = Spool(tmp / "spool2")
w2.orch = Orchestrator("crypto", tmp / "state2")
w2.consumer = Consumer("crypto", w2.spool, tmp / "consumer2.sqlite", w2.domain, {"state": "unused"})
w2.orch.propose(proposal(1), as_of=AS_OF)
w2.orch.dispatch(w2.spool)
(tf,) = w2.spool.task_files("crypto")
base = json.loads(tf.read_bytes())


def muts(obj, path=""):
    if isinstance(obj, dict):
        for k, v in list(obj.items()):
            yield f"{path}.{k}:del", (lambda o, k=k: o.pop(k))
            for tag, r in (("none", None), ("int", 1), ("str", "x"), ("list", []), ("dict", {}), ("huge", "z" * 400000),
                           ("float", 1.5), ("nul", "crypto:\x00")):
                yield f"{path}.{k}:{tag}", (lambda o, k=k, v=r: o.__setitem__(k, v))
            if isinstance(v, (dict, list)):
                for tag, fn in muts(v, f"{path}.{k}"):
                    yield tag, (lambda o, k=k, fn=fn: fn(o[k]))
    elif isinstance(obj, list):
        yield f"{path}[]:append", (lambda o: o.append("x"))


crashes, outcomes, n = [], {}, 0
for tag, fn in muts(base):
    n += 1
    m = copy.deepcopy(base)
    try:
        fn(m)
        raw = json.dumps(m, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    except Exception:
        continue
    name = "TASK-" + ("%032x" % n) + ".json"
    (tf.parent / name).write_bytes(raw)
    try:
        rep = w2.consumer.run_once()
        mine = [r for r in rep if r.get("file") == name]
        key = (mine[0]["action"] + ":" + mine[0].get("code", "")) if mine else "NO-LINE"
        outcomes[key] = outcomes.get(key, 0) + 1
    except BaseException as e:
        crashes.append((tag, type(e).__name__, str(e)[:100]))
    (tf.parent / name).unlink()
print("task mutations", n, json.dumps(outcomes, sort_keys=True))
print("consumer crashes", crashes)
print("domain runs", len(w2.domain.results))
deep = tf.parent / ("TASK-" + "f" * 32 + ".json")
deep.write_bytes(b"[" * 100000 + b"]" * 100000)
try:
    rep = w2.consumer.run_once()
    print("deep nesting:", [(r.get("file"), r["action"], r.get("code")) for r in rep if r.get("file") == deep.name])
except BaseException as e:
    print("deep nesting: CRASH", type(e).__name__)
deep.unlink()
