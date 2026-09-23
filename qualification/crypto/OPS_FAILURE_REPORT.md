# OPS_FAILURE_REPORT — missão crypto, fase `ops-failure`

Wheel sob exame: `predictor-ops 4.2.1` (`da4fa540…6f0e`), fonte `7bd99eb` (igual à tag v4.2.1 em
`src/`, `tests_v2/`, `pyproject.toml` e `uv.lock`). Matriz congelada em `FROZEN_PARAMETERS.json`
(`shared_003`, `shared_004`). Todos os números saem de
`RAW_LOGS/ops-failure/OPS_FAILURE_SUMMARY.json`, gerado por `scripts/analyze_ops_failure.py`
a partir dos logs brutos (um log por execução).

## Resumo

| Issue | Classificação | Bloqueia? | Veredito |
|---|---|---|---|
| SHARED-003 `test_timeout_and_truncation` | `test_only` | não | `qualification/shared/SHARED-003/SHARED_DEPENDENCY_VERDICT.json` |
| SHARED-004 3 testes de proveniência strict | `test_only` | não | `qualification/shared/SHARED-004/SHARED_DEPENDENCY_VERDICT.json` |
| SHARED-005 (nova) lock local entre processos no Windows | `flaky` | **sim** | `qualification/shared/SHARED-005/SHARED_DEPENDENCY_VERDICT.json` |

## SHARED-003: o timeout do Ops no Windows funciona

**O job real mata a árvore e trunca a saída no Windows.** Com `run_job` da wheel 4.2.1, sem
mock, um filho que cria um neto e trava foi morto por timeout, com filho e neto mortos e a
saída truncada no limite. Isso vale em 3/3 no Windows local (source), 3/3 no Windows local
(wheel), 6/6 no `windows-latest` e 21/21 no Linux.

Teste isolado: **72/72** passaram em toda a matriz (Linux source 30, Linux wheel 20,
Windows local source 10 e wheel 10, `windows-latest` 2). A falha se reproduziu pela sonda
com o mesmo cenário via `run_job`: **1 em 80** no Windows local. A assinatura foi exit 124,
término `windows_job` por timeout e **0 bytes** de saída.

Causa, demonstrada por intervenção:

| Ambiente | Partida do filho (mediana, 20 medições) | Prazo 0,2 s, filho lento (`slow-start`) | Prazo 3 s (`ample`) |
|---|---|---|---|
| Linux (Actions) | ~0,012–0,013 s | 10/10 e 10/10 | 10/10 e 10/10 |
| windows-latest | ~0,047 s | 8/10 | 10/10 |
| Windows local | ~0,10–0,13 s (máx. 0,16 s) | **0/10 e 0/10**, sempre 0 bytes | 10/10 e 10/10 |

O teste exige que o filho parta *e* escreva em 0,2 s. No Windows a partida consome quase todo
esse prazo. Quando passa dele, o Ops mata o filho corretamente, mas ainda não há saída. O
defeito é o pressuposto de tempo do teste, não o runtime.

Hipóteses do prompt:

- **H1** (árvore de processos): refutada; a árvore morre.
- **H2** (spawn atrasado): sustentada.
- **H3** (exit 124): refutada; o código é 124 em todos os ambientes.
- **H4** (leitura bloqueante): refutada; tudo termina em ~0,3 s.
- **H5** (`\r\n`): refutada; ficam exatamente 20 bytes.

## SHARED-004: os testes pressupõem instalação editable

Com a wheel, os 3 testes falharam em todas as execuções: Linux 3/3 por run, Windows local
3/3 e `windows-latest` 1/1. Com editable passaram em todas: Linux 3/3 por run e Windows 3/3.
O trace (`RAW_LOGS/ops-failure/shared004-trace/trace.log`) mostra que o caminho do runtime
das missões (`runner.py:237`, strict, sem `source_root`) valida a wheel corretamente.

Observação secundária (P2, proposta ao dono do Ops): o CLI
`predictor-ops provenance --source-root <fonte suja>` responde `VALIDATED` com a identidade
da *wheel*. Nenhuma missão usa esse comando nem `collect_provenance(source_root=…)`.

## SHARED-005 (nova): lock local do Ops no Windows

Na `tests_v2` completa com a wheel (Windows local),
`test_local_lock_has_one_winner_across_processes` falhou. Em execuções isoladas o resultado
foi 1/20 falha (source) e 0/20 (wheel). A assinatura é sempre a mesma: `PermissionError` em
`runtime.py:27` (`handle.flush()` dentro de `_mutation_guard`). O A/B determinístico
(`scripts/ops_lock_guard_ab.py`) confirmou a causa em 3/3. Com a guarda vazia e o byte 0
travado por outro processo, dá `PermissionError`. Com a guarda já inicializada, o processo
espera e entra.

Efeito: na primeira disputa concorrente por um `job_id` novo no Windows, o processo perdedor
morre com exceção dentro de `run_job` em vez de receber `SKIPPED`. Não há dois vencedores
nem efeito duplicado. Mas o comportamento instável está no lock de todo job do runtime no
Windows. Pela C13, **bloqueia** até a correção (`qualification/shared/SHARED-005/PROPOSED_FIX.md`),
que exige decisão do dono (Ops congelado).

## Erros de método (preservados, fora da contagem)

- Run `35831189005`: a variante wheel não instalou (`ensurepip -q` inválido). O script foi
  corrigido e passou a falhar alto no setup.
- A sonda `real-tree` no Windows tinha um bug de aspas antes da correção. As linhas inválidas
  foram preservadas.
- Na `tests_v2` completa pela wheel, 2 falhas vêm do método (árvore de teste sem `src/` e sem
  `CHANGELOG.md`): `test_wheel_record_tampering_fails_in_isolated_environment` e
  `test_changelog_latest_release_matches_package_version`.
