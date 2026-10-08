# integration-stocks — CAIN_ROUNDTRIP_REPORT

Gates `E2E`, `PROVENANCE`, `IDEMPOTENCY`, `RESTART_RECOVERY`, `FAILURE_INJECTION`, `AUTHORITY_SEPARATION`, `FUTURE_CANARY`, `CAIN_INGESTION`, `CAIN_CONTAINMENT`, `N_PLUS_1_DETERMINISTIC`, `CROSS_DOMAIN_ISOLATION`, `DOMAIN_QUALIFIED_IDS`, `CONTRADICTION_PRESERVATION`, `WINDOWS_SMOKE`. Gerado por `scripts/render_reports.py`.

Circuito: `cain research propose` → DecisionPolicy → TaskOutbox → spool → `predictor-research-consumer` → adapter do Stocks → `Circuit.submit_request` (admission → Ops → Core) → resultado → ResultInbox → memória do domínio `stocks` → próxima decisão. Tudo pelos entrypoints instalados das wheels publicadas; os venvs do CAIN e do consumidor são separados (o CAIN não tem domínio instalado; `runtime_env.sh` confere).

Dados reais: painel B3/CVM do pin do run (`data/SOURCES.json`), data_cutoff `2026-10-08T03:00:00Z`, painel `3ba4924a5573c8a7…`, dataset `b3-cvm-real-2021-01-04_2026-10-07-cotahist522444a57761-k100`.

| Cenário | Ambiente | Conferências OK | Falhas | Fonte |
|---|---|--:|--:|---|
| E2E (dados reais, restart do consumidor e do CAIN, outros domínios intercalados, canário, N+1) | Linux primário, run `run37704456789` | 55 | 0 | `qualification/integration-stocks/RAW_LOGS/runtime/run37704456789/e2e/SUMMARY.json` (sha256 `d5a72bb2ba5e1c17…`) |
| E2E + restart (WINDOWS_SMOKE) | GitHub Actions windows-latest, run `run37704456789-windows` | 55 | 0 | `qualification/integration-stocks/RAW_LOGS/runtime/run37704456789-windows/e2e/SUMMARY.json` (sha256 `2847ac2a2e869546…`) |
| N+1 congelado (3 processos, receipt byte a byte) | Linux primário | 63 | 0 | `qualification/integration-stocks/RAW_LOGS/runtime/run37704456789/n-plus-1/frozen/SUMMARY.json` (sha256 `47e25f116bc2c2ef…`) |
| N+1 integrado (resultado real do cripto no spool) | Linux primário | 64 | 0 | `qualification/integration-stocks/RAW_LOGS/runtime/run37704456789/n-plus-1/integrated/SUMMARY.json` (sha256 `9eb7ea9ab8b40a6f…`) |
| Isolamento e IDs (cripto integrado; brasileirao por fixture) | Linux primário | 28 | 0 | `qualification/integration-stocks/RAW_LOGS/runtime/run37704456789/isolation/SUMMARY.json` (sha256 `bb435a0eb13a3cc4…`) |
| Contradição | Linux primário | 9 | 0 | `qualification/integration-stocks/RAW_LOGS/runtime/run37704456789/isolation/contradiction/SUMMARY.json` (sha256 `5aea1d916b98b517…`) |
| Contrato C24.3 (d) | Linux primário | 11 | 0 | `qualification/integration-stocks/RAW_LOGS/runtime/run37704456789/contract-revalidation/SUMMARY.json` (sha256 `871107ffcdf3865b…`) |

Decisões do E2E (em ordem): ALLOW, ALLOW, ALLOW, DUPLICATE, BLOCK, BLOCK, BLOCK, ALLOW.

Estados do domínio nos resultados reais do E2E (copiados como vieram; nenhum é promovido; C22: QUALIFIED não é edge):

| Episódio | Operacional | Resultado | Científico | Econômico |
|---|---|---|---|---|
| 01 | SUCCEEDED | INCONCLUSIVE | INCONCLUSIVE | NO_EDGE |
| 02 | SUCCEEDED | INCONCLUSIVE | INCONCLUSIVE | NO_EDGE |
| 08 | SUCCEEDED | INCONCLUSIVE | INCONCLUSIVE | NO_EDGE |

Memória por cubo no estado compartilhado do isolamento: {"brasileirao": [], "crypto": ["crypto:QUAL-SHADOW-REAL-001"], "stocks": ["stocks:QUAL-PIT-MOM-REAL-001"], "verify": "intact"}.

## N+1 (as_of `2026-09-27T00:00:00Z`)

| Candidata | Decisão | Motivo | Regra | receipt sha256 |
|---|---|---|---|---|
| 01-next | ALLOW | ALLOWED | R14 | `0874661808814678…` |
| 02-duplicate | DUPLICATE | DUPLICATE_REQUEST | R08 | `f99ab6fe3ed7d94b…` |
| 03-crypto-h9 | BLOCK | DOMAIN_MISMATCH | R01 | `ebe03df1ec946f96…` |
| 04-stocks-h9 | BLOCK | HYPOTHESIS_CLOSED | R05 | `e06d96b39b04943c…` |
| 05-brasileirao-h9 | BLOCK | DOMAIN_MISMATCH | R01 | `373ebbfd4618ef6b…` |
| 06-new-hypothesis | REQUIRE_HUMAN | NEW_HYPOTHESIS | R11 | `40d23edbff3bd3ea…` |
| 07-h1-momentum | BLOCK | HYPOTHESIS_CLOSED | R05 | `8073f0bd3db41e9e…` |
| 08-h2-low-vol | BLOCK | HYPOTHESIS_CLOSED | R05 | `e54309a77cbe672f…` |
| 09-h14-52w-high | BLOCK | HYPOTHESIS_CLOSED | R05 | `aceff41c03db805b…` |
| 10-h15-volume | BLOCK | HYPOTHESIS_CLOSED | R05 | `93eaee463d744bde…` |
| 11-family-momentum | BLOCK | HYPOTHESIS_CLOSED | R05 | `fdbdc6463e0b3771…` |
| 12-family-low-vol | BLOCK | HYPOTHESIS_CLOSED | R05 | `fc1c50bdf3f74de1…` |
| 13-family-52w-high | BLOCK | HYPOTHESIS_CLOSED | R05 | `46ab206a6430c5e8…` |
| 14-family-volume | BLOCK | HYPOTHESIS_CLOSED | R05 | `c5c9ed9194c824f9…` |
| 15-watch-high-priority | BLOCK | PRIORITY_ABOVE_CAP | R06 | `3694df11b2141f26…` |
| 16-cost-mismatch | BLOCK | COST_MODEL_MISMATCH | R06 | `cf90194fd256cbb7…` |
| 17-collection | ALLOW | ALLOWED | R14 | `df2c178c12751809…` |
| 18-llm-shape | BLOCK | SCHEMA_INVALID | R02 | `e3c561801a6380af…` |
| 19-unqualified-id | BLOCK | DOMAIN_MISMATCH | R01 | `063571b67ffc82ea…` |
| 20-reference-not-allowed | BLOCK | REFERENCE_NOT_ALLOWED | R06 | `f0253193b343ed34…` |

Receipts da variante integrada iguais aos da congelada: **sim**.

## Matriz de falhas (FAILURE_MATRIX.json)

| Ponto | OK | Falhas |
|---|--:|--:|
| F01 | 3 | 0 |
| F02 | 3 | 0 |
| F03 | 3 | 0 |
| F04 | 3 | 0 |
| F05 | 4 | 0 |
| F06 | 2 | 0 |
| F07 | 2 | 0 |
| F08 | 10 | 0 |
| F09 | 2 | 0 |
| F10 | 3 | 0 |
| F11 | 3 | 0 |
| F12 | 3 | 0 |
| F13 | 2 | 0 |
| F14 | 3 | 0 |
| F15 | 4 | 0 |

Fonte: `qualification/integration-stocks/RAW_LOGS/runtime/run37704456789/failure-matrix/FAILURE_MATRIX_RESULTS.json` (sha256 `62f9f41cd8595210…`).

## Parecer de contenção (CAIN_CONTAINMENT)

- O CAIN só propõe: o pedido não carrega handler, comando, módulo, caminho, URL, budget, prioridade final nem capital (R03). O handler vem da `admission_policy` do Stocks (allowlist compilada).
- O CAIN nunca lê banco de domínio: ele só lê o spool (envelopes V2) e a própria memória. O venv do CAIN não tem domínio instalado, e nenhum console script do `cain` alcança um pacote de domínio (`test_loop_fenced.py`).
- O CAIN nunca executa código de avaliação fora do circuito: o loop do PR #50 continua fora do runtime qualificado (`python -m cain.loop`, ferramenta de laboratório; nenhum console script o alcança).
- PR #51 (`cain findings ingest-*`): leitura de arquivo versionado por `git show` num commit fixado, só leitura. A orquestração qualificada do Stocks não chama esse comando: a configuração do domínio vem de 61fc017 (SHA completo) pelo `tools/build_domain_config.py` e fica empacotada (`data/stocks.json`).
