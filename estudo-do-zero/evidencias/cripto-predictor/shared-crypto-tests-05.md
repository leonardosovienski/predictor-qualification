# Revisão semântica dos testes Crypto — bloco 05

Leitura integral de fixtures, mocks e assertions; nenhuma execução. Os cenários demonstram contratos sintéticos ou reconciliação de artefatos, sem estabelecer lucro futuro, autorização ou execução real.

## tests/test_dpl_aggregation.py

Fakeproviders consensusmediana por timestamp e publishedmax; TWAP sérieuniforme200, parcial mantém sobrevivente, allfail/invalidpolicy rejeitados e eventoaggregated. Breakerthreshold abre, clockmock timeout HALF_OPEN sucesso fecha/falha reabre. Não prova quorum independente, disponibilidade real ou TWAP irregular.

## tests/test_dpl_business_days.py

Calendário businessdays conta apenas weekdays, sexta+1segunda (inclusive7set feriado brasileiro não excluído), quinta+3terça, preservesdatetime, nnegativo rejeitado. published_atwrapper e helpercanônico identidade. Não é calendário completo de feriados.

## tests/test_dpl_dxy.py

ClientfakeFRED CSV parsers3/4valores, limit2, missingdot não interpolado, empty/HTML inválido rejeitados, customseries passado. published/vintage receiptcurrent e available_at_receipt mesmo lag0, sexta não inventa publicação segunda; helperweekday2=>terça e negativoerro. Snippet descrito real é literal fixture, sem fetch nem autenticação vintagehistórico.

## tests/test_dpl_feature_store.py

Fixtures forwardfill disponível, publicationfuture mantémNaN atédia3, stale2dias NaN, semsignal sópreço. SQLitetmp rawroundtrip/replayidempotent e featureNaNroundtrip; fakeprice/feargreed ingest materializa versão diária e forwardfill40 emduasdatas. Sem rede.

## tests/test_dpl_features.py

Sériessintéticas change24h10%, indicadores longos apenas comhistorysuficiente, harddata separa indicadores/descarta ts/feargreed/NaN, zeros evitamdivzero. CCXTvolumeBTC2*50000=USD100000 marcadoestimado, CoingeckoUSD100000nãoestimado. Não valida precisão de fonte.

## tests/test_dpl_football.py

MapperSQLite normalizeaccentcase, alias explícitoresolve/unknownNone, sugestão fuzzy não autoaplica. CSVliteral football canonicaliza times/escores e unmappedNarnia pula/registra. Events alignment usa somente ranking disponível antes kickoff, NaN sempassado. Teste é DPLgenérico dentroCrypto, sem integraçãoBrasil real nem downloadMartj42.

## tests/test_dpl_macro_calendar.py

Calendáriolocal exige33datas2026/8FOMC12CPI13PPIuniqueordenadas; schema/date/typeinválidos rejeitados. Fixtures dummy±1dia, signalnames por tipo, emptynone, published_at=ingestedat, negativewindowrejeitado e SQLite3sinaisroundtrip. Contagem não autentica fontes nem calendário futuro.

## tests/test_dpl_migrations.py

SQLite PK inclui source/name/ts/vintage, reabertura preserva dados e duas revisõescoexistem; schema11. ExecutaSQLisolado migração0005 legacyvintage vazio e0007feature_versionv1 preservando valor/PK. Não percorre todos caminhos de atualização histórica.

## tests/test_dpl_stocks.py

COTAHIST245chars sintetizado decodifica preços/volume, publicationlag18h declarado, filtraBDI/mercado e callbackinvalidzero não aborta lote. Arquivolatin1tmp providerlimit e PITrevisõesIPCA/SQLitevintages. FakeBCBpublished/vintagecollectedat12Abrnão referência31Mar; ingeststocksfakeSelic guarda provenance. Módulo dentroCrypto testa adapters genéricos, sem coletarB3/BCBnem alterarStock.

## tests/test_dsr_provenance.py

Ledgerhistóricounidadesmisturadas impedeDSR; fixturescompatíveis contam3tentativasmesmoSharpeNone(nsharpes2). Registryattestationfixture registra, alteraexpire2000 e updatefalha preservandobytes. Não valida poder real do atestado nem estimativa robusta fora amostra.