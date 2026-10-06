import study,json,pathlib,hashlib,difflib,tomllib
rows=json.loads(study.read('linked',study.ROOT/'evidencias/linked-roots.json'))
roots={'core-predictor':r'C:\PREDICTORS\core-predictor','predictor-ops':r'C:\PREDICTORS\predictor-ops','ecosystem-predictor':r'C:\CAIN\contrato'}
for x in rows:
 p=x['project']
 if p not in roots:continue
 alt=pathlib.Path(x['path']);old=pathlib.Path(roots[p])
 _,files=study.run(p+'-alternativa',alt,['git','ls-files'],f'{p}/alternative-tracked.txt')
 original=json.loads(study.read(p,study.ROOT/'evidencias'/p/'hashes.json'))
 material=[];diffs=[];alternative_hashes={}
 for rel in files.splitlines():
  f=alt/rel
  if not f.is_file():continue
  h=hashlib.sha256(f.read_bytes()).hexdigest();alternative_hashes[rel]=h
  if h==original.get(rel):continue
  if (rel.endswith(('.py','.toml','.yml','.yaml','.json','.ps1','.lock')) and not rel.startswith(('docs/','evidence/','evidencias/','audits/','audit/','reports/'))):
   content=study.read(p+'-alternativa',f)
   previous=study.read(p,old/rel) if (old/rel).is_file() else ''
   patch='\n'.join(difflib.unified_diff(previous.splitlines(),content.splitlines(),fromfile='primaria/'+rel,tofile='alternativa/'+rel,lineterm=''))
   if rel.endswith('.lock'):
    study.save(f'evidencias/{p}/alternative-lock-'+rel.replace('/','_')+'.json',tomllib.loads(content))
   material.append({'path':rel,'old_sha256':original.get(rel),'new_sha256':h,'lines':len(content.splitlines()),'mode':'leitura integral de material alterado; partes idênticas cobertas pela fonte primária'})
   if not rel.endswith('.lock'):diffs.append(patch)
 study.save(f'evidencias/{p}/alternative-hashes.json',alternative_hashes)
 study.save(f'evidencias/{p}/alternative-changes.json',material)
 study.save(f'evidencias/{p}/alternative-material.diff','\n'.join(diffs))
 manifest=tomllib.loads(study.read(p+'-alternativa',alt/'pyproject.toml'))['project']
 study.save(f'relatorios/PRELIMINAR_ALTERNATIVA_{p}.md',f'# Caracterização antes da narrativa: {p} alternativa\n\nRaiz `{alt}`, HEAD `{x["head"]}` limpo conforme linked-roots.json. Manifest `{manifest["name"]}` versão `{manifest["version"]}`. Método: hash de todos rastreados; leitura integral de todo código/config/teste alterado; trechos idênticos referenciados à leitura semântica da fonte primária, sem reconstruir execução. Material e hashes em alternative-changes.json/alternative-hashes.json; diff preservado. Nenhum código da raiz alternativa executado. Narrativa alternativa ainda não lida neste bloco.\n')
 study.log(p+'-alternativa',alt,'Hash todos rastreados e leitura integral material código/config alterado antes narrativa',0,f'{len(material)} arquivos materialmente diferentes',artifacts=f'{p}/alternative-hashes.json;{p}/alternative-changes.json;{p}/alternative-material.diff;relatorios/PRELIMINAR_ALTERNATIVA_{p}.md')
 print(p,len(material));print('\n'.join(r['path'] for r in material));print('\n'.join(diffs))
