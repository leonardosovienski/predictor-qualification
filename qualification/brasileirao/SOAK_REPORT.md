# SOAK_REPORT — missão brasileirao (gate `SOAK`, C10)

**Estado do gate: `PASS` (requalificação rc3, 2026-09-24).** Com a emenda da D-9 no `main` (D-19: o PC 2
do dono vale como Linux primário `owner_linux` só para dado privado; núcleo v2.2, D-20), o soak rodou no PC 2
com o dado real, pela wheel 0.3.0rc3 (`25cdf4d`, `403e6a02…`), com o perfil `QUALIFICATION_PROFILE_BR_V1`
inteiro e tolerância zero sem exceção (seção "Requalificação rc3" abaixo). Histórico: `NOT_RUN — BLOCKED:
D-16 pendente` até a D-16; depois `NOT_RUN — evidência bruta pronta no PC 2; aguarda emenda da D-9 e do
schema` (rc2, PR #19), com bruto `PASS`.

## Requalificação rc3 — soak com o dado real no Linux primário `owner_linux` (C14 do BR-F018)

* Onde: PC 2 (Ubuntu 24.04.5 LTS no WSL2, provisionado por `provision_linux_vm.sh`, recibo
  `RAW_LOGS/c14-rc3-20260924/host/PROVISION_RECEIPT.json`), Python 3.13.15 gerenciado. Runtime suportado:
  dependências de runtime do `uv.lock` do `25cdf4d` com `--require-hashes` + wheel publicada 0.3.0rc3 (sha256
  conferido). Driver `scripts/pc2_d16_runtime.sh` → `scripts/soak.py --real-dataset` (o mesmo da rc2).
* Dado: cópia `~/predictors/runtime/brasileirao2/data/matches_source_copy.sqlite3`, sha256 `31f30a4d…` na fonte
  e na cópia, antes e depois (`RAW_LOGS/c14-rc3-20260924/d16-pc2-rc3/dataset_sha256.log`); nada do dado na
  evidência (`scan_final/no_data_rows_check.json`).
* Números (`EVIDENCE_NUMBERS.json` → `soak.pc2_owner_linux_real_rc3`, de `d16-pc2-rc3/soak.jsonl`):

| Medida | Valor |
|---|---|
| chamadas de processo | 71 (54 sem falha; 4 `before_admission_commit`, 4 `during_result_write`, 3 `ops_worker_crash`, 3 `ops_worker_hang`, 1 `during_materialization`, 1 `after_ops`, 1 `after_result_store`) |
| pedidos com resultado / guardados / efeitos de domínio | 49 / 49 / 49 |
| perdidos / inesperados / releitura ≠ blob autoritativo | 0 / 0 / 0 |
| SUCCEEDED do Ops por job (máximo) / jobs | 1 / 49 |
| `reconcile` | exit 0, sem achados |
| violações (duplicata, restart, falha, mesmo kickoff, permutação, canário, autoridade/IDs) | 0 |
| veredito de tolerância zero | `true` |

* Soak sintético da rc3 no Actions (run 36010604163, linux-primary): o mesmo resultado
  (`soak.actions_linux_synthetic_rc3`), idêntico ao da Etapa A.
* Protegidos: 1877/1877 iguais no `25cdf4d` (`c14/protected_check_25cdf4d.json`).

## Diagnóstico com vetores sintéticos (Linux primário, runtime suportado)

Perfil congelado antes: `QUALIFICATION_PROFILE_BR_V1.json` (20 ciclos normais, 5 restarts, 5
duplicatas, 3 por classe de falha relevante — crash do worker, timeout do Ops, morte antes do commit
da admission, morte durante a gravação do resultado —, 5 ciclos de mesmo kickoff, 5 com dataset fora
de ordem, 5 com canário). Driver `scripts/soak.py`, cada chamada um processo novo do
`brasileirao-research` instalado da wheel v0.3.0rc2.

Números de `EVIDENCE_NUMBERS.json` → `soak.linux_synthetic_rc2` (tirados de
`RAW_LOGS/cleanroom-final/run35963501898/brasileirao-runtime-linux-primary/soak.jsonl`):

| Medida | Valor |
|---|---|
| chamadas de processo | 71 (54 sem falha injetada; 4 `before_admission_commit`, 4 `during_result_write`, 3 `ops_worker_crash`, 3 `ops_worker_hang`, e os pontos de restart) |
| pedidos com resultado | 49; resultados guardados 49 |
| perdidos / inesperados | 0 / 0 |
| efeitos de domínio | 49 (= resultados) |
| SUCCEEDED do Ops por job (máximo) | 1 |
| releitura ≠ blob autoritativo | 0 |
| `reconcile` | exit 0, sem achados |
| violações (duplicata, restart, falha, mesmo kickoff, permutação, canário, autoridade/IDs) | 0 |
| veredito de tolerância zero | `true` |

Diagnóstico adicional com **dado real** no Windows local (não é o ambiente do gate): 20 pedidos
reais + E2E real 25/25 + corroboração temporal (`TEMPORAL_INTEGRITY_REPORT.md` §4), sem violação.

## D-16 no PC 2 — soak com o dado real (2026-09-24, evidência bruta)

* Onde: PC 2, Ubuntu 24.04.5 LTS no WSL2 (kernel 6.18.33.2), Python 3.13.15 gerenciado por uv 0.12.18.
  Runtime suportado em `~/predictors/runtime/brasileirao/…/rt`: dependências de runtime do `uv.lock` do
  `04b42c9` com `--require-hashes` (Core 3.2.1 e Ops 4.2.2rc1 pela URL da release) + wheel publicada
  0.3.0rc2 (`70344f22…`, sha256 conferido). Driver `scripts/pc2_d16_runtime.sh` → `scripts/soak.py
  --real-dataset`.
* Dado: `~/predictors/data/d16/brasileirao/matches_source_copy.sqlite3` (só leitura), copiado byte a
  byte para `~/predictors/runtime/brasileirao/data/`; sha256 `31f30a4d…` na fonte e na cópia, antes e
  depois (`RAW_LOGS/d16-pc2-20260924/d16/dataset_sha256.log`). Nada do dado entrou na evidência
  (`scan_final/no_data_rows_check.json`: 0 ocorrências de time, jogador ou event_id em 81 arquivos).
* Modo dado real do `soak.py` (mudança de kit desta noite): **o mesmo perfil, as mesmas classes de
  falha, as mesmas seeds (11, 23, 37, 41, 53), o mesmo canário `FUTURE_CANARY_BR_001`, os mesmos
  comparadores, a mesma política e os mesmos objetos JSON congelados de `tests/conformance/fixtures.py`**;
  muda só o dataset: a base é a cópia real (snapshot com o mesmo sha256 `31f30a4d…`), o canário são 2
  jogos depois do cutoff (2023-10-20 e +7 d, 17–0 e 0–17, cache `current_elo` envenenado) numa cópia
  derivada, as permutações reconstroem uma cópia com as mesmas linhas em outra ordem física (mesmos
  índices e gatilhos), e os 5 pares de mesmo kickoff são jogos reais de 2023 (jun–set) escolhidos com
  os filtros do worker. O caminho sintético não mudou (o push desta branch dispara o
  `brasileirao-runtime.yml`, que roda o soak sintético de novo no Actions).
* Números (`RAW_LOGS/d16-pc2-20260924/d16/evidence_numbers_pc2.json` → `soak.pc2_real`, tirados de
  `d16/soak.jsonl` por `scripts/evidence_numbers.py`):

| Medida | Valor |
|---|---|
| chamadas de processo | 71 (54 sem falha; 4 `before_admission_commit`, 4 `during_result_write`, 3 `ops_worker_crash`, 3 `ops_worker_hang`, 1 `during_materialization`, 1 `after_ops`, 1 `after_result_store`) |
| pedidos com resultado / guardados / efeitos de domínio | 49 / 49 / 49 |
| perdidos / inesperados / releitura ≠ blob autoritativo | 0 / 0 / 0 |
| SUCCEEDED do Ops por job (máximo) / jobs | 1 / 49 |
| `reconcile` | exit 0, sem achados |
| violações (duplicata, restart, falha, mesmo kickoff, permutação, canário, autoridade/IDs) | 0 |
| veredito de tolerância zero | `true` |

* **Veredito bruto pelos critérios congelados: `PASS`** (perfil inteiro, tolerância zero sem exceção,
  no runtime suportado, com o dado real). O gate continua `NOT_RUN` porque o PC 2 não é, hoje, um host
  Linux primário admitido pela D-9 nem pelo `where` do schema (C14): emenda proposta em
  `D16_PC2_REPORT.md`.
* Achado da noite, independente do soak: **BR-F018 (P1)** — os números de um resultado (não os estados)
  dependem do SO; ver `D16_PC2_REPORT.md` e `FINDINGS.json`.
