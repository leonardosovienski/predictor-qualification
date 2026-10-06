# 12 — Evidência relevante para financiamento (Fase 2)

Objetivo: o que um revisor de grant/fellowship/laboratório consegue **verificar** sem confiar na frase "a parte importante está privada". Nada abaixo é narrativa; é lista de evidências com maturidade e limite. A narrativa pública é Fase 3.

## A. O que está provado em escopo estreito (candidatos a Evidence Pack)

| Evidência | Escopo exato | Maturidade | Verificável por terceiro como | Evidence ID |
|---|---|---|---|---|
| Seis attestations QUALIFIED com P0=0, `capital_permission=false`, hash-identificadas; 19 superseded preservadas (história não apagada) | commits de emissão, 2026-09-24→28 | EXERCISED; identidade REPRODUCED | sha256 publicáveis dos JSON + contagens | EVID-QUAL-002 |
| Teste conjunto dos três domínios reais com orquestrador: 58/58, após 47/57 → 56/58 → 57/58 | 2026-09-28, pilha rc13 | REPRODUCED (identidade) | sha256 de SUMMARY.json + contagens | EVID-QUAL-003 |
| 15 ataques adversariais de PIT, 0 vazamentos; canário do futuro falha fechado nos três domínios; same-kickoff e metamórfico PASS | wheels publicadas, Linux + Windows | EXERCISED | contagem de casos + nomes genéricos dos ataques | EVID-QUAL-014/017 |
| Controles negativos sobre painel real (81 execuções): labels embaralhados nunca SUPPORTED | stocks, run de 2026-09-24 | EXERCISED | contagens | EVID-QUAL-013 |
| 310 testes de transporte reproduzidos nesta auditoria; invariantes de registry OK | ECO @ 602f369, 2026-10-06 | REPRODUCED | SHA + contagem | EVID-ECO-003/004 |
| 29 trials pré-registradas no futebol: 1 comprovada (qualidade de previsão), 6 refutadas, 6 inconclusivas | BRAS @ 1e0c6f0 | PROVEN (contagem) | contagens por status | EVID-BRAS-003 |
| Auditoria adversarial interna com 7 achados, 2 críticos, respondida em release; auditor retrata 2 erros próprios | 2026-09-05/06 | EXERCISED | sumário dos achados + versão que os fechou | EVID-BRAS-002, EVID-CORE-002 |
| 17 hipóteses falsificadas com critérios pré-registrados; "capital aprovado: zero" em 42 hipóteses | 2026-07 → 2026-08-31 | DECLARED (números dos domínios a verificar nos repos) | tabela agregada | EVID-ECO-011/023/030 |
| Hashes de integridade conferidos nesta auditoria: 10/10 atestados, 13/13 manifesto, 7/7 teste conjunto, 4/4 attestations citadas | 2026-10-06 | REPRODUCED | reexecutável por qualquer um com acesso | EVID-ECO-027, EVID-QUAL-001/002/003 |

## B. Capacidade de execução (engenharia) — fatos de definição e de execução registrada

- Oito repositórios, 12 pacotes publicados como wheels com hash, lock conjunta instalável (12 pacotes/42 dependências) verificada em CI.
- Release reprodutível (`git archive` + epoch fixo, build duplo com bytes idênticos) nas pré-releases da Etapa B.
- CI com matriz Python 3.11–3.14 nos pacotes, cobertura mínima, varredura de segredos do histórico completo com controle sintético, drift diário entre registries e remotos.
- Suítes: cain 1.446/4 em três Pythons; core 278 (86%); ops 88+1 (80,9%); eco 165 (78%) — todas EXERCISED em QUAL (2026-09-28), não reproduzidas aqui.
- Correções fechadas em release a partir de auditorias adversariais (core 3.2.0; transporte rc6/rc7; cain rc15; brasileirão rc3 para BR-F018).

## C. Linha de pesquisa CAIN — separação exigida pelo protocolo

| Classe | Conteúdo | Evidence ID |
|---|---|---|
| **BUILT** | Orquestração por domínio: proposta → política de decisão determinística versionada por hash (sem LLM, sem relógio) → task no outbox → spool → adapter do domínio → resultado → inbox fail-closed → memória bitemporal. Grants de admissão; CAIN sem domínio instalado no venv qualificado; `capital_permission=false` em todo receipt. Catálogo literal de hipóteses dos três domínios (102 publicações). | EVID-CAIN-002/003/006 |
| **TESTED** | Contenção verificada pela qualificação (três integrações QUALIFIED; item "nenhum capital_permission true" 1/1; isolamento e IDs cruzados; matriz de falhas F01–F15); auditoria adversarial CAIN_EXTREME (envelope ilegível, `as_of` impossível → corrigidos); 1.446 testes. | EVID-QUAL-002/003/010 |
| **OBSERVED** | Modo LLM local em teste conjunto: cripto ALLOW, stocks ALLOW, brasileirão NO_ELIGIBLE_HYPOTHESIS (1/1); soak com 6 propostas do LLM (integration-crypto rc15, 48/0). Piloto L0: recuperação documental em 3 braços, 5 episódios; revisão independente: síntese livre com conclusões falsas apesar de citações exatas. | EVID-ECO-008, EVID-CAIN-004/005 |
| **PROPOSED** | Pergunta: "um agente de pesquisa pode usar evidência para mudar o que investiga sem que a evidência vire rota para mais autoridade (evaluator, held-out, permissões, budget)?" Comparação A (prompt-only) vs B (isolamento de avaliação) vs C (isolamento + fronteira determinística evidência/autoridade): **nenhum desenho experimental, pré-registro ou dado encontrado** nos cinco repositórios. Permanece PROPOSED. | — (ausência registrada) |
| **FUNDING_DEPENDENT** | Execução do experimento A/B/C com corpus held-out e juiz independente; tempo de máquina para soaks longos; dados licenciados (odds históricas timestamped) para destravar EXP-001 histórico e MARKET-05; coleta de H6 até n≈250; Windows/PC secundário para fechar gates BLOCKED do ciclo D-27. | EVID-ECO-011/029, EVID-QUAL-006 |

## D. Trajetória intelectual verificável

Datas ancoradas em commits/tags (11_RESEARCH_LINEAGE): junho (sistemas de previsão) → junho–agosto (problemas de avaliação, falsos positivos, retratações) → agosto–setembro (reprodutibilidade e governança no core; auditoria adversarial) → setembro (qualificação formal; agente de pesquisa com contenção; avaliação do agente). Inclui uma tentativa de infraestrutura invalidada e removida (agregador), o que é evidência de disciplina, não de falha.

## E. Limitações a declarar sempre

- Nenhum edge econômico demonstrado em nenhum domínio; todos os estados econômicos são NO_EDGE/INCONCLUSIVE; capital proibido por contrato e por config.
- Três attestations vigentes não revalidam no `main` atual (artefatos regravados); lacre operacional do Stocks quebrado no `main` por decisão.
- Síntese livre de modelos locais no CAIN não tem confiabilidade demonstrada (resultado negativo do próprio projeto).
- Corpus de avaliação do CAIN pequeno, não held-out; pilotos não permitem inferir superioridade.
- Toda a história pública até 2026-10-05 inclui código completo; o valor defensável está na evolução futura e na evidência, não no sigilo retroativo.
- Pesquisa de uma pessoa, com agentes de IA como executores; a revisão independente interna foi feita por modelos, não por humanos externos.

## F. O que financiamento desbloqueia (específico, não genérico)

1. Experimento A/B/C do CAIN com pré-registro, corpus held-out e juiz humano: hoje PROPOSED.
2. Dados licenciados PIT (odds históricas com timestamp) para decidir EXP-001 histórico e MARKET-05: hoje bloqueado por custo/licença (Gate L0: acima do teto pessoal).
3. Fechamento dos gates BLOCKED do ciclo D-27 (Windows local/PC 2): hoje dependente do tempo do dono.
4. Revisão humana externa das attestations e da qualificação (hoje só auditorias por agentes).
5. Coleta prospectiva de H6 até poder adequado (n≈250) e cohort prospectiva do EXP-001 (n≥300 no primeiro checkpoint).
