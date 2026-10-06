import study,json
r=study.ROOT
f=r/'evidencias/predictor-qualification/findings.json';rows=json.loads(f.read_text());rows[0].update(claim='Atestados possuem épocas distintas: 94/94 referências do final e 100/100 do parcial conferem nos commits de emissão; 12 referências antigas diferem dos arquivos atuais',evidence='attestation-issuance-check.json; issuance-ATTESTATION_PARTIAL_v1-1-attestation.json; hash-mismatch-original-check.json',limit='Hashes no commit de emissão não reexecutam os gates nem autenticam conclusões científicas; diferença atual não demonstra corrupção histórica',prioridade='P2',certeza='OD + ET-RUN de hashes');study.save('evidencias/predictor-qualification/findings.json',rows)
inv=r/'relatorios/INVENTARIO_predictor-qualification.md';text=inv.read_text();start=text.find('ET-RUN: verificador independente de contagem/hash');end=text.find('\n',start)
if start>=0:text=text[:start]+'ET-RUN: a comparação inicial contra a árvore atual encontrou 12 referências divergentes, sem transformação da cópia. A investigação de proveniência verificou Git blobs nos commits de emissão: final em 800d4d1211b439144d48138bed629a826ef21295 tem 94/94 referências corretas; parcial V1.1 em ed5375d57984cae44f052775d4a525d11c9704b1 tem 100/100. O final primário é NOT_QUALIFIED; o parcial é IN_PROGRESS. As diferenças posteriores são de época e não invalidam a emissão por si mesmas. Não foi reexecutado o validador oficial completo, limitado por dependências. Evidências: attestation-issuance-check.json, issuance-ATTESTATION_PARTIAL_v1-1-attestation.json, hash-mismatch-original-check.json.'+text[end:];study.save('relatorios/INVENTARIO_predictor-qualification.md',text)
state=json.loads((r/'evidencias/RETOMADA_PENDENCIAS_EXATAS.json').read_text());table='\n'.join(f"|{x['assignment']}|{x['total']}|{x['reviewed']}|{len(x['pending'])}|" for x in state['assignments'])
handoff='''# Ponto de retomada — estudo dos oito projetos

**PAUSADO A PEDIDO DO USUÁRIO. O estudo não está concluído.** O usuário informou 5% do limite semanal restante e pediu salvar o que foi feito e o que faltou. Não iniciar outra revisão nesta sessão.

## Começar daqui

Leia este arquivo, `RELATORIO_GERAL.md` e `../evidencias/RETOMADA_PENDENCIAS_EXATAS.json`. O pedido original integral está no anexo `<USER_PROFILE>/.codex/attachments/68f7a209-51c6-4c39-bab0-9953110e96fd/Texto colado.txt`. Não reler fontes já certificadas só para recompor contexto. Os preliminares foram salvos antes da interpretação e devem permanecer preservados.

## Feito

- Identificação das oito raízes, commits/status, hashes de arquivos rastreados e não rastreados aplicáveis; inventários/preliminares; clones independentes. Leituras nos originais foram somente leitura; ensaios mutáveis apenas em cópias após preflight.
- Revisão semântica dos executáveis ativos, testes, scripts, contratos, configurações e CI registrados pelos quatro responsáveis. CAIN e Stocks encerrados; Core, Ops, Ecosystem e Qualification encerrados nas suas fontes. Crypto fonte ativa, 75 scripts e 169 testes encerrados. Brasileirão Python/testes, 124 scripts e 34 C#/.NET encerrados; .NET sem execução. Falta reconciliar os registros individuais no inventário global antes afirmar cobertura integral do estudo.
- Matrizes em MD/CSV/JSON com colunas exigidas; relatório provisório, oito guias de funcionamento/aprendizado, arquitetura/glossário/guia de leitura e diagramas Mermaid. São entregáveis em progresso, com últimas descobertas ainda por integrar.
- Identidades remotas, versões/locks/wheels, Anexo, releases, CI e decisões discriminadas por commit. Todos os oito HEADs originais diferem do main remoto. D27 remoto APPROVED não é refutado pelo atestado NOT_QUALIFIED de outra época local.
- Ensaios leves de engenharia em cópias, com recibos e falhas preservadas. Stocks check_project/verify_operational_state e smoke/unittests; Crypto probes contratos/PIT/numpy/backup; Core/Ops/Eco smokes e drift offline. Não executar nem apresentar suites completas/harness econômicos como concluídos; ausência pytest/jsonschema e metadata instalada limita alguns controles. Nenhuma instalação, serviço, coleta de mercado, treinamento ou capital acionado.
- Proveniência Qualification: 94/94 referências do final corretas no commit800d4d12; 100/100 parcial no ed5375d5. As12 diferenças contra árvore atual são posteriores à emissão; não inferir corrupção. Validador oficial completo não reexecutado.
- Preservação repetida ao salvar: HEAD/status e11.ª linha de base de hashes dos oito originais conferidos, 9.888 arquivos rastreados sem diferença (ver preservation-summary.json; conferir soma no artefato). Estados sujos preexistentes de CAIN/Brasileirão preservados. Isso é comparação de bytes/estado, não monitor contínuo de metadados.

## Faltou: revisão histórica Crypto

Os arquivos históricos não são o código ativo. Reusar base já semanticamente integral e ler todas diferenças executáveis; SHA/catálogo/AST sozinho não é leitura. Não executar arquivos históricos, inclusive scripts top-level de coleta, instalação, migração, publicação e empacotamento.

|Partição|Total|Certificados|Pendentes|
|---|---:|---:|---:|
'''+table+'''

Lista exata por índice/path/base em `../evidencias/RETOMADA_PENDENCIAS_EXATAS.json`. As partições são `archive-derivation-assignment-0..3.json`; `archive-derivation-plan.json` e `archive-executable-map.json` registram origem/bytes/diffs. Partição2 applications está totalmente fechada. Partição1 shared tem índices40..192 completos; 0..39 pendentes. Partição3 root tem blocos000..006 e021..034 fechados (163 objetos); os30 objetos dos blocos007..020 ficaram para domains e devem ser conferidos contra sua cobertura final. Partição0 consultar JSON de pendências atualizado, sem supor conclusão por mensagens antigas.

Root preparou `archive_root_chain.py`, chain-plan/index e raw-source-chain-root, mas essa alternativa **não é cobertura certificada** e não deve ser usada como conclusão. Root leu chain000/001 adicionalmente, porém não os registrou como objetos encerrados; retomar pelo índice original archive-root-review-index, não pela cadeia experimental. Arquivos root035..043 antigos são resíduos de preparação, fora do índice vigente000..034.

## Faltou: consolidação e entrega final

1. Fechar apenas históricos pendentes; reconciliar hashes/path/disjunção das coberturas, reuso byte-idêntico/LF e base integral. Verificar classes de executáveis dos oito inventários e registrar lacunas sem promovê-las mecanicamente.
2. Mesclar coberturas Brasil scripts: root-scripts-coverage.json (75), shared-brasil-scripts-coverage.json (35), applications-brasil-scripts-coverage.json (14). Mesclar testes/shared/apps e Crypto histórico/ativo separadamente. Notas em evidencias são autoridade; suplementos em relatorios preservam interpretação.
3. Atualizar inventários, findings, componentes/integrações, matrizes e relatório/arquitetura/guias. Separar problemas atuais de versões históricas corrigidas. Explicar limitações quantitativas, PIT, validade/receipts, execução e capital sem transferir ET-HIST para ET-RUN.
4. Conferir links locais, diagramas incorporados e arquivos .mmd; existem documentos de agentes na raiz/docs além de relatorios/docs que precisam reconciliação. Conferir colunas e equivalência MD/CSV/JSON. Remover G-COBERTURA só após reconciliação concluída.
5. Repetir preservação dos originais, scan/manifesto de publicação, git diff --check, commit/push exclusivo branchautorizado e igualdade HEAD/remoto. Nunca PR/main/merge. Marcar relatório concluído somente então.

## Ambiente e publicação

Raiz: pasta pai deste relatório (`outputs/estudo-do-zero`). Python3.12 bundled `<USER_PROFILE>/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe` possui numpy/pydantic e não pytest/jsonschema. Python3.13 stdlib `C:/QUALIFICACAO/tools/python/cpython-3.13.14-windows-x86_64-none/python.exe`. Usar `-X utf8 -B`; não instalar. `study.py` registra leituras/comandos em REGISTRO.log append-only. Git original GIT_OPTIONAL_LOCKS=0; SQLite original mode=ro.

Publicação independente em `../publicacao/predictor-qualification`, branch`estudo-do-zero-2026-09-30`. Último marco antes deste checkpoint:97b49de26253a5ada7b2668d93bbc13c741c51af, confirmado remoto. `publish.py` copia lista explícita de textos sanitizados, exclui cópias/env/raw-sources/datasets; verificar publication-manifest e publication-verification para este novo checkpoint. Permissão de publicar exclusivamente esse branch veio do mandato. Preliminares e evidências históricas não reescrever para fabricar conclusão.

## Comandos de retomada

`archive_display.py` gera diff completo por partição/intervalo para leitura; não certifica leitura. `archive_root_notes.py` contém notas root por bloco e registra cobertura após leitura efetiva. `save_resume.py` recalcula pendências a partir das coberturas persistidas. `preservation.py` compara originais; `consolidate.py` gera matrizes; `publish.py` cria commit e precisa push separado. Não invocar wrappers originais, automações ou scripts mutáveis dos projetos.
'''
handoff=handoff.replace('11.ª linha de base de hashes','hashes da linha de base').replace('9.888 arquivos','9.888 arquivos')
study.save('relatorios/CONTINUIDADE.md',handoff);study.save('relatorios/RETOMAR_AQUI.md',handoff)
study.log('CONTINUIDADE',r,'Salvar ponto retomada por pedido explícito usuário limite semanal5%',0,'Estado incompleto e tarefas futuras discriminados',limits='Pausa do estudo solicitada; nenhuma alegação conclusão integral',artifacts='relatorios/CONTINUIDADE.md; relatorios/RETOMAR_AQUI.md; evidencias/RETOMADA_PENDENCIAS_EXATAS.json')
print('Ponto retomada salvo')
