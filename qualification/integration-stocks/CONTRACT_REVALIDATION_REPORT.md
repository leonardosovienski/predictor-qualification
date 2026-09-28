# integration-stocks — CONTRACT_REVALIDATION_REPORT

Gate `DOMAIN_CONTRACTS_PRESERVED` e `domain_attestations[0].revalidation` (C24.3), domínio stocks, entre o final_commit da Etapa A (`61fc017256ffea815ae96bbe02b847dccdb395cc`) e o desta missão (`6f857b232eaa63f3fccda6a16f92dbfc8983ab3b`, tag v0.3.0rc3).

## C24.3 (a) — diff completo do domínio

| Arquivo | Estado |
|---|---|
| `docs/engineering/2026-09-27-integration-stocks/evidence/operational-capacity.json` | A |
| `docs/engineering/2026-09-27-integration-stocks/evidence/operational-real.json` | A |
| `docs/engineering/current-operational-evidence.json` | M |
| `pyproject.toml` | M |
| `stocks_predictor/adapters/research_v2.py` | A |
| `tests/adapters/__init__.py` | A |
| `tests/adapters/conftest.py` | A |
| `tests/adapters/test_research_v2.py` | A |
| `uv.lock` | M |

Fora de `stocks_predictor/adapters/` só entram:

- C24.3(a): a linha `version` do `pyproject.toml` e a linha da versão do projeto no `uv.lock` (pré-release);
- **autorizados pela D-24 (4)** (decisão do dono, resposta ao conflito C19 entre a regra local R8 e C24.3(a)): arquivos NOVOS em `tests/adapters/`, os dois recibos R8 novos (só `.json`) em `docs/engineering/2026-09-27-integration-stocks/evidence/` e o selo `docs/engineering/current-operational-evidence.json`.

Parte estática (`qualification/integration-stocks/RAW_LOGS/contract-revalidation-rc13/static_checks.json` (sha256 `4fa34ff80c3a5f0b…`)):

| Conferência | Resultado |
|---|---|
| (a) outside adapter_paths only: version files, new tests/adapters/, new R8 receipts (.json) and the seal | OK |
| (a) no existing test changed (tests/ outside tests/adapters/ untouched) | OK |
| (a) no new Markdown and nothing under tools/, .github/, research/, policy/ or the rest of docs/ | OK |
| (a) pyproject.toml: only the pre-release version line changed | OK |
| (a) uv.lock: only the pre-release version line changed | OK |
| (a) uv.lock identical apart from the project version (no dependency change) | OK |
| (a) the seal points to the new R8 receipts and never enables capital or certifies profit | OK |
| (a) previous R8 receipts intact | OK |
| (b) nothing outside adapter_paths imports from it | OK |
| (b) no console script or plugin entry point added (adapter_entrypoints is empty) | OK |
| (e) every protected item of the stocks domain has the same blob at the final commit | OK |
| (f) CI of the domain on the exact final commit: green push run (prompt 9.3) or the workflow_dispatch run accepted by the owner (IS-F004/IS-F005 b) | OK |

(c) suíte de conformidade verde com as wheels da integração: 87 testes, 0 falhas (`qualification/integration-stocks/RAW_LOGS/runtime/run36462320273/cleanroom-final/conformance.junit.xml` (sha256 `6ca2fc7d978e98f8…`)).

(d) vetor congelado da Etapa A pelo adapter: 11 conferências OK, 0 falhas (`qualification/integration-stocks/RAW_LOGS/runtime/run36462320273/contract-revalidation/SUMMARY.json` (sha256 `baaf5ae87f812415…`)): hash canônico sem `client_ref` igual ao do vetor (`ef6472aa058a1fbb…`, o mesmo conferido contra o resultado real da Etapa A), `client_ref` devolvido igual, payload byte-idêntico ao `show` (adapter_api).

(f) CI do domínio: ver `HOSTED_CI_REPORT.md` (IS-F004, IS-F005 e a decisão do dono, quando houver).
