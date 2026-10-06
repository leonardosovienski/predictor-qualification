# 06 — Exposure History (Fase 1)

**Fato informado pelo proprietário (não verificado por esta auditoria):** os oito repositórios foram **públicos no GitHub até 2026-10-05**; em 2026-10-05 tornaram-se privados; em 2026-10-06 `predictor-qualification` foi reaberto exclusivamente para provisionamento (clone local concluído em 2026-10-06T01:09:35Z). Classificação adotada: conteúdo presente no histórico até 2026-10-05 = **exposição pública passada confirmada**; conteúdo posterior = exposto só na janela de 2026-10-06. O encerramento da janela permanece `EXTERNAL_VALIDATION_REQUIRED`. Não se conclui nada sobre acessos ou clones externos, nem que a privatização elimina cópias.

Consequência para o programa: o histórico Git de **todos** os privados é considerado contaminado por exposição; a vitrine `ecosystem-predictor` deve nascer com histórico independente (já era a regra), e qualquer "sanitização" deve assumir que o conteúdo abaixo já pode ser conhecido por terceiros.

| Projeto | Categoria | Localização histórica | Situação | Reconstruction Risk | Recomendação |
|---|---|---|---|---|---|
| QUAL | **Código integral** de `cain` (1,2 MB) e `stocks-predictor` (1,8 MB) em texto plano + índices AST (cain, stocks, qualificação) | `estudo-do-zero/evidencias/{cain,stocks-predictor}/source-text.txt`, `source-index.json` | presente no HEAD d9f0216; público até 2026-10-05 e em 2026-10-06 | HIGH | **HIGH_PRIORITY_EXPOSURE_REVIEW**; decisão humana sobre remoção/reescrita de histórico (fora desta fase) |
| QUAL | Revisão objeto a objeto do arquivo histórico do Cripto (773 objetos, nomes por hash) | `estudo-do-zero/evidencias/cripto-predictor/shared-archive-*-review.md` | presente | MEDIUM–HIGH | PRIVATE_ONLY |
| QUAL | 2.435 logs brutos (RAW_LOGS), 238 MB, incl. caminhos locais, usuários de máquina, runs | `qualification/**/RAW_LOGS/**` | presente | HIGH (composição) | PRIVATE_ONLY; nunca publicar bruto |
| QUAL | Regras do agente pressupondo "repos públicos" | `CLAUDE.md` | presente | LOW | Rever premissa após privatização |
| ECO | PII de 10 terceiros (nome, empresa, cargo, URL de perfil, mensagens) | `registries/commercial_discovery.json` desde ≥2026-09-03 | presente; público até 2026-10-05 | N/A (privacidade) | Remover do repositório; avaliar obrigação de tratamento de dados |
| ECO | Código de 6 repositórios (patches ~950 KB) | zip em `docs/audit-2026-08-31/` | presente; público | HIGH | PRIVATE_ONLY; considerar remoção |
| ECO | Cópia de código do bundle | `.ci/cain-supply/overlay.zip` | presente | HIGH | PRIVATE_ONLY |
| ECO | Caminhos Windows, usuário, porta, launcher | 18 arquivos | presente | LOW | Sanitizar antes de reaproveitar texto |
| ECO | Arquitetura antiga (gateway, scheduler, db, storage, cache, telemetry, migrations, docker, compose) | histórico Git 2026-07→09 (34 arquivos removidos) | só histórico; público até 2026-10-05 | MEDIUM | Histórico não serve de base ao público |
| ECO | Fixtures com JWT descrito como fictício (3 exceções gitleaks) | commit `9d53e53a…` (presente no histórico completo) | histórico | LOW–MEDIUM | NOT_TESTED (varredura do histórico bloqueada pela sessão); confiar no CI `security-history` + revisão humana |
| ECO | Incidente de credencial em logs locais (2026-07) | docs; logs nunca versionados (claim) | histórico | LOW | Lição genérica |
| ECO | 24 branches remotas históricas + 24 PRs | documentadas em `organization-20260913.md`; não clonadas | existência documentada | MEDIUM | Verificar remoto antes da Fase 3 |
| ECO | Nome `ecosystem-predictor` e URLs `github.com/leonardosovienski/ecosystem-predictor/...` | HEAD; releases e tags citadas | ativo | N/A | Colisão com a vitrine; EXTERNAL_VALIDATION_REQUIRED |
| CAIN | Código completo (408 commits), configs de domínio, política de decisão | repositório inteiro | público até 2026-10-05 | HIGH | Assumir conhecido; proteger evolução futura, não o passado |
| BRAS | Código completo, `data/trials.json` com parâmetros, contratos | repositório inteiro | público até 2026-10-05 | HIGH | Idem |
| CORE | Código completo, CHANGELOG, auditoria adversarial | repositório inteiro | público até 2026-10-05 | HIGH | Idem |
| STOCKS/CRIPTO/OPS | Código completo | não clonados aqui; fato de exposição informado | público até 2026-10-05 | HIGH | Idem; Fase 2 |
| CRIPTO | `docs/source_archive_20260908` (773 objetos) e tags `snapshot-2026-09-08`/`archive-source-20260908` | presente no HEAD estudado em 2026-09-30 (QUAL); tags não mencionadas em QUAL | BLOCKED (clone negado) | ? | Fase 2 |
| Todos | Git LFS | ECO: `.gitattributes` só `-text`; `git lfs ls-files` vazio | sem LFS em ECO | N/A | Checar demais na Fase 2 |

Diferenciação obrigatória: tudo acima é **existência local/histórica**. A exposição pública passada é fato **informado**, não observado por esta auditoria. Nenhum item é conclusão sobre acesso efetivo por terceiros.
