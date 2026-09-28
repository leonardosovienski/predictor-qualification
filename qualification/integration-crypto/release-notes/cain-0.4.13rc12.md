Pré-release de correção da v0.4.13rc11 na Etapa B, publicada a partir do main `302a5c8`. A rc11 continua publicada sem mudança.

## O que corrige
**Regressão da rc11, trazida pelo #73.** Com `result_metrics`, o contexto do modo de proposta passava do orçamento de entrada do provider, e nenhuma proposta chegava ao modelo. No soak da integration-crypto, prompt + instrução somaram 8226 bytes contra um orçamento de 7680 (num_ctx 8192 − num_predict 256 − 256).

**A correção (#75):** o CAIN monta o contexto dentro de `effective_input_byte_budget`.
- Os resultados mais antigos saem primeiro.
- O `hypothesis_summary` mantém todas as contagens.
- `results_omitted` diz quantos resultados ficaram de fora. Isso inclui os que passam do teto de 50, e aí a chave aparece mesmo sem corte por orçamento.
- Dentro do orçamento, o prompt não muda.

## O que não muda em relação à rc11
- `policy.py`: mesmos bytes (sha256 `aff2f5fc…`).
- Configurações, byte a byte iguais: `crypto.json` `28e978e7…`, `stocks.json` `c44b4eb2…`, `brasileirao.json` `f51ac735…`.
- Dependência: `predictor-research-transport` 0.1.0rc5.

## Build e escopo
- Wheel construída 2× por `git archive` com `SOURCE_DATE_EPOCH=1758240000`, com o mesmo sha256 nas duas.
- É qualificação, não operação: sem modo operacional e sem capital.
