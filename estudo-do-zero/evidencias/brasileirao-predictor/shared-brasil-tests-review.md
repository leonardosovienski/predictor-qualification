# Revisão integral semântica de testes Brasil

Nenhum teste executado. Hash dos bytes originais em REGISTRO.log.

## tests/test_bet_log.py

JSONL tmp adiciona/settle idempotente por bet_id, confronto invertido e datas desambiguadas; HT obrigatório para mercados parciais, ROI/drawdown e flows/reinit banca, duplicate apenas warning. Naive vs aware marca late None. validated por mercado não é validação deste fixture. Capital_gate é warning baseado status string comprovada de JSON sintético, não verifica evidência/autorização; ou15 fora do gate retorna None.

## tests/test_bitemporal_store.py

SQLite tmp bitemporal só mostra após published e ingested; revisão mais recente/dedup e clock impossível rejeitado. Source/chater strings declaradas, sem provider real.

## tests/test_bookmaker_odds.py

Fixtures de nomes acentos/aliases/ambiguidades, kickoff próximo/placeholder meia-noite e mando invertido; JSONL dedup separa bookmaker/mercado. Closing último pre-kickoff/valid>1/selection. Não observa bookmaker e política tolera placeholder sem hora real.

## tests/test_bookmaker_stability.py

Três dias sintéticos com cobertura10 classificam pinnacle stable, cobertura1 insuficiente e matchbook rejeitado. Retr ievaltime usado e três smokes em24h mantêm pending. Critérios heurísticos não medem estabilidade externa.

## tests/test_bootstrap.py

Seeded bootstrap média/CI/constante/n1/vazio/determinismo, amostra200 estreita mais que10. Não verifica coverage nominal repetido nem lucro.

## tests/test_brasileirao_domain.py

Config real identidade325/seasons e sportkey; quatro clubes sintéticos Elo/modelo com probabilidades normalizadas. Resultado Bahia0x2 declarado fixture, não API real. SQL in-memory sync idempotente/remove orphan adiamento/remarca fixture e exclui passado; HT fraction antescutoff/mínimo60.

## tests/test_build_data_archive.py

ZIP sintético preserva bytes/mapas/omissões e verifica restore; recusa hashes ruins/overwrite/exclusion incompleta/extras código/snapshot sem receipt/traversal/windowsNFCcase collisions/nesting budget/code referências com credencial. Snapshot é opaco fakeSQLite, receipt integrity_ok declarado não consultaDB real. Não autentica remotecommit nem descriptografa/protege secrets .env que política permite.

## tests/test_bundle_h9_evidence.py

Manifest ledger sintético registra hash real bytes/2rows/commit abc123 e capitalFalse, janelas irrecoverable. Não autentica commit ou conteúdo econômico.

## tests/test_calibration_gate.py

Report A10 físico NO_GO e servingFalse; métricas declaradas exigem gainRPS>.002/guardrails, candidate só novo protocolo. Losses/CI subset homewin sintético20boot. Sem reexecução do A10 inteiro.

## tests/test_capture_decision.py

Payload/receipt fake SHA gerado prova par condicional EV.08 nunca execution/PnL; latestbad não ressuscita older, NaN/dupJSON/clockties/identity/status recusa, futurereceipt excluída antesparse. CLI artifact tmp e overwrite/incomplete-universe reject. Hash comprova bytes transportados declarados, não origem externa ou preço executável.

## tests/test_capture_sofascore_event.py

FakeSofascore/clock injetado comprova boundary anteskickoff estrita, naive rejeita, captureJSONL dedup e post-kickoff não entra odds SQLite. wait jáconfirmed não dorme e kickoff false; semHTTP/lineup verdadeiro.

## tests/test_ci_current_elo_containment.py

Guard temp root permite script H14 copiado auditado, rejeita db.load_elo em research/backtest/similarname. Prova scanner destes padrões, não ausência de outras formas de leakage.

## tests/test_ci_dependency_pins.py

RegexURLs workflow igual uv sources e filenames no checksum. Não calcula hash download ou observaCI remota.

## tests/test_ci_nao_suja_a_arvore.py

git check-ignore esperado em quatro artifactdirs; regex --output destinos cobertos. Não executaCI nem cobre todos caminhos de escrita possíveis.

## tests/test_closeout_coverage.py

SQLite fixture intersectioneventids impede300%, emptyN/A e nãoInf. Sem cobertura realprovider.

## tests/test_closeout_integrity.py

Bad scores bool/fraction/inf sem mutate; JSONL duplicate/orphan/changedprofit/dupkeys rejeitados. Latestquote unusable/tie abstains, origem/evento/contrato misturados erro; chronologypublished/receipt e readiness types/blank fail. Declarations ready mas pre_match_evidence_eligibleFalse explícito.

## tests/test_closeout_research_inputs.py

Shadowstake nonfinite/bounds erro; travel coordinates limites, bool strictsurface, coach integer/vintage e recebimento pósKO rejeitados. Conteúdo geográfico/team causal é fixture, não fonte autenticada.

## tests/test_closeout_status.py

Tracked SQLite monkeypatch exige read_only=True e closeconnection. Emit_event e loaders mocked, não verifica filesystempermissions ou modo URI real.

## tests/test_closing_scenario.py

Decimal cenário congela escolha sem labels/protected2026 e duplicatas; selfodds nenhumedge, badprices mantémABSTAIN. Principal não luc ro, win1.38/loss-1.02 e unresolvedlockROIundefined. Mesmo dia ganhos não financiam2ª, dia seguinte sim. Liquidação condicional por labels fixtures, não execution/recebimento real.

## tests/test_collection_only_archive.py

SQLite fixture collection dry_run não grava apesar transitions_written>0 nome count potencialmente confuso; execução idem/no PROSPECTIVE_ELIGIBLE e retry event started sem regressão. Resultados históricos mantêm collection only.

## tests/test_collector_contract.py

Clientkey missing bloqueia, sem methods historical; aliasfuzzy só sugere, schema source/extra/odds rejeita e snapshots homologatedFalse. JSONLhash detecta edit sem rehash, conflicts/dedup/batchtail válido, SQLite mirror reschedule v2 e duplicate repara mirror deletado. Capturecomplete partialfailFalse. Economic7dias rehearsal; full7dias sem rotationatt FAIL. FakeCLIdetailsredaction/quota reserve20 attempt2/backoff30. Nenhuma API real ou anchor externa de cadeia.

## tests/test_compare_hypothesis_errors.py

Pairing keys ordena datas em vez eventid em três fixtures, não bootstrapa causalidade.

## tests/test_completion_anchor.py

Consensus exclui offeredbook da fairprob .5/.5 mas bestodds2.05, rejeita mixed capturevintage e conflictingduplicate. Odds inteiramente sintéticas.

## tests/test_completion_compose_init.py

Initializer tmp não sobrescreveDB, exige sports/marketdistinct, cria apenas demo integrity_ok/matches0. Não inicia Compose/Redis/produção.

## tests/test_completion_event_inputs.py

Target countfinite integer/missingfeatures/emptytraining/distributionunknown erro; overdispersionFalse forçaPoisson. Fixtures repetidas8 não calibram countmodel.

## tests/test_completion_ledger.py

Bad bet oddsNaN/Inf/stakebool/selection/prob impedem arquivo; stableid após reordenações no list/bank, duplicateid beforeappend e HTlado>FT rejects antes settlement. Não torna JSONL inviolável.

## tests/test_completion_math_consumer.py

NB total zero é produto de distribuições2times; pricerbadmeasures/handicap e negativoslive rejeitados. CLIprever fakebuild/SQLite e diskfull log injection exige RuntimeError auditlog em full/period. Não prova persistência em sucesso ou timing de dados.

## tests/test_completion_pit_contracts.py

Charter integra identidade, mixedcharter sem filtro recusa, mesmo clock diferenteevent conflict, schema legado recusa sem alterarhash; UTCoffset SQLdecision correto e strict prekickoff; HHI denomclub appearances=.5. BootstrapInf/bool e OUs unsupportedquarter reject.

## tests/test_completion_regressions.py

Spy comprova show calcula1x e mesma previsão/date enviada ao log; bitemporal conflitotie sem hashwinner. Sportmonks fake partialpage não afirma league absent e orçamento1request. Confidence nãoALTA por configedge apenas.

## tests/test_completion_serving_storage.py

SQLite temp serving conexão efetivamente readonlyDELETE falha; thetaextra dict/tuple preservada no predictionJSONL. Sem servinglive ou terceiros.

## tests/test_completion_source_budget.py

Sportmonksfake paginationmissing rejeita, cursorencoded não segue arbitrarynextURL, budget evitaextra1; ApiFootballerrors não eco fakecredential. Não atesta subscription atual.

## tests/test_contextual_ensemble.py

80 registros sintéticos expandingdates PASS/servingFalse,10 BLOCKED e available_at==KO erro. PASS é execução experimentalde fixtures, não lucro ou predictivegainreal.

## tests/test_core3_harness_contract.py

Lê committedattestation verifica coremetadata/controls/verdictstrings/executed==passed/fingerprintprefix e gitSHA40nãozero/sem dirty. Não reexecuta controles ou verifica commit existe/hashdataset/expiração neste arquivo.

## tests/test_core_integrity.py

Installedversions core3.2/ops4.2.1/no vendor e workflow sem PYTHONPATH/symlink/ignorefail tokens. Não observaCI remoto ou ausência de toda dependênciaworkspace.

## tests/test_db.py

Inmemory fixtures openingwriteonce COALESCE/closeoverwrites/placeholderteamsupdate, snapshotsdedup e longitudinal, HTconstant60frac1/3, kickoffUTC e v2reschedule. CompletedbestknownKOjoin porid. Dados fixtures inclusiveWC genérico não resultsreal.

## tests/test_db_extended_odds.py

Inmemory legacy migrateaddflatcols preservelegacy/idem/backfillOU somente se existe, flatopeningwriteonce/missingNULL/closeoverwrites e váriosOU/AH coexistem. Odds1.0 armazenada em linha6.5 mostra storage não é admissiongate.

## tests/test_db_readonly.py

TempDBseed e checkpoint: readonlySELECT permite eINSERTOperationalError. Não cobre toda função customSQLite/WAL.

## tests/test_dixon_coles.py

Equações tau thin cells/rhonegdraws/correctbounds, exponentialhalf life120, gridnormalização e scoresrange. Não estima validade distribuição esportiva.

## tests/test_dixon_coles_fit.py

Poissonseeded30rounds recupera plantedstrengthorder/meanlogattack≈0/homeadv/rhobounds; walkforward retorna PredictionPoints normalizados/timeordered. Nome never uses future kickoff sóassert predicted<matures: não altera futuro nem observa subset de fit. Nome empty-and-single-team só exercita empty.

## tests/test_draw_diagnostics.py

Display modelode times iguais expõe empate/gap0 e robustchoiceNone em JSON/humano, CLVmock. Não escolhe robustamente estratégia.

## tests/test_dynamic_strength.py

EWMAfixtures iguais neutral e4x0 dá correctionsdirecionais, unknownteams0; alpha inválido erro. Não holdoutperformance.

## tests/test_economic_search.py

Fractionarbitragem três odds/custo.02/commission.01 e seis partialcasesworst<0; forecastpermutafuture/recentlabels/allodds ignora, season2026 excluí antesparse, invalidlabelunsettled. Ledger same-dayreservedstakes98 e missingresultROIunknown, selfbooknormnone. Economia condicional depreçosfixtures e receipt/fillausentes.

## tests/test_ecosystem_plugin.py

Pluginshape domains/statusenum/capssupportprediction/NOT_VALIDATED/FORBIDDEN; não executa pipelines ou afere upstreamreal.

## tests/test_elo_baseline.py

40 jogos planted forte/fraco: properdistributions/strengthfavored/determinismo/drawrateinterior. Não marketaccuracy; drawrateassert não verifica valor do truncamento.

## tests/test_elo_baseline_block_guard.py

40blocks fixtures simultâneos contabilizam blocked>0, horáriosdistintos0; semhistoryusable lançaerro, predicted<matures e normalização. Nome drawrate from truncated só bounds0..1, não contraprova futuro.

## tests/test_emit_h9_shadow.py

SQLite Elo/cache e trials modelo fixtures, approved_bookmaker monkeypatch permite shadowwindow; emitscapitalFalse/currentElo/fingerprint16, frozenparams usados, cacheold fail e idempotência. Missingquote/team/wrongbook/block são auditados. Campo executed_odds é odd da cotação shadow e slippagevsbest meradiferença preçosfake, não execução real.

## tests/test_evaluate_h14_prospective.py

3 vs21 eventos com probabilidades fabricadas: mínimo antes métricas, n21 gera verdictenum/capitalFalse, unknownoutcomeexcluído e CLI refuseoverwrite. Não comprova timestamps prospectivos nos fixtures (ledger mínimo sem predicted_at) nem autenticidade.

## tests/test_evaluate_h15_prospective.py

Mesma estrutura mínimo21/refit10 vs100 declarados, n3 espera, n21 calcula, missingoutcomeexclui e overwritefailure. Não reestima modelos ou afirma beneficio refit real.

## tests/test_exp001_coverage_audit.py

Dois eventos porhorizonte um missing mantém denominatorcoverage.5; não coverage observada.

## tests/test_exp001_cutoff_state_regression.py

Timelinefake latestinactive/partialleg/unknownactive/tieconflicts impedemressuscitação, futurestateignored e reactivation antescutoff aceita. Transporterrorsrequests monkeypatch traceback sem keyURL. Sem请求 API real ou sourcevintage autenticada.

## tests/test_exp001_data_pilot.py

1x2 timelinefixture futuroprice99 excluído e missinglegs failclosed; não ingestreal.

## tests/test_feature_builder.py

SQLite sintético médias2.25xG/56.5possession antesalvo; ausênciaNone/count0 nãozero, deltaapenasduaslados, side/ALLperiod filtre98/99contaminação. Não verifica published/ingested nesta baselegacy.

## tests/test_find_odds.py

Lookupcanon/countryaliases e mandoswap1x2/OUinvariant, closestdate±3dias/malformedignore. Matching aproximado aceita cotação até3dias depois da dataalvo; teste não prova PIT ou identidadeeventid exata.

## tests/test_followup_capture_contract.py

Collector/auditor docsreprodução com clock/opener/helper fake: account/odds/account só1metered/idempotente, janelaantescredencial/quota20/paidplanblock, HTTP429semretry/redaction, rawJSONbadpreservado e offlineauditreject. Fixture/hashendpoint/timestamps/admissionprospectivefalseexec. Auditor adda udithook patchdesliga isolamento durante teste, não prova sandbox real. Sem rede/charge efetivo.

## tests/test_formal_prediction.py

Aliases fixtures identidade/data/quoteeventwrong reject, model spy blockedbeforecall capitalTrue; formalpredictionid desambigua repeatedmatches e missingref não gravaresultado. Context ready declarativo não atestavintage.

## tests/test_h10_fadiga_walkforward.py

Seeded rows60, restcap/sign/debut/outcomes, WFA paired30/games2blocks e constantsbootstrapgain.1. CLItrials tmp reg/attestation viarealhelpers e idempotente, mincal reduzido10; não proves fatigueedge real ou valida parâmetrosserving.

## tests/test_h9_missed_window_exit.py

Reportmock missed2risk1 emits stderralert mas exit0. Consequência: schedulerSUCCEEDED não significa ausência de missedwindows.

## tests/test_h9_shadow.py

Shadowapprovedbook none bloqueia; quote1.9fake emit idem, resultados2x1 settlementPnl.9/CLV vs1.8 e settledidem. Nome rejects early-result-and-other-book só exercita earlyresult, nenhum bookmakerdivergente neste corpo. Sem aposta externa.

## tests/test_historical_admission.py

Timeline sintético latestactive literalbool/pricefinitefloat/clockordered/ties failclosed; futureignored/permutationinvariant. Ambiguouslimitunknown e nãofill; retrospective receivedSept paraMay nuncaexecution apesarconditionalpositiveEV. Identity/market/skew30/age120diagnostics/resultignored/protectedwindow. Sem fonte externa ou execução.

## tests/test_historical_expansion.py

ShadowSQLite aliasraw/canonical/idem, scoreconflicts1/new1 contra productioninmemory impedepromotion. Returncount1 no rerun é processados, databasecount1. Não muda produção.

## tests/test_historical_numeric_boundary.py

Huge10**500price erro, limit0 preservado e negativo minúsculo unknown. Zero limite não filladmitted.

## tests/test_hostil_2026_07_18.py

Shin inválidos rejeita; legacy_marketplaceholder1x2todo1 omitido, validlinha selecionada. Sombra duplicate/rerunsettles1 e closeinvalidCLVNone com PnLsimulado, linhasinteiras recusadas. TruncatedSQLitequeryerror, readonlyconcurrentread n>=1 fraco (não exige novo commit2), writeerro. Não comprova relato de apostas real.

## tests/test_hotpath_cold_start.py

Importhook impede numeric/kernelcoldimport durante verifyregisteredFakeRedis, dupJSONinvoke rejeita. Sem medir latency deadline5s real.

## tests/test_hotpath_smoke.py

FakeRedis current/request exact registeredv2, missing/invalidpayload no wake, correlationrun/identity e noncurrent/timeoutreject. FakeCLIredaction/close e syntheticlineups11 enqueue sem autorregistro. ScriptLua não executado por fakeeval; não atesta .NETconsumer/kernelreal.

## tests/test_identity.py

Catalogtemp canonicalid/name/normalizedalias, fuzzyunknownonlysuggestion, targetunknown/normalcollision reject. Não autentica catálogo de equipes.

## tests/test_info_stake_cap.py

BETLOG_MAX_INFO_STAKE optional: absent aceita2uinformativo, configured.5caps, ou25 legacyvalidated ignora teto. Não universalcapitalgate; apenas manualjournalpolicy.

## tests/test_ingest_typing_boundaries.py

Runtimeconfigpath, pandasnullable score/stringfalse neutral0, HTMLFBref sintético Min1,234 ->1234/xAG--None. Sem scraping real.

## tests/test_integral_review_admission.py

Payloadstate trueStart/End/hasOddsfalse/missingclock impedem preço; rawduplicatekeys/receiptkeys/nonfinite e swappedparticipants com SHA válido recusados. Injetor competingaudit publica durante tmpwrite e nãooverwrite. Concorrência simulada determinística, não dois processos reais.

## tests/test_integral_review_domain.py

Simulatorliga unsupported SystemExit antes dbconnect spy; não simulatorimplementado.

## tests/test_integral_review_event_backtest.py

Fakefit/predict/loaders observam splitantes1ºtestday, multi-lines deduptrain e conflictingtargetsreject; unsupported/missingprob/invalidoddABSTAIN. Allsame day nofit. Não avalia eventmodelreal.

## tests/test_inventario_dados.py

DBsynthetic2021/2025coverage/xG/openflatcounts e JSON/missingclean. ASTconstexecute queriesSELECT/PRAGMA e substringmode_ro; f-stringregex procura só SELECT/PRAGMA portanto não prova inexistência de writes escondidos/dinâmicos. Holdout aparececontagem apenas.

## tests/test_kernel_cli_redis.py

Integration fixture skip sem URL/runid explícitos; loopback porta não6379 DB14 vazia identidaderealrunid e cleanup onlyhealthkey/sameinstance, semFLUSHDB. Subprocess healthcheck missing/healthy/expired sem criar absentDB; heartbeatrenew no numericmodel. Nenhuma execução neste estudo.

## tests/test_kernel_protocol.py

Fakeeval claim/completion verifica keys/lease5000 e correlation6fields TTL5; parser strictrequired/type/NaNInf/huge/additional, finite-rateoverflowbeforeclaim, invalid não poisonretry. Version decimalstringmaxint64 preservado; legacyV1recusado. Schema timestamps1e20 aceitos não chronologicalfreshness; Lua atomicity real não provada pelo fake.

## tests/test_kernel_runtime.py

JIT/py_func matemáticagridnormalização/DC/fairod dsrounded/zeroprobNone. Paramscacheclose/missing/stale/configtheta; warmup2calls; CLI missing/healthfake/coroutinehandoff. DaemonFakeRedis/pubsub/signalshutdown verificaheartbeatstartrelease/cleanup. Sem latency real ou RedisLua.

## tests/test_kernel_v2_runtime.py

Fakeeval injeta ConnectionError/CancelledError completion: release apenasattemptmatching e cancelreraises; computefailno complete. Poller fake recupera2semPubSub, Windowsfallbacksignalsrestored; in-flight async cancelfinallycleanup beforeclientclose. Não dura networkrestart ou comprova atomicLua.

## tests/test_kickoff_block_guard.py

Spy actual_fit trained_at<horizon emcadences1/4/9, simultaneousblocked>0/ distinct0, rarecadencefewerfits, emptyusablefail. Boa observação de modeltreino nos fixtures; não vintagepublication de resultadoprovider.

## tests/test_ledger_consistency.py

Thread pause leitura soblock: contendingadd/settle lançaOSError e não dup, appendnewlinepreserve/lockreleaseafterfail; bank lê único snapshot profit/exposure. Importedbank/contract/dupkeys/scores/invalidcap rejeitados e scoreorientation corrected. CLI relatosmanuaisbrutos semCLVcomprovado; locks process/threadfixture não immutableauthledger.

## tests/test_lineup_archive.py

JSONL idem porcontenthash e mudança rolehash registra2vintages. Hasha/b declarados, não recomputados sourcepayload neste teste.

## tests/test_lineup_inbox.py

FakeLuaevalcapacity10000 semMAXLEN/XTRIM e rawpayloadpreserved; oversized65k/NaN antes Redis rejeita. Não exige eventfullschema aqui.

## tests/test_lineup_inbox_redis.py

Conditionalintegration loopbacknon6379DB14empty/runidguard/cleanupownedkey. 10000 entries+pending7 recusa10001 semtrim; identicalretry gera2streamids preservapayloadclock; wrongkeytype nãooverwrite. Importredisrequired e fixture skips sem dedicatedservice; nãoexecutado.

## tests/test_live_capture_admission.py

Nested APIflagsparents/market/selection/missing strict, statusFalse nãozero, regionalbooknotgeneric, identity/preKO, inputsimmutable. Freshnetworkreceipt1sec separado changeold/limitunknown e executionFalse. Allpayloadfixture semAPIreal.

## tests/test_logic_registry.py

Assertstrings físicos9famílias e drawcatalog métricas/uncertainty/notvalidated. Prova documentação contémtermos, não implementação/evidência econômica.

## tests/test_market_0b_resolution.py

Fixtures probvar/cobertura e invalidodds separamNO_GO_LOW_RESOLUTION/noGOcoverage; variance sufficient apenas PROCEED_FULL0B,10cells/2sides/2permutations fixture e lambda distribution. Não poder estimado suficiente nem lucro.

## tests/test_market_anchor.py

Proportionaldevig/completeness e medianconsensus sócompletebooks ignora incomplete9odd; bestobserved separado fair; persistence COLLECTION_ONLY. Não sourceauth/executability.

## tests/test_market_edge_ordering.py

Declared60cells/devig/bin deterministic e permutations porstratum preservam outcomes enquanto predictorsfixed; requiredNvariance cresce, smallPSRDSRNone. Developmentpowerreference reused, plantedthreebands monotonicROItrue; missingEloPITexclui. Duas permutações nosfixtures não fullpower/economic evidence.

## tests/test_market_pricer.py

Gridmanual normalizado exact sums 1x2/DC/BTTS/OUintegerpush/DNB/AHquarterhalfstakes e non-squareerro. quarterwin/push/lose prob de stakeparts, não payoff completo de execução.

## tests/test_market_probs_date.py

SQLitefixtures editions/date±3d/currentlatest/mandoinverse e invaliddateerror. Aceita July15quote paraJuly13target, matchingaproximado não comprovaPIT.

## tests/test_market_research_jobs_manifest.py

Eachjob scriptrelative existentes underbrasileirao_scripts. Não schedulerconfiguration effectsexternos.

## tests/test_market_residual.py

Seeded200logitbinary/600multinomial planted signal learns probabilityorder/bounds, smallsamplefail e artifactsroundtripcapitalTrue reject. ShadowlowerCI/Kellypostfriction, frictionturnNoBet e undercomplement. Só treino sintético/in-sample; não calibrainterval outofsample/performance real.

## tests/test_math.py

Shinnormalização/vig/longshot bias matemático; _settle synthetic PnLofferedodd/CLVdevigclose e fallback openingmissing usa close. Time preKO estrito. Fallbackclose não prova cotação disponível antes decisão.

## tests/test_missingness_audit.py

3played/1pairedxGvalid contra fixtures, distingue realizedgoals legacyfallback, unmatchedforecastnotplayedexcluído. Sem fonteexterna/qualityreal.

## tests/test_model.py

NBalpha~0 coincide PoissonSciPy, gridprob1/DCnormalizer .97958/rhonegcellrejeita, drawdiagnosticargmaxonlyno robustchoice. Remainingfraction scaleslambda/0 degenerate/rejectoutside. Matemática não validaforecastlive.

## tests/test_model_xg.py

Cincofixtures fit4/5params xGtheta!=0, unitweightslegacyparity e recentweightsinfluence. Badcounts/weights/xG failclosed; empty permitecoldstartconstants enquanto optimizerfailtypednofallback; half-life360exact e futureexcluded. Não demonstra xG predictivegain ou fontehistorical.

## tests/test_odds_api_snapshot.py

Rawhash/strictJSON/identity/league/completelegs/marketupdateclock gates, late receipt nuncaprospective apesar oldchange, ABSTAIN/econFalse. Contraprova explícita adapter legado TheOddsApiProvider marca PROSPECTIVE_ELIGIBLE recebimento pósKO; novo decoder não promove. Não modifica adaptador protegido neste estudo.

## tests/test_odds_shop_stale.py

Fixture fresh2min/stale3h/nodate max15min exclui, maxNone desliga e aceita3books/morto melhorodd. Illegibledateempty. Não observa feedreal.

## tests/test_odds_source_smoke.py

Report rowsfake countsquotes/events/sanitizedmetadata/HUMAN_DECISION_REQUIRED/persistencenone. Não executa smokeHTTP.

## tests/test_operational_provenance.py

Tempfiles inputSHA64 envelopemorning sem toolsmetadata, subprocessfake lê jobconfig e envnightcapturedturn. Não predictor_ops execução ou dados reais.

## tests/test_operational_readiness.py

FaltacredencialBLOCKED; arquivos minimalfixtures snapshotsid1/dbtablesid/PASSreport+heartbeat reaches sóREADY_FOR_HUMAN_REVIEW/capitalFalse. Não valida autenticidade/processo de coletasevendias via esses minimalbody; staleheartbeatblock.

## tests/test_ou25_annual.py

Prices51/1.002placeholderrejected, oneunitfixture win1/CLVdevig e badprice dropsn0. Não elapsed2026economicdata.

## tests/test_ou25_certainty.py

Wilson8/10vs80/100tightens e confidence99 lower bound menor. Coverage estatística não repetida.

## tests/test_ou25_market_anchor.py

40synthetic fixedpoorprob.8 alternatingoutcomes selectsmarketweight0, groupingkickoffsplittrain18/test10, invalidpricesexcluem39/denom19. Futurelabels mutation firstweightinvariant. Exclusão invalidprice altera universo, não proofallfixtures economicprofit.

## tests/test_ou25_nested_replay.py

Seeded520prob Bernoulli/nine configs: train/teststrict/SameKOgroup/co ntaminated2024..26 declared/capitalFalse/strengthcap40; futurelabels pastconfig/selectionstable e repeatdeterministic. Holm/rawp, singletonCINone, CLVdevig, runnerPITbackfillrequired. Freezecandidate accepts handcrafted metrics200positive and source_hash string source, não revalida evidencia externa nesse teste.

## tests/test_parse_all_odds.py

Sofascorefixtures fractionaltoDecimal flatmarkets/multilineOU/AHmandoflip, missingnamesAHskip, openingseparate/no fallback. No providerlive ou capturetime.

## tests/test_parse_ou_scope_regression.py

OU excludescards/corners/partial/teamtotals/conflictingperiod/line/dupprices; allowFTaliases/knownid/noname/legacygoalname; validduplicatesaccepted and open/current separate. Strong parser scope fixtures, não fonteauth.

## tests/test_parsers_sofascore.py

Fractioninvalid/zero/3termsNone, initialmissingnãofallback, partial1x2retorna(2,None,4) semaviso enquantoOUincompleteNone; exactline não substring12.5. PreKO rejectsms, parse_matchnormalizesmsUTC/HTonlyfinished. Parsing não homologação.

## tests/test_permutation_test.py

Synthetic200permutation preserva scorepairs/marginals/time/determinismo e não muta, perfectprobabilities construídas doslabels batem climatologia; semsignal0. ProtegedholdoutCLIperiods e zeroPermreject. Controle planted não forecastreal.

## tests/test_persist_h14_prospective.py

TempDBcacheElo/params/1prior: clock2027prefixture windowpersistsnorm/idempotência/outside38h/postKO omit; futurematch não climatology, versionfingerprintchanges/missingcacheerror. Não autentica source/published clocks dospriorresults ou execução schedulerreal.