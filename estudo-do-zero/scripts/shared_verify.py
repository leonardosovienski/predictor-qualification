import study,json
out=[]
for p in ['core-predictor','predictor-ops','ecosystem-predictor']:
 rows=json.loads(study.read(p,study.ROOT/'evidencias'/p/'components.json'))
 catalog={x['path']:x for x in json.loads(study.read(p,study.ROOT/'evidencias'/p/'source-catalog.json'))}
 for r in rows:
  if r['path'] not in catalog or not r['sha256']:out.append((p,r['path'],'badpath'))
  elif r['symbol'] not in [s['name'] for s in catalog[r['path']].get('symbols',[])]:out.append((p,r['path'],r['symbol']))
study.save('evidencias/shared-reference-check.json',out)
study.log('shared',study.ROOT,'Verificar referências componentes contra catálogo AST/hashes',0,str(out),limits='Símbolos de atribuição e package-level não ASTdef são exceções esperadas',artifacts='shared-reference-check.json')
print(out)
