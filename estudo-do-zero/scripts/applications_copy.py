import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent));import study
p='stocks-predictor';base=Path(r'C:\STOCKS\stocks-predictor');target=study.ROOT/'copias'/p
study.log(p,base,'Preflight estático antes execução: config.yaml config_rj.yaml operations.py operational_store.py external_intelligence.py trials_gate.py',0,'APIs B3/CVM e paths DB/trials possíveis. Teste escolhido importa só execution portfolio validation economic_gate via spec; sem chamar CLI, rede, DB ou trials.',limits='Ambiente herdado não impresso; imports escolhidos stdlib apenas')
if not target.exists():study.run(p,study.ROOT,['git','clone','--no-hardlinks',str(base),str(target)],p+'/copy-clone.txt',timeout=60)
study.run(p,target,['git','rev-parse','HEAD'],p+'/copy-head.txt')
assert (target/'.git').is_dir() and not (target/'.git/objects/info/alternates').exists()
study.log(p,target,'Verificação cópia independente .git diretório sem alternates; arquivos importados lidos por spec',0,'Cópia independente',artifacts=p+'/copy-head.txt')
