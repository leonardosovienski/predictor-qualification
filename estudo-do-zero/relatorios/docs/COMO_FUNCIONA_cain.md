# Como funciona o CAIN observado

A árvore local 0.4.12 fornece duas trilhas: conversa com identidade explícita e consulta de pesquisas recebidas por Snapshot/Bundle. Os elementos abaixo são OD de código; setas expressam chamadas ou relações de aplicação. Nenhum diagrama prova serviço ativo. Os arquivos e hashes estão em `evidencias/cain/hash(es).json`, `source-index.json`, `coverage.json` e `REGISTRO.log`.

## Componentes

```mermaid
flowchart TD
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
```

`runtime.build_cain` seleciona as implementações concretas dos ports de persistência, registra os agentes e escolhe o router. A API cria o WorkspaceStore e monta pesquisa; são bancos locais e arquivos, sem leitura direta automática de toda raiz produtora. O provedor de biblioteca pode ser FakeLLM; a configuração de aplicação escolhe Ollama.

## Conversa e recuperação

```mermaid
sequenceDiagram
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
```

`Cain.run` observa preferências apenas no `user_input` explícito, carrega contexto por escopo, escolhe agente e registra decisões. Preferências reconhecidas ignoram citações, blocos colados, desejos de terceiros e ambiguidades. A resposta gera hash e dois eventos separados: mediated e completed. Na API, completed e outcome permitem reconstruir a UI sem repetir inferência. O Lock de geração é por processo; não é lock distribuído. Uma identidade de usuário é isolamento local de dados, não autenticação.

Aritmética tem parser AST limitado e Fraction, sem execução geral de código. SearchAgent prioriza trechos documentais e só recorre ao histórico do usuário quando não há fonte recuperada. Busca literal não certifica completude. CodeAgent produz texto e não executa o resultado.

## Recebimento e explicação de pesquisa

```mermaid
sequenceDiagram
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
```

A identidade do Snapshot usa namespace do produtor, source_id e revision, com assinatura de conteúdo e evidências. Raw é autoritativo; projeções são verificadas/reconstruíveis. Revisões coexistem sem regra automática de mais recente. Consulta reautoriza e grava auditoria em `queries`, por isso não é um comando forense somente leitura. Bundle possui controles próprios para metadata e CAS; o workflow de seis etapas usa evidências Snapshot, conforme `coverage.workflow_input=snapshots_only`.

Na trilha de IA: fonte recebida → operação read/generate autorizada → recorte com offsets/contexto → prompt e schema → Ollama → JSON/IDs/quotes verificados → proposta. `semantic_support=not_certified`, `memory_promoted=False` e `proposals_only=True` tornam o limite explícito. Uma citação literal não demonstra que a interpretação é correta. Transcrição de tabelas reconhecidas é determinística e evita paraphrase do modelo.

## Estados do workflow

```mermaid
stateDiagram-v2
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
```

`Workflows` fixa question, protocolo research-workflow/19, identidade do modelo e fingerprint da política/corpus. Geração requer aprovação explícita; falhas mantêm tentativa. `recover` permite nova tentativa e lease expirada após 600 segundos; `abstain` é checkpoint do operador, sem aceitação do output falho. `awaiting_generation_approval` é estado devolvido ao cliente, não status persistido de job. A contagem de chamadas do modelo cobre receipts concluídos; chamadas em falhas são desconhecidas.

## Esquema

```mermaid
erDiagram
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
```

As relações de agent_jobs/steps/attempts no desenho são relações por chaves da aplicação, não FKs declaradas nesses CREATE TABLE. Identidades, workspace e pesquisas têm schemas separados. Bundle possui ainda reservas globais de entidades, aprovações e variantes raw. Arquivos de documentos e CAS permanecem fora do SQLite e são conferidos por hash.

Backup completo tira snapshots independentes de workspace e research e copia documentos/CAS imutáveis. O manifesto declara essa consistência; não há transação única entre os dois bancos. Restore exige diretório novo e ativação manual após revisão da política.

## Ordem de leitura

Comece por pyproject.toml, settings.py, runtime.py, orchestrator/__init__.py, agents/__init__.py e workspace.py. Depois identity/explicit.py e persistence/adapters/sqlite.py. Para pesquisa: service.py → objects.py/bundles.py → inspection.py → grounding.py → analysis.py/historian.py → workflows.py. Evaluation, harnesses de CI e relatórios antigos ficam para a segunda passagem. A revisão integral desses últimos continua pendente no coverage.json.
