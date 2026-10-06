import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent));import study
for p in ['cain','stocks-predictor']:
 d=study.ROOT/'evidencias'/p
 c=json.loads(study.read(p,d/'coverage.json'));n=json.loads(study.read(p,d/'module-notes.json'))
 extra=['shared-test-notes.json','shared-untracked-test-notes.json'] if p=='cain' else ['root-tools-notes.json']
 for f in extra:
  data=json.loads(study.read(p,d/f))
  if isinstance(data,dict):
   print(f,'dictionary',list(data)[:3]);data=data.get('files',data.get('notes',data))
  if isinstance(data,dict):data=[dict(path=k,notes=v) for k,v in data.items()]
  for r in data:
   if 'path' in r:n[r['path']]=str(r.get('notes',r.get('semantic_note',r.get('summary',''))))+' Revisão integral registrada em '+f+'; execução separada.'
  if f=='root-tools-notes.json':
   for r in json.loads(study.read(p,d/'root-tools-coverage.json')):n[r['path']]='Revisão integral por root, evidência e achados temáticos em root-tools-notes.json; cobertura por caminho em root-tools-coverage.json. Execuções apenas nas cópias, resultados separados.'
 if p=='stocks-predictor':
  conf={'.github/dependabot.yml':'Atualizações semanais pip e GitHub Actions; não execução nem correção automática.', '.gitleaks.toml':'Regras e exceções por caminhos e linhas/hashs específicos; não prova ausência de segredo fora do scanner.', 'config.yaml':'H1..H19 pré-registros; execução next_open declarada, custos .36% roundtrip, bootstrap stationary 10000/bloco21/seed42; economics NAO_DECLARADO. Configuração não prova consumo em cada fluxo legado.', 'config_rj.yaml':'RJ nove famílias, oito preditivas; FDR .10, cluster 10000, LOCO e censura; janelas60/252, horizonte756. Parser PyYAML neste domínio; calendário real precisa dados.', 'pyproject.toml':'Python>=3.13<3.15, Hatchling1.32, PyYAML6 e Core>=3.2<4 via wheel3.2.1; PluginV1; ruff F/E9, Pyright basic exceção arquivo congelado, cobertura77. Declaração não execução de checks.', 'uv.lock':'Lock catalogado com hashes e distribuição; bytes lidos, não auditadas implementações de dependências externas.'}
  for r in c:
   path=r['path']
   if path in conf:n[path]=conf[path]
   if path.startswith('experiments/') and path.endswith('.yaml'):n[path]='Protocolo/registro lido integralmente: critérios e estados declarados, congelamento e hash, seleção/rejeição V2; evidência histórica numérica do próprio registro não revalidada externamente. TRUE_PROSPECTIVE indisponível; registros de interface completa não promovem capital. Mandato e resultados separados.'
   if path.endswith('.html') and path.startswith('tests/fixtures/'):n[path]='Fixture estática catalogada/hashada e usada por testes; não código executável próprio nem publicação externa revalidada.'
 for r in c:
  if r['path'] in n:r.update(depth='revisado semanticamente' if not ('fixtures/' in r['path'] or r['path']=='uv.lock') else 'artefato/dependência catalogado; não código próprio',notes=n[r['path']])
 if p=='cain':
  for r in json.loads(study.read(p,d/'shared-untracked-test-coverage.json')):
   if not any(x['path']==r['path'] for x in c):c.append(dict(path=r['path'],sha256=r['sha256'],depth='revisado semanticamente',notes=n.get(r['path'],'shared-untracked-test-notes.json'),source_state='untracked-local-tree'))
 study.save('evidencias/'+p+'/coverage.json',c);study.save('evidencias/'+p+'/module-notes.json',n)
 study.log(p,d,'Consolidação final de revisão semântica e catálogo separado',0,str(len(c))+' arquivos; pendentes='+str([r['path'] for r in c if 'pendente' in r['depth']]),artifacts=p+'/coverage.json')
 print(p,len(c),'pendentes',[r['path'] for r in c if 'pendente' in r['depth']])
