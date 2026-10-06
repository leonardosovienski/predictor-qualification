import sys,json,ast,re
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent));import study
for project,base in [('cain',Path(r'C:\CAIN\projeto')),('stocks-predictor',Path(r'C:\STOCKS\stocks-predictor'))]:
 files=study.read(project,study.ROOT/'evidencias'/project/'tracked-files.txt').splitlines()
 selected=[f for f in files if (f.endswith(('.py','.js','.html','.css','.toml','.lock','.yml','.yaml','.cmd','.ps1')) and not f.startswith(('docs/','research/','evaluation/results/','vendor/'))) or f in ['requirements-dev.lock']]
 index=[]; blobs=[]
 for rel in selected:
  text=study.read(project,base/rel);entry={'path':rel,'lines':len(text.splitlines())}
  if rel.endswith('.py'):
   try:
    tree=ast.parse(text);entry['symbols']=[{'kind':type(n).__name__,'name':n.name,'line':n.lineno} for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef))];entry['imports']=sorted(set(n.module or '' for n in ast.walk(tree) if isinstance(n,ast.ImportFrom))|set(a.name for n in ast.walk(tree) if isinstance(n,ast.Import) for a in n.names))
   except SyntaxError as e:entry['parse_error']=str(e)
  index.append(entry);blobs.append('\n### '+rel+'\n'+text)
 study.save('evidencias/'+project+'/source-index.json',index)
 study.save('evidencias/'+project+'/source-text.txt',''.join(blobs))
 study.log(project,base,'Inventário AST de arquivos executáveis/config/locks/CI rastreados; exclusão docs/research/evaluation-results/vendor explícita',0,str(len(index))+' arquivos, '+str(sum(i['lines'] for i in index))+' linhas',limits='Leitura mecânica completa não equivale a revisão semântica linha a linha',artifacts=project+'/source-index.json;'+project+'/source-text.txt')
 print(project,len(index),sum(i['lines'] for i in index))
 print('\n'.join(x['path']+' '+str(x['lines']) for x in index if not x['path'].startswith('tests/')))
