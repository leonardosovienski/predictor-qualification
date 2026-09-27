# integration-crypto — CONTRACT_REVALIDATION_REPORT

Gate `DOMAIN_CONTRACTS_PRESERVED` e `domain_attestations[0].revalidation` (C24.3), domínio crypto, entre o final_commit da Etapa A (`341d270e4d709150c581c3cd93f4518d483009eb`) e o desta missão (`ee3d3d17de0b76cf731808243ffa838a0f5ee8cc`, tag v1.2.0rc3).

Parte estática (`qualification/integration-crypto/RAW_LOGS/contract-revalidation-c14/static_checks.json` (sha256 `1d589d52eb96a450…`)):

| Conferência | Resultado |
|---|---|
| (a) files changed outside adapter_paths are only the version files | OK |
| (a) GarimpoInvestimentos/__init__.py: only the pre-release version line changed | OK |
| (a) pyproject.toml: only the pre-release version line changed | OK |
| (a) uv.lock: only the pre-release version line changed | OK |
| (a) uv.lock identical apart from the project version (no dependency change) | OK |
| (b) nothing outside adapter_paths imports from it | OK |
| (b) no console script points into adapter_paths | OK |
| (e) every protected item of the crypto domain has the same blob at the final commit | OK |
| (f) CI of the domain green on the exact final commit (push run) | OK |

(c) suíte de conformidade verde com as wheels da integração: 48 testes, 0 falhas (`qualification/integration-crypto/RAW_LOGS/runtime/run36360075557/cleanroom-final/conformance.junit.xml` (sha256 `0da0659238bee316…`)).

(d) vetor real da Etapa A pelo adapter: 10 conferências OK, 0 falhas (`qualification/integration-crypto/RAW_LOGS/runtime/run36360075557/contract-revalidation/SUMMARY.json` (sha256 `44dcd6db12f5af2a…`)): hash canônico sem `client_ref` igual ao do vetor, `client_ref` devolvido igual, payload byte-idêntico ao `show` (adapter_api).
