Pré-release da missão `integration-crypto` (Etapa B). Substitui a 0.1.0rc2, que continua publicada sem mudança.

- **Mesmo código do 0.1.0rc2; só a versão muda.** O rc2 saiu de `a19655f`, cujo CI ficou vermelho só pelos atestados de harness do cripto vencidos (IC-F004).
- **Commit desta release:** `61f3ac42160489ffbd872b05881a9b58b5bc0fcf`, branch `integration-crypto/harness-renewal-20260927`. É o commit que renova esses atestados, com CI de push verde.
- **Build:** wheel construída 2× por `git archive` com `SOURCE_DATE_EPOCH=1758240000`, com o mesmo sha256 nas duas.
