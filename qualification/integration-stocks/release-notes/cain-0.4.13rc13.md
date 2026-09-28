Pré-release da Etapa B (missão integration-stocks, ciclo 4), publicada a partir do main `960fb25`. As rc11 e rc12 continuam publicadas sem mudança.

## O que entra em relação à rc12

**cain#77, correções da rodada de utilidade com o stocks:**
- O molde de pedido do LLM nunca é uma task recusada.
- `allowed_requests` vai no contexto do modelo.
- `refusal_mismatches` pega "recusada" falsa na justificativa.
- Linter de claims:
  - números de identificador entre crases são nomes;
  - `95%` ↔ `0.95`;
  - número colado a unidade é número.
- `findings-policy` v2: nome de família ou de trial no enunciado; candidatos por embedding só para revisão.

**cain#78:**
- `tools/build_domain_config.py` aceita `additional_frozen_families` (decisão D-26 do dono). Só acrescenta famílias, com blob e sha256 conferidos.
- `ingest-state --describe` é opcional.
- A calibração selada do embedding de paráfrase deu `KEEP_REVIEW_ONLY`. O dono decidiu manter só revisão, e a `findings-policy` continua na v2.
- `predictor-research-transport` passa a 0.1.0rc6: um consumidor por domínio por vez.

**cain#79, configuração do Stocks do ciclo 4** (`predictor-qualification` `37a0e28`, FROZEN_PARAMETERS `40d740cb…`):
- 17 famílias congeladas: as 15 da base mais `quality_net_margin` e `quality_roe_leverage_double_filter`;
- 8 hipóteses só para o LLM, com controles negativos de sementes 9001–9008.

## O que não muda
- `policy.py`: mesmos bytes (sha256 `aff2f5fc…`).
- `crypto.json` `28e978e7…` e `brasileirao.json` `f51ac735…`: byte a byte iguais. `stocks.json` passa a `c514a7b0…`.

## Build e escopo
- Wheel construída 2× por `git archive` com `SOURCE_DATE_EPOCH=1758240000`, com o mesmo sha256 nas duas.
- A wheel e o transporte mudaram, então a C14 vale para as três integrações.
- É qualificação, não operação: sem modo operacional e sem capital.
