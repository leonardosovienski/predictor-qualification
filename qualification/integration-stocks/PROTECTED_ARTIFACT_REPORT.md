# integration-stocks — PROTECTED_ARTIFACT_REPORT

Gate `PROTECTED_ARTIFACTS_UNCHANGED` (C15.1). O conjunto veio do PROTECTED_SET.json de `truth-map` e foi reconferido por `scripts/protected_check.py` (`qualification/integration-stocks/RAW_LOGS/protected-c2/protected_check.json` (sha256 `dd5560e005ad6691…`)).

| Domínio | Repo | Commit conferido | Itens | Alterados |
|---|---|---|--:|--:|
| crypto | cripto-predictor | `ee3d3d17de0b` | 1387 | 0 |
| stocks | stocks-predictor | `6f857b232eaa` | 89 | 0 |
| brasileirao | brasileirao-predictor | `25cdf4d9bb30` | 1884 | 0 |

Artefatos compartilhados conferidos por sha256: 27; alterados: 4. Total de itens: 3387; tudo igual (a letra da C15.1): NÃO; tudo igual ou encadeado: sim.

Conflito entre a C14 (novo ciclo) e a C15.1 (IS-F008): decidido pelo dono em 2026-09-28 ("(a) Encadeada (Recomendado)": O gate aceita cada um dos 4 itens só com a cadeia conferida byte a byte até o sha256 protegido (arquivo preservado + ponteiro, salto a salto). Todo outro item alterado continua FAIL. É o mesmo critério do IS-F006 e do IC-F011 do cripto.)

- `qualification/integration-crypto/QUALIFICATION_ATTESTATION.json`: esperado `112d18a35c7b3abf…`, atual `d1c76b4eedb96710…`. Cadeia: `QUALIFICATION_ATTESTATION_superseded_2d588e3df966.json` (ponteiro `2d588e3df966bdf1…`, arquivo `2d588e3df966bdf1…`) → `QUALIFICATION_ATTESTATION_superseded_112d18a35c7b.json` (ponteiro `112d18a35c7b3abf…`, arquivo `112d18a35c7b3abf…`); chega ao sha256 protegido com cada salto conferido: **sim**.

- `qualification/integration-crypto/FROZEN_PARAMETERS.json`: esperado `c428e4b769e3a6f9…`, atual `2ee84f572c1f678b…`. Cadeia: `FROZEN_PARAMETERS_cycle1_c428e4b769e3.json` (ponteiro `c428e4b769e3a6f9…`, arquivo `c428e4b769e3a6f9…`); chega ao sha256 protegido com cada salto conferido: **sim**.

- `qualification/integration-stocks/FROZEN_PARAMETERS.json`: esperado `771b8a23e9b9bde7…`, atual `11ad4cb7f255da06…`. Cadeia: `FROZEN_PARAMETERS_cycle1_771b8a23e9b9.json` (ponteiro `771b8a23e9b9bde7…`, arquivo `771b8a23e9b9bde7…`); chega ao sha256 protegido com cada salto conferido: **sim**.

- `qualification/integration-stocks/FROZEN_VECTORS.json`: esperado `3ad4d197cb79bb2f…`, atual `efba834f780f00be…`. Cadeia: `FROZEN_VECTORS_cycle1_3ad4d197cb79.json` (ponteiro `3ad4d197cb79bb2f…`, arquivo `3ad4d197cb79bb2f…`); chega ao sha256 protegido com cada salto conferido: **sim**.
