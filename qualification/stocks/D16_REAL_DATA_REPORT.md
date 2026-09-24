# D-16 — métricas econômicas reais e evidência (missão stocks)

Gerado por `scripts/d16_apply.py` a partir de `D16_EVIDENCE_NUMBERS.json` (tirado dos logs brutos do run [35983568296](https://github.com/leonardosovienski/predictor-qualification/actions/runs/35983568296) por `scripts/d16_finalize.py`). Nenhum número foi digitado à mão (C20).

## Gates (critérios congelados)

| Gate | Estado |
|---|---|
| `E2E` | PASS |
| `WINDOWS_SMOKE` | PASS |
| `SOAK` | PASS |
| `STOCKS_NEGATIVE_CONTROLS` | PASS |

Estado terminal da missão: **QUALIFIED** (31 PASS, 0 FAIL, 0 NOT_RUN).

## Painel real

* `b3-cvm-real-2021-01-04_2026-09-23-cotahist4f2cf2aac107-k100`, cutoff `2026-09-24T03:00:00Z`, sha256 fixado `5a5e410b6106acec2683915ed583cb2e9bc509bee5433f47aa9f74811872c7dd`; construído em cada job a partir das fontes baixadas: linux-primary = fixado (173/173 fontes baixadas e conferidas), linux-controls = fixado (173/173 fontes baixadas e conferidas), windows-latest = fixado (173/173 fontes baixadas e conferidas).
* 169 ISIN no painel (de 572 ações/units no COTAHIST da janela), 236577 barras com revisões, 81 eventos acionários oficiais da B3 aplicados como revisões PIT; identidade: {'B3_CODE_CVM+CVM_FCA': 7, 'CVM_FCA': 162}; sem CNPJ: ['BRBRDTACNOR1', 'BRDTEXACNOR3', 'BRMRFGACNOR0', 'BRVVARACNOR1'].

## Sonda `stocks:QUAL-PIT-MOM-001` (momentum 12-1, quintil superior, top 60 PIT; não é hipótese científica)

Estado: **INCONCLUSIVE** (científico INCONCLUSIVE, econômico NO_EDGE); 49 períodos de carteira (2022-07-12 → 2026-08-25, rebalance a cada 21 pregões — ST-F007); universo de [60] ações e carteira de [12] em todo período. Validação temporal do Core (`predictor_core.measurement.replay`): PASS em 237084 registros, máx. available_at 2026-09-24T03:00:00Z ≤ as_of.

| Média por período | Bruto | Líquido |
|---|--:|--:|
| Estratégia | +65 bps | +54 bps |
| Baseline EW do universo | +27 bps | +26 bps |
| Excesso | +38 bps | +29 bps |
| IC95 do excesso (bootstrap estacionário, bloco 3, 2000 reamostras, seed 42) | [-33 bps, +104 bps] | [-43 bps, +95 bps] |

Custos (H1, por lado): emolumentos 3 bps + spread/slippage 15 bps; custo médio por período: estratégia +11 bps, baseline +1 bps. Drawdown máximo da estratégia (líquido): -1765 bps; acerto do excesso líquido: 0.4897959183673469. Campo `baseline_comparison.outcome` do resultado: BEATS (é só o sinal da média do excesso líquido; não é teste estatístico — o que vale é o IC95 acima).

Leitura: o IC95 do excesso bruto contém zero — sem evidência de edge (INCONCLUSIVE); nada disso concede capital (capital_permission = false) nem vale fora deste painel, commit e janela (C22).

## Contaminação por eventos não ajustados (ST-F008, diagnóstico)

Eventos corporativos NÃO ajustados considerados (salto > 30% com troca do número de distribuição + bonificação em outra classe): 127. Períodos com algum deles dentro de (início, fim]: carteira 1 de 49, universe/baseline 1 de 49.

* carteira: período 2025-12-18, BRCYREACNOR7 em 2025-12-31 (bonus_in_other_class BONIFICACAO)
* universo: período 2025-12-18, BRCYREACNOR7 em 2025-12-31 (bonus_in_other_class BONIFICACAO)
* universo: período 2025-12-18, BRRENTACNOR4 em 2025-12-30 (bonus_in_other_class BONIFICACAO)

Retorno só-preço (proventos em dinheiro não reinvestidos), como a rota (b) da H1: viés declarado.
