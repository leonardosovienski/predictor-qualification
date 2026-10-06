import study,json,pathlib
r=study.ROOT;p='cripto-predictor';d=r/'evidencias'/p
paths=set();sources=[]
for pattern in ['archive-derivation-0-*-coverage.json','archive-derivation-2-coverage.json','archive-root-semantic-coverage.json','shared-archive-1-coverage.json','archive-root-extra-domains-coverage.json']:
 for f in d.glob(pattern):
  data=json.loads(f.read_text(encoding='utf-8')); rows=data if isinstance(data,list) else data.get('files',data.get('coverage',[]))
  paths.update(x['path'] for x in rows if isinstance(x,dict) and x.get('path'));sources.append(f.name)
assignments=[]
for i in range(4):
 rows=json.loads((d/f'archive-derivation-assignment-{i}.json').read_text());missing=[dict(index=j,path=x['path'],base=x.get('base')) for j,x in enumerate(rows) if x['path'] not in paths]
 assignments.append(dict(assignment=i,total=len(rows),reviewed=len(rows)-len(missing),pending=missing))
study.save('evidencias/RETOMADA_PENDENCIAS_EXATAS.json',dict(saved_at_utc=study.stamp(),status='PAUSADO_POR_PEDIDO_DO_USUARIO',coverage_files=sources,assignments=assignments,preparation_is_not_semantic_review=True))
print(json.dumps([dict(assignment=x['assignment'],total=x['total'],reviewed=x['reviewed'],pending=len(x['pending'])) for x in assignments]))
