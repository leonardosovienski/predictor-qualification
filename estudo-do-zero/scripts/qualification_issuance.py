import study,json,pathlib,hashlib,subprocess,sys
p='predictor-qualification';base=pathlib.Path('C:/QUALIFICACAO/predictor-qualification');name=sys.argv[1] if len(sys.argv)>1 else 'QUALIFICATION_ATTESTATION';rel='qualification/crypto/'+name+'.json';artifact='predictor-qualification/issuance-'+name+'.json'
att=json.loads(study.read(p,base/rel));code,out=study.run(p,base,['git','log','--format=%H','--',rel],'predictor-qualification/attestation-history-commits.txt');commits=out.splitlines();records=[]
for commit in commits:
 a=subprocess.run(['git','show',f'{commit}:{rel}'],cwd=base,env=study.ENV,capture_output=True)
 if a.returncode:continue
 doc=json.loads(a.stdout);refs=[]
 def walk(node,location=''):
  if isinstance(node,dict):
   if node.get('file') and node.get('sha256'):yield location,node
   for key,val in node.items():yield from walk(val,location+'/'+str(key))
  elif isinstance(node,list):
   for i,val in enumerate(node):yield from walk(val,location+'/'+str(i))
 for location,ref in walk(doc):
   path=ref['file'];expected=ref['sha256']
   b=subprocess.run(['git','show',f'{commit}:{path}'],cwd=base,env=study.ENV,capture_output=True)
   actual=hashlib.sha256(b.stdout).hexdigest() if b.returncode==0 else None
   refs.append(dict(location=location,path=path,expected=expected,actual=actual,match=actual==expected))
 records.append(dict(commit=commit,attestation_sha256=hashlib.sha256(a.stdout).hexdigest(),generated_at=doc.get('generated_at'),result=doc.get('result'),ref_checks=refs))
 study.log(p,base,'Ler Git blobs atestado e refs no commit '+commit,0,str(len(refs))+' referências SHA verificadas',limits='Gitshow read-only semcheckout; hash não reexecuta nem autentica resultado',artifacts=artifact)
study.save('evidencias/'+artifact,records)
print(json.dumps(dict(current_result=att.get('result'),keys=list(att),commits=len(commits),records=[dict(commit=x['commit'],result=x['result'],refs=len(x['ref_checks']),matches=sum(y['match'] for y in x['ref_checks'])) for x in records])))
