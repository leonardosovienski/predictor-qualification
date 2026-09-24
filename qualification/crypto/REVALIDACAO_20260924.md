# REVALIDACAO_20260924 — missão crypto (reexecução completa depois do fechamento da D-16)

Pedido do dono: "confere e executa tudo". Reexecução de todos os gates que podem ser reexecutados, no alvo
congelado (cripto `341d270`, wheel `6e62f67f…`, core 3.2.1, ops 4.2.2rc1), sem mudar
parâmetro, vetor, perfil ou limiar. **Não altera gate nem attestation**: é reconfirmação. Números gerados por
`scripts/revalidation_summary.py` a partir de `RAW_LOGS/revalidacao-20260924/` (também em `revalidation_numbers.json`).

## D-16 (dados reais, Linux primário): run 36003570075

- `where=github_actions`, `done`=True, `SETUP FAIL`=False, `BLOCKED`=False; exits {'e2e_real': 0, 'e2e_cases': 0, 'science': 0, 'soak_real': 0, 'conformance': 0}.
- E2E real all_ok=True; casos A/B/C all_ok=True; conformidade {'tests': 48, 'failures': 0, 'errors': 0, 'skipped': 0}.
- Soak real: 77 chamadas, falhas {'after_admission': 1, 'after_ops': 1, 'before_admission_commit': 4, 'before_ops': 1, 'during_materialization': 1, 'during_result_write': 3, 'host_killed_during_ops_job': 3, 'none': 57, 'ops_worker_crash': 3, 'ops_worker_hang': 3}, corrupções 3 (falha fechada em 3); 43/43 resultados, perdidos 0, inesperados 0, violações 0, releitura divergente 0, SUCCEEDED por job ≤ 1, reconcile exit 5 (estranhos 0, não acusados 0), `zero_tolerance_ok=True`.
- Econômico: {'gross_return_bps': -45, 'gross_ci_bps': [-214, 112], 'net_return_bps': -83, 'net_ci_bps': [-253, 76], 'sample_size': 52, 'scientific_state': 'INCONCLUSIVE', 'economic_state': 'NO_EDGE'}. Controles: {'future_injection': 0, 'temporal_ablation': 0, 'shuffled_supported': 3, 'canary_leaks': 0}.
- Dados: 45/45 conferidos pelo `.CHECKSUM`.
- Igual ao run definitivo 35978221282, campo a campo: {'e2e_real': True, 'e2e_cases': True, 'conformance': True, 'economic': True, 'controls': True, 'data': True, 'soak': True, 'exits': True}.

## Runtime suportado (cleanroom, identidade, conformidade, suíte pela wheel, E2E, soak sintético): run36003574024

- **linux-primary**: done=True; conformidade 48 testes, falhas 0, skip 0; suíte pela wheel 1664 testes, falhas 17 (as mesmas da V1.1: True; CR-F016); E2E all_ok=True; wheels {'predictor-core': 'sha256=10ef42f34ace8bb2df5f83ff7de2ceec79b035a25ea0a690e8942bd60d2fb4e3', 'predictor-ops': 'sha256=0be70bfbb2437dfb080baceb9af41043a09d03b15a358903b8bd7007f5f169b3', 'cripto-predictor': 'sha256=6e62f67f0779aef7e913d34b4d3d3d6ed5f88ad882e8fa8372f54c4ab59bc8ee'}.
  Soak sintético: 80 chamadas, 46 resultados, perdidos 0, violações 0, corrupções 3, `zero_tolerance_ok=True`.
- **windows-latest**: done=True; conformidade 48 testes, falhas 0, skip 0; suíte pela wheel 1664 testes, falhas 17 (as mesmas da V1.1: True; CR-F016); E2E all_ok=True; wheels {'predictor-core': 'sha256=10ef42f34ace8bb2df5f83ff7de2ceec79b035a25ea0a690e8942bd60d2fb4e3', 'predictor-ops': 'sha256=0be70bfbb2437dfb080baceb9af41043a09d03b15a358903b8bd7007f5f169b3', 'cripto-predictor': 'sha256=6e62f67f0779aef7e913d34b4d3d3d6ed5f88ad882e8fa8372f54c4ab59bc8ee'}.

## Ops (SHARED-003/004/005): run36003577891

- Mesmos números da V1.1 em todos os ambientes: True.
- Corrida de lock (SHARED-005): {'ops-failure-v1-1-linux-source': {'runs': 50, 'exit_0': 50}, 'ops-failure-v1-1-linux-wheel': {'runs': 50, 'exit_0': 50}, 'ops-failure-v1-1-windows-latest-wheel': {'runs': 50, 'exit_0': 50}}.

- ops-failure-v1-1-linux-source: shared003_test {'executions': 10, 'executions_all_passed': 10, 'executions_with_failure': 0}; shared004_tests {'executions': 3, 'executions_all_passed': 3, 'executions_with_failure': 0}; full_tests_v2 {'executions': 1, 'executions_all_passed': 1, 'executions_with_failure': 0}; probe_real_tree {'n': 3, 'killed_tree_and_truncated': 3, 'child_alive_after': 0, 'grandchild_alive_after': 0}; probe_startup {'n': 20, 'over_0_2s': 0}; probe_test_exact {'n': 10, 'assertions_pass': 10}; probe_a_b_delay {'n': 10, 'assertions_pass': 10}
- ops-failure-v1-1-linux-wheel: shared003_test {'executions': 10, 'executions_all_passed': 10, 'executions_with_failure': 0}; shared004_tests {'executions': 3, 'executions_all_passed': 0, 'executions_with_failure': 3}; full_tests_v2 {'executions': 1, 'executions_all_passed': 0, 'executions_with_failure': 1}; probe_real_tree {'n': 3, 'killed_tree_and_truncated': 3, 'child_alive_after': 0, 'grandchild_alive_after': 0}; probe_startup {'n': 20, 'over_0_2s': 0}; probe_test_exact {'n': 10, 'assertions_pass': 10}; probe_a_b_delay {'n': 10, 'assertions_pass': 10}
- ops-failure-v1-1-windows-latest-wheel: shared003_test {'executions': 3, 'executions_all_passed': 3, 'executions_with_failure': 0}; shared004_tests {'executions': 1, 'executions_all_passed': 0, 'executions_with_failure': 1}; full_tests_v2 {'executions': 1, 'executions_all_passed': 0, 'executions_with_failure': 1}; probe_real_tree {'n': 3, 'killed_tree_and_truncated': 3, 'child_alive_after': 0, 'grandchild_alive_after': 0}; probe_startup {'n': 20, 'over_0_2s': 0}; probe_test_exact {'n': 10, 'assertions_pass': 10}; probe_a_b_delay {'n': 10, 'assertions_pass': 10}

## CI hospedado (reexecutado nos commits do baseline e finais; `gh run rerun`)

| Repo | Commit | Run | Tentativa | Evento | Resultado | Jobs | pytest |
|---|---|---|---|---|---|---|---|
| core-predictor | `5a08415` | 35823003554 | 2 | push | success | Python 3.13=success, Build and test wheel outside checkout=success, Python 3.14 (experimental)=success, Security and distribution audit=success | 278 passed |
| cripto-predictor | `5fd4e1b` | 35822807920 | 2 | push | success | python-314-experimental=success, all-extras=success, container=success, quality=success | 1583 passed, 7 skipped; 1618 passed |
| cripto-predictor | `341d270` | 35906112873 | 2 | push | success | all-extras=success, python-314-experimental=success, container=success, quality=success | 1629 passed, 7 skipped; 1664 passed |
| cripto-predictor | `341d270` | 35925694691 | 2 | push | success | container=success, python-314-experimental=success, all-extras=success, quality=success | 1629 passed, 7 skipped; 1664 passed |
| predictor-ops | `7bd99eb` | 35823068759 | 2 | push | success | container=success, test (ubuntu-latest, 3.14)=success, test (windows-latest, 3.13)=success, test (ubuntu-latest, 3.13)=success | 1 passed; 2 passed; 87 passed |
| predictor-ops | `9831b0d` | 35905393899 | 2 | pull_request | success | container=success, test (ubuntu-latest, 3.14)=success, test (windows-latest, 3.13)=success, test (ubuntu-latest, 3.13)=success | 1 passed; 2 passed; 88 passed |
| predictor-ops | `9831b0d` | 35905678198 | 2 | push | success | container=success, test (ubuntu-latest, 3.13)=success, test (ubuntu-latest, 3.14)=success, test (windows-latest, 3.13)=success | 1 passed; 2 passed; 88 passed |

O run Release do predictor-ops **não** foi reexecutado (publicaria asset; nunca sobrescrever).

## Verificações determinísticas (PC 2, `local/`)

- `attestations.log`:
  - attest.py check QUALIFICATION_ATTESTATION.json: OK
  - attest.py check ATTESTATION_PARTIAL_d16.json: OK
  - ATTESTATION_PARTIAL_baseline.json                          f4b22ee IN_PROGRESS   checked=  8 problemas=1
  - ATTESTATION_PARTIAL_cleanroom-baseline.json                42cbef8 IN_PROGRESS   checked= 17 problemas=0
  - ATTESTATION_PARTIAL_cleanroom-final.json                   cd7e71d IN_PROGRESS   checked=102 problemas=3
  - ATTESTATION_PARTIAL_contract-sign-off.json                 800d4d1 IN_PROGRESS   checked=104 problemas=0
  - ATTESTATION_PARTIAL_contract-wiring.json                   cd7e71d IN_PROGRESS   checked=102 problemas=3
  - ATTESTATION_PARTIAL_d16.json                               7359b9f IN_PROGRESS   checked=110 problemas=0
  - ATTESTATION_PARTIAL_e2e.json                               cd7e71d IN_PROGRESS   checked=102 problemas=3
  - ATTESTATION_PARTIAL_freeze-parameters.json                 dca05e9 IN_PROGRESS   checked=  4 problemas=0
  - ATTESTATION_PARTIAL_hosted-ci.json                         cd7e71d IN_PROGRESS   checked=102 problemas=3
  - ATTESTATION_PARTIAL_idempotency-failure.json               cd7e71d IN_PROGRESS   checked=102 problemas=3
  - ATTESTATION_PARTIAL_ops-failure.json                       42cbef8 IN_PROGRESS   checked= 17 problemas=0
  - ATTESTATION_PARTIAL_publish-candidates.json                cd7e71d IN_PROGRESS   checked=102 problemas=3
  - ATTESTATION_PARTIAL_science.json                           cd7e71d IN_PROGRESS   checked=102 problemas=3
  - ATTESTATION_PARTIAL_soak.json                              cd7e71d IN_PROGRESS   checked=102 problemas=3
  - ATTESTATION_PARTIAL_truth-map.json                         42cbef8 IN_PROGRESS   checked= 17 problemas=0
  - ATTESTATION_PARTIAL_v1-1-attestation.json                  ed5375d IN_PROGRESS   checked=109 problemas=0
  - ATTESTATION_PARTIAL_v1-1-baseline.json                     ed5375d IN_PROGRESS   checked=109 problemas=0
  - ATTESTATION_PARTIAL_v1-1-cleanroom-final.json              ed5375d IN_PROGRESS   checked=109 problemas=0
  - ATTESTATION_PARTIAL_v1-1-contract-wiring.json              ed5375d IN_PROGRESS   checked=109 problemas=0
  - ATTESTATION_PARTIAL_v1-1-e2e.json                          ed5375d IN_PROGRESS   checked=109 problemas=0
  - ATTESTATION_PARTIAL_v1-1-hosted-ci.json                    ed5375d IN_PROGRESS   checked=109 problemas=0
  - ATTESTATION_PARTIAL_v1-1-idempotency-failure.json          ed5375d IN_PROGRESS   checked=109 problemas=0
  - ATTESTATION_PARTIAL_v1-1-ops-failure.json                  ed5375d IN_PROGRESS   checked=109 problemas=0
  - ATTESTATION_PARTIAL_v1-1-publish-candidates.json           ed5375d IN_PROGRESS   checked=109 problemas=0
  - ATTESTATION_PARTIAL_v1-1-science.json                      ed5375d IN_PROGRESS   checked=109 problemas=0
  - ATTESTATION_PARTIAL_v1-1-soak.json                         ed5375d IN_PROGRESS   checked=109 problemas=0
  - ATTESTATION_PARTIAL_v1-1-windows-smoke.json                ed5375d IN_PROGRESS   checked=109 problemas=0
  - ATTESTATION_PARTIAL_windows-smoke.json                     cd7e71d IN_PROGRESS   checked=102 problemas=3
  - QUALIFICATION_ATTESTATION.json                             7359b9f QUALIFIED     checked=110 problemas=0
  - QUALIFICATION_ATTESTATION_superseded_eb3e79f48c7d.json     800d4d1 NOT_QUALIFIED checked=104 problemas=0
- `blockers.log`:
  - abertos por severidade: {'P2': 8} | attestation counts: {'P0': 0, 'P1': 0, 'P2': 8}
  - abertos: [('CR-F001', 'P2'), ('CR-F010', 'P2'), ('CR-F011', 'P2'), ('CR-F016', 'P2'), ('CR-F017', 'P2'), ('CR-F018', 'P2'), ('CR-F020', 'P2'), ('CR-F021', 'P2')]
- `domain_contract.log`:
  - contrato origin/main: 0831fe3db2b7ca41a26ff7665f93c07b0edda3c937ac4ce83fe0e96720a9eb55
  - contrato branch:      0831fe3db2b7ca41a26ff7665f93c07b0edda3c937ac4ce83fe0e96720a9eb55
  - attestation domain_contract_sha256: 0831fe3db2b7ca41a26ff7665f93c07b0edda3c937ac4ce83fe0e96720a9eb55
  - último commit do contrato no main: cd7e71d 2026-09-23 13:13:01 -0300 crypto: cleanroom-final, e2e, falhas, ciência, windows-smoke, hosted-ci e soak (parciais)
- `evidence_numbers_repro.log`:
  - evidence_numbers EVIDENCE_NUMBERS (invocação padrão, clone descartável) exit=0
  - EVIDENCE_NUMBERS.json: reproduz byte a byte
  - evidence_numbers EVIDENCE_NUMBERS_V1.1 exit=0
  - EVIDENCE_NUMBERS_V1.1.json: reproduz byte a byte
  - evidence_numbers EVIDENCE_NUMBERS_D16 exit=0
  - EVIDENCE_NUMBERS_D16.json: reproduz byte a byte
  - exit=0
  - gerado: OPS_FAILURE_SUMMARY.json
  - OPS_FAILURE_SUMMARY (V1.1): reproduz byte a byte
- `protected_set.log`:
  - regenerado == PROTECTED_SET.json (itens e blobs): True | itens: 1382 1382
  - commit 341d270: 1382/1382 blobs iguais; alterados/ausentes: []
  - commit 174573d: 1382/1382 blobs iguais; alterados/ausentes: []
  - no 341d270 e fora do conjunto: [] | do conjunto e ausentes no 341d270: []
- `scientific_state.log`:
  - == 341d270
  - hipóteses: {'H1': 'CLOSED_NO_GO', 'H2': 'CLOSED_NO_GO', 'H3': 'CLOSED_NO_GO', 'H4': 'CLOSED_INSUFFICIENT_SAMPLE', 'H5': 'CLOSED_NO_GO', 'H6': 'CLOSED_INSUFFICIENT_SAMPLE', 'H7': 'REGISTERED_NOT_ACTIVATED', 'H8': 'REGISTERED_NOT_ACTIVATED', 'H9': 'CLOSED_INSUFFICIENT_SAMPLE'}
  - igual ao esperado do prompt §5: True | frozen_families: ['funding_oi_hmm_v3'] (esperado ['funding_oi_hmm_v3']) | capital_authorized: False
  - == 174573d
  - hipóteses: {'H1': 'CLOSED_NO_GO', 'H2': 'CLOSED_NO_GO', 'H3': 'CLOSED_NO_GO', 'H4': 'CLOSED_INSUFFICIENT_SAMPLE', 'H5': 'CLOSED_NO_GO', 'H6': 'CLOSED_INSUFFICIENT_SAMPLE', 'H7': 'REGISTERED_NOT_ACTIVATED', 'H8': 'REGISTERED_NOT_ACTIVATED', 'H9': 'CLOSED_INSUFFICIENT_SAMPLE'}
  - igual ao esperado do prompt §5: True | frozen_families: ['funding_oi_hmm_v3'] (esperado ['funding_oi_hmm_v3']) | capital_authorized: False
- `uv_lock_check.log`:
  - HEAD=341d270e4d709150c581c3cd93f4518d483009eb alterações=0
  - uv 0.12.18 (x86_64-unknown-linux-gnu)
  - Using CPython 3.13.15
  - Resolved 79 packages in 0.91ms
  - exit=0
  - Using CPython 3.13.15
  - Resolved 79 packages in 654ms
  - exit=0
  - sha256 uv.lock: 9ab423a06086989a5108ec6f91383e4f8991884fd41187dfdea5e5d9487cc6b7

## Não reexecutável aqui

- Windows local (secundário, D-3): é o PC 1 (`C:\Cripto\qualificacao\runtime\`). No PC 2 as regras proíbem escrever em
  `/mnt/c`. A evidência de `WINDOWS_SMOKE` continua a da V1.1; o `windows-latest` acima é informação adicional.
