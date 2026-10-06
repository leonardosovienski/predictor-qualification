# 08 — Metadados da auditoria (Fase 1)

- **Janela:** 2026-10-06, ~00:28Z → ~02:10Z (duas execuções: a primeira sem `predictor-qualification`; a segunda após provisionamento e autorização explícita do proprietário para a Fase 1 completa).
- **Raiz local:** `/home/user/`.

## Repositórios locais e estado Git

| Repo | Disponível | HEAD | Branch | Shallow | Commits | Tags | Branches remotas | WT inicial | WT final |
|---|---|---|---|---|---|---|---|---|---|
| ecosystem-predictor-cain | sim | `602f369d7a8f2f91bf7b5e26d237908badc1dd02` | `claude/audit-ecosystem-predictor-cain-jlna7o` (= main = origin/main) | inicial shallow (83 commits); aprofundado por `fetch --depth=1000 origin main --tags` → completo (267, 14 tags) | 267 | 14 | 2 | limpa | limpa |
| predictor-qualification | sim (clone completo 2026-10-06T01:09:35Z) | `d9f02169d7bdd87cb565d8262cf5238d0aa3373c` | main | não | 315 | 0 | 2 | limpa | **8 arquivos não rastreados em `showcase-audit/`** (criados por esta auditoria; sem commit) |
| cain | sim (clone completo 01:55Z) | `abeb1e6011537bea2d8a0d87334780f8370f1cbd` | main | não | 408 | 10 | 1 | limpa | limpa |
| brasileirao-predictor | sim (clone completo 01:57Z) | `1e0c6f0b31e7cdc514190f08d5d2ff9689bd905d` | main | não | 379 | 6 | 3 | limpa | limpa |
| core-predictor | sim (clone completo 01:57Z) | `956891ea728f8e1e038cbfebb7f0148abc77f700` | main | não | 129 | 10 | 2 | limpa | limpa |
| stocks-predictor | não | — | — | — | — | — | — | — | BLOCKED (acesso negado pelo controle de permissões da sessão) |
| predictor-ops | não | — | — | — | — | — | — | — | BLOCKED (idem) |
| cripto-predictor | não (acesso concedido; clone negado) | — | — | — | — | — | — | — | BLOCKED |

Alterações preexistentes do usuário: nenhuma em nenhum repo. Nenhum commit, amend, rebase, merge, reset, clean, stash, tag, branch ou push foi feito. Nenhuma configuração de repositório remoto (visibilidade, permissões, apps) foi tocada. Operações de rede executadas após autorização do proprietário: 4 `git clone` + 1 `git fetch` (aprofundamento) — todas somente leitura.

## Comandos/testes de alto nível

- Leitura: `git log/show-ref/for-each-ref/cat-file/ls-files/diff-filter=D`, `cat/sed/grep`, listagem de zips em memória, `sha256sum`.
- Integridade: 10/10 atestados de harness (ECO) vs `evidence_sha256`; 13/13 `MANIFEST.sha256` (QUAL); 3/3 attestations de integração e 1/1 superseded vs hashes citados em ECO; 7/7 arquivos do teste conjunto (rc13 e rc12) vs hashes citados em ECO.
- Varredura de padrões de segredo no HEAD do ECO com saída redigida: 0 achados. Varredura do histórico completo: **bloqueada** pelo classificador da sessão (NOT_TESTED).
- Sandbox 1 (ECO, `git archive HEAD` → scratchpad; runner montado do cache local do uv: pytest 9.1.1, pluggy 1.6.0, packaging 26.2, pygments 2.20.0; Python 3.13.14; `TMPDIR` no sandbox; sem rede/credenciais): snapshot 10 passed; bundle 62; transport 20; protocol 218 (módulo de schemas, 7 testes, não coletado: `rpds` nativo ausente); raiz 54 passed em 3 módulos stdlib, 6 módulos não coletados (pydantic); `check_ecosystem_drift.py --offline-check` → `ECOSYSTEM_NO_DRIFT (OFFLINE)`; `sync_canonical_ecosystem_facts.py --offline-check` → `CANONICAL_SCOPE_OK`. Limitação: runner ≠ lock.
- Sandbox 2 (CORE, idem): 4 passed, 2 failed, 36 erros de coleta por `PackageNotFoundError` (metadata do pacote não instalada; sem rede para instalar) → NOT_TESTED/BLOCKED.
- Ambos os sandboxes removidos; scratchpad vazio ao final.

## Verificações bloqueadas

Clones de stocks/ops/cripto; suíte raiz ECO e suíte CORE completas; ruff/pyright/coverage; `compat/` joint-install; varredura de segredos do histórico; validação de CI runs remotas; tags/arquivo histórico do Cripto; fonte primária dos lacres Stocks; estado atual de `predictor-ops`.

## Arquivos criados pela auditoria

`predictor-qualification/showcase-audit/01_EXECUTIVE_DIAGNOSIS.md`, `02_INVENTORY.md`, `03_CLAIMS_LEDGER.md`, `04_EVIDENCE_REGISTRY.md`, `05_NEGATIVE_RESULTS.md`, `06_EXPOSURE_HISTORY.md`, `07_OPEN_QUESTIONS.md`, `08_AUDIT_METADATA.md`. Nenhum outro arquivo persistente foi criado nos oito repositórios. Nada foi commitado.

## Exposição (registro)

Fatos informados pelo proprietário: oito repos públicos até 2026-10-05; privados em 2026-10-05; `predictor-qualification` reaberto em 2026-10-06. Clone local concluído em 2026-10-06T01:09:35Z. Encerramento da janela: EXTERNAL_VALIDATION_REQUIRED. Esta pasta `showcase-audit/` está **não rastreada** e não será exposta por nenhuma ação desta auditoria; se o repositório ainda estiver público quando for commitada, ela será pública.

## Fase 2 — adendo (2026-10-06, ~02:15Z → ~02:40Z)

- Autorização: o proprietário confirmou que `predictor-qualification` voltou a privado e autorizou a Fase 2.
- Repositórios usados: os cinco clones da Fase 1 (sem novos clones; stocks/ops/cripto continuam BLOCKED pelo controle de permissões da sessão; nenhuma nova tentativa foi feita).
- Operações: somente leitura (`cat/sed/grep/git log/python -I` sobre JSON); nenhuma execução de testes nesta fase; nenhum sandbox criado; nenhuma rede.
- Estado Git final: ECO 602f369, QUAL d9f0216, CAIN abeb1e6, BRAS 1e0c6f0, CORE 956891e; working trees limpas exceto `predictor-qualification/showcase-audit/` (13 arquivos não rastreados). Nenhum commit, push, branch, tag.
- Arquivos criados na Fase 2: `09_PROJECT_MAP.md`, `10_RESEARCH_CARDS.md`, `11_RESEARCH_LINEAGE.md`, `12_FUNDING_EVIDENCE.md`, `13_MISSING_EVIDENCE_AND_OPPORTUNITIES.md`; `04_EVIDENCE_REGISTRY.md` e este arquivo receberam adendos.
- Não executado (Fases 3/4): narrativa pública, threat model, matriz de exposição final, projeto do repositório `ecosystem-predictor`.

## Fase 3 — adendo (2026-10-06, ~02:25Z → ~02:35Z)

- Autorização: proprietário aprovou a Fase 3 ("aprovo").
- Operações: somente escrita dos seis documentos abaixo, a partir das evidências das Fases 1–2; nenhuma leitura nova de repositório, nenhuma rede, nenhum teste, nenhum sandbox.
- Arquivos criados: `14_PUBLIC_NARRATIVE.md`, `15_IP_BOUNDARY.md`, `16_EXPOSURE_MATRIX.md`, `17_COMPOSITION_RISK_REPORT.md`, `18_FUNDING_NARRATIVE.md`, `19_SKEPTICAL_REVIEWER_ATTACK.md`. Todos rascunhos privados; nenhum aprovado para publicação.
- Decisões humanas pendentes listadas em `15_IP_BOUNDARY.md` §"Decisões de fronteira".
- Estado Git: inalterado (ECO 602f369, QUAL d9f0216, CAIN abeb1e6, BRAS 1e0c6f0, CORE 956891e); 19 arquivos não rastreados em `showcase-audit/`; nenhum commit.
- Fase 4 (projeto do repositório `ecosystem-predictor`, README em três níveis) não iniciada.

## Fase 4 — adendo (2026-10-06, ~02:50Z → ~03:05Z)

- Autorização: proprietário delegou as decisões pendentes e aprovou a Fase 4.
- Decisões tomadas: registradas em `20_SHOWCASE_DESIGN.md`.
- Operações: leitura dos artefatos para cálculo de sha256 (attestations, teste conjunto, atestados de harness, wheels); escrita de `public-draft/` (12 arquivos) e de `20_SHOWCASE_DESIGN.md`, `21_PUBLICATION_CHECKLIST.md`. Nenhuma rede, nenhum teste, nenhum sandbox, nenhum repositório criado, nenhum commit.
- Verificação: 33/33 hashes únicos do Evidence Pack público conferem com os artefatos; um erro de transcrição foi detectado e corrigido antes do fechamento.
- Estado Git: inalterado nos cinco repositórios; `predictor-qualification` com `showcase-audit/` não rastreado (21 arquivos privados + `public-draft/` com 12).
- Programa: Fases 1–4 concluídas em rascunho. Publicação não iniciada.

## Fase 5 — adendo (2026-10-06, 04:00Z → ~04:30Z)

- Pre-flight: HEADs inalterados (ECO 602f369, QUAL d9f0216, CAIN abeb1e6, BRAS 1e0c6f0, CORE 956891e); working trees limpas; QUAL com `showcase-audit/` não rastreado.
- Incidente operacional: uma rodada de edição falhou por diretório de trabalho inesperado; verificado em seguida que nenhum arquivo rastreado foi modificado (`git status` sem entradas ` M`). Edições refeitas com caminhos absolutos.
- Mecanismo autorizado de validação externa usado: listagem de repositórios da sessão (somente leitura). Resultado: `ecosystem-predictor` existe e está público → colisão de nome; `predictor-qualification` e `ecosystem-predictor-cain` também constam como públicos em 2026-10-06T04:01Z.
- Edições na camada pública: README (8), RESEARCH_CARDS (1), LINEAGE (3), EVIDENCE_PACK (12, incl. datas de emissão por `generated_at` e seção de semântica dos hashes), ARCHITECTURE (reescrita), FUNDING (reescrita), SECURITY (1). Nenhuma evidência privada alterada.
- Criados: `22_PUBLICATION_GO_NO_GO.md`, `23_BUILD_ALLOWLIST_AND_PROCEDURE.md`.
- Veredicto: CONTENT_REVIEW_STATUS = PUBLICATION_READY; PUBLICATION_GATE_STATUS = HUMAN_PRECONDITIONS_PENDING; repositório local limpo não construído; nenhum commit, remote, push ou alteração de visibilidade.
- Fim do programa (Fases 1–5). Nenhuma fase adicional será criada.

## Fase 5 — conclusão (2026-10-06, ~04:25Z → ~04:45Z)

- Decisões do proprietário recebidas e aplicadas na camada pública: `LICENSE` (CC BY 4.0) criado; `LICENSE-NOTICE.md` reescrito; contato = perfil GitHub em README, FUNDING e SECURITY; nota do pack ajustada para "integridade apenas, sem anterioridade". Hashes recalculados (13 arquivos).
- Revalidações: 33/33 hashes do pack conferem; zero achados em segredos, PII de terceiros, caminhos, nomes de repositórios privados, Evidence IDs, identificadores internos, termos de mecanismo, metadata; links internos válidos; URLs externas restritas à licença CC e ao perfil GitHub do proprietário.
- `git ls-remote` do remoto reservado: sem refs (vazio). Nenhum clone do remoto foi feito.
- Build: `/home/user/ecosystem-predictor` criado com `git init -b main`; 13 arquivos copiados da allowlist; sha256 idênticos origem/destino; `git status` lista exatamente a allowlist; 0 remotes; 0 commits.
- Commit e push **não executados**: o classificador de permissões do ambiente negou configurar a identidade Git do proprietário (PII). Registrado como `PUBLICATION_BLOCKED_GIT_EMAIL`. Comandos exatos para o proprietário em `23_PHASE5_FINAL_REPORT.md`.
- Nenhum repositório privado tocado; nenhum conteúdo de `showcase-audit/` copiado para o build.

## Publicação (2026-10-06, 05:40Z → 05:46Z)

- Autorização explícita do proprietário para commit e push após informar ter tornado privados os dois repositórios; a listagem da sessão ainda os exibia como públicos às 05:40Z (possível cache) — registrado para confirmação humana.
- Identidade do commit: `Leonardo Sovienski <86319239+leonardosovienski@users.noreply.github.com>` (configuração local ao novo repositório; endereço noreply do GitHub presente em centenas de commits do proprietário; nenhum e-mail pessoal usado, nenhuma identidade Claude/Anthropic).
- Commit `a0adb71323533c848f85e2504e23fd50a51c2ade`, mensagem `Initial public research showcase`, 13 arquivos, sem trailers.
- Remote `origin` = `https://github.com/leonardosovienski/ecosystem-predictor.git` adicionado ao novo repositório apenas; `git ls-remote` vazio antes do push; `git push -u origin main` OK; pós-push: `refs/heads/main` = commit local; árvore remota idêntica (hash `27b324e6c2d517040b90b11a6b9ee664bacd4655`); 0 arquivos de `showcase-audit/`.
- Repositórios privados: nenhum arquivo rastreado alterado; nenhum remote, commit ou push neles; `showcase-audit/` segue não rastreado e não publicado.
- Programa encerrado definitivamente. Sem Fase 6.
