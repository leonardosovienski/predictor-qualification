# SOAK_REPORT — missão crypto (C10, gate `SOAK`)

**Gate: `PASS` pela D-16** (dados reais, Linux primário, run 35978221282; seção abaixo). As
execuções anteriores com vetores sintéticos (V1.0 e V1.1) foram **diagnóstico** e não fecham o gate. O
harness delas só cobria 4 das 6 classes de falha do perfil (CR-F019).

## D-16: dados reais, Linux primário (fecha o gate)

- Run: [predictor-qualification 35978221282](https://github.com/leonardosovienski/predictor-qualification/actions/runs/35978221282), job `d16` (ubuntu-latest, Python 3.13), disparado a partir da branch `cripto/d16-20260924` (kit corrigido, PR #17). O `d16_finalize.py` aceitou: D-16 `APPROVED`, commit `341d270` e wheel `6e62f67f…` do `runtime_target.json`, `where=github_actions`.
- Runtime suportado: venv limpo, deps do lock com `--require-hashes`, wheel do Cripto conferida por sha256 (`core_identity.json`, `pip_freeze.txt`).
- Dados: Binance data.vision (BTCUSDT UM, klines 1d + funding): 45 arquivos, 45 conferidos contra o `.CHECKSUM` publicado. Dataset in-sample `0d04cf7c11e8…` (52 observações semanais). Conferência cruzada com a cópia do pendrive em `RAW_LOGS/d16-conferencia/data_run35978221282_x_pendrive.log`.
- Log bruto: `RAW_LOGS/d16/35978221282/soak_real.jsonl`. Números extraídos por `scripts/evidence_numbers.py --d16` para `EVIDENCE_NUMBERS_D16.json` (`d16.soak`).

| Classe de falha do perfil (mínimo 3) | Executado |
|---|---|
| crash do worker (`ops_worker_crash`) | 3 |
| timeout do Ops (`ops_worker_hang`, `--state` com timeout de 5 s) | 3 |
| host do Ops morto durante o job (`ops_worker_slow` + kill externo) | 3 |
| morte antes do commit da admission (`before_admission_commit`, inclui 1 restart) | 4 |
| morte durante a gravação do resultado (`during_result_write`) | 3 |
| corrupção (`research-result.json` alterado) | 3 (falha fechada em 3) |

- chamadas ao entrypoint: **77** (sem falha injetada: 57; restarts em rodízio também em `after_admission` 1, `during_materialization` 1, `before_ops` 1, `after_ops` 1);
- resultados armazenados: **43**, iguais aos 43 pedidos com resultado esperado; perdidos: **0**; inesperados: **0**;
- efeitos de domínio: **43**; jobs do Ops: **43**; máximo de `SUCCEEDED` por job: **1**;
- releitura por `show`: divergências **0**. Os resultados corrompidos de propósito continuam recusados (exit 5), sem reparo;
- `reconcile`: exit 5, **6** achados, todos das corrupções injetadas (estranhos: 0; corrupções não acusadas: 0);
- violações: **0**; `zero_tolerance_ok = true`.
- Casos A/B/C: A ×3 sobre os dados reais no soak; C = crash e timeout acima. B ×3 no mesmo runtime Linux, com o vetor sintético congelado (`e2e_cases`: 20 checagens, `all_ok=true`), como congelado no `D16_RUNBOOK.md`.

O run 35976569248 (a partir do `main`, kit antigo) está preservado em `RAW_LOGS/d16/35976569248/`. O soak dele não executou "host do Ops morto" nem "corrupção" (CR-F019), e ele não fecha gate.

## Execução diagnóstica (Linux primário, runtime suportado)

- Run: [predictor-qualification 35885023422](https://github.com/leonardosovienski/predictor-qualification/actions/runs/35885023422), job `linux-primary`
  (ubuntu-latest, Python 3.13). Venv limpo com as `final_wheels`: cripto-predictor 1.2.0rc1
  `1f76b8c4…`, core 3.2.1, ops 4.2.1, via lock com `--require-hashes`.
- Log bruto: `RAW_LOGS/cleanroom-final/run35885023422/crypto-runtime-linux-primary/soak.jsonl`.
  Números extraídos por `scripts/evidence_numbers.py` para `EVIDENCE_NUMBERS.json`.

| Item do perfil | Mínimo | Executado |
|---|---|---|
| ciclos normais | 20 | 20 pedidos distintos, cada um num processo novo |
| restarts | 5 | 5 mortes do processo em rodízio (`before_admission_commit`, `after_admission`, `during_materialization`, `before_ops`, `after_ops`) + reexecução |
| duplicatas | 5 | 5 reenvios com `client_ref` diferente, sempre `DUPLICATE` com o `client_ref` da submissão |
| por classe de falha | 3 | 3× worker crash, 3× timeout do Ops, 3× morte antes do commit da admission, 3× morte durante a gravação do resultado |
| casos A/B/C | 3 cada | 3× A, 3× B; C = crash e timeout acima |

Tolerância zero, conferida no fim sobre o estado:

- chamadas ao entrypoint: **65**;
- resultados armazenados: **40**, iguais aos 40 pedidos com resultado esperado;
- perdidos: **0**; inesperados: **0**;
- efeitos de domínio: **40**; jobs do Ops: **40**; máximo de `SUCCEEDED` por job: **1**;
- releitura por `show` byte-idêntica ao blob armazenado em todos os 40;
- `reconcile`: exit 0, sem achados;
- violações: **0**; `zero_tolerance_ok = true`.

## O que falta

Nada para o gate: a D-16 foi decidida e executada (seção D-16 acima).

## V1.1

Mesmo perfil, mesmo diagnóstico sintético no Linux (run 35925914768): `zero_tolerance_ok = true` (`EVIDENCE_NUMBERS_V1.1.json`). Na V1.1 o gate ficou **NOT_RUN — BLOCKED: D-16 pendente**; fechou depois pela D-16 (seção acima).
