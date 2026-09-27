Pré-release da missão `integration-crypto` (Etapa B, D-22). Commit `6b460afd5f19e8a1739a09a9eaabab1dbe98084f`
(branch `integration-crypto/framework-20260927`, a partir do main `f343701`).

- `cain.orchestration`: orquestração de pesquisa por domínio sobre o envelope V2 (propose com DecisionPolicy
  determinística e receipt canônico, decision-receipt, dispatch/retry pelo spool do transporte, ingest com
  ResultInbox V2 fail closed, memória por cubo de domínio, episódios), configuração do cripto gerada de
  `341d270e4d709150c581c3cd93f4518d483009eb` (SHA completo).
- `cain loop` fora do console script (laboratório: `python -m cain.loop`); leitura de registro do cripto só com SHA completo.
- Propostas por modelo local (`cain research explain --propose-for-domain`), auditadas, fora do caminho do receipt.
- Dependências: predictor-research-protocol 2.0.0rc2 (release congelada), predictor-research-transport 0.1.0rc2.
- Wheel construída 2× por `git archive` com `SOURCE_DATE_EPOCH=1758240000` (mesmo sha256).
Qualificação, não operação: sem modo operacional, sem capital.
