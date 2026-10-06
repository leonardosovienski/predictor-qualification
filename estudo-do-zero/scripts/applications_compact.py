import sys,json,ast,io,tokenize
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent));import study
for project,base in [('cain',Path(r'C:\CAIN\projeto')),('stocks-predictor',Path(r'C:\STOCKS\stocks-predictor'))]:
 index=json.loads(study.read(project,study.ROOT/'evidencias'/project/'source-index.json')); chunks=[];current=[];length=0;manifest=[]
 for item in index:
  rel=item['path']
  if not rel.endswith('.py') or rel.startswith(('tests/','.ci/','tools/','scripts/','evaluation/','experiments/')):continue
  t=study.read(project,base/rel);tree=ast.parse(t);skip=set()
  for node in ast.walk(tree):
   if isinstance(node,(ast.Module,ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)) and node.body and isinstance(node.body[0],ast.Expr) and isinstance(node.body[0].value,ast.Constant) and isinstance(node.body[0].value.value,str):skip.update(range(node.body[0].lineno,node.body[0].end_lineno+1))
  lines=[f'{n}: {l}' for n,l in enumerate(t.splitlines(),1) if n not in skip and l.strip() and not l.lstrip().startswith('#')]
  block='\n### '+rel+'\n'+'\n'.join(lines)+'\n'
  if length+len(block)>32000 and current:chunks.append(''.join(current));manifest.append(current_names);current=[];length=0
  if not current:current_names=[]
  current.append(block);current_names.append(rel);length+=len(block)
 if current:chunks.append(''.join(current));manifest.append(current_names)
 for n,chunk in enumerate(chunks):study.save(f'evidencias/{project}/executable-{n:02}.txt',chunk)
 study.save('evidencias/'+project+'/executable-chunks.json',manifest)
 print(project,[(n,len(chunk),len(manifest[n])) for n,chunk in enumerate(chunks)])
