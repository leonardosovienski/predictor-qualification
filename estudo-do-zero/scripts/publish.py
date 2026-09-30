import study, json, pathlib, shutil, re, sys, hashlib
r=study.ROOT; cfg=json.loads((r/'evidencias/publication.json').read_text(encoding='utf-8')); dest=pathlib.Path(cfg['path']); target=dest/'estudo-do-zero'
patterns=[('private_key',r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),('github_token',r'\b(?:ghp_|github_pat_)[A-Za-z0-9_]{20,}'),('openai_token',r'\bsk-[A-Za-z0-9_-]{25,}'),('aws_key',r'\bAKIA[A-Z0-9]{16}\b'),('credential_url',r'https?://[^\s/@:]+:[^\s/@]+@'),('email',r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b')]
allowed={'.md','.mmd','.json','.csv','.log','.txt','.py','.ps1'}
files=[]; findings=[]
active_inventory=sys.argv[2] if len(sys.argv)>2 else None
previous_inventories={p.name for p in (target/'relatorios').glob('INVENTARIO_*.md')} if target.exists() else set()
for directory in ['relatorios','evidencias','scripts']:
 for p in (r/directory).rglob('*'):
  if not p.is_file() or p.suffix.lower() not in allowed: continue
  if p.name.startswith(('source-text','narrative-','raw-source','all-source','executable-','central-extract','remaining-')): continue
  if p.name in ('remote-releases.json','ci-head-local.json','ci-main-remoto.json','release-identity-summary.json'): continue
  if any(part in ('__pycache__','.venv','node_modules','.pytest_cache') for part in p.parts):continue
  if active_inventory and p.name.startswith('INVENTARIO_') and p.name != 'INVENTARIO_'+active_inventory+'.md' and p.name not in previous_inventories: continue
  rel=p.relative_to(r); content=p.read_text(encoding='utf-8-sig',errors='replace')
  for name,pattern in patterns:
   hits=list(re.finditer(pattern,content))
   if hits:
    findings.append({'file':str(rel),'category':name,'occurrences':len(hits)})
    content=re.sub(pattern,'<REDACTED_'+name.upper()+'>',content)
  content=content.replace(str(r),'<STUDY_ROOT>').replace(str(r).replace('\\','/'),'<STUDY_ROOT>')
  content=content.replace('C:\\Users\\leona','<USER_PROFILE>').replace('<USER_PROFILE>','<USER_PROFILE>')
  files.append((rel,content))
manifest={'timestamp_utc':study.stamp(),'milestone':sys.argv[1],'files':[{'path':str(p).replace('\\','/'),'published_sha256':hashlib.sha256(c.encode('utf-8')).hexdigest()} for p,c in files], 'excluded':['copias/','publicacao/','.venv','caches','bancos','datasets brutos','extensões não previstas'], 'redactions':findings}
study.save('evidencias/publication-manifest.json',manifest)
study.log('PUBLICACAO',dest,'Pré-sincronização: lista explícita extensões texto previstas; scan tokens/chaves/URLs autenticadas/emails; sanitizar cópia',0,f'{len(files)} arquivos; {len(findings)} grupos redigidos',artifacts='publication-manifest.json',limits='Varredura heurística, sem garantia absoluta; nenhuma cópia/dataset/ambiente')
previous_manifest=target/'evidencias/publication-manifest.json'
if previous_manifest.exists():
 previous=json.loads(previous_manifest.read_text(encoding='utf-8'))
 current={str(x).replace('\\','/') for x,_ in files}
 removed=[]
 for item in previous.get('files',[]):
  name=item['path']; candidate=(target/name).resolve()
  if name not in current and candidate.is_relative_to(target.resolve()) and candidate.is_file():
   candidate.unlink(); removed.append(name)
 if removed:study.log('PUBLICACAO',target,'Retirar apenas arquivos previstos no manifesto anterior e agora excluídos; caminho resolve dentro estudo-do-zero validado',0,str(removed),limits='Somente cópia de publicação; histórico Git preservado')
for rel,content in files:
 t=target/rel;t.parent.mkdir(parents=True,exist_ok=True);t.write_text(content,encoding='utf-8',newline='\n')
t=target/'evidencias/publication-manifest.json';t.write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8',newline='\n')
study.run('PUBLICACAO',dest,['git','add','--','estudo-do-zero'],'publication-add.txt')
code,out=study.run('PUBLICACAO',dest,['git','diff','--cached','--name-only'],'publication-staged.txt')
if out.strip():
 code,out=study.run('PUBLICACAO',dest,['git','commit','-m','estudo-do-zero: '+sys.argv[1]],'publication-commit.txt')
 if code:raise SystemExit(code)
code,commit=study.run('PUBLICACAO',dest,['git','rev-parse','HEAD'],'publication-head.txt')
study.log('PUBLICACAO',dest,'Marco commit '+sys.argv[1],code,commit.strip(),artifacts='publication-manifest.json; publication-head.txt')
print(commit.strip())
