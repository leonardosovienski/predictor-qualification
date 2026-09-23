# MISSÃO — FASE 0: HIGIENE DO STACK (Rev 8 — enxuto)

Núcleo: `qualification/COMMON_QUALIFICATION_CORE.md` v2.0, sha256 =
`50e8f49859daae6dcdf17164781d1837d8b656796924c35060f8d35855ee36e1`. Um único agente, sem subagentes.

Objetivo: deixar os 7 repositórios instaláveis, com versões certas e CI verde,
para que o baseline comum (`STACK_BASELINE_V1`) nasça sem bloqueio. Você não
qualifica nada aqui.

## Onde trabalhar

| Repo | Clone de qualificação |
|---|---|
| `cain`, `ecosystem-predictor`, `core-predictor`, `predictor-ops`, `brasileirao-predictor` | `C:\QUALIFICACAO\repos\<repo>` |
| `cripto-predictor` | `C:\Cripto\qualificacao\cripto-predictor` |
| `stocks-predictor` | `C:\STOCKS\work\qualification\stocks-predictor` |
| evidência | `C:\QUALIFICACAO\predictor-qualification` (este repo) |

Clone que não existir: `git clone https://github.com/leonardosovienski/<repo>.git`
no caminho acima. **Nada** em `C:\CAIN\` é alterado (`C:\CAIN\projeto` só leitura).
Stocks: não criar venv nem instalar nada no Python do Windows — valide pelo CI.

## Itens

Lista e critérios em `qualification/HYGIENE.json`. Ordem sugerida:

```text
HYG-010 → HYG-011 → HYG-005 → HYG-006 → HYG-001 → HYG-002 → HYG-003 → HYG-009
→ HYG-015 → HYG-004 → HYG-012 → HYG-007 → HYG-008
```

Para cada item:

1. Diga em uma linha o que vai fazer.
2. Trabalhe numa branch `hygiene/HYG-0xx-<resumo>` do repo afetado e abra PR.
   Nunca faça merge nem push em `main`.
3. Evidência em `qualification/shared/HYGIENE/HYG-0xx.md`: comandos, saída
   relevante, links de PR e de runs do CI, sha256 dos artefatos. Log bruto em
   `qualification/shared/HYGIENE/RAW_LOGS/`.
4. Quando o critério de aceite estiver cumprido **depois do merge do dono no
   repo afetado**, abra PR neste repo mudando o item para `DONE` em
   `HYGIENE.json`, com `evidence_file`, `evidence_sha256` e `commits`.
5. Siga para o próximo. Pare só quando precisar do dono (merge, decisão).

Você pode publicar releases pré-release (`rc`) — HYG-001 — com tag nova; nunca
sobrescreva asset existente.

## Pontos de atenção

* **HYG-003 (Cripto):** `predictor-research-protocol` hoje está declarado sem
  fonte e fora do `uv.lock` (não instala). Colocar a URL da release de HYG-001 em
  `tool.uv.sources`, regenerar o lock; sem `cain-research`;
  `tests/test_research_execution.py` → `legacy/v1_integration/`, fora de `testpaths`.
* **HYG-009 (Stocks):** `predictor-core>=3.2,<4` → `>=3.2.1,<4`, lock continua 3.2.1.
* **HYG-015:** os 7 workflows de integração V1 passam a só `workflow_dispatch`,
  com cabeçalho "aposentado por D-13". Não apagar.
* **HYG-004:** respeitar a exceção de C4 (smoke da própria wheel e `--require-hashes`).
* **HYG-008 / SHARED-003:** se `test_timeout_and_truncation` falhar, registrar em
  `qualification/shared/SHARED_ISSUES.json` e seguir; o veredito é da missão `crypto`.
* **Linux (D-9):** tudo que precisa de Linux roda no GitHub Actions.
* Achado fora do escopo do item → `qualification/shared/HYGIENE/FINDINGS.md`.
* Nunca escreva segredo em arquivo, log ou commit (repos públicos).

## Fim

Todos os itens `DONE` no `main` deste repo e um resumo em
`qualification/shared/HYGIENE/SUMMARY.md`.
