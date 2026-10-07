# 15 — IP Boundary (Fase 3)

Premissa corrigida pela Fase 1/6: todo o código dos oito repositórios foi público até 2026-10-05. A fronteira de IP, portanto, não protege o passado; protege (a) a **evolução pós-privatização**, (b) a **composição** que transforma peças soltas em sistema reproduzível, e (c) dados, credenciais e PII, que nunca deveriam ter sido expostos.

## Camadas

| Camada | Conteúdo | Regra |
|---|---|---|
| PUBLIC | Perguntas, trajetória datada, princípios (4 eixos de estado; capital fail-closed; proposta ≠ autoridade; pré-registro; PIT), resultados agregados com IC e estado, resultados negativos e retratações, contagens de testes/gates com SHA e data, hashes de artefatos com rótulos genéricos, limitações, próximos experimentos como PROPOSED, licença proprietária como fato | Publicável após revisão humana; cada número com Evidence ID |
| ILLUSTRATIVE | Fluxo abstrato proposer → policy → evaluator → evidence store → execution environment; diagrama de "domínio ↔ orquestrador por envelope"; exemplos sintéticos de attestation (campos genéricos: resultado, contagens, hash) | Sempre com o aviso "Modelo conceitual ilustrativo. Não descreve a implementação privada."; nunca nomes internos, campos reais, códigos de saída, regras |
| PRIVATE | Código, patches, dumps, schemas (envelope V2, attestation), regras de decisão e seus estados, matrizes de falhas, perfis de soak, parâmetros congelados, vetores de teste, custos congelados, universos/painéis, features/instrumentos, prompts, configs de domínio, políticas/grants, mecanismos de isolamento, held-out, RAW_LOGS, caminhos, usuários, portas, PII, incidentes com detalhe | Nunca publicar nem parafrasear a ponto de reconstruir |

## Decisões de fronteira que exigem humano

1. Publicar o **nome genérico dos 15 ataques PIT** (ex.: "constituinte do futuro", "backfill tardio") ou só a contagem? Recomendação: contagem + 3 exemplos genéricos; a lista completa é parte do protocolo.
2. Publicar **intervalos de confiança das sondas** (bps) ou só o estado (INCONCLUSIVE/NO_EDGE)? Recomendação: estado + sinal do IC ("cruza zero"), sem valores, janelas ou universos.
3. Publicar **nomes de hipóteses** (H1–H22, MARKET-05) ou só famílias genéricas? Recomendação: famílias genéricas ("momentum", "baixa volatilidade", "score de LLM") e contagens; nomes internos ficam privados.
4. Publicar a **auditoria adversarial de 2026-09-05** em resumo? Recomendação: sim, os 7 achados em uma linha cada e o veredito, sem detalhe de mecanismo do bypass.
5. Publicar **datas de pré-registro** por hipótese? Recomendação: sim (é a anterioridade), junto com hash do registro, sem conteúdo.

## Riscos específicos pós-privatização

- O repositório privado chama-se historicamente `ecosystem-predictor`; URLs e releases com esse nome existem. Se a vitrine usar o mesmo nome, buscas e caches antigos podem apontar para conteúdo que foi público. EXTERNAL_VALIDATION_REQUIRED.
- Attestations citam `final_commits` e hashes de wheels; publicá-los permite a quem tenha clonado antes de 2026-10-05 alinhar exatamente a versão. Aceitável para verificação; não acrescenta reconstrução.
