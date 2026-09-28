Pré-release da missão `integration-stocks` (Etapa B, D-22/D-24). A v0.3.0rc2 (runtime qualificado da Etapa A) continua
publicada sem mudança.

- **Base:** `61fc017256ffea815ae96bbe02b847dccdb395cc` (runtime_target, D-24); nada de `61fc017..main` (#99–#106) entra.
- **Adapter V2** em `stocks_predictor/adapters/research_v2.py` (adapter_paths do contrato): ResearchTaskV2 → adapter_api
  (`Circuit.submit_request/show`), só stdlib, sem console script; carregado pelo nome do módulo pelo consumidor do
  transporte (predictor-research-transport 0.1.0rc4).
- **Testes novos** em `tests/adapters/` (D-24 (4a)); versão 0.3.0rc3 (pyproject + linha do uv.lock).
- **Procedimento R8** da D-24 (4b): recibos `docs/engineering/2026-09-27-integration-stocks/evidence/` (COTAHIST_A2026
  local sha256 `34b77468…`, 55.986 linhas; capacidade 250.000 sintéticas) e selo `current-operational-evidence.json`.
  Evidência de engenharia da regra local, nunca de gate.
- **Commit desta release:** `6f857b232eaa63f3fccda6a16f92dbfc8983ab3b`, branch `integration-stocks/adapter-20260927`.
  CI Pipeline por workflow_dispatch nesse SHA: Quality 3.13 e 3.14 verdes; job secrets vermelho por um falso positivo
  já documentado que está no histórico do main (commit 28f17d2, PR #99), fora desta branch (achado IS-F005 da missão).
- **Build:** `tools/reproducible_build.py` (duas builds, mesmos bytes, SOURCE_DATE_EPOCH = data do commit).
- Qualificação, não operação: sem autorização de capital.
