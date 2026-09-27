Pré-release da missão `integration-crypto` (Etapa B). Substitui a 0.1.0rc1 (que continua publicada, sem mudança).

- `predictor-research-consumer`: stdout só com as linhas JSON do relatório; logs que o domínio escreve no stdout
  (handlers em processo ou processos filhos) vão para o stderr enquanto o domínio trabalha.
- Commit `a19655f45f84842fea9f331429aa30d2c9ee4394`, branch `integration-crypto/transport-20260927`.
- Wheel construída 2× por `git archive` com `SOURCE_DATE_EPOCH=1758240000` (mesmo sha256).
