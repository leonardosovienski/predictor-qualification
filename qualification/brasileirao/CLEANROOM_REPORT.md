# CLEANROOM_REPORT — missão brasileirao (C5)

## 1. cleanroom-baseline (diagnóstico do estado inicial)

Os commits do baseline da missão são os do `STACK_BASELINE_V1.1`: brasileirao `e14f339`,
core `5a08415`; o Ops do baseline do brasileirao ainda é a wheel 4.2.1 (`da4fa540…`) do `uv.lock`
(BR-F003). O cleanroom-baseline Linux × 3.13 de `e14f339` já existe, feito pelo SHARED-002
(run 35827048915, `qualification/shared/SHARED-002/CLEANROOM_REPORT.md`). Esta missão o
reaproveita como diagnóstico e não refaz a execução, porque o commit é o mesmo
(`STACK_BASELINE.json` → `head_vs_stack_baseline_v1_1`: brasileirao e core `equal: true`).

O que ele mostra para o brasileirao:

- A wheel publicada `0.2.0` (`2a862b4c…`, tag `4dbd353`) difere do commit com a mesma versão
  → **BR-F009**. Resolve com release nova em `publish-candidates`.
- Runtime instalado: `config.yaml` não vai na wheel e `ingest.load_config()`/avaliadores derivam a
  raiz de `__file__`; fora de checkout é preciso `BRASILEIRAO_CONFIG_PATH`/`BRASILEIRAO_PROJECT_ROOT`.
  O circuito novo não depende disso: dados, modelo e custos entram como objetos de referência com
  sha256 (contrato).
- Na árvore sem o pacote, 40 falhas + 2 erros do build do commit são testes que abrem arquivos de
  `brasileirao_scripts/` pelo caminho do repo ou a configuração do checkout (classe T do SHARED-002).
- Os 3 entrypoints respondem a `--help`; o plugin carrega.

Windows × 3.13 no baseline (checkout, diagnóstico): `RAW_LOGS/baseline/windows_suite_e14f339.log`
— ruff, format e pyright limpos; pytest 2207 passed, 1 skipped (BR-F010), 30 deselected
(integração com Redis de serviço, que roda só no CI).
