import sys,json,re,tomllib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent));import study
for p in ['cain','stocks-predictor']:
 index=json.loads(study.read(p,study.ROOT/'evidencias'/p/'source-index.json'))
 tests=[i for i in index if i['path'].startswith('tests/')]
 assertions=[]
 for entry in tests:
  base=Path(r'C:\CAIN\projeto') if p=='cain' else Path(r'C:\STOCKS\stocks-predictor')
  t=study.read(p,base/entry['path']);assertions.append({'path':entry['path'],'tests':[s['name'] for s in entry.get('symbols',[]) if s['name'].startswith('test_')],'assertion_lines':[{'line':n+1,'text':l.strip()} for n,l in enumerate(t.splitlines()) if l.lstrip().startswith(('assert ','with pytest.raises'))]})
 study.save('evidencias/'+p+'/test-contracts.json',assertions)
 study.log(p,study.ROOT,'Extração dos nomes/asserts dos testes; ET-SRC, sem execução',0,str(sum(len(x['tests']) for x in assertions))+' funções de teste nos arquivos selecionados',limits='Extração não prova passage nem independência de fixtures',artifacts=p+'/test-contracts.json')
 print(p,len(tests),sum(len(x['tests']) for x in assertions))
