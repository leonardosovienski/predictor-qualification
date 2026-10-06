import study,pathlib,json,sys
roots={'core-predictor':r'C:\PREDICTORS\core-predictor','predictor-ops':r'C:\PREDICTORS\predictor-ops','ecosystem-predictor':r'C:\CAIN\contrato'}
for p,root in roots.items():
 baseline=json.loads(study.read(p,study.ROOT/'evidencias'/p/'baseline.json'))
 target=study.ROOT/'copias'/p
 if not target.exists():
  code,out=study.run(p,study.ROOT,['git','clone','--no-hardlinks',root,str(target)],f'{p}/clone.txt',timeout=60)
  if code:raise RuntimeError(out)
 git=target/'.git'; independent=git.is_dir() and not (git/'commondir').exists() and not git.is_symlink()
 study.log(p,target,'Verificação cópia independente .git diretório sem commondir/symlink; no-hardlinks',0,str(independent),artifacts=f'{p}/clone.txt')
 if not independent:raise RuntimeError('copy not independent')
 study.run(p,target,['git','rev-parse','HEAD'],f'{p}/copy-head.txt')
 hazards=[]
 files=study.read(p,study.ROOT/'evidencias'/p/'tracked-files.txt').splitlines()
 import re
 for rel in files:
  rel=rel.strip()
  if rel.endswith(('.py','.toml','.ps1','.json','.yml')) and not rel.startswith(('docs/','evidence/','audits/','audit/')):
   src=study.read(p,pathlib.Path(root)/rel)
   for term in ['os.environ','getenv','urlopen','httpx','sqlite3.connect','subprocess','Path.home','icacls','PREDICTOR_EVENTS_PATH','configure_otel']:
    if term in src:hazards.append({'path':rel,'mechanism':term})
 study.save(f'evidencias/{p}/execution-preflight.json',{'hazards':hazards,'policy':'Somente smoke próprio local; não chamar downloads, configuração HTTP, OTEL, schedulers ou dados de produção; sys.path apenas cópia; runtime roots dentro da cópia de estudo. Runtime 3.12.14 abaixo requisito >=3.13 para core/ops/ecosystem raiz; resultados exploratórios não qualificam ambiente suportado. Nenhum pytest disponível.'})
 study.log(p,target,'Pré-execução recursos externos/compartilhados',0,'Mecanismos e mitigação salvos; não revelar valores; somente smoke limitado local',artifacts=f'{p}/execution-preflight.json')
print('copies/preflight ready')
