# integration-crypto — CAIN_ROUNDTRIP_REPORT

Gates `E2E`, `PROVENANCE`, `IDEMPOTENCY`, `RESTART_RECOVERY`, `FAILURE_INJECTION`, `AUTHORITY_SEPARATION`, `FUTURE_CANARY`, `CAIN_INGESTION`, `CAIN_CONTAINMENT`, `N_PLUS_1_DETERMINISTIC`, `CROSS_DOMAIN_ISOLATION`, `DOMAIN_QUALIFIED_IDS`, `CONTRADICTION_PRESERVATION`. Gerado por `scripts/render_reports.py`.

Circuito: `cain research propose` → DecisionPolicy → TaskOutbox → spool → `predictor-research-consumer` → adapter → admission → Ops → Core → resultado → ResultInbox → memória do domínio → próxima decisão. Tudo pelos entrypoints instalados das wheels publicadas; os venvs do CAIN e do consumidor são separados (o CAIN não tem o domínio instalado; `runtime_env.sh` confere).

| Cenário | Ambiente | Conferências OK | Falhas | Fonte |
|---|---|--:|--:|---|
| E2E (dados reais, restart do consumidor e do CAIN, outros domínios intercalados, canário, N+1) | Linux primário, run `run36439656179` | 56 | 0 | `qualification/integration-crypto/RAW_LOGS/runtime/run36439656179/e2e/SUMMARY.json` (sha256 `b58ffa8d7fad9681…`) |
| E2E + restart (WINDOWS_SMOKE) | Windows local do **PC 2** | 56 | 0 | `qualification/integration-crypto/RAW_LOGS/windows-smoke-ciclo3/e2e/SUMMARY.json` (sha256 `e8911fa3e27e077f…`) |
| N+1 (3 processos, receipt byte a byte) | Linux primário | 21 | 0 | `qualification/integration-crypto/RAW_LOGS/runtime/run36439656179/n-plus-1/SUMMARY.json` (sha256 `ae3bd25dd7775b58…`) |
| Isolamento, IDs com domínio, contradição | Linux primário | 22 | 0 | `qualification/integration-crypto/RAW_LOGS/runtime/run36439656179/isolation/SUMMARY.json` (sha256 `525f6dd323315b62…`) |
| Contrato C24.3 (d) | Linux primário | 10 | 0 | `qualification/integration-crypto/RAW_LOGS/runtime/run36439656179/contract-revalidation/SUMMARY.json` (sha256 `7389c4d626c20115…`) |

Decisões do E2E (em ordem): ALLOW, ALLOW, ALLOW, DUPLICATE, BLOCK, BLOCK, ALLOW.

## N+1 (as_of `2026-09-27T00:00:00Z`)

| Candidata | Decisão | Motivo | Regra | receipt sha256 |
|---|---|---|---|---|
| 01-next | ALLOW | ALLOWED | R14 | `8a6a0ad36f8e9649…` |
| 02-duplicate | DUPLICATE | DUPLICATE_REQUEST | R08 | `cd95e7e44beac0b7…` |
| 03-crypto-h9 | BLOCK | HYPOTHESIS_CLOSED | R05 | `89886db8d2969e2f…` |
| 04-stocks-h9 | BLOCK | DOMAIN_MISMATCH | R01 | `b4f42591602d9bcc…` |
| 05-brasileirao-h9 | BLOCK | DOMAIN_MISMATCH | R01 | `f468f3bcd749f06c…` |
| 06-new-hypothesis | REQUIRE_HUMAN | NEW_HYPOTHESIS | R11 | `b448c93a706ec94e…` |

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

Fonte: `qualification/integration-crypto/RAW_LOGS/runtime/run36439656179/failure-matrix/FAILURE_MATRIX_RESULTS.json` (sha256 `62f9f41cd8595210…`).

## Parecer de contenção (CAIN_CONTAINMENT)

- O CAIN só propõe: o pedido não carrega handler, comando, módulo, caminho, URL, budget, prioridade final nem capital (R03). O handler vem da `admission_policy` do domínio.
- O CAIN nunca lê banco de domínio: ele só lê o spool (envelopes V2) e a própria memória. O venv do CAIN não tem o domínio instalado, e nenhum console script do `cain` alcança um pacote de domínio (`test_loop_fenced.py`).
- O CAIN nunca executa código de avaliação fora do circuito. O loop do PR #50 ficou fora do runtime qualificado (ver DECISION_POLICY_REPORT.md §4).
- PR #51 (`cain findings ingest-*`): lê arquivo versionado por `git show` num commit fixado, só leitura, sem efeito no domínio. Para o cripto, só com o SHA completo (teste `test_findings_pinned_sha.py`). A orquestração qualificada não chama esse comando: a configuração do domínio já vem da base congelada.
