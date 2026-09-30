import sys,importlib.util,json,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent));import study
base=study.ROOT/'copias/stocks-predictor';p=base/'stocks_predictor/simulation.py'
started=time.perf_counter();checks=[]
study.read('stocks-predictor',p)
spec=importlib.util.spec_from_file_location('isolated_simulation',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
ds=['2026-01-01','2026-01-02','2026-01-03','2026-01-04']
def check(name,condition):
 if not condition:raise AssertionError(name)
 checks.append(name)
kw=dict(initial_cash=10,cost_per_side=0)
bars={'A':{d:(10,10) for d in ds}}
r=m.simulate_portfolio(ds,bars,{ds[0]:{'A':1}},**kw)
check('Sinal D1 só compra D2',r['executions'][0]['exec_date']==ds[1] and r['nav']==[10,10,10,10])
divbars={'A':{d:((10,10) if i<2 else (9,9)) for i,d in enumerate(ds)}}
r=m.simulate_portfolio(ds,divbars,{ds[0]:{'A':1}},cash_events={'A':[(ds[2],ds[3],1)]},**kw)
check('Direito de caixa preserva NAV e credita só payment',r['nav']==[10,10,10,10] and r['cash']==1 and not r['receivables'])
splitbars={'A':{d:((10,10) if i<2 else (5,5)) for i,d in enumerate(ds)}}
r=m.simulate_portfolio(ds,splitbars,{ds[0]:{'A':1}},splits={'A':{ds[2]:.5}},**kw)
check('Split altera quantidade e mantém NAV',r['holdings']=={'A':2} and r['nav']==[10,10,10,10])
r=m.simulate_portfolio(ds,splitbars,{ds[0]:{'A':1}},stock_events={'A':[(ds[2],ds[3],1)]},**kw)
check('Bonificação preserva NAV e entrega no crédito',r['nav']==[10,10,10,10] and r['holdings']=={'A':2} and r['stock_deliveries']==[(ds[3],'A',1)])
delayed={'A':{ds[0]:(10,10),ds[2]:(10,10),ds[3]:(10,10)}}
r=m.simulate_portfolio(ds,delayed,{ds[0]:{'A':1}},**kw)
check('Sem cotação D2 ordem espera D3',r['executions'][0]['exec_date']==ds[2])
stale={'A':{ds[0]:(10,10),ds[1]:(10,10)}}
try:m.simulate_portfolio(ds,stale,{ds[0]:{'A':1}},**kw)
except ValueError as e:check('Valuation final stale aborta','incomplete final valuation' in str(e))
else:raise AssertionError('stale')
result={'category':'ET-RUN','runtime':sys.version,'copy':str(base),'module_sha256_basis':'leitura registrada antes import','checks':checks,'passed':len(checks),'duration_seconds':time.perf_counter()-started,'limitations':'Seis cenários sintéticos unitários stdlib; não executa pytest nem DB/serviços; não valida integridade/completude de dados reais nem resultado econômico.'}
study.save('evidencias/stocks-predictor/simulation-smoke-run.json',result)
study.log('stocks-predictor',base,'Simulation stdlib synthetic isolated copy Python3.13 -B',0,str(len(checks))+' checks passaram',status='ET-RUN',limits=result['limitations'],artifacts='stocks-predictor/simulation-smoke-run.json')
print(json.dumps(result,ensure_ascii=False,indent=2))
