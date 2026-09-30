import sys,json,re,ast
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent));import study
for project,base in [('cain',Path(r'C:\CAIN\projeto')),('stocks-predictor',Path(r'C:\STOCKS\stocks-predictor'))]:
 files=study.read(project,study.ROOT/'evidencias'/project/'tracked-files.txt').splitlines()
 if project=='cain':
  status=study.read(project,study.ROOT/'evidencias'/project/'baseline-status.txt')
  extra=[x[3:] for x in status.splitlines() if x.startswith('?? ') and x[3:].endswith('.py')]
  for f in extra:study.read(project,base/f)
  study.save('evidencias/cain/untracked-source-scope.json',extra)
 docs=[f for f in files if f.endswith('.md')];study.save('evidencias/'+project+'/document-catalog.json',[{'path':f,'date_in_name':re.findall(r'20\d{2}[-_]?[01]\d[-_]?[0-3]\d',f),'topic_hint':Path(f).stem,'read_depth':'catalogado'} for f in docs])
 narrative=['README.md']+([f for f in files if Path(f).name in ('AGENTS.md','CLAUDE.md','LEIA_PRIMEIRO.md','STOCKS_CURRENT_STATE.md','HANDOFF.md','CONTINUIDADE.md')])
 for f in narrative:
  text=study.read(project,base/f);study.save('evidencias/'+project+'/narrative-'+f.replace('/','_'),text)
  print('\n### '+project+'/'+f+'\n'+text[:11000])
