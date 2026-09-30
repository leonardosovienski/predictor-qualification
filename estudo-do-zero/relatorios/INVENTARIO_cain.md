# Inventário técnico — cain

Estado da investigação: caracterização central baseada em código, com cobertura por módulo em `evidencias/cain/coverage.json`. A revisão semântica dos módulos próprios executáveis selecionados, ferramentas, testes e UI foi concluída; artefatos estáticos e dependências têm catálogo separado. Este documento não certifica instalação nem funcionamento atual.

## Identidade e origem

Raiz forense `C:/CAIN/projeto`, HEAD local `24f784c5dde1fa66c262ad5899f4fd8d02526adf`, detached HEAD e alterações preexistentes. `baseline.json`, `baseline-status.txt`, `hashes.json` e `untracked-hashes.json` delimitam a época. `analysis.py` modificado importa `claim_tables.py` não rastreado; descrever apenas commit omitiria parte executável efetiva. Versão declarada 0.4.12 do pacote `cain-research`, Python>=3.11, setuptools>=75. Nenhum arquivo original modificado pelo estudo.

`origin/main` local/remoto, tags/releases e CI são os registros separados `baseline.json`, `release-identity.json`, `ci-head-local.json` e consultas do registro central. O fonte local não representa automaticamente `main` remoto. Wheel instalado, runtime principal, identidade efetiva de modelo e acervo vivo: NV; não abertos nem interrogados.

## Caracterização independente e confronto

A caracterização preliminar está preservada em `PRELIMINAR_cain.md`; foi salva antes de ler narrativas do projeto. Limite metodológico: o pedido integral, incluindo Anexo A, foi lido inicialmente para conhecer as regras; portanto não houve cegamento absoluto ao anexo. Papéis e versões desse anexo não foram adotados como premissas do inventário.

README local declara conversa/memória/pesquisa Snapshot e Bundle e versão0.4.12: concorda com pyproject/runtime/service. Sua frase de contratos integrados e instalados é DD; estudo não confirmou instalação. CONTINUIDADE documenta QA/candidata não promovida e trabalho preexistente, compatível com status dirty, mas contagens históricas não foram recomputadas. Anexo afirma0.4.13rc16, Python3.13, DecisionPolicy bitemporal e consumo apenas envelopeV2: diverge do código local que importa research_snapshot/research_bundle, políticas versions1/2/3 e workflows snapshotsonly. Isso prova diferença de época/árvore examinada; não refuta a versão remota sem lê-la.

## A–L: o que faz e como

**A — Propósito.** Assistente local para conversa, documentos de projetos, preferências explícitas, recuperação e pesquisa sobre publicações autorizadas. Usuário identificado por nome é um escopo de dados, não autenticação. `PersonalityState` tem defaults e está explicitamente marcada STUB; não confundir estrutura persistida com identidade humana/modelo validado.

**B — Estrutura.** `src/cain/runtime.py` é composition root; `orchestrator` coordena; `agents` executam quatro papéis; `identity` extrai preferências; `persistence` define três ports e adapters SQLite/lexical. `research` contém serviço Snapshot, Bundle/CAS, inspeção, historiador, grounding e workflows. `search` contém retrievers/embeddings. `workspace` guarda projetos/documentos/turnos; `evaluation` tem harness/v2; web contém UI JS/HTML/CSS. CLI `cain`, `cain-mcp`, `cain-stream` declarados; `__main__` chama CLI. Installation/windows e scripts PowerShell são launchers; .ci são harnesses, não serviço central.

**C — Tecnologia.** Python stdlib SQLite, dataclasses, urllib/tomllib; FastAPI/uvicorn opcionais API; Pillow opcional visão. Dependências obrigatórias `predictor-research-snapshot==1.0.1` e `predictor-research-bundle==1.0.0`. Wheels vendor existem; requirements-dev.lock diferente de uv.lock (não encontrado uv.lock no inventário rastreado). Relação pacote remoto→asset ainda depende do registro releaseidentity; não inferir versão instalada pela wheel guardada.

**D — Interfaces.** `api.create_app`: /run, /profile, projetos/documentos/sessões/feedback, /runs recuperação e pesquisa montada por research.api. Lock da geração é por processo; hostloopback e sameOrigin, CSP/no-store. `health` declara provider_availability=not_probed/inference=not_exercised. `CodeAgent` gera texto sem executar comandos. CLI/MCP/stream são adaptadores; API construção já cria tabelas, portanto não executar original como inspeção.

**E — Configuração.** `Settings` defaults ollama,qwen2.5:3b,127.0.0.1:11434,temperature0,seed42,timeout120,num_ctx8192,num_predict768,max_input_bytes6500; cain.toml local troca modelo para qwen3.5:4b e configura embeddingqwen3-embedding:0.6b. Modelo configurado não prova instalado. `load_settings` escolhe cwd/cain.toml ou bundled e ancora paths ao arquivo; overrides CAIN_DB,CAIN_PROVIDER,CAIN_MODEL,CAIN_OLLAMA_URL. Policypath é necessário antes de criar research storage. `CAIN_RESEARCH_OBJECTS` escolhe CAS. Valores sensíveis não inspecionados.

**F — Persistência.** SQLite `identities`, `identity_snapshots`, `identity_signals`, `scoped_preferences`, `decisions`; workspace `projects`, `project_documents`, `ui_sessions`, `ui_turns`, `run_receipts`, `response_feedback`; pesquisa `publications`, `records`, `membership`, `receipts`, `queries`, `conflicts`; Bundle tabelas research_bundles/entities/artifacts/relations/reservations/approvals e rawvariants; workflowsagent_jobs/steps/attempts. JSON/raw fonte autoritativo e projeções reconstituíveis, hashes e namespaces. Query de pesquisa escreve audit em queries, mesmo operação consulta. ArtefatosCAS são sha256-addressed, fsyncdurável antes metadata, órfãos possíveis. Nenhum banco original foi aberto. Backup completo faz snapshots independentes de bancos e verifica docs/CAS; consistência conjunta não é atômica.

**G — Algoritmos.** Roteamento RuleRouter com classificaçãoLLM opcional; detalhe completo ainda emcoveragependente. `Cain.run` oito passos sequenciais: sessão→observe/context→rota→agente→resposta→media/log→identidadeinteração→completed. Preferênciaexplicit regex ignora quoted/pasted terceiros e ambiguidade; escopos turn/session/project/user. Arithmeticast whitelist com Fraction, máximo64nós/160chars/16passos e limite1e18. SearchAgent recupera fontes com budget2400chars e ajuste serializedbytes; prioriza documentos, fallback histórico segregadouser/project. Pontuações não probabilidades.

**IA.** Ollama /api/generate recebe `prompt`, `system`, `options`, seed/temp/context, opcionalformat/schema; limite bytes é aproximação conservadora, não tokenização. Sem redirecionamentos/retry/fallbackimplícito; respostaHTTPbounded4MiB, JSONparse, resposta não vazia, done_reasonlength viraLLMTruncated com parcial. FakeLLM só wiring hash/excerpt. Providers embeddings conferem /api/tags e digest. Research review admite fonte sob read+generate, extrai cards/offsets/contexto, structuredschema e quote membership; semantic_support=not_certified. `claim_tables` transcreve tabelas rotuladas sem modelo. Propostas não promovidas memória, concordância support/challenge/synthesis não é independência. Corpusfingerprint epolicy rechecados.

**H — Fluxos.** Conversa/API validaownership, reivindica run_id, cria runtime, executa8passos, guarda completed/outcome de forma atômica, recupera turno sem nova geração. Snapshotimport valida scope antes fileaccess, confinedroot,restrictions+grant,package,BEGINIMMEDIATE,raw/projection/receipt; conflito vira receipt durable. Workflows6etapas, id fixado question/model/fingerprint, geração exige aprovação, lease600seg, recover explícito e tentativas preservadas. Diagnósticostructural-counts opt-in não constitui evidência científica independente.

**I — Testes.** Seleção rastreada contém65arquivos sobtests e450funções test_ extraídas, ET-SRC (`test-contracts.json`); não contagem de coleção pytest e não inclui todos não rastreados. Testes extras claimtables,reviewproviderbudget,BRauditsinstructions eLLMfailurecatalogados/lidos. Nenhum pytest/LLM executado neste estudo; dependências pytest/contracts/API ausentes no runtime bundled. Testes e documentação histórica não certificam semântica.

**J — Operação.** CI declarada lint/test/build e smoke wheel fora checkout, matrizPython; .ci supply/completion são harnesses com overlays/artefatosversionados. Não executados aqui; consultar run/commitstatus em evidência central. Retry explicitamente negado em orchestrator; workflowrecovertemlease. Arquivos/modelos/DB vivos não investigados. Segurança loopback/origin é controle de fronteira local, não sistema autenticação.

**K — Documentação.** `document-catalog.json` lista narrativas/histórico, datasnomes e profundidade. README/CONTINUIDADE foram confrontados; registros de avaliações/QA continuamDD/ET-HIST apenas. Não se declara código morto porlackreference. Avaliação, ferramentas e UI foram revisadas integralmente na árvore local; branches secundárias e remoto não herdam essa cobertura.

**L — Fonte vs uso.** Fonte dirty mais untracked é OD. Publicação release remoto distinta é registrada à parte. Instalação principal C:/CAIN/.venv e serviço8877 são DD doREADME, sem EU atual. Nenhuma capacidade remotaV2 foi atribuída a esta árvore.

## Cobertura e limites finais

A cobertura consolidada está em `evidencias/cain/coverage.json` e as notas por módulo em `module-notes.json`. Todos os executáveis próprios selecionados foram revisados semanticamente. Lock, fixtures estáticas e código de terceiros são catalogados com essa profundidade distinta. Histórico e fontes remotas não recebem certificação por transferência desta revisão. Nenhum banco original, modelo vivo ou serviço externo foi acionado.

Leitura de testes (ET-SRC), execuções isoladas (ET-RUN), CI por commit e declarações históricas permanecem separados. Consulte `SUPLEMENTO_CAIN_STOCKS_COBERTURA_FINAL.md` para a contagem exata e limites das execuções.


## Épocas remotas observadas

Os manifests do main remoto e os assets do Anexo foram verificados separadamente, por SHA/versão. Veja [confronto do Anexo](CONFRONTO_ANEXO_REMOTO.md). Essas identidades não ampliam automaticamente a cobertura semântica da raiz primária nem provam integração runtime.
