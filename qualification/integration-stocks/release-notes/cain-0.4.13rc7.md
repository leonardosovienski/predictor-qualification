Pré-release da missão `integration-stocks` (Etapa B, D-22/D-24). Substitui a 0.4.13rc6, que continua publicada sem mudança.

- **Framework sem mudança** (DecisionPolicy, composition root, TaskOutbox/ResultInbox V2, memória por domínio): o código
  da orquestração é o mesmo da 0.4.13rc6.
- **Acrescenta só a configuração do Stocks** (`src/cain/orchestration/data/stocks.json`), gerada por
  `tools/build_domain_config.py stocks` a partir de stocks-predictor `61fc017256ffea815ae96bbe02b847dccdb395cc` (SHA
  completo), do contrato do Stocks e dos parâmetros congelados da missão; o ramo crypto do construtor regenera o
  `crypto.json` byte a byte.
- Dependência `predictor-research-transport` 0.1.0rc3 → 0.1.0rc4 (só a entrada `stocks` na allowlist fixa de adapters).
- **Commit desta release:** `deccaaa0a0e2cb2b5f292614659eb4bf2e943e50`, branch `integration-stocks/stocks-config-20260927`
  (CI de push verde).
- **Build:** wheel construída 2× por `git archive` com `SOURCE_DATE_EPOCH=1758240000`, com o mesmo sha256 nas duas.
- Qualificação, não operação: nenhum modo operacional, nenhum capital, nenhum treinamento.
