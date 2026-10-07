# 19 — Skeptical Reviewer Attack (Fase 3)

Dez personas atacam a vitrine proposta. Para cada ataque: o que diriam, se procede, e a resposta honesta disponível (ou a lacuna).

| Persona | Ataque | Procede? | Resposta honesta / lacuna |
|---|---|---|---|
| Pesquisador de AI Safety | "A pergunta central (evidência ≠ autoridade) é interessante, mas vocês só construíram a contenção; não há experimento, nem ameaça modelada, nem métrica de escalada." | **Sim** | Declarar PROPOSED; publicar pré-registro conceitual; a contenção é engenharia, não resultado científico. [EVID-CAIN-007] |
| Pesquisador acadêmico (métodos) | "42 hipóteses, 8 comprovadas em qualidade de previsão: qual a correção por multiplicidade? O DSR foi considerado 'quase inoperante' pela própria auditoria." | **Sim, parcialmente** | A auditoria de 2026-09-05 achou exatamente isso; o core 3.2.0 registrou contagens de tentativas como fato de auditoria e exige atestado. Publicar o achado e a correção, não esconder. [EVID-BRAS-002, EVID-CORE-002] |
| Pesquisador acadêmico (reprodutibilidade) | "29/29 trials sem proveniência em setembro; três attestations não revalidam hoje. Onde está a reprodutibilidade?" | **Sim** | Reconhecer: proveniência passou a ser obrigatória (Trial Registry V2) após o achado; as três attestations serão reemitidas ou isoladas (decisão pendente). Mostrar hashes conferidos nesta auditoria. [EVID-QUAL-007, EVID-ECO-027] |
| Engenheiro experiente | "Oito repositórios, 83 markdowns só no canônico, seis ciclos de 'fechamento final' em dois meses. Isso é engenharia ou documentação?" | **Parcialmente** | A própria auditoria interna de 2026-08-31 fez essa crítica; o agregador foi removido; a evidência executável (310 testes reproduzidos, 58/58, 15 ataques PIT) é o que conta. Reconhecer a razão doc:código histórica. [EVID-ECO-015, EVID-ECO-003] |
| Engenheiro de ML/produção | "QUALIFIED com 30 gates PASS, mas o lacre operacional está quebrado no main e a CI está vermelha." | **Sim** | Quebrado por decisão documentada (relacrar com dados de hoje afrouxaria o lacre); publicado como limitação. [EVID-QUAL-007] |
| Concorrente | "Todo o código foi público até ontem; eu já clonei. O que a vitrine protege?" | **Sim** | A vitrine não protege o passado; protege a evolução futura e não acrescenta composição. Decisão humana sobre histórico já exposto. [06_] |
| Grant reviewer | "Qual é a contribuição além de 'fizemos direito'? Nenhum resultado positivo." | **Parcialmente** | Contribuições: (1) corpus datado de resultados negativos com pré-registro; (2) mecanismo de contenção para agente de pesquisa, testado em integração real; (3) pergunta aberta com infraestrutura pronta. Resultados negativos são evidência. |
| Fellowship reviewer | "Pesquisa de uma pessoa com agentes de IA como executores; a 'revisão independente' foi feita por modelos. Quem valida?" | **Sim** | Declarar explicitamente; pedir revisão humana externa como item financiável. [EVID-CAIN-005, 12_ §F] |
| Universidade/laboratório | "Isso é generalizável ou é específico de três domínios brasileiros de aposta/mercado?" | **Parcialmente** | O contrato temporal foi exercitado em outros três domínios (F1, LoL, CS) em 2026-08; a pergunta do agente é independente de domínio. Não afirmar generalização sem o experimento. [EVID-ECO-025] |
| Incubadora | "Há cliente? Há produto?" | **Sim (não há)** | B0/E0; a vitrine é de pesquisa; hipótese comercial explicitamente não validada e secundária. [EVID-ECO-018] |
| Investidor | "Nenhum edge em nenhum domínio, capital proibido por código. Por que existe?" | **Sim** | Porque o objetivo mudou de prever para avaliar; não é tese de investimento. Dizer isso na primeira linha. |
| Alguém tentando reconstruir | "Com hashes, nomes de gates e IC das sondas eu reconstruo o protocolo." | **Sim, se publicado sem sanitização** | Aplicar 16_/17_: hashes com rótulos genéricos, sem nomes de gates, sem IC com janela/universo. |
| Jornalista/leitor leigo | "Vocês tornaram público por meses dados pessoais de dez pessoas." | **Sim** | Fato; recomenda-se remoção do repositório e avaliação de obrigação de tratamento. Não mencionar na vitrine, mas preparar resposta. [EVID-ECO-013] |

## Síntese

Os ataques que procedem integralmente são sobre **ciência não feita** (experimento do CAIN), **reprodutibilidade parcial** (attestations/lacre) e **exposição passada**. Todos têm resposta honesta disponível e nenhum exige esconder nada; exigem rotular PROPOSED como PROPOSED, publicar limitações ao lado dos resultados e decidir sobre o histórico exposto.
