# integration-crypto — CORE_IDENTITY_REPORT

Gates `LOCK_INTEGRITY` e `CORE_IDENTITY` (C4). Gerado por `scripts/render_reports.py`.

Fonte: `qualification/integration-crypto/RAW_LOGS/core-identity-rc16/core_identity.json` (sha256 `1627c03709808564…`), produzido por `scripts/core_identity.py` a partir dos `uv.lock` dos commits finais (git show, SHA completo) e dos logs do run `run37696817503`.

Resultado: **13 conferências OK, 0 falhas**.

| Conferência | Resultado |
|---|---|
| cain: predictor-research-bundle same wheel in pyproject/STACK_WHEELS.json/uv.lock/fetch/install (D-32) | OK |
| cain: predictor-research-protocol same wheel in pyproject/STACK_WHEELS.json/uv.lock/fetch/install (D-32) | OK |
| cain: predictor-research-snapshot same wheel in pyproject/STACK_WHEELS.json/uv.lock/fetch/install (D-32) | OK |
| cain: predictor-research-transport same wheel in pyproject/STACK_WHEELS.json/uv.lock/fetch/install (D-32) | OK |
| cripto-predictor: predictor-core same wheel in pyproject/uv.sources/uv.lock/install | OK |
| cripto-predictor: predictor-ops same wheel in pyproject/uv.sources/uv.lock/install | OK |
| cain-research: installed version == published final wheel | OK |
| cripto-predictor: installed version == published final wheel | OK |
| predictor-research-transport: installed version == published final wheel | OK |
| predictor-research-protocol: installed version == published final wheel | OK |
| every final wheel downloaded by URL passed sha256sum -c in the runtime | OK |
| the CAIN registry fetch verified every stack wheel by sha256 (stack_wheels.py fetch, D-32) | OK |
| runtime modules load from site-packages (not a checkout) | OK |

Os runtimes (CAIN e consumidor) são instalados só com requisitos exportados dos `uv.lock` (`--require-hashes`) e com as wheels publicadas conferidas por sha256 antes de instalar (`scripts/runtime_env.sh`). Nenhum pacote do stack vem de índice público, de `vendor/` ou de checkout.
