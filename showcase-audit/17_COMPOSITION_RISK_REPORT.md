# 17 — Composition Risk Report (Fase 3)

Pares ou conjuntos de artefatos individualmente aceitáveis cuja combinação eleva o Reconstruction Risk ou enfraquece a honestidade.

| # | Combinação | Risco emergente | Mitigação |
|---|---|---|---|
| C1 | Hashes das attestations + nomes de arquivos reais + nº de gates/fases + datas | Permite a quem clonou o repositório antes de 2026-10-05 identificar exatamente a attestation e inferir a estrutura do protocolo (gates, fases, missões) | Publicar hashes com rótulos genéricos ("attestation domínio A, 2026-09-28"); nunca nomes de arquivo nem contagem de fases |
| C2 | Fluxo ilustrativo do orquestrador + princípios de governança do core + descrição do envelope | Os três juntos aproximam-se de uma especificação funcional (quem valida o quê, onde está o fail-closed, como a memória alimenta a decisão) | Um só diagrama de alto nível; os princípios do core e do transporte em frases, não em fluxos; sem "estados" nem "códigos" |
| C3 | 15 ataques PIT nomeados + canário do futuro + regra temporal | Reconstrói a suíte de conformidade temporal | Contagem + 3 exemplos genéricos; regra temporal só como princípio ("nada disponível após o corte entra") |
| C4 | IC/bps das sondas + janela + universo + custos congelados | Reconstrói painel e modelo de custos; permite replicar a sonda e comparar | Publicar só estado e sinal do IC; ou IC sem janela/universo/custos (decisão humana) |
| C5 | Datas de pré-registro + nomes de hipóteses + resultados | Mapeia o espaço de busca interno e as famílias ainda não exploradas (valor competitivo) | Famílias genéricas; datas e contagens; sem lista nominal |
| C6 | Narrativa "disciplina de evidência" + omissão das três attestations não reproduzíveis / lacre quebrado | Honestidade seletiva: um revisor que encontrar o achado interno concluirá cherry-picking | Publicar as limitações na mesma página dos resultados |
| C7 | "58/58 no teste conjunto" + "QUALIFIED" + "zero P0" sem a frase "não é edge nem autoriza capital" | Leitor infere maturidade econômica | Toda métrica de engenharia acompanhada do estado econômico (NO_EDGE) |
| C8 | Trajetória datada + repositórios históricos fora do escopo (cs, lol, f1, nba, wc) | Infla a contagem de "projetos" e mistura escopos; ou, se omitidos, apaga a origem real dos problemas de avaliação | Citar como "trabalhos anteriores (2026-06/07) fora do escopo da vitrine", com uma linha |
| C9 | Pergunta do CAIN (evidência ≠ autoridade) + descrição da contenção implementada | Leitor assume que o experimento foi feito | Rotular a pergunta como PROPOSED e a contenção como BUILT/TESTED em colunas separadas |
| C10 | Nome `ecosystem-predictor` na vitrine + URLs/releases antigas com o mesmo nome | Confusão de identidade e redirecionamento de buscas para conteúdo que foi público | Confirmar rename e disponibilidade; considerar nome distinto |
| C11 | Hipótese comercial pública + nenhum cliente | Leitor financeiro vê "produto sem demanda"; leitor acadêmico vê conflito de interesse | Apresentar como hipótese explicitamente não validada e secundária à pesquisa |
| C12 | Síntese do incidente de credencial + datas + nome do provedor | Permite inferir integrações externas e janela de exposição | Lição genérica sem provedor, datas ou mecanismo |
