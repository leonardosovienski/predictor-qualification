# 16 — Exposure Matrix (Fase 3)

Regras: HIGH verif + LOW reconstr → público; HIGH verif + MEDIUM reconstr → SANITIZE + revisão humana; LOW verif → não publicar; HIGH reconstr → PRIVATE_ONLY. Em dúvida, restritivo.

| Candidato | Verification Value | Reconstruction Risk | Camada | Decisão | Condições | Evidence ID |
|---|---|---|---|---|---|---|
| Trajetória datada (cronologia por commits/tags, 11_) | HIGH | LOW | PUBLIC | PUBLICAR | datas e marcos; sem SHAs de domínio além de tags públicas já citadas | EVID-ECO-028, EVID-*-001 |
| Princípio dos 4 eixos de estado + capital fail-closed | HIGH | LOW | PUBLIC | PUBLICAR | texto novo; sem enums reais | EVID-ECO-007 |
| Taxonomia de vereditos (comprovada/refutada/não comprovada/inconclusiva; GO/NO-GO) | HIGH | LOW | PUBLIC | PUBLICAR | reescrita | EVID-ECO-024 |
| Resultados negativos agregados (30 cards → ~15 linhas públicas) | HIGH | LOW | PUBLIC | PUBLICAR | famílias genéricas; estado; "IC cruza zero"; data | EVID-ECO-011/023/030, EVID-BRAS-003/006 |
| Retratações explícitas (Maher, viés pró-zebra, baseline contaminado, agregador, atestado do Stocks) | HIGH | LOW | PUBLIC | PUBLICAR | uma linha cada | EVID-BRAS-006/007, EVID-ECO-010/015 |
| Auditoria adversarial 2026-09-05 (7 achados; veredito) | HIGH | LOW–MEDIUM | PUBLIC | SANITIZE | sem mecanismo do bypass; citar correção em release | EVID-BRAS-002, EVID-CORE-002 |
| Attestations: resultado, nº de gates, P0/P1/P2, capital=false, sha256, data | HIGH | MEDIUM | PUBLIC | SANITIZE + revisão humana | sem nomes de gates, fases, ambientes, caminhos | EVID-QUAL-002 |
| Teste conjunto 58/58 + trajetória 47/57→58/58 + hashes | HIGH | LOW–MEDIUM | PUBLIC | SANITIZE | sem itens da lista de conferência; só contagem e hashes | EVID-QUAL-003 |
| 15 ataques PIT, 0 vazamentos; canário do futuro | HIGH | MEDIUM | PUBLIC/ILLUSTRATIVE | SANITIZE | contagem + 3 exemplos genéricos; decisão humana (15_ §1) | EVID-QUAL-014/017 |
| Controles negativos (81 execuções; labels embaralhados 0/20) | HIGH | LOW | PUBLIC | PUBLICAR | sem seeds/critérios | EVID-QUAL-013 |
| Sondas reais: estado INCONCLUSIVE/NO_EDGE nos três domínios | HIGH | MEDIUM | PUBLIC | SANITIZE | só estado e sinal do IC; sem bps, janelas, universos, custos (decisão 15_ §2) | EVID-QUAL-012/015/016 |
| Contagens de testes por repositório com SHA e data | MEDIUM | LOW | PUBLIC | PUBLICAR | tabela | EVID-QUAL-010, EVID-ECO-003 |
| Hashes de atestados de harness (10) e manifesto (13) | MEDIUM | LOW | PUBLIC | PUBLICAR | rótulos genéricos | EVID-ECO-027, EVID-QUAL-001 |
| Fluxo abstrato do orquestrador (proposta → política → task → domínio → resultado → memória) | HIGH | MEDIUM | ILLUSTRATIVE | SANITIZE | aviso obrigatório; sem decisões, códigos, comandos, nomes de classes | EVID-CAIN-002 |
| Princípio "modelo propõe; política determinística decide" | HIGH | LOW | PUBLIC | PUBLICAR | conceito | EVID-CAIN-002, EVID-ECO-020 |
| Pergunta de pesquisa do CAIN + desenho A/B/C | HIGH | LOW (enquanto PROPOSED) | PUBLIC | PUBLICAR como PROPOSED | pergunta, braços, métrica, critério de parada em nível conceitual; sem protocolo operacional | EVID-CAIN-007 |
| Pilotos de avaliação L0 (3 braços, 5 episódios, abstenção) e resultado negativo da síntese livre | HIGH | LOW | PUBLIC | PUBLICAR | sem nomes de modelos nem parâmetros | EVID-CAIN-004/005 |
| Catálogo de hipóteses no CAIN (22/32/48 fontes; 0 falhas) | MEDIUM | LOW | PUBLIC | PUBLICAR | contagens | EVID-CAIN-006 |
| Governança do core (pré-registro, Trial Registry V2, atestado de poder, replay anti-lookahead) | HIGH | MEDIUM | ILLUSTRATIVE | SANITIZE | princípios; sem campos, API, exceções | EVID-CORE-004 |
| DEC-010: 9 primitivas removidas por falta de 2º consumidor | MEDIUM | LOW | PUBLIC | PUBLICAR | contagem + princípio | EVID-CORE-004 |
| Workflows de CI (matriz, cobertura mínima, varredura de histórico com controle sintético, release reprodutível) | MEDIUM | LOW | PUBLIC | PUBLICAR | fatos; sem YAML | EVID-ECO-006 |
| Hipótese comercial B0/E0; receita 0 | MEDIUM | LOW | PUBLIC | PUBLICAR | sem contatos, sem oferta detalhada | EVID-ECO-018 |
| Licença proprietária | MEDIUM | LOW | PUBLIC | PUBLICAR | fato | EVID-ECO-022 |
| Attestations não reproduzíveis no main (EPOCA-QUAL-1) e lacre R8 quebrado | HIGH (honestidade) | LOW | PUBLIC | PUBLICAR como limitação | sem detalhe de arquivos | EVID-QUAL-007 |
| Intervalos de confiança numéricos das sondas | MEDIUM | MEDIUM | PRIVATE até decisão | ADIAR | ver 15_ §2 | EVID-QUAL-012/015 |
| Nomes de hipóteses internas (H1–H22, MARKET-0x, IC-F0xx) | LOW | MEDIUM | PRIVATE | NÃO PUBLICAR | famílias genéricas no lugar | — |
| Nomes de gates/fases/regras C-numeradas | LOW | HIGH | PRIVATE | NÃO PUBLICAR | — | EVID-QUAL-011 |
| Schemas (envelope V2, attestation), contratos, parâmetros/vetores congelados, matriz de falhas, perfis de soak | LOW | HIGH | PRIVATE | PRIVATE_ONLY | — | EVID-ECO-020, EVID-QUAL-011 |
| Código, patches, dumps, overlays | LOW | HIGH | PRIVATE | PRIVATE_ONLY | — | EVID-ECO-015/016, EVID-QUAL-008 |
| RAW_LOGS, recibos com caminhos, usuários, portas | LOW | HIGH (composição) | PRIVATE | PRIVATE_ONLY | — | EVID-QUAL-003, EVID-ECO-014 |
| PII de terceiros | N/A | N/A | PRIVATE | NUNCA | remoção recomendada | EVID-ECO-013 |
| Incidente de credencial (detalhe) | LOW | LOW | PRIVATE | lição genérica apenas | — | EVID-ECO-012 |
| Documentos históricos de fechamento, handoffs, blueprints | LOW | MEDIUM | PRIVATE | OBSOLETE | — | EVID-ECO-021 |
