import json
import study
p='brasileirao-predictor'
d=study.ROOT/'evidencias'/p
notes=json.loads(study.read(p,d/'applications-semantic-notes.json'))
text='''# Suplemento Brasil: aplicação Python e testes

Fonte primária: árvore local com alterações de C:/BRASILEIRAO/brasileirao-predictor, HEAD f87806900d2aa3c5e267259a67f27ce56e18dc03. Não confundir esta época com interfaces alternativas ou main remoto. Este suplemento registra leitura semântica integral de 201 módulos em applications-semantic-notes.json; 107 testes adicionais foram lidos pelo agente shared e incorporados à cobertura. Não houve execução de pytest Brasil, Redis, provedores, coleta, banco original ou envio de apostas.

O caminho de previsão combina Elo, modelo de gols e ensemble xG opcional; o cache usa quantidade de partidas concluídas e hash de configuração. Essa chave não identifica correções que preservam a quantidade. O db.connect legado cria/migra esquema; inspeção por conexão comum não é universalmente somente leitura. A previsão formal e os envelopes Redis separam a identidade do pedido e a disponibilidade do resultado; os testes Redis exigem instância descartável explicitamente identificada e permanecem não executados neste estudo.

O collector_a1 persiste JSONL e depois espelha SQL sem transação comum. Hash de conteúdo demonstra integridade dos bytes sob o contrato, não autenticidade externa. O adapter legado TheOddsApiProvider e o decoder novo odds_api_snapshot possuem validação temporal diferente; fixtures de teste do legado incluem publicação posterior ao retrieved_at e marca de elegibilidade indevida após kickoff. O decoder novo valida raw, identidade, tipos finitos e ordenação temporal de forma mais estrita. Nenhuma dessas fixtures comprova recebimento real em produção.

price_strength reúne admissão histórica/live, preços independentes da casa candidata, estado mais recente sem ressuscitar cotação inválida, força xG temporal e cálculo de hurdle/custos. economic_search aplica protocolo fixo, embargo e reservas de capital em simulação. São cenários e regras implementadas, sem comprovação de lucro ou financiamento real. residual_gate mantém desenho pendente mesmo após critérios numéricos. A família protocol_v2 congela amostra conjunta de 900 eventos, escrow e métricas separadas OU/1x2; os testes fabricam os registros e os recibos. scientific_claim_authorized permanece False no cenário positivo de teste.

Os caminhos survival_test, verify_calibration, test_combinations e vorp_ridge exigem atenção científica específica: parâmetros atuais não garantem fit histórico; presença de jogadores pós-jogo e cadastro futuro podem entrar em atributos; buscas reutilizam holdout; fechamento sem ORDER BY pode depender da ordem das linhas. No survival_test os percentis individuais de CLV são impressos como IC95, sem serem intervalo da média. Em ou25_nested_replay a série de lucro reportada é bruta embora o score desconte fricção; cálculo Holm não implica aplicação no critério de seleção. Estes são limites observados no código, sem experimento econômico novo.

bet_log protege persistência e reconciliação de unidades/moedas com locks, mas capital_gate_status é aviso e add_bet não impõe uma autorização global de capital. Separadamente, evaluate_shadow_cohort.compute_verdict retorna capital_enabled=True quando seus critérios GO são cumpridos; o teste fabrica dez retornos positivos e também força evaluate(min_sample=1). Essa flag isolada não prova autorização conjunta de plugin, book, conta ou ordens reais. Não é correto afirmar que todo caminho do Brasil sempre retorna capital_enabled=False.

Os testes combinam oráculos algébricos úteis (gradiente independente, comparação de scoring Core, conservação/normalização, rejeição anterior a scoring), regressões que recompõem a própria implementação, checagem de textos/contagens e fixtures sintéticas. Há testes Windows de encerramento da árvore de subprocessos, sujeitos a plataforma; integrações Redis dependem de URL/run_id explícitos; provas de implantação e scheduler por substring não verificam processos ou tarefas registrados. O registro de 29 trials históricas irreproduzíveis é uma exceção explícita congelada, não recuperação de proveniência.

## Rastreabilidade

Cada módulo e bloco efetivamente lido consta em evidencias/brasileirao-predictor/applications-semantic-notes.json; arquivos applications-brazil-000.txt até applications-brazil-079.txt preservam números de linha do original, omitindo somente comentários e docstrings no agregado. Blocos 042..059 pertencem à revisão shared e estão em shared-brasil-tests-notes.json/coverage.json/review.md. REGISTRO.log registra leituras e SHA256; baseline.json, hashes.json e hashes do overlay delimitam a árvore examinada. Código próprio foi lido integralmente, não certificado apenas por AST. Os scripts operacionais possuem revisão separada, ainda em consolidação.
'''
study.save('relatorios/SUPLEMENTO_BRASIL_APLICACAO_TESTES.md',text)
study.log(p,d,'Suplemento aplicação e testes Brasil',0,'201 módulos own +107 shared; leitura integral sem pytest',artifacts='relatorios/SUPLEMENTO_BRASIL_APLICACAO_TESTES.md')
