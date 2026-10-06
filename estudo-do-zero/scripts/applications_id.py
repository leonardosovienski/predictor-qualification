import sys,json,tomllib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent));import study
for p in ['cain','stocks-predictor']:
 b=json.loads(study.read(p,study.ROOT/'evidencias'/p/'baseline.json'));print(p,b['head'],b['status'][:200])
 study.save('evidencias/'+p+'/components.json',[])
