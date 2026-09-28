Pré-release única de reconciliação das três integrações da Etapa B, por decisão do dono em 2026-09-28: convergir numa só release do cain e requalificar cripto, stocks e Brasileirão nela.

Substitui três pré-releases, que continuam publicadas sem mudança:
- v0.4.13rc6 (cripto);
- v0.4.13rc7 (stocks);
- v0.4.13rc9 (Brasileirão), construída de uma branch com a política v1.

Construída do main `fb0e1dc`, que já contém tudo o que está abaixo.

## Conteúdo em relação à rc9
**Política de decisão (DecisionPolicy):**
- **v2 (#59):**
  - R15: um pedido de hipótese que o domínio já recusou como não admitida vai para decisão humana (`REQUIRE_HUMAN HYPOTHESIS_NOT_ADMITTED_BY_DOMAIN`);
  - a memória guarda só códigos fechados de recusa.
- **#62:** custos da R06 conforme a variante do contrato.
- **R16 (#65):** um pedido que tocaria um escopo lacrado vai para decisão humana (`REQUIRE_HUMAN SEALED_SCOPE`). Um campo lacrado ausente ou malformado também retém o pedido. O Brasileirão lacra o holdout 2025 (#66); cripto e stocks não lacram nada.
- **#67:** tipo de pedido por hipótese (`proposable_request_types`), com a R04 verificada por hipótese.
- **R17 (#68):** um pedido que repete o mesmo experimento com outro ID vira `DUPLICATE EQUIVALENT_REQUEST`.
  - O experimento é o pedido sem `request_id`, `hypothesis_id`, `research_id` e `client_ref`.
  - Só conta contra tarefas que rodaram ou estão abertas.

**Propostas por LLM:**
- só entram hipóteses que a política aceitaria no momento;
- a semente é atribuída pelo CAIN;
- o molde do pedido é o da própria hipótese (#67);
- a justificativa é conferida contra a visão da memória (#69), e a auditoria passa a `/3`.

**Configurações:**
- Brasileirão (#64/#66) com lacres;
- as três ganham as chaves `sealed_scopes` e `proposable_request_types`;
- as três são regeneradas pelo `tools/build_domain_config.py`, iguais byte a byte ao que a ferramenta gera a partir dos commits registrados.

**Dependências:** `predictor-research-transport` 0.1.0rc5, a mesma da rc9.

## Build e escopo
- Wheel construída 2× por `git archive` com `SOURCE_DATE_EPOCH=1758240000`, com o mesmo sha256 nas duas.
- É qualificação, não operação: sem modo operacional e sem capital.
