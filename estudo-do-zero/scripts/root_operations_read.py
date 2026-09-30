import study,json,sys
from pathlib import Path
p=sys.argv[1]; index=json.loads((study.ROOT/f'evidencias/{p}/source-index.json').read_text())
base=Path(json.loads((study.ROOT/f'evidencias/{p}/baseline.json').read_text())['path'])
xs=[x['path'] for x in index if not x['path'].startswith(('src/','tests/'))]
for rel in xs[int(sys.argv[2]):int(sys.argv[3])]:
 print('\n### '+rel+'\n'+study.read(p,base/rel))
