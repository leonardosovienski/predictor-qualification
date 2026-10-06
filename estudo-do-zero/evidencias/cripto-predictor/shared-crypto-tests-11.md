# Revisão semântica dos testes Crypto — bloco 11

Leitura integral de fixtures, mocks e assertions; nenhuma execução. Os cenários demonstram contratos sintéticos ou reconciliação de artefatos, sem estabelecer lucro futuro, autorização ou execução real.

## tests/test_predictions_append_only.py

SQLite archiveINSERT/preUPDATEsnapshotpreserva anterior70 enquanto live permitecorrection40; replaylive1archive2 e DELETEblocked. Reopenmigrationpreserva; legacypré0016populado nãoarchivebackfill, primeiroupdatecaptura70. Teste nome migrationfalhameio apenas aplica migraçõesprefix e reabre restantes, NÃO injeta falhaintermediária/rollback. Appendonlyarchive difere liveupsert.

## tests/test_prefilter.py

Prefilter disabledall; syntheticbull/bear seleccionados, lowvolume/weakmomentum/missingtechnical reasonaudit. Critério seleçãoLLM não efeito futuro.

## tests/test_profit_recovery_v1.py

ProfitRecoveryfixtures oracle separado causal/nottraining/capitalfalse/noquotespaperNone. Expanding forecastunmatured sample0WATCH, assumedcost37bps bloqueiaTrade; observedmarketflagfabricado permitepaperTradecapfalse. Quotesfakefull/partial/causalitycrossed, portfolioPnL1/cash1001/drawdown e MLTTseparaoracle/policyunidades. Protocolcompletehashorderstable/defaultNOTREADY/syntheticcontrol etiquetado, samecohortbaselines, operationalconfigured vsenabledNOTVERIFIED. SQLite readonlyreplayhash/output/nogaps e intraday1h/4hNone. Episodeeffectivecount<=signals. Não actualobservedmarket nem mercado/executioncapital.

## tests/test_profit_research.py

Decimalcase syntheticnet-6.97/break-even11.35, unknowncost/cashflowNone nãozero e positivearith candidateonly verifiedfalse/capfalse. Contractcapital/time/evidencekind/risk/costnotes/comparisonunits/windows/scenarios reject; rankingsemtotalprofit/dedup. Transitionshold/adjust/reduce/close/reversecostdelta, lot/instrumentvalidity. APY/APRexplicitunits, yieldsstables/wrappedunknownretidos semfreshnessverified; missingapyBase não usaaggregate999, dup/invalidreportedtodos. Snapshotlocalhash/source/time/status e JSONNaNdup reject. CLIhash/exit2; HTTPMockcaptureGETnooverwrite/networkfailure nãoempty. Semyieldreal ou costsvalidated.

## tests/test_provider_runtime_config.py

DotenvfakeCoinGeckokey reachesfacade/collectorsheaders3Mockrequests, precedenceprocess/injected/anonymous; CCXTfake201rows incluiopenhoje e devolve200closed/SMA200100. Não valida keyreal nem disponibilidadedeAPI.

## tests/test_provider_validation.py

require_finite rejeitaNaN±Inf e aceita valoresfinitosinclnegativo0/negative, messagefieldproviderasset. Finite não implícapricepositive.

## tests/test_quality_snapshot.py

QualitySnapshot645linhas integral: SQLitevazio/currentday/fallback excluídos,maturitythresholds/targetpower250/capitalfalse. Directionstatsneutralexcluded,buckets,majorityN4/providerstats fixtures; historyJSONLprefixpreserved. H6gate<30omiterho, >gatepublishesdeclared, poweroptional/render. Writeidempotentpreservaobservedat/mtime, corrupt/nonUTF8 conserva, gitignoreartifacttrackedcheck. PublishedregressionrefusedporNdrop mas allow_regression=Trueexplicitpermite; endtoend1row seguido snapshotmaduro31 MANUALfabricado e emptydbnãoapaga. mainbuild/render/historymocks, manifesttmpisolado e primeira-publicação/changeavisos. Não comprova31maturedreal nem economic.

## tests/test_readme_reflete_charter.py

READMEtablesregex exige hypothesesigualcharter/status/trialsubstring. Teste documentconsistency, não valida hipóteses ou status por evidência.

## tests/test_recover_aave_history.py

FakeRPCheadersblocktimestampn//4: binaryboundary403/404 <40calls, missingbracket/forkreject. Synthetic13Rayincome/Fractioninterest/costreconcile, zero-liquidity/paused/frozen tornamexecutabilityfalse, missingperiodreject e sensitivity7.25 explícita allinprofitNone; ABIhexmalformedreject. SemRPCreal nem withdrawal.

## tests/test_registry_e_scripts_encoding.py

PS1physicfilesexige ASCIIouBOMUTF8/decodable, trialJSONUTF8/mojibake6patterns/dedupname e grid16tentativas. Não parseexecutaPowerShell nem confere semântica/poder trials.