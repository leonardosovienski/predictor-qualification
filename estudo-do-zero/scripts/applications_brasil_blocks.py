import sys,json,ast
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent));import study
p='brasileirao-predictor';d=study.ROOT/'evidencias'/p
c=json.loads(study.read(p,d/'coverage.json'));b=json.loads(study.read(p,d/'baseline.json'));root=Path(b['path'])
selected=[r for r in c['files'] if not r['semantic_integral_certified'] and r['path'].endswith('.py') and (r['path'].startswith('brasileirao_predictor/') or r['path'].startswith('tests/'))]
blocks=[];buf=[];paths=[];size=0
for r in selected:
 t=study.read(p,root/r['path']);ls=t.splitlines();omit=set()
 try:
  tree=ast.parse(t)
  for node in ast.walk(tree):
   body=getattr(node,'body',None)
   if isinstance(body,list) and body and isinstance(body[0],ast.Expr) and isinstance(body[0].value,ast.Constant) and isinstance(body[0].value.value,str):omit.update(range(body[0].lineno,body[0].end_lineno+1))
 except SyntaxError:pass
 lines=[str(i)+': '+line for i,line in enumerate(ls,1) if i not in omit and line.strip() and not line.lstrip().startswith('#')]
 if size+len(lines)>500 and buf:
  blocks.append({'files':paths,'lines':size});study.save(f'evidencias/{p}/applications-brazil-{len(blocks)-1:03}.txt','\n'.join(buf));buf=[];paths=[];size=0
 buf+=['### '+r['path'],*lines];paths.append(r['path']);size+=len(lines)
if buf:
 blocks.append({'files':paths,'lines':size});study.save(f'evidencias/{p}/applications-brazil-{len(blocks)-1:03}.txt','\n'.join(buf))
study.save(f'evidencias/{p}/applications-brazil-index.json',blocks)
print(len(selected),'files',sum(r['lines'] for r in selected),'original lines',len(blocks),'blocks');print(json.dumps(blocks[:5],ensure_ascii=False))
