# Glossário com origem

Os nomes de arquivo são relativos à raiz do projeto indicado. IDs têm namespace do domínio; V2 em módulo de avaliação não é automaticamente envelopeV2.

|Termo|Significado e limite|Origem observada ou DD explícita|
|---|---|---|
|OD / DD / ET-SRC / ET-HIST / ET-RUN / EU / INF / NV|Categorias deste estudo: observado, declarado, teste fonte, resultado histórico, teste executado, uso, inferência, não verificado.|Mandato seção3; REGISTRO.log|
|HEAD / origin/main local / main remoto|Commit checkout, ref remote-tracking e ref consultada no servidor, respectivamente; não são intercambiáveis.|evidencias/*/baseline.json; git rev-parse e ls-remote|
|DatasetFreeze|Contrato de congelamento: hashes, partições, cutoff e proveniência declarados, sem provar qualidade econômica dos dados.|core: src/predictor_core/contracts/scientific.py|
|PastView / ReplayEngine|Visibilidade de prefixo histórico ao handler, validando ordem/disponibilidade; referências/ambiente não sandboxados.|core: src/predictor_core/measurement/replay.py|
|TrialRegistry / TrialRegistryV2|Registro V1 com lock e superseded; V2 prospectivo com validação própria, sem herdar lock V1. Versão do registro não é protocolo ResearchV2.|core: measurement/trials.py; contracts/trial_v2.py|
|Brier / RPS / DM / PSR|Métricas probabilísticas, comparação Diebold-Mariano e probabilistic Sharpe ratio; validade depende amostra e premissas.|core: measurement/metrics.py; stats.py|
|PIT / available_at / cutoff|Dado admissível pela sua disponibilidade antes da decisão, não apenas data do evento; a implementação varia por domínio.|core: data/contracts.py; Brasil research_runtime temporal; Stocks cvm_pit.py|
|Ops run / provenance / heartbeat|Execução subprocesso com lock, tentativas, timeout, registros e vida; êxito operacional não decisão científica/econômica.|ops: src/predictor_ops/runner.py; provenance.py; CLI (ver inventário)|
|predictor.plugins|Entry point de capabilities/contratos com import opcional; não prova disponibilidade de inferência ou um serviço central.|pyproject.toml de domínios; ecosystem registry|
|ResearchSnapshotV1|Publicação documental com origin, records, evidence, coverage e restrictions; ID sela conteúdo canônico.|ecosystem: packages/research-snapshot/src/research_snapshot/contract.json|
|ResearchBundleV1 / CAS|Entidades/relações/artefatos; content-addressed storage pelos hashes, com objetos recebidos distintos de referências.|ecosystem research-bundle/contract.json; CAIN research/{bundles,objects}.py|
|ResearchTaskV1 / ResearchResultV1 / AuthEnvelope|Mensagens de pesquisa autenticadas no protocolo examinado, com assinatura e validade; distintos dos exports documentais.|ecosystem: packages/research-protocol; Crypto research_{admission,results}.py|
|Research envelope V2|Papel declarado no Anexo; não demonstrado nas fontes primárias estudadas. evaluation/v2 CAIN é avaliação do produto e não esse envelope.|DD AnexoA2/A3; fontes primárias protocol1.0.3rc1 e src/cain/evaluation/v2.py|
|Scope / grant / binding|Escopo usuário/projeto/coleção, permissões e raízes de importação que delimitam leitura/geração; reautorização em query.|CAIN: src/cain/research/service.py; bundles.py|
|Received / referenced|Bytes recebidos e verificáveis versus referência cujo conteúdo não foi admitido; arquivo citado não amplia coverage.|Snapshot/Bundle contracts; CAIN inspection.py|
|Proposta / semantic_support|Texto de IA e citações estruturalmente aceitos; não certifica suporte semântico ou verdade factual.|CAIN research/analysis.py; field_review.py; evaluation/quality.py|
|Workflow checkpoint|Sequência durável, retomada e aprovação explícita de geração; cancelamento/completed pertencem ao job, não à ciência.|CAIN src/cain/research/workflows.py|
|DESCRIPTIVE_REPLAY / WFA|Reutilização de fit histórico descritivo versus divisão walk-forward separada; causalidade da inferência não corrige fit futuro.|Crypto GarimpoInvestimentos/v3/{pipeline,regime_engine}.py|
|SHADOW_TRADE / SHADOW_CANDIDATE / FORBIDDEN|Estados de observação e vedação; não tratar candidato como operação autorizada.|Crypto core/economic_gate.py; Brasil recommendation.py; plugin.py|
|CLV / closing_definition|Comparação com cotação de fechamento sob definição/time/book; alternativaBrasil sem offer aceita pode declarar NOT_MEASURABLE.|Brasil temporal/prospective_shadow.py; pesquisa alternativa handler|
|H8 / H9 / H14 / H15 / A1|Identificadores de hipóteses do domínio Brasil, com proteção e tipos próprios; mesmo número H em outro projeto não é identidade comum.|Brasil plugin.py; research_runtime/handlers; A1 arquivos no inventário|
|H4 / H6 e CLAIM-BR-MARKET|IDs de relatos usados por CAIN como identidades fornecidas pelo domínio; não prova validade da hipótese.|CAIN research/historian.py e evaluation protocolos; exportadores domínio|
|DT_RECEB / D+1|Disponibilidade de documentos CVM deslocada para dia seguinte; dataevento e datarecepção distintas.|Stocks stocks_predictor/cvm_pit.py; ingest_cvm.py|
|RJ episodes / repeated companies|Episódios de recuperação judicial com scores próprios; episódios sobre mesmaempresa afetam independência.|Stocks rj_episodes.py; rj_judge.py; rj_models.py|
|R6 / R7 / R8|Receipts/consolidação/lacre operacionais próprios Stocks, com verificadores CI; não gates de rentabilidade.|Stocks .github/workflows/ci.yml; tools/{audit_registry,verify_operational_evidence}.py|
|Gate / finding / P0 / P1 / P2|Resultado e artefato de verificação versus problema e impacto. Prioridade não probabilidade/certeza.|qualification/crypto/GATES.json; FINDINGS.json; scripts/attest.py|
|C7.1 / QUALIFIED / NOT_QUALIFIED / IN_PROGRESS|Regras e estados de atestação vinculados a baseline e missão; check implementa subconjunto e não transfere decisão a novo commit.|qualification/COMMON_QUALIFICATION_CORE.md; scripts/attest.py; attestation-epochs.json|
|D-27 / D-29 / D-30 / D-31|D27 APPROVED observado no DECISIONS do main remoto fixado por SHA; D29–D31 não encontrados naquele arquivo/instante. Ausência no primário local delimita outra época, não aprovação remota.|OD remote-main-decisions-summary.json; CONFRONTO_ANEXO_REMOTO.md|
|Cleanroom / ET-HIST|Instalações de wheelpublicada e buildHEAD isoladas, com introspecção; logs históricos precisam commit/ambiente.|qualification/shared/scripts/cleanroom_baseline.py; RAW_LOGS catalogados|
|Edge / capital_allowed|Alegação científica/econômica e permissão de capital requerem evidência distinta; smoke, bootstrap ou gate não bastam.|Charters/economic_decision domínio; contratos Core; docs de cada projeto|
