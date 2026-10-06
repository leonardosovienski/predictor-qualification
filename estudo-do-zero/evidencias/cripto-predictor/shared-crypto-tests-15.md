# Revisão semântica dos testes Crypto — bloco 15

Leitura integral de fixtures, mocks e assertions; nenhuma execução. Os cenários demonstram contratos sintéticos ou reconciliação de artefatos, sem estabelecer lucro futuro, autorização ou execução real.

## tests/test_trading_execution.py

Objetos locais de ciclo NEW/ACCEPTED/PARTIAL/FILLED/CANCELLED/REJECTED: imutabilidade, ordem errada, sobrepreenchimento e transições inválidas rejeitados. Ledger deduplica clientid e retira ordens fechadas; adapter simulado reconcilia fill reportado, missing gera break de quantidade sem correção automática. Nenhum envio à exchange.

## tests/test_trading_microstructure.py

Livro sintético valida spread/mid, ordenação e não cruzamento; walks BUY/SELL com VWAP e partial 8 de requested100. Square-root impact dobra ao quadruplicar participação; parâmetros inválidos rejeitados. FakeClient parse Binance sequence123 e timestamps locais, marca ausência de eventtime; limits/formato inválidos. Sem HTTP real.

## tests/test_trading_portfolio.py

Beta/correlação de vetores construídos, HHI, exposições assinadas, leverage, vol targeting, drawdown e liquidation distance de modelo. Missing mark, equity zero e margens inválidas falham. Reconciliation aceita tolerance1e-7 e retorna delta50 em divergência. Não comprova margem específica de venue ou performance de portfólio real.

## tests/test_trading_recovery_lifecycle.py

Recuperação de objetos locais UNKNOWN -> RECONCILING -> RECONCILED com reason obrigatório; estado conhecido impede reconciliação e expiry é terminal. Timestamp anterior à criação rejeitado. Motivo venue_timeout é string de fixture, sem consulta efetiva à venue.

## tests/test_trading_report_and_cost_policy.py

Relatório de posições fixtures calcula exposição/leverage e warnings de correlação/leverage, sem capital. CostPolicy seleciona PERP/spot e rejeita classe desconhecida; assert_verdict_grade rejeita ambos não calibrados. Último nome de teste sugere default calibrado mas assertion apenas compara asset_class PERP: não prova calibração.

## tests/test_trading_signal_adapter.py

Adapter converte FakeSignal em intent com fraction .5*.05, direção, timestamps e proveniência; inactive/flat/strength0 e uncertain default omitem. Família frozen/asset class desconhecida/custos spot sem calibração rejeitados. Maioria monkeypatch CALIBRATED_FOR_VERDICT para permitir construção; teste final sem patch confirma PERP default não calibrado. Não certifica custos ou envia ordem.

## tests/test_trading_store.py

SQLite temporário insere eventos/orderbooks idempotentes, conflito de status rejeitado, COLLECTION_ONLY/hash64 e ordem event<=received<=ingest. Nome append-only não é prova contra SQL direto neste arquivo; invariantes estruturais são tratadas em outros testes. Sem trading real.

## tests/test_trials.py

DSR com variância estimada obrigatória, penalização por número de trials inclusive Sharpe faltante e expectedmax monotônico. Registry deduplica e atualiza fixture com power_attestation=False. Helper frozen bloqueia família nova mas permite existente/None; wrappers públicos fazem controles adicionais. Spy cobra veto antes de core, sem registrar nesta análise.

## tests/test_v3_backtest_barriers.py

Barreiras em preços horários sintéticos: horizonte log return, stop long e take-profit short usam preço observado além limiar, não preço exato de execução da barreira. Sem trigger cai horizonte; sem entry retorna None. Não simula slippage ou fill de stop.

## tests/test_v3_circuit_breaker.py

CircuitBreaker estados CLOSED/OPEN/HALF_OPEN, limiar3, timeout0 e sucesso/falha de sonda; score1/0/.5 é mapeamento do estado. Sem clock controlado prolongado, concorrência ou provider real.