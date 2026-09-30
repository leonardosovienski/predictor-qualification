import study,json,hashlib,pathlib
P='cripto-predictor'; stem=f'evidencias/{P}/shared-archive-1'
def record(notes):
 rows=json.loads(study.read(P,study.ROOT/f'evidencias/{P}/archive-derivation-assignment-1.json'))
 out=json.loads(study.read(P,study.ROOT/(stem+'-notes.json'))) if (study.ROOT/(stem+'-notes.json')).exists() else []
 old={r['index']:r for r in out}
 for i,note in notes.items():
  x=rows[i];s=study.read(P,pathlib.Path('C:/CRIPTO/pesquisa-20260909')/x['path'])
  old[i]={'index':i,'path':x['path'],'base':x['base'],'source_sha256':x.get('source_sha256',x.get('sha256')),'sha256_utf8':hashlib.sha256(s.encode()).hexdigest(),'state':'historico_revisado_por_derivacao_integral' if x['base'] else 'historico_corpo_integral_revisado','execution':'nao_executado','notes':note}
 out=[old[i] for i in sorted(old)]
 study.save(stem+'-notes.json',out);study.save(stem+'-coverage.json',[{k:v for k,v in r.items() if k!='notes'} for r in out]);study.save(stem+'-review.md','# Arquivo histórico Crypto — partição1\n\nObjetos históricos, distintos da implementação atual; corpos atuais já revisados na partição principal. Nenhum original executado.\n\n'+'\n\n'.join('## '+str(r['index'])+' '+r['path']+'\n\n'+r['notes'] for r in out))
 print('Persistidos',len(out),'de',len(rows))
