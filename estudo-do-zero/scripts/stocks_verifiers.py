import study,json,hashlib,pathlib
r=study.ROOT; p='stocks-predictor'; b=json.loads((r/f'evidencias/{p}/baseline.json').read_text());copy=r/'copias'/p
study.log(p,copy,'Preflight verificadores tools/check_project_files.py e verify_operational_evidence.py: stdlib, caminhos ROOT da cópia, Git somente leitura, sem HTTP/banco/credenciais; --write-index e materializadores NÃO usados',0,'Config externa ausente nestes dois caminhos; manifests/locks preservados',status='OD',limits='Testa índices/hashes/receipts na época do clone; nãoexecuta ingestão nem refaz run econômico')
for rel in ['pyproject.toml','uv.lock','tools/check_project_files.py','tools/verify_operational_evidence.py']:
 expected=json.loads((r/f'evidencias/{p}/hashes.json').read_text())[rel]; actual=hashlib.sha256((copy/rel).read_bytes()).hexdigest();study.log(p,copy,'Identidade pré-teste '+rel,0,'original_sha='+expected+'; copy_sha='+actual,limits='Byte diferenças fimlinha possíveis checkout')
py=r'C:\QUALIFICACAO\tools\python\cpython-3.13.14-windows-x86_64-none\python.exe'
for name in ['check_project_files','verify_operational_evidence']:
 code,out=study.run(p,copy,[py,'-B','-X','utf8',f'tools/{name}.py'],f'{p}/{name}-run.txt',timeout=60);print(name,code,out[:600]);study.log(p,copy,'Classificar teste '+name,code,'ver saída integral',status='ET-RUN',artifacts=f'{p}/{name}-run.txt',limits='Windows Python3.13.14 stdlib; não suite completa e não CI remoto')
