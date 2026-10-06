import study,json,urllib.request,tomllib,hashlib,concurrent.futures
r=study.ROOT
ps=['cain','brasileirao-predictor','cripto-predictor','stocks-predictor','predictor-ops','core-predictor','ecosystem-predictor','predictor-qualification']
def check(p):
 b=json.loads((r/f'evidencias/{p}/baseline.json').read_text());sha=b['origin_main_remote'];repo=b['remote'].removesuffix('.git').split('github.com/')[-1];paths=['pyproject.toml'] if p!='predictor-qualification' else ['qualification/DECISIONS.json']
 if p=='ecosystem-predictor':paths+=['packages/research-protocol/pyproject.toml','packages/research-transport/pyproject.toml']
 out=[]
 for path in paths:
  u=f'https://raw.githubusercontent.com/{repo}/{sha}/{path}'
  try:
   with urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'EvidenceStudy'}),timeout=30) as f:data=f.read()
   if path.endswith('toml'):
    d=tomllib.loads(data.decode()); fields={k:d.get('project',{}).get(k) for k in ('name','version','requires-python','dependencies','scripts','entry-points','readme')};fields['uv_sources']=d.get('tool',{}).get('uv',{}).get('sources')
   else:
    d=json.loads(data);fields=d
   study.save(f'evidencias/{p}/remote-main-'+path.replace('/','_')+'.json',{'sha':sha,'url':u,'sha256':hashlib.sha256(data).hexdigest(),'observation':fields,'scope':'confirmado-remotamente; leitura do manifest/registro apenas, não revisão executável completa'})
   study.log(p,r,'GET somente leitura '+u,0,'sha256='+hashlib.sha256(data).hexdigest(),status='OD' if path.endswith('toml') else 'DD',artifacts=f'{p}/remote-main-'+path.replace('/','_')+'.json',limits='Época main remoto; nenhuma alteração ou fetch dos originais')
   out.append({'project':p,'path':path,'sha':sha,'name':fields.get('name') if isinstance(fields,dict) else None,'version':fields.get('version') if isinstance(fields,dict) else None,'state':'confirmado-remotamente'})
  except Exception as e:study.log(p,r,'GET '+u,1,type(e).__name__,status='NV');out.append({'project':p,'path':path,'state':'NV','reason':type(e).__name__})
 return out
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as e:out=[x for a in e.map(check,ps) for x in a]
study.save('evidencias/remote-main-manifests-summary.json',out);print(json.dumps(out,ensure_ascii=False))
