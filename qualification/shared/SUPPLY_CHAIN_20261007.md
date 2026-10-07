# Supply chain do stack — quebra e remediação (2026-10-07)

Registro de evidência do item R01 do programa de auditoria/remediação do CAIN. Nada aqui altera attestation, lock
histórico ou artefato congelado; é uma camada posterior (ORIGINAL_STATE → NEW_INTERPRETATION) com data e motivo.

## ORIGINAL_STATE (observado em 2026-10-07)

| Fato | Evidência |
|---|---|
| `ecosystem-predictor` foi renomeado `ecosystem-predictor-cain` em 2026-10-05; um repositório novo e público tomou o nome antigo (showcase, 0 releases) | API do GitHub: `ecosystem-predictor` `private=false`, sem releases; `ecosystem-predictor-cain` `private=true`, 14 releases |
| Todos os repositórios de produto são privados (`cain`, `core-predictor`, `predictor-ops`, `cripto-predictor`, `stocks-predictor`, `brasileirao-predictor`, `ecosystem-predictor-cain`, `predictor-qualification`) | API do GitHub (`private: true`), 2026-10-07 |
| Toda URL `releases/download/` fixada em `pyproject`/`uv.lock` responde 404 (anônimo e com token): o GitHub só serve asset de release privada pela API (`/releases/assets/{id}`, `Accept: application/octet-stream`), que o `uv` não usa | `curl`/`gh` 2026-10-07; logs de CI abaixo |
| CI vermelho: cain run 37564492275 (`514a2ea1`) e 37564025843 (`44ae555b`): `uv lock --check` 404 no `predictor_research_bundle-1.0.1rc1`; ecosystem-predictor-cain run 37627597341 (`602f369d`): 404 no protocolo (`research-transport`), 404 no `brasileirao_predictor-0.3.0rc5` (lock conjunta `compat/`), 404 da API de `cripto-predictor` nos checks de drift com `GITHUB_TOKEN`; cripto-predictor run 37162696842 (`964e8945`): 404 no `predictor_core-3.2.1`; stocks-predictor run 36719558172 (`3ec7e413`) e brasileirão (`curl` sem token) na mesma classe | logs dos jobs (GitHub Actions) |
| Os dez assets continuam íntegros: sha256 re-baixado pela API em 2026-10-07 igual ao dos locks antigos (core `10ef42f3…`, ops `0be70bfb…`, snapshot `3bd4c041…`, bundle `65cf40c5…`, protocolo `34a1e412…`, transporte `d3dfbff4…`, cain rc15 `ff642b72…`, cripto rc4 `32a4bd6d…`, brasileirão rc5 `be3bc512…`, stocks rc3 `902f0d34…`) | `sha256sum` nesta sessão; `compat/STACK_WHEELS.json` |

Causa raiz confirmada: duas quebras independentes, (1) rename com reuso do nome antigo, (2) privatização, sobre locks
que acoplavam identidade de artefato a nome de repositório + visibilidade. Nenhum sentinela de disponibilidade existia;
nenhum consumidor foi validado após o rename; não havia estratégia de autenticação para dependência privada.

## NEW_INTERPRETATION (branch `claude/cain-audit-remediation-fiwdei` em cada consumidor; aprovação = merge do dono)

Registro canônico por consumidor (`STACK_WHEELS.json`: repositório, tag, asset, sha256; nomes aposentados recusados) +
`stack_wheels.py` (`fetch` pela API com conferência de sha256 para o índice local `.stack-wheels/`, não versionado;
`check` = registro ⇔ índice ⇔ `uv.lock` ⇔ `pyproject`, e nenhuma URL de release no lock; `requirements` para
`pip --require-hashes`; `probe` = sentinela). `uv.lock` fixa os pacotes no índice por nome + versão (portável;
`uv lock --check` passa; versões de terceiros idênticas às dos locks anteriores). Consumidores alterados: `cain`
(4 wheels), `ecosystem-predictor-cain/packages/research-transport` (1) e `compat/` (10), `cripto-predictor`,
`stocks-predictor`, `brasileirao-predictor` (core + ops; Dockerfiles do Brasileirão e do cripto instalam do contexto de
build, sem rede). Leitura de C4/C5: decisão D-32 (proposta). Os locks históricos em `qualification/*/tools/` não mudam.

## IMPACT

* Attestations vigentes: inalteradas (valem para os `final_commits` delas). Reproduzir hoje `CLEANROOM_FINAL`,
  `HOSTED_CI`, `CORE_IDENTITY` ou `LOCK_INTEGRITY` a partir dos locks do `main` é impossível (404); passa a ser possível
  com os locks da branch **e** um token de leitura (`STACK_READ_TOKEN`, fine-grained, *Contents: read* nos produtores)
  em cada repositório consumidor — segredo que só o dono cria. Sem ele o `fetch` falha fechado com o motivo
  (cain run 37647716025, 2026-10-07).
* Qualquer ciclo novo (D-27 rc15 reaberto ou rc nova) implica C14: `publish-candidates`, `cleanroom-final` e fases
  dependentes com os locks novos; o runtime suportado continua sendo "instalação limpa só com as wheels publicadas".
* `CLAUDE.md` deste repositório dizia "repos públicos": corrigido (privados desde 2026-10; regras de segredo mantidas).
* Não demonstrado nesta sessão: CI verde em `main` (depende do merge e do segredo), imagens Docker (sem daemon aqui).

DATE: 2026-10-07 · REASON: R01 do programa de remediação · ORIGINAL_STATE preservado acima e nos logs de CI citados.
