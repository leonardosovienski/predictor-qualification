# Auditoria adversarial do stack integrado — cain 0.4.13rc13 (2026-09-28)

**Pedido do dono:** "ler e testar tudo aos extremos, principalmente o cain; tudo pronto, validado e sincronizado".
**Sessão:** nuvem (Linux, uv 0.8.17, Python 3.13.12), clones dos cinco repositórios no estado do `main` de 2026-09-28:
cain `960fb25` (0.4.13rc13), ecosystem-predictor `bac1f7b`, core-predictor `5a08415`, predictor-ops `40c703a`,
predictor-qualification `d188810`. Nenhuma instalação operacional foi tocada; nenhum dado real; nenhum segredo.

Isto **não é uma missão** do núcleo (C23) e não emite attestation nem gate. É evidência auxiliar (C2: orienta,
nunca substitui execução) para o dono decidir o que entra nas missões. Todo número abaixo sai de um arquivo de
`RAW_LOGS/` desta pasta (C20); os sha256 estão em `SHA256SUMS`.

## 1. Estado das seis missões (lido do `main` `d188810`)

| Missão | Resultado | Gates fora de PASS | cain | transporte |
|---|---|---|---|---|
| crypto, brasileirao, stocks (Etapa A) | QUALIFIED | nenhum | — | — |
| integration-crypto | QUALIFIED | nenhum | 0.4.13rc13 `960fb25` | 0.1.0rc6 `bac1f7b` |
| integration-stocks | QUALIFIED | nenhum | 0.4.13rc13 `960fb25` | 0.1.0rc6 `bac1f7b` |
| integration-brasileirao | QUALIFIED | nenhum | **0.4.13rc12 `302a5c8`** | **0.1.0rc5 `b11494a`** |

**Sincronização pendente:** só o `integration-brasileirao` ficou na rc12/rc5. Pela C14 as fases de runtime dele são
refeitas na rc13/rc6; elas rodam só no PC 2 (dado privado, D-19), então esta sessão preparou a troca sem executá-la
(`qualification/integration-brasileirao/scripts/rc13_edits.py`, `RAW_LOGS/release-rc13/`, entrada no
`QUALIFICATION_CHANGELOG.md`). O `brasileirao.json` empacotado na rc13 é byte a byte o da rc12 (`f51ac735…`), e
`policy.py`, `service.py`, `store.py`, `config.py` também não mudaram entre as duas
(`RAW_LOGS/repro/wheels_rc12_rc13_transport_rc5_rc6.log`). O waiver IB-F009 continua valendo na rc13 (seção 4).

## 2. Suítes de CI dos cinco repositórios, localmente, com `uv sync --locked` (Python 3.13)

| Repositório | Comandos do CI | Resultado | Log |
|---|---|---|---|
| cain `960fb25` | `uv lock --check`, `ruff check .`, `pytest -q`, `python -m cain --help` | 1446 passed, 4 skipped | `RAW_LOGS/ci/cain_rc13_py313.log` |
| cain `960fb25` | idem em Python 3.11 e 3.12 | 1446 passed, 4 skipped (cada) | `RAW_LOGS/ci/cain_rc13_py311_py312_py314rc2.log` |
| cain `960fb25` | Python 3.14 | **não rodou**: só existe 3.14.0rc2 nesta nuvem, e `pydantic` quebra ao importar `fastapi` (`typing._eval_type(prefer_fwd_module)`); ambiente, não código; o CI usa o 3.14 final | mesmo log |
| cain `2807c23` (com as correções da seção 5) | `pytest -q --cov=cain --cov-fail-under=86`, `--help` | 1462 passed, 4 skipped; cobertura 87.76 % | `RAW_LOGS/ci/cain_patched_py313_cov.log` |
| core-predictor `5a08415` | `uv lock --check`, `lint-imports`, `coverage run -m pytest`, `coverage report --fail-under=80`, `ruff check` + `format --check`, `pyright` | 278 passed; cobertura 86 %; contratos 1 kept; 0 erros de tipo | `RAW_LOGS/ci/core-predictor.log` |
| predictor-ops `40c703a` | `uv lock --check`, `ruff`, `pyright`, `pytest --cov` (`-W error::ResourceWarning`), `posix_integration` | 88 passed + 1; cobertura 80.93 % (piso 80) | `RAW_LOGS/ci/predictor-ops.log` |
| ecosystem-predictor `bac1f7b` | raiz: `ruff`, `pyright`, `coverage run -m pytest …`, `--fail-under=75`, `sync_canonical_ecosystem_facts --offline-check`, `check_ecosystem_drift --offline-check`; pacotes: `pytest tests` de transport, protocol, snapshot, bundle | 165 passed (78 %); `CANONICAL_SCOPE_OK`; `ECOSYSTEM_NO_DRIFT (OFFLINE)`; pacotes 19 / 233 / 10 / 62 passed | `RAW_LOGS/ci/ecosystem-predictor.log` |
| ecosystem-predictor | `check_current_representation.py`, `check_architecture_manifest.py` | **não rodaram**: batem na API do GitHub (proxy TLS / 403 nesta nuvem); ficam para o CI hospedado | mesmo log |

## 3. Wheel publicada da cain rc13

- `uv build --wheel` + `tools/verify_wheel.py` (instalação não editável fora do checkout, requisitos com hash do lock):
  `verification: passed` (`RAW_LOGS/repro/cain_wheel_verify.log`).
- Build reprodutível como o `publish_rc.sh` (`SOURCE_DATE_EPOCH=1758240000`, duas árvores de `git archive 960fb25`,
  `uv build --no-cache`): as duas wheels locais são idênticas entre si (`32141ab4…`), mas **não** têm o sha256 do asset
  publicado (`a1d94fd5…`). O conteúdo extraído dos dois zips é idêntico arquivo a arquivo (`diff -r` vazio; mesmo
  `Generator: setuptools (84.0.0)`); a diferença está só no contêiner zip. O asset publicado bate com o sha256 das
  attestations e do `runtime_targets.json` (`RAW_LOGS/repro/cain_rc13_reproducible_build.log`). Nada a corrigir; fica o
  registro de que a reprodutibilidade byte a byte depende do ambiente do build, não do código.
- Transporte rc6 publicado: sha256 `6c7e83c4…` conferido no download anônimo.

## 4. Testes aos extremos do cain (orquestração, política, memória, transporte)

Suíte fora do repositório (`scripts_test_adv_cain.py`, 24 testes), rodada com o domínio substituto dos testes de
integração do cain (o lado do CAIN, o transporte e o protocolo são o código real). Cada teste grava as observações em
`NOTES_*.json`.

| Prova | rc13 `960fb25` (`pytest_rc13_960fb25.log`) | com as correções `2807c23` (`pytest_patched_2807c23.log`) |
|---|---|---|
| 10 `propose` em processos concorrentes no mesmo estado | episódios 1..10 contíguos, 1 ALLOW e 9 ABSTAIN (`max_open_tasks = 1`), 1 task, 0 traceback | igual |
| 8 `ingest` concorrentes do mesmo resultado | 1 linha no inbox, 1 fato, memória intacta, 0 traceback | igual |
| 8 `dispatch --resend` concorrentes | 1 arquivo de task | igual |
| 12 processos `propose`/`ingest` intercalados | 3 resultados ingeridos, memória intacta | igual |
| 372 mutações de campo único de um resultado válido | 364 rejeitadas, 6 ingeridas (só `adapter.*` e `outcome.reason`, texto livre que não entra na memória; nenhum segundo fato ou payload), **2 tracebacks** (`outcome.status` lista/objeto → `TypeError` do validador) | 366 rejeitadas, 6 ingeridas, 0 traceback |
| 12 arquivos-lixo no spool de resultados (vazio, NUL, BOM, NaN, float, 33 MB, chaves duplicadas, latin-1, CRLF, lista, string, **100 000 níveis**) | 11 rejeitados com código fechado; **aninhamento absurdo derruba o `ingest` com `RecursionError`** | 12 rejeitados |
| symlink para arquivo esparso de 200 MB | `SIZE_LIMIT` em 2 ms, sem ler | igual |
| 19 propostas-lixo pelo CLI (`propose` e `decision-receipt`) | tudo exit 2 ou recibo BLOCK, exceto: **aninhamento absurdo → traceback (exit 1)**; **`--as-of 2030-13-45T99:00:00Z` → ALLOW gravado e task emitida** | tudo exit 2 ou recibo BLOCK; `AS_OF_INVALID` |
| 15 IDs parecidos (`H9`, `Crypto:H9`, `crypto :H9`, `crypto:H9​`, `crypto::H9`, `stocks:H9`, NUL, 300 chars…) em `hypothesis_id`, `request_id`, `research_id`, `based_on`, `proposal_id` | nenhum ALLOW; tudo BLOCK R01/R02 | igual |
| `decision-receipt` sob `PYTHONHASHSEED` 0/1/4242, `TZ` Tóquio/São Paulo, `LC_ALL=C`, `PYTHONUTF8=0`, `PYTHONIOENCODING=latin-1`; e com o estado copiado para outro diretório | 1 sequência de bytes distinta em 8 execuções; cópia idêntica | igual |
| mesmo experimento sob outro `request_id` com `as_of` em 2000, 1 s antes do resultado, no instante e depois | DUPLICATE R17 nos quatro (nunca ALLOW) | igual |
| resultado produzido depois do `as_of` | invisível no view, task fica aberta; visível no instante exato | igual |
| resultado do domínio datado em 2999 | ingerido; próxima proposta ABSTAIN OPEN_TASK_PENDING (fail closed; observação, não defeito do CAIN) | igual |
| 30 ciclos com 21 mortes (`exit 86`) sorteadas nos 5 pontos de falha, às vezes duas no mesmo ponto | 30 episódios contíguos; 12 ALLOW = 12 outbox = 12 tasks = 12 resultados = 12 entregas = 12 execuções do domínio = 12 fatos; memória intacta | igual |
| adulteração da projeção `memory_facts` (SUPPORTED → REFUTED) | `verify()` acusa `projection: diverged`; **a política decide sobre a projeção adulterada** (ver 5.4) | igual |
| adulteração da task no outbox / no spool | outbox: `PAYLOAD_INVALID` ao reler; spool: consumidor rejeita, domínio não é chamado | igual |
| modelo falso respondendo hipótese fechada / de outro domínio / sem domínio / injeção na rationale / chaves extras / não-JSON / lista / rationale de 100 000 chars / float | fechada → BLOCK R05; estrangeira e sem domínio → BLOCK R01; injeção fica texto (proposta com as chaves fixas, ALLOW legítimo); chaves extras, lista, float → `LLM_ANSWER_INVALID`; não-JSON → erro fechado; rationale truncada a 2000 | igual |
| lacres do Brasileirão (13 pedidos) | 2023 → ALLOW; season 2025/2026, janela que toca 2025, fixture em 2025 → REQUIRE_HUMAN SEALED_SCOPE; season texto/ausente, events ausente, fixture malformada → BLOCK R02; janela invertida → REQUIRE_HUMAN (malformada, fail closed); janela `[2024-06-01, 2025-01-01)` → ALLOW (semiaberto, correto) | igual |
| três domínios num só diretório de estado | views do stocks e do brasileirao vazios; resultado do cripto no spool do stocks → `DOMAIN_MISMATCH`; proposta do cripto no orquestrador do stocks → BLOCK R01 | igual |
| escala: 300 ciclos (150 tasks) | 29 s para montar; 1 decisão em 0.046 s em processo quente e 0.20 s em processo novo; estado 1.7 MB | igual |
| Windows (`msvcrt.locking`), soak com LLM real, dado real | **não cobertos aqui** (só Linux, domínio substituto, modelo falso) | — |

Fuzz do transporte rc6 (`scripts_transport_task_fuzz.py`, log `RAW_LOGS/adversarial/transport_task_fuzz.log`): 433
mutações de campo único de um arquivo de task, com o consumidor real → 433 rejeições sem chamar o domínio (1 execução
do domínio, a da task válida), 0 traceback; só o **aninhamento absurdo derruba a passada inteira com `RecursionError`**
(reproduzido em `tests/test_transport.py` novo do ecosystem-predictor#38). O mesmo log mede `memory.verify()`: 0.026 s
com 135 eventos (400 ciclos, 135 tasks ALLOW).

**IB-F009 na rc13 (por leitura de `llm.py`):** `templates()` toma emprestada a última task do mesmo tipo e `_request()`
só varia `hypothesis_id`/`request_id`; sem `parameters` o pedido do Brasileirão é o mesmo experimento, e a R17 segura
todas as hipóteses (`NO_ELIGIBLE_HYPOTHESIS`). O waiver continua necessário; a alternativa (sobreposição de campos do
pedido, `proposal_overlays` para chaves fora de `parameters`) é código novo do `cain`.

## 5. Achados (propostos; a atribuição a missões e a reemissão de attestations são decisão do dono)

Nenhum P0 ou P1: em nenhum caso houve resultado errado, duplicado, perdido, vazamento de futuro, ação não autorizada,
contaminação entre domínios ou capital. Todos os itens abaixo são robustez de borda (C6: P2).

| # | Onde | O quê | Correção proposta (PR) | Estado |
|---|---|---|---|---|
| 5.1 | cain `service.ingest` | arquivo de resultado aninhado 100 000 níveis → `RecursionError`; `outcome.status` lista/objeto → `TypeError` do validador congelado. O `ingest` morre com traceback e nada do domínio entra até remover o arquivo | tratar como envelope malformado: rejeição `SCHEMA_INVALID` gravada; `_payload` idem | cain#80 (`2807c23`), 14 testes novos |
| 5.2 | cain `cli._proposal` | proposta aninhada demais → traceback, exit 1 | `SCHEMA_INVALID`, exit 2 | cain#80 |
| 5.3 | cain `service.propose/decision_receipt` e modo LLM | `as_of` com a forma certa mas impossível (`2030-13-45T99:00:00Z`) aceito com memória vazia, gravado e emitido em `created_at` da task | `check_as_of`: instante real, senão `AS_OF_INVALID`; `policy.py` intacto (mesmo `code_sha256` nos recibos) | cain#80 |
| 5.4 | cain `store.view` | a política lê a projeção `memory_facts` sem conferir a cadeia; adulteração da projeção muda decisões e só `verify()` (chamado por `episodes` e pelo soak) acusa | **não corrigido**: `verify()` custa 0.026 s com 135 eventos (`transport_task_fuzz.log`) e cresce linearmente; conferir a cada decisão é escolha de projeto do dono (custo × "corrupção silenciosa" da C10) | registrado |
| 5.5 | transporte `consumer._load` | arquivo de task aninhado demais → `RecursionError` derruba a passada inteira do domínio | rejeição `SCHEMA_INVALID`, passada segue; versão 0.1.0rc7 | ecosystem-predictor#38 (`8ce2a64`) |
| 5.6 | protocolo congelado 2.0.0rc2 (`loads_strict`, `validate_result`) | origem dos 5.1/5.5: `json.loads` sem limite de profundidade e `status not in dict` com valor não hasheável | **não tocado** (release congelada); os chamadores ficaram robustos | registrado |
| 5.7 | cain (observação) | resultado do domínio datado no futuro deixa a task aberta e o domínio em ABSTAIN sem aviso | nenhuma; fail closed, e o relógio do domínio não é do CAIN | registrado |
| 5.8 | brasileirao.json (observação) | `data_cutoff` em 2025 com janela em 2023, e `season` 2027, são ALLOW: os lacres cobrem só temporadas 2025/2026 e janelas em 2025; o cutoff é regra PIT do domínio | nenhuma | registrado |

**Consequência das correções (C14):** se o dono adotar cain#80 e/ou ecosystem-predictor#38 numa release (rc14 / rc7),
as três integrações refazem as fases que exercitam o `cain` e o transporte e reemitem. O `integration-brasileirao` já
tem a C14 da rc13/rc6 pendente no PC 2; pode ser um só ciclo.

## 6. O que continua fora do alcance desta sessão

- Fases de runtime do `integration-brasileirao` (PC 2, dado privado).
- Windows (`WINDOWS_SMOKE` das três integrações), soak com modelo local, E2E com os predictors reais.
- Python 3.14 final (só rc2 disponível aqui) e os dois scripts do ecosystem que consultam a API do GitHub.

## 7. Arquivos

```text
REPORT.md                          este relatório
SHA256SUMS                         sha256 de tudo nesta pasta
scripts_test_adv_cain.py           a suíte adversarial (roda com o venv do cain: uv run pytest <arquivo>)
scripts_transport_task_fuzz.py     fuzz de arquivos de task no consumidor + custo de memory.verify()
RAW_LOGS/ci/                       saídas dos comandos de CI dos cinco repositórios
RAW_LOGS/repro/                    verify_wheel, build reprodutível, comparação das wheels rc12/rc13 e rc5/rc6
RAW_LOGS/adversarial/              pytest -rA e NOTES.json na rc13 (960fb25) e com as correções (2807c23)
```
