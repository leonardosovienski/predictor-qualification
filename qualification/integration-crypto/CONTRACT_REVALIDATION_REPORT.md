# integration-crypto — CONTRACT_REVALIDATION_REPORT

Gate `DOMAIN_CONTRACTS_PRESERVED` e `domain_attestations[0].revalidation` (C24.3), domínio crypto, entre o final_commit da Etapa A (`21f8b182286248859e1b2cb8fa2bab0138a58e2a`) e o desta missão (`21f8b182286248859e1b2cb8fa2bab0138a58e2a`, tag v1.2.0rc3).

Parte estática (`qualification/integration-crypto/RAW_LOGS/contract-revalidation-rc16e/static_checks.json` (sha256 `789d73d13830a82a…`)):

| Conferência | Resultado |
|---|---|
| (a) files changed outside adapter_paths are only the version files | OK |
| (a) uv.lock identical apart from the project version (no dependency change) | OK |
| (b) nothing outside adapter_paths imports from it | OK |
| (b) no console script points into adapter_paths | OK |
| (e) every protected item of the crypto domain has the same blob at the final commit | OK |
| (f) CI of the domain green on the exact final commit (push run) | OK |

(c) suíte de conformidade verde com as wheels da integração: 48 testes, 0 falhas (`qualification/integration-crypto/RAW_LOGS/runtime/run37703318858/cleanroom-final/conformance.junit.xml` (sha256 `b2e450f0299b09dd…`)).

(d) vetor real da Etapa A pelo adapter: 10 conferências OK, 0 falhas (`qualification/integration-crypto/RAW_LOGS/runtime/run37703318858/contract-revalidation/SUMMARY.json` (sha256 `a9f354c125fb37a6…`)): hash canônico sem `client_ref` igual ao do vetor, `client_ref` devolvido igual, payload byte-idêntico ao `show` (adapter_api).
