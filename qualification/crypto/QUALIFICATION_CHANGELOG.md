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
| `2bafad9` | teste de corrupção usa diretório temporário irmão (limite de raiz no Windows) | a guarda da CR-F013 recusou o próprio teste aninhado | suíte Windows 1663 passed |
| `2bc63eb` | `execute()`: o resultado autoritativo é devolvido **antes** de revalidar a policy | **CR-F015** (duplicata depois de mudança de policy voltava REJECTED); reproduzido em 2bafad9, mesma prova passa depois | `test_duplicate_after_policy_change_returns_the_stored_result` |

**final_commit:** `2bc63ebdc47f93661a4f37cb988b06939de060fe`. Release pré-release
[`v1.2.0rc1`](https://github.com/leonardosovienski/cripto-predictor/releases/tag/v1.2.0rc1),
wheel `1f76b8c4dbcb2ca145c053a7dc84d98d30c49859d95c1e1a78ad4d5916b3df49` (build reprodutível).
PR: [cripto-predictor#126](https://github.com/leonardosovienski/cripto-predictor/pull/126).

## predictor-qualification (evidência)

- `.gitattributes`: `qualification/crypto/RAW_LOGS/** -text`, para os logs brutos ficarem byte a byte (C20).
- Workflow `crypto-ops-failure.yml` e scripts em `qualification/crypto/scripts/`.
- Vereditos `qualification/shared/SHARED-003/004/005`, e `SHARED_ISSUES.json` atualizado.

## Erros de método (preservados, não contam)

- `RAW_LOGS/baseline/windows_pytest_5fd4e1b.log`: sem `uv build` e com `CRIPTO_ROOT` fora do TEMP (CR-F002).
- `RAW_LOGS/ops-failure/run35831189005/*-wheel`: `ensurepip -q` inválido, a wheel não instalou.
- `RAW_LOGS/contract-wiring/windows_pytest_9844976.log`: árvore do clone alterada por mim
  (versão/`__init__`) **durante** a execução. Só diagnóstico; as 25 falhas revelaram a CR-F013.
- `RAW_LOGS/cleanroom-final/run35883218077`: árvore de testes sem `scripts/` e raiz temporária
  longa no windows-latest (harness); refeito no run 35885023422.
- O commit `b3acbc2` do repo de evidência gravou os logs de `RAW_LOGS/windows-smoke/local/`
  enquanto o runtime Windows ainda escrevia neles. O commit seguinte traz a versão final; nada
  foi editado à mão.

## V1.1 — correção da SHARED-005 (D-17)

| Repo | Commit | O quê | Teste |
|---|---|---|---|
| predictor-ops | `9831b0d` (PR #26) | `_mutation_guard`: inicialização da guarda por descritor sem buffer; escrita recusada espera no laço de lock. Versão 4.2.2rc1; contrato de versão do CHANGELOG aceita pré-release PEP 440 | `test_empty_guard_locked_by_another_process_waits_instead_of_crashing` (falha antes, passa depois); corrida 50/50 |
| cripto-predictor | `341d270` | Ops 4.2.2rc1 (`>=4.2.2rc1,<5`, lock), versão 1.2.0rc2; `test_core_integrity`/`verify_installed_wheels` exigem a wheel nova | suíte Windows 1664/1664; CI verde |

Releases pré-release: predictor-ops `v4.2.2rc1` (asset oficial do workflow Release, `0be70bfb…`), cripto-predictor `v1.2.0rc2` (`6e62f67f…`).

Notas de método: o workflow Release do Ops substituiu, com o mesmo conteúdo e outros carimbos de data, os assets que enviei manualmente um minuto antes; o asset canônico é o do workflow (CORE_IDENTITY_REPORT §3); a suíte Windows de `341d270` perdeu 1 teste para o Modern Standby do host (CR-F018) e foi refeita (1664/1664); de novo um log em andamento (`windows_pytest_341d270_run2.log`) entrou num commit antes de terminar, e a versão final vem no commit seguinte.

## D-16 — dados reais no Linux primário (2026-09-24, sessão da noite no PC 2)

Nenhum código de produto mudou (`cripto-predictor`, `core-predictor` e `predictor-ops` intocados; alvo = `runtime_target.json`: cripto `341d270`, wheel `6e62f67f…`). Nenhum parâmetro, vetor, perfil ou limiar mudou.

| Repo | Commit | O quê | Por quê | Prova |
|---|---|---|---|---|
| predictor-qualification | `c5d627a`, `8693f5d` ([PR #17](https://github.com/leonardosovienski/predictor-qualification/pull/17)) | kit: `soak.py` executa as 6 classes de falha do perfil (entram "host do Ops morto durante o job" e "corrupção do arquivo de resultado", como na `FAILURE_MATRIX`); `d16_finalize.py` exige ≥ 3 execuções de cada classe para `SOAK`; `evidence_numbers.py --d16`; runbook | **CR-F019** (P1): o soak executava 4 das 6 classes, e o finalize fecharia `SOAK` sem essa cobertura | `RAW_LOGS/d16-conferencia/finalize_ensaio_runs.log` (run 1 → SOAK FAIL; run 2 → PASS) |
| predictor-qualification | `ec250a4` e o commit do fechamento | saídas brutas dos dois runs; `scripts/d16_crosscheck.py`; conferências (`RAW_LOGS/d16-conferencia/`); `d16_finalize.py`; `EVIDENCE_NUMBERS_D16.json`; CR-F019..F021; seções D-16 do `SOAK_REPORT` e do `SCIENTIFIC_INTEGRITY_REPORT`; parcial `d16` e attestation final | runbook §3 | `attest.py check` OK |

Runs do `crypto-d16.yml` (ubuntu-latest, Python 3.13):

- [35976569248](https://github.com/leonardosovienski/predictor-qualification/actions/runs/35976569248): `main` 3983de1, kit antigo. Execução completa, mas o soak não cobre o perfil (CR-F019). Preservado em `RAW_LOGS/d16/35976569248/`; **não fecha gate**.
- [35978221282](https://github.com/leonardosovienski/predictor-qualification/actions/runs/35978221282): branch `cripto/d16-20260924` 8693f5d (kit corrigido). **Definitivo**: aceito pelo `d16_finalize.py` (D-16, commit e wheel conferidos).

Conferências da sessão (`RAW_LOGS/d16-conferencia/`): as 28 attestations conferidas no próprio commit (10 parciais V1.0 com divergência histórica, **CR-F020**); wheels das releases × registrado × source `341d270`; dados de cada run × `.CHECKSUM` × cópia conferida do pendrive (45/45); varredura de segredos; suíte do `cripto-predictor` no PC 2 (`pc2-diagnostico/`, só diagnóstico). Lacuna do `attest.py check`: **CR-F021**.

Resultado: **`QUALIFIED`**, com 31/31 gates `PASS`, P0 = P1 = 0 e P2 = 8 abertos. Attestation `QUALIFICATION_ATTESTATION.json` sha256 `565326d367a5d2d8d229392e68d49182009e3c25bbfa0671dc4662ca9e3a4c27`, com `supersedes_sha256 = eb3e79f4…`; a anterior foi preservada byte a byte como `QUALIFICATION_ATTESTATION_superseded_eb3e79f48c7d.json`. `QUALIFIED` não é edge nem autoriza capital (C22): com dados reais, o líquido foi −83 bps/semana, `INCONCLUSIVE`/`NO_EDGE`.

## Núcleo v2.1 (D-19) — attestation reemitida (2026-09-24)

A D-19 mudou o núcleo para a v2.1 (`owner_linux` como Linux primário só para dado privado) e mandou, pelo C14 "Núcleo (versão)", que o crypto revalide e reemita a attestation com o novo `common_core_sha256`, **sem refazer fases**.

- Revalidação (`RAW_LOGS/v2.1/revalidacao_nucleo_v2.1.log`): a attestation `565326d3…` é válida no schema v2.1 (`4b78f1fa…`) e só falha na C7.1 regra 6 (núcleo `50e8f498…` × vigente `a3b4b7bb…`). O crypto não usa `owner_linux`: o Linux primário é o `github_actions`.
- `scripts/attest.py`: `CORE_SHA` = v2.1. `common_core_version` e `attestation_version` ficam `"2.0"`, porque o schema v2.1 ainda os fixa com `const`.
- `565326d3…` preservada byte a byte como `QUALIFICATION_ATTESTATION_superseded_565326d367a5.json`. Nova fase `v2-1-core` (`ATTESTATION_PARTIAL_v2-1-core.json`) e nova `QUALIFICATION_ATTESTATION.json` sha256 `ec22a085125a08c6c102c6f0d48d6ef623c5ebbd21da0629b47d96ae9765fc69` (`supersedes_sha256 = 565326d3…`). Continua `QUALIFIED`: 31/31 PASS, P0 = P1 = 0, P2 = 8. Gates, evidências, ambientes, wheels, vereditos e contagens estão idênticos; muda só o sha do núcleo, a data, o `supersedes` e a fase.
- Não mudam (registro histórico do núcleo em vigor quando foram gravados): `FROZEN_PARAMETERS.json`, `STACK_BASELINE.json` e `STACK_BASELINE_V1.1.json` continuam citando o núcleo v2.0.
