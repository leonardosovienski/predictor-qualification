# 13 — Evidência faltante e oportunidades de alto ROI (Fase 2)

## A. Evidência faltante (por claim que o showcase gostaria de fazer)

| Claim desejado | O que existe | O que falta | Custo estimado | Bloqueio |
|---|---|---|---|---|
| "Attestations verificáveis por terceiro no estado atual" | 6 QUALIFIED; 3 só validam no commit de emissão | reemissão ou isolamento por ciclo (D-29..31 propostas); regra de imutabilidade por diretório | baixo (processo) | decisão do dono |
| "Números dos domínios cripto/stocks/ops conferidos na fonte primária" | ECO/QUAL relatam; QUAL tem RAW_LOGS das sondas | clone dos três repositórios e leitura de `trials.json`/charters | baixo | permissão da sessão (negada) |
| "Pré-registros têm anterioridade forte" | commits/tags internos | carimbo externo (OpenTimestamps ou release assinada por terceiro) dos JSON de trials/attestations | baixo | decisão |
| "Lacre operacional do Stocks íntegro no main" | quebrado por 3 arquivos (licença/CI/build-requirements) | relacre com o arquivo preservado pelo dono | baixo | só o dono |
| "CI verde" por run ID | URLs em docs | captura/arquivamento das páginas de run (repos agora privados) | baixo | externo |
| "Suítes raiz do ECO e do CORE passam no HEAD" | contagens em QUAL (2026-09-28) | ambiente com dependências instaláveis (offline bloqueou) | baixo | ambiente |
| "CAIN separa evidência de autoridade" (científico) | contenção BUILT/TESTED | experimento comparativo A/B/C pré-registrado, corpus held-out, juiz independente | médio–alto | financiamento/tempo |
| "O agente recupera evidência sem inventar" | L0 em 5 episódios, braços, limitações | avaliação held-out, humano cego, tamanho de efeito | médio | financiamento |
| "Modelo de futebol perde do mercado (n≈1.318)" | dossiê documental | reexecução com o banco (não versionado, D-11) | baixo (dono) | dado privado |
| "H6 cripto inconclusiva por poder" | n=84 relatado | `h6_status` versionado atualizado; verificação no repo | baixo | clone |
| "Resultados negativos têm critério pré-registrado" | VEREDITOS/FALSIFIED (ECO) | ligação explícita de cada veredito ao registro anterior (data do pré-registro < data do dado) nos `trials.json` dos domínios | médio | clones |
| "Correção de 2026-09-20: 1580/7 ou 1614/1" | dois números | errata | trivial | — |
| "Inconsistência de identidade: ecosystem-predictor vs -cain" | pyproject/docs | confirmação do rename e disponibilidade do nome | trivial | externo |

## B. Oportunidades de alto ROI (pouco esforço, alto ganho de verificabilidade; nenhuma iniciada nesta fase)

1. **Evidence Pack de hashes**: publicar sha256 (e tamanho) das 6 attestations, dos 7 arquivos do teste conjunto, dos 10 atestados de harness e do manifesto da qualificação, com data e commit de emissão. Verificação por terceiro passa a ser mecânica; exposição ≈ zero.
2. **Carimbo externo** dos mesmos hashes (serviço de timestamp público) para transformar `INTERNAL_TIMESTAMP_ONLY` em `EXTERNAL_TIMESTAMP` daqui para frente.
3. **Reemissão/isolamento das 3 attestations** que não revalidam no main: converte um achado P1 em prova de processo.
4. **Tabela pública de resultados negativos** (30 cards agregados) com data, critério pré-registrado (sim/não) e veredito, sem parâmetros.
5. **Página de limitações e retratações** (Maher, H13, agregador, atestado do Stocks, síntese livre do CAIN): maior diferencial de credibilidade a custo nulo.
6. **Pré-registro público do experimento A/B/C do CAIN** em nível conceitual (pergunta, braços, métrica, critério de parada), marcado PROPOSED: cria anterioridade sem expor mecanismo.
7. **Errata** do audit de 2026-09-20 e do nome do repositório.
8. **Mapa conceitual ilustrativo** (proposer → policy → evaluator → evidence store → execution environment) com o aviso obrigatório, sem nomes internos.

## C. Riscos de composição a observar na Fase 3

- Hashes + nomes de arquivos internos + números de gates podem, juntos, revelar estrutura do protocolo de qualificação; publicar hashes com rótulos genéricos.
- Cards RC-21/22/27 (governança do core, replay, política do CAIN) descritos em conjunto aproximam-se de uma especificação; manter cada um no nível de "princípio".
- Resultados numéricos de sondas (bps, IC) com datas e universos podem permitir inferir painéis e custos congelados; publicar só sinal/IC/estado, sem janelas exatas.
- Como todo o código foi público até 2026-10-05, o risco marginal de reconstrução a partir do showcase é menor que o estimado na Fase 1; o risco relevante passa a ser **revelar a evolução pós-privatização**.
