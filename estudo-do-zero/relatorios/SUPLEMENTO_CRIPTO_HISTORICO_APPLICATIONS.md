# Cripto: revisão histórica da atribuição 2

Concluída a leitura semântica de 194/194 objetos da atribuição archive-derivation-assignment-2.json, nos blocos raw-source-archive-applications-000.txt a 036.txt. Não há pendentes nesta atribuição. Nenhum objeto histórico foi importado ou executado, e nenhum serviço, coletor, chave ou banco real foi acionado.

O método combina a base executável já integralmente revista pela equipe com todas as inserções, deleções e contexto do diff completo. Objetos sem base foram lidos integralmente. A cobertura separada registra caminho e SHA-256 de base e objeto; a reconstrução com todos os opcodes foi validada linha por linha. Diferenças vazias significam corpo executável equivalente à base, com proveniência própria, e não uma nova execução.

As notas detalhadas por objeto estão em evidencias/cripto-predictor/archive-derivation-2-notes.json; a cobertura está em archive-derivation-2-coverage.json. Leituras e verificação constam do REGISTRO.log. Esses arquivos são suplemento histórico e não alteram automaticamente a cobertura central ou a classificação da implementação atual.

A evolução preservada mostra versões com ausência de escrow dos inputs da previsão, reutilização de cache sem identidade de dados, datas de publicação inferidas a partir do evento, modelos HMM sem hash da amostra, CSV/JSONL sem transação ou bloqueio e contratos numéricos sem validação finita. Outros objetos retiram controles de congelamento ou de calibração no paper trader/adapter. Esses comportamentos pertencem aos hashes históricos citados nas notas; não constituem achados atuais por transferência.

Os relatórios antigos de paper trading somam retornos logarítmicos e podem compor operações sobrepostas sem carteira ou financiamento comum; funding constante multiplicado por horizonte e custos fixos são proxies. Ausência de observações convertida em zero não demonstra lucro zero. Os testes sintéticos e controles positivos plantados avaliam sensibilidade e invariantes declarados; não provam desempenho causal ou capital autorizado.

Utilitários preservados de migração, empacotamento, coleta, restauração e consolidação Git têm efeitos concretos se invocados. Foram somente lidos. Números literais de testes e resultados neles escritos são declarações históricas do código e não testes executados neste estudo. O subconjunto de experimentos de unidades, relógios e ledger preserva incerteza e bloqueia F03/F04 quando faltam identidade econômica, regra de payoff, disponibilidade histórica ou sincronização de relógios.

Limite: revisão estática integral por derivação verificável; não houve teste de execução destes 194 objetos, validação dos mercados externos ou nova atestação econômica.
