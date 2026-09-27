# integration-crypto — ENVELOPE_V2_CONFORMANCE_REPORT

Gate `ENVELOPE_V2_CONFORMANCE` (prompt comum §6.1). Os números estão em `EVIDENCE_NUMBERS.json` (C20).

## Consumo da release congelada

- `predictor-research-protocol` **2.0.0rc2** (`ENVELOPE_V2_FREEZE.json`): wheel `34a1e412…`, conferida por URL + sha256 no pré-voo (`RAW_LOGS/c0/c0_preflight.log`).
- Consumidores V2 criados nesta missão, todos pinando essa wheel pelo `uv.lock`:
  - `cain` 0.4.13rc6;
  - `predictor-research-transport` 0.1.0rc3 (mesmo código do 0.1.0rc2, republicado de um commit com CI verde; IC-F004).
- `packages/research-protocol` não mudou.

## Adapter do cripto (só em `GarimpoInvestimentos/adapters/`)

- `GarimpoInvestimentos/adapters/research_v2.py` (cripto-predictor `v1.2.0rc3`, commit `ee3d3d1`):
  - **V2 → pedido do contrato**: os bytes submetidos são o JSON canônico de `task["payload"]`, isto é, o pedido do contrato com o `client_ref` do envelope. É exatamente `research_protocol.v2.request_bytes(task)`.
  - **só pela `adapter_api`**: `Circuit(state, policy, objects).submit_request` e `Circuit(state).show`.
  - **resultado → V2**: o outcome do domínio volta sem mudança. O consumidor do transporte embala com o `build_result` normativo do protocolo congelado. O payload vai como a string canônica do resultado do domínio.
- Sem console script e sem dependência do protocolo no domínio, com prova:
  - `RAW_LOGS/diag-import-closure/probe_adapter_entrypoint.log`;
  - `tests/test_shared_wheel_download_hashes.py` do cripto (SPEC V2 §9; achados IC-F002 e IC-F003).

## Conferências do consumidor (a cada entrega)

1. A task é validada fail closed: bytes canônicos, schema, IDs, hashes, domínio do consumidor e nome do arquivo.
2. `outcome.submission_sha256 == sha256(request_bytes(task))`. O domínio recebeu exatamente os bytes do envelope.
3. Em `RESULT`/`DUPLICATE`, `payload_sha256 == cripto-research show().result_sha256`: o payload é byte-idêntico ao da `adapter_api` (C24.3 d).
4. Uma falha em qualquer uma dessas → `REQUIRES_HUMAN` no ledger do consumidor. Nada é publicado.

## Evidência de execução

Tudo com as wheels publicadas no Linux primário:

- E2E: a proveniência de cada resultado e as conferências byte a byte;
- contrato (d): o vetor da Etapa A passa pelo adapter e o hash canônico coincide;
- matriz F11–F13: versão errada, outro payload, task errada.

As chaves correspondentes estão em `EVIDENCE_NUMBERS.json`.
