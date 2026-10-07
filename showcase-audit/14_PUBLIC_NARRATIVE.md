# 14 — Public Narrative (Fase 3, rascunho para revisão humana)

Status: **rascunho privado**. Nada aqui está aprovado para publicação. Toda frase numérica aponta para um Evidence ID; nenhuma frase descreve mecanismo. Texto em português; versão em inglês só após aprovação do conteúdo.

## Tese pública (uma frase)

Um programa de pesquisa individual que construiu sistemas de previsão em três domínios, descobriu que seus problemas eram de **avaliação** e não de modelagem, e respondeu construindo disciplina de evidência: pré-registro, integridade temporal verificável, qualificação por protocolo com attestations, e um agente de pesquisa que propõe sem nunca ganhar autoridade.

## Narrativa em quatro atos (cada ato com evidência agregada)

**Ato 1 — Previsão (jun–jul/2026).** Três sistemas de previsão (futebol, ações, cripto) chegaram a resultados que pareciam bons. Um backtest de +44% de ROI foi decomposto e explicado como variância e viés de compressão de rating; um ganho atribuído a um modelo mais rico foi retratado após um experimento de controle; famílias de sinais em cripto que tinham edge bruto positivo tornaram-se negativas após custos. [EVID-BRAS-006, EVID-ECO-030]

**Ato 2 — Avaliação (jul–ago/2026).** Quarenta e duas hipóteses receberam veredito formal; nenhuma foi aprovada para capital. Um sinal baseado em LLM mostrou correlação negativa significativa com o retorno que deveria prever. Um baseline foi descoberto contaminado pela própria coorte e corrigido antes de qualquer veredito. Uma arquitetura de agregação foi auditada, julgada desnecessária e removida. [EVID-ECO-023/011/015, EVID-BRAS-007]

**Ato 3 — Reprodutibilidade e governança (ago–set/2026).** Uma biblioteca científica compartilhada passou a exigir pré-registro, proveniência completa de cada trial e um atestado de controle positivo antes de registrar ou alterar um veredito. Uma auditoria adversarial interna falsificou a tese "um terceiro consegue verificar isso" na parte científica e a sustentou na parte de engenharia; as correções entraram na versão seguinte. [EVID-CORE-002/004, EVID-BRAS-002]

**Ato 4 — Qualificação e agente de pesquisa (set/2026).** Um protocolo de qualificação com gates congelados e logs brutos emitiu seis attestations, todas com capital proibido. Quinze ataques de informação-do-futuro foram repelidos sem vazamento. Um agente de pesquisa foi construído para propor experimentos aos domínios sem jamais decidir handler, orçamento ou capital; sua contenção foi verificada em um teste conjunto com os três domínios reais (58/58). A pergunta científica que ele levanta — se evidência pode mudar o que se investiga sem virar rota para mais autoridade — permanece **proposta, não testada**. [EVID-QUAL-002/003/014, EVID-CAIN-002/007]

## O que o público pode verificar

- Hashes publicados de attestations, do teste conjunto e dos atestados de harness, com data e commit (Evidence Pack).
- Contagens por status de hipóteses e trials, com data de registro anterior à data do dado.
- Tabela de retratações e resultados negativos, com o que mudou depois.
- Limitações declaradas: nenhum edge econômico; três attestations não revalidam no estado atual; síntese livre de modelos locais sem confiabilidade demonstrada.

## O que o público não verá

Código, parâmetros, features, prompts, regras de decisão, schemas, contratos, configurações, dados, logs brutos, nomes internos e caminhos. O showcase mostra **que** a disciplina existe e **o que** ela produziu, não **como** ela funciona.

## Frases proibidas (não propagar)

"Sistema validado", "edge comprovado", "pronto para produção", "exactly-once", "seguro", "o agente aprende", "CI verde prova", "qualificado = lucrativo", qualquer número sem Evidence ID.
