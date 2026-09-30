import pathlib,sys,importlib.util,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1];copy=ROOT/'copias/core-predictor'
def leaf(name):
 path=copy/'src/predictor_core/measurement'/f'{name}.py';spec=importlib.util.spec_from_file_location('studied_'+name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
class SourceLeafSmoke(unittest.TestCase):
 def test_replay_prefix_and_rejection(self):
  m=leaf('replay');self.assertEqual(m.replay([1,2,3],lambda p:tuple(p[:])),[(1,),(1,2),(1,2,3)])
  with self.assertRaises(m.LookaheadError):m.replay([1],lambda p:p[1])
  with self.assertRaises(ValueError):m.replay([2,1],lambda p:None,key=lambda e:e)
  with self.assertRaises(m.LookaheadError):m.replay([(1,2)],lambda p:None,key=lambda e:e[0],available_at=lambda e:e[1])
 def test_metric_formula(self):
  m=leaf('metrics');self.assertAlmostEqual(m.brier([[.8,.2],[.3,.7]],[0,1]),.13)
  self.assertEqual(m.rps([[1.,0.]],[0]),0.)
 def test_bootstrap_seed_and_constant(self):
  m=leaf('bootstrap');mean=lambda x:sum(x)/len(x);args=dict(scheme='iid',n_boot=100,seed=17)
  self.assertEqual(m.bootstrap_ci([2.]*5,mean,**args)[:2],(2.,2.))
  self.assertEqual(m.bootstrap_ci([1,2,3],mean,**args),m.bootstrap_ci([1,2,3],mean,**args))
print('Runtime:',sys.version);print('Scope: exact source leaf modules from independent copy; package facade/distribution metadata not loaded.')
unittest.main(verbosity=2)
