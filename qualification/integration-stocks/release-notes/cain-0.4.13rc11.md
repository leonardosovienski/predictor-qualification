Pré-release da release única da Etapa B, sucessora da v0.4.13rc10. Junta as mudanças que as três integrações precisaram depois da rc10, cada uma por decisão do dono na sessão dela. Cripto, stocks e Brasileirão são requalificados nesta versão (C14).

A v0.4.13rc10 continua publicada, sem mudança.

Construída do main `3b65ffe`, que já contém tudo o que está abaixo. A política de decisão (`policy.py`) é a mesma da rc10, com os mesmos bytes: regras R01–R17 na mesma ordem.

## Conteúdo em relação à rc10
**Molde de pedido do LLM:**
- **`proposal_overlays` (#72, integration-stocks):** chave opcional da configuração.
  - Dá a uma hipótese proponível parâmetros próprios no molde do LLM, como um controle negativo com semente própria.
  - Sem task própria, a hipótese pega a última task do seu tipo sem as chaves de overlay e aplica o seu overlay.
  - Nunca custos nem `placebo_seed`.
  - Ausente, vale `{}` e os bytes da configuração não mudam.
- **Pedido sem `parameters` (#72, relatado pela integration-brasileirao):** o molde, a sonda de elegibilidade e a proposta do LLM mantêm o pedido sem a chave. Na rc10, `explain --propose-for-domain brasileirao` falhava com `KeyError`.

**Métricas e findings (#73, integration-crypto):**
- **`result_metrics`:** chave opcional por domínio. As métricas numéricas finitas do resultado entram no fato da memória, na visão e no contexto do LLM.
- **`findings check`:** aceita o ID qualificado do próprio domínio.

**Configurações:**
- **stocks (#74):** 5 hipóteses de qualificação só para o LLM (`stocks:QUAL-LLM-CTRL-001..005`), com controle negativo `SHUFFLED_LABELS` e sementes 9001–9005. Vêm do ciclo 2 dos parâmetros congelados da integration-stocks (predictor-qualification `30c02c7`).
- **Brasileirão (#71):** 24 hipóteses de qualificação do soak, uma por ciclo (predictor-qualification `0920d90`).
- **cripto (#73):** `result_metrics` e o ponteiro do ciclo 3 dos congelados (predictor-qualification `73cab73`).
- As três configurações são regeneradas pelo `tools/build_domain_config.py` do main e saem iguais byte a byte ao empacotado.

**Dependências:** `predictor-research-transport` 0.1.0rc5, a mesma da rc10.

## Build e escopo
- Wheel construída 2× por `git archive` com `SOURCE_DATE_EPOCH=1758240000`, com o mesmo sha256 nas duas.
- É qualificação, não operação: sem modo operacional e sem capital.
