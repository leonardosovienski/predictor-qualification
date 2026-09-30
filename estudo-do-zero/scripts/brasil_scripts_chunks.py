import study,json,pathlib,re,ast
r=study.ROOT;p='brasileirao-predictor';d=json.loads((r/f'evidencias/{p}/semantic-pending-by-class.json').read_text());files=[x['path'] for x in d['files']['scripts']];chunks=[];current=[];paths=[];index=[]
for rel in files:
 text=study.read(p,pathlib.Path('C:/BRASILEIRAO/brasileirao-predictor')/rel);lines=text.splitlines();skip=set()
 try:
  a=ast.parse(text)
  for n in ast.walk(a):
   if isinstance(n,(ast.Module,ast.ClassDef,ast.FunctionDef,ast.AsyncFunctionDef)) and n.body and isinstance(n.body[0],ast.Expr) and isinstance(n.body[0].value,ast.Constant) and isinstance(n.body[0].value.value,str):skip.update(range(n.body[0].lineno,n.body[0].end_lineno+1))
 except SyntaxError:pass
 part=['### '+rel]+[str(i)+': '+line for i,line in enumerate(lines,1) if i not in skip and line.strip() and not line.lstrip().startswith('#')]
 if len(current)+len(part)>600 and current:
  n=len(chunks);study.save(f'evidencias/{p}/root-scripts-{n:02}.txt','\n'.join(current));chunks.append(paths);current=[];paths=[]
 current+=part;paths.append(rel)
if current:n=len(chunks);study.save(f'evidencias/{p}/root-scripts-{n:02}.txt','\n'.join(current));chunks.append(paths)
study.save(f'evidencias/{p}/root-scripts-index.json',chunks);study.log(p,r,'Preparar fonte executável scripts para revisão humana; leitura/hash≠revisão',0,str(len(files))+' arquivos '+str(len(chunks))+' blocos',artifacts=f'{p}/root-scripts-index.json',limits='Comentários/docstrings omitidos na visualização; bytes originais mantidos')
print(json.dumps({'files':len(files),'chunks':len(chunks),'index':chunks},ensure_ascii=False))
