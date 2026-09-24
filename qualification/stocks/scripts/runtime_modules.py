"""Trace em runtime: executa um console script instalado (ou `-m módulo`) no mesmo processo e
lista os módulos carregados (sys.modules) ao final, com o arquivo de origem de cada pacote do stack.

Uso: python runtime_modules.py <dist> <script> [args...]
     python runtime_modules.py -m <módulo> [args...]
Imprime JSON: script, argv, exit, origens, componentes do circuito de pesquisa carregados, módulos.
"""
import json
import runpy
import sys
from importlib.metadata import entry_points

first, *rest = sys.argv[1:]
code = 0
if first == "-m":
    module, *argv = rest
    script = f"-m {module}"
    sys.argv = [module, *argv]
    try:
        runpy.run_module(module, run_name="__main__", alter_sys=True)
    except SystemExit as exc:
        code = exc.code
else:
    dist, script, *argv = rest
    ep = next(e for e in entry_points(group="console_scripts") if e.name == script and e.dist.name == dist)
    sys.argv = [script, *argv]
    try:
        code = ep.load()()
    except SystemExit as exc:
        code = exc.code
INTEREST = ("research_protocol", "research_snapshot", "research_bundle", "cain", "ecosystem",
            "predictor_core", "predictor_ops", "stocks_predictor")
mods = sorted(m for m in sys.modules if m.split(".")[0] in INTEREST)
origins = {top: getattr(sys.modules.get(top), "__file__", None) for top in INTEREST if top in sys.modules}
print("\n" + json.dumps({"script": script, "argv": argv, "exit": code, "origins": origins,
                          "research_components_loaded": [m for m in mods if m.startswith("stocks_predictor.research_")],
                          "modules": mods}, indent=1))
