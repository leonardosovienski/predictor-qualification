# QUALIFICATION_CHANGELOG — missão crypto (Etapa A)

O que a missão mudou, onde, por quê, com commit e PR. `core-predictor` e `predictor-ops`
**não** foram alterados (congelados na Etapa A).

## cripto-predictor (branch `qualification/crypto-stage-a`)

| Commit | O quê | Por quê | Teste que prova |
|---|---|---|---|
| `33fed6b` | `research_contract.py` (novo): schemas de pedido/resultado do Cripto, IDs `crypto:`, estados operacional/científico/econômico separados, invariantes de autoridade | §8/§9: domínio sem envelope; C18; §11 | `tests/test_research_domain_units.py`, `tests/conformance/*` |
| `33fed6b` | `research_admission.py` reescrito: policy V2 do operador (`LOCAL_FILE_ONLY`), sem HMAC/`verify_task`; hipóteses `crypto:H1..H9` do `scientific_state.json` nunca reabertas; cota de pendentes liberada por `mark_terminal` | CR-F007 (envelope), **CR-F003** (cota nunca liberava) | `test_pending_quota_is_released_when_the_request_terminates` (regressão), `test_admission_rejects_before_any_execution` |
| `33fed6b` | `research_execution.py` reescrito: job real do `predictor_ops` com `economic_key` (lock, heartbeat, timeout, attempt, idempotência e eventos do Ops); estado científico relido do `TrialRegistryV2` do Core; resultado determinístico com hash no journal antes da gravação; falha fechada em corrupção | CR-F006/F007/F008; §11–§12 | `tests/conformance/test_failure_recovery.py` |
| `33fed6b` | `research_worker.py`: validação temporal pelo `replay` do Core (`LookaheadError`), sinal só via `PastView`, custo líquido pelo `CostModel` congelado (2 pernas + funding), IC do bruto **e** do líquido | **CR-F004** (líquido com 1 perna, sem funding: +15 bps bruto reportava 0 bps líquido; CostModel = −36 bps), CR-F008 | `test_net_return_uses_the_frozen_cost_model_and_has_its_own_interval` (regressão), `test_future_canary_fails_closed_and_never_leaks` |
| `33fed6b` | `research_results.py`: `ResultStore` autoritativo (sem assinatura/outbox V1), relido e conferido após restart | §9 `authoritative_result_source` | `test_e2e_result_is_reread_identically_after_restart`, testes de corrupção |
| `33fed6b` | `research_runner.py` + `[project.scripts] cripto-research`: composition root que lê pedidos em arquivo | CR-F006; C24.1 entrypoint | `tests/conformance/test_import_closure.py` (componentes alcançáveis) |
| `33fed6b` | `GarimpoInvestimentos/adapters/` reservado (vazio) | C24.1 `adapter_paths` | `test_no_entrypoint_reaches_envelope_cain_or_adapter_paths`, `test_nothing_outside_adapter_paths_imports_them` |
| `33fed6b` | sai `predictor-research-protocol` do `pyproject.toml`/`uv.lock` (só remoção); `scripts/verify_installed_wheels.py` e `tests/test_shared_wheel_download_hashes.py` passam a exigir a ausência | §8; D-13 | os próprios testes |
| `33fed6b` | `tests/test_research_admission.py` e `tests/test_research_results.py` → `legacy/v1_integration/` (preservados, fora da coleta) | testavam o envelope V1 removido por mandato; equivalentes novos em `tests/conformance` | — |
| `33fed6b`→`9844976` | `.gitignore`: `output/` → `/output/` | **CR-F005**: `GarimpoInvestimentos/output` (reporter) ficava fora da wheel. Efeito colateral: um `output/` aninhado fora da raiz passa a aparecer como não rastreado | `test_repo_hygiene`, cleanroom-final (conteúdo da wheel) |
| `33fed6b` | `GarimpoInvestimentos/output/reporter.py`: só ordem de imports e formatação (o ruff não via o arquivo ignorado) | lint do CI | ruff |
| `9844976` | `research_faults.py`: injeção de falha na borda (morte real do processo; worker crash/hang/slow); ponto `before_admission_commit` | §12 FAILURE_INJECTION | `test_process_death_at_each_point_recovers_exactly_once`, `test_host_process_killed_during_ops_job_recovers_exactly_once` |
| `6f73051` | layout curto no disco (`x/`, `x/e/<16hex>`, `x/o`); raiz de estado > 120 caracteres no Windows falha logo | **CR-F013** (MAX_PATH no Windows) | `test_windows_state_root_longer_than_max_path_budget_fails_fast`, suíte Windows |
| `6f73051` | versão `1.2.0rc1`; `__version__` alinhado à distribuição | CR-F012; `publish-candidates` (versão nova, nunca sobrescrever) | `tests/test_package_version_contract.py` |
| `6f73051` | conformidade: subprocessos sem variáveis do pytest-cov | CR-F014 | job `quality` do CI |

## predictor-qualification (evidência)

- `.gitattributes`: `qualification/crypto/RAW_LOGS/** -text`, para os logs brutos ficarem byte a byte (C20).
- Workflow `crypto-ops-failure.yml` e scripts em `qualification/crypto/scripts/`.
- Vereditos `qualification/shared/SHARED-003/004/005`, e `SHARED_ISSUES.json` atualizado.

## Erros de método (preservados, não contam)

- `RAW_LOGS/baseline/windows_pytest_5fd4e1b.log`: sem `uv build` e com `CRIPTO_ROOT` fora do TEMP (CR-F002).
- `RAW_LOGS/ops-failure/run35831189005/*-wheel`: `ensurepip -q` inválido, a wheel não instalou.
- `RAW_LOGS/contract-wiring/windows_pytest_9844976.log`: árvore do clone alterada por mim
  (versão/`__init__`) **durante** a execução. Só diagnóstico; as 25 falhas revelaram a CR-F013.
