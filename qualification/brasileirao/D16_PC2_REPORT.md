# D16_PC2_REPORT — missão brasileirao, noite de 2026-09-24 (D-16 no PC 2 + conferência geral)

Sessão autônoma no PC 2 (Ubuntu 24.04.5 LTS no WSL2, x86_64). Autorização: D-16 (`APPROVED` no `main`,
PR #16). Alvo congelado: brasileirao-predictor `04b42c9` / wheel 0.3.0rc2 `70344f22…`, predictor-core
3.2.1 `10ef42f3…`, predictor-ops 4.2.2rc1 `0be70bfb…`. Toda a saída bruta está em
`RAW_LOGS/d16-pc2-20260924/` (`stage-a/`, `suite/`, `d16/`, `scan_final/`); nenhum número aqui foi digitado
à mão (C20). Nada foi treinado; nenhum capital foi movido; nada do dado real entrou na evidência.

## Resumo

| Item | Resultado |
|---|---|
| A Etapa A se sustenta? | **Sim.** 130 citações de evidência existem e batem com o último parcial; hashes congelados, contrato, vetores, lock e wheels conferem; protegidos 1877/1877; `attest.py check` OK no último parcial |
| Suíte completa (PC 2, checkout `04b42c9`) | 2305 passed, 2 skipped, 30 deselected (`integration`); ruff e `uv build` ok; pyright 0 erros (com `libatomic1` extraída no runtime) |
| CI do `main` (`e540f97` = árvore do `04b42c9`) | CI Pipeline e publication-validation `success`, nenhum job pulado |
| Conformidade no runtime do PC 2 | 89/89; todos os gates mapeados verdes (`d16/gate_tests_pc2.json`) |
| **E2E** (parte Linux, dado real) | 20/20 pedidos reais exit 0; E2E real **25/25**. **Bruto teria sido `PASS`**; o gate fica `NOT_RUN` (D-9/schema) |
| **SOAK** (perfil BR_V1, dado real) | 71 chamadas, 49 resultados, 0 perdidos/duplicados/violações, reconcile limpo, tolerância zero ok. **Bruto teria sido `PASS`**; o gate fica `NOT_RUN` (D-9/schema) |
| Dado | sha256 `31f30a4d…` na fonte e na cópia, antes e depois; 0 registros do dado na evidência (82 arquivos varridos) |
| Achado novo | **BR-F018 (P1, aberto)**: os números de um resultado dependem do SO (os estados, não). `BLOCKERS_ZERO` passa a `FAIL` |

## 1. A Etapa A se sustenta? (`stage-a/`)

* `scripts/stage_a_recheck.py` → `stage-a/stage_a_recheck.json`: `verdict OK`. GATES.json com 30 `PASS` e 2
  `NOT_RUN`; 130 arquivos de evidência dos gates, 0 ausentes, 0 com sha256 diferente do
  `ATTESTATION_PARTIAL_attestation.json`; evidências de `environments` e veredictos SHARED-003/004 batem;
  núcleo, `STACK_BASELINE_V1.1`, `FROZEN_PARAMETERS`, `PROTECTED_SET`, `FROZEN_VECTORS`, perfil do soak e
  contrato (= `domain_contract_sha256`) batem; counts = FINDINGS; 7/7 vetores congelados = blobs do
  `04b42c9`; `runtime_target.json`, `uv.lock` e `constraints/shared-wheels.sha256` apontam as mesmas wheels.
* Commits: `04b42c9` (árvore = `main` `e540f97`), core `5a08415`, ops `9831b0d` (árvore = `main` `31d3939`).
  A tag `v3.2.1` do Core aponta `7bb212c`; o diff até `5a08415` só toca `.github/`, `tools/` e `*.md`
  (já registrado no `STACK_BASELINE_V1.1`).
* Wheels baixadas das releases (`stage-a/wheels_download.log`): sha256 = `final_wheels` e = `digest` do
  asset no GitHub, para as três.
* `protected_check.py` no `04b42c9`: 1877/1877 iguais.
* `attest.py check` (`stage-a/attest_check.log`): OK em `attestation` e `contract-sign-off`. Os parciais de
  fases anteriores falham só por `counts`/sha256 de `FINDINGS.json`, `HOSTED_CI_REPORT.md` e da varredura
  de segredos, que mudaram depois (já descrito no `QUALIFICATION_CHANGELOG.md`). Observação: os parciais de
  `contract-admission` a `soak` têm `generated_at` entre 07:01:04Z e 07:01:15Z (gerados em lote).

## 2. Conferência geral (`suite/`, `stage-a/ci_main.log`)

`scripts/pc2_suite.sh`: método do job `python` do `ci.yml` (como o `win_suite.sh`), venv
`~/predictors/runtime/brasileirao/venv-suite` por `uv sync --locked --all-extras`, Python 3.13.15.
Resultado em `suite/pc2_suite_04b42c9.log`/`.junit.xml`. Não rodou: `pytest -m integration` (exige o Redis
de serviço do CI) e a perna 3.14 da matriz (só o 3.13 está instalado no PC 2). O pyright falhou primeiro
por ambiente (`libatomic.so.1` ausente para o Node que ele baixa) e passou com a `libatomic1` do arquivo
oficial do Ubuntu extraída em `runtime/brasileirao/sysroot` (`suite/pyright_libatomic.log`).

## 3. D-16 no PC 2 (`d16/`)

Driver `scripts/pc2_d16_runtime.sh` (análogo Linux do `windows_runtime.sh` + `runtime_cleanroom.sh`):

1. **Dado:** `~/predictors/data/d16/brasileirao/matches_source_copy.sqlite3` (só leitura) copiado byte a
   byte para `~/predictors/runtime/brasileirao/data/`; sha256 conferido na fonte e na cópia, antes e depois
   (`d16/dataset_sha256.log`). O snapshot capturado pelo `put-dataset` tem o mesmo sha256 (como no Windows).
2. **Runtime suportado (C3.1):** venv limpo só com as dependências de runtime do `uv.lock` do `04b42c9`
   (`--require-hashes`; Core e Ops pela URL da release) e a wheel publicada (sha256 conferido);
   identidade e trace em `d16/core_identity.json`, `d16/runtime_trace.log`. A conformidade roda num venv de
   teste separado (mesmas pinagens + extras): 89/89.
3. **Dado real pelo entrypoint:** `real_env.py` (20 pedidos: 2021–2024 e 2026 × 1X2/OU25 × climatologia/
   mercado; 2025 nunca é alvo): 20/20 exit 0.
4. **E2E real** (`e2e_runtime.py --real`, pedido idêntico ao do windows-smoke): 25/25 checagens — processo 1
   termina, processo novo relê o mesmo resultado (store autoritativo, bytes iguais), duplicata devolve o
   mesmo resultado; recibo da admission, journal, efeito, trial do Core, job do Ops (jobs file v3, módulo da
   wheel, `strict`, `FORECAST_GENERATION`, sem capital), heartbeat, lock econômico, IDs com domínio,
   replay temporal com `max_used_minus_cutoff < 0` e sem cache lido.
5. **SOAK real** (`soak.py --real-dataset`): perfil inteiro; números em `SOAK_REPORT.md`.
6. **Separação evidência × privado** (`pc2_export.py`): os resultados `show` (previsões por jogo) e o
   `commands.log` do `real_env.py` ficam só no PC 2 (`~/predictors/runtime/brasileirao/d16-pc2-20260924/
   private`); na evidência entram o sha256 de cada um (`d16/private_manifest.sha256`), as linhas de outcome
   (ids e estados) e os resumos numéricos (`d16/evidence_numbers_pc2.json`).
7. **Varreduras:** `scan_final/no_data_rows_check.json` (marcadores tirados da cópia em modo
   `ro&immutable`: 30 times, 1275 jogadores, 2322 event_id; 0 ocorrências em 82 arquivos) e
   `scan_final/secrets_scan.json` (0 achados em 80 arquivos).

**Veredito bruto pelos critérios congelados:** `E2E` → `PASS`; `SOAK` → `PASS`. Os dois continuam
`NOT_RUN` com a nota "evidência bruta com dado real pronta no PC 2; aguarda emenda da D-9 e do schema
(C14)", porque o PC 2 não é, hoje, um Linux primário admitido pela D-9 nem pelo enum `where` do schema.

Erros de método desta noite (preservados, não contam): `d16/export_METHOD_ERROR_idempotency_path.*` (o
exportador procurou o registro de idempotência do Ops na pasta do job; ele fica em `x/o/idempotency/`),
`d16/fit_sensitivity_METHOD_ERROR_*` (diagnóstico sem o filtro `available_at < refit_at`; contraprova que
abortava na primeira falha do otimizador), `d16/fit_sensitivity_script_v1.log` (saída da versão anterior do
script, refeita com a versão versionada).

## 4. BR-F018 (P1, aberto) — o número depende do SO

`d16/compare_real_windows_pc2.json` (`scripts/compare_real_metrics.py`): Windows local (windows-smoke rc2)
× PC 2 Linux, mesma wheel, mesmo lock (numpy 2.5.3, scipy 1.18.1, pandas 3.0.6), mesmo snapshot
(`sqlite_sha256` e contagens iguais), mesmos 20 pedidos:

* estados de resultado/científico/econômico iguais em 20/20; métricas iguais em só 4/20; conteúdo
  comparável igual em 0/20;
* 7120 previsões comparadas: `information_fingerprint` igual em 7120 (o conjunto de informação é o mesmo);
  diferem `params` do refit (máx. 1,42e-2), `lambda_home`/`lambda_away` e as probabilidades em 6600
  (`p_home` até 6,2e-3, `p_over25` até 3,8e-3);
* economia: até 5 apostas a mais ou a menos por pedido; ROI líquido 2021 O/U +1,16% (Windows) × −0,05%
  (Linux); em 2022 o IC95 do ROI líquido cruza zero no Windows e fica inteiro abaixo de zero no Linux (1X2 e
  O/U) — `REAL_DATA_METRICS.md`, tabela do Linux.

Causa raiz (`d16/fit_sensitivity*.json`, `scripts/fit_sensitivity.py`, diagnóstico com a wheel instalada):
o mesmo ajuste repetido no mesmo processo é bit-idêntico em 62/62 refits mensais, mas multiplicar os pesos
por (1 + 2⁻⁵²) muda os parâmetros em 62/62 (mediana 2,7e-3, máximo 1,6e-2). O L-BFGS-B de
`brasileirao_predictor.model.fit_goal_model` (gradiente por diferenças finitas, tolerâncias padrão,
penalidade 1e12 fora da região válida) amplifica as diferenças de último bit que os binários de cada SO
produzem. Só apertar a tolerância (ftol 1e-15, gtol 1e-10) baixa a mediana para 4,1e-4, mas o máximo fica
em 1,4e-2 e 1 refit passa a falhar: não é conserto de uma linha.

Não há vazamento, violação temporal, resultado duplicado ou perdido; em cada SO o resultado é
determinístico (metamórfico, soak e E2E passam). Classificado **P1** pela C6 (afeta o resultado — os
números de um resultado não ficam determinados por pedido + dado + wheel + commit —, sem violação
observada); por isso `BLOCKERS_ZERO` passa a `FAIL`. O dono pode reclassificar (com o motivo).

## 5. Emenda proposta (o dono edita; o agente não tocou no núcleo, no schema nem no `CLAUDE.md`)

**Schema** (`qualification/ATTESTATION_SCHEMA.json`), `environments.items.properties.where.enum`:

```json
["github_actions", "cloud_vm", "local_windows", "owner_linux"]
```

com, de preferência, a regra `if where == "owner_linux" then os == "linux"`. Consequência em cadeia: o
sha256 do schema está fixado no núcleo (C0.2), então o núcleo precisa de versão nova com o sha256 novo; o
sha256 do núcleo está fixado nos prompts (C0.1) e no `MANIFEST.sha256`; pela C14 ("Núcleo (versão)"), as
attestations são revalidadas no schema novo.

**D-9, nova redação** (`qualification/DECISIONS.json`):

> A máquina local (PC 1) não comporta Linux. Linux principal = **GitHub Actions** `ubuntu-latest` × py3.13
> para testes, reproduções da SHARED-003, E2E; **VM Linux na nuvem sob demanda** (ou GitHub Codespaces) para
> o soak e para o que exigir processo de longa duração, destruída ao fim. **Para dado privado sem direito de
> redistribuição (D-11), o Linux principal é o PC 2 do dono (Ubuntu 24.04 LTS no WSL2, x86_64), com Python
> 3.13 gerenciado por uv em `~/predictors/tools`, runtime em `~/predictors/runtime/<missão>` e o dado só em
> `~/predictors` (cópia hash-verificada, só leitura); vale como ambiente `primary` com `where = "owner_linux"`.
> O dado nunca sai do PC 2: a evidência leva só logs sem registros do dado, sha256 e resumos numéricos. Hoje a
> exceção cobre o `matches_source_copy.sqlite3` do Brasileirão (D-16).** Usa só **cópias** hash-verificadas
> dos dados necessários (sem dado sem direito de redistribuição em repo público); evidência no repositório de
> evidência. Nada é instalado no Python do Windows para o Stocks. Aprovar esta decisão emenda, **só para a
> qualificação**, a regra "todo trabalho em `C:\Cripto`" do Cripto no que roda fora desta máquina.

**Textos que acompanham a emenda** (mesmo motivo): núcleo C11 — "**Primário:** Linux × Python 3.13
(GitHub Actions, VM na nuvem ou, para dado privado, o PC 2 do dono — D-9)"; `CLAUDE.md`, regra fixa — "Linux
= GitHub Actions, VM na nuvem ou, para dado privado, o PC 2 do dono (D-9)".

Com a emenda no `main`, `E2E` e `SOAK` podem ser fechados com esta evidência (ambiente `linux/primary/
owner_linux` com `d16/env.log`, `d16/conformance.junit.xml` e `d16/soak.jsonl`), revalidando a attestation no
schema novo (C14).

## 6. Decisões do dono

1. **Merge deste PR** (evidência bruta, scripts do PC 2, BR-F018 registrado, `BLOCKERS_ZERO = FAIL`).
2. **Emenda D-9 + schema + núcleo** (texto da seção 5), ou manter `E2E`/`SOAK` em `NOT_RUN`.
3. **BR-F018:** (a) aceitar como limitação documentada — reclassificar para P2/`ACCEPTED_LIMITATION` com o
   motivo, `BLOCKERS_ZERO` volta a `PASS`, e declarar que os números valem por ambiente; ou (b) corrigir o
   ajuste no brasileirao-predictor (gradiente analítico ou reparametrização, convergência estável) → rc nova
   e C14 (publish-candidates, cleanroom-final, temporal-suite, e2e, idempotency-failure, windows-smoke,
   hosted-ci, soak).
4. Pela C7.3, com um P1 aberto o estado terminal da missão seria `NOT_QUALIFIED`. Não emiti attestation
   final: o último parcial (`ATTESTATION_PARTIAL_d16-pc2.json`, `IN_PROGRESS`) registra o estado até a
   decisão 3.
