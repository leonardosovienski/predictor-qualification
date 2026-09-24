# D-16 — o que falta para o Stocks (missão stocks)

Estado antes da D-16: 4 gates `NOT_RUN` com `BLOCKED: D-16 pendente` — `E2E`, `WINDOWS_SMOKE`, `SOAK`,
`STOCKS_NEGATIVE_CONTROLS` (regra congelada em `FROZEN_PARAMETERS.d16_dependency_rule`). Todos rodam hoje com a
fixture sintética congelada como **diagnóstico** e passam; nada disso vale como PASS.

Alvo congelado: `qualification/stocks/runtime_target.json` (stocks-predictor `61fc017`, wheel `v0.3.0rc2`
`92cb1131…`; Core 3.2.1 e Ops 4.2.2rc1 pelo `uv.lock`).

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

## 4. D-16 aprovada (3983de1): o que foi construído e fixado ANTES da execução (2026-09-24, noite no PC 2)

Tudo em `qualification/stocks/d16/`; workflow `.github/workflows/stocks-d16.yml` (push nesses caminhos ou
dispatch). Nenhum código do stocks-predictor mudou (alvo continua `61fc017` / `v0.3.0rc2`).

* **Construtor** `build_real_panel.py` (só stdlib, determinístico): `dados reais públicos → stocks-pit-panel/1`.
  Regras em `RULES` (repetidas no `SOURCES.json`; o build recusa divergência). Por fonte:

  | Fonte (URL oficial) | Uso | `available_at` | Classe PIT |
  |---|---|---|---|
  | B3 COTAHIST anual 2021–2026 (`bvmf.bmfbovespa.com.br/InstDados/SerHist/COTAHIST_A<ano>.ZIP`) | barras (close = PREULT/(100·FATCOT), volume R$), listagem (1º pregão na janela), tickers | próximo dia de semana após o pregão, 00:00 BRT (03:00Z) | `PIT_RECONSTRUCTED` |
  | CVM FCA 2021–2026 (`dados.cvm.gov.br/.../FCA/DADOS/fca_cia_aberta_<ano>.zip`) | emissor (CNPJ) por código de negociação; reserva por `CD_CVM` | DT_RECEB + 1 dia, 00:00 BRT (regra de `cvm_pit.receipt_dates`) | `PIT_RECONSTRUCTED` |
  | B3 eventos acionários por emissor (API pública `GetListedSupplementCompany`) | fatores oficiais de desdobramento, grupamento e bonificação (revisões PIT das barras anteriores à data ex); `codeCVM` da raiz | max(disponibilidade da barra ex, aprovação + 1 dia 00:00 BRT) | `PIT_RECONSTRUCTED` |
  | CVM VLMO 2026 (`dados.cvm.gov.br/.../VLMO/DADOS/vlmo_cia_aberta_2026.zip`) | só as 5 coletas `COLLECTION_ONLY` do soak (nunca painel/trial) | instante do download | — |

  Instrumentos: TPMERC 010 + CODBDI 02 (regra `cotahist.is_avista`) e ESPECI ações/units; `security_id` = ISIN.
  Pré-filtro de liquidez PIT (top 100 por mediana de 126 pregões, só passado) para caber no limite de 32 MiB do
  `ReferenceStore`; `verify_prefilter.py` prova pela wheel instalada que o universo de cada rebalance é idêntico
  ao do painel completo (falha fechada se não for). `data_cutoff` = disponibilidade do último pregão do snapshot.
* **Fontes fixadas:** `d16/SOURCES.json` (URL + sha256 + bytes + instante de cada arquivo; 6 COTAHIST, 6 FCA,
  1 VLMO, uma resposta da B3 por raiz de emissor do painel) e o sha256 esperado do painel. O job baixa tudo de
  novo pela URL oficial e confere cada hash (falha fechada). `COTAHIST_A2026.ZIP` é o snapshot da B3 do dia da
  fixação (hash diferente da cópia do PC 1 `34b77468…f4dc4f4`, de 2026-09-09, o que é esperado: o arquivo do ano
  corrente cresce a cada pregão; foi escolhido o snapshot atual porque é o que a URL oficial serve hoje e
  permite ao job conferir o hash; a cópia do PC 1 não pode ser baixada da B3).
* **Protocolo real** `d16/PROTOCOL_REAL.json`: objetos de operador a partir de `FROZEN_PARAMETERS.research_circuit`
  (top_n 60, liquidez 126, histórico 252, momentum 252/21, quintil superior, custos H1, baseline EW, bootstrap
  estacionário bloco 3 × 2000 seed 42, amostra mínima 24). Rebalance "fim de mês" não existe no handler compilado:
  usado `rebalance_every_sessions = 21`, declarado antes (achado **ST-F007**, decisão do dono).
* **Execução** (`d16_run.sh`, runtime suportado = só as final wheels, fora do checkout): `linux-primary`
  (E2E real por `scripts/e2e_runtime.py --real`, soak `d16_soak.py` no perfil congelado, conformidade),
  `linux-controls` (`d16_science.py`: referência + 4 controles × 20 seeds congeladas), `windows-latest`
  (E2E real + restart nos pontos de morte + conformidade). Nada de dado bruto ou painel no artefato (D-11).
* **Limitações declaradas do painel** (achado **ST-F008**): retorno só-preço (proventos em dinheiro, cisões,
  restituição de capital e bonificação em outra classe não ajustados; lista no `BUILD_MANIFEST.json`); API da B3
  sem alguns eventos antigos e vazia para raízes renomeadas; troca de ISIN = novo `security_id`; deslistagem não
  informada pelo COTAHIST (saída por inatividade); emissor desconhecido ⇒ fora do universo.

## 5. Resultado (run 35983568296, commit 5d1944c)

E2E, WINDOWS_SMOKE, SOAK e STOCKS_NEGATIVE_CONTROLS: **PASS** pelos critérios congelados (números em
`D16_EVIDENCE_NUMBERS.json`, tirados de `RAW_LOGS/d16/run35983568296/` por `scripts/d16_finalize.py`). Métricas
econômicas reais e contaminação por eventos não ajustados: `D16_REAL_DATA_REPORT.md`. Run 35981568362 (anterior)
parou no setup por download truncado da B3 (falha fechada; corrigido em 5d1944c) e não é evidência de gate.
