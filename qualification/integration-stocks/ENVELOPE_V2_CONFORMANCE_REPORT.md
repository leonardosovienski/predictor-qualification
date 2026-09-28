# integration-stocks — ENVELOPE_V2_CONFORMANCE_REPORT

Gate `ENVELOPE_V2_CONFORMANCE`. Protocolo V2 consumido da release congelada `predictor-research-protocol` 2.0.0rc2 (`34a1e4121e4085b9…`, ENVELOPE_V2_FREEZE.json), sem mudança; transporte `predictor-research-transport` 0.1.0rc4 (só a entrada stocks na allowlist).

| Propriedade | Evidência |
|---|---|
| adapter só pela `adapter_api` (`Circuit.submit_request/show`), sem console script, só stdlib | cleanroom-final `adapters` (11 testes) e `conformance` (87), `qualification/integration-stocks/RAW_LOGS/runtime/run36365355063/cleanroom-final/cleanroom_final.log` (sha256 `10f5590b2481d89c…`) |
| pedido V2 → `stocks-research-request/1` com `client_ref`; hash canônico sem `client_ref` = vetor da Etapa A | C24.3 (d): 11/11 |
| payload de domínio byte-idêntico ao `show` em todo RESULT/DUPLICATE | E2E 55/55, Windows 55/55 |
| versão errada, mesmo ID com outro payload, envelope válido da task errada | F11 3 OK, F12 3 OK, F13 2 OK |
| resultado de outro domínio nunca aceito | isolamento 27/27 |
