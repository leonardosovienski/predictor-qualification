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
risks.insert(0,{'ID':'G-COBERTURA','Projeto':'conjunto','Prioridade':'P1','Certeza':'OD','Afirmação':'Revisão semântica integral permanece pendente nos projetos grandes; não há bloqueio externo comprovado para ler os arquivos restantes.','Evidência':'evidencias/*/coverage.json','Limites':'Nenhuma contagem mecânica pode substituir a profundidade requerida.','Próximo passo':'Fechar cada arquivo pendente com notas semânticas e revisar tests/config/CI antes declarar estudo completo.'})
risks.insert(1,{'ID':'G-EPOCAS','Projeto':'conjunto','Prioridade':'P1','Certeza':'OD confirmado-remotamente','Afirmação':'HEADs originais diferem main remoto; AnexoA descreve outra época.','Evidência':'LINHA_DE_BASE.md; */baseline.json; */remote-refs.txt; linked-roots.json','Limites':'Main remoto observado por ref e CI, código remoto integral não revisado.','Próximo passo':'Associar cada conclusão a SHA; estudar nova época em cópia independente se necessário.'})
risks.sort(key=lambda x:x['Prioridade']);matrix('PROBLEMAS_PRIORIZADOS',list(risks[0]),risks)
study.save('evidencias/consolidation-counts.json',{'timestamp_utc':study.stamp(),'components':len(components),'integrations':len(integrations),'findings':len(risks)})
study.log('CONSOLIDACAO',r,'Normalizar matrizes mantendo exatamente colunas do mandato em MD/CSV/JSON e prioridades com certeza separada',0,f'{len(components)} componentes; {len(integrations)} integrações; {len(risks)} achados',artifacts='relatorios/MATRIZ_EVIDENCIAS.*; relatorios/MATRIZ_INTEGRACOES.*; relatorios/PROBLEMAS_PRIORIZADOS.*')
