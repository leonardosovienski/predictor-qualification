# 22 — Publication GO / NO-GO (Fase 5 final)

**Veredicto**

| Dimensão | Status |
|---|---|
| `CONTENT_REVIEW_STATUS` | **PUBLICATION_READY** (após as correções desta fase; nenhuma crítica CRITICAL em aberto no conteúdo) |
| `PUBLICATION_GATE_STATUS` | **HUMAN_PRECONDITIONS_SATISFIED** para build (decisões de 2026-10-06: nome, licença CC BY 4.0, contato = perfil GitHub, carimbo externo não bloqueante); publicação autorizada pelo proprietário |
| `NAME_STATUS` | **NAME_VALIDATED** — o proprietário declarou que `leonardosovienski/ecosystem-predictor` foi reservado deliberadamente para a vitrine; `git ls-remote` em 2026-10-06 confirmou remoto sem refs (vazio) |
| `LICENSE_STATUS` | **RESOLVED** — CC BY 4.0 para textos (`LICENSE` + `LICENSE-NOTICE.md`); código futuro com licença separada |
| `PUBLIC_CONTACT` | **RESOLVED** — perfil público GitHub do proprietário; nenhum e-mail publicado |
| `EXTERNAL_TIMESTAMP` | não bloqueante por decisão do proprietário; pack descreve hashes só como integridade, sem anterioridade |
| Repositório local limpo `ecosystem-predictor` | **CONSTRUÍDO** em `/home/user/ecosystem-predictor` (git init novo, branch `main`, 13 arquivos byte-idênticos à allowlist, sem remote, sem commits). **Commit NÃO criado: `PUBLICATION_BLOCKED_GIT_EMAIL`** — o ambiente negou (classificador de PII) configurar a identidade Git do proprietário; o e-mail é determinável a partir dos commits dele, mas não pode ser aplicado por esta sessão |

Conteúdo aprovado (revisão repetida em 2026-10-06 após licença/contato: 13 arquivos, 33/33 hashes do pack conferidos, zero achados em segredos/PII/caminhos/identificadores/metadata, links válidos). Único bloqueio restante: commit e push exigem a identidade Git do proprietário, que esta sessão não pode configurar. Ação humana: executar os comandos de commit e push listados em `23_PHASE5_FINAL_REPORT.md`.

---

## 0. Achado de segurança prioritário (fora do conteúdo)

A listagem de repositórios da sessão em 2026-10-06T04:01Z mostrou **três repositórios do proprietário ainda `public`**: `predictor-qualification` (último push 2026-10-06T01:02Z), `ecosystem-predictor` (push 2026-10-05T23:56Z) e `ecosystem-predictor-cain` (push 2026-10-05T23:54Z). Os outros cinco estão `private`. Isso contradiz a confirmação dada ("já voltei pra privado") e mantém expostos: dumps de código em `predictor-qualification`, PII e patches em `ecosystem-predictor-cain`. **Ação humana urgente, fora desta execução: tornar os três privados.** Nenhuma alteração de visibilidade foi feita por esta auditoria (proibido).

## 6. Pre-flight

- UTC: 2026-10-06T04:00:55Z. HEADs: ECO `602f369`, QUAL `d9f0216`, CAIN `abeb1e6`, BRAS `1e0c6f0`, CORE `956891e`; STOCKS/OPS/CRIPTO `BLOCKED_LOCAL_REPO_MISSING`. Working trees limpas; QUAL com `showcase-audit/` não rastreado (preexistente desta auditoria; preservado). Nenhum arquivo rastreado foi modificado (verificado após um erro de diretório de trabalho que não afetou arquivos rastreados).
- `public-draft/`: 12 arquivos (4 na raiz, 8 em `docs/`), só Markdown. Relatórios privados usados: 03, 04, 05, 06, 10, 11, 12, 15, 16, 17, 19, 20, 21.

### HUMAN_DECISIONS_PENDING

| # | Decisão | Por que é humana | Bloqueia publicação? |
|---|---|---|---|
| H1 | Tornar privados `predictor-qualification`, `ecosystem-predictor`, `ecosystem-predictor-cain` | visibilidade remota | Sim (pré-condição da checklist) |
| H2 | Nome: `ecosystem-predictor` já existe como repositório público do próprio proprietário (colisão real); manter/renomear/usar `predictor-evidence` | identidade pública | Sim |
| H3 | Licença dos textos (recomendação CC BY-ND 4.0 é só recomendação) | direito autoral | Sim |
| H4 | Contato público (ou decidir que não haverá) | PII do próprio proprietário | Sim (checklist) |
| H5 | Carimbo externo de tempo do Evidence Pack (material em 23_) | ação externa | Sim (seção 11) |
| H6 | Reemitir ou isolar as três attestations que não revalidam no `main` antes de publicar, ou publicar como limitação (texto já pronto) | decisão de processo | Não (limitação já publicada); recomendado |
| H7 | Tratamento do PII e dos patches/dumps nos repositórios privados | dever de cuidado | Não bloqueia a vitrine; recomendado antes |
| H8 | Confirmar que nenhuma candidatura enviada contém número incompatível (ver §26) | material não disponível localmente | Não bloqueia; EXTERNAL_VALIDATION_REQUIRED |

## 7. Revisão claim-by-claim (resumo; ledger completo abaixo)

| Claim público (texto exato ou resumo) | Evidence ID | Scope / Valid At | Maturidade | Risco | Verif. | Decisão |
|---|---|---|---|---|---|---|
| "dozens of hypotheses judged against pre-registered criteria; zero approved for capital" (README) | EVID-ECO-023/030, EVID-BRAS-003, EVID-QUAL-006 | HISTORICAL 2026-07→09 | DECLARED/EXERCISED | LOW | HIGH | SUPPORTED_WITH_REWORDING (era "42+ pre-registered": o 42 incluía projetos fora do escopo; corrigido) |
| "Ten published packages pinned by hash in a single joint lock" | EVID-ECO-006 (`compat/`) | CURRENT | DECLARED | LOW | MEDIUM | SUPPORTED_WITH_REWORDING (era "eight repositories, twelve packages") |
| "a +44% backtest ROI explained as variance" | EVID-BRAS-006 | 2026-06-27 | EXERCISED | LOW | HIGH | SUPPORTED |
| "an LLM-derived signal whose recorded verdict showed correlation in the opposite direction" | EVID-ECO-030 | 2026-07-28 | DECLARED (fonte primária não local) | LOW | MEDIUM | SUPPORTED_WITH_REWORDING ("recorded verdict") |
| "a baseline contaminated by its own cohort" | EVID-BRAS-007 | 2026-08-26 | EXERCISED | LOW | HIGH | SUPPORTED |
| "an internal adversarial audit that broke the thesis … answered in the next release" | EVID-BRAS-002, EVID-CORE-002 | 2026-09-05/06 | EXERCISED | LOW | HIGH | SUPPORTED |
| "six attestations, zero critical findings, capital_permission=false" | EVID-QUAL-002 | emissão 2026-09-24→28 | EXERCISED | MEDIUM | HIGH | SUPPORTED (labels genéricos) |
| "58/58 joint test after 47/57, 56/58, 57/58" | EVID-QUAL-003 | 2026-09-28 | REPRODUCED (identidade) | LOW–MEDIUM | HIGH | SUPPORTED |
| "fifteen adversarial PIT attacks … equities circuit; canaries fail closed in all three domains" | EVID-QUAL-014/015/017 + FUTURE_CANARY (BRAS) | 2026-09-24/29 | EXERCISED | MEDIUM | HIGH | SUPPORTED_WITH_REWORDING (atribuição ao circuito de ações acrescentada) |
| "81 negative-control executions" | EVID-QUAL-013 | 2026-09-24 | EXERCISED | LOW | HIGH | SUPPORTED |
| "29 registered football trials: 1 confirmed, 6 refuted, 6 inconclusive" | EVID-BRAS-003 | HEAD 1e0c6f0 | PROVEN | LOW | HIGH | SUPPORTED_WITH_REWORDING ("registered", não "pre-registered": 2 exploratórias e 3 informativas) |
| "containment built and tested; comparative experiment proposed, not run" | EVID-CAIN-002/003/007, EVID-QUAL-010 | CURRENT | IMPLEMENTED+EXERCISED / ausência | LOW | HIGH | SUPPORTED + PROPOSED |
| "free-form synthesis by local models produced false conclusions despite exact quotes" | EVID-CAIN-005 | 2026-09-11 | EXERCISED | LOW | HIGH | SUPPORTED |
| "three of six attestations no longer re-validate" | EVID-QUAL-007 | 2026-09-30 | EXERCISED | LOW | HIGH | SUPPORTED |
| "an operational seal broken by documented decision" | EVID-QUAL-007 | 2026-09-30 | EXERCISED | LOW | HIGH | SUPPORTED |
| Evidence Pack §1–§4: 33 hashes | EVID-QUAL-001/002/003, EVID-ECO-009/027, released_architecture | datas internas | REPRODUCED (33/33 conferidos) | LOW–MEDIUM | HIGH | SUPPORTED |
| Evidence Pack §5 contagens | EVID-ECO-003/004/027, EVID-QUAL-001/003/013/014, EVID-BRAS-003 | 2026-10-06 | REPRODUCED/PROVEN | LOW | HIGH | SUPPORTED |
| Lineage: datas | EVID-*-001, EVID-CORE-005, EVID-BRAS-008, EVID-ECO-028 | commits/tags | PROVEN | LOW | HIGH | SUPPORTED (ver §9) |
| Research Cards 1–15 | RC-01…30 (10_) | diversas | mistas | LOW–MEDIUM | HIGH | SUPPORTED/SUPPORTED_WITH_REWORDING (card 15 sanitizado: "sem relógio"/"hash" removidos) |
| Negative results (16 + 11 linhas) | 05_ | diversas | DECLARED/EXERCISED | LOW | HIGH | SUPPORTED (números numéricos ausentes por desenho) |
| Architecture illustrative | EVID-CAIN-002, 15_ | DESIGN | — | MEDIUM→LOW após reescrita | MEDIUM | ILLUSTRATIVE (redesenhado como separações, sem sequência) |
| Next experiments E1–E6 | EVID-CAIN-007, EVID-ECO-029 | — | — | LOW | MEDIUM | PROPOSED (todos marcados) |
| Funding F1–F5 | 12_, 18_ | — | — | LOW | MEDIUM | SUPPORTED (reestruturado em cadeia evidência→limitação→recurso→milestone→output; "nenhum funding recebido" declarado) |
| "Hashes prove content integrity only; external timestamping pending" | — | — | — | LOW | HIGH | SUPPORTED (acrescentado) |

Nenhum claim ficou em NEEDS_EVIDENCE ou REMOVE após as correções. Nenhuma evidência privada foi alterada.

## 8. README — três horizontes

- 15 s: o que é (vitrine de evidência, não implementação), por que (avaliação > modelagem), linha (disciplina de evidência e agente contido), por que ler (pergunta aberta financiável). **Passa**; sem jargão privado.
- 2 min: feito / proof of work (pacote de hashes) / resultados / negativos / importância / próxima etapa / o que funding desbloqueia. **Passa.**
- 10 min: tabela com Evidence Pack, limitações, negativos, lineage, proposta vs resultado, arquitetura conceitual, próximos experimentos, funding. **Passa.** Dependência de informação privada: só para verificar hashes (declarado).

## 9. Lineage — classificação das conexões

| Conexão | Classe | Tratamento no texto público |
|---|---|---|
| prediction research → evaluation failures / negative results | SUPPORTED (datas e documentos) | fato |
| evaluation failures → qualification & reproducibility | SUPPORTED (auditoria 2026-09-05 → QUAL 2026-09-23; ADR-001) | fato |
| qualification → research infrastructure | PARTIALLY_SUPPORTED (infraestrutura aparece antes e depois) | "appears twice"; linguagem proporcional |
| research infrastructure → evidence/authority boundaries | PARTIALLY_SUPPORTED (contratos de capital fail-closed desde ago; política do agente em set) | proporcional |
| evidence/authority boundaries → CAIN / agentic research | INFERENCE_ONLY (sem documento de motivação datado) | marcado "Interpretation, not fact" |

## 10–11. Evidence Pack e hashes

Recalculado sobre os bytes aprovados: 33 digests únicos em 34 linhas (6 attestations vigentes, 3 superseded, 8 linhas do teste conjunto com 7 digests únicos, 10 atestados de harness, 7 wheels); 33/33 conferem com os artefatos privados. Datas de emissão trocadas de "data do commit" por `generated_at` interno dos artefatos (UTC). Categorias explícitas em §6 do pack: CONTENT_INTEGRITY sim; INTERNAL_TIMESTAMP sim; TEMPORAL_PRECOMMITMENT/EXTERNAL_TIMESTAMP **não** (declarado). Material para carimbo externo: em 23_.

## 12. Attestations superseded

As três publicadas (pilha anterior, 2026-09-28T15:25–15:38Z) foram substituídas no mesmo dia pelas vigentes (18:10–18:54Z) por mudança de pilha (correção de concorrência no transporte). Valor histórico: mostram a trajetória 57/58 → 58/58. Risco de confusão: baixo, com a frase obrigatória acrescentada. Reemissão: não se aplica a superseded; aplica-se às três **vigentes** que não revalidam (H6), já declaradas como limitação no pack e em LIMITATIONS.

## 13–15. Negativos, limitações, experimentos

Cada linha de NEGATIVE_RESULTS responde testado/veredicto/aprendido/mudou em nível seguro; nenhuma interpretação posterior apresentada como hipótese original (RC-02 explicitamente "retracted"). LIMITATIONS: 12 itens reais, incluindo exposição pública passada e revisão só por agentes. NEXT_EXPERIMENTS: E1–E6 todos PROPOSED; E1 reduzido a pergunta/braços/medidas conceituais.

## 16. Funding

Reestruturado em cadeia de cinco colunas; tipos de recurso separados; "nenhum funding, crédito, incubação ou acesso recebido" declarado.

## 17. Arquitetura

Redesenhada: tabela de papéis e proibições + diagrama de separações sem sequência; "no clock" e "hash-versioned" removidos; aviso obrigatório presente. Confrontada com 15_: dentro da camada ILLUSTRATIVE.

## 18. Revisão combinatória

Ataque "README + arquitetura + pack + cards + negativos + lineage + funding": inferências possíveis: (a) existem três domínios e um agente; (b) há um protocolo de qualificação com ~30 gates e estágios A/B; (c) versões dos pacotes e cadência de releases; (d) um lacre operacional e um atestado de poder existem. Nada disso permite reconstruir regras, schemas, parâmetros, universos, custos ou ordem real. Correlação removida nesta fase: contagem de repositórios ("eight") e pipeline sequencial do diagrama. Resultado: nenhum par LOW+LOW→HIGH remanescente identificado.

## 19. Metadata forensics

Só Markdown; sem comentários HTML, caracteres de controle, TODO, nomes de usuário, nomes de máquina, caminhos, URLs ou identificadores de sessão. Timestamps no texto são deliberados (evidenciais). Hashes recalculados após toda edição (23_).

## 20. PII e terceiros

Zero nomes de terceiros, zero e-mails, zero usernames. Sem imagens, logos, screenshots ou trechos de terceiros. Contato do proprietário: PENDING.

## 21–23. Licença, contato, nome

- LICENSE_STATUS = PUBLICATION_BLOCKED_LICENSE_DECISION (nenhum LICENSE criado; `LICENSE-NOTICE.md` declara "todos os direitos reservados até decisão").
- PUBLIC_CONTACT_PENDING (placeholder explícito; sem e-mail inventado).
- NAME: a listagem autorizada de repositórios da sessão mostra `leonardosovienski/ecosystem-predictor` **existente e público** (push 2026-10-05). Colisão real com repositório do próprio proprietário → PUBLICATION_BLOCKED_NAME_COLLISION. Não troquei para `predictor-evidence`. Opções humanas: renomear/arquivar o existente; escolher outro nome; ou reutilizar deliberadamente (não recomendado: o existente tem histórico contaminado por exposição).

## 24. Ataque do revisor cético

| Crítica | Severidade | Evidência existente | Correção | Status |
|---|---|---|---|---|
| Claim maior que evidência: "42+ pre-registered hypotheses" incluía projetos fora do escopo | HIGH | VEREDITOS cobre cs/lol/f1 | reescrito para "dozens … pre-registered criteria" | RESOLVIDA |
| Falta de reprodução externa: tudo é auditoria interna por agentes | HIGH | LIMITATIONS §8; F3 | declarado; funding pede revisão humana | ACEITA COMO LIMITAÇÃO DECLARADA |
| Dependência de evidência privada: hashes só verificáveis com acesso | MEDIUM | pack §6 | declarado; carimbo externo pendente (H5) | ACEITA; GATE H5 |
| Novidade pouco clara: "pré-registro e PIT não são novos" | MEDIUM | — | README não reivindica novidade metodológica; a contribuição declarada é corpus datado + contenção testada + pergunta aberta | RESOLVIDA (linguagem) |
| Cherry-picking: só sucessos de engenharia | MEDIUM | NEGATIVE_RESULTS 27 linhas; LIMITATIONS | publicado na mesma página que os resultados | RESOLVIDA |
| Narrativa retrospectiva: "lições → CAIN" | HIGH | sem documento de motivação | marcado "Interpretation, not fact" | RESOLVIDA |
| Lineage fraca: infraestrutura antes e depois | MEDIUM | 11_ | dito explicitamente ("appears twice") | RESOLVIDA |
| Hash sem significado semântico | MEDIUM | pack §6 | quatro categorias explícitas; "no semantic validity" | RESOLVIDA |
| Timestamp independente ausente | HIGH | — | declarado; H5 pendente; não publicar antes | GATE H5 |
| Viés de seleção nos negativos (só os que ficam bem?) | MEDIUM | 05_ cobre também achados contra o processo (attestations não revalidam, lacre quebrado, síntese falsa) | mantidos | RESOLVIDA |
| Funding desconectado de milestone | MEDIUM | FUNDING antigo era lista | cadeia de cinco colunas | RESOLVIDA |
| "QUALIFIED" soa como validação | HIGH | LIMITATIONS §11; README | definido como engenharia; estado econômico sempre ao lado | RESOLVIDA |
| Contagem de testes sem SHA no público | LOW | pack §5 datado | datas sim; SHAs privados não (por desenho) | ACEITA |
| Três repositórios ainda públicos contradizem a privatização declarada | CRITICAL (operacional, não de conteúdo) | list_repos 2026-10-06 | ação humana H1 | GATE H1 |

Nenhuma CRITICAL de conteúdo em aberto. A CRITICAL operacional é pré-condição humana.

## 25. IP red team — teste cego

**Passo A (só `public-draft/`), inferências registradas antes de consultar privados:**
A1 há três domínios e um agente proposer com política determinística; A2 existe protocolo de qualificação com estágios A (domínio) e B (integração) e ~30–32 gates; A3 há ~10 pacotes, versões rc, um core "3.2.1"; A4 há "atestados de poder" com validade de 7 dias e duas famílias de métrica; A5 existe um lacre operacional e lacres de configuração por hash; A6 o agente usa memória append-only e recuperação; A7 há envelopes/transporte entre agente e domínios; A8 futebol usa Elo+distribuição de gols; A9 cripto testou funding/OI e score LLM; A10 ações testaram momentum/baixa vol.

**Passo B (comparação com 15_ e privados):**
| Inferência | Classe | Nota |
|---|---|---|
| A1, A6 | LOW | princípios já na camada PUBLIC/ILLUSTRATIVE; sem regras, estados ou ordem |
| A2 | MEDIUM→LOW | contagem de gates publicada por decisão (16_); nomes de gates/fases ausentes |
| A3 | LOW | versões são metadados de release |
| A4 | LOW–MEDIUM | validade de 7 dias e "duas famílias" revelam existência, não mecanismo; famílias rotuladas A/B |
| A5 | LOW | existência, não conteúdo |
| A7 | LOW | "evidence-transport layer"; sem schema |
| A8–A10 | LOW | famílias genéricas já documentadas publicamente em literatura; sem parâmetros |
Nenhuma inferência HIGH. **Sem PUBLICATION_BLOCKED_IP_LEAK.**

## 26. Coerência com candidaturas

Nenhum material de candidatura (Emergent Ventures, BlueDot, Anthropic External Researcher Access, Z Fellows, 1517 Medici, Cohere Labs) encontrado nos repositórios locais. **EXTERNAL_VALIDATION_REQUIRED**: o proprietário deve conferir, antes de publicar, que números enviados (testes, qualificação, teste conjunto, hipóteses, vereditos) não contradizem o pack. Números que mais provavelmente aparecem em candidaturas e seus valores públicos aqui: 6 attestations QUALIFIED; 58/58; 29 trials (1/6/6); 15 ataques PIT; 81 controles; "zero capital".

## Construção do repositório local

Não executada (regra 5.3). Allowlist, hashes finais e procedimento prontos em 23_. Nenhum `git init`, nenhum commit.

## Pós-publicação (executar só após confirmação explícita do proprietário)

1. Recalcular sha256 dos arquivos publicados e comparar com 23_. 2. Confirmar visibilidade do público e privacidade dos oito privados. 3. Conferir que nenhum arquivo além da allowlist foi publicado. 4. Registrar commit público, data e URL em 08_. 5. Confirmar que o carimbo externo referencia o digest final do `EVIDENCE_PACK.md`.


## Atualização final (2026-10-06, ~04:40Z)

- Decisões do proprietário aplicadas: nome `ecosystem-predictor` (remoto reservado, confirmado vazio por `git ls-remote`); CC BY 4.0 nos textos; contato = perfil GitHub; carimbo externo não bloqueante.
- Estado de visibilidade reconferido às 04:3xZ: `ecosystem-predictor` public (correto); **`ecosystem-predictor-cain` e `predictor-qualification` continuam public**, contrariando a decisão "devem permanecer PRIVATE". Ação humana urgente (não executada por esta sessão: proibido alterar visibilidade).
- Build local concluído por allowlist; commit bloqueado por `PUBLICATION_BLOCKED_GIT_EMAIL` (restrição do ambiente, não do conteúdo).


## Publicação (2026-10-06T05:45Z)

Autorização explícita do proprietário recebida. Commit `a0adb71323533c848f85e2504e23fd50a51c2ade` (autor Leonardo Sovienski, endereço noreply do GitHub) enviado para `leonardosovienski/ecosystem-predictor`, branch `main`, remoto confirmado vazio antes do push. Verificação pós-push: árvore remota idêntica à local (13 arquivos), sem material de `showcase-audit/`. `PUBLICATION_BLOCKED_GIT_EMAIL` resolvido sem e-mail pessoal. Programa encerrado.
