# SOAK_REPORT — missão stocks (C10; gate SOAK)

**Estado do gate: NOT_RUN — BLOCKED: D-16 pendente.** A regra congelada (`FROZEN_PARAMETERS.d16_dependency_rule`)
exige dado real no Linux primário para o SOAK; a execução abaixo usa a fixture sintética congelada e é
**diagnóstico**.

Perfil: `QUALIFICATION_PROFILE_STOCKS_V1.json` (números congelados em `FROZEN_PARAMETERS.soak_profile` antes da
execução). Runtime suportado (wheels publicadas), GitHub Actions ubuntu-latest, cada chamada ao `stocks-research` num
processo novo. Log bruto: `qualification/stocks/RAW_LOGS/cleanroom-final/run35954279991/stocks-runtime-linux-primary/soak.jsonl`.

| medida | valor |
|---|---|
| chamadas ao entrypoint | 73 |
| falhas injetadas | 17 |
| pedidos com resultado esperado | 48 |
| resultados armazenados | 48 |
| efeitos de domínio | 48 |
| jobs do Ops / máximo de SUCCEEDED por job | 48 / 1 |
| resultados perdidos / inesperados | 0 / 0 |
| releitura divergente | 0 |
| violações (duplicata, autoridade, IDs) | 0 |
| violações PIT | 0 |
| trials elegíveis de External Intelligence | 0 (nenhuma família READY) |
| tolerância zero | True |
