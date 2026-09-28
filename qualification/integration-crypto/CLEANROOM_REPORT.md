# integration-crypto — CLEANROOM_REPORT

## cleanroom-baseline (DIAGNÓSTICO, sem valor de gate; C5)

Executado nesta sessão no WSL do PC 2 (diagnóstico; não é ambiente primário). Script
`scripts/cleanroom_baseline.sh`; log bruto `RAW_LOGS/cleanroom-baseline/cleanroom_baseline.log` (sha256 `eabf68fbb6578447cde3a806e709a39e1c1247ca0f62ecc9c53b5e7309c27011`);
junit `RAW_LOGS/cleanroom-baseline/conformance.junit.xml` (sha256 `a595cb17b43781fa990d52fabb4dada4f537eff5479c03182f81e838169b2e19`).

| Lado | O que foi instalado | Resultado |
|---|---|---|
| domínio | venv limpo; dependências exportadas do `uv.lock` de `341d270` com `--require-hashes`; wheel publicada `cripto_predictor-1.2.0rc2` (sha256 `6e62f67f…` conferido) + wheel congelada `predictor_research_protocol-2.0.0rc2` (sha256 `34a1e412…` conferido), `--no-deps`; `pip check` sem erro | suíte de conformidade da Etapa A (`tests/conformance` de `341d270`, fora do checkout) contra o pacote instalado: junit tests="48" failures="0" 
errors="0" (números do junit) |
| CAIN | — | o commit base do cain (`f343701`, versão `0.4.13rc4` no pyproject) **não tem wheel publicada** (nenhuma tag no commit; releases do repo: só `v0.4.5`). O runtime qualificado do CAIN nasce da pré-release desta missão |

Conclusão do diagnóstico: o domínio instalado da release é compatível com a presença do protocolo V2 no mesmo venv
(o fecho de imports continua limpo: nenhum console script do cripto alcança `research_protocol` ou `adapters/`).

## cleanroom-final (gate CLEANROOM_FINAL; C24.3 c)

GitHub Actions ubuntu-latest × Python 3.13, run `run36462444590`, só as wheels publicadas de `runtime_targets.json` em venvs limpos fora dos checkouts (`scripts/cleanroom_final.sh`). Log: `qualification/integration-crypto/RAW_LOGS/runtime/run36462444590/cleanroom-final/cleanroom_final.log` (sha256 `6ae6001bbdd097a9…`).

| Suíte (instalada da wheel) | testes | falhas | erros | pulados |
|---|--:|--:|--:|--:|
| conformance | 48 | 0 | 0 | 0 |
| transport | 19 | 0 | 0 | 0 |
| cain | 65 | 0 | 0 | 0 |

- `conformance`: a suíte de conformidade congelada da Etapa A do cripto (`tests/conformance` do commit final), contra o `cripto-predictor` 1.2.0rc3 instalado com o protocolo e o transporte no mesmo venv (C24.3 c).
- `transport`: testes do `predictor-research-transport` 0.1.0rc6 contra a wheel instalada.
- `cain`: política, orquestração, cerco do loop e SHA completo, contra o `cain-research` 0.4.13rc13 instalado.
