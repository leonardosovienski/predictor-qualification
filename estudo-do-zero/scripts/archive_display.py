import sys,json,difflib,hashlib
from pathlib import Path
import study
sys.stdout.reconfigure(encoding="utf-8")
root=Path(r'C:\CRIPTO\pesquisa-20260909')
assignment=int(sys.argv[1]); start=int(sys.argv[2]); end=int(sys.argv[3])
rows=json.loads(study.read('cripto-predictor',study.ROOT/f'evidencias/cripto-predictor/archive-derivation-assignment-{assignment}.json'))
for i,x in enumerate(rows[start:end],start):
 print(f'\n=== {i} {x["path"]} BASE {x["base"]} CHANGED {x.get("changed_lines", x.get("lines",0))} ===')
 new=study.read('cripto-predictor',root/x['path']).replace('\r\n','\n').replace('\r','\n').splitlines()
 if x['base']:
  old=study.read('cripto-predictor',root/x['base']).replace('\r\n','\n').replace('\r','\n').splitlines()
  print('\n'.join(difflib.unified_diff(old,new,fromfile=x['base'],tofile=x['path'],n=3,lineterm='')))
 else:
  print('\n'.join(f'{j+1}: {t}' for j,t in enumerate(new)))
