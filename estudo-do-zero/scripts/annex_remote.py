import study,json,urllib.request,hashlib,zipfile,io,email.parser,concurrent.futures
r=study.ROOT
requested={'core-predictor':[('predictor_core','3.2.1')],'predictor-ops':[('predictor_ops','4.2.2rc1')],'cain':[('cain_research','0.4.13rc15')],'cripto-predictor':[('cripto_predictor','1.2.0rc4')],'brasileirao-predictor':[('brasileirao_predictor','0.3.0rc5')],'stocks-predictor':[('stocks_predictor','0.3.0rc3')],'ecosystem-predictor':[('ecosystem_predictor','0.2.1'),('predictor_research_protocol','2.0.0rc2'),('predictor_research_transport','0.1.0rc7'),('predictor_research_snapshot','1.0.2rc1'),('predictor_research_bundle','1.0.1rc1')]}
items=[]
for p,reqs in requested.items():
 releases=json.loads((r/f'evidencias/{p}/remote-releases.json').read_text())
 for name,version in reqs:
  matches=[(rel,a) for rel in releases for a in rel.get('assets',[]) if a['name']==f'{name}-{version}-py3-none-any.whl']
  if not matches:items.append({'project':p,'name':name,'version':version,'state':'não publicada no espaço tags/releases consultado','asset':None});continue
  rel,a=matches[0];items.append({'project':p,'name':name,'version':version,'tag':rel['tag_name'],'release_url':rel['html_url'],'url':a['browser_download_url'],'api_digest':a.get('digest'),'published_at':rel['published_at'],'size':a['size'],'state':'confirmado-remotamente'})
def inspect(x):
 if 'url' not in x:return x
 try:
  with urllib.request.urlopen(urllib.request.Request(x['url'],headers={'User-Agent':'EvidenceStudy'}),timeout=30) as f:raw=f.read(20_000_001)
  if len(raw)>20_000_000:raise ValueError('SIZE_CAP')
  with zipfile.ZipFile(io.BytesIO(raw)) as z:
   name=next(n for n in z.namelist() if n.endswith('.dist-info/METADATA'));m=email.parser.BytesParser().parsebytes(z.read(name));body=m.get_payload();x.update(computed_sha256=hashlib.sha256(raw).hexdigest(),metadata_version=m['Version'],metadata_readme_body_present=bool(body.strip()),metadata_body_sha256=hashlib.sha256(body.encode()).hexdigest())
  study.log(x['project'],r,'GET bytes wheel publicada '+x['url'],0,'sha256='+x['computed_sha256'],status='OD',artifacts='published-annex-identities.json',limits='Bytes/METADATA; wheel não instalada, código executável não ensaiado')
 except Exception as e:x['bytes_state']='NV '+type(e).__name__;study.log(x['project'],r,'GET wheel '+x['url'],1,type(e).__name__,status='NV')
 return x
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as e:out=list(e.map(inspect,items))
study.save('evidencias/published-annex-identities.json',out)
main=json.loads((r/'evidencias/remote-main-manifests-summary.json').read_text());d=json.loads((r/'evidencias/predictor-qualification/remote-main-qualification_DECISIONS.json.json').read_text())['observation'];dec=[{'id':x['decision_id'],'status':x['status']} for x in d['decisions']]
study.save('evidencias/remote-main-decisions-summary.json',dec)
text='# Confronto do Anexo com main remoto e releases\n\nÉpoca distinta das oito fontes locais. URLs usam SHA exato consultado por ls-remote; manifests e registro de decisão lidos somente após caracterizações preliminares. OD manifest não é execução da stack atual.\n\n|Projeto / path|Versão main remoto|Commit|Estado|\n|---|---|---|---|\n'+'\n'.join('|'+x['project']+'/'+x['path']+'|'+str(x.get('version'))+'|'+x.get('sha','NV')+'|'+x['state']+'|' for x in main)
text+='\n\nAs versões main do AnexoA3 concordam com os manifests observados. CAIN declara protocolo2.0.0rc2 e transporte0.1.0rc7, além snapshot1.0.2rc1/bundle1.0.1rc1; isso confirma dependência declarada, sem concluir envelope funcionando. Ecosystem possui manifest de transporte; a ausência nos checkouts primáriosV1 não se aplica ao main.\n\n|Pacote publicado do Anexo|Versão|Tag|SHA256 bytes wheel|Estado|\n|---|---|---|---|---|\n'+'\n'.join('|'+x['name']+'|'+x['version']+'|'+x.get('tag','NV')+'|'+x.get('computed_sha256','NV')+'|'+x['state']+'|' for x in out)
text+='\n\nURLs integrais/API digest/METADATA e datas em published-annex-identities.json. Sem instalação; presença de corpo METADATA não comprova README equivalente a main pós-bump. As versões não publicadas main foram distinguidas das consumidas; consultar release-identity de cada fonte e refs-tags para a busca delimitada.\n\nDD remoto DECISIONS contém D-1..D-28 APPROVED, incluindo D-27 pós-qualificação: atestados permanecem vinculados final_commits/final_wheels antigos e novo ciclo agendado. D-29/D-30/D-31 não encontrados no campo decision_id da lista desse arquivo/commit. Aprovação no registro observada não valida execução das fases; attestations finais desse novo ciclo não foram recomputadas.\n\nET-HIST Stocks run36719558172 main3ec7...: dois qualityjobs3.13/3.14 falham no passo R8, tests/build subsequentes skipped; secrets success. Causa privada/religação de população não foi ensaiada. Na cópia do checkout primário5cf27... o verificador R8 PASS confirma época diferente.\n'
study.save('relatorios/CONFRONTO_ANEXO_REMOTO.md',text);study.log('CONFRONTO',r,'Consolidar manifests main e decisões remoto+assets publicados do Anexo sem fundir fontes locais',0,str(len(out))+' pacotes publicados consultados',artifacts='relatorios/CONFRONTO_ANEXO_REMOTO.md; published-annex-identities.json; remote-main-decisions-summary.json')
print([(x['name'],x['version'],x.get('computed_sha256','NV')[:10]) for x in out])
