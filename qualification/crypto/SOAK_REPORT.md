# SOAK_REPORT — missão crypto (C10, gate `SOAK`)

**Gate: `NOT_RUN` — BLOCKED: D-16 pendente.** O perfil congelado
(`QUALIFICATION_PROFILE_CRYPTO_V1.json`) exige o runtime suportado no Linux primário. Pela
regra congelada em `FROZEN_PARAMETERS.json` (`d16_dependency_rule`), o soak só vale com
dados reais no Linux, e a D-16 ainda não foi decidida. A execução abaixo, com os vetores
sintéticos da suíte de conformidade, é **diagnóstico** e não fecha o gate.

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

Decidir a D-16 (dados reais no Linux/Actions ou numa VM). Com a decisão, o mesmo harness
(`scripts/soak.py`) roda com o dataset real no runtime suportado Linux, sem mudar o perfil.

## V1.1

Mesmo perfil, mesmo diagnóstico sintético no Linux (run 35925914768): `zero_tolerance_ok = true` (`EVIDENCE_NUMBERS_V1.1.json`). O gate segue **NOT_RUN — BLOCKED: D-16 pendente**.
