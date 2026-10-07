# 18 — Funding Narrative (Fase 3, rascunho privado)

Para quem: grants de pesquisa em avaliação/governança de agentes e ML, fellowships individuais, laboratórios universitários, incubadoras científicas. Não é pitch comercial.

## Problema

Sistemas de previsão falham silenciosamente por avaliação, não por modelagem: vazamento temporal, seleção de hipóteses, custos ignorados, baselines contaminados. Agentes de IA que executam pesquisa agravam o problema: podem usar "evidência" para ganhar acesso a dados de teste, permissões ou orçamento. Pouco se sabe empiricamente sobre como separar evidência de autoridade em agentes de pesquisa.

## O que já foi feito (verificável)

- Três domínios de previsão com 42+ hipóteses julgadas por critérios pré-registrados; nenhum edge econômico encontrado e todos os resultados negativos preservados com data. [EVID-ECO-023/030, EVID-BRAS-003]
- Uma biblioteca científica que exige pré-registro, proveniência de trial e atestado de controle positivo antes de aceitar vereditos; auditoria adversarial interna que derrubou e depois fechou achados críticos. [EVID-CORE-002/004, EVID-BRAS-002]
- Um protocolo de qualificação com gates congelados, logs brutos hash-identificados e seis attestations, verificado por teste conjunto dos três domínios reais com um orquestrador. [EVID-QUAL-002/003]
- Um agente de pesquisa que propõe experimentos aos domínios por meio de uma política determinística versionada e nunca decide handler, orçamento ou capital; contenção verificada; avaliação piloto mostrou que a síntese livre de modelos locais não é confiável. [EVID-CAIN-002/005]
- Quinze ataques adversariais de informação-do-futuro repelidos sem vazamento; 81 controles negativos. [EVID-QUAL-013/014]

## A pergunta que financiamento permite responder

**Um agente de pesquisa pode usar evidência para mudar o que investiga sem que a evidência se torne rota para mais autoridade (avaliador, held-out, permissões, orçamento)?**

Desenho proposto (PROPOSED, não executado): comparação pré-registrada de três regimes — (A) agente com instruções apenas; (B) agente com isolamento do avaliador; (C) isolamento mais fronteira determinística entre evidência e autoridade — sobre episódios de pesquisa com corpus held-out e juiz independente, medindo tentativas de escalada de autoridade, qualidade das propostas e taxa de fabricação. A infraestrutura para (C) existe e foi testada; (A) e (B) são configurações de controle.

## O que o financiamento compra, especificamente

| Item | Hoje | Com financiamento |
|---|---|---|
| Experimento A/B/C | PROPOSED | pré-registro público, corpus held-out, juiz humano, execução e relatório |
| Dados PIT licenciados (odds históricas com timestamp) | bloqueado por custo/licença | decisão do EXP-001 histórico e do caminho estrutural de mercado |
| Revisão humana externa | só auditorias por agentes | revisão independente das attestations e do protocolo |
| Tempo de máquina e secundários (Windows/PC 2) | gates BLOCKED do ciclo atual | fechamento dos gates e reemissão das attestations |
| Coleta prospectiva (H6 até n≈250; EXP-001 n≥300) | passiva, lenta | cadência e cobertura adequadas |

## Por que acreditar

Porque o programa publica o que não funcionou: retratações, baselines contaminados, uma arquitetura inteira removida, attestations que deixaram de revalidar, um lacre quebrado por decisão documentada. A evidência não depende de confiar em código privado: hashes, contagens, datas e limitações são verificáveis.

## O que não se promete

Lucro, edge, produto, "segurança", generalização além dos domínios estudados, ou que o agente "aprende". Capital permanece proibido por contrato e por configuração em todos os componentes.
