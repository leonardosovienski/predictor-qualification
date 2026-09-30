import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent));import study
reports={
'cain':'''# Inventário técnico — cain

Estado da investigação: caracterização central baseada em código, com cobertura por módulo em `evidencias/cain/coverage.json`. Revisão integral de todos os módulos próprios, ferramentas e fixtures ainda pendente. Este documento não certifica instalação nem funcionamento atual.

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

**K — Documentação.** `document-catalog.json` lista narrativas/histórico, datasnomes e profundidade. README/CONTINUIDADE foram confrontados; registros de avaliações/QA continuamDD/ET-HIST apenas. Não se declara código morto porlackreference. Módulos avaliação/tools/JS e branches secundárias ainda precisam revisão integral por módulo.

**L — Fonte vs uso.** Fonte dirty mais untracked é OD. Publicação release remoto distinta é registrada à parte. Instalação principal C:/CAIN/.venv e serviço8877 são DD doREADME, sem EU atual. Nenhuma capacidade remotaV2 foi atribuída a esta árvore.

## Cobertura e pendências

Em profundidade: agentes, aritmética, API, runtime/orchestratorcentral, configurações, identidadeexplicit/scopes, workspace, SnapshotService, CAS/backup, workflows/providers, coverage/diagnósticos. Leitura mecânica/AST integral da seleção169arquivos/25.175linhas; isso NÃO equivale à revisão semântica integral. Restante módulossearch/router/persistencedetalhes/Bundles/historian/grounding/evaluation/scripts/funções fixtures eweb: coverage.json é fonte precisa; alguns métodos centrais foram examinados sem arquivo completo. Históricodocs/evaluationresults/vendor apenascatalogado salvo quando citado. Pendentes testeisolado completo e reconstrução respostas atuais; sem bloqueio de acesso ao fonte, portanto não rotular estudo completo.
''',
'stocks-predictor':'''# Inventário técnico — stocks-predictor

Estado: estudo central do conteúdo local com cobertura explícita, ainda parcial quanto à revisão semântica integral. Não é qualificação científica, recomputação de lucros ou ativação.

## Identidade e confronto

Fonteforense `C:/STOCKS/stocks-predictor`, HEAD`5cf27f44f579cb40d8b873c0f10005360427a2d0`, árvore limpa no baseline. Versão0.2.0, Python>=3.13,<3.15, hatchling1.32.0. Baseline, hashes por arquivo e fonte remota estão em evidencias/stocks-predictor. A cópia independente gitclone--no-hardlinks foi criada após baseline apenas para smoke e seuHEADguardado; não representa remotoatual.

`PRELIMINAR_stocks-predictor.md` foi salva antes confrontoREADME/AGENTS/HANDOFF/estado. Limitação de cegamento: o Anexo foi lido junto ao mandato inicial; suas identidades não foram adotadas como premissas. README local0.2.0 e exportSnapshotV1/Bundle concordam comcódigo. StagingEXTERNAL_INTELLIGENCE_V1 descrito coincide com módulo; não prova dadosvivos. Anexo0.3.0rc4/adapterV2/Opsrunner diverge destaárvore: pyproject sóPyYAML+Core e pluginadapterv1, sem pacotev2 nos rastreados. Não atualizar clones para ocultar diferença.

## A–L

**A — Responsabilidades.** Pesquisa de açõesB3 por fatores/hipóteses/backtests e eventos, linhaRJ, carteira/paper, catálogo versionado e ingestão públicaexterna. `ecosystem_plugin` declara scientificDISCOVERY_INCONCLUSIVE, predictiveNO_VALIDATED_NET_EDGE, economicNO_GO, capitalFORBIDDEN. Plugin capacidades são introspecção estática, não saída recomputada nem healthdeumserviço. Consumidores CLI, relatórios/paper eexportadoresCAIN; instalaçãoativada NV.

**B — Estrutura.** Pacote stocks_predictor; main.py legado; __main__ →operations CLI offline; research scripts históricos separados; experiments BIG_WINNER programas próprios; tests/fixtures; tools audits/transfers/exporters; vendor/predictor_core terceiro preservado. Pacote não declara [project.scripts], entrada via `python -m`. `predictor.plugins` stocks→StocksPredictorPlugin. `source-index.json` registra estrutura/símbolos/imports.

**C — Ambiente e dependências.** PyYAML>=6,<7 eCore>=3.2,<4. `tool.uv.sources` fixaURLreleasev3.2.1 wheel; uv.lockCore3.2.1 sha256`10ef42f34ace8bb2df5f83ff7de2ceec79b035a25ea0a690e8942bd60d2fb4e3`. Dependência código importada predictor_core bootstrap/stats/trials/kernelinfra; wheelversão não confirma metadatainstalado. Devpytest/ruff/pyright/build/coverage. Pythonbundled3.12.14 smokeinicial não satisfazcontrato; rerun3.13.14feito e anterior preservado. Sem instalação novasdependências.

**D — Interfaces.** main.pytraz ingestão/scan/quarentena/fatores/backtests/paper/RJ; operations tem doctor/init/inspect/ingest/snapshot/restore/profile/evidence/simulate-selected/external. JSONoperacional rejeita dupkeys/nonfinite/typesunknown eoutputs capitalfalse. doctor consulta metadatainstalada eDBmode=ro seexplicit; `external status/verify`, apesar nomesconsulta, conectam escrevendo egravamexternal_receipts ao success. Não executar originais.

**E — Configuração.** config.yamlsectionsuniverse/factor/portfolio/execution/backtest/bootstrap/jumpdetector/hypothesiscriteria/economics/data; config_rjfamilies/rally/episodes/judge/influence/paths. config.pycongela parâmetros eidentifica hipóteses, leitura semântica ainda pendente. OverridesDB_PATH_ENV/PREDICTOR_TRIALS_PATH/reportpaths eargs explícitos; pathsdefault podem usar raizoriginal em código, por isso smoke apenas imports4primitivasstdlib. Nenhum segredovalueimpresso; B3/CVM públicoscontém caminhosURLs conhecidos, acessoexterno não executado.

**F — Persistência.** DBlegado migrationsprices_raw,adjustments,quarantine,universe_snapshots,decisions,runs,fundamentals/dividends/cash_events/stock_bonus ePITfundamentals_pit/shares_pit/source_docs, RJuniverso/events/episodes/scores/companyobservations. operational_storeé físico separadocomapplication_id0x53544B50,version1,source_versions+prices_raw,foreignkeys eappendonlytriggers; DBlegado rejeita managedstore para impedir mistura. external contémrawobjects/sourceversions/observations/securitylinks/rejections/receipts/holdings/deliveries. Bancoarquivo original não aberto. Trialregistry JSON eattestationarquivo são escritasruntimeversionadas; estudo não os altera.

Catálogo source_idhashdepublisher/dataset/version/policy/content, ingestcopia arquivoemtemp antes parsing, SHAexpected,Savepointatomic. Conflictsepayloaddiferente mesmaversão declarado recusados. `observed_at` conhecimento catálogo, não publicaçãohistórica. DatasetSelectionsourcesexplícitas cutoff/start/end ehash, materializeusaDBmode=ro numaSnapshotSQL eviewmemory; conflitosbarversões não escolhem latestimplicit.

**G — Algoritmos científicos.** Factor momentum252skip21, realizedvol252, quintiltop/bottom, inversevol/doublefilter. Currentaccruals/E/P/B/M usamcvm_pit, pathslegacy de hipótesesjulgadas conservam embargoestimado; umaembargo90dias não prova disponibilidadereal. Revenuegrowthpega2refdates elegíveis sem exigir distânciade12meses. Universe usa pregõescalendário antesasof, volumezerosessõesausentes, quarentena resolução timestamp, dedup4letrasticker é heurísticaemissor, nãoCNPJ/ISIN. Materializesnapshotdate recusa composição conflitante.

Simulationtemmotorcausal D+1; legacy_walk_forward explicitamentepreservado para hipóteseshistóricas. Legacy mantémretornozero tickersemcotação (convenção assumida, não preço executável),benchmarkmédia presentdata eturnoverreal; conhecimento deeventos/source não se deduz depricecutoff. judge retornasemdata/amostracurta/IC95Sharpe; defaultbootstrap10kblock21seed42, PSRdescritivo, COMPROVADA seIClower>0. TrialsGate acrescenta DSRthreshold0.95,deflationapplied eextra_failures, harnessplantado/null efingerprintnewtrial. Todas tentativas registry emdenominador; dadosfaltantes/trialssemsharpe exigem limites decoverage. Gate estatístico não autoriza capital.

EconomicRebalanceGate usa mean-zSEM e custos de turnover paraHOLD/REBALANCE,capitalfalse; normalapproximation eindependência não comprovada. DatedOutcome rejeita duplicados/futuro/maturidadecontraditória, masdatasfornecidas não verdadecertificada. ResearchProfile validaDecimal/capital/custos/tempo ecompletude, semlucronegativo/positivo certificado.

RJ: candidatesfirstcausaltrough, outcome futuro rallyversuscontrol/censored/invalid; unidadeprimária umaempresa, secundáriasrepetidas bloqueiam inferência semclusterpermutation. 9famílias sendo contemporaneousvolume sódescritiva,8predictive; ownershipNone nopipeline por cobertura desconhecida. Judge usa bootstrapcluster epermutationplusone, BH-FDR, categoricalCramersV; LOCO influência nãoOOS. RobustjointmaxT usa sharedpermutationslabels, nomelegadoromano_wolf_stepdown é aliasjointmaxT, haircut0.36 não holdoutreal. Power é simulaçãoGaussiana planted, não poderempírico. Persist_run atualiza episodes/scores poridentitysemrun_id,portanto banco não guarda épocasdeexecução distintas automaticamente.

**IA.** Pacote examinado usa cálculoregras/estatísticas; não encontrou dependênciaLLM nosimports próprios selecionados e não chama modelo nofluxoexport. Não seprova ausência absoluta em todo acervo histórico. `external_intelligence` é ingestão/normalização, nomeintelligence não implicaLLM. ServiçoCAINexterno é consumidor separado.

**H — Fluxos completos.** COTAHISTZIP/hash→sourcecatalogstrict/spotfilter→prices_raw versão→selectionexplícita→barsnormalizedfatcot→targets+eventoscorp/custos→simulationD+1→receiptengine/inputsSHA semverdicteconômico. LegadoCSV/CVM→migrationsfundamentals/adjustments/quarantine→universe/factor/portfolio→pairedbacktest→judge/DSRtrial→report/paper. RJmanualapproveduniverse→candidatePIT→rallyfuture/censoring→featuresfamilies→companyinferenceFDR→report+persist. ExternalB3/CVM→rawCASversions→contractschema/temporal/identitychecks→observations/rejections→verify/status+receipts; rawpayloadgravado antes metadata, órfãos podem exigirreconcile. ExportCAINSnapshot/bundle lêfontesadmitidas porhash efornecemetadata/exactstates semreplicarpreçoslicensed.

**I — Testes.** 97arquivos sobtests e812funções test_ extraídasET-SRC; não contagemcoleção completa incluindoexperiments/tools/history. `test-contracts.json` preserva asserts/raises. ET-RUN smoke11checksstdlibruntime3.13.14copiagitindependente: D+1/ausênciafuture,turnovernormalização/inicial,quintilweights,hold/rebalancecapitalfalse,ISOdate/bool/nonfinite rejeitados. Anterior3.12preservado. Nenhum pytest/Core/PyYAML/suite/persistencereal/HTTP/backtest foi executado; CIhistórica não érunagora.

**J — Operação.** CIdeclara uvsync--locked,lint/type/coverage77%,testsarchived selecionados, build/wheelsmoke isolado, docsprojectchecks, gitleaks+synthcontroles eoperationalR8verify. Não inferir statusremoto peloyaml; consulteci-head-local/mainremoto. sqlitewal singlehost,BEGINIMMEDIATE eclonebackup. snapshots comINCOMPLETE atécomplete,restore destnovo exclusiveSHA. CLI external recebe receiptpaths, errosclasses exit2/3/4 e não prova scientificstatus.

**K — Documentação.** README/HANDOFF/STOCKS_CURRENT_STATE lidos para confrontoDD, arquivodatadohistórico catalogado. Relatoslucroamostras/fontes/CIhistórica permanecem declarações não números atuaisrecomputados. Verifieroperational fonte lido/símbolos, nenhum lacre refeitonooriginal. ASTvendorcatalogado como terceiro, não assumir defaultvendoréimportreal.

**L — Fonte/build/uso.** Versão0.2.0 eHEADforenses; wheelrelease3.2.1Core URL/hash configura packagefutureinstall, não instalação atual. Plugin não confirmaativo. Nenhuma ordem/brokerfoiobservado nosfluxos centrais; todos caminhosoperacionais específicos retornamcapitalfalse/FORBIDDEN, ausênciaabsoluta brokeremacervocompleto não demonstrada.

## Cobertura pendente

235arquivosselecionados/36.308linhas leitura mecânica integral eAST; módulo próprio central revisto emcoverage.json. Integral semânticaDBmigrations/CVMingest/externalall/continuouscash/simulation/backtestrunners/discovery/experiments/tools/fixtures ainda pendente. Histórico research eVendor catalogados; profundo sóquando conclusãoexigir. Dados/bancos/execuçõesmercado/modelos não verificados. Artefatossource-text/executable compact são locais intermediários,excluirpublicação. Documento aprendizado reconstrói fluxo observado, não aprovação econômica.
'''}
for p,text in reports.items():study.save('relatorios/INVENTARIO_'+p+'.md',text);study.log(p,study.ROOT,'Inventário central A-L e divergências salvo; integralpendente explícito',0,'Inventário com escopo rastreável',artifacts='relatorios/INVENTARIO_'+p+'.md')
