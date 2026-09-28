# integration-stocks — HOSTED_CI_REPORT

Gate `HOSTED_CI` (C21; prompt da sessão 9.3: só o run de **push** cujo SHA é exatamente o commit vale). Coletado por `scripts/hosted_ci.py` (`qualification/integration-stocks/RAW_LOGS/hosted-ci/final-rc13/HOSTED_CI_SUMMARY.json` (sha256 `e6d2eddea0d04e88…`)). Core e Ops não mudaram (CI da Etapa A, HERDADO).

| Repo | Papel | Commit | Estado | Runs de push | Jobs não verdes |
|---|---|---|---|---|---|
| cain | baseline | `10744a9f1496` | verde | [CI 36359969690](https://github.com/leonardosovienski/cain/actions/runs/36359969690) success |  |
| ecosystem-predictor | baseline | `61f3ac421604` | verde | [CI 36359189276](https://github.com/leonardosovienski/ecosystem-predictor/actions/runs/36359189276) success |  |
| stocks-predictor | baseline | `61fc017256ff` | SEM PUSH VERDE | nenhum run de push |  |
| cain | final | `960fb2561470` | verde | [CI 36462212689](https://github.com/leonardosovienski/cain/actions/runs/36462212689) success |  |
| ecosystem-predictor | final | `bac1f7b7b3ae` | verde | [Full-history security regression 36454565598](https://github.com/leonardosovienski/ecosystem-predictor/actions/runs/36454565598) success; [CI 36454957031](https://github.com/leonardosovienski/ecosystem-predictor/actions/runs/36454957031) success |  |
| stocks-predictor | final | `6f857b232eaa` | SEM PUSH VERDE | nenhum run de push |  |

## stocks-predictor

O `ci.yml` do stocks-predictor dispara `push` só em `main` (intocável pela D-24 (4c)): nem a base `61fc017` nem o final_commit `6f857b2` têm run de push (IS-F004).

**Decisão do dono** (chat da sessão, 2026-09-28: "aceita o run workflow_dispatch (b) e reemite"; IS-F004 e IS-F005 `ACCEPTED_LIMITATION`): só para o stocks-predictor, o run `workflow_dispatch` do CI Pipeline no SHA exato vale como o run de C21 / prompt 9.3 e de C24.3 (f), com o job `secrets` vermelho só pelo falso positivo pré-existente fora da branch da missão.

Conferência mecânica da decisão (`qualification/integration-stocks/RAW_LOGS/hosted-ci/final-rc13/stocks_dispatch_acceptance.json` (sha256 `ffd9b2bdb6374d79…`)): **9 OK, 0 falhas**, aceito: sim.

| Conferência | Resultado |
|---|---|
| IS-F004: decisão do dono registrada (ACCEPTED_LIMITATION, palavras do dono) | OK |
| IS-F005: decisão do dono registrada (ACCEPTED_LIMITATION, palavras do dono) | OK |
| final: CI Pipeline, workflow_dispatch, headSha == final_commit | OK |
| final: jobs Quality verdes | OK |
| final: o único job não verde é secrets | OK |
| final: gitleaks acusa exatamente 1 vazamento | OK |
| final: o commit do vazamento não é ancestral do final_commit (fora da branch da missão) | OK |
| final: passos do job secrets (gitleaks vermelho; varredura da árvore e controle pulados por isso; upload final sem os arquivos deles; nenhuma outra falha) | OK |
| base: run workflow_dispatch da Etapa A no SHA exato, todos os jobs verdes | OK |

- final_commit: run [36363108348](https://github.com/leonardosovienski/stocks-predictor/actions/runs/36363108348): secrets=failure, Quality / Python 3.14=success, Quality / Python 3.13=success.
- base: run [35953418753](https://github.com/leonardosovienski/stocks-predictor/actions/runs/35953418753) (Etapa A), todos os jobs verdes.
- vazamento acusado: commit `9f7cce367817` (branches origin/evidence/prompt1-segredos-20260924), `docs/evidence/2026-09-24-prompt1-segredos.md`:57 (generic-api-key), ancestral do final_commit: não.
- com o gitleaks vermelho, não rodaram no Actions: Scan the complete tracked tree including merged code, Prove an exempted file still detects a synthetic token. Reproduzidos localmente (diagnóstico, WSL do PC 2, NÃO é CI hospedado), com o mesmo gitleaks 8.24.3 conferido pelo sha256 da release e os mesmos comandos do `ci.yml` (`qualification/integration-stocks/RAW_LOGS/hosted-ci/final-rc13/tree_scan_local.log` (sha256 `03cf75bdc56499cb…`)): varredura da árvore sem achados e controle detectou o token sintético (PASS).
