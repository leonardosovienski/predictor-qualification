# Como funciona — cripto-predictor

## Leitura rápida e identidade

O pacote combina aquisição de dados de mercado, diagnóstico por LLM, pesquisa quantitativa, governança e jobs operacionais. O usuário escolhe uma CLI; o ecossistema descobre um plugin mais estreito, de saúde/capacidades. Estes dois acessos não são intercambiáveis. O código local estudado é HEAD `88158f25ab067ed34a845a52f3816e215addf486`, `main` limpo no baseline, versão fonte `1.1.1rc4`; o remoto consultado aponta outro SHA. A investigação não atualizou a origem. Fonte OD: baseline.json, pyproject.toml e hashes.json em evidencias/cripto-predictor; leituras e testes no REGISTRO.log.

Nenhum resultado presente demonstra lucro pessoal, prontidão de produção ou capital autorizado. O plugin proíbe capital, e ScientificStateCharter rejeita capital/alavancagem/trading direto por LLM. Isso descreve controles inspecionados, não uma prova de ausência de qualquer outro caminho em todos os arquivos. A saúde observada deste Windows permanece NV: o banco privado e os processos operacionais não foram sondados.

## A — Propósito e fronteiras

`cli.main` oferece status, ingest/analyze, history, migrate-history, research e profit-recovery. `status` imprime NOT_PROBED e capital_permission False; não verifica operação. `plugin.CryptoPredictorPlugin.health` inspeciona Feature Store e mapeia READY/STALE/EMPTY/MISSING/CORRUPT para estados operacionais. `capabilities` lê governança, mas declara supports_prediction/settlement/collection False. Há contratos PredictionRequest/Result e protocolos em contracts.py, porém a existência deles não implementa métodos do plugin.

`governance.ScientificStateCharter.fail_closed` exige H1/H2/H3/H5 CLOSED_NO_GO e família funding_oi_hmm_v3 congelada. Os demais estados dependem do charter efetivamente carregado. Datas de incidentes e rotações expostas pelo plugin são rótulos hardcoded/documentais; não foram verificadas externamente.

## B/C — Estrutura, tecnologias e identidade de dependências

Pacote principal `GarimpoInvestimentos`; entrypoints `cripto-predictor` → cli.main, `cripto-predictor-job` → jobs.main; plugin `predictor.plugins/cripto` → plugin.PLUGIN. A camada dpl contém contratos, provedores, router, alinhamento, features, migrations e SQLite. Analyzers implementa LLM e backtest; v3 separa coleta derivativos, HMM, sinais, custos e WFA; research fornece ferramentas offline; trading inclui contratos/simulação; external_intelligence implementa adapters próprios. `packages/research-export` é pacote independente, versão1.0.1/Python>=3.11, com snapshot como dependência e bundle como extra.

Python fonte >=3.13,<3.15, Hatchling/uv; httpx, pydantic/settings, websockets, PyYAML. Extras LLM, v3 (ccxt/hmmlearn/numpy/sklearn), excel, science/test são escolhas distintas. Lock local fixa predictor-core3.2.1 wheel hash `10ef42f34ace8bb2df5f83ff7de2ceec79b035a25ea0a690e8942bd60d2fb4e3`, predictor-ops4.2.1 hash `da4fa540703879669caba919521ec7d3c33734b5d57781122823df8817346f0e`, ambos por URLs oficiais GitHub descritas em pyproject e uv.lock. Consultar investigação central de assets para bytes publicados.

**Divergência OD:** manifest declara predictor-research-protocol==1.0.3rc1; análise TOML de todos os package entries de uv.lock não encontrou esse pacote. O código importa research_protocol em admission/results/execution. Portanto manifest, lock e instalação não podem ser tratados como uma entrega coerente comprovada. Não foi executado uv sync para confirmar seu erro específico.

## D/H — Fluxo de análise completo

1. cli.main resolve caminhos antes dos imports, escolhe runtime_mode e instala redaction. analyze não permite flag ingest; Settings de análise exige credenciais do LLM/notícias selecionados.

2. main.run resolve ativos por lista ou símbolos já armazenados. Ingest separado usa ingestion.run_ingest: provider facade (fallback/consensus) + FearAndGreed, janela200 candles diários, alinhamento, sinais e features no FeatureStore.

3. Análise abre FeatureStore e usa snapshots.serving_context. Sem snapshot recente/identificado/features de contrato atual, ativo SOURCE_UNAVAILABLE. Mercado é offline; notícias e LLM podem alcançar rede. Cache compara fingerprint de features/snapshot/juiz/fonte/política, não apenas nome do ativo.

4. Prefilter opcional pode excluir ativo; guard pode impedir chamada por orçamento. NewsResult degradado e falta de indicadores são registrados. ai_insights escolhe juiz; multi é partição SHA256 do ativo modulo número de provedores, não voto de vários juízes. Ensemble_N repete o mesmo juiz e usa mediana de amostras bem sucedidas.

5. _analyze_once valida score finito0..100, sentimento e resumo. Falha retorna fallback neutro50 com llm_fallback True; main registra esse fallback e evita cacheá-lo. score_engine apenas limita/arredonda opportunity_score; sentimento não pesa. Divergência técnico/LLM é flag, não alteração do score.

6. prediction_payload preserva prompt, notícia, análise, juiz e snapshot normalizado. append_history persiste cada nova previsão antes do cache/export falível; summarize_outcomes distingue SUCCEEDED/PARTIAL/FAILED. Partial termina exit2. Exportação gera apresentação; score acima limiar não executa ordem.

Recuperação: retries LLM limitados a quatro tentativas; cota diária não tenta novamente; delays inválidos/longos encerram retry; cache fallback não prolonga erro. Não foram consultados provedores reais.

## E — Configuração e orçamento

config.Settings lê arquivo do perfil via local_runtime e ambiente, normaliza nomes/CSV, valida contratos e segredos em valores já resolvidos. DATA/OUTPUT/CACHE e CRIPTO_ROOT dirigem isolamento; caminhos fora da raiz geram LocalRuntimePathError. O estado real do perfil privado não foi lido. Provedores LLM Gemini/OpenAI e APIs compatíveis têm clientes preguiçosos e chaves repr=False.

**Divergência funcional OD/ET-RUN:** API_GUARD_ENABLED default True, mas MAX_INGEST_ASSETS/MAX_NEWS_ATTEMPTS/MAX_LLM_CALLS default0. `core/api_guard.allow` libera quando `not enabled or limit<=0`, com aviso api_guard_disabled. Assim instalação com defaults não recebe teto finito. A sonda de função isolada reproduziu True+0→allowed. Guard com limite positivo usa bucket dia UTC e SQLite BEGIN IMMEDIATE para serializar check/increment; orçamento lógico não equivale a quota real do provedor. O estudo não corrigiu código.

## F — Dados e persistência

`dpl/feature_store.FeatureStore`: raw_market_data, raw_signals, features_aligned, ingestion_provenance; migrations acrescentam snapshots/inputs/predictions/scorecards. As chaves incorporam fonte, símbolo, intervalo, ts; leituras de predictions ordenam ts/ativo. `_check_temporal` e os contratos distinguem tempos. Snapshots codificam JSON canônico e SHA256, normalizando não finitos; `market_payload` declara raw_http_response_preserved False. Portanto o contexto normalizado é auditável, mas não é arquivo bruto HTTP nem prova independente de disponibilidade histórica. Correções/upserts não tornam banco inteiro imutável.

Dados V3 persistem CSV/JSONL e modelo/scaler serializado; manter fonte, janela, versão e hash em separado. Esta investigação não abriu SQLite operacional, portanto tabelas efetivamente instaladas, integridade física, volumes e freshness NV. Retenção e recuperação total histórica não foram demonstradas.

## G — Algoritmos e limites científicos

- LLM: score textual0..100, juiz provider:model:hash_prompt[:12], ensembleN quando usado. Não é probabilidade calibrada ou retorno esperado; threshold de destaque não prova vantagem.

- V3: funding/OI/retorno/volatilidade e covariáveis → HMM treinado offline com scaler; regime_engine._forward_causal usa apenas observações até t na inferência. Porém pipeline.run_symbol ajusta em sua janela histórica e etiqueta DESCRIPTIVE_REPLAY; inferência causal não transforma fit de história completa em previsão PIT. WFA é caminho próprio com folds, purge e custos; resultados atuais não foram recomputados por treinamento/backtest extenso.

- economic_gate.estimate_edge calcula média IS com erro HAC Bartlett declarado; decide_cost_aware exige limite conservador líquido acima custo e retorna SHADOW_TRADE/NO_TRADE, capital_enabled False. Tela IS não é garantia de IC pós seleção nem lucro executável; funding e fricção são modelo de cenário.

- research.validation.walk_forward exige fim do label antes de test_start-gap e available antes de test_start, separa FUTURE/overlap/unavailable. Testes sintéticos reproduziram fronteiras.

- research.simulation.ScenarioLedger usa Decimal, identidade direta spot, reserva por venue/asset e fills explícitos com relógio monotônico/latência/duplicatas. Não estima fila, probabilidade de execução/impacto nem suporta derivativos. Ledger sintético não prova execução histórica.

## Integração científica CAIN → CRIPTO → CAIN

O código local vai além de exportar relatos: `research_admission.AdmissionStore` verifica ResearchTaskV1 autenticado, política do operador, handler allowlist BACKTEST_EXISTING_HYPOTHESIS, referências resolvidas, prazo, orçamento e idempotência/conflitos. Admissão aceita não executa sozinha. `research_execution.ReferenceStore` materializa objetos CAS só com hashes e caminhos confinados; ResearchExecutor revalida, gera identidade lógica/journal, delega worker por predictor_ops JobConfig shadow/capitalFalse e registra tentativa, efeito e resultado. Hash divergente/falta de bytes requer reconciliação. ResultOutbox valida correlação task/admission/policy/references, assina ResearchResult com consumer CAIN e usa PENDING/PUBLISHED/RETRYABLE/DEAD_LETTER. Permissões e chaves pertencem operador; nenhuma chave lida no estudo. Código implementado OD; execução real, instalação protocol e integração end-to-end atual NV.

Separadamente `crypto-research-export` admite fontes por hashes/commits e produz Snapshot/Bundle. `bundle.export` transporta charter/trial/attestation selecionados, não inventa ligação causal de attestation a trial e declara datasets não admitidos. Há contato documental com CAIN, não acesso compartilhado obrigatório ao banco.

## I/J — Testes, operação e evidência atual

Cobertura estrutural/ET-SRC está em INVENTARIO e refined-coverage.json; funções test_* não são casos coletados. CI define Ruff/Pyright/build/pytest, perfis3.13/all-extras e3.14 reduzido, container sem rede para store vazio e integração instalada com CAIN em ambientes separados. Workflows presentes não provam runs verdes no HEAD estudado; central ci-head-local.json discrimina consultas remotas.

**Divergência OD:** ci.yml constrói versão corrente, mas passo installed-wheels referencia dist/cripto_predictor-1.1.0-py3-none-any.whl; manifest1.1.1rc4. Não foi produzido build atual; esse alvo antigo é risco verificável de workflow desatualizado.

Jobs compõem run_job do predictor_ops, estado por PREDICTOR_OPS_STATE_DIR/platformdirs, exit0 SUCCEEDED/exit2 PARTIAL e jobs específicos. Agendadores/scripts Windows e Compose são declarados; não ativados nem sondados. Locks/heartbeat/watchdogs existem em fonte, não prova de scheduler vivo.

ET-RUN:13 sondas Crypto no runner domains_probe.py usando cópia independente, módulos puros e sockets bloqueados. Resultados em domain-probes.json/output. Runtime auxiliar3.12 com NumPy existente; não representa suporte integral3.13/3.14. API guard foi função AST isolada com config e event emit sintéticos, sem testar SQLite concorrente. Pytest/predictor_core indisponíveis nesse runtime; suíte, HMM, bancos, rede e instalação atual não executados. Clone e independência .git registrados; sem escrita original.

## K/L — Documentação, anexo e disponibilidade

PRELIMINAR salvo antes do confronto com README. README concorda com pesquisa sem lucro comprovado, DPL, LLM, WFA, limites históricos e integração documental. A tabela de engenharia cita metadados1.1.0 em corte anterior; fonte estudada1.1.1rc4. O documento avisa explicitamente que cortes datados não são painel ao vivo; logo contagens históricas de predictions e estado STALE não foram recicladas como OD. Anexo A é hipótese orientadora após descoberta; não confirma versões/funcionamento. A ampliação local ResearchTask/Result deve constar mesmo que ausente do anexo.

Separar: fonte observada; build não produzido aqui; release bytes investigados centralmente; ambiente operacional não inspecionado; modelo serializado só catalogado; serviço ativo não sondado. Lacuna real de instalação manifest/lock e riscos de defaults/CI permanecem abertos para missão posterior, sem alteração nesta investigação.

## Cobertura e continuidade

A-L possuem fontes e limites explícitos acima. Profundidade semântica integral de todos os módulos próprios ainda não foi certificada; coverage.json lista arquivos aprofundados e pendentes. Não converter leitura mecânica em revisão humana. Revisão posterior deve terminar módulos pendentes e suítes isoladas antes de declarar integralidade; preserva preliminar, identidade, hashes, logs e probes. Diagramas em diagramas/cripto-predictor_{sequencia,estados,er}.mmd são modelos INF dos caminhos citados, não observações de operação.

Atualização de escopo: outra raiz com versão mais nova foi localizada. Consulte [suplemento de épocas e contratos locais](../relatorios/SUPLEMENTO_RAIZES_DOMINIOS.md). Não misturar interfaces/finding desta fonte primária com a alternativa.

Aprofundamento adicional: `GarimpoInvestimentos/analyzers/factor_dsl.py`: Revisão semântica de todas funções: whitelist/aridade/validação tipos finitos, AST própria sem eval, lag>=1, rolling fechado i com amostra completa, variância amostral, None em desvio/divisor zero; warmup composição. Causalidade por índice exige input cronológico/alinhado; não comprova disponibilidade histórica externa.

`GarimpoInvestimentos/analyzers/backtest.py`: Revisão integral 973 linhas em blocos: contrato diagnóstico exclui legacy/fallback e mede mesma fonte de next UTC close em diante; caminho diagnóstico não registra Sharpe/veredito. Caminhos legacy de rede/estratos/eras/H6 separados; fechamento trials escreve registro e só deve executar cópia, não realizado. H6 pós-registro strict + n30; poder estático n250 contexto; capitalFalse e gross returns. Bootstrap externo Core não reexecutado.

`GarimpoInvestimentos/analyzers/trials.py`: Shim Core: strictDSR rejeita Sharpe de base diversa; load valida; registro no caminho oficial protege closed_trials e família explicitamente declarada, caminho alternativo não herda charter; encaminha atestado existente sem inventá-lo. Novo nome sem family não bloqueado por familyguard; integridade Core separada.

`GarimpoInvestimentos/dpl/alignment.py`: Todas funções revistas: availability=max published,vintage,ingested, bisect<=candle, prefixwinner por timestamp+datarank impede revisão velha substituir observação recente, staleness pelo dado; input candlestick close é entregue sem verificar sua própria disponibilidade/close_time neste módulo. Causalidade signal dependente contratos source.

`GarimpoInvestimentos/dpl/hash_chain.py`: Todas funções revistas: seal em savepoint verifica antes estender; canonical fields predictionsarchive, prev+payload SHA, detecta lacuna/retroinserção/tamper; unsealed posterior contado não erro; manifesthead anchor externo necessário contra rewrite coerente total. SAVEPOINT não global processo; integrity hash não assinatura de fonte.

`GarimpoInvestimentos/durable_io.py`: Integral: OS advisoryfilelock inode stable timeout10sec released finally; tempuuid exclusive write flushfsync replace then cleanup; strictJSON rejects duplicates/NaN; corrupt history errors, listdict validation, append lock atomic rewrite. Directory fsync not observed; lock only cooperating writers.

`GarimpoInvestimentos/core/cache.py`: Integral: fingerprint sorted market/judge/source/policy defaultstr; load corruptedempty emits diagnostics, rootdict/entry/timestamps bounds age>=0<TTL; save validates strict original under lock, merges cached valid, stamped cached_at precedes **entry so caller cached_at may override newstamp; atomic finite JSON. Cache corruption read vs write behaviors differ deliberately.

`GarimpoInvestimentos/analyzers/gate_power.py`: Integral: syntheticdailyGaussian overlap hdays, score=true_rho*normalizedfuture+sqrt(1-rho²)*noise => latent linear/Pearson rho, gate tests rankSpearman via Core; bothsign CI rejects0 detection, defaultsim400 boot1000 deterministic seeds, no write hypothesis. Simulated DGP and TypeI/power not empirical market effect or exact ranktarget; invalid n_sim/horizon/rho not locally explicit validation.

`GarimpoInvestimentos/analyzers/pbo.py`: Integral CSCV stdlib >=2configs, splits even>=2, same lengths finite >=2obs/block; chronological equalblocks dropsold remainder, allhalfcombinations default16=12870, maximize IS sortedname tie, OOS rank strictlower conservative ties, logit rank/(N+1), pbo logit<=0; Sharpe nonannual mean/sampleSD zero returns-inf. Same dates assumed by arrays not validated; noncausal CSCV diagnostic selectionoverfit not walkforward forecast gate.

`GarimpoInvestimentos/analyzers/judge_calibration.py`: Integral descriptive score marginals mean/sampleSD/median/range/thr frac/nassets; groups first provider component of signature so model/prompt versions pooled by provider locally; source _load_rows filters valid diagnostic. No paired assignments, no concordance statistic nor trialwrite. Provider differences confounded asset fixedpartition; calibrated probability not established.

`GarimpoInvestimentos/analyzers/hypothesis_loop.py`: Integral: prompt whitelist generated, human causalmechanism instruction not semanticvalidated; canonicalrecipe16hex dedup, JSONfinite malformed receipts, fromrecipe validations rejected, all statuses recorded under filelock atomic rewrite after LLM call. No trials/promote; evaluation warmup finitepairs rankbootstrap block horizon*freq, description only. IDs recipe only (not horizon/dataset), history prevents re-evaluation same recipe new horizon globally; empty JSONarray yields no proposal receipt; sourceavailability delegated.

`GarimpoInvestimentos/analyzers/hypothesis_loop_runner.py`: Integral: existingV3CSV historical features5, oneasset timestampsuniqueascending, exactts+horizonMS forward logreturn nullmissing/invalid; no indexshortcut. proposals saved then accepted evaluated and evalsappend, two ledgers separate transactions; failure may leave accepted unevaluated receipts. RealGemini default, dryrun synthetic proposer own files; no scheduler, newprospective data, trialwrite, or verdict; cannot fulfill economic/predictive protocol solely this replay.

`GarimpoInvestimentos/dpl/feature_engineering.py`: Integral: sorts 1d candles unique timestamp retains contiguoussuffix no gaps, changes 1/7/30 actual days, volume CCXT base*close approximation flags vs CGUSD, indicators nested harddata excludesfeargreed/nonfinite. Same source/asset/unit consistency delegated to caller, not checked here.

`GarimpoInvestimentos/dpl/entity_mapper.py`: Integral: canonical/alias tables source/type/normalized PK, normalization NFKD lowercollapse, curated upsert; resolver exactnormalized returnsNone, fuzzy difflib cutoff.6 suggestions only; no FK integrity canonical in alias SQL, curated_at default not updated upsert; no historical version retention of aliases observed.

`GarimpoInvestimentos/dpl/macro_calendar.py`: Integral: localschema/calendar parse, eventtypeuppercase, dummy ±window pertype/day, all published/vintage/ingested receipt time flags historyunverified, write COLLECTION_ONLY. Publishedschedule historical availability not invented; todayreceipt cannot establish past replay provenance. No calendar external verification repeated.

`GarimpoInvestimentos/dpl/business_days.py`: Integral: genericdate/datetime adds nonnegativeinteger n excludesweekends only; publication proxy addition, no holidays/releasehours/revisions. Docstrings predicate conditional lag not actual publishing receipt.

`GarimpoInvestimentos/research_worker.py`: Integral: exactrequestschema/type closed refs all5, bounded>=4obs, orderedobservations awareclock available>=obs<=cutoff, finitegross/funding, costref match; deterministic fixturegross long1 not model predictiveforecast. Net equity uses CostModel roundtrip+funding, BUT reported net_bps=gross_bps-(fee+slippage) ignores secondleg/funding; baselinecomparison/economicstate use this discrepantmetric. Trialcounts1, executed_at registered_at, iidboot500seed17; registry/effect separate idempotentwrites. Primary V1 only, alternate worker differs.

`GarimpoInvestimentos/v3/costs.py`: Integral: finite nonnegativefee/slip perleg, friction(1+exitratio)*fee+slip*absposition, constant funding rate/horizon8h signed, netgross+funding-friction; zero position returnsgross unmodified callerresponsibility. No realfee/tier/fill/variablefunding receipt validation; defaults assumptions.

`GarimpoInvestimentos/dpl/providers/ccxt_base.py`: Integral: lazyCCXT ownclientpercall finallyclose, supportedinterval map, requestlimit+1 filter candleopen+duration<=now, duplicates integerpositive timestamp reject, OHLCpricepositive rangecoherence volumenonnegative finite, published_at inferredclose, sorttail; timestamp inferredavailability not verified historical exchange release/receipt. No actual network run.

`GarimpoInvestimentos/dpl/providers/coingecko.py`: Integral: dailyonly withvolume, authDemo injected/env not read secret study, retry Core; marketchart syntheticO=H=L=C daily midnight pricepoint minusday, availability+10min assumption partial omitted, volume timestampsame required duplicatesconflict, sorttail, pinghealth. OHLCsynthetic cannot support intradayexecution/highlow models; receipt/historyproof absent.

`GarimpoInvestimentos/dpl/providers/bcb.py`: Integral: series/name integer validation lagcompat ignored not backdating, breaker failurefetch/success beforepayloadvalidation; latestSGS observations dateparse finite ref<=receipt, duplicatesconflict; published=vintage receipt qualityhistoryunverified, sorted; revisions no historical availability proof. Parsererror does not record breaker failure afterfetchsuccess.

`GarimpoInvestimentos/dpl/providers/fear_greed.py`: Integral: TTLfinite positive monotoniccache perlimit retaining vintage, fetch receivednow referenceAPIts <=receipt, finite0..100 duplicateconflict, published/vintage receipt flags historyunverified; emptyerror, sort cache; no sourcepublishing claim or live network probe.

`GarimpoInvestimentos/dpl/feature_store.py`: Integral849lines em3blocos: readonlymode URI query_only no migration, writableinfra/migrations recursive_triggers protects replace; rawOHLC current-state upsert PKsource/symbol/interval/ts overwrites samevintage historicalcorrections, not bitemporalraw. SignalBEGINIMMEDIATE identity conflictcompare fullmetadata, receiptflag clocks vsdefault45daylag, enrichedoptional, dedup identicalcontent acrossvintage; windows eventtime no asofclock clause (caller alignment needed). Qualityscorecard append / observation immutablehash manual check, provenance normalizedpoints SHA optional no rawHTTPauth; featuresversion PK coexist but sameversionupsert. Predictions+input snapshot sharetx conflict immutable preservedinput, legacy rows withoutsnapshot may update; archive via migrations. snapshots contentaddress latestcollected decodeverify. close_on optional published cutoff; closed_daily_price exact same source previousdayboundary only publication>=boundary<=asof positivefinite. latest_features versionv1 no asof and latestsource tielackssecondaryorder; runtime serving not PITreplay unless snapshot path establishes clocks. No realDB execute.

`GarimpoInvestimentos/v3/backtest_v3.py`: Integral1720lines em4blocos. IS180/OOS30/purge7/step30 por timestamp, continuouscausal features then HMMfit IS only, forwardfilter contiguousISpurgeOOS. Price known t uses hourlyopenkey t-1h close, barrier hourlyclose observed fillsproxy (missingpath rejects); realizedfunding exact8hsettlements mark/entry withintrade coverage required. Position direction*strength*kelly, simple expm1(logret), friction exitnotionalratio, funding signed; multipleconcurrent positions cash+reserved allocationequity closingeventsbeforeopening, no intratradeMTM, MaxDDclosed only. Optional edgecalibration ISlabels mature<=ISend directions HAC estimate; rejectedsignals zeros notexecution. Spearmanblock usesCoredefault (not horizonexplicit), IIDPSR overlapping conditional selection invalidconfidence; netmovingblock min21,n/3 descriptor notpostselection. Nonfinite coerced0 logged; diagnosticGO thresholds PSR>=.8 IClower>0 DD<.2, final_verdict ALWAYSUNVALIDATED stateDESCRIPTIVE_REPLAY capitalFalse. Hashinputs before/after, uniquerunatomicreturns artifact ownresearch_runs; no frozenreturns overwritten. Sweeps familyfreezecheck+allattempts registered before results, bestGO branch cannot happen while finalUNVALIDATED; no sweepactualrun. Fundinghistorical unavailable receipts/priceperpproxy/fill assumptions preclude economicvalidation even computedcosts. Source feature contract/RegimeEngine dependencies separately reviewed central.

`GarimpoInvestimentos/research_recovery.py`: Integral primaryV1: newbundle staging+atomicreplace, eachSQLite onlinebackup integritycheck, filescopied SHA+sizes manifest, verify rootrelativepath/hash/check eachDB, restore new/empty via staging verifies destination. No global multi-store snapshot, activeartifactwriters not locked; names mapping operatortrusted no pathcomponentvalidation here; verify checks listed files not exhaustive inventory. Rootresolve may hide source root link before childcheck. Alternate recovery probe not primaryexecution.

`GarimpoInvestimentos/research_results.py`: Integral primaryV1 signedResearchResult CAINoutbox protocoldep: validate+authorize admitted task/research/hypothesis+payload/policy/resolved hashes, signer fixed or keyStore, result/message uniques BEGINIMMEDIATE idempotentconflict, pendingmax100 PENDING/RETRYABLE, sendpersist beforetransport then ACKidentity+attemptcount awaretimestamp, retries3deadletter, published cannotfail. Acknowledge publicmethod not authenticate receipt itself; transportcaller must supply trustedACK. reconcile counts only (not resulthash/fileaudit unlike alternate). OPSSUCCESS not inferredscience here; producer validates provided state provenance againstadmission.

`GarimpoInvestimentos/runtime_mode.py`: Integral defaultanalysis select explicitglobal; if configalreadyinitialized and mode differs raisenewprocess, no env relaxanalysis. ModeLiteral compileannotation not runtimevalidation at selector; downstream config may validate values.

Admissão/execução primária (revisão integral 484/527 linhas): submit valida assinatura CAIN, escopos, política e registry; execute revalida antes materializar, usa identidade lógica e OPS SHADOW com capital_permission=False. As quotas contam todos os ACCEPTED persistidos, sem liberação na conclusão observada: inferência de limite vitalício, não quota corrente. Journal transacional preserva hashes/attempts/reconciliação; não há lock exclusivo por experimento nem CAS de estado na transição, portanto concorrência não está validada. Timeout passa ao OPS; CPU/mem/disco declarados não são prova de enforcement. Fonte: research_admission.py e research_execution.py, hashes e leituras em REGISTRO.log.

Trading primário: execution.py é máquina de estados pura com adapter simulado em memória; microstructure.py anda apenas a profundidade observada e exige resnapshot ao perder sequência. Book/VWAP é cenário, sem fila ou recibo de execução real. cost_policy.py mantém CALIBRATED_FOR_VERDICT vazio; signal_adapter.py exige for_verdict=True, portanto sinais ativos spot/perp não geram intenção nesse estado do código. TradingStore persiste hashes, relógios e sessão, compacta v1/v2 para zlib/layout denso sob verificação de metadados; não há triggers universais de imutabilidade nessas tabelas. Scorecards de cobertura são fração de minutos com observação, não uptime contínuo, e não promovem estado COLLECTION_ONLY. Fontes e SHA: trading/*.py no REGISTRO.log/coverage.json.

## Épocas remotas observadas

Os manifests do main remoto e os assets do Anexo foram verificados separadamente, por SHA/versão. Veja [confronto do Anexo](../CONFRONTO_ANEXO_REMOTO.md). Essas identidades não ampliam automaticamente a cobertura semântica da raiz primária nem provam integração runtime.

Reconstrução V3: features exigem funding a cada 8h por janela90 e candles fechados consecutivos; OI usa as-of e spot fecha uma hora antes da chave funding. RegimeEngine ajusta scaler/HMM3 na amostra fornecida (full covariance, ou diagonal com extras nomeados), rotula estados por retorno médio IS e filtra por recursão forward. Essa recursão não olha observações futuras, mas modelo/scaler ajustados na série inteira continuam retrospectivos. O pipeline grava DESCRIPTIVE_REPLAY e o WFA separado precisa fit IS por fold. Sinal contrarian usa fundingz>=2/OI crescente/regime bull-sideways para short, z<=-2/regime bear-sideways para long; confiança mínima0.60, qualidade/regime incerto produzem FLAT; strength é intensidade, não retorno esperado. Macro exige disponibilidade documentada ou hipótese explícita; receipt/checksum de arquivos Vision e CSV não provam publicação histórica. Todo bloco revisado integralmente nos arquivos v3 feature_builder, regime_engine, signal_engine, pipeline e collectors; registro/hashes em coverage.json/REGISTRO.log.

External Intelligence primária usa SQLite separada e revisions/receipts com triggers de imutabilidade; as-of usa provider_available_at apenas para PROVIDER_PIT, e primeiro receipt para as outras classes. Nansen/Santiment/CoinMetrics históricos são RECONSTRUCTED, permissões UNKNOWN por padrão ou política explícita; rights são sumarizadas no contexto e consumidor deve aplicar autorização. O audit full-vs-truncated repete context_equal em quatro campos (late_revision/reconstructed/future_deletion), portanto não são quatro perturbações independentes. CoinMetrics valida hosts de next_page_url mas não tem teto de páginas/URLs visitadas/orçamento total no loop. CLI context-at grava snapshot mesmo sendo consulta; não foi executada na fonte. Expanding z-score/condicionais são pesquisa descritiva sem custos ou validação causal externa. Fontes external_intelligence/*.py integralmente revisadas; coverage/REGISTRO preservam leituras.

## Observação e recuperação econômica reconstruídas por código

A governança (governance.py) rejeita capital, alavancagem e trading LLM direto, exige H1/H2/H3/H5 CLOSED_NO_GO e congela V3. SHA de plano/ativação verifica conteúdo canônico, sem comprovar coleta material ou assinatura de aprovação. A maturidade (observation_reporting.maturity_report) permanece bloqueada: scheduled_tests, human_approval e custo medido são False; gerar relatório retorna0 sem promover ciência. Scorecards técnicos contam slots por instrumento e idade desde evento, com requests padrão1/1; não confundem cobertura com retorno econômico.

profit_recovery_v1.py separa catálogo ORACLE e detecção por prefixo; previsão usa resultados cujo published_at já amadureceu. A entrada reconstruída não prova received_at histórico; intervalos normais IID e melhor baseline selecionado no próprio painel são diagnósticos. O corte60/20/20 não purga labels que cruzam fronteiras. O arquivo de ledger contém outcomes de todos os candidatos, incluindo a seção final descrita como sem métricas.

Há limites adicionais objetivos: paper_execute_v2 reduz o fill pela profundidade disponível na saída futura, registra latência sem deslocar execução, e portfolio_summary soma fechamento serial sem reserva ou margem. money_left_on_table subtrai PnL monetário capturado de soma de retornos fracionários capturáveis, unidades incompatíveis quando paper não está vazio. _return_metrics define operação ativa pelo retorno bruto diferente de zero, dispensando custo de uma operação com retorno bruto exatamente zero. Os rótulos REALISTIC_PAPER_V2 e POSITIVE não validam fills, capacidade ou lucro. Todas as rotas preservam capital_permission=False.

profit_research.py compara só contas com moeda, capital, período, cenário e evidence_kind iguais, exige seis categorias de custo e distingue net desconhecido de teto conhecido. renewal_research.py reconstrói fluxos e limita economias de renovação sob quantidades fixas; seus bounds otimistas e sensibilidades não são backtest executável.
