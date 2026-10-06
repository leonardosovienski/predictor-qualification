# Revisão semântica complementar Stocks

17 módulos lidos integralmente no conteúdo executável numerado; sem execução. Fonte/bytes conforme hashes.json e executable-chunks.json. Testes não revistos aqui.

## stocks_predictor/discovery_h17.py::score_outcome/build_cross_sections/summarize/run

H17 price diagnostic: hashes protocolo fixo e arquivos antes/depois; SQLite mode=ro normaliza quote_factor; universo snapshots2018-2025 até60 emissores dedupeCNPJ/PITfiles. Ordena accruals asc seleciona quintil mínimo20; nextsessionopen e nextmonthopen. Rejeita ausênciaendpoint/identitybreak/fatores conflitantes/unmodelled/overnight>30%. Available-caseIC versus complete-case spread; gates por metades fixas. Outputexclusive JSON com investable_alphaFalse e executableprofitNone.

Limites: Retorno é preço sem todos proventos/custos; classificação promising é screen não capital. Constância hash não autentica fonte. Calendário insuficiente pode gerar IndexError; não foi executado.

SHA256 `0254b3542f014649e4512daf40cbf3c63cbe8ee12640808775df397f5f97d4cc`, agregado `executable-09.txt`.

## stocks_predictor/discovery_reorganizations.py::validate_terms/score/run

Recalcula coortes congeladas com ledger de conversão/entitlements. Validaterms únicos ticker/ISIN/exdate,originsSHAURLs,ratiospositivos e datas. followrecursivo depth20; segmentos validamidentidade,fatores,jumps e successors; rights subscriptions zero semexercise. Stockmarks e cashreceivables teóricos somamterminal,creditdate marcadoverificadoantesexit. Dataset/primarysources/protocolhash comparados before/after;outputexclusive.

Limites: Inclui recebíveis NÃO spendable e frações teóricas na marca, não dinheiroexecutável. Não muda seleção/fatores dofirst. Physicalcredit verified é teste da data declarada, não brokercredit verificado nesta investigação.

SHA256 `359b3301baf44bc61f89fb3148bf689dec0036da232ae8a02a14be95c10fd304`, agregado `executable-10.txt`.

## stocks_predictor/discovery_value.py::value_feature/observe/period_statistics/summarize/run

H18earnings/capitalproxy,H19equity/capitalproxy. ExactdocumentkeyCNPJ/ref/version,receipt+1dia,PITsecuritydocuments,age<=550d,volume>=1MBRL,ONsingleclassACNOR,cotaçãofiscalpróxima<=10d. Ajusta sharesproxy por splitfactor desdefiscal e usa rawcloseasof; earningsannual330-400d. Quartetofamily×horizon1/3m;min20/topquintil;priceoutcomes. Cenáriomissing selected=-100%,other=+100%;haircuts36/72bp/horizonte;stablehalves/material>=.0042/coverage para priorizarrepair.

Limites: Decisão é alocação de pesquisa. investablealphaFalse/executableprofitNone; shares reportadas antigas e ausênciaeventosfull/totreturn mantêm proxy limitado.

SHA256 `ac9096efeff26f2d5672e0d08437f07aec779135da22017146baeb98b74e9347`, agregado `executable-11.txt`.

## stocks_predictor/discovery_value_repair.py::score/run

Remeasure preço conservando features e seleção congelada. Overnight>30 só aceito se reviewedmove casa exatamente ticker/date/ISIN/previousclose/nextopen/factor; notes explicitam override. Protocolhash e inputhash vinculados before/after. Changedreturns auditados; JSONexclusive.

Limites: Reviewedmoves/hash não transformam histórico exposto em holdout. Não há custos/totalreturn; aceite fonte declarada não comprova fonteexterna atual.

SHA256 `6c44d04b6f8cfede0f8e5ba00401528e83139ed9d0e7350b4ba98384df316453`, agregado `executable-11.txt`.

## stocks_predictor/document_panel.py::fundamentals_asof/capital_from_viewer

Filtra financialavailable/ref<=asof e seleciona latestref/version; filings conflitantes fora campossourcehash rejeitados. Security metadataoptional newestdoc e tickerissuer ambiguity rejeitada. HTML capital parsescellsIDsCVM,escala unidade/mil única,basisdate presente,classsums/treasurybounds;hashraw;outstanding emitido.

Limites: capital_from_viewer marca eligible_for_valuation=False/class-price equivalence/interveningevents restantes. Parser é layoutespecífico, sem webreal executado.

SHA256 `a8590fe6d3f9efb6586e502ef88cf6311cbee09ce892f305c05deaeccf59dc03`, agregado `executable-11.txt`.

## stocks_predictor/big_winner_v2.py::verify_selection_freeze/momentum_12_1/generate_decision

Modelo frozenidentity BIG_WINNER_V2_MOMENTUM_12_1_BASELINE; freezehashcanonical removeartifacthash. Momentum usa apenas datas<asof,253history,value[-253]→[-22];rankingfinite tiebreakticker/topceil20%;fallbacktickeronlyidentity. Shareadjustments<=asof aplicamem datasanteriores.

Limites: UNVALIDATED_PROSPECTIVE_CANDIDATE explícito. generate_decision expande **metadata apóscamposfixos, caller pode sobreporidentidade/status/cutoff; canonicalhash por si não verifica esses significados. Sérieschronological/corporateactionsadequados dependem caller.

SHA256 `190b90e5a0939b5460b98db4c4d4dea357b282014d211e4f27620683d18547aa`, agregado `executable-02.txt`.

## stocks_predictor/buffered_rebalance.py::freeze_rebalance/execute_rebalance

FrozenRebalance holdbookdigest projectedentry deepcopied,signalcrossidentity/date/lot/cashceiling. Integer_targets capital;buffer2.5% suprimedifference de holdingscontinuing. Exec requiresreviewedorderunitsTrue,digestentrymatch,execidentity/datelot,stageddeepcopy;rebalance e clearingcheck beforecommitbookdict.

Limites: Result SIMULATED_REBALANCE_NOT_PROFIT_EVIDENCE,incrementalsaletaxesFalse/profitNone. Pendingreceivables incluídos sizingceiling; atual funding é RetailBook. Deepcopy+commit não é transação concorrente crossprocess.

SHA256 `66ff3940575b47a778651a53e90f2f46f560895c2ab512b8efc2c278bfe57a39`, agregado `executable-02.txt`.

## stocks_predictor/cash_events.py::import_verified_events/require_coverage/total_return_series

CSVcash exige ticker/eventid/ex/pay/value/source;pay>=ex,finitepositive,coveredintervals,uniqueduplicate. Savepoint juntaevent ecoverage rows ourollback. Coverage uniãointervals contínuos; totalreturn exigefullcoverage e calcula units/splits+dividends por exdate nos intervalos e reinveste valor econômico.

Limites: Coverage fornecida pelo caller não prova fontes completas. Totalreturn econômica por exdate não simula availability de cash na paymentdate; não generalizar para carteira financável.

SHA256 `a20d9680d84bf5fffe380ec812ed155d107b6452157f85791c081a69801e8de7`, agregado `executable-02.txt`.

## stocks_predictor/economics.py::screen/classify

Screen compounding CAGR,populationstdvol/sharpe/drawdown comruin. Configdeclaredfinite(notbool)capital/minannualprofit/maxDD; falta retornaNAO_DECLARADO. Classifica equivalente histórico capital*CAGR vsmin/DD; esperadofutureprofitNone,forecastNOT_ESTIMATED,capacityNone.

Limites: BACKTEST_IN_SAMPLE_NET_OF_MODELED_COSTS; passage mínima explicitamente não deploy/capital. Valores declarados não têm boundspositivos todos; estatísticas nãovalidaminputsfiniteindividual neste módulo.

SHA256 `fa1778ac2e9274f00b5e882a0b30f08e4412d97236550735164665ae103d0098`, agregado `executable-12.txt`.

## stocks_predictor/entry_feasibility.py::entry_case/load_unit_reviews

Entrysignal→integersizing→emptyRetailBook→trade→settlement. Açõesentreasof/entry exigemreviewspecialbonusdifferentclass semremover original/unitsunchanged,known<=entry,hashsourceconfinement. Boundary semreview bloqueia,exceptions retornam BLOCKED. Outputstandard/fractional/unfilled/fundedcash.

Limites: SIMULATED_ENTRY_ONLY/profitNone/actualcontinuousturnoverNone; novaentrada não recebebonusright. Históriacontínua não qualificada.

SHA256 `0a4aafcdea65541eca50ada7cdb30b1d1c592f8c9a7d86034530296053482651`, agregado `executable-12.txt`.

## stocks_predictor/etf_hold.py::validate_quotes/simulate/selic_reference

BOVA11/BRBOVACTF003market010R$factor1,OHLC+volpositive,calendarcoverageexact. Decimalcentcost/tax; buy integerlot,opens ouworstopenclose,costtax15%default,unsettledsalereceivable,settleD+3before2019-05-27/D+2after. EquityyearPnl reconcile,equitymarkedDD/underwater/liquidityparticipation;grossSelicdaily series11 benchmarkrequirescoverage.

Limites: Singlehold conditionalprofit beforeunknownexpenses; fullynetexecutablenone/futureprofitnone/eventinventoryFalse/capacitynone. Model nãoauditaETFactions; nomes de regras tributárias são modelo implementado, não opinião jurídica atual.

SHA256 `c254225e605593efddb9dddeaf1e5a0287f57a19df742a3a414f0b7a4095e9b6`, agregado `executable-12.txt`.

## stocks_predictor/h20_research.py::verify_sources/signal_diagnostics/entry_diagnostics/run

Protocol/inputrawfixedhash,accountarchivesconfinement+binding,executionmanifest. QuarterlyH20 ARMS selection rank,previousINTENDEDmembershipbuffer comparisons; freshentryemptybookcases capital/costgrid throughentry_case;optionalentryreviewaddendum frozenhash. Exposure sourcegate explicit.

Limites: COMPLETE_H20_SIGNAL_AND_FEASIBILITY_DIAGNOSTIC_NOT_RETURN_EVIDENCE; nofreshholdout,plannednames notrealturnover,casesprofitNone,newhistoricalreturneval0. Read source/input current via inspectnotlongrun.

SHA256 `23e3a7763a3121fcbe72f80fd9c2d48a8f8400513193197de2b7aa02e843ed28`, agregado `executable-15.txt`.

## stocks_predictor/ingest_cotahist.py::download_cotahist/_pick_cotahist_txt/parse_cotahist

Corekernelnetdownload B3annualCOTAHIST ZIP. TXTselectionpreferssingleCOTAHIST named orsingleTXT elseerrorambiguity. Streaminglatin1decode zippedfile→cotahist.load_prices→dbconnection closed.

Limites: Networkdownload eDBingestmutáveis; nãoexecutados. Imports barecotahist/db exigem configuração de módulo/entrada adequada; arquivo ZIP nãoextraído globalmente por código.

SHA256 `40316fceaf8a8b43725203f4497b2cf817d09543d44ab77ddbf85ca6d0a0ab33`, agregado `executable-15.txt`.

## stocks_predictor/ingest_rj_universe.py::parse_b3_rj_list_html/save_snapshot/propose_universe_rows

urllib currentB3HTMLURLUserAgenttimeout60;HTMLtablecelltickerregexdedupe. Snapshot16hexhashrowsINSERTORIGNORE commit. Diffobservedsnapshot dates entries/exits;propose firstseen as candidate pendingreview,semalteraruniverso. Emptyparse failsbeforewrite.

Limites: Livecurrent list não fornece RJrequesthistoricaldate; firstseen écandidate. DefaultURL genericempresaslistadas; parser extrai tickerdequalquertable, nãoevidencia classificaçãoRJ real. save_snapshot retorna leninput mesmoINSERTIGNORE, não rowcountinserido.

SHA256 `209da4863c556c9dec2ad19180ca6e4fdf1ff3d2982527bef41d5d5d2009c1a5`, agregado `executable-17.txt`.

## stocks_predictor/monthly_etf.py::monthly_signals/MonthlyTax/simulate

BOVA11quotescalendarcanonicalexactOHLC/BDI02or14,quantitypositive;10completedmonthSMA longclose>SMA,nextexecsession. Hold/trendarms;reserveallmonthlycostsupfront;lots10;cash onlysettled+taxreserved,feesfixedvariable,worstcloseoption. SellpendingD+2/3,monthlyloss carrytax15%,terminal sale,wealthcent/yearaccounting.

Limites: CONDITIONAL_SIMULATION; external event/costcertification. Target flips only triggertrade; rejectednoaffordablebuy still sets previous_target=True so retry waits targetcycle. Terminal sell explicitlastday liquidationscenario,notfreshsignal. Não prova legislação/taxreal correctness.

SHA256 `56b4d8c1246c5107f5f962b3c8df5b24fa4f279611a4ba80f7526f1b815f2c2a`, agregado `executable-17.txt`.

## stocks_predictor/prospective_big_winner.py::append_decision/verify_chain/append_outcome_observation

SQLiteledger_eventsDECISION/CORRECTION sequentialhashchain,uniquepayload,eventhash,triggersforbidUPDATE/DELETE;outcomes uniqueid/horizonmetricsha andtriggers. Decisionid logicalhashasof/model/config/dataset;duplicatepayload idempotent,differentreject;backfill andsignaldayafterfreeze+nonemptycommit eligibility. Correction pointsoriginalhash;artifacthashimmutable compare existing.

Limites: verify_chain recomputa eventhash de payload_hash stored, não recomputa payload_json actualhash. Eligible usa signaldate lexical e truthycommit, semverifiedfreezecommit/schema/awaretime. primary_endpoint_mature=int(horizon==12),nãoelapsedtime12m nem observed_at causalvalidation. Leitura integral mostrou gates sãodeclarações estruturais; estudo nãoexecutou.

SHA256 `081c6670fb81ef7826162847af52b52585719f82ca0d7a68b20d26dc9c1ce805`, agregado `executable-19.txt`.

## stocks_predictor/report.py::build_markdown/write_report

Summarizeseries uses corestatsSharpe/Sortino/maxDD+equity,nonfiniteformatn/d. TemplateverdictPSR/bootstrapDSR/DD e _BIAS_NOTE H1..H19, avisos históricos/price/proventos; default reports path env/configROOT,filenamehypothesis/run writesoverwrite;emitcoreeventcodeversion metricsfinite.

Limites: BIAS_NOTE textos são DD embutida, não provaempírica de direção do viés. Mesmo runid pode sobrescreverMD. Template linha custo proportionalturnover/D+1 é declaração fixa não valida upstream execução específica.

SHA256 `df758c42f9e66be6ea959808d652eefb96424be269f0acc0786d91b433d40c82`, agregado `executable-19.txt`.