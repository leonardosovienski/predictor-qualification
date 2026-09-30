import study,json,csv,io,shutil
r=study.ROOT
projects=['cain','brasileirao-predictor','cripto-predictor','stocks-predictor','predictor-ops','core-predictor','ecosystem-predictor','predictor-qualification']
cc=['Projeto','Componente','Propósito','Implementação','Testes','Uso','Estado','Limitações','Evidências']; ic=['Origem','Destino','Mecanismo','Informação','Contrato','Implementação','Testes','Uso','Evidências']
components=[];integrations=[];risks=[]
for p in projects:
 inv=r/f'INVENTARIO_{p}.md'
 if inv.exists() and not (r/f'relatorios/{inv.name}').exists():shutil.copyfile(inv,r/f'relatorios/{inv.name}');study.log(p,r,'Copiar inventário entregue para relatorios preservando bytes',0,inv.name)
 for x in json.loads((r/f'evidencias/{p}/components.json').read_text()):
  if 'Projeto' in x: row={k:x.get(k,'NV') for k in cc}
  else:row=dict(zip(cc,[p,x.get('component',x.get('id','')),x.get('role',x.get('behavior','NV')),x.get('path',x.get('evidence','NV'))+(':'+x['symbol'] if x.get('symbol') else ''),x.get('evidence','OD')+'; testes detalhados no inventário e cobertura',x.get('runtime','NV uso atual'),x.get('status',x.get('evidence','OD')),x.get('limit','Leitura não é execução; cobertura integral não certificada quando pendente'),f'evidencias/{p}/components.json; evidencias/{p}/hashes.json; REGISTRO.log']))
  components.append(row)
 for x in json.loads((r/f'evidencias/{p}/integrations.json').read_text()):
  if 'Origem' in x: row={k:x.get(k,'NV') for k in ic}
  else:row=dict(zip(ic,[x.get('origin',x.get('source',p)),x.get('destination',x.get('target','NV')),x.get('mechanism','NV'),x.get('payload','NV informação não detalhada nesta linha; ver inventário'),x.get('contract','NV contrato não detalhado nesta linha; ver inventário'),x.get('path',x.get('status','OD'))+'; '+x.get('permissions_auth','')+'; '+x.get('errors',x.get('limits','')),x.get('evidence','ET-SRC quando explicitado no inventário; ETRUN não pressuposto'), 'NV uso atual',f'evidencias/{p}/integrations.json; INVENTARIO_{p}.md; REGISTRO.log']))
  for k in ('Autenticação','Sincronismo','Erros','Obrigatória'):
   if k in x:row['Implementação']+='; '+k+': '+str(x[k])
  integrations.append(row)
 for j,x in enumerate(json.loads((r/f'evidencias/{p}/findings.json').read_text())):
  risks.append({'ID':x.get('id',p+'-'+str(j+1)),'Projeto':p,'Prioridade':x.get('prioridade','P1' if any(w in x.get('claim','').lower() for w in ('capital','hash','concorr','lock','budget','ci ')) else 'P2'),'Certeza':x.get('certeza',x.get('category',x.get('status','NV'))),'Afirmação':x.get('afirmação',x.get('claim','')),'Evidência':x.get('evidência',x.get('evidence',x.get('path',''))),'Limites':x.get('limit',x.get('limits','Ver inventário e cobertura')),'Próximo passo':x.get('próximo_passo','Verificar na mesma época e no fluxo consumidor; não corrigir fontes nesta missão')})
def matrix(name,cols,rows):
 study.save('relatorios/'+name+'.json',rows)
 f=io.StringIO(newline='');w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(rows);study.save('relatorios/'+name+'.csv',f.getvalue())
 esc=lambda v:str(v).replace('|','/').replace('\n',' ')
 study.save('relatorios/'+name+'.md','# '+name.replace('_',' ')+'\n\nColunas idênticas no Markdown, CSV e JSON. Escopo: épocas locais da linha de base, salvo indicação de suplemento. OD não implica serviço ativo; ET-SRC não implica teste aprovado.\n\n|'+'|'.join(cols)+'|\n|'+'|'.join(['---']*len(cols))+'|\n'+'\n'.join('|'+'|'.join(esc(x[k]) for k in cols)+'|' for x in rows)+'\n')
matrix('MATRIZ_EVIDENCIAS',cc,components);matrix('MATRIZ_INTEGRACOES',ic,integrations)
ep=r/'evidencias/epoca-main-20260930/findings.json'
if ep.exists():
 for x in json.loads(ep.read_text(encoding='utf-8')):
  risks.append({'ID':x['id'],'Projeto':x['projeto'],'Prioridade':x['prioridade'],'Certeza':x['certeza'],'Afirmação':'[época main 2026-09-30] '+x['afirmação'],'Evidência':x['evidência'],'Limites':x['limites'],'Próximo passo':x['próximo_passo']})
risks.insert(0,{'ID':'G-COBERTURA-RESIDUAL','Projeto':'conjunto','Prioridade':'P2','Certeza':'OD','Afirmação':'Após a reconciliação de 2026-09-30, a revisão semântica integral cobre o código próprio ativo dos oito projetos e o arquivo histórico Crypto (773 objetos). Residual explícito: Brasileirão 16 arquivos de configuração/contratos JSON/workflows/lock cujos bytes locais diferem do remoto; Stocks research/ (301 .py históricos separados), vendor/ (43, terceiros) e docs/OSS (10 protótipos) catalogados sem leitura semântica; docs/ históricos dos demais projetos catalogados.','Evidência':'evidencias/*/coverage.json; evidencias/brasileirao-predictor/retomada-residual-pendentes.json; evidencias/cripto-predictor/crypto-archive-coverage-merged.json','Limites':'Leitura não é execução; nenhum dos residuais está no caminho de serving revisado, mas isso não foi provado por grafo de imports.','Próximo passo':'Reler os 16 arquivos Brasil no original Windows; decidir se research/ do Stocks entra no escopo de uma missão própria.'})
risks.insert(1,{'ID':'G-EPOCAS','Projeto':'conjunto','Prioridade':'P1','Certeza':'OD confirmado-remotamente','Afirmação':'HEADs originais diferem do main remoto; o Anexo A descreve outra época. Época main estudada em 2026-09-30 (LINHA_DE_BASE_EPOCA_MAIN.md): os oito HEADs originais são ancestrais dos main atuais; delta inventariado por arquivo e revisado só nos projetos pequenos (ops, core, ecosystem V2/transport) e nos adapters/contratos dos domínios.','Evidência':'LINHA_DE_BASE.md; LINHA_DE_BASE_EPOCA_MAIN.md; */baseline.json; epoca-main-20260930/baseline/SUMMARY.json; epoca-main-20260930/delta/*.json','Limites':'Main remoto observado por ref e CI, código remoto integral não revisado.','Próximo passo':'Associar cada conclusão a SHA (feito nos suplementos); revisar o delta pendente (EPOCA-COBERTURA-1).'})
risks.sort(key=lambda x:x['Prioridade']);matrix('PROBLEMAS_PRIORIZADOS',list(risks[0]),risks)
study.save('evidencias/consolidation-counts.json',{'timestamp_utc':study.stamp(),'components':len(components),'integrations':len(integrations),'findings':len(risks)})
study.log('CONSOLIDACAO',r,'Normalizar matrizes mantendo exatamente colunas do mandato em MD/CSV/JSON e prioridades com certeza separada',0,f'{len(components)} componentes; {len(integrations)} integrações; {len(risks)} achados',artifacts='relatorios/MATRIZ_EVIDENCIAS.*; relatorios/MATRIZ_INTEGRACOES.*; relatorios/PROBLEMAS_PRIORIZADOS.*')
