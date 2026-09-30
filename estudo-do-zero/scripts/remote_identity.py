import study, pathlib, json, tomllib, urllib.request, urllib.error, concurrent.futures, zipfile, io, email, hashlib
r=study.ROOT
def api(project,url,artifact):
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'EvidenceStudy/1.0','Accept':'application/vnd.github+json'})
  with urllib.request.urlopen(req,timeout=25) as response: data=json.load(response)
  study.save('evidencias/'+artifact,data)
  study.log(project,url,'GET público anônimo JSON GitHub API',0,'confirmado-remotamente',artifacts=artifact)
  return data
 except Exception as exc:
  study.log(project,url,'GET público anônimo JSON GitHub API',1,type(exc).__name__,status='NV',limits=str(exc)[:200])
  return None
def inspect(b):
 project=b['project']; root=pathlib.Path(b['path']); repo=b['remote'].rstrip('/').rsplit('/',1)[-1].removesuffix('.git')
 manifests=[root/'pyproject.toml']+[p for p in (root/'packages').glob('*/pyproject.toml')]
 rows=[]
 releases=api(project,f'https://api.github.com/repos/leonardosovienski/{repo}/releases?per_page=100',project+'/remote-releases.json')
 refs=study.read(project,r/'evidencias'/project/'remote-refs.txt').splitlines()
 for mf in manifests:
  if not mf.is_file(): continue
  doc=tomllib.loads(study.read(project,mf)); p=doc.get('project',{}); version=p.get('version'); pname=p.get('name');
  if not version:continue
  relevant=[x for x in refs if 'refs/tags/' in x and (x.split('/')[-1].removesuffix('^{}')==version or x.split('/')[-1].removesuffix('^{}')=='v'+version or x.split('/')[-1].removesuffix('^{}').endswith('-'+version))]
  found=[]
  for release in releases or []:
   for a in release['assets']:
    normalized=(pname or '').replace('-','_')
    if a['name'].startswith(normalized+'-'+version+'-') and a['name'].endswith('.whl'):
     row={'tag':release['tag_name'],'url':a['browser_download_url'],'api_digest':a.get('digest'),'size':a['size'],'published_at':release['published_at'],'state':'confirmado-remotamente'}
     if a['size']<=20_000_000:
      try:
       request=urllib.request.Request(a['browser_download_url'],headers={'User-Agent':'EvidenceStudy/1.0'})
       with urllib.request.urlopen(request,timeout=30) as response: raw=response.read(20_000_001)
       row['computed_sha256']=hashlib.sha256(raw).hexdigest()
       with zipfile.ZipFile(io.BytesIO(raw)) as z:
        metadata=next(x for x in z.namelist() if x.endswith('.dist-info/METADATA'))
        md=email.message_from_bytes(z.read(metadata)); body=md.get_payload()
        readme=p.get('readme','README.md'); readme=readme.get('file') if isinstance(readme,dict) else readme
        local=study.read(project,mf.parent/readme) if readme and (mf.parent/readme).is_file() else None
        row['metadata_version']=md.get('Version'); row['readme_equal_normalized_newline']=(body.replace('\r\n','\n').rstrip()==local.replace('\r\n','\n').rstrip()) if local else None
        row['metadata_body_sha256']=hashlib.sha256(body.encode()).hexdigest()
       study.log(project,row['url'],'Download wheel público em memória; sha256; ZIP METADATA; comparar README normalizado LF/rstrip',0,'sha256='+row['computed_sha256']+'; README igual='+str(row['readme_equal_normalized_newline']),artifacts=project+'/release-identity.json',limits='Wheel não instalada; normalização ignora LF/CRLF e final em branco')
      except Exception as exc:
       row['download_error']=type(exc).__name__+': '+str(exc)[:160]
       study.log(project,row['url'],'Download wheel público; inspeção identidade',1,type(exc).__name__,status='NV',limits='Hash conteúdo/METADATA indisponíveis')
     found.append(row)
  rows.append({'manifest':str(mf.relative_to(root)),'name':pname,'version':version,'python':p.get('requires-python'),'tag_refs':relevant,'release_assets':found,'publication_state':('não publicada (sem tag correspondente na consulta)' if not relevant else 'tag observada; asset '+('observado' if found else 'não encontrado nas 100 releases consultadas')) if releases is not None else 'NV'})
 study.save('evidencias/'+project+'/release-identity.json',rows)
 for label,sha in [('head-local',b['head']),('main-remoto',b['origin_main_remote'])]:
  if sha: api(project,f'https://api.github.com/repos/leonardosovienski/{repo}/actions/runs?head_sha={sha}&per_page=100',project+'/ci-'+label+'.json')
 print(project,[(x['name'],x['version'],len(x['release_assets'])) for x in rows])
if __name__=='__main__':
 baselines=[json.loads(p.read_text(encoding='utf-8')) for p in (r/'evidencias').glob('*/baseline.json')]
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(inspect,baselines))
