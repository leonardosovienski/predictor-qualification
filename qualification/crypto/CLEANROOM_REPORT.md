# CLEANROOM_REPORT — missão crypto (C5)

## 1. cleanroom-baseline (diagnóstico do estado inicial)

Os commits do baseline da missão são os mesmos do `STACK_BASELINE_V1`: cripto `5fd4e1b`,
core `5a08415`, ops `7bd99eb`. O cleanroom-baseline Linux × 3.13 desses commits já existe,
feito pelo SHARED-002 (runs 35826713033 e 35827048915, relatório
`qualification/shared/SHARED-002/CLEANROOM_REPORT.md`). Esta missão o reaproveita como
diagnóstico. Não refaço a execução porque os commits são idênticos
(`STACK_BASELINE.json` → `head_vs_stack_baseline_v1`: os três `equal: true`).

O que o cleanroom-baseline mostra para o crypto (achados abertos na missão):

- `GarimpoInvestimentos/output/` fica fora da wheel porque o `.gitignore` tem `output/` sem
  âncora. O caminho padrão de análise quebra no runtime instalado → **CR-F005**.
- Não existe wheel publicada da versão do commit (`1.1.1rc4`). A `1.1.0` publicada difere.
  Resolvido pela fase `publish-candidates`.
- `crypto-research-export` (pacote separado em `packages/research-export`) exige
  `predictor-research-snapshot`, que está fora do lock. Não faz parte da wheel
  `cripto-predictor` nem do circuito da Etapa A → **CR-F011** (P2, Etapa B).
- Testes que leem o checkout (`trials.json`, `dist/`, git) falham na árvore sem pacote. São
  defeitos só de teste (classe T do SHARED-002).
- Core 3.2.1 e Ops 4.2.1: wheel publicada = commit. Ops com SHARED-003/004 (vereditos nesta
  missão).

Windows × 3.13 no baseline: suíte do checkout com 1618 passed
(`RAW_LOGS/baseline/windows_pytest_5fd4e1b_run2.log`, diagnóstico).

## 2. cleanroom-final

Preenchido na fase `cleanroom-final`: instalação limpa só com as wheels publicadas dos
`final_commits`, fora do checkout.
