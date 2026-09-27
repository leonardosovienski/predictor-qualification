Pré-release do envelope V2 para a Etapa B (três orquestrações por domínio, D-22). Substitui a 2.0.0rc1.

- `episode_id` (`<domínio>:episode-<n>`) e `previous_task_id` na `ResearchTaskV2`; `episode_id` ecoado na `ResearchResultV2`; `task_id` derivado também do episódio.
- `client_ref` nulo aceito em `STATE_BUSY_RETRYABLE` (outcome real do stocks com o banco de estado ocupado durante a admission).
- Registro dos domínios gerado dos contratos da Etapa A no `main` do `predictor-qualification`.

Especificação: `packages/research-protocol/SPEC_V2.md` (PR #29). Só a wheel é publicada. Ela é reproduzível: build 2× pelo método D-14, com o mesmo sha256 do asset. Congelamento: `qualification/shared/ENVELOPE_V2_FREEZE.json` no `predictor-qualification`.
