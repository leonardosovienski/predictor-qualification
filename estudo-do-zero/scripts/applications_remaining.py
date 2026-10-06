import sys,json,ast
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent));import study
p='stocks-predictor';base=Path('C:/STOCKS/stocks-predictor');c=json.loads(study.read(p,study.ROOT/'evidencias'/p/'coverage.json'))
buf=[];index=[];num=0;size=0
for r in c:
 rel=r['path']
 if r.get('depth')=='revisado semanticamente' or not rel.endswith('.py'):continue
 text=study.read(p,base/rel);tree=ast.parse(text);lines=text.splitlines();skip=set()
 for node in ast.walk(tree):
  if isinstance(node,ast.Expr) and isinstance(node.value,ast.Constant) and isinstance(node.value.value,str):skip.update(range(node.lineno,node.end_lineno+1))
 compact=['### '+rel]+[str(i)+': '+line for i,line in enumerate(lines,1) if i not in skip and line.strip() and not line.lstrip().startswith('#')]
 if size and size+len(compact)>850:
  study.save(f'evidencias/{p}/remaining-{num:02}.txt','\n'.join(buf));index.append({'block':num,'files':files});num+=1;buf=[];size=0
 if not size:files=[]
 buf+=compact;size+=len(compact);files.append(rel)
if buf:study.save(f'evidencias/{p}/remaining-{num:02}.txt','\n'.join(buf));index.append({'block':num,'files':files})
study.save(f'evidencias/{p}/remaining-index.json',index);print(json.dumps(index,ensure_ascii=False))
