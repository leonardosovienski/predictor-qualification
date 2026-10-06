import sys,pathlib,ast,json
sys.path.insert(0,str(pathlib.Path(__file__).parent));import study
roots={'core-predictor':r'C:\PREDICTORS\core-predictor','predictor-ops':r'C:\PREDICTORS\predictor-ops','ecosystem-predictor':r'C:\CAIN\contrato'}
for p,root in roots.items():
 files=[f.strip() for f in study.read(p,study.ROOT/'evidencias'/p/'tracked-files.txt').splitlines() if f.strip()]
 selected=[f for f in files if f.endswith(('.py','.toml','.yml','.lock','.json','.ps1')) and not f.startswith(('docs/','evidence/','audits/','audit/'))]
 catalog=[]; texts=[]
 for rel in selected:
  content=study.read(p,pathlib.Path(root)/rel);texts.append('\nFILE '+rel+'\n'+content)
  row={'path':rel,'lines':len(content.splitlines()),'bytes':len(content.encode())}
  if rel.endswith('.py'):
   try:
    tree=ast.parse(content);row['symbols']=[{'name':n.name,'line':n.lineno,'type':type(n).__name__} for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef))];row['imports']=[ast.unparse(n) for n in ast.walk(tree) if isinstance(n,(ast.Import,ast.ImportFrom))]
   except Exception as e:row['parse_error']=str(e)
  catalog.append(row)
 study.save(f'evidencias/{p}/source-catalog.json',catalog);study.save(f'evidencias/{p}/source-full.txt',''.join(texts))
 print(p,len(selected),sum(x['lines'] for x in catalog))
