# REABERTURA V1.2 — missão crypto (D-27, C24.4, C14)

Por que reabriu: o `main` do `cripto-predictor` avançou depois do `final_commit` da Etapa A (`341d270`, 1.2.0rc2)
com pesquisa fora dos `adapter_paths` (PRs #128–#134) e com as correções de 2026-09-29 (gate de identidade de release,
CI, `test_distribution_security`), publicados como pré-release **v1.2.0rc4** (`21f8b182`, wheel `32a4bd6d…`). Pelo C14
("código do domínio depois de `cleanroom-final`") e pelo C24.4, a Etapa A do crypto reabre para esse alvo. Decisão
delegada pelo dono (D-27). Nenhum parâmetro, vetor, perfil ou limiar congelado mudou (`FROZEN_PARAMETERS.json`,
`FROZEN_VECTORS.json`, `QUALIFICATION_PROFILE_CRYPTO_V1.json`, `FAILURE_MATRIX.json`, `AUTHORITY_STATE_MATRIX.json`
inalterados; os blobs da suíte de conformidade em `21f8b182` são os mesmos de `341d270`).

## O que a sessão de 2026-09-29 executou

| Fase V1.2 | Onde | Evidência bruta |
|---|---|---|
| baseline | coletor (git + API pública) | `RAW_LOGS/v1.2/baseline/collect.log`, `STACK_BASELINE_V1.2.json`, `shared/STACK_BASELINE_V1.2.json` |
| truth-map | `truth_map.py` em `21f8b182` | `RAW_LOGS/v1.2/truth-map/`, `RAW_LOGS/v1.2/protected/`, `PROTECTED_SET_V1.2.json` |
| publish-candidates | release v1.2.0rc4 já publicada pelo workflow Release (build duplo) | `runtime_target.json`, `RAW_LOGS/v1.2/hosted-ci/jobs_cripto-predictor_36643518795.json` |
| cleanroom-final, e2e, idempotency-failure, soak sintético | GitHub Actions `ubuntu-latest` (`crypto-reopening.yml`, run 36646241688, job `runtime linux-primary`) | `RAW_LOGS/v1.2/run36646241688/runtime-linux-primary/` |
| e2e real, casos A/B/C, science, soak real (D-16) | GitHub Actions `ubuntu-latest` (mesmo run, job `d16`) | `RAW_LOGS/v1.2/run36646241688/d16/` |
| windows-latest (informação adicional) | GitHub Actions `windows-latest` (mesmo run) | `RAW_LOGS/v1.2/run36646241688/runtime-windows-latest/` |
| hosted-ci, secrets | API pública + `scan_secrets.py` | `RAW_LOGS/v1.2/hosted-ci/`, `RAW_LOGS/v1.2/secrets/` |

A saída de cada job foi devolvida pelo próprio job numa branch `crypto/raw-36646241688-<job>` deste repositório
(o ambiente da sessão não baixa artefatos do Actions) e copiada sem edição para `RAW_LOGS/v1.2/run36646241688/`,
com `SHA256SUMS` por job. Números: `EVIDENCE_NUMBERS_V1.2.json` (`scripts/evidence_numbers_v12.py`).

## O que falta e só o dono faz: `WINDOWS_SMOKE`

O secundário do crypto é o Windows local (D-3): `C:\Cripto\qualificacao\runtime\`. No clone de qualificação
`C:\Cripto\qualificacao\cripto-predictor` (ou no checkout deste repositório), com o `main` deste repositório já
contendo a V1.2:

```bash
# Git Bash, Python 3.13 e uv da qualificação (C:\QUALIFICACAO\tools), como na V1.1
bash qualification/crypto/scripts/windows_runtime.sh <out_dir>   # lê qualification/crypto/runtime_target.json (rc4)
```

Depois, numa branch nova: copiar `<out_dir>` sem editar para `qualification/crypto/RAW_LOGS/v1.2/windows-local/`,
rodar `python qualification/crypto/scripts/evidence_numbers_v12.py --run run36646241688` (acrescentar a seção do
Windows), fechar `WINDOWS_SMOKE` no `GATES.json` (`PASS` ou `FAIL` pelos mesmos critérios da V1.1: E2E real 10/10 +
restart + releitura, conformidade 48/48), `attest.py final` (a attestation V1.1 é preservada como
`QUALIFICATION_ATTESTATION_superseded_<sha12>.json` e a nova aponta para ela em `supersedes_sha256`), `attest.py check`,
`QUALIFICATION_CHANGELOG.md`, PR.

Alternativa que exige decisão nova em `DECISIONS.json`: aceitar o job `windows-latest` do Actions como secundário do
crypto (como a D-1 faz para o Stocks). O run 36646241688 já tem essa evidência; a decisão é do dono, não do agente
(algo congelado pela D-3 precisaria mudar).

## Estado terminal desta sessão

`BLOCKED` (C7.3): nenhum gate `FAIL`, `WINDOWS_SMOKE` `NOT_RUN` com `note` `BLOCKED: …`. Só parciais
(`ATTESTATION_PARTIAL_v1-2-*.json`, `result = IN_PROGRESS`). A `QUALIFICATION_ATTESTATION.json` vigente continua sendo
a V1.1 (`QUALIFIED` para `341d270` / 1.2.0rc2), válida só para aqueles `final_commits` (C22). Consequência para a
Etapa B: `integration-crypto` só pode citar uma attestation `QUALIFIED` do crypto (C7.1 regra 7); enquanto a V1.2 não
fechar, a integração com a cripto 1.2.0rc4 fica com os mesmos parciais (ver `qualification/integration-crypto/`).

## Fechamento (2026-10-07, D-30)

A decisão D-30 (delegada pelo dono em 2026-09-30, `qualification/shared/CICLO_D27_20260930.md` §5, escrita em 2026-10-07) aceita o
job `windows-latest` × 3.13 do run 36646241688 como ambiente secundário do crypto. `scripts/v12_gates.py windows-smoke-d30` fecha
`WINDOWS_SMOKE` com a evidência já coletada em `RAW_LOGS/v1.2/run36646241688/runtime-windows-latest/` (E2E pelo entrypoint instalado
com restart e releitura, conformidade, identidade das wheels; números em `EVIDENCE_NUMBERS_V1.2.json`), e `attest.py final` emite a
attestation V1.2 **QUALIFIED** para `21f8b182` / 1.2.0rc4. A V1.1 (`QUALIFIED` para `341d270` / rc2) fica preservada como
`QUALIFICATION_ATTESTATION_superseded_2b1491a03a6b.json`; a nova aponta para ela em `supersedes_sha256`. O Windows local do dono
continua admitido como evidência adicional (D-3), não é mais o único secundário. Estado terminal: `QUALIFIED`.
