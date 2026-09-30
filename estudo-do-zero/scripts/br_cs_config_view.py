import study,pathlib
rows=study.read('brasileirao-shared',study.ROOT/'evidencias/brasileirao-predictor/tracked-files.txt').splitlines()
for p in rows:
 if (p.startswith('dotnet/') and not p.endswith('.cs')) or ('schema' in p.lower() and not p.startswith(('archive/','work/','research/')) and p.endswith('.json')):
  if not p.endswith(('.png','.ico','.dll','.pdb')):
   print('FILE',p);print(study.read('brasileirao-shared',pathlib.Path('C:/BRASILEIRAO/brasileirao-predictor')/p).replace('\r',''))
