import sys,pathlib,importlib.util,json,copy,socket,time
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'));import study
socket.socket=lambda *a,**k:(_ for _ in ()).throw(RuntimeError('network forbidden'))
checks=[]
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
def check(name,v):
 if not v:raise AssertionError(name)
 checks.append(name)
def reject(name,fn):
 try:fn()
 except ValueError:checks.append(name);return
 raise AssertionError(name)
c=load('crypto_contract',ROOT/'copias/cripto-predictor/study-alternate/crypto_contract.py')
b=load('br_contract',ROOT/'copias/brasileirao-predictor/study-alternate/contract.py')
p=load('br_pit',ROOT/'copias/brasileirao-predictor/study-alternate/pit.py')
def references(kinds):return {k:{'name':'synthetic','version':'v1'} for k in kinds}
cr={'schema_version':c.REQUEST_SCHEMA,'request_id':'crypto:req1','research_id':'crypto:research1','hypothesis_id':'crypto:H7','request_type':'BACKTEST_EXISTING_HYPOTHESIS','references':references(c.REFERENCE_KINDS),'data_cutoff':'2026-09-01T00:00:00Z','parameters':{'symbol':'BTCUSDT','horizon_days':7,'max_observations':100,'fee_bps':10,'slippage_bps':5},'priority_hint':'NORMAL'}
check('Crypto own local request accepted schema',c.validate_request(cr) is cr)
reject('Crypto cannot inject command',lambda:c.validate_request(cr|{'command':'fake'}))
check('Crypto client_ref excluded content identity',c.request_content_hash(cr)==c.request_content_hash(cr|{'client_ref':{'trace':'opaque'}}))
reject('Crypto identifiers reject foreign domain',lambda:c.validate_request(cr|{'request_id':'brasileirao:r1'}))
reject('Crypto malformed duplicate JSON rejected',lambda:c.loads_strict('{"a":1,"a":2}'))
check('Contracts requester trust local only',c.REQUESTER_TRUST==b.REQUESTER_TRUST=='LOCAL_FILE_ONLY')
br={'schema_version':b.REQUEST_SCHEMA,'request_id':'brasileirao:req1','research_id':'brasileirao:res1','hypothesis_id':'brasileirao:exploratory1','request_type':'WALKFORWARD_FORECAST_EVALUATION','competition':'Brasileirão Série A','season':2025,'target':'OU25','events':{'kickoff_from':'2025-01-01T00:00:00Z','kickoff_to':'2026-01-01T00:00:00Z'},'data_cutoff':'2026-01-01T00:00:00Z','decision_lead_minutes':60,'references':references(b.REFERENCE_KINDS),'priority_hint':'NORMAL'}
check('Brasil own local request accepted schema',b.validate_request(br) is br)
reject('Brasil schema cannot inject SQL',lambda:b.validate_request(br|{'sql':'fake'}))
reject('Brasil competition boundary enforced',lambda:b.validate_request(br|{'competition':'Premier League'}))
reject('Brasil lead zero rejected',lambda:b.validate_request(br|{'decision_lead_minutes':0}))
reject('Brasil timezone offset request rejected',lambda:b.validate_request(br|{'data_cutoff':'2026-01-01T00:00:00-03:00'}))
from datetime import datetime,UTC
check('Brasil result availability kickoff+180min',p.result_available_at(datetime(2026,9,1,18,tzinfo=UTC)).isoformat()=='2026-09-01T21:00:00+00:00')
check('Brasil date-only availability next03UTC',p.result_available_at(None,'2026-09-01').isoformat()=='2026-09-02T03:00:00+00:00')
reject('Brasil PIT refuses naive kickoff',lambda:p.result_available_at(datetime(2026,9,1,18)))
result={'status':'passed','count':len(checks),'checks':checks,'python':sys.version,'scope':'Somente contratos puros/PIT fonte alternativa; arquivos materializados copies independentes. Sem admission/runtime/worker/science/economy e sem treino.','source_crypto':'C:/Cripto/qualificacao/cripto-predictor 1.2.0rc2','source_brasil':'C:/QUALIFICACAO/repos/brasileirao-predictor 0.3.0rc2'}
study.save('evidencias/alternate-domain-probes.json',result);print(json.dumps(result,indent=2,ensure_ascii=False))
