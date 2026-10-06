import sys,pathlib,tempfile,unittest,copy
ROOT=pathlib.Path(__file__).resolve().parents[1];repo=ROOT/'copias/ecosystem-predictor'
for name in ['research-snapshot','research-bundle','research-protocol']:sys.path.insert(0,str(repo/'packages'/name/'src'))
class ContractSmoke(unittest.TestCase):
 def test_protocol_strict_canonical(self):
  from research_protocol import canonical,loads
  self.assertEqual(loads(canonical({'b':1,'a':'ação'})),{'a':'ação','b':1})
  with self.assertRaises(ValueError):canonical({'a':1.5})
  with self.assertRaises(ValueError):loads(b'{"a":1,"a":2}')
 def test_bundle_paths(self):
  from research_bundle import safe_path
  for p in ['../escape','CON','C:/absolute','a\\b']:
   with self.assertRaises(ValueError):safe_path(p)
  self.assertEqual(safe_path('files/record.json'),'files/record.json')
 def test_snapshot_publication_idempotent_conflict(self):
  from research_snapshot import seal,loads,validate
  from research_snapshot.publication import publish
  body={'contract':'ResearchSnapshotV1','profile':'local-evidence/1','extensions':{},'origin':{'domain':'synthetic','repository':'synthetic','publisher':'test','stream':'test','code_revision':'test','exporter_revision':'test','inputs':{'source.md':'a'*64}},'exported_at':'2026-09-13T00:00:00Z','coverage':{'scope':'test','completeness':'partial','included':['source.md'],'missing':[],'excluded':[],'limitations':['synthetic only']},'restrictions':{'policy':'test','read':True,'disclose':False,'generate':False},'records':[],'evidence':[]}
  package=seal(body)
  with tempfile.TemporaryDirectory(dir=repo) as d:
   dest=pathlib.Path(d)/'publication.json';receipt=publish(package,dest);self.assertEqual(publish(package,dest),receipt);self.assertEqual(validate(loads(dest.read_bytes())),package)
   body['exported_at']='2026-09-13T00:00:01Z'
   with self.assertRaises(FileExistsError):publish(seal(body),dest)
print('Runtime:',sys.version);print('Only stdlib contract subpackages; no root registry or domain plugin.')
unittest.main(verbosity=2)
