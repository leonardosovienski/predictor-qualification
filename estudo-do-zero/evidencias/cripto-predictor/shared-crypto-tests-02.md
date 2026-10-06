# Revisão semântica dos testes Crypto — bloco 02

Leitura integral de fixtures, mocks e assertions; nenhuma execução. Os cenários demonstram contratos sintéticos ou reconciliação de artefatos, sem estabelecer lucro futuro, autorização ou execução real.

## tests/test_api_guard.py

Fixture autouse desvia budget SQLite e events para tmp. Guarda habilitada consome quota durável, reset_for_test não apaga uso, bloqueio antes próxima unidade; desabilitada permite repetição e emite um aviso por processo. Teste chamado persistência entre reaberturas apenas chama allow duas vezes, sem reiniciar processo. News fake provider/cache garante uma chamada; feargreed cache pré-preenchido evita rede. Não atesta orçamento real do fornecedor nem concorrência.

## tests/test_architecture_boundaries.py

SQLite temporário missing read_only não cria banco; banco marcador abre sem migrar e escrita falha, bytes preservados. Outcomes SOURCE_UNAVAILABLE=>FAILED, FILTERED=>SUCCEEDED, combinação failed/succeeded=>PARTIAL distingue fonte de ausência de oportunidade.

## tests/test_architecture_contracts.py

PredictionRequest rejeita datetime naive; fallback excluído da elegibilidade científica, caso não degraded elegível. ResiliencePolicy timeout0 falha. Testes de contrato, sem avaliação de previsão ou provedores.

## tests/test_audit_economic_accounting.py

Preços sintéticos verificam stop no gap observado -10% e duração1h, horizonte incompleto e caminho intermediário não observado sem fill. Funding usa rates e mark em cada settlement, missing settlement None e janela sem settlement0. Fricção usa notional de saída; edge rejeita NaN. Família paper congelada levanta antes run_symbol mock forbidden, sem demonstrar mercado.

## tests/test_audit_expansion_regressions.py

Regressões em objetos artificiais: replay de fill inclusive completo idempotente, fillid conflitante rejeitado, reconcile percebe preço/fee/time/id alterados, ledger impede colisão order/clientid e receipt anterior. Nonfinite fill/book e preço duplicado rejeitados, depthupdate inválido/cruzado não muda snapshot/sequence, tinyqty não vira phantom. Soma lotes no portfolio. CSV tmp dedup por lote e conflito conserva bytes; lag mantém comprimento, DSL malformado falha, Spearman empate None, duplicate não oculta previsão faltante, PBO NaN e equivalence sem comparação falham. Traces JSON corruptos preservados, alvos desalinhados rejeitados, TradingStore venue inválida/short session, parserNaN. Sem exchange real.

## tests/test_audit_final_boundaries.py

Dados sintéticos validam neutralidade de momentum0/RSIflat50, scoreNaN rejeitado e cache corrupto conservado. Revisão de observação antiga não substitui latest. Heartbeat malformed/naive/futuro falha e JSON inválido unhealthy. Watchdog consulta diretório log operacional; um dia perfeito não cobre semana. CCXT client fake com timestamps duplicados rejeitado e discoveryvolumeInf não candidato. Nenhum polling real.

## tests/test_audit_model_integrity.py

H8 alvo usa horizonte real24h e lacuna não encurta; volume candle aberto excluído de crowding, volatilidade exige todas horas e SortedTimeIndex copia mapping. Testes HMM podem skip via importorskip hmmlearn/numpy: refit fake falhado preserva modelo/scaler/state; forward causal simétrico faz uma inversa por estado e probabilidades1/3. Não prova regime no mundo real.

## tests/test_audit_persistence_safety.py

SQLite temp comprova batch sinais conflitante atômico, mesma vintage sem hash não sobrescreve e histórico recebido agora conserva published_at atual. Storehealth futuro CORRUPT; micros ano2250 preserva precisão. Compaction conflitante conserva fonte, latest decodifica só última linha. Exportação pode skip openpyxl; workbook/csv escapa texto fórmula =1+1. Não aborda corrupção não coberta nem throughput real.

## tests/test_audit_public_anchor.py

Snapshot build/render/history mockados: manifesto público corrupto/null/estrutura inválida gera exit3, bytes conservados, statusH6 não criado. SQLite archive sela id2 e inserção retroativa id1 invalida chain e impede extensão. Não demonstra âncora externa imutável; manifesto permanece local.

## tests/test_audit_release_guards.py

Autocorrelação vazia/curta/constante/NaN não evidência; JSON NaN/keys duplicados rejeitado e conservado. Frozen sweep para antes dados/registro mocks; tentativasKelly ambas registradas antes primeira resposta sintética e duas identidades. Macro2026 não representa missing2024; paper idempotency lê corrupção mesmo após match, registro retrospectivo semspot contado e PnLNone; repetir amostra não aumenta Sortino. Não valida estratégia econômica.