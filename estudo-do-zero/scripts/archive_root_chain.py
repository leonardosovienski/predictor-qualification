import study,pathlib,json,hashlib,difflib,ast
p='cripto-predictor';root=pathlib.Path('C:/CRIPTO/pesquisa-20260909');folder=f'evidencias/{p}/'
items=json.loads((study.ROOT/(folder+'archive-derivation-assignment-3.json')).read_text());idx=json.loads((study.ROOT/(folder+'archive-root-review-index.json')).read_text());done={q for b in idx[:7] for q in b}
def body(path):
 text=study.read(p,root/path);lines=text.splitlines();skip=set()
 try:tree=ast.parse(text)
 except SyntaxError:tree=ast.Module(body=[],type_ignores=[])
 for n in ast.walk(tree):
  if isinstance(n,(ast.Module,ast.ClassDef,ast.FunctionDef,ast.AsyncFunctionDef)) and n.body and isinstance(n.body[0],ast.Expr) and isinstance(n.body[0].value,ast.Constant) and isinstance(n.body[0].value.value,str):skip.update(range(n.body[0].lineno,n.body[0].end_lineno+1))
 return [s for i,s in enumerate(lines,1) if i not in skip and s.strip() and not s.lstrip().startswith('#')]
cache={x:body(x) for x in done};groups=[];cur=[];paths=[];plan=[]
for item in items:
 path=item['path']
 if path in done:continue
 source=body(path);candidates=list(cache)
 if item.get('base'):
  if item['base'] not in cache:cache[item['base']]=body(item['base'])
  candidates.append(item['base'])
 candidates=list(dict.fromkeys(candidates));parent=min(candidates,key=lambda q:len(list(difflib.unified_diff(cache[q],source,n=3))))
 diff=list(difflib.unified_diff(cache[parent],source,fromfile=parent,tofile=path,n=3,lineterm=''));part=['OBJECT '+path,'BASE '+parent]+diff
 if len(cur)+len(part)>250 and cur:
  study.save(folder+f'raw-source-chain-root-{len(groups):03}.txt','\n'.join(cur));groups.append(paths);cur=[];paths=[]
 cur+=part;paths.append(path);plan.append(dict(path=path,base=parent,sha256=hashlib.sha256((root/path).read_bytes()).hexdigest(),base_sha256=hashlib.sha256((root/parent).read_bytes()).hexdigest(),diff_lines=len(diff)));cache[path]=source
if cur:study.save(folder+f'raw-source-chain-root-{len(groups):03}.txt','\n'.join(cur));groups.append(paths)
study.save(folder+'archive-root-chain-index.json',groups);study.save(folder+'archive-root-chain-plan.json',plan)
print(json.dumps(dict(objects=len(plan),blocks=len(groups),diff_lines=sum(x['diff_lines'] for x in plan))))
