import sys,importlib.util,json,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent));import study
base=study.ROOT/'copias/stocks-predictor'
started=time.perf_counter();checks=[]
def load(name):
 p=base/'stocks_predictor'/(name+'.py');spec=importlib.util.spec_from_file_location('isolated_'+name,p);module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module);return module
def check(name,condition):
 if not condition:raise AssertionError(name)
 checks.append(name)
e=load('execution');p=load('portfolio');v=load('validation');g=load('economic_gate')
check('exec estritamente posterior D+1',e.next_open_after(['2026-01-01','2026-01-02'],[10,11],'2026-01-01')==('2026-01-02',11))
check('sem pregão futuro não executa',e.next_open_after(['2026-01-01'],[10],'2026-01-01') is None)
check('turnover saída normaliza carteira anterior',abs(e.equal_weight_turnover_cost({'A','B'},{'A'},0.01)-0.005)<1e-12)
check('turnover inicial cobra lado inteiro',e.equal_weight_turnover_cost(set(),{'A','B'},0.01)==0.01)
check('quintil top mantém pesos',p.select_portfolio({'A':1,'B':2,'C':3,'D':4,'E':5})=={'E':1.0})
check('sem amostra madura hold',g.decide_rebalance(None,0.01).action=='HOLD')
check('evidência positiva acima custo rebalance sem capital',g.decide_rebalance(g.EdgeEstimate(.2,.1,12),.01).action=='REBALANCE' and not g.decide_rebalance(g.EdgeEstimate(.2,.1,12),.01).capital_enabled)
check('evidência abaixo custo hold',g.decide_rebalance(g.EdgeEstimate(.2,.001,12),.01).action=='HOLD')
for label,fn in [('data inválida',lambda:v.iso_day('2026-02-30')),('bool não é inteiro',lambda:v.positive_integer(True,'n')),('amostra não finita',lambda:g.estimate_edge([float('nan')]*12))]:
 try:fn()
 except ValueError:checks.append(label+' rejeitada')
 else:raise AssertionError(label)
result={'category':'ET-RUN','runtime':sys.version,'copy':str(base),'checks':checks,'passed':len(checks),'duration_seconds':time.perf_counter()-started,'limitations':'Smoke stdlib isolado em quatro módulos, sem pytest/Core/DB/modelos/dados/API; não valida suíte, previsão ou lucro.'}
study.save('evidencias/stocks-predictor/smoke-run.json',result);study.log('stocks-predictor',base,'Python -B applications_smoke.py; imports spec de execution portfolio validation economic_gate da cópia independente',0,str(len(checks))+' checks passaram; '+str(result['duration_seconds'])+' segundos',status='ET-RUN',limits=result['limitations'],artifacts='stocks-predictor/smoke-run.json');print(json.dumps(result,ensure_ascii=False,indent=2))
