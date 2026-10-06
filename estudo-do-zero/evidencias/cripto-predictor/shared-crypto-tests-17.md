# Revisão semântica dos testes Crypto — bloco 17

Leitura integral de fixtures, mocks e assertions; nenhuma execução. Os cenários demonstram contratos sintéticos ou reconciliação de artefatos, sem estabelecer lucro futuro, autorização ou execução real.

## tests/test_v3_production_paths.py

Seis paths mutáveis V3 iguais DATA_DIR/CACHE_DIR configurados. Importa módulos, sem executar ingest/paper; igualdade de constantes não audita todos efeitos laterais.

## tests/test_v3_regime_engine_extra_covariates.py

HMM seeded quatro regimes artificiais, extra covariates nomes/dimensões obrigatórios, inferência e invariância de prefixo com fit150; fingerprint inclui extras/covariance full->diag e modelo H7 não carrega H1. Fake subclasses injetam falha fit/predict duas vezes, seeds42/43/44 e máximo retries error. Covars offdiagonal0 e predict_last repassa extras. importorskip numpy/hmmlearn/sklearn; primeiro nome default-comportamento anterior apenas labels/len, sem golden.

## tests/test_v3_regime_staleness.py

Pickle de DummyModel preserva fingerprint/state_map, rejeita fingerprint999 e legacy sem fingerprint mantendo bytes. Não testa pickle hostil nem treina; fingerprint é compatibilidade declarada, não autenticidade.

## tests/test_v3_signal_engine.py

SimpleNamespace de feature/regime testa gates quality.4 critical, uncertainty/degraded, confidence e funding/OI squeeze, strengthclamp, threshold overrides e signal time>=exchange. Posterior/confidence são fixtures, HEALTHY é enum operacional, não previsão correta.

## tests/test_v3_wfa_actual_slicing.py

WFA real orchestration com loaders sintéticos e SpyEngine observa arrays consumidos: fit180dias, embargo7, OOS30, step30; infer inclui embargo sem usar avaliação, calibrations só labels maduros dentro treino. costAware False/True, nenhum sinal ativo causa RuntimeError nenhum fold completado. Boa verificação de slicing real, sem model fit/edge.

## tests/test_v3_wfa_purge_contract.py

Gerador de folds implementado no próprio teste replica fórmula de constantes e comprova purge/step; nome slicing real apenas aritmética ms. Contraprova fakepurge0 trivial assert0. Teste165 cobre consumo da função real e evita confundir este contrato com execução WFA.

## tests/test_watchdog_coleta.py

SQLite minimal fixture e watchdog import por spec; fallback1 não conta, NULL legado conta como real, dia distinto fora. Não prova que NULL tem juiz autêntico nem fluxo collector real.

## tests/test_watchdog_paths.py

Watchdog paths externos; predictor_ops run_job subprocess fakeexit0/1 no pytest execution neste estudo, exige heartbeat schema SUCCEEDED/missing/FAILED. H6 bridge só alarma avanço local mais published antigo; valores iguais há30dias não alarmam, diferença recente12h tolerada, última linha vence inclusive regressão30->6. Não valida verdade/assinatura H6 ou saúde contínua.