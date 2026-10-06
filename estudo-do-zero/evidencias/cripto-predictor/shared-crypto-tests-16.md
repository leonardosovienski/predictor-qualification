# Revisão semântica dos testes Crypto — bloco 16

Leitura integral de fixtures, mocks e assertions; nenhuma execução. Os cenários demonstram contratos sintéticos ou reconciliação de artefatos, sem estabelecer lucro futuro, autorização ou execução real.

## tests/test_v3_costs.py

CostModel algebraico: duas pernas fee/slippage em posição absoluta, funding long paga/short recebe e linear24h, net .0069, zero posição sem custo e edge pequeno líquido negativo. Parâmetros são declarados, sem calibração histórica.

## tests/test_v3_crowding_features.py

Crowding log OI/(volume*spot) em fixtures, alinhamento mais recente anterior à decisão, futuro excluído e tolerância; ausentes/zero neutro e tolerância negativa erro. Nome diz negativo mas body apenas volume zero, portanto negativo não demonstrado aqui.

## tests/test_v3_derivatives_dpl.py

Funding/OI fixtures transformados em SignalPoints enriched com hash64 e três métricas; SQLite persiste três pontos, scorecard DEGRADED e COLLECTION_ONLY. Timestamp de ingestão artificial; sem API/qualidade externa.

## tests/test_v3_economic_gate.py

Filtro opt-in defaultFalse preservado, mínimo20 da mesma constante calibrada; custos .003 convertem .002 em NO_TRADE e retorno grande apenas SHADOW_TRADE com capitalFalse. Sem calibration retorna failclosed; fundingNaN rejeita. Constantes não provam edge econômico.

## tests/test_v3_feature_prefix_regression.py

Prefix regression compara todos campos asdict com inputs efetivamente truncados em três cortes; perturba fortemente rates/OI/spot futuros e mantém prefixo. OI futuro não preenche missing; candle fechado ausente não é bridged e volume futuro não altera crowding. Evidência causal sintética, não integridade vintage de provider.

## tests/test_v3_hmm_no_lookahead.py

HMM stub fixo + série seeded compara cada posterior/estado em prefixos50/120/199 com completo; contraprova backward smoothing muda passado e dá sensibilidade. Modelo real treinado só primeiros150 também compara prefixo220, mas importorskip numpy/hmmlearn/sklearn. Sem qualidade preditiva ou treinamento em mercado real.

## tests/test_v3_macro_dxy_integration.py

230 dias CSV sintético sinusoidal/funding spikes, DXY published_at dia seguinte e calendário assumido disponível na origem. WFA integrado cobre folds/artifact com final UNVALIDATED e diagnostic GO/NO-GO, missing DXY argumento erro. Primeiro teste nome comportamento inalterado apenas exige n_folds>=1, não compara saídas com referência. Módulo skip sem hmmlearn/sklearn.

## tests/test_v3_macro_features.py

Macro dummy usa assume_calendar_known=True; DXY retorna % com defasagem declarada businessdays, exclui futuro e sexta até segunda, CSV inválido/vazio falha e coverage imputed. Lag0 admite close do mesmo dia, teste não prova hora de publicação. Segunda7Set feriado é aceita: calendário é de weekdays, sem prova de feriados/vintage real.

## tests/test_v3_paper_report.py

Paper report composto, closest price de candle fechado e tolerância, n_active/n_flat; PnL .1 usa preços fake100->110/exists patch e marca retrospective_records1. max_ddNone com um trade. Não observa fills, custos reais ou forward performance.

## tests/test_v3_paper_trader.py

Importorskip hmmlearn em helpers: latest_signal max timestamp, ref_price candle fechado/tolerância e futuro rejeitado. position_math apenas calcula expressão direction*strength*kelly no próprio teste, sem invocar produção; default Kelly=.5 prova constante, não homologação econômica.

## tests/test_v3_portfolio_equity.py

Equity slots sintéticos concorrentes perdas aditivas, ganhos realizados reinvestidos, slot ocioso sem rendimento e curva não negativa; Sortino/Calmar convenções (zero sem losses, Calmar cumulative/DD). Não exercita seleção de trades ou capital real.