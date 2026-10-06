import study,json,pathlib,hashlib,ast
def record(block,notes):
 j=json.loads(study.read('cripto-shared',study.ROOT/'evidencias/cripto-predictor/semantic-pending-by-class.json'))
 b=json.loads(study.read('cripto-shared',study.ROOT/'evidencias/cripto-predictor/baseline.json'))
 rows=[r for r in j['files']['tests'] if r['state']=='pendente'];out=[]
 for i,n in notes.items():
  r=rows[i];s=study.read('cripto-shared',pathlib.Path(b['path'])/r['path']);a=ast.parse(s)
  out.append({'index':i,'path':r['path'],'sha256_utf8':hashlib.sha256(s.encode()).hexdigest(),'state':'semanticamente_revisado_integral','execution':'nao_executado','symbols':[x.name for x in ast.walk(a) if isinstance(x,(ast.FunctionDef,ast.AsyncFunctionDef)) and x.name.startswith('test_')],'notes':n})
 prefix='evidencias/cripto-predictor/shared-crypto-tests-'+block
 study.save(prefix+'-notes.json',out);study.save(prefix+'-coverage.json',[{k:v for k,v in x.items() if k!='notes'} for x in out])
 study.save(prefix+'.md','# Revisão semântica dos testes Crypto — bloco '+block+'\n\nLeitura integral de fixtures, mocks e assertions; nenhuma execução. Os cenários demonstram contratos sintéticos ou reconciliação de artefatos, sem estabelecer lucro futuro, autorização ou execução real.\n\n'+'\n\n'.join('## '+x['path']+'\n\n'+x['notes'] for x in out))
 print('Persistido',block,len(out))
