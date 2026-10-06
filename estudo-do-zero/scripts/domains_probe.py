import sys, pathlib, importlib.util, types, socket, json, time, ast
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import study
start=time.monotonic()
def denied(*a,**k): raise RuntimeError('Network prohibited in study probe')
socket.socket=denied
checks=[]
def check(name, condition):
    if not condition: raise AssertionError(name)
    checks.append(name)
def raises(name,fn):
    try: fn()
    except ValueError: checks.append(name);return
    raise AssertionError(name)
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);mod=importlib.util.module_from_spec(spec);sys.modules[name]=mod;spec.loader.exec_module(mod);return mod
crypto=ROOT/'copias/cripto-predictor'; br=ROOT/'copias/brasileirao-predictor'
v=load('study_crypto_validation',crypto/'GarimpoInvestimentos/research/validation.py')
labels=[v.LabelInterval(0,1,2),v.LabelInterval(2,4,5),v.LabelInterval(3,3,4),v.LabelInterval(8,9,10)]
split=v.walk_forward(labels,[(4,7)])[0]
check('walk_forward excludes overlap, unavailable, future',split['train']==[0] and split['excluded']=={'1':'LABEL_OVERLAP_OR_GAP','2':'LABEL_NOT_AVAILABLE','3':'FUTURE'})
raises('walk_forward rejects overlapping windows',lambda:v.walk_forward(labels,[(2,5),(4,7)]))
s=load('study_crypto_simulation',crypto/'GarimpoInvestimentos/research/simulation.py')
c=s.SpotContract('BTCUSD','venue-a','BTC','USD','BTC','USD/BTC','USD')
l=s.ScenarioLedger({('venue-a','USD'):'1000'},synthetic=True)
l.submit('o',c,'BUY','2','100',at=0,latency=1,fee_rate='0.01')
check('synthetic order reserves quote+fees',l.free('venue-a','USD')==s.Decimal('798'))
raises('latency blocks premature fill',lambda:l.fill('f','o','1','90',at=0))
check('partial fill changes reservation and cash',l.fill('f','o','1','90',at=1) and l.free('venue-a','USD')==s.Decimal('808.1'))
check('identical duplicate fill no cash effect',l.fill('f','o','1','90',at=1) is False)
raises('conflicting fill rejected',lambda:l.fill('f','o','1','91',at=1))
l.cancel('o',at=2)
check('cancel releases remaining reservation',l.free('venue-a','USD')==s.Decimal('909.1') and l.snapshot()['orders']['o']['state']=='CANCELED')
raises('synthetic false rejected',lambda:s.ScenarioLedger({},synthetic=False))
score=load('study_crypto_score',crypto/'GarimpoInvestimentos/analyzers/score_engine.py')
check('score passes through bounded opportunity score',score.calculate_final_score({'opportunity_score':120,'sentiment':'negativo'})==100)
raises('nonfinite score rejected',lambda:score.calculate_final_score({'opportunity_score':float('nan')}))
check('technical divergence is flag only',score.divergence_flag(90,{'preco_vs_sma200_pct':-4,'macd_histogram':-1})==1)
# Isolate the observed allow() branch from all project imports and storage.
source=(crypto/'GarimpoInvestimentos/core/api_guard.py').read_text(encoding='utf-8');tree=ast.parse(source)
fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='allow')
ns={'settings':types.SimpleNamespace(API_GUARD_ENABLED=True),'_disabled_notice_emitted':False,'emit_event':lambda *a,**k:None,'GuardDecision':lambda allowed,reason:types.SimpleNamespace(allowed=allowed,reason=reason)}
exec(compile(ast.Module(body=[fn],type_ignores=[]),'isolated-allow-branch','exec'),ns)
check('guard enabled+zero limit still permits (isolated function)',ns['allow']('llm','synthetic',0).allowed is True)
pkg=types.ModuleType('brasileirao_scripts');pkg.__path__=[str(br/'brasileirao_scripts')];sys.modules['brasileirao_scripts']=pkg
m=load('brasileirao_scripts.prospective_metrics',br/'brasileirao_scripts/prospective_metrics.py')
check('OU Brier sums both classes',m.brier_ou25(.75,2,1)==.125 and m.brier_ou25(.75,2,0)==1.125)
raises('OU missing forecast rejected',lambda:m.brier_ou25(None,2,1))
h=m.holm_family({'H14':.03,'H15':.04},expected_ids=('H14','H15'))
check('Holm preserves whole family',h['adjusted_p_values']=={'H14':.06,'H15':.06} and not any(h['rejected'].values()))
raises('Holm cannot shrink family',lambda:m.holm_family({'H14':.02},expected_ids=('H14','H15')))
p=load('brasileirao_scripts.prospective_protocol_v2',br/'brasileirao_scripts/prospective_protocol_v2.py')
history=[{'event_id':i+1,'home_goals':2,'away_goals':1,'final_at':'2027-01-01T20:00:00Z','available_at':'2027-01-01T21:00:00Z'} for i in range(200)]
b=p.climatology_snapshot(history,kickoff_at='2027-01-04T18:00:00Z')
check('baseline reproduced smoothing and cutoff',b['p_home']==201/203 and b['p_over_2_5']==201/202 and b['cutoff']=='2027-01-03T00:00:00+00:00')
late=dict(history[0],event_id=201,available_at=b['cutoff'])
check('result available exactly cutoff excluded',p.climatology_snapshot(history+[late],kickoff_at='2027-01-04T18:00:00Z')['n_prior']==200)
raises('small prospective sample rejected',lambda:p.paired_inference([.1]*899))
check('degenerate gains never approve',p.paired_inference([1.]*900)['p_one_sided']==1)
check('protocol does not activate capital or legacy cohorts',p.specification()['status']=='SPECIFIED_NOT_ACTIVATED' and p.specification()['capital_enabled'] is False and p.specification()['legacy_cohorts_eligible'] is False)
result={'status':'passed','checks':checks,'count':len(checks),'duration_seconds':time.monotonic()-start,'method':'File-specific copied pure modules via importlib. Package bootstrap/conftest skipped. allow function isolated AST with synthetic config; no private data, sockets denied.','limits':'Synthetic semantic probes only. No pytest suite, predictor-core comparison, Redis/.NET/container, capital, prospective evidence or profitability.'}
study.save('evidencias/domain-probes.json',result)
print(json.dumps(result,ensure_ascii=False,indent=2))
