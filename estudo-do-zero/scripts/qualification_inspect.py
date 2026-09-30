import study, pathlib, ast, json
p=pathlib.Path('C:/QUALIFICACAO/predictor-qualification'); name='predictor-qualification'
files=study.read(name,study.ROOT/'evidencias'/name/'tracked-files.txt').splitlines()
sources=[x for x in files if x.endswith(('.py','.yml','.yaml'))]
inventory=[]
for rel in sources:
 text=study.read(name,p/rel); symbols=[]; imports=[]
 if rel.endswith('.py'):
  tree=ast.parse(text)
  symbols=[{'name':n.name,'line':n.lineno,'end':n.end_lineno,'type':type(n).__name__} for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef))]
  imports=[ast.unparse(n) for n in ast.walk(tree) if isinstance(n,(ast.Import,ast.ImportFrom))]
 inventory.append({'path':rel,'lines':len(text.splitlines()),'symbols':symbols,'imports':imports})
study.save('evidencias/'+name+'/source-index.json',inventory)
study.log(name,p,'Leitura integral e AST de todos .py/.yml/.yaml em git ls-files',0,str(len(sources))+' arquivos',limits='Leitura mecânica integral não equivale a revisão semântica integral',artifacts=name+'/source-index.json')
if __name__=='__main__':
 for item in inventory:
  print(item['path'],item['lines'], ', '.join(x['name'] for x in item['symbols']))
