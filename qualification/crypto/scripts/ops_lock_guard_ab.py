"""SHARED-005: A/B determinístico do _mutation_guard do predictor_ops no Windows.

Processo "holder" abre o arquivo de guarda e trava o byte 0 (msvcrt.locking), como o
_mutation_guard faz depois de inicializar. O processo principal entra no
predictor_ops.runtime._mutation_guard real sobre o mesmo arquivo:
  A (guarda vazia):        o código escreve/flush no byte 0 travado → PermissionError esperado
  B (guarda inicializada): o código não escreve; espera no laço de lock → entra depois que o holder solta
Uso: python ops_lock_guard_ab.py <tmpdir>   (só Windows)
"""

from __future__ import annotations

import json
import multiprocessing
import sys
import time
from pathlib import Path


def holder(path: str, ready, release) -> None:
    import msvcrt

    with open(path, "a+b") as handle:
        handle.seek(0)
        msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
        ready.set()
        release.wait(10)
        handle.seek(0)
        msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)


def case(tmp: Path, name: str, initialized: bool) -> dict:
    import predictor_ops
    from predictor_ops.runtime import _mutation_guard

    guard = tmp / name / ".mutation.guard"
    guard.parent.mkdir(parents=True, exist_ok=True)
    guard.write_bytes(b"0" if initialized else b"")
    ctx = multiprocessing.get_context("spawn")
    ready, release = ctx.Event(), ctx.Event()
    proc = ctx.Process(target=holder, args=(str(guard), ready, release))
    proc.start()
    ready.wait(10)
    outcome = {"case": name, "guard_initialized": initialized, "predictor_ops_file": predictor_ops.__file__}
    started = time.monotonic()
    try:
        # solta o holder daqui a 0.5 s em paralelo, para o caso B conseguir entrar
        import threading

        threading.Timer(0.5, release.set).start()
        with _mutation_guard(guard):
            outcome["entered"] = True
    except Exception as exc:  # noqa: BLE001 - o tipo da exceção é a evidência
        outcome["entered"] = False
        outcome["exception"] = f"{type(exc).__name__}: {exc}"
    outcome["seconds"] = round(time.monotonic() - started, 3)
    release.set()
    proc.join(10)
    return outcome


def main() -> None:
    if sys.platform != "win32":
        raise SystemExit("só Windows")
    tmp = Path(sys.argv[1])
    for name, initialized in (("A_empty_guard", False), ("B_initialized_guard", True)):
        print(json.dumps(case(tmp, name, initialized), sort_keys=True))


if __name__ == "__main__":
    main()
