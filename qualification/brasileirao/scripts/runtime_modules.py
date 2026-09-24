"""Trace em runtime: executa um console script instalado no mesmo processo e lista os
módulos carregados (sys.modules) ao final, com o arquivo de origem de cada pacote do stack.

Uso: python runtime_modules.py <dist> <script> [args...]
Imprime JSON: script, argv, exit, módulos brasileirao_predictor.*, pacotes externos de interesse."""
import json
import sys
from importlib.metadata import entry_points

dist, script, *argv = sys.argv[1:]
ep = next(e for e in entry_points(group="console_scripts") if e.name == script and e.dist.name == dist)
sys.argv = [script, *argv]
code = 0
try:
    ep.load()()
except SystemExit as exc:
    code = exc.code
INTEREST = ("research_protocol", "research_snapshot", "research_bundle", "cain", "ecosystem",
            "predictor_core", "predictor_ops", "brasileirao_predictor", "brasileirao_scripts")
mods = sorted(m for m in sys.modules if m.split(".")[0] in INTEREST)
origins = {top: getattr(sys.modules.get(top), "__file__", None) for top in INTEREST if top in sys.modules}
print("\n" + json.dumps({"script": script, "argv": argv, "exit": code, "origins": origins,
                          "research_components_loaded": [m for m in mods if m.startswith("brasileirao_predictor.research_runtime")],
                          "modules": mods}, indent=1))
