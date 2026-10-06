import sys,pathlib,sqlite3,json,hashlib,importlib.util,socket,uuid
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'));import study
socket.socket=lambda *a,**k:(_ for _ in ()).throw(RuntimeError('network forbidden'))
checks=[]
def check(n,v):
 if not v:raise AssertionError(n)
 checks.append(n)
def refuses(n,fn):
 try:fn()
 except (FileExistsError,ValueError):checks.append(n);return
 raise AssertionError(n)
for p in ['cripto-predictor','brasileirao-predictor']:
 src=ROOT/'copias'/p/'study-alternate/recovery.py';spec=importlib.util.spec_from_file_location(p.replace('-','_')+'_recovery',src);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 scratch=ROOT/'copias'/p/'study-alternate'/('recovery-probe-'+uuid.uuid4().hex);scratch.mkdir()
 dbpath=scratch/'synthetic.sqlite'
 with sqlite3.connect(dbpath) as db:db.execute('CREATE TABLE evidence(id INTEGER PRIMARY KEY,value TEXT)');db.execute('INSERT INTO evidence VALUES(1,?)',('synthetic only',))
 a=scratch/'synthetic-artifacts';a.mkdir();(a/'effect.json').write_text('{"fixture":true}',encoding='utf-8')
 before={str(x):hashlib.sha256(x.read_bytes()).hexdigest() for x in [dbpath,a/'effect.json']}
 bundle=scratch/'bundle';manifest=m.create_recovery_bundle(bundle,sqlite_databases={'state':dbpath},artifact_roots={'effects':a})
 check(p+' bundle includes DB+artifact',len(manifest['files'])==2 and manifest['source_mutated'] is False)
 after={str(x):hashlib.sha256(x.read_bytes()).hexdigest() for x in [dbpath,a/'effect.json']};check(p+' source bytes preserved',before==after)
 restored=scratch/'restored';check(p+' restore new root',m.restore_recovery_bundle(bundle,restored)['status']=='RESTORED_TO_NEW_ROOT')
 with sqlite3.connect(f'file:{(restored/"sqlite/state.sqlite").as_posix()}?mode=ro',uri=True) as db:check(p+' restored SQLite data and integrity',db.execute('SELECT value FROM evidence').fetchone()[0]=='synthetic only' and db.execute('PRAGMA integrity_check').fetchone()[0]=='ok')
 refuses(p+' nonempty restore refused',lambda:m.restore_recovery_bundle(bundle,restored))
 target=bundle/'artifacts/effects/effect.json';target.write_text('tampered fixture',encoding='utf-8');refuses(p+' mutated bundle rejected hash',lambda:m.verify_recovery_bundle(bundle))
result={'status':'passed','count':len(checks),'checks':checks,'python':sys.version,'scope':'Dois módulos recovery alternativas, dados SQLite/artifacts sintéticos exclusivamente copies. Sem escritora concorrente, backup multi-DB real, processo ativo ou credenciais.'};study.save('evidencias/domain-recovery-probes.json',result);print(json.dumps(result,ensure_ascii=False,indent=2))
