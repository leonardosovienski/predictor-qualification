# integration-stocks — PROTECTED_ARTIFACT_REPORT

Gate `PROTECTED_ARTIFACTS_UNCHANGED` (C15.1). O conjunto veio do PROTECTED_SET.json de `truth-map` e foi reconferido por `scripts/protected_check.py` (`qualification/integration-stocks/RAW_LOGS/protected-r1/protected_check.json` (sha256 `c4de734f1ebe4dbd…`)).

| Domínio | Repo | Commit conferido | Itens | Alterados |
|---|---|---|--:|--:|
| crypto | cripto-predictor | `ee3d3d17de0b` | 1387 | 0 |
| stocks | stocks-predictor | `6f857b232eaa` | 89 | 0 |
| brasileirao | brasileirao-predictor | `25cdf4d9bb30` | 1884 | 0 |

Artefatos compartilhados conferidos por sha256: 27; alterados: 1. Total de itens: 3387; tudo igual: NÃO.

- `qualification/integration-crypto/QUALIFICATION_ATTESTATION.json`: esperado `112d18a35c7b3abf…`, atual `2d588e3df966bdf1…`. Reemissão: os bytes esperados estão em `qualification/integration-crypto/QUALIFICATION_ATTESTATION_superseded_112d18a35c7b.json` (sha256 `112d18a35c7b3abf…`) e o `supersedes_sha256` da attestation atual é `112d18a35c7b3abf…`. Conflito entre a C14 congelada (`FROZEN_PARAMETERS.c14_integration_crypto`) e a C15.1 (IS-F006): decidido pelo dono em 2026-09-28 ("(a) Aceitar a reemissão C14": Decido que a reemissão prevista em c14_integration_crypto, com os bytes protegidos preservados e encadeados, satisfaz a C15.1 para esse item. A attestation reemitida sai com 30/30 gates PASS.). O gate aceita o item só com a supersessão conferida.
