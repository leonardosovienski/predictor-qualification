import study,json,hashlib,pathlib,sys
p='brasileirao-predictor';base=pathlib.Path('C:/BRASILEIRAO/brasileirao-predictor');target=f'evidencias/{p}/root-scripts-coverage.json'
idx=json.loads((study.ROOT/f'evidencias/{p}/root-scripts-index.json').read_text())
notes={
0:[
'Namespace vazio.',
'Top-level ajusta modelo burn-in e Core power com alternativa sintética, grava atestado TRIALS; import tem efeitos. Poder de harness não demonstra lucro.',
'Claim exclusivo por trial e ledger.basename; x/fsync/inode e hardlink final sem overwrite; mantém claim em erro/sucesso, libera só AGUARDANDO_N verificando identidade. Sem fsync de diretório nem congelamento do ledger aqui.',
'Phase0 fingerprint política e cinco fontes, inicialização grava estado capital false. Report compara captured_at por string com initialized_at, não valida received/cutoff nem prova resultados econômicos.',
'Missingness usa DB read_only, cobertura xG JSON e finally close.',
'Auditoria top-level DB mutável, Elo cronológico, WC2026 corte, odds aproxima nomes e datas ±3 dias sem captured_at. Calibração descritiva, modelo/mercado em amostras diferentes; não PIT autenticado.',
'Backfill agrupa retrieved_at, apenda smokes antes do espelho PIT bitemporal; ValueError causal vira quarentena. Sem transação conjunta entre JSONL e SQLite.',
'Stats cache por evento, contagens finitas não negativas, nulos preservados e jogador duplicado rejeitado. available_at materialização atual, PK agrega nome/time/competição/temporada sem vintages; não reconstrói disponibilidade histórica.',
'Backtest close monkeypatch settle no módulo, DB read_only mas import altera funções; n30 PSR e bootstrap por partida, referências históricas impressas não execução nova.'],
1:[
'Walk-forward blocos alinhados por dia, burn-in, fit usa apenas datas anteriores ao bloco; Elo histórico pode atualizar dentro dele. Odds carregadas sem timestamp PIT explícito. PSR/DSR/cluster bootstrap gates e TrialRegistry lido; n30 não garantia, H2 validada compara hit a0.60 sem IC. Main escreve CSV/JSON mesmo DB RO, não executado.',
'Backup H9 destination LOCALAPPDATA timestamp, create_backup seguido verify_backup; efeitos mutáveis, sem execução.'],
2:[
'Benchmark quatro motores; DC default distinto de serving, baseline climatologia congela por data e Shin aggregate sem bookmaker explicitamente economic_evidence_eligible false. Walkforward via evaluator, missing kickoff fallback meia-noite; block21 é número observações, estratos by_team só mandante. Delta CI paired moving bootstrap; skill_score CI guarda diferença absoluta de loss e não razão normalizada. half_life desconhecido usa default, trial não congela todo modelo; main grava JSON. Nenhuma execução econômica.']}
notes[3]=[
'Import executa DB mutável e bootstrap exploratório janela CY/Ngames por argv, treino antes2026 e odds atuais sem received_at. n2 mínimo e IC cluster por jogo não ajusta busca de janelas nem dependência entre jogos.',
'Manifesto H9 SHA bytes/contagem linhas/commit, capital false; fontes faltantes silenciosamente omitidas, sem validar cadeia nem consistência transacional dos arquivos lidos em momentos distintos.',
'Fit usa dados até junho2026 e holdout declarado2024..junho2026 sobrepõe treino: calibração retrospectiva in-sample. Mercado WC Npequeno explicitamente hipótese, odds datas±3 sem PIT. Import DB mutável.',
'Calibração WC2026 fit anterior primeiro teste, odds matching datas±3 semcaptura/identidadebookmaker; pooling1x2triplica observações dependentes, médias Brier/acerto semIC. Import DB mutável.',
'Capture timestamp fornecido antes quatro chamadasHTTP sequenciais; pre_match compara esse relógio comkickoff/status, não received_at fim da coleta, podendo captura atravessar kickoff (INF). JSONL fsync antesSQLite sem transação conjunta e dedup ignora JSON inválido; semlock. point_in_time true não certificação.',
'CLI JSON input assess_prediction_readiness, imprime modelo, exit0ready ou2; não habilita capital por si.']
notes[4]=[
'CI regex bounded readonly200chars/allowlists/debt warnings, full pytest oufastskip e smokeprobs99..101. Sem timeout filhos, paths temp fixos concorrentes; pularDB permiteverde semsmoke. Não provaPITnemintegralidade, não executado.',
'Collection-only abre SQLiteRO mas collect pode gravar arquivo salvo --dry-run; delegação à implementação, nenhumserviço executado.',
'APIs pagas odds/lineups, featured+H1 persistidos JSONL, só featured espelhoPIT e smokes. Semtx entreJSONL/smoke/SQLite, erroparcial propagado depois efeitos; labelCOLLECTION_ONLY não autenticaçãoeconômica.',
'A1 due_label escolhe primeiro target vencido, podendo recuperarT-1440 emT-10 e próximosrunsoutros labelsmesmajanela. Guard quota/backoff registraantesAPI, sealsdiasantigos, fingerprint sóappendapóscoleta. CAPTURES eheartbeat write_text sematomic/locklocal; PASS dependeerrors e nãoquarantine/quota, capitalshadowfalse.',
'Metrics heartbeat escrito antesleituras, hojeapenas eexpectedtodosfixtures8dias, modoúltimologglobal. Métrica arquivo overwrite não comprova saúde/transaçãodurable; semsnapshots retornaNOT_STARTED.']
notes[5]=[
'Comparison intersects event IDs checks date/home/away/outcome, hashes inputs, pairedlossdelta movingblock21 and Bonferroni familylooks overall. Dictloader silently replacesduplicateID; trusts providedlosses/probs, missingevents excluded. Stratifying byactual/controlerror changes temporalspacing, fixedblock maynot representdependence; no capital.',
'Confound top-level mutableDB; Maher/strength tune2023 validation then monthlyrefit2024..2026, but frozenElo NB/DC fitthrough2026 evaluated2024..2026 overlapping. Optimizer convergence unchecked, IID SE threshold2 labels REAL, not dependency/multiplicityadjusted; comparison confounded.',
'Cosh-free top-level fits throughJune2026 and evaluates2024..June2026 overlapping, optimizerres.success unchecked; gridnegativeclip differs strictmodel; descriptiveMLE notholdoutvalidation.',
'Coverage branch+statement counts strict intvalid, requiredfilesmissing fail and gates80%, generator56%; Redisgroup duplicatesKERNEL despite REDIS_INTEGRATION empty. JSON inputcounts selfreported no artifactauth; classify runtime_homologado vocabularynot certification.']
notes[6]=[
'Zebra DBRO e ratings_asof datas, params cache atual; sweepb seisvalores e médias de mesmaamostra explicitamente in-sample, não fix validado. n0 dividezero potencial.',
'Elasticidade importDB mutável, fitatéJune2026 eidxdesde2024sobrepostos. Médias saídasmodelo não gols observados; texto nunca mudaTOTAL contradiz cosh que varia comdiff, sóbaixaelasticidade na amostra.',
'H9 frozenparamtrial+homeadvconfig, Elo current cachefresh12h nãohashElo. Janela de decisãoatékickoff, não sóhorizonte±15m; emitpolicy podeestreitar. Bestavailable odds semstaleness/finitude ecomparação sembookidentityauth. Attemptsappendsemfsync/lock/jointtx comledger, capital false.',
'Eval WCfitantesfirsttest eElohistorical; odds±3dias semreceivedtimestamp. Brier pairedsubset maslogloss/acerto modelall contra marketsubset rotuladosmesmosjogos; semIC/power/multiplicity. ImportDB mutável.',
'Contextualensemble CLI parâmetros dataset, writesJSONoutput, exit2 somenteFAIL_NUMERIC, outrosNO_GOexit0 não elegibilidadecapital.',
'A1 seteúltimosarquivosconsecutivos semexigirterminarhoje, manual/test/keyrotationcampos declaradosnãoassinados. Economicmode sempreREHEARSAL, fullcriteriaPASS homologatedtrue capitalfalse; possíveisdadosstale eNaNcomparações. Writesverdict, NO_STARTEDexit0 nãohomologação.']
notes[7]=[
'H14 claim single-look, protocoloexactprimary/guardrails anteslercohort, duplicateeventsreject, n mínimo semmétricas, pairedgain bootstrap21/10000/42. Maturados qualquer scorepresente semstatusfinal/availability timestamp, ledgerordemappend semsort/hashauth/policycompat aqui. IC0refutada significa não superioridade, não equivalência; guardrailnãoICnegativo não provanoninferiority; capitalfalseindividualonly.',
'H15 mesmo guard singlelook epairedmetrics H14, armsrefit100/10 eprotocolcheck. Sem validarbootstrap/minNcontra frozenparams alémprimary/guardrails; coefconst21/10000/42. Não validafinalscoretimestamp/ledgerhashness/cronologia aqui; capitalfalse.',
'Residual CLI dadosJSONL, mínimosamostra/PENDING eparâmetrosuserfriction/minedge, writesreport; missingfile viraempty, mainretorna0 inclusivepending, semautorizaçãoeconômica.',
'Coldstart data ratings/promotions/firstmatches protocolo do próprioJSON; ausenteBLOCKED_DATA masexit0, writesreport semmkdir; delega avaliador, sem autenticidade fonte/protocolo aqui.',
'Rho stability DBRO Elohistory+sortedtemporalkeys, writesreport; deixa conexão semfinallyclose atéprocessend, exit2apenasFAIL_NUMERIC. Read-onlyDB não significa somente-leituraartefatos.']
notes[8]=[
'H3/H5 validates picks/settlement,timeUTC,pickduplicate andn100; resultsdictlastwinsduplicates. Bootstrapclusterpartida CLVlower>0 ROI>-2% geraGO E capital_enabled=true, semsinglelook/family/power/authgate. Numericmeans nãofinitemeancheck aqui; eligibilityinputhashnãoassinatura. Script nãoautoriza automaticamente stack nemlucroreal.',
'EXP001 coberturaOddsPapi apikey redactedHTTPerrors, todosfixturesfinished Jan..Sep e3horizons. Retoma rows por schema só, completedmatchsequalquerhorizon jápresente nãoexige3; summary usa denominatorfixturesnow epreviousrowspossiblydifferentcohort. Writesatomicreplace semfsync, rawfalse, paidcredits nãoexecutado.',
'Pilot escolhe primeiro/meio/último3fixtures, history sideúltimoantescutoff comactive/conflictingties checks, returnedtimestamp min3sides nãoquotejointinstant. Missingpricefinitude/timeawarenesscheck, trusts historicalprovidercreatedAt notlocalreceipt. Apenas4requestsdeclaredfree nãoverificadoemserviço, rawfalse.',
'ExpA fitting throughJune2026 includes hold2024..June2026, sweepskx4 Brier/Logloss descriptive noIC adjusted; top-levelDBmutable.',
'ExpF freezeparams preWC thenrhox4 evalsameWC, odds±3 semcapturePIT, edge p-1/odd distinctShinrelative elsewhere; countroles+Brier meansnoIC/multiplicity, notcausalproof DC. ImportDBmutable.']
notes[9]=[
'Experimentos causa fitpreWC model/Shin/noise/sweepk countsrole semoutcomepayoff, ruídos500 nãoexperimentosindependentesreais; marketperfeito é assumidonãoobservado. odds±3semPIT, importDBmutable; diagnóstico mecânicofiltro.',
'Exportloss servingdefault replaysobservations+useroverridescadence/xG/HL, per-event metricsJSON writes. CheckMIN_HISTORY sódepoisrun, nouniqueIDsorfreezehashmetadata no própriooutput; downstreamcompare maycollapseNoneIDs.',
'Genteams cachecompetição2026 concatenatesbyname lastwins, checks20warnonly, writesdata. Cacheprovenance nãoauth/receiptPIT.',
'Governança synthetic800inflation1.3/vig5%, funilIIDPSR/bootstrap; amostra novo scoreparacada seleção mesmojogo quebrajointdependence mascontroletoy. Poweratestado eH1/H2trialregister escreveapósharness, H2hit60nãoecon; notasCLV histórico declaração nãoverificação nova.',
'H10 restcapped5, mensalblocos190jogos semalinhardia, fitpastdates baselinevsdelta_xg rest, pairedmoving10. PoweroutroIIDprobabilisticpredictor mede réguaRPSnãofatigacausal, registraapósverresultado, explicitno capital. SQLloadcompleted porscoresemavailability; missingICdetail pode chamarnegativo, formataçãoNone falhaantesregistro.']
notes[10]=[
'H4 half-life360winner da mesmavarredura, pairedIID10000bootstrap semselectionadjust/dependence, DCrefit100 vsElorefit1 diferentescadências. Alignindex/team masnotdates; actualmidnightfallback. Trialupdatepostresult, hypothesisRPSnotmarket; nãoexecutado.',
'Hotpath Redis writes publish/enqueuesynthetic, Lua verifiescurrentpayload/requestTTL/result/snapshotstate atomically; strictfair5keysfinite>=1orNone. nrechecks sameid, verificationlatencyexplicitnotkernelmeasurement; RedisURLexternalsnãochamado.',
'Backfill separateSQLite新path atomic x/hardlink/fsync/newoutputguard, operationalDBRO. Matchuniquepair±1day, pricefinite>1, sourceSHAaggregateunknowncapture explicitexploratory/clvfalse/capitalfalse. Temporaryleftonfailure; nojointatomicreportdbpublication; contaminated0flag nãoautoridadePIT.',
'APIFootball history productionSQLitedefaultmutableonlyquery, shadowmutable andpaidnetworkseasons. Noclosefinally/boundedseasonsquota aqui; nãoexecutado.',
'Compose init requiresdistinctnewDBs xcreatesboth, seededDEMOparamsnottrained withconfigSHA timestamp; no rollback firstDB ifsecondfails, noauthPIT/econ, nãoexecutado.',
'Scheduler installsForce closing3daily interactiveuser PythonPATH resolved runtime,5minIgnoreNew, optionalRunNow; persisttaskchange notexecutado, nofreshnessguarantee/runtimefreezing.']
notes[11]=[
'A1tasks Force UVrun (pode resolverdeps), apikeypresençanão rotação verificável, collect15m3650days/discoverMonday8dayhorizon/metrics2355. SeparatetaskIgnoreNew nãojointlock; RunNow iniciaindependentementeordering, nãoexecutado.',
'Scheduler Force manifestjobscadence+market/model/H9/H14/H15, disables5legacytasks; VENVexplicit ewrongroot stringcheckafterwrites, noimmutableentryhash. Restart3 mayduplicatemutableeffects, modelcachetraining30m; nãoexecutado.',
'InventárioDBRO countscoverage genericnonnullladohome nãofullmarket, abertura!=flat porcentagem20infereclose semcapturedtimestamp; argumento proxydeclaração nãoPIT. Missingtableexceptions, semwrites.',
'Calibrationwindowgrid9 fitpreJan2026 evalprimeirosN40, oddsaggregate andflaggedteams selected, maximizaROI/Brier/bias namesdescriptive semIC/multiplicity/holdoutfresh. Top-levelDBmutable, nãoexecutado.',
'Half-lifegrid10 computesElohistorycadaHL fitpreJan2026 evalprimeirosN40, bestBrier/bias sobremesmoeval semadjust; descriptivo nãolearningindependent. Top-levelDBmutable.',
'LineupInbox RedisLuaatomic type/XLENcap10000 +XADD, strictJSONnanreject size64KB. XLENretainedhistory não pendingPEL e pode bloquearapósprocessar seworker não remove; validaçãoeventschema downstream, noexternalschamados.']
notes[12]=[
'Maher tuneL1? L2lambda1/3/10/30/100 prior6m; monthlyrefits4yrpast, baselineNB/DCalpha/rho fitthroughJune2026 applied2024..2026, sharedfutureparams contaminam ambos. Optimizer uncheckedsuccess egridclipsnegatives, means onlynoCI. ImportmutableDB.',
'Maherverif fixeLR3 monthlypastfit mas sharedalpha/rho/frozenElo futurefitthrough2026; IIDSE1.96 eabs(t)>2 não temporaladjust/nestedchoice. PrintsSIGNIFICATIVO não economicvalidation, importDBmutable.',
'H8 monitor historicalexploratory explícitopriceevidence/CLVfalse capitalfalse, clusterbootstrap+PSR/DSR andmilestones. Leitura arbitraryJSONL nohashauth/seqvalidation, emptyseries fail, repeatedlooks não authorization.',
'Shadow monitor calls evaluator comverdict cadaexec inclusiveantes100 bootstrap abstenção, no single-lookguard; metadados frozen declaradossemtrialload/hash. Pendingclosing e result iguaiscontagemnãocausas; omitecapitalflag returned masGO continuaapresentado.']
notes[13]=[
'Oddsshop strictcompletebooks+finitudeprice/dedup, medianperbookno-vig renormalized consensus, futurekickoff/freshnessonline15m; offlinefromfile disallowsnetworktempos. Modellegacycurrentcache/params semage/configfullserving; rawJSON writeexclusive semfsync/hashreceipt, APIspaidnotcalled. Footerdiagnosticnocapital/noCLV, bestprice not acceptedfill.',
'Readiness CLI delegated report statusREADY_FOR_HUMAN_REVIEW exit0 else2; nenhumaaprovaçãoautomatcapital.',
'P1cost syntheticPoisson timing/loopvsclosednormalizer/vectorobjective andoptimfits, printsrelativeerrors/convergence notassertthreshold or exitreject. Goalsclipped10 distributiontoy, no economicvalidation/performanceobservedlocal semexecução.']
notes[21]=[
'xG ensemble forceson/off deepcopy sameevents andcontract, checkidenticalp_winonly, warnsdegradedfits. Holdout2025flag canunseal, provenance explicitlyposthoc sameobserved2021..24sample, movingpairedCI notmultiplicity/selectionproof. Verdict lacksfiniteICcheck vsH14, writesreport+registry+syntheticpower, no capital.',
'H4sweep HL6orquick2 differencescadence250/100, walkforwarddatesmidnight, choosesminRPS samepanel, syntheticIIDpower distinctevaluation, one trial winnerregistryrecordsgridnot6independent trials. Noouterholdout/selectionadjust, no execution.',
'Passivejobs fixedallowlist withtimeouts, Win taskkilltree/cleanupfailseparatecodes +hiddenprocess, POSIXsubprocess.run onlychildkillnotwholegroup. A1 fingerprint/rotatedflag/keypresence preflight, heartbeat atomicreplace notfsync; nojointjoblock, wrapperSHAonlynotclosure, successcode noteconomicvalidation.',
'Seedfixture creates schema emptyDB, guardexisting unlessforce. Forcedoesnotdeleteexisting, connectmaymigrate existing so destructivehelp overstatesrecreate; noactualfixturedata inserted. Neverrunoriginal.']
notes[22]=[
'H9settlement opensdecisions JSONL nohashchaincheckhere, joinsrepresentative firstquote fixture andscorepresence notofficialfinished; result_published_at=nowlocalcapture nãoactualpublicationtime. Delegates settle validatesquotes/chronology, DBRO ledgerwrite, noorders.',
'Live settlement requiresfinished eventidentity strictintscore/probsfinite normalized, diagnosticcapitalfalse predictionSHA/factSHA ignoringtime; lock idempotentconflict andfsyncappend. Predictionoriginalhashcomputed now not comparedoriginalcapturehash; noexternalrawreceiptproof, waitfinalunbounded unlesswrapper. Noactualservicecall.',
'Dashboard callsH3/H5evaluator andinterimdiagnosticbootstrapn2 but explicitly capitalfalse/individualgatenotpermission. Diagnosticsrawresults separate eligibility andevent_idmissingcanclusterNone, ETA based fixeddate/rate notforecastcertainty. --jsonwritesdata; historicalROIreminder declaração.',
'Sim2025/26 DBRO importexecfullmodelsmonthlyfitpast firstmatchday; Elotemporalhistory, aggregateoddsnamedclosingwithoutcaptureevidence, descriptiveBrier/accuracy/team/calibration notpayoff. Fixedlabels17rodadas though actualyearfilter dynamic; testsnotexecuted.']
cov=json.loads((study.ROOT/target).read_text()) if (study.ROOT/target).exists() else []
for block in map(int,sys.argv[1:]):
 assert len(idx[block])==len(notes[block])
 for rel,note in zip(idx[block],notes[block]):
  cov=[x for x in cov if x['path']!=rel]
  cov.append(dict(path=rel,sha256=hashlib.sha256((base/rel).read_bytes()).hexdigest(),depth='semantic-integral',status='ET-SRC',executed=False,notes=note))
 study.log(p,base,'Revisão semântica integral scripts bloco '+str(block),0,'Todos os corpos executáveis lidos; notas persistidas',limits='ET-SRC; nenhum script executado',artifacts=target)
study.save(target,cov)
print(len(cov))
