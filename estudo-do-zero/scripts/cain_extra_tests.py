import study,json,pathlib
rows=json.loads(study.read('cain-shared',study.ROOT/'evidencias/cain/source-index.json'))
for r in rows:
 if not r['path'].startswith('tests/') and ('test_' in r['path'] or 'conftest' in r['path']):
  print('FILE',r['path']);print(study.read('cain-shared',pathlib.Path('C:/CAIN/projeto')/r['path']))
