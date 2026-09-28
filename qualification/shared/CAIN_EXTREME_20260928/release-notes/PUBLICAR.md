# Publicação das pré-releases rc14 (cain) e rc7 (transporte) — roteiro para o PC 2

Esta sessão (nuvem) não pode criar releases: a API do GitHub responde
`Creating, editing, or deleting releases is not permitted for this session type`. Tudo o mais está pronto.
Publicar pelo `publish_rc.sh` da integration-crypto (mesmo método das rc12/rc13 e das rc5/rc6), no PC 2, com `gh`.

## 1. Transporte 0.1.0rc7 (já no `main`: ecosystem-predictor#38 e #39)

```bash
S=qualification/integration-crypto/scripts/publish_rc.sh
bash $S <clone do ecosystem-predictor> leonardosovienski/ecosystem-predictor \
  f0cc041f72c000aadb53ec25682bfd2da9cdc511 packages/research-transport \
  predictor-research-transport-v0.1.0rc7 \
  "predictor-research-transport 0.1.0rc7 (task ilegível nunca derruba a passada)" \
  qualification/shared/CAIN_EXTREME_20260928/release-notes/predictor-research-transport-v0.1.0rc7.md \
  <saída>
```

Esperado: `REPRODUCIBLE=YES` e wheel `predictor_research_transport-0.1.0rc7-py3-none-any.whl` com sha256
`d3dfbff4b72d717ed4f655b1c97e85ca909140dcd9ebfb17e9a51a8b089c60c2` (o mesmo que esta sessão obteve 2× em
`RAW_LOGS/repro/transport_rc7_reproducible_build.log`; tree `6cfc7ad9…`). CI do push no `main` `f0cc041`: 21/21.

## 2. cain 0.4.13rc14 (depois do merge do cain#81)

```bash
COMMIT=<sha completo do merge do cain#81 no main>
bash $S <clone do cain> leonardosovienski/cain $COMMIT . v0.4.13rc14 \
  "cain-research 0.4.13rc14 (robustez da borda, auditoria de 2026-09-28)" \
  qualification/shared/CAIN_EXTREME_20260928/release-notes/cain-v0.4.13rc14.md <saída>
```

Esperado: `REPRODUCIBLE=YES`; conferir que o CI do push no `main` está verde nesse SHA antes de publicar (C21).

## 3. Depois

Adotar as duas releases nas três integrações (`runtime_targets.json`, `adopt_release.py` no Brasileirão) e refazer
as fases pela C14: cleanroom-final, C24.3 (d), e2e, N+1, isolamento, F01–F1x, windows-smoke, hosted-ci, soak, attestation.
O `policy.py` e os três `<domínio>.json` não mudam, então os congelados e os vetores N+1 continuam válidos.
