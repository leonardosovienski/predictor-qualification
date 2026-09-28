# integration-stocks — CLEANROOM_REPORT

## cleanroom-baseline (DIAGNÓSTICO, sem valor de gate; C5)

WSL do PC 2 (diagnóstico). Script `scripts/cleanroom_baseline.sh`; log `qualification/integration-stocks/RAW_LOGS/cleanroom-baseline/cleanroom_baseline.log` (sha256 `de4247627ca6897c…`).

- domínio: stocks-predictor 0.3.0rc2 (wheel da release) + protocolo 2.0.0rc2 + transporte 0.1.0rc3 num venv limpo; conformidade da Etapa A contra o pacote instalado: 87 testes, 0 falhas (`qualification/integration-stocks/RAW_LOGS/cleanroom-baseline/conformance.junit.xml` (sha256 `6006e8de9aac6549…`));
- consumidor `--domain stocks`: `ADAPTER_UNAVAILABLE` (allowlist do transporte só com crypto);
- `cain research propose --domain stocks` (cain 0.4.13rc6): `CONFIG_INVALID`, sem estado gravado (só `crypto.json` empacotado).

## cleanroom-final (gate CLEANROOM_FINAL; C24.3 b/c)

GitHub Actions ubuntu-latest × Python 3.13, run `run36440479456`, só as wheels publicadas de `runtime_targets.json` em venvs limpos fora dos checkouts (`scripts/cleanroom_final.sh`). Log: `qualification/integration-stocks/RAW_LOGS/runtime/run36440479456/cleanroom-final/cleanroom_final.log` (sha256 `5d42c912f1e25dd0…`).

| Suíte (instalada da wheel) | testes | falhas | erros | pulados |
|---|--:|--:|--:|--:|
| conformance | 87 | 0 | 0 | 0 |
| adapters | 11 | 0 | 0 | 0 |
| transport | 15 | 0 | 0 | 0 |
| cain | 80 | 0 | 0 | 0 |

- `conformance`: suíte de conformidade congelada da Etapa A (`tests/conformance` do commit final) contra o `stocks-predictor` 0.3.0rc3 instalado com o protocolo e o transporte no mesmo venv (C24.3 c), inclusive `test_import_closure.py` (regras de adapter_paths, C24.3 b);
- `adapters`: testes novos do adapter (D-24 (4a)) contra a mesma wheel;
- `transport`: testes do `predictor-research-transport` 0.1.0rc5 contra a wheel instalada;
- `cain`: política, configuração do Stocks, orquestração, cerco do loop e SHA completo, contra o `cain-research` 0.4.13rc12 instalado.
