import study,json,hashlib,pathlib,concurrent.futures
r=study.ROOT
ps=['cain','brasileirao-predictor','cripto-predictor','stocks-predictor','predictor-ops','core-predictor','ecosystem-predictor','predictor-qualification']
def check(p):
 b=json.loads((r/f'evidencias/{p}/baseline.json').read_text());path=pathlib.Path(b['path']);out={'project':p,'timestamp_utc':study.stamp(),'path':str(path)}
 for k,args in [('head',['rev-parse','HEAD']),('status',['status','--porcelain=v1','--untracked-files=all'])]:
  c,v=study.run(p,path,['git',*args],f'{p}/preservation-{k}.txt');out[k+'_unchanged']=v.strip()==b[k];out[k]=v.strip()
 differences=[];hashes=json.loads((r/f'evidencias/{p}/hashes.json').read_text())
 for name,h in hashes.items():
  f=path/name;actual=hashlib.sha256(f.read_bytes()).hexdigest() if f.is_file() else None
  if actual!=h:differences.append({'path':name,'baseline_sha256':h,'current_sha256':actual})
 out['tracked_hashes_checked']=len(hashes);out['tracked_differences']=differences
 u=r/f'evidencias/{p}/untracked-hashes.json'
 if u.exists():
  d=json.loads(u.read_text()); out['untracked_hash_shape']=type(d).__name__;out['untracked_differences']=[]
  if isinstance(d,dict):
   for name,h in d.items():
    if isinstance(h,dict):h=h.get('sha256')
    f=path/name;actual=hashlib.sha256(f.read_bytes()).hexdigest() if f.is_file() else None
    if h!=actual:out['untracked_differences'].append({'path':name,'baseline_sha256':h,'current_sha256':actual})
 study.save(f'evidencias/{p}/preservation.json',out);study.log(p,path,'Revalidar HEAD/status/hashs de arquivos originais no encerramento de bloco',0,str(out['tracked_hashes_checked'])+' hashes; differences='+str(len(differences)),artifacts=f'{p}/preservation.json',limits='Comparação de estado/bytes; não monitor contínuo de metadados Git ou escritores externos')
 return {k:out[k] for k in ('project','head_unchanged','status_unchanged','tracked_hashes_checked','tracked_differences')}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as e:out=list(e.map(check,ps))
study.save('evidencias/preservation-summary.json',out);print(json.dumps(out,ensure_ascii=False))
