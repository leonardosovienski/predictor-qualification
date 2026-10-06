import study,pathlib,json,hashlib,difflib,sys,ast
p='cripto-predictor';base=pathlib.Path('C:/CRIPTO/pesquisa-20260909');items=json.loads((study.ROOT/f'evidencias/{p}/archive-derivation-assignment-3.json').read_text());current=[];groups=[];paths=[]
def executable(text):
 lines=text.splitlines();skip=set()
 try:
  tree=ast.parse(text)
  for n in ast.walk(tree):
   if isinstance(n,(ast.Module,ast.ClassDef,ast.FunctionDef,ast.AsyncFunctionDef)) and n.body and isinstance(n.body[0],ast.Expr) and isinstance(n.body[0].value,ast.Constant) and isinstance(n.body[0].value.value,str):skip.update(range(n.body[0].lineno,n.body[0].end_lineno+1))
 except SyntaxError:pass
 return [line for i,line in enumerate(lines,1) if i not in skip and line.strip() and not line.lstrip().startswith('#')]
for item in items:
 source=study.read(p,base/item['path']);parent=study.read(p,base/item['base']) if item['base'] else ''
 digest=hashlib.sha256((base/item['path']).read_bytes()).hexdigest()
 if item.get('source_sha256'):assert digest==item['source_sha256']
 else:item['source_sha256']=digest
 if item['base']:assert hashlib.sha256((base/item['base']).read_bytes()).hexdigest()==item['base_sha256']
 part=['OBJECT '+item['path'],'BASE '+str(item['base'])]+list(difflib.unified_diff(executable(parent),executable(source),fromfile=str(item['base']),tofile=item['path'],n=3,lineterm=''))
 if len(current)+len(part)>450 and current:
  n=len(groups);study.save(f'evidencias/{p}/raw-source-archive-root-{n:03}.txt','\n'.join(current));groups.append(paths);current=[];paths=[]
 current+=part;paths.append(item['path'])
if current:
 n=len(groups);study.save(f'evidencias/{p}/raw-source-archive-root-{n:03}.txt','\n'.join(current));groups.append(paths)
study.save(f'evidencias/{p}/archive-root-review-index.json',groups)
study.log(p,base,'Preparar diff completo histórico assignment3 para revisão derivada',0,str(len(items))+' objetos / '+str(len(groups))+' blocos',limits='Preparação/hash não revisão; diferençasincluemdeleções/inserções; baserevisadaintegralmente por outroagente',artifacts='cripto-predictor/archive-root-review-index.json')
print(json.dumps(dict(objects=len(items),blocks=len(groups))))
