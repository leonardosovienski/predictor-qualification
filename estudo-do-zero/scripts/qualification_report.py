import study, pathlib, json
r=study.ROOT; pr='predictor-qualification'; p=pathlib.Path('C:/QUALIFICACAO/predictor-qualification'); base=json.loads((r/'evidencias'/pr/'baseline.json').read_text(encoding='utf-8'))
latest=json.loads(study.read(pr,p/'qualification/crypto/ATTESTATION_PARTIAL_v1-1-attestation.json'))
att=json.loads(study.read(pr,p/'qualification/crypto/QUALIFICATION_ATTESTATION.json'))
study.save('evidencias/'+pr+'/attestation-epochs.json',{'final':{'result':att['result'],'generated_at':att['generated_at'],'common_baseline_id':att['common_baseline_id'],'final_commits':att['final_commits'],'counts':att['counts']},'partial_v1_1':{'result':latest['result'],'generated_at':latest['generated_at'],'common_baseline_id':latest['common_baseline_id'],'final_commits':latest['final_commits'],'counts':latest['counts']}})
txt='''# Inventário — predictor-qualification

Fonte: C:\\QUALIFICACAO\\predictor-qualification, HEAD f21bbbcccb06252cd5bc156c4093d571d03f0933. Branch main, árvore limpa na linha de base. main remoto é outra identidade; conferir LINHA_DE_BASE. Toda caracterização preliminar está congelada em PRELIMINAR_predictor-qualification.md. Este inventário não transfere seus atestados para os sete checkouts locais examinados.

## A–D. Propósito, estrutura, tecnologia e interfaces

OD: coleção de executores de investigação/qualificação e registros públicos. Sem manifest raiz installável na listagem rastreada. Seus entrypoints são arquivos scripts: coleta baseline, truth_map, check/build attestation, cleanroom, E2E/science/soak e sondas Ops. Python stdlib, jsonschema no validador, bibliotecas dos domínios/Core/Ops no runtime; Git, gh, curl, uv e Bash nos executores. PowerShell keep_awake mantém execução Windows acordada por processo. O diretório qualification/<domínio> é organização de evidência, não serviço de pesquisa.

Pontos de leitura: qualification/shared/scripts/collect_stack_baseline.py (collect_repo e verify_stack_wheels), cleanroom_baseline.py (Log/main/wheel_digest), qualification/crypto/scripts/attest.py (build/check/write), evidence_numbers.py (main/junit), runtime_cleanroom.sh e d16_linux.sh; outros scripts têm índice de símbolos em source-index.json. Não foram invocados comandos encontrados nesses documentos.

## E–F. Configuração e persistência

OD: cleanroom usa plano JSON com repo/sha/wheels/hashes/suites/limits; usa CLEANROOM_UV, RUNNER_TEMP, UV_* e CLEANROOM_GUARD_*. Scripts Windows usam caminhos absolutos C:/QUALIFICACAO/tools, C:/Cripto/qualificacao, inclusive caches fora de cwd. Não devem ser executados indiscriminadamente nem mesmo após clone. d16_linux lê DECISIONS e runtime_target; exige APPROVED. build_real_dataset baixa publicamente data.binance.vision, confere checksum e grava raw/MANIFEST/datasets fora do repo. Não houve download de datasets nesta investigação.

Persistência de evidência: JSON/JSONL/XML/log, hashes, Git e artefatos do Actions. DDL próprio não encontrado no espaço de 22 Python, 13 shell/PowerShell e 6 workflows; scripts E2E/soak abrem SQLite do domínio produzido em ambiente de teste. Nenhum banco original foi aberto nesta investigação. real_env preserva bytes dos datasets mediante MANIFEST e CAS e deriva vetores de futuro, disponibilidade inválida e direção aleatória.

## G–H. Lógica e fluxos

Fluxo baseline: configuração de raízes → Git/manifests/lock → API CI/releases → cruzamento lock/hash asset → JSON/log. A coleta usa refs locais e deve ser distinguida da consulta main remota; o script original não faz essa distinção do modo exigido por este estudo.

Fluxo cleanroom: plano congelado → clone do commit → lock/export → download de wheel → duas instalações independentes published/head_build → introspecção módulos/plugin/script → testes em árvore sem diretório pacote → fatos/JUnit/guard → comparação da wheel. Observação: guard apenas grava origens, não torna a suíte vermelha ao achar módulo externo; o consumidor precisa aplicar gate. clone, instalações, rmtree e git clean fazem deste executor mutável. Não o executamos integralmente.

Fluxo atestado: GATES e FINDINGS → hashes e contagens → schema + regras parciais → JSON novo. check reconta P0/P1/P2 atuais e hashes dos gates; não confirma sozinho releases, todos ambientes, contratos domínio, supersession ou semântica científica. Relação hash correta prova identidade, não verdade do conteúdo.

Fluxo Crypto runtime: runtime_target → wheel/hash/deps → CLI instalada → request → admission/journal/Core/Ops/effect/result → reinício/show → conferência de hashes e IDs. science_real usa controles negativos; separated_with_ci só verifica dois limites inferiores não nulos. A presença de limites superiores coerentes não está testada por esse predicado. d16_finalize confere strings de identidade em env.log e valores de JSON; não torna os JSONs prova independente de experimento. Conformance JUnit considera só primeira suite quando testsuites, não exige explicitamente tests>0; risco de aceitar fixture vazia/multissuíte não ensaiado nesta sessão.

soak.py implementa 20 ciclos normais, 5 duplicatas, 5 restarts e falhas/retries, mas o perfil JSON lista morte do host Ops e corrupção de resultado como classes próprias. A leitura do harness examinado não encontrou execução explícita dessas duas classes no soak.py; elas podem existir em suítes separadas. Isso é divergência de cobertura do harness, não prova de ausência no stack. Ver stdout/exit do domínio e logs: shells set -uo pipefail sem -e continuam após alguns erros e podem concluir com exit0 mesmo com evidência de subcomando falho.

## I–J. Testes e operação

ET-RUN: em clone --no-hardlinks independente, evidence_numbers.py terminou exit0 e gerou JSON semanticamente igual ao original. É recomputação de logs antigos; não executou as milhares de asserções históricas que resumiu. Falhas históricas anteriores permanecem no arquivo gerado (ex.: baseline com quatro falhas e execução de método corrigida). attest.py check terminou exit1 por ModuleNotFoundError jsonschema; checagem oficial NV. Sem instalação de dependências.

ET-RUN: verificador independente de contagem/hash em cópia mostrou P0=0, P1=0, P2=6; counts_match false para o final local; 12 referências de gates têm SHA divergente. A verificação adicional nos originais confirmou os mesmos bytes da cópia: não é transformação de checkout. Evidências: recomputed-attestation.json e hash-mismatch-original-check.json. O final é da época STACK_BASELINE_V1 e há parcial mais recente v1-1 com outra identidade. Portanto o conflito é atestado histórico versus árvore atual, não uma sentença sobre validade no commit original de emissão ou sobre atestado remoto de 30/09. Próxima verificação é recomputar no commit de emissão, cujo contexto deve ser fixado.

OD workflows: contents:read; runtime e matriz usam uv0.12.1 e Python3.13; provision script fixa uv0.12.18. cleanroom lê uv do plano. CI inclui upload-artifact, triggers por paths e workflow_dispatch, matrizes Linux/Windows, limites de duração. Metadados atuais consultados anonimamente em ci-head-local.json e ci-main-remoto.json; não confundir execução API remota com ET-RUN. Não acionamos Actions.

## K–L. Confronto e artefatos em uso

DD README declara evidência pré-treinamento e ausência de código de produção: concorda com scripts diagnósticos observados. Núcleo promete qualificação confiável e enums/regras de autoridade: existe implementação parcial nos scripts, mas a validade financeira e científica não decorre dos gates. DD núcleo C7.1 possui oito regras; attest.check implementa subconjunto, como docstring admite. C24/Etapa B/V2 são narrativa nesta fonte local, sem diretório integration executável examinado. GATES/FINDINGS/atestado/RAW_LOGS são registros a contextualizar, não oráculo.

Anexo A: papel geral é compatível; datas/versões/requalificações atuais não podem ser confirmadas por esta árvore anterior. DECISIONS local contém D-1..D-15 e D-17, sem D-16 aprovada e sem D-27/D-29/30/31 na lista lida. Busca delimitada a campo decision_id dos registros atuais deste arquivo; main remoto não foi baixado nem estudado em conteúdo. Não atribuir ausência ao servidor remoto. Fontes instaladas e serviços ativos NV: não importados nem consultados.

## Cobertura e limites

Código próprio executável: 22 Python, 12 shell e 1 PowerShell, seis workflows lidos integralmente e revisados por responsabilidade/efeitos/configuração/erros. Índice e coverage por arquivo estão em evidencias/predictor-qualification. Schema, core de governança, DECISIONS, GATES/FINDINGS, final e parcial selecionado, parâmetros/perfil/matriz de autoridade lidos. Histórico repetitivo catalogado, aprofundado apenas quando sustenta recomputação. Não há teste de domínio real, instalação cleanroom, Linux primário, acesso dados privados, prova financeira, ou implantação observada. Integração V2 remota e ciclo D27 permanecem fora do conteúdo local estudado.
'''
study.save('relatorios/INVENTARIO_'+pr+'.md',txt)
diagrams={
'qual-componentes':'''flowchart LR
 Plano[Planos JSON] --> Coletor[collect_stack_baseline]
 Git[Git e API publica] --> Coletor
 Coletor --> Baseline[Baseline JSON e logs]
 Plano --> Cleanroom[cleanroom_baseline]
 Cleanroom --> Facts[Facts JUnit e guard]
 Gates[GATES e FINDINGS] --> Attest[attest build check]
 Arquivos[Evidencias por hash] --> Attest
 Attest --> Atestado[Atestado JSON]
''',
'qual-sequencia-coleta':'''sequenceDiagram
 participant Dono
 participant Coletor as collect_stack_baseline
 participant Git
 participant API as GitHub API
 participant Arquivos
 Dono->>Coletor: argumentos e raizes configuradas
 Coletor->>Git: HEAD status manifests locks
 Coletor->>API: runs releases assets publicos
 Coletor->>Coletor: comparar identidades e hashes
 Coletor->>Arquivos: baseline JSON e log
''',
'qual-sequencia-atestado':'''sequenceDiagram
 participant CLI
 participant Gates as GATES e FINDINGS
 participant Attest as attest.py
 participant Evidencias
 participant JSON
 CLI->>Attest: partial ou final
 Attest->>Gates: ler estados e findings
 Attest->>Evidencias: verificar existencia e calcular hashes
 Attest->>Attest: schema e check parcial
 alt arquivo novo e check OK
 Attest->>JSON: gravar atestado
 else conflito ou problema
 Attest-->>CLI: erro e recusa escrita
 end
''',
'qual-sequencia-runtime':'''sequenceDiagram
 participant Shell as runtime_cleanroom
 participant Wheel
 participant CLI as cripto-research instalado
 participant Stores as admission journal resultados
 participant Probe as e2e science soak
 Shell->>Wheel: baixar conferir hash instalar
 Probe->>CLI: pedido em novo processo
 CLI->>Stores: processamento e persistencia
 Probe->>CLI: show em novo processo
 Probe->>Stores: conferir ids hashes estado
 Probe-->>Shell: JSON logs exit
''',
'qual-estados':'''stateDiagram-v2
 [*] --> IN_PROGRESS: partial
 IN_PROGRESS --> QUALIFIED: gates PASS e zero bloqueantes
 IN_PROGRESS --> NOT_QUALIFIED: gates FAIL ou findings bloqueantes
 IN_PROGRESS --> BLOCKED: DD nucleo impedimento externo
 [*] --> ABORTED: DD nucleo C0 falhou
 QUALIFIED --> [*]
 NOT_QUALIFIED --> [*]
''',
'qual-schema':'''classDiagram
 class Attestation {
 string common_baseline_id
 string common_core_sha256
 array final_commits
 array final_wheels
 object gates
 object counts
 boolean capital_permission
 string result
 }
 class Gate {
 string status
 array evidence
 }
 class Evidence {
 string file
 string sha256
 }
 Attestation --> Gate
 Gate --> Evidence
'''}
doc='# Como funciona predictor-qualification\n\nFonte local e limites no INVENTARIO. Abaixo nós OD de scripts/esquemas; BLOCKED/ABORTED do diagrama de estados são DD do núcleo, explicitamente marcados. Nenhum diagrama é observação de serviço ativo.\n'
for name,text in diagrams.items():
 study.save('relatorios/docs/diagramas/'+name+'.mmd',text)
 doc+='\n## '+name+'\n\n```mermaid\n'+text+'```\n\n'
doc+='O contexto do repositório é evidência versionada. As sequências mostram coleta, construção de atestado e prova de runtime; cada execução pode gravar artefatos e por isso exige ambiente independente. O esquema representa objetos JSON, sem banco próprio demonstrado. QUALIFIED combina estados documentais e checks de identidade; não é previsão validada nem capital autorizado.\n'
study.save('relatorios/docs/COMO_FUNCIONA_'+pr+'.md',doc)
rows=[]
for comp,purpose,impl,test in [('baseline','Fixar fontes e wheels','collect_stack_baseline.collect_repo','ET-SRC coletor; API remota observada nesta investigação'),('cleanroom','Separar wheel publicada e build HEAD','cleanroom_baseline.main / cleanroom_guard.py','ET-SRC harness; execução completa NV'),('attestation','Consolidar gates/hashs','attest.build/check/write','ET-RUN oficial ERROR jsonschema; independente counts/hash conflito época'),('numbers','Recomputar logs históricos','evidence_numbers.main','ET-RUN exit0 JSON igual original'),('crypto-runtime','Sondar E2E ciência operação','e2e_runtime/science_real/soak','ET-SRC executores; testes domínio agora NV')]:
 rows.append({'Projeto':pr,'Componente':comp,'Propósito':purpose,'Implementação':'OD '+impl,'Testes':test,'Uso':'ET-HIST registros locais associados a épocas; uso atual NV','Estado':'implementado; limites no inventário','Limitações':'não provar edge; fonte local anterior remoto','Evidências':'predictor-qualification/source-index.json; INVENTARIO_predictor-qualification.md; REGISTRO.log'})
study.save('evidencias/'+pr+'/components.json',rows)
ints=[]
for target,mechanism,contract in [('core-predictor','imports de predictor_core em sondas e dependência em planos','TrialRegistry e contratos trial'),('predictor-ops','imports run_job/probes e wheels em CI','JobConfig/runtime/events'),('cripto-predictor','wheel CLI conformance CAS/journal/readback','runtime_target e request/result Crypto'),('cain','clone Git/wheel por plano cleanroom','plan sha/wheels/paths'),('ecosystem-predictor','clone Git/build packages por plano','plan sha/wheels'),('brasileirao-predictor','clone Git/wheel por plano','plan sha/suites'),('stocks-predictor','clone Git/wheel por plano','plan sha/suites')]:
 ints.append({'Origem':pr,'Destino':target,'Mecanismo':mechanism,'Informação':'identidades fontes/pacotes; entradas de sondas; resultados de teste','Contrato':contract,'Implementação':'OD scripts de qualificação','Testes':'ET-SRC harness; reexecução domínio NV','Uso':'ET-HIST arquivos locais, fonte atual NV','Evidências':'qualification/shared/scripts/collect_stack_baseline.py; cleanroom_baseline.py; source-index.json'})
study.save('evidencias/'+pr+'/integrations.json',ints)
study.save('evidencias/'+pr+'/findings.json',[
 {'priority':'alta','certainty':'OD + ET-RUN','claim':'Atestado final local não confere contra árvore atual em contagens e 12 referências de gate; parcial V1.1 possui outra época','evidence':'recomputed-attestation.json; attestation-epochs.json; hash-mismatch-original-check.json','limit':'Não prova inválido no commit de emissão nem no main remoto'},
 {'priority':'alta','certainty':'OD','claim':'attest.check verifica subconjunto das oito regras C7.1; schema/hashs não provam semântica científica','evidence':'qualification/crypto/scripts/attest.py check; COMMON_QUALIFICATION_CORE.md C7.1','limit':'Outros gates podem aplicar verificações adicionais'},
 {'priority':'média','certainty':'OD','claim':'science_real.separated_with_ci não verifica upper endpoints de IC; d16_finalize first JUnit suite e sem piso tests>0 explícito','evidence':'science_real.py main; d16_finalize.py main','limit':'Risco por leitura, não explorado com fixture'},
 {'priority':'média','certainty':'OD/DD','claim':'Perfil soak declara corrupção e morte host Ops como classes, não encontradas como execução explícita em soak.py','evidence':'QUALIFICATION_PROFILE_CRYPTO_V1.json; soak.py','limit':'Suítes separadas podem cobrir, não afirmar ausência total'},
])
study.log(pr,p,'Salvar inventário/docs diagramas/matrizes parciais após confronto e recomputação',0,'Relatório individual salvo',artifacts='relatorios/INVENTARIO_predictor-qualification.md; docs/COMO_FUNCIONA_predictor-qualification.md; components.json; integrations.json; findings.json')
print('Qualification reports saved; latest partial:',latest['result'],latest['common_baseline_id'])
