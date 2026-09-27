# Preparação do envelope V2: relatório

Missão `envelope-v2` (`prompts/prompt_preparacao_envelope_v2_rev8.md`), núcleo v2.3
(`beaa5feed193356f554922439936ad401c8f177bfd18d8864ca329fae94216fc`), D-22. Executada no PC 2 (Ubuntu 24.04, WSL2) por
um único agente, entre 2026-09-26 e 2026-09-27. Os números abaixo vêm dos logs brutos em
`RAW_LOGS/envelope-v2-20260926/`, extraídos pelo `scripts/build_envelope_v2_freeze.py` para o `ENVELOPE_V2_FREEZE.json`
(C20). Esta missão não emite attestation. Ela entrega o congelamento que a Etapa B consome.

## 1. C0 e pré-condições

`c0_preflight.log` (`origin/main` `1c26028`) e `c0_preflight_4390fdb.log` (`4390fdb`, no momento do congelamento),
ambos na raiz de um worktree destacado do `origin/main`:
- núcleo = v2.3;
- `sha256sum -c MANIFEST.sha256` passa (13/13);
- D-22 `APPROVED`;
- `HYGIENE.json` todo `DONE`;
- as três attestations da Etapa A estão `QUALIFIED`, cada uma com `domain_contract_sha256` igual ao contrato do `main`;
- em `SHARED_ISSUES.json`, nenhum bloqueio para as wheels em uso: SHARED-003/004 são `test_only`; SHARED-005 bloqueia só a
  Ops 4.2.1 `da4fa540…`, e as três missões usam a 4.2.2rc1 `0be70bfb…` (D-17).

## 2. Ponto de partida herdado

A sessão `etapa-b` (2026-09-24) já tinha publicado a `predictor-research-protocol` **2.0.0rc1**
(ecosystem-predictor#28, `fcc005c`, wheel `9ad09b50…`), derivada dos contratos do `predictor-qualification@cb28674`.
Três problemas impediam congelar a rc1:

| Problema | Evidência | Efeito |
|---|---|---|
| anterior à D-22: tem `domain`, mas nenhuma correlação de episódio | o prompt da missão ganhou "correlação que permita encadear episódios por domínio" depois da publicação da rc1 | não atende à especificação que as três orquestrações precisam |
| `STATE_BUSY_RETRYABLE` sem `client_ref` recusado | `stocks-predictor@61fc017`, `research_runner.py` (`sqlite3.OperationalError` na admission → `request_id: null`, sem `client_ref`); a rc1 só aceita `client_ref` nulo em `REJECTED`. Reproduzido com o outcome **real** (`rc1_vs_real_state_busy.log`: `CLIENT_REF_MISMATCH`) | um status declarado no contrato do stocks não tinha representação V2; a matriz de falhas da `integration-stocks` bateria nisso |
| registro dos domínios com o contrato antigo do brasileirao | a rc1 cita `e6f98ca2…` (rc2 do domínio); no `main` é `1c75fc45…` (rc3). O diff muda só `implementation.{final_commit, version, wheel}` | proveniência desatualizada; conteúdo funcional igual |

## 3. O que foi entregue

1. **Especificação** `ecosystem-predictor/packages/research-protocol/SPEC_V2.md` + JSON Schemas de `ResearchTaskV2` e
   `ResearchResultV2`: `predictor-research-protocol` **2.0.0rc2** (ecosystem-predictor#29, merge `49ffb16`). Mudanças
   sobre a rc1:
   - `episode_id` = `<domínio>:episode-<n>` na task, ecoado no resultado. É a forma C18 do `<domínio>/episode-<n>` da
     Etapa B comum §2. O CAIN numera; o envelope confere a forma e o domínio (`EPISODE_INVALID`, `DOMAIN_MISMATCH`);
   - `previous_task_id`: elo para a task do episódio anterior do mesmo domínio, ou `null`. Um episódio sem task
     (BLOCK, ABSTAIN, DUPLICATE, COOLDOWN, REQUIRE_HUMAN) é legítimo, então só a ordem não distingue uma task perdida no
     log de um episódio sem task. Com o elo, a lacuna aparece;
   - `task_id` = f(domain, episode_id, request_id, payload_sha256): uma task por episódio e conteúdo. O mesmo pedido num
     episódio posterior gera task nova, e o domínio responde `DUPLICATE` com o mesmo `result_id` (sem segundo efeito);
   - `client_ref` nulo aceito só em `REJECTED` e `STATE_BUSY_RETRYABLE`;
   - `domains.json` regenerado dos contratos do `main`. HMAC não é requisito e continua fora da V2.
   O domínio nunca vê CAIN, episódio nem transporte: os bytes enviados são `canonical(payload)`, com o mesmo hash
   canônico sem `client_ref` do vetor da Etapa A (C24.3 d). Nada exige mudança num domínio fora dos `adapter_paths`
   (SPEC §9).
2. **Tabela de mapeamento** V2 ↔ contrato por domínio: SPEC §10, gerada de `domains.json` por
   `tools/render_v2_mapping.py`. Um teste falha se ela divergir do registro. Todo campo obrigatório do pedido é o próprio
   payload; o resultado vai em bytes exatos (`payload_canonical`), com o cabeçalho conferido contra ele.
3. **Builds reproduzíveis e release**:
   - a wheel sai com o mesmo sha256 em dois builds (método D-14), no commit do PR e no commit de merge, e a suíte passa
     nos quatro Pythons;
   - a pré-release `predictor-research-protocol-v2.0.0rc2` foi publicada **depois do merge**, só com a wheel e com a tag
     em `49ffb16`, e o download anônimo foi conferido contra o digest da API (`release_publish_rc2.log`,
     `release_download_verify_rc2.log`);
   - hoje nenhum pacote consome a V2 (o `cain` usa a V1 1.0.3rc1; snapshot e bundle não dependem do protocolo), então
     não há consumidor para reconstruir.
4. `ENVELOPE_V2_FREEZE.json`: versão, release, sha256 da wheel, dos três contratos, da SPEC e dos schemas; builds,
   suítes e diagnóstico extraídos dos logs; rc1 marcada como substituída. `--check` refaz tudo e confere.
5. `STACK_BASELINE_V2.0.json` (C3): base de cada repo, com os `final_commits` da Etapa A, e o `origin/main` como
   informação; seção 4.

## 4. Base da Etapa B por repositório

| Repo | Base | Origem | `origin/main` no congelamento |
|---|---|---|---|
| cripto-predictor | `341d270` (1.2.0rc2) | final_commit crypto = `runtime_target.json` (decisão do dono, 2026-09-26) | à frente (PRs #128–#134, pesquisa fora dos `adapter_paths`): **só informação, não é reabertura** (C24.4) |
| stocks-predictor | `61fc017` (0.3.0rc2) | final_commit stocks = `runtime_target.json`; decisão do dono repassada (seção 7) | à frente (protocolo de pesquisa em `stocks_predictor/v2`, `research/`, `policy/`, docs): **só informação, não é reabertura** |
| brasileirao-predictor | `25cdf4d` (0.3.0rc3) | final_commit brasileirao = `runtime_target.json` | `d80a4ed`, merge com a mesma árvore |
| core-predictor | `5a08415` (3.2.1) | final_commits (iguais nas três) | igual |
| predictor-ops | `9831b0d` (4.2.2rc1) | final_commits (iguais nas três) | `31d3939` = squash do PR #26, mesma árvore |
| ecosystem-predictor | `49ffb16` | merge do #29 (SPEC V2 rc2) | igual |
| cain | `f343701` | `origin/main` no congelamento; muda livremente na Etapa B (C3) | igual |

As seis `final_wheels` (Core 3.2.1, Ops 4.2.2rc1, os três domínios e o protocolo rc2) conferem com o digest dos assets
(`final_wheel_verification`).

## 5. Diagnóstico com outcomes reais (não é gate)

Montagem: um venv py3.13 por domínio, com a wheel final da Etapa A (sha256 da attestation), as deps do `uv.lock` do
final_commit (`uv export --locked`, `--require-hashes`) e a wheel rc2, sobre as fixtures sintéticas congeladas da suíte
de conformidade (`scripts/envelope_v2/`).

Conferido em cada domínio:
- registro = constantes do contrato instalado;
- hash do pedido = vetor da Etapa A;
- payload V2 = `Circuit.show()` (fonte autoritativa);
- reenvio → `DUPLICATE`;
- mesmo pedido em episódio posterior → task nova, `DUPLICATE`, mesmo `result_id`;
- conteúdo diferente → `CONFLICT`;
- canário;
- resultado de outro domínio rejeitado.

No stocks, com `admission.sqlite` travado por outra conexão, o `STATE_BUSY_RETRYABLE` real é representado como
`RETRYABLE`, e o reenvio depois do lock dá `RESULT`. É a primeira vez que o Brasileirão rc3 passa pela V2: o
diagnóstico da rc1 cobriu só crypto e stocks.

## 6. Achados e observações (sem mudança nesta missão)

- **CI do `ecosystem-predictor` vermelho por relógio desde 2026-09-27T02:02Z.** No `49ffb16`, o CI do push do merge
  passou (run 36270444486). Os runs posteriores no mesmo commit falharam só no job `quality`: o agendado 36317521235 e o
  do push da tag 36350241339. A causa é `tests/test_ecosystem_drift.py::test_real_registry_has_current_hash_verified_target_harness`:
  - dois atestados de harness do cripto (`registries/harness_registry.json`,
    `docs/engineering_controls/20260920/crypto-trials.*harness_attestation.json`) venceram em
    `2026-09-27T02:02:47Z`/`02:02:16Z` e continuam `ALIGNED`, e a regra "atestado vencido não pode continuar ALIGNED"
    falha;
  - todos os jobs `research-packages`, inclusive `research-protocol` em 3.11–3.14, passaram nesses runs.
  Não é da rc2. Mas a Etapa B muda o ecosystem, e o `HOSTED_CI` dela exige CI verde nos commits finais, então isso vai
  bloquear a `integration-crypto` se não for resolvido (seção 7).
- **Contrato do crypto:** o bloco `implementation` cita `2bc63eb`/1.2.0rc1, mas o final_commit e o `runtime_target.json`
  são `341d270`/1.2.0rc2. O `request_schema` e o `result_schema` não dependem disso. Mudar o contrato é C14
  ("Contrato de domínio"), então fica registrado.
- **Build backend** do protocolo: `setuptools>=75`, resolvido na hora do build (84.0.0 aqui). O artefato congelado é a
  wheel publicada (digest). Um rebuild futuro com outro setuptools pode dar outro sha256 sem mudar o conteúdo.
- **Sessão paralela:** uma segunda sessão abriu a mesma missão em 2026-09-26 às ~05:15 UTC e parou pela D-5, sem commit,
  PR nem release. Ela deixou um worktree local abandonado, `work/envelope-v2-rc2-ecosystem-predictor` (branch local,
  nunca publicada).

## 7. Pendências para o dono

1. **Merge deste PR.** Com `ENVELOPE_V2_FREEZE.json` e `STACK_BASELINE_V2.0.json` no `main`, a `integration-crypto` pode
   começar (D-22).
2. **Atestados de harness vencidos no ecosystem** (seção 6). Escolha uma:
   - renovar o atestado do harness do cripto, o que reexecuta o harness e atualiza o registro do ecosystem. Isso pode
     tocar artefato protegido do cripto; a decisão é sua;
   - reclassificar as duas entradas vencidas no registro (sair de `ALIGNED`). Aí a regra "nenhum harness ALIGNED" do
     mesmo verificador precisa ser avaliada.
   Até lá, o `quality` do ecosystem fica vermelho em qualquer commit novo.
3. **Stocks à frente do final_commit: respondida por repasse.** A sessão `arrumando cain - predictors` (`e1a8cb`)
   repassou em 2026-09-27 às ~21:05 UTC a resposta do dono escrita naquele chat: "base do stocks = 61fc017, igual ao
   cripto". Ela não foi dita no chat desta sessão. O `STACK_BASELINE_V2.0` já usa `61fc017` como base, com o `main`
   posterior só como informação e sem reabertura (C24.4), o que também é o que o `prompt_etapa_b_stocks_rev9.md` manda.
4. Opcional: remover o worktree/branch local abandonado da sessão paralela (o agente não apaga branch).
