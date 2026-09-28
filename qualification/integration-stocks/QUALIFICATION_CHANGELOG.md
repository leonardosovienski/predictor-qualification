# integration-stocks — QUALIFICATION_CHANGELOG

O que o agente mudou, onde, por quê, commit e PR (C6). Sessão única (D-5), executada no **PC 2** do dono (Claude Code
desktop, comandos Linux no WSL Ubuntu 24.04 só para desenvolvimento, diagnóstico e recibos R8). Toda afirmação de gate
cita arquivo de evidência + sha256 no `GATES.json` / attestation.

## 2026-09-27 — C0 ABORTED (histórico)

| Onde | O quê | Por quê | Commit / PR |
|---|---|---|---|
| `qualification/integration-stocks/FINDINGS.json` (chave `c0`), `RAW_LOGS/c0/`, `scripts/c0_*` | C0 ABORTED: integration-crypto ainda não QUALIFIED no main | regra única do pré-voo | #58, #59 |

## 2026-09-27/28 — C0, D-24, freeze-parameters, baseline

| Onde | O quê | Por quê | Commit / PR |
|---|---|---|---|
| `qualification/DECISIONS.json` | acrescenta a D-24 (só ela), gerada por `scripts/add_d24.py` com conferência byte a byte das 23 anteriores | decisão explícita do dono no prompt da sessão (5.5) | `fc9f01b`, PR #63 (mergeado) |
| `RAW_LOGS/c0/` + `scripts/c0_preconditions.py` | pré-voo 4.1–4.7 refeito em cada mudança do main: 9937894 e 6af1e32 com 0 falhas; o script passa a baixar cada `final_wheel` de cain/ecosystem da integration-crypto e conferir o sha256, e confere as SHARED contra a pilha completa | C0 + pré-voo da sessão | este PR |
| `FROZEN_PARAMETERS.json` + `scripts/freeze_parameters.py`, `FROZEN_VECTORS.json` + `scripts/build_vectors.py` + `fixtures/`, `FAILURE_MATRIX.json`, `QUALIFICATION_PROFILE_INTEGRATION_STOCKS_V1.json` | parâmetros, vetores, matriz de falhas e perfil de soak congelados; configuração da DecisionPolicy do Stocks lida de 61fc017 (SHA completo) e do contrato; limites do framework achados antes do congelamento (IS-F002, IS-F003) | C15 (primeira fase); mostrados ao dono neste PR antes de qualquer execução de gate | este PR |
| `STACK_BASELINE.json` + `scripts/mission_baseline.py`, `RAW_LOGS/baseline/` | baseline com o coletor do STACK_BASELINE_V2.0 sem mudança, cain/ecosystem nos final_commits da integration-crypto; a primeira comparação (todos os campos) acusou só o estado remoto do cripto (main e release rc3 novos) e ficou preservada em `mission_baseline_run1_strict.log`; o script passou a separar campos de estado remoto dos da base | C3 | este PR |
| `FINDINGS.json`, `GATES.json`, `scripts/{attest,findings_init}.py`, `ATTESTATION_PARTIAL_{freeze-parameters,baseline}.json` | achados IS-F001..IS-F004 (P2) acrescentados preservando o registro do C0; ledger de gates; parciais validados no schema | C6, C7, C8 | este PR |
| `tools/pyproject.toml`, `tools/uv.lock` | ferramentas da missão: protocolo 2.0.0rc2 da release congelada (sha256 no lock) + jsonschema | venvs só de uv.lock | este PR |
