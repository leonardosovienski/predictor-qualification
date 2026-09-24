# PREPARAR O ENVELOPE V2 (Rev 8 — enxuto)

Núcleo: `qualification/COMMON_QUALIFICATION_CORE.md` v2.3, sha256 =
`beaa5feed193356f554922439936ad401c8f177bfd18d8864ca329fae94216fc`. Um único agente, sem subagentes. Tudo por PR; o dono aprova
fazendo merge. Você pode publicar releases pré-release (`rc`) dos pacotes do
protocolo depois que o PR da especificação estiver no `main`.

## Pré-condições

* `qualification/{crypto,brasileirao,stocks}/QUALIFICATION_ATTESTATION.json`
  com `result = QUALIFIED` e os três `DOMAIN_RESEARCH_CONTRACT.json` no `main`.
* Nenhum issue bloqueante em `qualification/shared/SHARED_ISSUES.json`.

## O que produzir

1. **Especificação** `ecosystem-predictor/packages/research-protocol/SPEC_V2.md`
   + JSON Schemas de `ResearchTaskV2` e `ResearchResultV2`, a partir dos três
   contratos (C24):
   * payload de domínio da task = `request_schema` do contrato, identificado
     por `domain_prefix`; o do result = `result_schema` (core/ops/domain facts);
   * envelope: versão, domínio, IDs qualificados (C18), correlação
     (research_id, task_id, result_id, `client_ref`), hash do payload, timestamps.
     Autenticação de transporte (HMAC) **não é requisito** nesta qualificação
     (tudo roda local); se o pacote atual já tiver, pode manter, mas não vira gate;
   * serialização canônica e rejeição fail closed (schema, versão, campo desconhecido);
   * nada que exija mudança num domínio fora dos `adapter_paths` (D-12). Se for
     inevitável, **pare** e descreva a reabertura (C24.4).
2. **Tabela de mapeamento** V2 ↔ contrato por domínio: todo campo obrigatório é
   representável sem perda.
3. **Builds reproduzíveis** (2×, mesmo sha256) do `predictor-research-protocol`
   V2 e dos pacotes que o consomem; depois do merge da spec, publicar como `rc`.
4. `qualification/shared/ENVELOPE_V2_FREEZE.json`: versões, URLs das releases,
   sha256 das wheels, dos três contratos, da SPEC e dos schemas.
5. `qualification/shared/STACK_BASELINE_V2.0.json`: HEAD e wheels de todos os
   repos, com os `final_commits` das três missões da Etapa A.

Quando o dono fizer merge de 4 e 5, a Etapa B pode começar (três missões, uma por domínio, D-22:
`prompt_etapa_b_{crypto,stocks,brasileirao}_rev9.md` + `prompt_etapa_b_comum_rev9.md`). A especificação precisa
servir às três orquestrações: `domain` obrigatório no envelope e correlação que permita encadear episódios por domínio.
