# Cobertura por projeto (as duas épocas)

Cinco categorias, por projeto: **analisado em profundidade** (revisão semântica integral registrada, com nota por arquivo), **catalogado** (identificado por caminho e hash, lido mecanicamente ou não lido), **pendente** (no escopo, não feito), **bloqueado** (não pode ser feito neste ambiente) e **não aplicável**. As contagens da época original vêm de `../evidencias/<projeto>/coverage.json`; as da época `main` vêm de `../evidencias/epoca-main-20260930/delta/<projeto>-delta-inventory.json` (campo `semantic_review`). Números consolidados em `../evidencias/epoca-main-20260930/coverage-by-project.json`. Leitura nunca é execução.

| Projeto | Época original: entradas | em profundidade | catalogadas | Época main: arquivos no delta | revisados | só diff lido | pendentes |
|---|---|---|---|---|---|---|---|
| cain | 174 | 174 | 0 | 357 | 1 | 0 | 356 |
| cripto-predictor | 1756 | 1756 | 0 | 132 | 5 | 0 | 127 |
| brasileirao-predictor | 1049 | 519 | 530 | 113 | 4 | 0 | 109 |
| stocks-predictor | 235 | 231 | 4 | 127 | 5 | 0 | 122 |
| core-predictor | 91 | 91 | 0 | 10 | 3 | 7 | 0 |
| predictor-ops | 41 | 41 | 0 | 14 | 6 | 8 | 0 |
| ecosystem-predictor | 70 | 70 | 0 | 61 | 15 | 0 | 46 |
| predictor-qualification | 41 | 41 | 0 | 5763 | 2 | 0 | 5761 |

As entradas da época original contam o que a cobertura registra (no Crypto e no Brasileirão, `files` reconciliado por caminho e hash: `semantic_integral_certified` ou `semantic_review` aprofundado = em profundidade; `catalogado-historico-terceiro` e `leitura-estrutural-sem-revisao-semantica` = catalogado; nos demais, a lista de arquivos próprios lidos). O arquivo histórico Crypto (773 objetos) está em `crypto-archive-coverage-merged.json`, fora da tabela.

## cain

- **Analisado em profundidade (época original, `24f784c5`):** código próprio ativo, scripts, CI, testes e UI conforme `coverage.json` (174 entradas) e suplementos `SUPLEMENTO_CAIN_*`.
- **Catalogado:** árvore suja/não rastreada da raiz Windows (baseline-status); docs históricos.
- **Pendente (época main):** 356 dos 357 arquivos do delta (+61.453 linhas), inclusive `DecisionPolicy`, `policy.py`, configs de domínio, `research/`, `loop/`, `orchestration/`, `claims/`, 87 testes. Lista exata no delta-inventory.
- **Bloqueado:** `cain doctor` com provedor real (sem Ollama); soak/E2E com LLM.
- **Não aplicável:** treinamento, capital.

## cripto-predictor

- **Em profundidade (original, `88158f25`):** 440 arquivos ativos (módulos, scripts 75, testes 169+1, CI/config) e 773 objetos do arquivo histórico, sem execução.
- **Catalogado:** cópias alternativas em `C:\CRIPTO` (uma com HEAD inválido).
- **Pendente (main):** 127 arquivos do delta: `research/` (10 módulos novos), `research_admission/execution/worker/recovery/results` modificados, `run_ledger.py`, `v3/` (backtest_v3 2.101 linhas, coletores, cost_spec), 21 testes novos/modificados, 4 testes V1 movidos para `legacy/`. Revisados: adapter V2, contrato, runner, ESTADO.
- **Bloqueado:** `check_release_identity.py --strict` (TLS via proxy); suíte completa (1.748 testes citados no ESTADO, ET-HIST); harness econômicos; Windows (D-3).
- **Não aplicável:** ordens/capital (`capital_authorized: false` protegido).

## brasileirao-predictor

- **Em profundidade (original, `f8780690`):** Python próprio, 124 scripts, 210 testes, .NET 42 arquivos (lido, não executado); 26 residuais lidos no clone do remoto com hash idêntico.
- **Catalogado:** 16 arquivos (workflows, contratos JSON, pyproject, lock, schemas) cujos bytes locais diferem do remoto (`retomada-residual-pendentes.json`).
- **Pendente (main):** 109 arquivos do delta, com destaque para `model.py`, `evaluator.py`, `serving_evaluator.py`, `ingest.py`, `elo_baseline.py` modificados (caminho de previsão), `research_runtime/` (10 módulos), scripts prospectivos v2, 28 testes. Revisados: adapter V2, contrato, ESTADO.
- **Bloqueado:** reler os 16 residuais no original Windows; bancos operacionais; PC 2 (`owner_linux`, D-19) para runtime e Windows da integração.
- **Não aplicável:** apostas (`bet_log` manual/declarativo), capital.

## stocks-predictor

- **Em profundidade (original, `5cf27f44`):** código próprio, ferramentas e verificadores (235 entradas; `stocks_verifiers.py` passou no HEAD local).
- **Catalogado:** `research/` (301 `.py` históricos), `vendor/` (43, terceiros), protótipos OSS em docs (10).
- **Pendente (main):** 122 arquivos do delta: `v2/` (24 módulos), `research_*` (11), `tools/chronos_forecast.py`, `tools/export_scientific_state.py`, 21 testes, 40 dados/texto. Revisados: adapter V2, contrato, ESTADO, lacre R8 (quebrado por 3 arquivos).
- **Bloqueado:** `windows-latest` (D-1) e Python do Stocks só no GitHub Actions; instalação local proibida pelas regras do dono.
- **Não aplicável:** capital (`capital_enabled: false`, `profit_certified: false` no lacre).

## core-predictor

- **Em profundidade (original, `9bf43efe`):** 91 arquivos próprios (leitura integral e parsing estrutural); smoke de folha (`core_leaf_smoke.py`).
- **Época main:** 10 arquivos no delta, todos lidos; `src/` intacto. `check_installed_wheel.py` passou contra a wheel 3.2.1 no venv do cripto.
- **Pendente:** nenhum arquivo; suíte de 278 testes citada no ESTADO é ET-HIST.
- **Bloqueado:** cleanroom (venv editable); `consumer-compatibility.yml` (Actions).
- **Não aplicável:** —

## predictor-ops

- **Em profundidade (original, `b19e6952`):** 41 arquivos próprios.
- **Época main:** 14 arquivos, todos lidos; único código novo é a correção SHARED-005 em `runtime.py` com teste. `predictor-ops provenance` VALIDATED contra a wheel 4.2.2rc1 no venv do cripto.
- **Pendente:** nenhum; 88 testes/cobertura 80,93 % citados no ESTADO são ET-HIST.
- **Bloqueado:** cleanroom; Windows (a própria SHARED-005 é comportamento Windows, não reproduzível aqui).
- **Não aplicável:** —

## ecosystem-predictor

- **Em profundidade (original, `a879525c`):** 70 arquivos próprios (contratos V1, registros, smoke de contrato).
- **Época main:** 61 arquivos; revisados os 15 de protocolo V2, transporte, ferramentas e estado; `--offline-check`, `--check` do registro (no commit-fonte) e `render_v2_mapping` passaram.
- **Pendente:** testes V2/transporte (12 arquivos) e workflows novos lidos só por diff; `compat/` não instalado.
- **Bloqueado:** `cross-repo-compatibility.yml`, `cain-crypto-integration.yml`, `crypto-harness-renewal.yml` (Actions); build do workspace de 5 pacotes offline.
- **Não aplicável:** —

## predictor-qualification

- **Em profundidade (original, `f21bbbcc`):** 41 scripts/workflows próprios; schema, núcleo, decisões, higiene; recomputo de números (`qualification_recompute.py`).
- **Época main:** 5.763 arquivos no delta (+1.128.312 linhas, 4.956 `RAW_LOGS`). Lidos: `CICLO_D27_20260930.md`, `DECISIONS.json` (28). Executado: `attest.py check` nas 6 missões, no commit de emissão (6/6 OK) e no `main` (3 não validam).
- **Pendente:** 198 scripts de missão e 106 documentos/relatórios; a revisão dos números de cada missão contra seus `RAW_LOGS` (C20) não foi refeita para o ciclo D-27.
- **Bloqueado:** reexecução dos runs de GitHub Actions citados; PC 2.
- **Não aplicável:** emitir attestation, decidir D-29/D-30/D-31 (só o dono).
