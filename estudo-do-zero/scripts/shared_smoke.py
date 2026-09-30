import sys,pathlib,json,tempfile,os,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
p=sys.argv[1];copy=ROOT/'copias'/p
sys.path.insert(0,str(copy/'src'))
os.environ['PREDICTOR_EVENTS_PATH']=str(copy/'smoke-artifacts'/'events.jsonl')
for n in ('research-snapshot','research-bundle','research-protocol'):sys.path.insert(0,str(copy/'packages'/n/'src'))
class Smoke(unittest.TestCase):
 def test_contract_boundaries(self):
  if p=='core-predictor':
   from predictor_core.measurement.replay import replay,LookaheadError
   self.assertEqual(replay((1,2,3),lambda past:past.latest),[1,2,3])
   with self.assertRaises(LookaheadError):replay((1,),lambda past:past[1])
   with self.assertRaises(ValueError):replay((2,1),lambda past:None,key=lambda e:e)
  elif p=='predictor-ops':
   from predictor_ops.models import JobConfig,JobType,RiskSnapshot
   from predictor_ops.operations import kill_switch_reasons
   job=JobConfig(id='blocked',command=[sys.executable,'-c','pass'],job_type=JobType.EXECUTION,capital_permission=True,risk_snapshot=RiskSnapshot())
   self.assertIn('risk_snapshot_incomplete',kill_switch_reasons(job))
  else:
   from research_protocol import canonical,loads
   self.assertEqual(loads(canonical({'a':1})),{'a':1})
   with self.assertRaises(ValueError):canonical({'a':1.5})
   with self.assertRaises(ValueError):loads(b'{"a":1,"a":2}')
 def test_persistence_or_diagnostic(self):
  with tempfile.TemporaryDirectory(dir=copy) as d:
   d=pathlib.Path(d)
   if p=='core-predictor':
    from predictor_core.kernel.jsonl_store import JsonlStore
    s=JsonlStore(d/'events.jsonl');s.append({'n':1});self.assertEqual(s.count(),1)
    with self.assertRaises(ValueError):s.append({'n':float('nan')})
    self.assertEqual(s.count(),1)
   elif p=='predictor-ops':
    from predictor_ops.models import JobConfig,RuntimeConfig,RunStatus
    from predictor_ops.runner import run_job
    j=JobConfig(id='smoke',command=[sys.executable,'-c',"print('local-smoke')"],runtime=RuntimeConfig(root=d),heartbeat_interval_seconds=.02,timeout_seconds=5)
    result=run_job(j);self.assertIs(result.run_status,RunStatus.SUCCEEDED);self.assertIn('local-smoke',result.record['output']['text'])
    self.assertEqual(json.loads((d/'smoke'/'heartbeat.json').read_text())['run_status'],'SUCCEEDED')
   else:
    from ecosystem.registry import Registry
    self.assertEqual(Registry().diagnostic_snapshot(),{})
    from research_snapshot import loads
    with self.assertRaises(ValueError):loads(b'{"a":NaN}')
 def test_numerical_or_safety(self):
  if p=='core-predictor':
   from predictor_core.measurement.metrics import brier,rps
   from predictor_core.measurement.trials import deflated_sharpe_ratio,DeflationNotEstimableError
   self.assertEqual(brier([[1,0]],[0]),0);self.assertEqual(rps([[1,0]],[0]),0)
   self.assertFalse(deflated_sharpe_ratio([.1,-.1,.2],[None])['deflation_applied'])
   with self.assertRaises(DeflationNotEstimableError):deflated_sharpe_ratio([.1,-.1,.2],[None],strict=True)
  elif p=='predictor-ops':
   from predictor_ops.operations import retry_action,OrderState,RetryAction
   from predictor_ops.redaction import redact_text
   self.assertIs(retry_action(OrderState.SUBMISSION_UNKNOWN),RetryAction.QUERY_EXTERNAL_STATE)
   self.assertNotIn('synthetic-long-secret',redact_text('Bearer synthetic-long-secret'))
  else:
   from research_bundle import safe_path
   with self.assertRaises(ValueError):safe_path('../escape')
   with self.assertRaises(ValueError):safe_path('CON')
   self.assertEqual(safe_path('files/record.json'),'files/record.json')
unittest.main(argv=[sys.argv[0]],verbosity=2)
