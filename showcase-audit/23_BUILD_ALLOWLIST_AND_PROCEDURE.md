# 23 — Allowlist de construção, hashes finais e material para carimbo externo (Fase 5)

Status: **preparado, não executado.** A construção do repositório local limpo só ocorre quando `CONTENT_REVIEW_STATUS = PUBLICATION_READY` **e** `HUMAN_PRECONDITIONS_SATISFIED` (ver 22_). Hoje: READY / PENDING.

## Allowlist (13 arquivos; sha256 dos bytes aprovados em 2026-10-06, versão final com licença e contato — ver tabela atualizada em 23_PHASE5_FINAL_REPORT.md)

| Caminho público | Bytes | SHA-256 |
|---|---|---|
| `CONTRIBUTING.md` | 260 | `e25d9d9dc2ecd7ba02d10cce066e2ec740c414f82d0429012fde7174c13171c8` |
| `LICENSE-NOTICE.md` | 441 | `d1caaa613031a2a94c28d02a3cab4c2b92bc945186effb12fba2e66f2738277e` |
| `README.md` | 6313 | `a8c2e434f451854200ee32131c44d36cc31484d553b4354ffb490158230f83db` |
| `SECURITY.md` | 280 | `2d8da7d9fb728f191c124705dd728cb13c59bf516b1f1458db74ba1f4c956af7` |
| `docs/ARCHITECTURE_ILLUSTRATIVE.md` | 2540 | `9cdffda3aab7577d2a3ad638e9af56e8764cb64beb237711246e8c170d2b7248` |
| `docs/EVIDENCE_PACK.md` | 7848 | `b6f1bbe5d4eef9cb36f066666192024d65253e5e16efb26fac84a0a4c49c9227` |
| `docs/FUNDING.md` | 2663 | `27abe20d040025a0a4d6eb80ea49462e6dbd190f90b04b609fbd4c717f61a4d3` |
| `docs/LIMITATIONS.md` | 1952 | `29066cd30496bd9c4e7db8057147a4c91fcb4c8be28ae2e4f439252b7dcb5c26` |
| `docs/LINEAGE.md` | 4610 | `22fc90177a24fe78e7bdbc9157e3a60b58680956affc2d55f46980032ddbc128` |
| `docs/NEGATIVE_RESULTS.md` | 4057 | `2e66babc135a8967b8ca22457cfc0ad611dfe30bdcc4b5ed9b68c1978428a0cb` |
| `docs/NEXT_EXPERIMENTS.md` | 2071 | `76345d4754748780e6fdaf205f63116252eba02b2b9111694b3291a016a1de11` |
| `docs/RESEARCH_CARDS.md` | 5524 | `5223befea2138f90e40b0a14dbb46c474a44861edb1b53acf27a82296d683039` |

Qualquer edição posterior (licença, contato, nome) altera bytes e exige recálculo desta tabela e do carimbo.

## Itens que mudarão por decisão humana antes do build

- `LICENSE` (arquivo novo) e ajuste de `LICENSE-NOTICE.md` → H3.
- Substituir `PUBLIC_CONTACT_PENDING` em `docs/FUNDING.md` e `SECURITY.md` → H4.
- Título do README se o nome mudar → H2.

## Material para carimbo externo (H5)

Objeto a carimbar: `docs/EVIDENCE_PACK.md` **na versão final após H2–H4**, identificado pelo seu sha256 (hoje `b6f1bbe5…`; será recalculado). Procedimento humano: (1) congelar o arquivo; (2) submeter o digest a um serviço público de timestamping (ex.: OpenTimestamps); (3) guardar a prova (`.ots` ou equivalente) e adicioná-la ao repositório público junto ao digest; (4) registrar em 08_ a data da âncora. Só então o pack pode afirmar `TEMPORAL_PRECOMMITMENT` para o próprio pack (não para os artefatos privados retroativamente).

## Procedimento de construção (quando os gates permitirem)

1. `mkdir <novo-diretório>` fora dos oito repositórios; `git init` novo (nunca reutilizar `.git`, worktree, clone ou fork de privado).
2. Copiar **somente** os 12 arquivos da allowlist (mais `LICENSE` e prova de carimbo quando existirem), preservando caminhos.
3. Verificar byte a byte: `sha256sum` de cada arquivo copiado contra esta tabela (recalculada se houve edição).
4. Verificar ausência de qualquer outro arquivo (`git status` deve listar exatamente a allowlist).
5. Um único commit inicial local, sem remote configurado.
6. PARAR. Publicação remota (criar repositório, configurar remote, push, visibilidade) é exclusivamente do proprietário.
