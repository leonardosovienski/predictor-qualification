import os, sys, json, subprocess, hashlib, datetime, pathlib, re, threading
ROOT = pathlib.Path(__file__).resolve().parents[1]
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS='0', PYTHONDONTWRITEBYTECODE='1')
def stamp(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def log(project, directory, action, code, output, status='OD', limits='', artifacts=''):
    row = ' | '.join(str(v).replace('\n',' <NL> ').replace('\r','') for v in [project,stamp(),directory,action,code,output,status,limits,artifacts])+'\n'
    for attempt in range(20):
        try:
            with (ROOT/'evidencias/REGISTRO.log').open('a',encoding='utf-8') as f: f.write(row)
            return
        except PermissionError:
            import time; time.sleep(.05)
    raise RuntimeError('Cannot append evidence')
def run(project, directory, args, artifact=None, timeout=60):
    try:
        p=subprocess.run(args,cwd=directory,env=ENV,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=timeout)
        out=p.stdout+p.stderr; code=p.returncode
    except subprocess.TimeoutExpired as e: out='TIMEOUT'; code=124
    if artifact:
        target=ROOT/'evidencias'/artifact; target.parent.mkdir(parents=True,exist_ok=True); target.write_text(out,encoding='utf-8')
    log(project,directory,subprocess.list2cmdline(args),code,out[:1500] if not artifact else 'Saída preservada em '+artifact,artifacts=artifact or '')
    return code,out
def read(project, path, artifact=None):
    path=pathlib.Path(path); data=path.read_bytes(); text=data.decode('utf-8',errors='replace')
    digest=hashlib.sha256(data).hexdigest()
    if artifact: (ROOT/'evidencias'/artifact).write_text(text,encoding='utf-8')
    log(project,path.parent,'Leitura '+str(path),0,'sha256='+digest,status='OD',artifacts=artifact or '')
    return text
def save(path, data):
    path=ROOT/path; path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,indent=2,ensure_ascii=False) if not isinstance(data,str) else data,encoding='utf-8')
def baseline(project,path):
    result={'project':project,'path':path,'timestamp_utc':stamp(),'timezone_user':'America/Sao_Paulo'}
    for key,args in [('head',['rev-parse','HEAD']),('branch',['rev-parse','--abbrev-ref','HEAD']),('status',['status','--porcelain=v1','--untracked-files=all']),('remote',['config','--get','remote.origin.url']),('origin_main_local',['rev-parse','refs/remotes/origin/main']),('submodules',['ls-files','--stage'])]:
        code,out=run(project,path,['git',*args],f'{project}/baseline-{key}.txt')
        result[key]=out.strip() if key!='submodules' else [x for x in out.splitlines() if x.startswith('160000')]
    code,out=run(project,path,['git','ls-remote',result['remote'],'refs/heads/main','refs/tags/*'],f'{project}/remote-refs.txt',timeout=45)
    result['remote_state']='confirmado-remotamente' if code==0 else 'não-verificável-por-indisponibilidade-de-rede'
    result['origin_main_remote']=next((x.split()[0] for x in out.splitlines() if x.endswith('refs/heads/main')),None)
    code,out=run(project,path,['git','ls-files'],f'{project}/tracked-files.txt')
    files=out.splitlines(); hashes={}
    for rel in files:
        p=pathlib.Path(path)/rel
        if p.is_file() and not p.is_symlink(): hashes[rel]=hashlib.sha256(p.read_bytes()).hexdigest()
    save(f'evidencias/{project}/hashes.json',hashes)
    log(project,path,'SHA256 de todos os arquivos rastreados regulares; git ls-files delimita espaço',0,str(len(hashes))+' hashes',artifacts=f'{project}/hashes.json')
    result['tracked_files']=len(files)
    save(f'evidencias/{project}/baseline.json',result)
    return result
if __name__=='__main__':
    if sys.argv[1]=='baseline':
        print(json.dumps(baseline(sys.argv[2],sys.argv[3]),ensure_ascii=False,indent=2))
