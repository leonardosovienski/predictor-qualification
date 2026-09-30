import study,json,pathlib,sys
j=json.loads(study.read('brasileirao-shared',study.ROOT/'evidencias/brasileirao-predictor/semantic-pending-by-class.json'))
b=json.loads(study.read('brasileirao-shared',study.ROOT/'evidencias/brasileirao-predictor/baseline.json'))
rows=j['files']['C#']
if len(sys.argv)==1:
 print('ROOT',b['path']);print('\n'.join(str(i)+' '+str(x) for i,x in enumerate(rows)))
else:
 for i,r in enumerate(rows):
  if int(sys.argv[1])<=i<=int(sys.argv[2]):
   print('FILE',i,r['path']);print(study.read('brasileirao-shared',pathlib.Path(b['path'])/r['path']).replace('\r',''))
