import study, pathlib, json, ast
r=study.ROOT; project='predictor-qualification'; p=pathlib.Path('C:/QUALIFICACAO/predictor-qualification')
pre='''# Caracterização preliminar — predictor-qualification

Salva antes do confronto com README, COMMON_QUALIFICATION_CORE, decisões ou relatórios. Base: scripts Python/shell/PowerShell e workflows lidos nesta investigação. O Anexo A foi visto ao ler o pedido, mas não usado como fonte destas conclusões.

A árvore não apresenta pyproject.toml ou uv.lock na listagem Git examinada. É uma coleção de scripts e arquivos de evidência, acionados por argumentos posicionais, argparse e Actions, e não um pacote installável demonstrado. Scripts demandam Python com tomllib; attest.py usa jsonschema; sondas dependem de predictor_ops e do domínio instalado.

collect_stack_baseline.py lê clones de sete projetos, Git, manifests, locks e API via gh; grava JSON/log. cleanroom_baseline.py clona fontes, resolve lock, instala wheels, cria variantes published/head_build, roda testes fora dos pacotes e compara arquivos das wheels. O guard registra módulos fora do site-packages, mas não muda o exitstatus da suíte. Caminhos e integrações fazem esses executores potencialmente mutáveis e inadequados ao original.

attest.py constrói documentos a partir de GATES/FINDINGS, SHA256 das evidências, core e baseline. check valida schema, conta findings, compara hashes de gate e combina statuses; não reexecuta domínio nem avalia verdade científica. write recusa sobrescrever. d16_finalize.py exige decisão D-16 APPROVED, cruza target com env.log e resume evidências para gates; move attestation anterior via git mv e grava GATES.

evidence_numbers.py recomputa contagens de XML/log/JSONL e grava EVIDENCE_NUMBERS; summarize_cleanroom.py lê facts/logs e imprime resumo. Ambos descrevem runs históricos: executá-los agora não é repetir testes de domínio. analyze_ops_failure.py distingue setup_failed mas algumas agregações excluem setup_failed do denominador; isto deve permanecer explícito.

Fluxo Crypto: build_real_dataset baixa Binance com checksum; real_env cria CAS/policy/vetores; e2e_runtime aciona CLI instalada, relê resultados e cruza admission/journal/Core/Ops; science_real gera controles e métricas; soak intercala duplicatas/restarts/faults e confere effects/store. Dados semanais e retornos de sinal long fixo são sondas técnicas; não demonstram capacidade preditiva de uma estratégia. science_real.separated_with_ci verifica apenas limites inferiores não nulos, um critério parcial frente à promessa de IC completo.

Persistência própria: JSON, JSONL, XML e texto versionados; os scripts de teste leem SQLite criado por domínios em runtime. Não há DDL próprio observado nos 22 Python, 13 shell/PowerShell e 6 workflows examinados. Ausência limitada a esse espaço.

Governança implementada: capital_permission=False e training_started=False nos construtores de atestados/baselines; guard D-16 é local ao executor. Não confundir QUALIFIED operacional com edge ou autorização de capital. Alguns shells sem errexit anotam erros intermediários e podem terminar com exit0; interpretar logs/artifacts, não apenas job verde.
'''
study.save('relatorios/PRELIMINAR_'+project+'.md',pre)
study.log(project,p,'Salvar preliminar exclusivamente scripts/config/workflows após leitura semântica',0,'Preliminar anterior ao confronto narrativo',artifacts='relatorios/PRELIMINAR_'+project+'.md')
files=study.read(project,r/'evidencias'/project/'tracked-files.txt').splitlines()
own=[x for x in files if x.endswith(('.py','.sh','.ps1','.cmd','.bat','.yml','.yaml'))]
study.save('evidencias/'+project+'/coverage.json',[{'path':x,'status':'analisado em profundidade','scope':'código/script/workflow próprio'} for x in own])
catalog=[]
for rel in files:
 f=p/rel
 if rel not in own:
  catalog.append({'path':rel,'kind':'evidência histórica' if 'RAW_LOGS/' in rel or 'EVIDENCE/' in rel else 'contrato/governança/documentação','extension':f.suffix,'filesystem_mtime_utc':study.datetime.datetime.fromtimestamp(f.stat().st_mtime,study.datetime.timezone.utc).isoformat() if f.exists() else None})
study.save('evidencias/'+project+'/document-catalog.json',catalog)
study.log(project,p,'Catalogar não executáveis via tracked-files + stat mtime',0,str(len(catalog))+' catalogados',limits='mtime não é data histórica do documento; histórico seletivo',artifacts=project+'/document-catalog.json')
for rel in ['README.md','CLAUDE.md','qualification/COMMON_QUALIFICATION_CORE.md','qualification/ATTESTATION_SCHEMA.json','qualification/DECISIONS.json','qualification/crypto/GATES.json','qualification/crypto/FINDINGS.json','qualification/crypto/QUALIFICATION_ATTESTATION.json','qualification/crypto/FROZEN_PARAMETERS.json','qualification/crypto/QUALIFICATION_PROFILE_CRYPTO_V1.json','qualification/crypto/AUTHORITY_STATE_MATRIX.json']:
 text=study.read(project,p/rel)
 # Apenas impressão; originais narrativos não são incorporados à entrega.
 print('\nFILE '+rel+'\n'+text)
dest=r/'copias'/project
if not dest.exists():
 code,out=study.run(project,r,['git','clone','--no-hardlinks',str(p),str(dest)],project+'/execution-clone.txt',timeout=120)
 if code:raise SystemExit(code)
study.log(project,dest,'Verificar cópia: .git diretório e sem alternates',0,str((dest/'.git').is_dir() and not (dest/'.git/objects/info/alternates').exists()),limits='Original .git/worktrees existente='+str((p/'.git/worktrees').exists()))
study.log(project,dest,'Preflight estático comandos selecionados attest check/evidence_numbers',0,'Somente leituras relativas e escrita EVIDENCE_NUMBERS na cópia; jsonschema já disponível no runtime; sem HTTP, serviços ou bancos nestes comandos',limits='Demais scripts não executados: possuem clone/install/download/raízes absolutas; env não é impresso')
study.run(project,dest,[sys.executable if False else __import__('sys').executable,'-X','utf8','qualification/crypto/scripts/attest.py','check','qualification/crypto/QUALIFICATION_ATTESTATION.json'],project+'/attest-check.txt',timeout=30)
study.run(project,dest,[__import__('sys').executable,'-X','utf8','qualification/crypto/scripts/evidence_numbers.py'],project+'/evidence-numbers-run.txt',timeout=30)
