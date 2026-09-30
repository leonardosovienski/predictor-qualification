# Revisão semântica dos testes Crypto — bloco 06

Leitura integral de fixtures, mocks e assertions; nenhuma execução. Os cenários demonstram contratos sintéticos ou reconciliação de artefatos, sem estabelecer lucro futuro, autorização ou execução real.

## tests/test_ecosystem_plugin_state.py

Plugin capabilities compara estado governança local NO_ACTIVE_HYPOTHESIS/INCONCLUSIVE/HISTORICAL_NO_GO/FORBIDDEN/securityownerconfirmation. Strings não comprovam rotação nem lucro/validação.

## tests/test_equivalence.py

Equivalence compara indicadores idênticos, RSI diferença.0001 reprova, missing unilateral reprova/bilateralaceita. Diferenças change24h apenas relatadas e não reprovam: equivalência é parcial declarada, não todos dados.

## tests/test_experiment_registry.py

Registry662linhas integral: schema real não-vazio, frozenhipóteses/H6/família impede antes core spy e conserva, nova família atingecore. Schema inválido/duplicado rejeitado; params imutáveis, timestampregistro preservado, campos opcionais. Muitos testes usam power_attestation=False explícito bypass, outros fixture. CloseSharpe não cria trial e exigeN3/fonte/horizonte/era, closedignored semreescrita. H6 semtrial/pre-registro/fonte reservada/highscore no-op; synthetic edge80 retorna VALIDADO e noise INCONCLUSIVO sem gravar registry. Seeds/samepred_date não representam observações independentes reais. SQLitefallbackstructural excluído. Atestado físico teste validade só passed_at/edge_verdictGO, NÃO expiração; poderjudge usa scriptsyntheticedge/noise. Dryrun sótmp protege real.

## tests/test_external_intelligence.py

ExternalIntelligence fixtures rightsunknown false, PITprovider semmetadata rejeitado/BTCWBTC ambiguidade. SQLiteappendonlytrigger, revisionid muda valor, recollectionearlierreceipt selecionável, snapshotsdeterminísticos, missing vs unsupported. Coinmetricsnormalizefabricado, Santimentpartialerrors/restrictions, Nansenrights/budget5exhaust e WBTCguard; perturbação latecontext PASS. Shadow conserva radarsignal e ledger sóreference semraw, providerfakefailureisolationPARTIAL, conditional pitfalseexcluído/hypothesisgenerating. Jobcollectioncapitalfalse. Semrequests reais nem validação termosdireitos.

## tests/test_factor_dsl.py

Todos builders DSL têm prefixperturbationcase e centeredmeancontraprova detectaleak. Closedwindow/warmup/lag/None/divzero/zscoreconstant e recipestable; unknownops/aridade/k0/janela1/missingfeature/payloadimport rejeitados. Mesmo fixture ajuda poder contra futuro, não prova todas variantes/dados financeiros.

## tests/test_failure_replay.py

Failure replays sintéticos: Settingsbadprovider antesrede, allingesttimeout mock causaRuntimeErrorsemdb, realchildsleepjobtimeout espera124FAILED preserva scientificartifact. H6 regressão recusada/bytes, candlefutureinvisível, droppingSQLiteguards+tamperhashchain detecta e sealrecusa. WALopenbackupincluicommit/integrity; prefilter missingvolume reason. Subprocesso/sleep não executados aqui.

## tests/test_feature_store_backup.py

SQLiteWALtemporário backup verify/restore roundtrip semsidecars/integritycheck, tamperedbytes/destexist/missingdb/badmanifest recusa. TruncaçãoSQLite comsizehashrecalculados ainda detectada integrity e WALcommit escritor aberto incluído. Não testa restore de datasetprodução/灾难 real.

## tests/test_feature_store_backup_agendado.py

BackupconfigdefaultDATA_DIR/backups, timestampformato e duplicate-seconds gera distinto. Jobstatuses0success e1/2 nãoPARTIAL, comandooperational.feature_store_backup outputroot declarado. Não executa agenda/tarefa.

## tests/test_feature_store_guards.py

SQLiteguards publicationanterior/lookahead e lag46dias rejeitados, lag0/2aceitos, custommax400aceita100. Featureversionsv1/v2coexistem e defaultservev1; SAMEversionupsert valor30=>31 é permitido, não appendonlyfeatures. Declaredpublication não autentica tempo.

## tests/test_feature_store_health.py

Bancosfabricados healthEMPTY/CORRUPT/STALE e offsettimezone instantes reais, futuro/malformed não escondidos por texto válido. READY sófreshness/integridade timestamps, não qualidade científica/econômica.