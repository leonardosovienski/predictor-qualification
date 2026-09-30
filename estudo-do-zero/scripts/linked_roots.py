import study,pathlib,json
r=study.ROOT
candidates={'cain':'C:/QUALIFICACAO/repos/cain','ecosystem-predictor':'C:/QUALIFICACAO/repos/ecosystem-predictor','core-predictor':'C:/QUALIFICACAO/repos/core-predictor','predictor-ops':'C:/QUALIFICACAO/repos/predictor-ops','brasileirao-predictor':'C:/QUALIFICACAO/repos/brasileirao-predictor','cripto-predictor':'C:/Cripto/qualificacao/cripto-predictor','stocks-predictor':'C:/STOCKS/work/qualification/stocks-predictor'}
study.log('ESTUDO','qualification/shared/scripts/collect_stack_baseline.py','Registrar links a sete raízes alternativas configuradas antes de segui-los',0,'Raízes da qualificação não presumidas principais',artifacts='linked-roots.json')
rows=[]
for name,root in candidates.items():
 p=pathlib.Path(root)
 if (p/'.git').exists():
  code,head=study.run(name,root,['git','rev-parse','HEAD'],name+'/linked-root-head.txt')
  code,status=study.run(name,root,['git','status','--porcelain=v1','--untracked-files=all'],name+'/linked-root-status.txt')
  code,remote=study.run(name,root,['git','config','--get','remote.origin.url'],name+'/linked-root-remote.txt')
  rows.append({'project':name,'path':root,'head':head.strip(),'status':status.strip(),'remote':remote.strip()})
 else:rows.append({'project':name,'path':root,'state':'inacessível ou ausente'})
study.save('evidencias/linked-roots.json',rows)
print(json.dumps(rows,indent=2))
