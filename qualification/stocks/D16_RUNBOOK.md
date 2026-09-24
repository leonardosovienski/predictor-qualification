# D-16 — o que falta para o Stocks (missão stocks)

Estado antes da D-16: 4 gates `NOT_RUN` com `BLOCKED: D-16 pendente` — `E2E`, `WINDOWS_SMOKE`, `SOAK`,
`STOCKS_NEGATIVE_CONTROLS` (regra congelada em `FROZEN_PARAMETERS.d16_dependency_rule`). Todos rodam hoje com a
fixture sintética congelada como **diagnóstico** e passam; nada disso vale como PASS.

Alvo congelado: `qualification/stocks/runtime_target.json` (stocks-predictor `9a6c09a`, wheel `v0.3.0rc1`
`3cc4e04a…`; Core 3.2.1 e Ops 4.2.2rc1 pelo `uv.lock`).

## 1. O que só o dono decide (entrada D-16 em `qualification/DECISIONS.json`, por PR + merge)

* **onde roda** o Linux primário (GitHub Actions ou VM na nuvem, D-9) — e o windows-latest para o `WINDOWS_SMOKE`,
  porque o Stocks não tem runtime no Windows local (D-1);
* **quais dados reais** entram, com URL + sha256 (prompt §4): o painel PIT precisa de preços (ex.: séries COTAHIST
  públicas da B3) **e** de identidade/eventos com `available_at` (listagem, deslistagem, ticker, CNPJ — ex.: CVM
  FCA). `C:\STOCKS\data` e `DADOS_STOCKS.zip*` não saem desta máquina sem decisão explícita (D-11: nada comprado ou
  sem direito de redistribuição em repo público);
* que a D-16 autoriza rodar os 4 gates no alvo congelado sem mudar parâmetros, vetores nem perfil (C15).

## 2. Trabalho que a D-16 destrava (e que não existe hoje)

Um construtor versionado `dados reais → stocks-pit-panel/1` (no repositório de evidência, como o
`build_real_dataset.py` do crypto), com a regra de `available_at` de cada fonte declarada e classe PIT honesta
(ex.: COTAHIST = `PIT_RECONSTRUCTED` com disponibilidade no dia útil seguinte). Não foi escrito nesta missão para
não inventar a solução da D-16. O circuito aceita qualquer painel que cumpra o contrato; nenhum código do
stocks-predictor precisa mudar (C14: se precisar, refazer publish-candidates e cleanroom-final).

## 3. Execução depois da D-16

Mesmo workflow `stocks-runtime.yml` com o painel real provisionado como objeto de referência (sha256 no
`FROZEN_PARAMETERS`/runbook): E2E pelo entrypoint, controles negativos (20 seeds congeladas), soak no perfil
`QUALIFICATION_PROFILE_STOCKS_V1.json`, e o E2E + restart no windows-latest. Métricas econômicas reais (bruto e
líquido com IC e custos H1) saem do mesmo resultado; hoje **não há nenhuma métrica econômica real medida**.
