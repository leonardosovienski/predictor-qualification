# QUALIFICATION_CHANGELOG — missão stocks (Etapa A)

O que a missão mudou, onde, por quê, com commit e PR. `core-predictor` e `predictor-ops`
**não** são alterados (congelados na Etapa A; Ops consumido pela release v4.2.2rc1, D-17).

## predictor-qualification (branch `stocks/qualification`)

| O quê | Por quê |
|---|---|
| `.github/workflows/stocks-suite.yml` + `qualification/stocks/scripts/suite.sh` | suíte do stocks-predictor antes/depois de cada mudança no Linux primário e no windows-latest (D-1/D-9), instalando só pelo lock |
| `qualification/stocks/scripts/collect_mission_baseline.py` | fase `baseline` (C3), reuso do coletor comum |
| `qualification/stocks/scripts/attest.py` | parciais/attestation a partir de `GATES.json` (C7/C8) |

## stocks-predictor

(preenchido a cada mudança)
