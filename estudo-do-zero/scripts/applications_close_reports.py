import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent));import study
for p in ['cain','stocks-predictor']:
 path='relatorios/INVENTARIO_'+p+'.md';t=study.read(p,study.ROOT/path)
 if p=='cain':
  t=t.replace('Revisão integral de todos os módulos próprios, ferramentas e fixtures ainda pendente.','A revisão semântica dos módulos próprios executáveis selecionados, ferramentas, testes e UI foi concluída; artefatos estáticos e dependências têm catálogo separado.')
  t=t.replace('Módulos avaliação/tools/JS e branches secundárias ainda precisam revisão integral por módulo.','Avaliação, ferramentas e UI foram revisadas integralmente na árvore local; branches secundárias e remoto não herdam essa cobertura.')
  marker='## Cobertura e pendências'
 else:
  t=t.replace('ainda parcial quanto à revisão semântica integral','com revisão semântica integral dos executáveis próprios selecionados concluída')
  marker='## Cobertura pendente'
 t=t.split(marker)[0]+'## Cobertura e limites finais\n\nA cobertura consolidada está em `evidencias/'+p+'/coverage.json` e as notas por módulo em `module-notes.json`. Todos os executáveis próprios selecionados foram revisados semanticamente. Lock, fixtures estáticas e código de terceiros são catalogados com essa profundidade distinta. Histórico e fontes remotas não recebem certificação por transferência desta revisão. Nenhum banco original, modelo vivo ou serviço externo foi acionado.\n\nLeitura de testes (ET-SRC), execuções isoladas (ET-RUN), CI por commit e declarações históricas permanecem separados. Consulte `SUPLEMENTO_CAIN_STOCKS_COBERTURA_FINAL.md` para a contagem exata e limites das execuções.\n'
 study.save(path,t)
 guide='relatorios/docs/COMO_FUNCIONA_'+p+'.md';g=study.read(p,study.ROOT/guide)
 g=g.replace('com cobertura pendente explícita','com cobertura final discriminada em coverage.json')
 g+='\n## Limites da revisão concluída\n\nA revisão semântica dos executáveis próprios selecionados desta árvore foi concluída. Esse estado não certifica instalação, modelo vivo, dados de mercado ou lucro. Notas e hashes por arquivo delimitam exatamente a fonte examinada; fontes remotas e versões posteriores exigem sua própria revisão. Consulte o suplemento final de cobertura para testes executados e apenas lidos.\n'
 study.save(guide,g)
 f=json.loads(study.read(p,study.ROOT/'evidencias'/p/'findings.json'));f=[r for r in f if 'pendente' not in r.get('afirmação','')]
 if p=='stocks-predictor':
  for assertion,evidence in [('Ledger prospective verifica ligações mas não recalcula hash do payload JSON','prospective_big_winner.verify_chain; shared-review-notes.json'),('Maturidade prospective é declarada pelo argumento horizon=12 sem comprovar tempo decorrido','prospective_big_winner; shared-review-notes.json'),('Teste de idempotência RJ contém comparação tautológica','tests/test_rj_audit_2026_08_24.py:test_persist_run_updates_row_when_asof_advances linhas340 e349'),('Outcome TOTALRETURN não exige série alcançar 12 meses','experiments/BIG_WINNER_DETECTION_V1/lib/outcome_stage.py:calculate_path_outcome; remaining-00.txt'),('Compra ETF rejeitada mantém previous_target true e não tenta de novo até mudança de alvo','monthly_etf; shared-review-notes.json e tests/test_monthly_etf.py')]:f.append({'projeto':p,'prioridade':'P2','certeza':'OD/ET-SRC','afirmação':assertion,'evidência':evidence,'próximo_passo':'Teste dirigido em cópia e revisão do contrato antes de promoção científica.'})
 study.save('evidencias/'+p+'/findings.json',f)
 study.log(p,study.ROOT,'Relatórios ajustados para cobertura final, sem certificação operacional/econômica',0,'Guias/inventário/findings atualizados',artifacts=path)
counts={p:len(json.loads(study.read(p,study.ROOT/'evidencias'/p/'coverage.json'))) for p in ['cain','stocks-predictor']}
study.save('relatorios/SUPLEMENTO_CAIN_STOCKS_COBERTURA_FINAL.md',f'''# Cobertura final — CAIN e Stocks

A revisão semântica dos executáveis próprios selecionados das duas árvores locais foi concluída. `coverage.json` discrimina {counts['cain']} entradas CAIN e {counts['stocks-predictor']} Stocks. Essa contagem inclui configurações e artefatos catalogados; não equivale a número de módulos de produção. CAIN inclui cinco arquivos adicionais não rastreados de testes/fixture. O módulo não rastreado claim_tables foi revisado e consta nas notas e hashes próprios.

CAIN: agentes, roteamento, contexto, persistência, Snapshot/Bundle, grounding, historian, análise, workflows, providers, avaliação, UI, ferramentas, CI e testes lidos integralmente. Os 65 arquivos de testes rastreados, dois harnesses POSIX e cinco arquivos locais adicionais foram revisados por shared; notas preservadas em shared-test-notes.json e shared-untracked-test-notes.json. Nenhuma suíte CAIN nem modelo vivo foi executado. Asserções com FakeLLM, vetores sintéticos, código apenas AST, fixtures HTTP falsas e testes com skip/importorskip não certificam qualidade de respostas reais.

Stocks: pacote central, experimentos executáveis, ferramentas, CI e testes lidos integralmente. Os blocos remaining00..13 foram revisados por applications; remaining14..18 por root. As notas duráveis constam em module-notes.json e root-tools-notes.json. Testes de custo, caixa, cotação, D+1, atomicidade, documentação e gates usam majoritariamente dados sintéticos ou fixtures locais. Nenhum pytest/Core/PyYAML nem recomputação econômica foi executado no estudo.

Execuções Stocks em cópia Git independente, com Python3.13.14: onze checks stdlib de aritmética/contratos; seis checks sintéticos do simulador; unittest TOTALRETURN 18/18 e PRICE 33/33. Root executou check_project_files e verify_operational_evidence com PASS na mesma época local. A execução anterior de onze checks em Python3.12 foi preservada como evidência distinta. Logs e receipts individuais estão em evidencias/stocks-predictor. Esses PASS verificam somente os caminhos exercitados e não promovem capital nem certificam lucro ou dados vivos.

Limites científicos: lift/enrichment sobre índice de preço exclui distribuição em caixa; total-return, marcação de direitos, dinheiro liquidado e resultado financiável são grandezas diferentes. Declaração de maturidade, hash de código, assinatura de aprovação e recebimento de fonte não substituem comprovação temporal independente. RJ tem inferência primária por empresa, ownership indisponível e inferência secundária repetida bloqueada. Poder Gaussian plantado e haircut não constituem validação empírica fora da amostra.

Identidade: CAIN local dirty 24f784c e Stocks local 5cf27f são épocas específicas. Manifestos main remotos e versões do Anexo são comparados pela raiz em evidência separada; a diferença de versão local não refuta o main atual. Nenhuma conclusão desta cobertura certifica automaticamente fonte alternativa, build instalado ou serviço ativo.
''')
