# PROTECTED_ARTIFACT_REPORT — missão crypto (C15.1, gate `PROTECTED_ARTIFACTS_UNCHANGED`)

- Conjunto: `PROTECTED_SET.json` (1382 arquivos, hash de blob git no commit de truth-map
  `5fd4e1b`), com os globs do prompt §5 e tudo o que `CR_RESEARCH_FREEZE.md`,
  `CR_FREEZE_INDEX.md`, `HYPOTHESES.md` e o `ci.yml` declaram congelado.
- Comparação no `final_commit` `2bc63eb` (`RAW_LOGS/final/protected_set_check_2bc63eb.json`,
  `git ls-tree` do commit): **1382/1382 iguais, 0 alterados ou ausentes**.
- Durante a missão também foi conferido depois do primeiro commit de código (`33fed6b`):
  0 alterados.
- `charters/scientific_state.json` (dentro do conjunto): H1–H3, H5 `CLOSED_NO_GO`; H4, H6, H9
  `CLOSED_INSUFFICIENT_SAMPLE`; H7, H8 `REGISTERED_NOT_ACTIVATED`; família congelada
  `funding_oi_hmm_v3`; `capital_authorized: false`. Nada foi reaberto. A admission recusa
  `crypto:H1..H9` (`HYPOTHESIS_CLOSED` / `HYPOTHESIS_NOT_ACTIVE`), e o worker recusa protocolo
  de família congelada (`FROZEN_FAMILY`). Os dois casos são testados na conformidade.
- O `GarimpoInvestimentos/v3/costs.py` (protegido) não foi alterado. A correção CR-F004 está
  no handler, que agora usa o `CostModel` congelado sem mudá-lo.

## V1.1

No `final_commit` `341d270`: 1382/1382 blobs iguais ao truth-map (`RAW_LOGS/v1.1/protected_set_check_341d270.json`).

## V1.2 (reabertura D-27: cripto 1.2.0rc4 / 21f8b182)

- Conjunto V1.0 (`PROTECTED_SET.json`, 1382 blobs de `5fd4e1b`) conferido em `21f8b182`: **1382/1382 iguais,
  0 alterados ou ausentes** (`qualification/crypto/RAW_LOGS/v1.2/protected/protected_set_check_21f8b182.json`). Nada do que estava protegido em `341d270` mudou nos PRs #128–#134 nem nas correções de 2026-09-29.
- Conjunto refeito pelo `truth_map.py` em `21f8b182` (`PROTECTED_SET_V1.2.json`): **1445 itens** (só cresce: +63 arquivos novos em `docs/evidence/`,
  cobertos pelos globs do prompt §5); 1445/1445 iguais no alvo (`qualification/crypto/RAW_LOGS/v1.2/protected/protected_set_v1_2_check_21f8b182.json`).
- `charters/scientific_state.json` continua com o mesmo blob: H1–H3, H5 `CLOSED_NO_GO`; H4, H6, H9 `CLOSED_INSUFFICIENT_SAMPLE`; H7, H8
  `REGISTERED_NOT_ACTIVATED`; família congelada `funding_oi_hmm_v3`; `capital_authorized: false`. Nada foi reaberto.

`PROTECTED_ARTIFACTS_UNCHANGED` V1.2: **PASS**.
