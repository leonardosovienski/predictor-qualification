import study,json,pathlib,ast,hashlib
p='brasileirao-predictor'
def record(notes):
 stem=f'evidencias/{p}/shared-brasil-scripts'
 old=json.loads(study.read(p,study.ROOT/(stem+'-notes.json'))) if (study.ROOT/(stem+'-notes.json')).exists() else []
 rows=[]
 for rel,note in notes.items():
  s=study.read(p,pathlib.Path('C:/BRASILEIRAO/brasileirao-predictor')/rel)
  rows.append({'path':rel,'sha256_utf8':hashlib.sha256(s.encode()).hexdigest(),'state':'semanticamente_revisado_integral','execution':'nao_executado','symbols':[n.name for n in ast.walk(ast.parse(s)) if isinstance(n,(ast.FunctionDef,ast.ClassDef))],'notes':note})
 merged={x['path']:x for x in old+rows}
 study.save(stem+'-notes.json',list(merged.values()))
 study.save(stem+'-coverage.json',[{k:v for k,v in x.items() if k!='notes'} for x in merged.values()])
 study.save(stem+'-review.md','# Scripts Brasil: revisão semântica\n\nNenhum script original executado. Hash dos bytes em REGISTRO.log.\n\n'+'\n\n'.join('## '+x['path']+'\n\n'+x['notes'] for x in merged.values()))
 print('persistidos',len(merged))
