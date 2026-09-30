import study, pathlib, sys, json, importlib.util
r=study.ROOT
study.log('ESTUDO',r,'Tentativa inline de runtime inventory via PowerShell',1,'SyntaxError quoting; substituída por arquivo script',limits='Sem execução de projeto')
found=[str(p) for p in pathlib.Path('C:/QUALIFICACAO/tools').glob('python/*/python.exe')]
study.save('evidencias/runtime-candidates.json',found)
study.log('ESTUDO','C:/QUALIFICACAO/tools','Inventário python/*/python.exe referido em código observado',0,str(len(found))+' candidatos',artifacts='runtime-candidates.json')
probe="import sys,importlib.util,json; print(json.dumps(dict(version=sys.version.split()[0], modules={m:importlib.util.find_spec(m) is not None for m in ('pytest','jsonschema','numpy','pydantic')})))"
for i,p in enumerate([sys.executable]+found):
 print(p,study.run('ESTUDO',r,[p,'-I','-c',probe],'runtime-check-'+str(i)+'.txt'))
study.log('predictor-qualification',r/'copias/predictor-qualification','Retificação preflight jsonschema',0,'Suposição disponibilidade estava incorreta; attest check ERROR ModuleNotFoundError, exit1; evidence_numbers exit0',status='ET-RUN',limits='Não qualifica domínio; nenhuma instalação realizada',artifacts='predictor-qualification/attest-check.txt; predictor-qualification/evidence-numbers-run.txt')
