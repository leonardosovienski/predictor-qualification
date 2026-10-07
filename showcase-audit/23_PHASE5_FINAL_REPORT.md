# 23 — Relatório final da Fase 5 (2026-10-06)

## Resultado

| Item | Estado |
|---|---|
| CONTENT_REVIEW_STATUS | **PUBLICATION_READY** |
| Nome | `ecosystem-predictor` — remoto `leonardosovienski/ecosystem-predictor` reservado pelo proprietário; `git ls-remote` em 2026-10-06 sem refs (vazio) |
| Licença | CC BY 4.0 (textos); código futuro separado |
| Contato público | perfil GitHub do proprietário; nenhum e-mail publicado |
| Carimbo externo | não bloqueante; pack declara hashes como integridade apenas |
| Build local | **concluído**: `/home/user/ecosystem-predictor`, `git init -b main`, 13 arquivos, byte-idênticos à allowlist, 0 remotes, 0 commits |
| Commit local | **criado** após autorização explícita do proprietário: `a0adb71323533c848f85e2504e23fd50a51c2ade`, autor `Leonardo Sovienski <86319239+leonardosovienski@users.noreply.github.com>` (endereço noreply do GitHub já usado em centenas de commits do proprietário; nenhum e-mail pessoal), mensagem `Initial public research showcase`, sem trailers; 1 commit no histórico |
| Push | **executado** em 2026-10-06T05:45Z para `https://github.com/leonardosovienski/ecosystem-predictor` (`main`); remoto confirmado vazio imediatamente antes; após o push `refs/heads/main` = `a0adb713…`; árvore remota (hash `27b324e6…`) idêntica à local; 13 arquivos; 0 ocorrências de material de `showcase-audit/` |
| `showcase-audit/` | nenhum arquivo copiado nem publicado |

## Visibilidade dos repositórios (listagem da sessão, 2026-10-06)

| Repositório | Observado | Decisão do proprietário | Ação |
|---|---|---|---|
| ecosystem-predictor | public | public | OK |
| ecosystem-predictor-cain | public na listagem da sessão às 05:40Z (proprietário informa ter tornado privado; possível cache da API) | private | confirmar no GitHub |
| predictor-qualification | public na listagem da sessão às 05:40Z (idem) | private | confirmar no GitHub |
| cripto, ops, core, brasileirão, stocks, f1, lol, cs, wc, nba | private | — | OK |

## Allowlist final (13 arquivos) — sha256 dos bytes em `/home/user/ecosystem-predictor`

| Arquivo | Bytes | SHA-256 |
|---|---|---|
| `CONTRIBUTING.md` | 260 | `e25d9d9dc2ecd7ba02d10cce066e2ec740c414f82d0429012fde7174c13171c8` |
| `LICENSE` | 857 | `8c63b2d739841a893eab7b042988f116926468849cb2c5230a4ae0a13e7de091` |
| `LICENSE-NOTICE.md` | 501 | `f03ef4b58ecdf9df8835276ff8e1479ea9629d7a22b1039dd05ec26b4429ccf6` |
| `README.md` | 6473 | `ff31d7c6717997000703739f1e43d5fe8c65535752ac1c650d0764fe97d4319d` |
| `SECURITY.md` | 400 | `189504cc7c20e72441e447e1ccc424647f547f5e00aeb30d8fd3373168641caf` |
| `docs/ARCHITECTURE_ILLUSTRATIVE.md` | 2540 | `9cdffda3aab7577d2a3ad638e9af56e8764cb64beb237711246e8c170d2b7248` |
| `docs/EVIDENCE_PACK.md` | 7871 | `296af37782f6709c0a61b233abe0bcff8ffd7d8c889f9ae3e6e18ab7fffa7178` |
| `docs/FUNDING.md` | 2733 | `5ff2f7a655cf6c879e2661846a6e716e1769d54ec6bae9ce81084b0038135b3e` |
| `docs/LIMITATIONS.md` | 1952 | `29066cd30496bd9c4e7db8057147a4c91fcb4c8be28ae2e4f439252b7dcb5c26` |
| `docs/LINEAGE.md` | 4610 | `22fc90177a24fe78e7bdbc9157e3a60b58680956affc2d55f46980032ddbc128` |
| `docs/NEGATIVE_RESULTS.md` | 4057 | `2e66babc135a8967b8ca22457cfc0ad611dfe30bdcc4b5ed9b68c1978428a0cb` |
| `docs/NEXT_EXPERIMENTS.md` | 2071 | `76345d4754748780e6fdaf205f63116252eba02b2b9111694b3291a016a1de11` |
| `docs/RESEARCH_CARDS.md` | 5524 | `5223befea2138f90e40b0a14dbb46c474a44861edb1b53acf27a82296d683039` |

## Revalidações executadas após as decisões

Claim review (nenhum claim alterado além de licença/contato/nota de integridade); Evidence Pack 33/33 hashes conferidos contra os artefatos privados; IP red team e composição: sem alteração de substância, nenhuma inferência HIGH; varreduras: 0 segredos, 0 PII de terceiros, 0 caminhos, 0 nomes de repositórios privados, 0 Evidence IDs, 0 identificadores internos, 0 termos de mecanismo, 0 comentários/controle/marcadores pendentes; links internos válidos; URLs externas apenas CC BY 4.0 e perfil GitHub do proprietário.

## Comandos executados pela sessão (registro; não é mais necessário rodá-los)

No diretório já construído, com a identidade escolhida (substitua o e-mail pelo que você usa no GitHub; o endereço `noreply` do GitHub também serve):

```sh
cd /home/user/ecosystem-predictor
git config user.name  "Leonardo Sovienski"
git config user.email "<seu-email-do-github>"
git add -A
git status --short            # deve listar exatamente os 13 arquivos acima
git commit -m "Initial public research showcase"
git remote add origin https://github.com/leonardosovienski/ecosystem-predictor.git
git ls-remote origin          # deve continuar vazio antes do push
git push -u origin main
git ls-remote origin          # confirma refs/heads/main = SHA do commit
```

Verificação pós-push sugerida: `git ls-tree -r --name-only origin/main` deve listar exatamente os 13 arquivos; nenhum arquivo de `showcase-audit/`.

## Verificação pós-publicação (executada 2026-10-06T05:45Z)

- `git ls-remote origin`: `refs/heads/main` = `a0adb71323533c848f85e2504e23fd50a51c2ade` = HEAD local.
- `git fetch` + `git ls-tree -r origin/main`: exatamente os 13 arquivos da allowlist; hash de árvore remoto = local.
- Nenhum arquivo de `showcase-audit/`, Evidence Registry, Claims Ledger, IP Boundary ou Composition Risk Report no remoto.
- URL pública: https://github.com/leonardosovienski/ecosystem-predictor

## Pendências humanas remanescentes (fora do conteúdo)

1. Confirmar no GitHub que `ecosystem-predictor-cain` e `predictor-qualification` estão privados (a listagem da sessão ainda os mostrava públicos às 05:40Z).
2. Recomendado, não bloqueante: reemitir as três attestations; tratar PII/dumps nos privados; conferir candidaturas.

Programa encerrado. Nenhuma fase adicional.
