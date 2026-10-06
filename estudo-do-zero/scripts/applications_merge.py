import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent));import study
for p,files in [('cain',['root-coverage.json','root-operations-coverage.json']),('stocks-predictor',['root-ci-coverage.json'])]:
 c=json.loads(study.read(p,study.ROOT/'evidencias'/p/'coverage.json'));n=json.loads(study.read(p,study.ROOT/'evidencias'/p/'module-notes.json'))
 if p=='cain':
  n.update({'src/cain/web/index.html':'HTML lido integralmente: UI local semauth, usuário leo default, coleçãocrypto default; formsproject/docs/scopedprefs/research/workflows/streaming commax lengths e labels/aria/status; disclaimersconsulta não ciência. CSP/APIvalidação no backend; markupmaxlength não byte-limit.','src/cain/web/style.css':'CSS lido integralmente: grid desktop trêscolunas, memoryoverlay1150, mobile700 flex e overridespara user/docs/service continuaremvisíveis; focusvisible/skip/sr-only e wrapping; scrollsmooth semregra reduced-motion explícita. Nenhum testevisual executado.'})
 else:
  for f in ['shared-review-notes.json','shared-review2-notes.json']:
   for r in json.loads(study.read(p,study.ROOT/'evidencias'/p/f)):n[r['path']]=r['semantic_note']+' Limitação: '+r['limitation']
 for f in files:
  for r in json.loads(study.read(p,study.ROOT/'evidencias'/p/f)):
   n[r['path']]='Revisão semântica integral por root: '+r.get('notes',r.get('evidence',''))
 for r in c:
  if r['path'] in n:r.update(depth='revisado semanticamente',notes=n[r['path']])
 study.save('evidencias/'+p+'/module-notes.json',n);study.save('evidencias/'+p+'/coverage.json',c)
 study.log(p,study.ROOT,'Mesclagem cobertura root e shared; HTML/CSS CAIN revisados',0,str(len(n))+' notas',artifacts=p+'/coverage.json')
