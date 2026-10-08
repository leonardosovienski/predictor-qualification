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

## LAYER 2026-10-07 (noite) — merges, repositórios públicos, CI verde, passagem de segurança

ORIGINAL_STATE: o bloco acima (branch não mesclada, produtores privados, `STACK_READ_TOKEN` obrigatório, CI em `main`
não demonstrado).

NEW_INTERPRETATION:

* Merges sob a D-33: cain #93, ecosystem-predictor-cain #52, cripto-predictor #148, stocks-predictor #116,
  brasileirao-predictor #91 (mecanismo R01); depois #149 (cripto: ccxt 4.5.85 → urllib3 2.8.0, Trivy), #92/#89/#93
  (brasileirão: urllib3 2.8.0, actions, virtualenv), #53/#54 (ecosystem-predictor-cain: pytest/virtualenv, teste de
  renovação sem data fixa, fallback de token), #117 (stocks), #145/#146/#150 (cripto: actions, pytest/virtualenv,
  fallback de token), core-predictor #38/#39, predictor-ops #32/#33.
* O dono tornou os nove repositórios públicos em 2026-10-07: o `fetch` resolve anônimo; `STACK_READ_TOKEN` vira
  opcional e cada workflow cai para o token do job (`secrets.STACK_READ_TOKEN || github.token`) porque execuções
  disparadas pelo Dependabot não recebem segredos e o acesso anônimo bateu no limite de taxa da API
  (cripto-predictor PR #147, run 37663391913).
* CI verde em `main` com o registro: cain (Linux) run 37651563333; ecosystem-predictor-cain 37651560309; cripto-predictor
  37663192063 (inclui o job `container` com Trivy); brasileirao-predictor 37662106707. stocks-predictor 37651574443
  vermelho só em "Current R8 operational evidence identities" (evidência que depende do dado privado do dono; anterior
  ao programa). A renovação agendada do harness do cripto voltou a passar (run 37664153832, PR #55 aberto pelo
  workflow; o merge é do dono, conforme o próprio workflow).
* Passagem de segurança (`pip-audit` sobre `uv export --all-extras --all-groups` de cada `uv.lock` em `main`):
  urllib3 2.7.0 (cripto, brasileirão; ops já em 2.8.0) corrigido; pytest 8.4.2 e virtualenv 21.7.x (extras de dev de
  cripto, ecosystem-predictor-cain, brasileirão) corrigidos; cain, core-predictor, predictor-ops, stocks-predictor sem
  achado. Residual: multidict 6.7.1 (CVE-2026-104874) fixado exatamente pelo ccxt 4.5.85, a release mais nova. As
  abas de segurança do GitHub (Dependabot alerts, code scanning) não estavam acessíveis a esta sessão.
* Nenhum lock histórico em `qualification/*/tools/` mudou; nenhuma attestation mudou.

IMPACT: `CLEANROOM_FINAL`, `HOSTED_CI`, `CORE_IDENTITY` e `LOCK_INTEGRITY` voltam a ser reproduzíveis a partir dos locks
de `main` sem segredo. O que falta continua sendo o ciclo C14 numa rc nova (decisão do dono).

DATE: 2026-10-07 · REASON: fechamento do R01 na parte de disponibilidade + passagem de segurança/qualidade pedida pelo
dono · ORIGINAL_STATE preservado acima.

## LAYER 2026-10-08 — ciclo C14 na rc nova fechado (D-34)

* cain `v0.4.13rc16` publicada (`de5db06b`, wheel `d8fca502…`, build reprodutível; código do pacote igual ao da rc15, lock pelo registro).
* Attestations reemitidas **QUALIFIED**: crypto V1.2 (D-30), integration-crypto rc16 → rc16e, integration-stocks ciclo 6 → ciclo 7
  (PRs #104, #105). O ecosystem adotou a rc16 na lock conjunta `compat/` (ecosystem 0.2.2, `6aeec475`) e as fases das integrações
  foram refeitas depois disso (C14). integration-brasileirao: só conferências estáticas na rc16; runtime no PC 2 do dono.
* O que ficava "faltando" na camada anterior (ciclo C14 numa rc nova) está feito. Pendente só o dono: runtime do brasileirão.

DATE: 2026-10-08 · ORIGINAL_STATE preservado acima.
