import study,json,tomllib,pathlib,re
r=study.ROOT; names={'predictor-core','predictor-ops','predictor-research-protocol','predictor-research-transport','predictor-research-consumer','predictor-research-snapshot','predictor-research-bundle','cain-research','ecosystem-predictor','cripto-predictor','brasileirao-predictor','stocks-predictor','crypto-research-export'}
rows=[]; third={}; manifests=[]
for f in (r/'evidencias').glob('*/baseline.json'):
 b=json.loads(study.read('ESTUDO',f)); root=pathlib.Path(b['path']); project=b['project']; mf=root/'pyproject.toml'
 if not mf.is_file():continue
 doc=tomllib.loads(study.read(project,mf)); p=doc['project']; sources=doc.get('tool',{}).get('uv',{}).get('sources',{}); lf=root/'uv.lock'
 lock=tomllib.loads(study.read(project,lf)) if lf.is_file() else {}; packages=lock.get('package',[])
 manifests.append({'project':project,'version':p.get('version'),'name':p['name'],'python':p.get('requires-python'),'lock_exists':lf.is_file(),'manifest_path':str(mf)})
 for dep in p.get('dependencies',[]):
  name=re.split(r'[\[<>=!~; ]',dep)[0].lower().replace('_','-')
  if name not in names:continue
  matched=[a for a in packages if a['name']==name]
  for a in matched or [None]:
   rows.append({'consumer':project,'dependency':name,'manifest_requirement':dep,'uv_source':sources.get(name),'lock_version':a.get('version') if a else None,'lock_source':a.get('source') if a else None,'wheels':a.get('wheels',[]) if a else [],'state':'OD cadeia declarada; instalação NV' if a else 'NV dependência ausente do lock examinado'})
 for a in packages:
  if a['name'] not in names:third.setdefault(a['name'],{}).setdefault(a.get('version','?'),[]).append(project)
study.save('evidencias/package-chain.json',rows);study.save('evidencias/package-manifests.json',manifests)
different=[{'name':n,'pins':v} for n,v in third.items() if len(v)>1]
study.save('evidencias/third-party-different-pins.json',different)
study.log('ESTUDO',r,'Cruzar manifests -> uv.sources -> lock de todas fontes primárias; inventário pins de terceiros',0,f'{len(rows)} cadeias stack; {len(different)} pacotes terceiros com versões diferentes',limits='Não foi feita resolução SAT; markers/extras podem alterar compatibilidade; não é prova de lock conjunta impossível',artifacts='package-chain.json; package-manifests.json; third-party-different-pins.json')
lines=['# Identidades de pacotes e CI','', 'Estas são identidades das fontes primárias locais da linha de base. Versões instaladas/serviços ativos são NV. Releases e main remoto são consultas independentes.', '', '| Projeto | Manifest | Python | Lock | Release local correspondente | README da wheel igual ao local |','|---|---|---|---|---|---|']
for m in manifests:
 f=r/'evidencias'/m['project']/'release-identity.json'; ids=json.loads(study.read(m['project'],f)); own=next((x for x in ids if x['manifest']=='pyproject.toml'),{})
 assets=own.get('release_assets',[]); equal=','.join(str(a.get('readme_equal_normalized_newline')) for a in assets) or 'NV sem asset'
 lines.append('| '+ ' | '.join([m['project'],str(m['version']),str(m['python']),'observado' if m['lock_exists'] else 'não encontrado na raiz examinada',own.get('publication_state','NV'),equal])+' |')
lines+=['','Cada asset possui URL, digest API, SHA256 calculado do download e versão METADATA em release-identity.json. Comparação README normaliza LF/CRLF e rstrip; divergência remanescente é conteúdo textual. Manifest do protocolo local não declara readme: igualdade NV, mesmo com asset existente. A ausência de uma tag/asset é limitada à consulta das refs e primeiras 100 releases.', '', 'Dependências do stack: veja package-chain.json (requirement, uv_source, lock_version, lock_source e URL/hash de cada wheel). Caminho declarado não prova biblioteca instalada. Crypto tem protocol declarado sem pacote correspondente no lock; CAIN não tem uv.lock na raiz rastreada. Estes são bloqueios de reprodutibilidade dos checkouts estudados.', '', 'Pins de terceiros diferentes: third-party-different-pins.json. Essa comparação não considera resolução de markers/extras e não prova insatisfatibilidade. compat/ remoto descrito no anexo não foi executado.', '', '## CI consultado remotamente','', '| Projeto | Época | Run | Commit | Status | Conclusão | URL |','|---|---|---|---|---|---|---|']
for f in (r/'evidencias').glob('*/ci-*.json'):
 data=json.loads(study.read(f.parent.name,f)); runs=data.get('workflow_runs',[])
 if not runs: lines.append('| '+f.parent.name+' | '+f.stem+' | nenhum retornado | NV | NV | NV | NV |')
 for run in runs:
  lines.append('| '+' | '.join(map(str,[f.parent.name,f.stem,run['id'],run['head_sha'],run['status'],run.get('conclusion'),run['html_url']]))+' |')
lines+=['','Estado confirmado-remotamente na consulta. Run de CI é ET-HIST remoto, não teste rodado por esta investigação; listagem não oferece logs nem semântica das asserções. Runs podem ser de eventos diferentes sobre o mesmo commit. Nenhum workflow foi acionado.']
study.save('relatorios/IDENTIDADES_PACOTES_CI.md','\n'.join(lines)+'\n')
print('saved',len(rows),len(different))
