import study,json,urllib.request,hashlib
r=study.ROOT
p='stocks-predictor'; data=json.loads((r/f'evidencias/{p}/ci-main-remoto.json').read_text()); out=[]
for run in data.get('workflow_runs',[]):
 u=run['jobs_url']+'?per_page=100'; req=urllib.request.Request(u,headers={'User-Agent':'EvidenceStudy','Accept':'application/vnd.github+json'})
 try:
  with urllib.request.urlopen(req,timeout=30) as f: raw=f.read()
  d=json.loads(raw); jobs=[{k:j.get(k) for k in ('id','name','head_sha','status','conclusion','started_at','completed_at','html_url','steps')} for j in d.get('jobs',[])]
  out.append({'run_id':run['id'],'sha':run['head_sha'],'jobs':jobs})
  study.log(p,r,'GET anônimo '+u,0,'sha256='+hashlib.sha256(raw).hexdigest()+'; jobs='+str(len(jobs)),status='ET-HIST',artifacts=f'{p}/remote-jobs.json',limits='Metadados de passos; saída bruta/logs não acessados. Não teste desta investigação.')
 except Exception as e: study.log(p,r,'GET anônimo '+u,1,type(e).__name__,status='NV')
study.save(f'evidencias/{p}/remote-jobs.json',out)
print(json.dumps(out,ensure_ascii=False))
chain=json.loads((r/'evidencias/package-chain.json').read_text()); assets={a['url']:a for p in r.glob('evidencias/*/release-identity.json') for i in json.loads(p.read_text()) for a in i.get('release_assets',[])}
checks=[]
for row in chain:
 for w in row.get('wheels',[]):
  a=assets.get(w['url']); checks.append({'consumer':row['consumer'],'dependency':row['dependency'],'url':w['url'],'lock_sha256':w.get('hash'),'remote_computed_sha256':a.get('computed_sha256') if a else None,'equal':w.get('hash')=='sha256:'+a['computed_sha256'] if a and a.get('computed_sha256') else None})
study.save('evidencias/package-chain-asset-check.json',checks);study.log('INTEGRACOES',r,'Comparar hashes lock versus bytes wheel remoto por URL exata',0,str(len(checks))+' referências',artifacts='package-chain-asset-check.json',limits='Instalação e satisfatibilidade conjunta NV')
for p in r.glob('evidencias/*/ci-*.json'):
 if p.name not in ('ci-head-local.json','ci-main-remoto.json'):continue
 d=json.loads(p.read_text());compact=[{k:x.get(k) for k in ('id','name','head_sha','head_branch','status','conclusion','created_at','updated_at','html_url','run_attempt')} for x in d.get('workflow_runs',[])]
 study.save(str(p.relative_to(r)).replace('.json','-summary.json'),compact)
