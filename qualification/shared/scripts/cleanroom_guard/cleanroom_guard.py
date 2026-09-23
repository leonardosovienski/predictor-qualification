"""Plugin do pytest do cleanroom-baseline (SHARED-002).

Não altera a suíte: ao fim da sessão, grava em $CLEANROOM_GUARD_OUT a origem de
todo módulo do stack importado ($CLEANROOM_GUARD_MODULES, top-level) e quantos
vieram de fora do site-packages do venv ($CLEANROOM_GUARD_SITE), o que indicaria
teste exercitando checkout em vez da wheel instalada.
"""

from __future__ import annotations

import json
import os
import sys


def pytest_sessionfinish(session, exitstatus):  # noqa: ARG001
    tops = {m for m in os.environ.get("CLEANROOM_GUARD_MODULES", "").split(",") if m}
    site = os.environ.get("CLEANROOM_GUARD_SITE", "")
    seen, outside = {}, []
    for name, module in list(sys.modules.items()):
        if name.split(".", 1)[0] not in tops:
            continue
        path = getattr(module, "__file__", None)
        if path is None:
            continue
        seen[name] = path
        if not (site and os.path.realpath(path).startswith(os.path.realpath(site))):
            outside.append({"module": name, "file": path})
    result = {
        "site_packages": site,
        "stack_modules_imported": len(seen),
        "top_levels_imported": sorted({n.split(".", 1)[0] for n in seen}),
        "outside_site_packages": sorted(outside, key=lambda x: x["module"]),
        "exitstatus": int(exitstatus),
    }
    target = os.environ.get("CLEANROOM_GUARD_OUT")
    if target:
        with open(target, "w", encoding="utf-8") as fh:
            json.dump(result, fh, indent=2)
