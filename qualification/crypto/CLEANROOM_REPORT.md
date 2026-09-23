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

## 2. cleanroom-final (gate `CLEANROOM_FINAL`)

Instalação limpa só com wheels publicadas, fora do checkout:

- cripto-predictor 1.2.0rc1: [release v1.2.0rc1](https://github.com/leonardosovienski/cripto-predictor/releases/tag/v1.2.0rc1), sha256 `1f76b8c4dbcb2ca145c053a7dc84d98d30c49859d95c1e1a78ad4d5916b3df49`, construída de `2bc63eb`. Build reprodutível: 2 builds idênticos (`RAW_LOGS/publish-candidates/build_rc_2bc63eb.log`).
- predictor-core 3.2.1 (`10ef42f3…`) e predictor-ops 4.2.1 (`da4fa540…`): releases publicadas, congeladas.
- Método: venv novo; dependências por `uv export --locked` + `pip install --require-hashes`; a wheel do Cripto baixada da URL da release, com o sha256 conferido antes de instalar; `pip check`. Testes numa árvore = `final_commit` **sem** `GarimpoInvestimentos/`, então o pacote só pode vir do site-packages. `core_identity.json` e `runtime_trace.log` confirmam a origem de cada módulo.

| Ambiente | Conformidade (48) | Suíte completa pela wheel | E2E (entrypoint, restart, releitura) | Evidência |
|---|---|---|---|---|
| Linux primário (ubuntu-latest, 3.13) | 48/48 | 1647 passed, 17 T | 20/20 checagens | `RAW_LOGS/cleanroom-final/run35885023422/crypto-runtime-linux-primary/` |
| windows-latest (3.13) | 48/48 | 1647 passed, 17 T | 20/20 checagens | `RAW_LOGS/cleanroom-final/run35885023422/crypto-runtime-windows-latest/` |
| Windows local (D-3) | 48/48 | — | 10/10 checagens, dado real | `RAW_LOGS/windows-smoke/local/` |

As 17 falhas "T" são as mesmas nos dois ambientes (CR-F016, P2): testes que leem o checkout
(`GarimpoInvestimentos/trials.json`, `main.py`, `analyzers/*` pelo caminho do repo; `dist/`
construído; higiene do `.gitignore`). No CI do checkout em `2bc63eb` todos passam. Nenhuma
exercita o código instalado.

Execuções anteriores preservadas como erro de método:
- `run35883218077`: árvore de testes sem `scripts/`, e a raiz temporária do windows-latest passou do limite de 120 caracteres do contrato. A conformidade (48/48), o E2E e o soak no Linux já estavam OK nesse run.

## 3. cleanroom-final V1.1 (cripto 1.2.0rc2 + Ops 4.2.2rc1)

- Wheels: cripto-predictor 1.2.0rc2 `6e62f67f…` (build reprodutível de `341d270`, `RAW_LOGS/v1.1/build_rc2_341d270.log`), predictor-ops 4.2.2rc1 `0be70bfb…` (release oficial do Ops), predictor-core 3.2.1.
- Linux primário e windows-latest (run 35925914768): conformidade 48/48; suíte completa 1647 passed + as **mesmas** 17 T de antes (CR-F016); E2E 20/20 checagens.
- Windows local (`RAW_LOGS/v1.1/windows-local/`): conformidade 48/48; E2E real 10/10.
