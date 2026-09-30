import sys,re,json,ast
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent));import study
projects={'cain':(Path(r'C:\CAIN\projeto'),['src/cain/research/service.py','src/cain/research/bundles.py','src/cain/research/historian.py','src/cain/research/grounding.py','src/cain/api.py','src/cain/research/api.py','src/cain/persistence/adapters/sqlite.py','src/cain/identity/__init__.py','src/cain/workspace.py','src/cain/settings.py','src/cain/search/__init__.py','.github/workflows/ci.yml']), 'stocks-predictor':(Path(r'C:\STOCKS\stocks-predictor'),['main.py','stocks_predictor/db.py','stocks_predictor/backtest.py','stocks_predictor/factor.py','stocks_predictor/cvm_pit.py','stocks_predictor/external_intelligence.py','stocks_predictor/source_catalog.py','stocks_predictor/simulation.py','stocks_predictor/profit_validation.py','stocks_predictor/temporal_evidence.py','stocks_predictor/diagnostics.py','.github/workflows/ci.yml','tools/verify_operational_evidence.py','uv.lock'])}
for project,(base,files) in projects.items():
 output=[]
 for rel in files:
  text=study.read(project,base/rel);lines=text.splitlines();out=['### '+rel]
  for i,line in enumerate(lines):
   if re.search(r'^\s*(?:async )?def |^\s*class |CREATE TABLE|CREATE TRIGGER|@(?:app|router)\.|capital_|BLOCKED|COMPROVADA|NO_GO|uv sync|pytest|ruff|pyright|version =|name = "predictor|wheel|schema|mode=ro|token|auth|cors|Origin|Host|return.*status|env\(|getenv|urlopen',line):
    out.append(f'{i+1}: '+line)
    if rel.endswith('.py') and re.match(r'^def |^class ',line):out.extend(f'{j+1}: {lines[j]}' for j in range(i+1,min(i+5,len(lines))))
  output.append('\n'.join(out))
 study.save('evidencias/'+project+'/central-extract.txt','\n\n'.join(output));print('\n\n'.join(output))
