# predictor-qualification

Evidência da qualificação pré-treinamento do stack CAIN × Ecosystem × Core × Ops
× {Cripto, Brasileirão, Stocks}. Regras para agentes em `CLAUDE.md`; núcleo em
`qualification/COMMON_QUALIFICATION_CORE.md`; missões em `prompts/`.

Nada aqui é código de produção. Nenhum segredo entra neste repositório.

> MODE: CURRENT_LIVING_STATE · o bloco "Estado atual" é o estado vigente; os blocos datados abaixo dele são registro histórico, preservados como escritos.

## Estado atual (2026-10-08)

- Attestations vigentes no `main` (`attest.py check` OK nas seis; `sha256sum -c MANIFEST.sha256` OK): Etapa A `crypto` V1.2 (cripto 1.2.0rc4; Linux e Windows hospedados, D-30), `stocks` (0.3.0rc2; a integração usa a rc3), `brasileirao` (0.3.0rc3; `owner_linux` + Windows local); Etapa B `integration-crypto` rc16e (cain **0.4.13rc16** `de5db06b` + transporte 0.1.0rc7 + cripto rc4; Linux e Windows hospedados, D-31) e `integration-stocks` ciclo 7 (cain rc16 + transporte rc7 + stocks rc3 + cripto rc3; Linux e Windows hospedados, D-1) `QUALIFIED`; `integration-brasileirao` continua `QUALIFIED` na cain **0.4.13rc13** (`960fb256`, transporte rc6, brasileirão rc4): o ciclo rc16 tem só as conferências estáticas (`ATTESTATION_PARTIAL_rc16-static.json`) e o runtime depende do PC 2 do dono (D-19/D-25). Attestations substituídas ficam como `QUALIFICATION_ATTESTATION_superseded_<sha12>.json`, referenciadas por `supersedes_sha256`.
- Escopo do "qualificada": a cain rc16 é qualificada por duas das três integrações; a terceira está na rc13. `QUALIFIED` não é edge, lucro nem autorização de capital (C22).
- Supply chain (D-32, APPROVED): cada consumidor fixa as wheels do stack por `STACK_WHEELS.json` + `stack_wheels.py fetch`; os nove repositórios são públicos desde 2026-10-07 (D-35), o fetch resolve sem token e a instalação limpa a partir dos locks foi reverificada em 2026-10-08 em clones novos sem credencial. Registro: [`qualification/shared/SUPPLY_CHAIN_20261007.md`](qualification/shared/SUPPLY_CHAIN_20261007.md).
- Decisões novas desde 30/09: D-29 (pin V1.2 nas integrações), D-30 e D-31 (Windows hospedado como secundário do crypto e da integration-crypto), D-32, D-33 (merges autorizados no programa de remediação), D-34 (ciclo rc16), D-35 (visibilidade pública). Stack conjunto vigente: `ecosystem-predictor-cain/ETAPA_B_INTEGRATED_STACK_20260928.md` (cabeçalho).
- Pendências que só o dono fecha (lista única e canônica em `cain/docs/funding/FUNDING_READINESS_SOURCE_OF_TRUTH.md` §8): runtime rc16 da `integration-brasileirao` no PC 2; relacre R8 do stocks-predictor (dado privado); CR-F022 (contrato do crypto, P2).

## Registro histórico — estado em 2026-09-30 (preservado como escrito)

- Attestations vigentes: Etapa A `crypto` (V1.1, 1.2.0rc2), `brasileirao` (0.3.0rc4), `stocks` (0.3.0rc2; a integração usa a rc3) e as três integrações
  (cain 0.4.13rc13 + transporte 0.1.0rc6) `QUALIFIED` para os `final_commits` delas. O `main` de cada repositório é pós-qualificação (D-27).
- Ciclo D-27 (cain 0.4.13rc15, transporte 0.1.0rc7, cripto 1.2.0rc4) executado até onde o GitHub Actions alcança: as quatro missões estão
  `BLOCKED` em ações que só o dono pode fazer (Windows local, PC 2, pin do conjunto protegido). Estado por missão, evidência nova e pendências em [`qualification/shared/CICLO_D27_20260930.md`](qualification/shared/CICLO_D27_20260930.md); runbook da reabertura do crypto em
  [`qualification/crypto/REABERTURA_V1.2.md`](qualification/crypto/REABERTURA_V1.2.md).
- `QUALIFIED` não é edge, lucro nem autorização de capital (C22).
