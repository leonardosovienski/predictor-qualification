# Fase 0 — Higiene do stack: resumo

Missão: `prompts/fase0_higiene_rev8.md` (núcleo v2.0, sha256 `50e8f498…ee36e1`, conferido no C0).
Nada foi qualificado nesta fase: o objetivo é que o `STACK_BASELINE_V1` nasça sem bloqueio.
Nenhum treinamento iniciado, nenhum capital movido, nenhuma instalação operacional alterada.

## Estado dos itens

| Item | Estado | Evidência | Commits / PRs |
|---|---|---|---|
| HYG-010 kit no `main` | DONE | `HYG-010.md` | predictor-qualification `1819e05` |
| HYG-011 clone do Ecosystem | DONE | `HYG-011.md` | — |
| HYG-005 preservação do CAIN | DONE | `HYG-005.md` | — (local, `C:\QUALIFICACAO\preserve\cain-24f784c-20260922`) |
| HYG-001 releases rc do protocolo | DONE | `HYG-001.md` | 3 tags em ecosystem `a879525` |
| HYG-002 `cain` uv.lock, sem vendor | DONE | `HYG-002.md` | cain#8 |
| HYG-003 `cripto` protocolo pela release, V1 fora | DONE | `HYG-003.md` | cripto#124, #125 |
| HYG-009 `stocks` Core `>=3.2.1,<4` | DONE | `HYG-009.md` | stocks#91 |
| HYG-008 suíte do Ops Linux/Windows | DONE | `HYG-008.md` | — |
| HYG-012 runtime Windows + VM Linux | DONE | `HYG-012.md` | predictor-qualification#2 |
| HYG-015 workflows V1 aposentados | DONE | `HYG-015.md` | stocks#92, cripto#125, core#32, cain#9, ecosystem#26, brasileirao#75 |
| HYG-004 CI por `uv sync --locked` | DONE | `HYG-004.md` | cain#8, cripto#124, core#33, ops#25, ecosystem#27, brasileirao#76 |
| HYG-006 clones limpos = `origin/main` | DONE | `HYG-006.md` | — |
| HYG-007 CI verde nos 7 `main` | DONE | `HYG-007.md` | 7/7 success |

**Todos os 13 itens estão `DONE`.** Os 7 repositórios têm `uv.lock` versionado, instalam o stack
só pelo lock no CI e estão com o CI verde no `main`. Os 7 clones de qualificação estão limpos e
iguais ao remoto. O `STACK_BASELINE_V1` (prompt `baseline_comum_rev8.md`) pode partir deste estado:

| Repo | `main` final |
|---|---|
| cain | `8b8915aa7c9053b8f078a9fba20b7029180d114c` |
| ecosystem-predictor | `0a4f87e53d3d131e449096f82ba7b0c672b91d85` |
| core-predictor | `5a0841509f091ea0aa95bde0d3d65e2a1a9e984d` |
| predictor-ops | `7bd99ebaea09c74a2ac4243d8991a81c44625a6c` |
| brasileirao-predictor | `e14f3394c1908fae6d2f25754e6ab3a6792dbf1e` |
| cripto-predictor | `5fd4e1b06c79231fd3d9485a1483f3b65e854bea` |
| stocks-predictor | `4e98a67b68c55888a4788663f3d5bf0899966cb4` |

## Decisões tomadas na fase (em `DECISIONS.json`)

- **D-14:** as rc do protocolo são publicadas do build LF canônico. Os hashes "auditados" vinham de
  uma árvore Windows com fim de linha misto.
- **D-15:** jobs de CI de push/PR que instalam o stack fora de lock saem para workflows só
  `workflow_dispatch` (Ecosystem: 4 jobs; Ops: `consumer-contracts`).
- Decisão do dono sobre HF-004: os 17 objetos git do CAIN só seriam apagados se fossem inúteis. Estão
  em uso por 10 worktrees, então nada foi apagado.

## Wheels do stack publicadas nesta fase

| Pacote | sha256 |
|---|---|
| predictor-research-protocol 1.0.3rc1 | `312ab9742271de9f0efe6912f5828122d546751e559f493bede01c8fc6a24032` |
| predictor-research-snapshot 1.0.2rc1 | `3bd4c0414ac2d457923601e3f919f6353b5cb9370a0f420a7a3ffc013a0aafad` |
| predictor-research-bundle 1.0.1rc1 | `65cf40c59c4f65d013a1134051fb94aa7c75b44f4ea6c71a54e25519143d0ea9` |

Core 3.2.1 (`10ef42f3…`) e Ops 4.2.1 (`da4fa540…`) não mudaram.

## Achados (todos P2) — `FINDINGS.md`

HF-001 hashes auditados não reproduzíveis (EOL) · HF-002 releases sem imutabilidade nativa ·
HF-003 caminhos longos no Brasileirão · HF-004 mtime de objetos do CAIN (fechado) · HF-005 17 e não
14 caminhos sujos · HF-006 versão do `cain` divergente (corrigido) · HF-007 modo online do drift ·
HF-008 arquivos congelados fora do formatter · HF-009 CVEs no lock do Cripto (corrigido, ccxt subiu) ·
HF-010 `release.yml` por tag.

## Dependências compartilhadas

SHARED-003 (`test_timeout_and_truncation`, Ops 4.2.1) registrada em `SHARED_ISSUES.json` como
`NOT_REPRODUCED_IN_TRIAGE`. O veredito é da missão `crypto`.

## Ferramentas locais da qualificação

uv 0.12.18 (sha256 `cae6a3bc…`) e CPython 3.13.14 gerenciado, em `C:\QUALIFICACAO\tools\`. Para
Cripto, cache/temporários/venv ficam em `C:\Cripto\qualificacao\`. Nada foi instalado no Python do
Windows. Para o Stocks não foi usado Python local.
