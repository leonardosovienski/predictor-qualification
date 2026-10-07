# 20 — Projeto do repositório público `ecosystem-predictor` (Fase 4)

Status: **projeto e rascunho completo em `showcase-audit/public-draft/`; repositório público NÃO criado** (o protocolo veda a criação nesta fase; a decisão de criar é do proprietário).

## Decisões tomadas nesta fase (delegadas pelo proprietário)

| Decisão | Escolha | Justificativa |
|---|---|---|
| Fronteira de IP (15_ §1–5) | Seguidas as recomendações: contagem + 3 exemplos genéricos dos ataques PIT; só estado e "IC cruza zero" para sondas, sem valores; famílias genéricas em vez de nomes de hipóteses; auditoria adversarial em uma linha por achado; datas de pré-registro sim, conteúdo não | minimiza composição (17_ C1–C5) mantendo verificabilidade |
| Nome | `ecosystem-predictor`, conforme o programa | colisão com o nome histórico do privado registrada como EXTERNAL_VALIDATION_REQUIRED; se o nome não estiver livre ou redirecionar, usar `predictor-evidence` como alternativa |
| Escopo da Fase 4 | textos completos em rascunho privado; sem criação de repositório, sem commit, sem publicação | ações externas exigem decisão humana explícita |
| Idioma | inglês nos textos públicos (público de grants/fellowships); versão em português pode ser adicionada depois | — |
| Nomes de repositórios privados no público | **não**; só papéis (core científico, runner, domínios por área, agente, qualificação) | reduz composição; os nomes já foram públicos, mas não acrescentam verificação |
| Números | contagens, datas e hashes sim; bps/IC/janelas/universos não | 15_ §2 |
| Licença dos textos | decisão pendente; recomendação CC BY-ND 4.0 registrada em `LICENSE-NOTICE.md` | texto citável, não derivável |

## Estrutura do repositório proposto

```
ecosystem-predictor/
  README.md                      # três níveis: 15 s · 2 min · 10 min
  LICENSE-NOTICE.md              # até decisão de licença
  SECURITY.md
  CONTRIBUTING.md
  docs/
    EVIDENCE_PACK.md             # hashes, datas, contagens (33 hashes únicos conferidos contra os artefatos)
    RESEARCH_CARDS.md            # 15 linhas sanitizadas
    NEGATIVE_RESULTS.md          # hipóteses falsificadas, retratações, achados contra nós mesmos
    LIMITATIONS.md               # 12 limitações declaradas
    LINEAGE.md                   # cronologia datada
    ARCHITECTURE_ILLUSTRATIVE.md # diagrama conceitual com aviso obrigatório
    NEXT_EXPERIMENTS.md          # E1–E6, PROPOSED
    FUNDING.md
```

Histórico Git independente, criado do zero; nenhum arquivo copiado dos privados (todos os textos foram redigidos nesta auditoria a partir de evidência agregada).

## Mapeamento público → evidência privada

| Documento público | Evidence IDs de origem |
|---|---|
| README | EVID-ECO-007/023, EVID-QUAL-002/003/014, EVID-CAIN-002/007, EVID-BRAS-003 |
| EVIDENCE_PACK | EVID-QUAL-001/002/003, EVID-ECO-009/027/003/004, EVID-BRAS-003, EVID-QUAL-013/014; wheels: released_architecture (ECO) |
| RESEARCH_CARDS | RC-01…RC-30 (10_) condensados em 15 |
| NEGATIVE_RESULTS | 05_, EVID-BRAS-002/006/007, EVID-QUAL-007/016, EVID-CAIN-005 |
| LIMITATIONS | 12_ §E, 19_ |
| LINEAGE | 11_ |
| ARCHITECTURE_ILLUSTRATIVE | EVID-CAIN-002, EVID-ECO-020, EVID-CORE-004 (só princípios) |
| NEXT_EXPERIMENTS | EVID-CAIN-007, EVID-ECO-029, 13_ |
| FUNDING | 12_, 18_ |

## O que foi deliberadamente excluído do público

Nomes de repositórios, de hipóteses, de gates, fases, regras, missões, arquivos, caminhos, SOs secundários, contagens de fases; valores de IC/bps; universos, janelas, custos; schemas; contratos; RAW_LOGS; PII; incidente de credencial em detalhe; hipótese comercial detalhada; qualquer URL.

## Checagens feitas no rascunho

- 33 hashes únicos do Evidence Pack conferidos programaticamente contra os artefatos reais (1 erro de digitação corrigido).
- 0 nomes de terceiros, 0 URLs, 0 caminhos locais, 0 padrões de segredo, 0 nomes de repositórios privados.
- Todo número público tem origem em um Evidence ID das Fases 1–2.
