import study, pathlib, json
r=study.ROOT
projects=[json.loads(p.read_text(encoding='utf-8')) for p in (r/'evidencias').glob('*/baseline.json')]
lines=['# Linha de base','', 'Inspeção em 30/09/2026, UTC nos registros; fuso do usuário America/Sao_Paulo. Fontes locais preservadas. Consultas remotas somente leitura, sem fetch.','', '| Projeto | Origem | HEAD local | Branch | origin/main local | main remoto | Estado local |','|---|---|---|---|---|---|---|']
for p in sorted(projects,key=lambda x:x['project']):
 lines.append('| '+ ' | '.join([p['project'],p['path'],p['head'],p['branch'],p['origin_main_local'],p['origin_main_remote'] or 'NV','alterações preexistentes' if p['status'] else 'limpo'])+' |')
 lines+=[]
lines+=['','Os oito projetos foram encontrados. Todas as consultas remotas de refs tiveram sucesso; nenhum HEAD local coincide com o main remoto observado. Isso não autoriza atribuir ao checkout local as versões ou funcionalidades do remoto.','', 'CAIN e Brasileirão contêm modificações e arquivos não rastreados preexistentes, detalhados em evidencias/<projeto>/baseline-status.txt. A fonte observada é a árvore local, não apenas o commit. Nenhuma alteração foi feita nela.','', 'Cripto: escolhido C:\\CRIPTO\\pesquisa-20260909 por estar em main e apresentar o commit mais recente entre as cópias encontradas no primeiro nível de C:\\CRIPTO. Outras cópias estão catalogadas, incluindo uma com HEAD inválido. A seleção não pressupõe instalação principal.','', 'Submódulos: entradas modo 160000 não encontradas nos índices examinados. Não foi feito inventário do disco inteiro; escopo de localização documentado em raizes-c.json e diretorios-candidatos.json.','', 'Evidências: baseline.json, baseline-*.txt, remote-refs.txt, tracked-files.txt e hashes.json por projeto. Hashes representam bytes da árvore de trabalho no instante da captura.','', 'Adaptação de ambiente: /home/user/estudo-do-zero substituído pela raiz Windows outputs/estudo-do-zero. Pedido e Anexo A foram lidos integralmente antes da investigação; nenhuma conclusão do anexo orienta a caracterização preliminar. A busca de memória anterior à leitura das regras foi descartada.']
study.save('relatorios/LINHA_DE_BASE.md','\n'.join(lines)+'\n')
study.save('relatorios/CONTINUIDADE.md','# Continuidade\n\nInventário de acesso dos oito concluído; linha de base capturada. Estudo de conteúdo em andamento por código/config/testes antes de narrativa. Publicação em cópia independente. Nenhum teste de projeto executado ainda.\n\nConsulte LINHA_DE_BASE.md e evidencias/REGISTRO.log.\n')
study.log('ESTUDO',r,'Consolidar 8 baseline.json em LINHA_DE_BASE.md',0,'Inventário de acesso concluído; oito main remotos diferem dos HEAD locais',artifacts='relatorios/LINHA_DE_BASE.md; relatorios/CONTINUIDADE.md')
for p in projects:
 untracked=[line[3:] for line in p['status'].splitlines() if line.startswith('?? ')]
 hashes={}
 for name in untracked:
  f=pathlib.Path(p['path'])/name
  if f.is_file(): hashes[name]=study.hashlib.sha256(f.read_bytes()).hexdigest()
 study.save('evidencias/'+p['project']+'/untracked-hashes.json',hashes)
 study.log(p['project'],p['path'],'SHA256 arquivos não rastreados listados no status baseline',0,str(len(hashes))+' hashes',artifacts=p['project']+'/untracked-hashes.json')
q=next(p for p in projects if p['project']=='predictor-qualification')
dest=r/'publicacao/predictor-qualification'
if not dest.exists():
 code,out=study.run('PUBLICACAO',r,['git','clone','--no-hardlinks',q['path'],str(dest)],'publication-clone.txt',timeout=120)
 if code: raise SystemExit(code)
independent=(dest/'.git').is_dir() and not (dest/'.git/objects/info/alternates').exists()
study.log('PUBLICACAO',dest,'Verificar .git diretório, sem alternates; origem .git/worktrees',0,'independente='+str(independent)+'; origem_worktrees='+str((pathlib.Path(q['path'])/'.git/worktrees').exists()),limits='clone --no-hardlinks não compartilha arquivos')
if not independent: raise SystemExit('Git copy not independent')
study.run('PUBLICACAO',dest,['git','remote','set-url','origin',q['remote']], 'publication-remote.txt')
code,out=study.run('PUBLICACAO',dest,['git','ls-remote',q['remote'],'refs/heads/estudo-do-zero-2026-09-30*'],'publication-branches.txt')
existing={x.split()[-1].split('/')[-1] for x in out.splitlines() if len(x.split())==2}
branch='estudo-do-zero-2026-09-30'; n=2
while branch in existing:
 branch=f'estudo-do-zero-2026-09-30-{n:02d}'; n+=1
study.run('PUBLICACAO',dest,['git','switch','-c',branch], 'publication-switch.txt')
study.save('evidencias/publication.json',{'path':str(dest),'branch':branch,'independent':independent,'source_head':q['head']})
