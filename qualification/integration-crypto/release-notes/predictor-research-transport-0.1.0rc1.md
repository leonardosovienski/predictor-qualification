Pré-release da missão `integration-crypto` (Etapa B, D-22): transporte local do envelope V2.

- Spool write-once por domínio e consumidor por domínio (`predictor-research-consumer`).
- Consome a release congelada `predictor-research-protocol` 2.0.0rc2 (`34a1e412…`).
- Allowlist de adapters: só `crypto → GarimpoInvestimentos.adapters.research_v2`.
- Commit `0cb672bdcd049ffc299bb3e3eda54b05f2e01a4e`, branch `integration-crypto/transport-20260927`.
- Wheel construída 2× por `git archive` com `SOURCE_DATE_EPOCH=1758240000` (mesmo sha256).

Qualificação, não operação: sem capital, sem conexão com exchange.
