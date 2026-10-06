import study,json,pathlib,difflib
roots={'core-predictor':r'C:\PREDICTORS\core-predictor','predictor-ops':r'C:\PREDICTORS\predictor-ops','ecosystem-predictor':r'C:\CAIN\contrato'}
for p,root in roots.items():
 alt=pathlib.Path(r'C:\QUALIFICACAO\repos')/p
 rows=json.loads(study.read(p,study.ROOT/'evidencias'/p/'alternative-changes.json'))
 substantive=[];line_only=[]
 for r in rows:
  old=pathlib.Path(root)/r['path'];new=alt/r['path']
  a=study.read(p,old) if old.is_file() else ''
  b=study.read(p+'-alternativa',new)
  (line_only if a.splitlines()==b.splitlines() else substantive).append(r['path'])
 study.save(f'evidencias/{p}/alternative-difference-classes.json',{'substantive':substantive,'line_ending_only':line_only,'method':'splitlines comparison; raw SHA256 always preserved'})
 docs=[]
 for rel in ['README.md','ARCHITECTURE_IMPLEMENTATION.md','HANDOFF.md','CURRENT_STATE.md']:
  f=alt/rel
  if f.is_file():
   content=study.read(p+'-alternativa-narrativa',f)
   old=pathlib.Path(root)/rel;a=study.read(p,old) if old.is_file() else ''
   diff='\n'.join(difflib.unified_diff(a.splitlines(),content.splitlines(),fromfile='primaria/'+rel,tofile='alternativa/'+rel,lineterm=''))
   study.save(f'evidencias/{p}/alternative-narrative-'+rel+'.diff',diff)
   docs.append(rel);print(p,rel,diff)
 summary={
 'core-predictor':'Código src, testes, pyproject e uv.lock são byte a byte iguais à fonte primária. As três mudanças materiais são workflows: --frozen→--locked em CI/release; consumer compatibility retirado de push/PR e mantido workflow_dispatch histórico, com alteração das actions. Portanto mecanismos de replay/trials e limitações anteriores permanecem aplicáveis a estes bytes; estado de Actions não pode ser transplantado.',
 'predictor-ops':'Versão sobe4.2.1→4.2.2rc1. Única mudança de src é _mutation_guard: inicialização de byte usa descriptor não buffered, captura PermissionError e espera a trava em vez de repropagar no seek/close Windows. Teste novo multiprocessos segura byte vazio e verifica espera>=0.3s; ET-SRC somente. Teste version aceita PEP440rc. CI/release passam a --locked; consumer contracts movido para workflow_dispatch histórico, fora push/PR. Runner/modelos/risco/provenance/processes continuam byte idênticos. Sem execução alternativa.',
 'ecosystem-predictor':'Fontes Python de plugin/diagnostics,snapshot,bundle/files,protocol/keystore e testes alterados têm diferenças apenas de terminações de linha; splitlines iguais. Contratos e limitações funcionais anteriores continuam aplicáveis a esses textos. Mudanças materiais adicionam dev pytest e uv.lock a cada researchpackage, sources locais(snapshot/bundle), raiz devgroup, CI research-packages matriz3.11-3.14 três pacotes com uv lock --check e --locked. Jobs crossrepo movidos de CI para workflow_dispatch histórico; caincrypto recebe comentário de aposentadoria. Continuam quatro pyprojects, root0.2.0 eprotocolV1; nenhuma evidência de transportV2/compat nesta raiz.'}[p]
 text=f'# Suplemento: {p} em raiz de qualificação\n\nFonte alternativa `{alt}`, identidade em linked-roots.json; fonte primária `{root}` não foi substituída. PRELIMINAR_ALTERNATIVA_{p}.md salvo antes das narrativas alternativas {docs}. Todos rastreados foram hashados; código/config alterado lido integralmente; código byte idêntico reaproveita a inspeção primária, sem nova execução. Diferenças apenas de line ending são explicitamente separadas e não anulam hash bruto.\n\n{summary}\n\nArquivos materialmente diferentes após normalizar somente quebra de linha: '+', '.join('`'+x+'`' for x in substantive)+'.\n\nArquivos diferentes somente em line ending: '+', '.join('`'+x+'`' for x in line_only)+'.\n\nFontes: alternative-changes.json,alternative-hashes.json,alternative-difference-classes.json,alternative-material.diff e alternative-lock-*.json em evidencias/'+p+'. Declarações documentais alternativas são preservadas em alternative-narrative-*.diff. Nenhum teste da raiz alternativa original foi acionado. Não generalizar diferenças para o main remoto ou AnexoA.\n'
 study.save(f'relatorios/SUPLEMENTO_RAIZ_ALTERNATIVA_{p}.md',text)
 study.log(p+'-alternativa',alt,'Confronto semântico de raízes e narrativa após prelim alternativa',0,summary,limits='Nenhuma execução alternativa; arquivos idênticos reaproveitam leitura fonte primária',artifacts=f'relatorios/SUPLEMENTO_RAIZ_ALTERNATIVA_{p}.md;{p}/alternative-difference-classes.json')
