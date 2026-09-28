predictor-research-transport 0.1.0rc4 — pré-release da missão integration-stocks (Etapa B, D-22/D-24).

- Única mudança de código: entrada `stocks` na allowlist fixa de adapters (`research_transport/adapters.py`), carregando
  `stocks_predictor.adapters.research_v2` da distribuição `stocks-predictor` pelo nome do módulo. Nada vem de task,
  arquivo ou linha de comando.
- Teste novo da allowlist; `packages/research-protocol` não muda (release congelada 2.0.0rc2).
- Commit: 1304b206239d1488fa6a8757364d7571d6c8cf81 (CI de push verde). Build reprodutível (git archive, SOURCE_DATE_EPOCH
  fixo, duas builds com os mesmos bytes).
- Qualificação, não operação: nenhum capital, nenhuma ordem, nenhum treinamento.
