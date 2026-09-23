# BASELINE COMUM — SHARED-001 e SHARED-002 (Rev 8 — enxuto)

Núcleo: `qualification/COMMON_QUALIFICATION_CORE.md` v2.0, sha256 =
`50e8f49859daae6dcdf17164781d1837d8b656796924c35060f8d35855ee36e1`. Um único agente, sem subagentes. Pré-condição: todos os itens
de `qualification/HYGIENE.json` em `DONE` no `main`.

1. **SHARED-001** — `qualification/shared/STACK_BASELINE_V1.json` com os 7
   clones de qualificação: HEAD (= `origin/main`), branch, limpo/sujo, versão,
   sha256 do `uv.lock`, wheels consumidas e seus sha256, Python, SO, schemas,
   migrations e workflows de CI (C3).
2. **SHARED-002** — cleanroom-baseline (C5) de cada repo no GitHub Actions
   (Linux × py3.13), instalando só wheels publicadas; nada de "equivalente
   local". Relatório em `qualification/shared/SHARED-002/CLEANROOM_REPORT.md`.
   É diagnóstico: registre o que quebra, não conserte aqui.
3. `qualification/shared/SHARED_ISSUES.json` atualizado com o que aparecer.

Tudo por PR neste repo; não faça merge. Quando o dono fizer merge, a Etapa A
pode começar.
