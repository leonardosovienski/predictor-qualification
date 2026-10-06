import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent));import study
D={
'cain-componentes':'''flowchart TD
 CLI[cain.cli e MCP] --> R[cain.runtime]
 WEB[Web e cain.api] --> R
 R --> C[Cain.run]
 C --> I[IdentityService]
 I --> S[SQLiteIdentityStore]
 I --> M[LexicalMemoryIndex derivado]
 C --> A[AgentRegistry: busca codigo resumo conversa]
 C --> L[SQLiteDecisionLog]
 A --> P[OllamaLLM ou FakeLLM]
 A --> Q[SearchProvider]
 WEB --> W[WorkspaceStore]
 WEB --> RS[ResearchService Snapshot]
 RS --> B[BundleService e Objects CAS]
 RS --> H[Historian e analysis]
 H --> P
 RS --> F[Workflows]
 F --> H
''',
'cain-conversa':'''sequenceDiagram
 participant U as CLI ou API
 participant W as WorkspaceStore
 participant C as Cain.run
 participant I as IdentityService
 participant A as Agent escolhido
 participant P as LLM opcional
 participant D as DecisionLog
 U->>W: validar projeto e sessao; claim_run na API
 U->>C: payload e ids
 C->>I: observe e context_for
 I-->>C: identidade e contexto autorizado
 C->>A: Message por rota
 opt Geracao necessaria
 A->>P: prompt e contexto
 P-->>A: response ou erro
 end
 A-->>C: texto
 C->>D: mediated com response_hash
 C->>I: persistir interacao
 C->>D: completed e outcome na API
 D-->>W: run_receipt ready
 W-->>U: resposta; restore_turn sem nova geracao
''',
'cain-pesquisa':'''sequenceDiagram
 participant O as Operador
 participant S as ResearchService
 participant P as Politica receptor
 participant D as SQLite
 participant A as Analysis ou Historian
 participant L as Ollama local
 O->>S: ingest snapshot relativo e scope
 S->>P: conferir root grants e restrictions
 S->>S: validar contrato e namespace revision hash
 S->>D: raw projeções membership receipt em transacao
 O->>S: query ou explain
 S->>P: reautorizar leitura e geracao
 S->>D: verificar arquivo e projeção
 S->>D: registrar query
 S-->>A: recorte de evidencia autorizada
 A->>A: cards, offsets, contexto e limites
 alt Transcricao literal reconhecida
 A-->>O: campos da fonte sem modelo
 else Geracao permitida
 A->>L: prompt schema e trechos
 L-->>A: proposta JSON
 A->>A: verificar IDs e quotes
 A-->>O: proposta not_certified ou generation_failed
 end
''',
'cain-workflow-estados':'''stateDiagram-v2
 [*] --> ready: create
 ready --> awaiting_generation_approval: etapa de geracao sem aprovacao
 awaiting_generation_approval --> running: approve_generation
 ready --> running: etapa deterministica
 running --> ready: etapa concluida e restantes
 running --> completed: ultima etapa concluida
 running --> failed: erro preservado em attempts
 failed --> running: recover explicito
 running --> running: recover apos lease 600s
 failed --> ready: abstain operador e restantes
 failed --> completed: abstain ultima etapa
 ready --> cancelled: cancel
 failed --> cancelled: cancel
 running --> cancelled: cancel invalida claim
 completed --> [*]
 cancelled --> [*]
''',
'cain-er':'''erDiagram
 projects ||--o{ project_documents : owns
 ui_sessions ||--o{ ui_turns : contains
 ui_turns ||--o{ response_feedback : receives
 identities ||--o{ identity_signals : observes
 identities ||--o{ scoped_preferences : scopes
 publications ||--o{ membership : includes
 records ||--o{ membership : referenced
 publications {
  string scope PK
  string id PK
  blob raw
 }
 records {
  string scope PK
  string id PK
  string source_id
  string revision
  string signature
 }
 membership {
  string scope PK
  string publication PK
  string record PK
 }
 agent_jobs ||--o{ agent_steps : application_scope_job
 agent_jobs ||--o{ agent_attempts : application_scope_job
''',
'stocks-componentes':'''flowchart TD
 CLI[main.py legado] --> ING[ingest COTAHIST e CVM]
 ING --> DB[SQLite legado e migrations]
 DB --> FACT[universe factor portfolio]
 FACT --> BT[backtest legacy e simulation causal]
 BT --> J[judge e trials_gate Core]
 J --> REP[report e registros trials]
 DB --> RJ[rj_pipeline e familias]
 RJ --> RJJ[rj_judge FDR e maxT]
 OPS[python -m stocks_predictor] --> STORE[operational_store]
 STORE --> CAT[source_catalog e DatasetSelection]
 CAT --> BT
 OPS --> EXT[external_intelligence staging]
 EXT --> CAS[raw CAS e tabelas external]
 OPS --> PR[ResearchProfile e DatedOutcome]
 PL[StocksPredictorPlugin V1] --> CAPS[WAITING NO_GO FORBIDDEN]
 EXPORT[tools export_cain_status e bundle] -.-> CAIN[CAIN consumidor separado]
''',
'stocks-ingestao-simulacao':'''sequenceDiagram
 participant U as Operador
 participant O as operations
 participant C as source_catalog
 participant D as operational_store SQLite
 participant S as DatasetSelection
 participant E as simulation
 U->>O: ingest arquivo ZIP, hash e versao explicita
 O->>D: BEGIN IMMEDIATE
 O->>C: copiar bytes temporarios e conferir SHA
 C->>C: parser estrito COTAHIST e filtro spot
 C->>D: source_versions e prices_raw atomicos
 D-->>O: receipt sem capital
 U->>S: source_ids cutoff e periodo
 S->>D: snapshot mode=ro
 D-->>S: fontes e precos escolhidos
 S->>S: normalizar FATCOT; recusar conflito
 U->>E: targets eventos corporativos e custos
 S->>E: barras e selection_sha
 E->>E: D+1, posicoes, custos e marcas
 E-->>U: medicao e hash de inputs; sem verdict economico
''',
'stocks-rj':'''sequenceDiagram
 participant U as CLI RJ
 participant D as SQLite legado
 participant P as rj_pipeline
 participant F as rj_families
 participant J as rj_judge
 U->>P: config asof e free_float opcional
 P->>D: universo e eventos approved_by
 D-->>P: precos e calendario
 P->>P: candidatos causais, primeiro episodio, outcomes e censura
 P->>F: features no trough
 F-->>P: valores ou None; ownership indisponivel no pipeline
 P->>J: uma unidade por empresa
 J->>J: bootstrap, permutacao e BH-FDR
 J-->>P: efeito CI p e influencia LOCO
 P->>P: bloquear secundarios com empresas repetidas
 P->>D: atualizar episodes scores e company_observations
 P-->>U: relatorio e faltas; sem capital
''',
'stocks-estados':'''flowchart LR
 OP[Operacional: WAITING ou PASS] --> SEP[Eixos separados no codigo]
 SCI[Cientifico: DISCOVERY_INCONCLUSIVE] --> SEP
 PRED[Preditivo: NO_VALIDATED_NET_EDGE] --> SEP
 ECO[Economico: NO_GO] --> SEP
 SEP --> CAP[Capital: FORBIDDEN ou capital_enabled false]
 J[Judge: SEM DADOS ou INCONCLUSIVO] --> OUT[Veredito estatistico]
 IC[IC inferior maior que zero] --> OUT
 DSR[DSR e desconto efetivo] --> OUT
 OUT --> C[COMPROVADA ou nao comprovada]
 C -.-> INF[Sem transicao implementada aqui para autorizar capital]
''',
'stocks-er':'''erDiagram
 source_versions ||--o{ prices_raw : source_file
 source_versions {
  string source_id PK
  string publisher
  string dataset
  string version
  string policy
  string sha256
  string observed_at
 }
 prices_raw {
  string date
  string ticker
  string source_file FK
  int quote_factor
  float close
 }
 rj_universe ||--o{ rj_episodes : ticker
 rj_episodes ||--o{ rj_family_scores : episode_id
 external_raw_objects ||--o{ external_source_versions : sha256
 external_source_versions ||--o{ external_observations : source_version_id
 external_source_versions ||--o{ external_rejections : source_version_id
 external_source_versions ||--o{ external_fund_holdings_documents : source_version_id
 external_fund_holdings_documents ||--o{ external_fund_holdings_observations : holdings_document_id
'''}
for name,text in D.items():study.save('relatorios/docs/diagramas/'+name+'.mmd',text)
ca='''# Como funciona o CAIN observado

A árvore local 0.4.12 fornece duas trilhas: conversa com identidade explícita e consulta de pesquisas recebidas por Snapshot/Bundle. Os elementos abaixo são OD de código; setas expressam chamadas ou relações de aplicação. Nenhum diagrama prova serviço ativo. Os arquivos e hashes estão em `evidencias/cain/hash(es).json`, `source-index.json`, `coverage.json` e `REGISTRO.log`.

## Componentes

{cain-componentes}

`runtime.build_cain` seleciona as implementações concretas dos ports de persistência, registra os agentes e escolhe o router. A API cria o WorkspaceStore e monta pesquisa; são bancos locais e arquivos, sem leitura direta automática de toda raiz produtora. O provedor de biblioteca pode ser FakeLLM; a configuração de aplicação escolhe Ollama.

## Conversa e recuperação

{cain-conversa}

`Cain.run` observa preferências apenas no `user_input` explícito, carrega contexto por escopo, escolhe agente e registra decisões. Preferências reconhecidas ignoram citações, blocos colados, desejos de terceiros e ambiguidades. A resposta gera hash e dois eventos separados: mediated e completed. Na API, completed e outcome permitem reconstruir a UI sem repetir inferência. O Lock de geração é por processo; não é lock distribuído. Uma identidade de usuário é isolamento local de dados, não autenticação.

Aritmética tem parser AST limitado e Fraction, sem execução geral de código. SearchAgent prioriza trechos documentais e só recorre ao histórico do usuário quando não há fonte recuperada. Busca literal não certifica completude. CodeAgent produz texto e não executa o resultado.

## Recebimento e explicação de pesquisa

{cain-pesquisa}

A identidade do Snapshot usa namespace do produtor, source_id e revision, com assinatura de conteúdo e evidências. Raw é autoritativo; projeções são verificadas/reconstruíveis. Revisões coexistem sem regra automática de mais recente. Consulta reautoriza e grava auditoria em `queries`, por isso não é um comando forense somente leitura. Bundle possui controles próprios para metadata e CAS; o workflow de seis etapas usa evidências Snapshot, conforme `coverage.workflow_input=snapshots_only`.

Na trilha de IA: fonte recebida → operação read/generate autorizada → recorte com offsets/contexto → prompt e schema → Ollama → JSON/IDs/quotes verificados → proposta. `semantic_support=not_certified`, `memory_promoted=False` e `proposals_only=True` tornam o limite explícito. Uma citação literal não demonstra que a interpretação é correta. Transcrição de tabelas reconhecidas é determinística e evita paraphrase do modelo.

## Estados do workflow

{cain-workflow-estados}

`Workflows` fixa question, protocolo research-workflow/19, identidade do modelo e fingerprint da política/corpus. Geração requer aprovação explícita; falhas mantêm tentativa. `recover` permite nova tentativa e lease expirada após 600 segundos; `abstain` é checkpoint do operador, sem aceitação do output falho. `awaiting_generation_approval` é estado devolvido ao cliente, não status persistido de job. A contagem de chamadas do modelo cobre receipts concluídos; chamadas em falhas são desconhecidas.

## Esquema

{cain-er}

As relações de agent_jobs/steps/attempts no desenho são relações por chaves da aplicação, não FKs declaradas nesses CREATE TABLE. Identidades, workspace e pesquisas têm schemas separados. Bundle possui ainda reservas globais de entidades, aprovações e variantes raw. Arquivos de documentos e CAS permanecem fora do SQLite e são conferidos por hash.

Backup completo tira snapshots independentes de workspace e research e copia documentos/CAS imutáveis. O manifesto declara essa consistência; não há transação única entre os dois bancos. Restore exige diretório novo e ativação manual após revisão da política.

## Ordem de leitura

Comece por pyproject.toml, settings.py, runtime.py, orchestrator/__init__.py, agents/__init__.py e workspace.py. Depois identity/explicit.py e persistence/adapters/sqlite.py. Para pesquisa: service.py → objects.py/bundles.py → inspection.py → grounding.py → analysis.py/historian.py → workflows.py. Evaluation, harnesses de CI e relatórios antigos ficam para a segunda passagem. A revisão integral desses últimos continua pendente no coverage.json.
'''
st='''# Como funciona o Stocks Predictor observado

Esta documentação descreve o fonte local 0.2.0, independente de main remoto e do Anexo A. OD de código sustenta os elementos; a exportação tracejada para CAIN indica ligação entre processos por publicação de arquivo, sem chamada de serviço observada. Fonte/hashes, notas por módulo e teste seguro estão em `evidencias/stocks-predictor/`.

## Componentes

{stocks-componentes}

Há um runtime legado de pesquisa e um armazenamento operacional versionado separado. O legado guarda preços, eventos, fundamentos, runs e RJ. O armazenamento gerenciado preserva versões físicas de fonte e rejeita updates/deletes; o acesso legado recusa esse banco para evitar consultas que misturem versões. Staging externo tem contratos e proveniência próprios, sem alimentar automaticamente os fatores.

## Arquivo de dados até medição

{stocks-ingestao-simulacao}

`source_catalog.ingest_version` copia bytes antes de parsear, verifica hash e identidade da versão, usa Savepoint e não aceita conteúdo distinto sob uma versão declarada. O parser estrito do catálogo interrompe linha malformada; parser legado tolera falhas individuais e conta rejeições. Cotações são normalizadas pelo FATCOT e filtradas para à vista quando configurado.

DatasetSelection escolhe source_ids e cutoff explicitamente. Seu observed_before é o conhecimento do catálogo, não prova de publicação no passado. A simulação recebe targets, custos e eventos corporativos explícitos; a referência desses eventos não certifica que estejam completos ou fossem conhecidos. O resultado é medição de engenharia, sem veredito econômico.

## Backtest e gates

Os fatores incluem momentum, volatilidade, proximidade da máxima, volume e contabilidade/valor. Universo usa calendário anterior à decisão e mediana de volume com zeros para sessões sem negócio. Deduplicação por quatro letras do ticker é heurística, não mapa histórico de emissores. Caminhos legacy conservam pressupostos das hipóteses julgadas; current accruals/E/P/B/M usam derivação PIT por versões.

`backtest.judge` calcula PSR e bootstrap pareado da diferença de Sharpe; séries vazias ou curtas têm estados próprios. `trials_gate.apply_dsr` acrescenta multiplicidade, desconto efetivo e falhas adicionais. Controle positivo plantado verifica sensibilidade do pipeline, sem demonstrar efeito em dados reais. Custos modelados, datas fornecidas e resultados históricos precisam de revisão independente antes de inferir lucro.

O gate de rebalanceamento econômico usa média menos z vezes erro padrão para comparar ganho com custo. Esse cálculo depende da maturidade/independência das observações; DatedOutcome verifica a cronologia informada, não sua veracidade. `capital_enabled` continua false.

## Recuperação judicial

{stocks-rj}

O pipeline escolhe primeiro candidato causal por empresa, classifica rally futuro e censura, e mantém exclusões visíveis. Inferência primária usa uma unidade por empresa, permutação com correção plus-one, bootstrap por cluster e BH-FDR. Volume contemporâneo é apenas descritivo. Ownership fica indisponível no pipeline; não virar zero silenciosamente. Episódios secundários com empresa repetida bloqueiam a inferência sem permutação por cluster.

LOCO mede influência do sinal, não validação preditiva. `joint_max_t` exige unidades/labels iguais entre famílias; o nome legado romano_wolf_stepdown é um alias dessa rotina. Haircut numérico e simulação de poder não constituem holdout real.

## Eixos de estado

{stocks-estados}

A figura é um mapa de eixos e condições, não máquina de estados única: o código não define enum global com todas essas transições. PASS operacional, COMPROVADA estatística e lucro/permissão econômica são diferentes. A aresta tracejada expressa inferência limitada aos gates/plugin examinados: não foi encontrada ali transição para autorizar capital; não é prova de ausência em todo o acervo.

## Esquema

{stocks-er}

O ER é parcial e separa conceptualmente schemas de bancos distintos; tabelas de catálogo e staging não implicam banco único. Preços gerenciados têm UNIQUE(date,ticker,source_file), fontes têm identidade de publisher/dataset/version/policy e hash. Os timestamps available_at, observed_at, received_at e first_seen têm semânticas distintas. CDA e Entrega usam primeiro recebimento pelo coletor; entrega oficial e competência não provam disponibilidade pública histórica.

RJ atualiza episode e family_score sem chave de run; para reconstruir épocas distintas é necessário guardar snapshots/relatórios por execução. Snapshots operacionais usam backup SQLite consistente, SHA e INCOMPLETE até conclusão; restore cria destino novo.

## Operação segura e testes observados

Doctor/inspect gerenciados usam leitura mode=ro; `external status` e `external verify` via CLI inicializam conexão e gravam receipts quando sucesso. Esses nomes não autorizam execução em fontes forenses. Nenhuma coleta B3/CVM ou banco real foi executado no estudo.

Uma cópia independente foi usada para 11 checks stdlib de execução D+1, turnover, portfolio e gate econômico. Rerun Python3.13.14 passou; receipt anterior Python3.12.14 preservado. Isso não verifica suíte pytest, Core, integração persistência, previsões ou lucro.

## Ordem de leitura

pyproject.toml → operations.py → operational_store.py/source_catalog.py → dataset_selection.py → simulation.py; depois main.py → db.py → universe.py/factor.py → backtest.py/trials_gate.py. Para PIT: cvm_pit.py e source_history.py; para caixa: continuous_cash.py/retail_cash.py; para RJ: rj_pipeline.py → rj_episodes.py → rj_families.py → rj_judge.py. Staging externo fica em external_intelligence.py. Experimentos congelados e relatórios históricos ficam para segunda passagem, com cobertura pendente explícita.
'''
for p,text in [('cain',ca),('stocks-predictor',st)]:
 for name,diagram in D.items():text=text.replace('{'+name+'}','```mermaid\n'+diagram+'```')
 study.save('relatorios/docs/COMO_FUNCIONA_'+p+'.md',text)
 study.log(p,study.ROOT,'Documentação de aprendizado e diagramas componentes sequência estados ER salvos',0,'Diagramas sustentados em módulos examinados; relações de aplicação e inferências explicadas',limits='ER e fluxos parciais; cobertura integral pendente',artifacts='relatorios/docs/COMO_FUNCIONA_'+p+'.md')
