# integration-crypto — QUALIFICATION_CHANGELOG

O que o agente mudou, onde, por quê, commit e PR (C6). Sessão única (D-5), executada no **PC 2** do dono (Claude
Code desktop, comandos Linux no WSL Ubuntu 24.04 só para desenvolvimento e diagnóstico). Toda afirmação de gate cita
arquivo de evidência + sha256 no `GATES.json` / attestation.

## 2026-09-27 — C0, D-23, freeze-parameters, baseline

| Onde | O quê | Por quê | Commit / PR |
|---|---|---|---|
| `predictor-qualification` `qualification/DECISIONS.json` | acrescenta a D-23 (só ela) | decisão explícita do dono no prompt da sessão (base 341d270/1.2.0rc2; estado do CAIN só de 341d270; WINDOWS_SMOKE no PC 2) | `d81b8d9`, PR #56 (separado, pode entrar sozinho) |
| `qualification/integration-crypto/RAW_LOGS/c0/` + `scripts/c0_preflight.sh`, `c0_preconditions.py` | pré-voo 4.1–4.7 do prompt da sessão: 21/21 OK | C0 do núcleo + pré-voo da sessão, antes de qualquer mudança | este PR |
| `RAW_LOGS/diag-import-closure/` | sonda de diagnóstico: o console script de adapter que o contrato permite quebra o teste congelado de fecho de imports | evidência do desenho (SPEC V2 §9); achado IC-F002 | este PR |
| `fixtures/v2/` + `scripts/build_v2_fixtures.py` | fixtures V2 congeladas dos três domínios, montadas dos vetores e resultados reais da Etapa A (pedido conferido pelo `request_content_hash`) + par `H9` de cada domínio | C9, C18, prompt do cripto §4 (stocks e brasileirao ainda não integrados) | este PR |
| `FROZEN_PARAMETERS.json` + `scripts/freeze_parameters.py`, `FAILURE_MATRIX.json`, `QUALIFICATION_PROFILE_INTEGRATION_CRYPTO_V1.json` | parâmetros, matriz de falhas e perfil de soak congelados; configuração congelada da DecisionPolicy do cripto (fonte: 341d270 com SHA completo + contrato) | C15 (primeira fase); mostrados ao dono neste PR antes de qualquer execução de gate | este PR |
| `STACK_BASELINE.json` + `scripts/mission_baseline.py`, `RAW_LOGS/baseline/` | baseline da missão com o coletor do STACK_BASELINE_V2.0, sem mudança: igual ao V2.0 em todos os repos e wheels | C3 (antes de qualquer mudança) | este PR |
| `FINDINGS.json`, `GATES.json`, `scripts/attest.py`, `scripts/findings_init.py`, `ATTESTATION_PARTIAL_{freeze-parameters,baseline}.json` | achados IC-F001..IC-F007; ledger de gates; parciais validados no schema | C6, C7, C8 | este PR |
| `tools/pyproject.toml`, `tools/uv.lock` | ambiente das ferramentas da missão: protocolo 2.0.0rc2 da release congelada (sha256 no lock) + jsonschema | venvs só de uv.lock | este PR |

## 2026-09-27 — implementação, publish-candidates, runtime (Linux primário e Windows do PC 2)

| Onde | O quê | Por quê | Commit / PR |
|---|---|---|---|
| `ecosystem-predictor` `packages/research-transport` (novo), `registries/architecture_registry.json`, `tests/test_architecture_inventory.py` (11→12 pacotes), `.github/workflows/ci.yml` (matriz) | transporte V2: spool write-once + `predictor-research-consumer` + allowlist fixa de adapters; 0.1.0rc2 corrige o stdout do consumidor | SPEC V2 §9 e §12; C24.3 (d) | `0cb672b`, `a19655f`; ecosystem-predictor#30; pré-releases `predictor-research-transport-v0.1.0rc1` e `-v0.1.0rc2` |
| `cripto-predictor` `GarimpoInvestimentos/adapters/research_v2.py` (novo) + versão `1.2.0rc3` (pyproject, `__version__`, linha do uv.lock) | adapter V2 só stdlib + adapter_api | prompt do cripto §3.4; 7.1 do prompt da sessão; testes congelados da Etapa A | `ee3d3d1`; cripto-predictor#135; pré-release `v1.2.0rc3` (final_commit = commit da tag) |
| `cain` `src/cain/orchestration/*`, `tools/build_domain_config.py`, `src/cain/loop/{__main__,similarity}.py`, `cli.py`, `research/cli.py`, `findings/cli.py`, `.gitignore`, testes | framework de orquestração por domínio, DecisionPolicy + receipt, configuração do cripto de 341d270, cerco do loop do PR #50, SHA completo no PR #51, propostas por LLM auditadas | prompt comum §2–§8, prompt do cripto §3 | `1af5426`, `a41fbb7`, `8f50791`, `6b460af`; cain#57; pré-release `v0.4.13rc5` |
| `predictor-qualification` `qualification/integration-crypto/` | vetores congelados, harness, workflow `integration-crypto-runtime.yml`, evidências, relatórios; `.gitattributes`: `RAW_LOGS/**` e `E2E_EVIDENCE/**` da missão como `-text` (logs do Windows com CRLF preservados byte a byte, como nas missões da Etapa A) | C8, C16, C20 | #57 (mergeado até `f0cb40f`), #61 |

**WINDOWS_SMOKE no PC 2** (Windows local secundário do dono, `DESKTOP-EJPA2MT`):

- Pasta `C:\Cripto\qualificacao\runtime\integration-crypto\`, criada e escrita só por PowerShell (D-23).
- `uv` 0.12.18 extraído do zip conferido contra o `.sha256`, e Python 3.13.15 gerenciado, copiado de `C:\QUALIFICACAO\runtime\brasileirao2\tools\`.
- venvs só dos `uv.lock` e das wheels publicadas.
- 48 arquivos públicos de `~/predictors/data/d16/cripto/` com sha256 conferido antes e depois da cópia.
- E2E com restart: evidência em `RAW_LOGS/windows-smoke/`, sha256 conferido na cópia.
- A pasta não foi apagada.
- A tentativa 1 falhou por defeito do próprio script (`Write-Output` dentro de função); o log foi preservado.

## 2026-09-27 — soak, fechamento e attestation (sessão no PC 2)

| Onde | O quê | Por quê | Commit / PR |
|---|---|---|---|
| `RAW_LOGS/runtime/run36357313578/` | soak 1: todos os pisos menos o de propostas de LLM (0). O `num_ctx = 4096` do harness limitava a entrada do cliente LLM | C10; mantido como evidência | `2319ed0`, #61 |
| `scripts/soak.py` | o `cain-llm.toml` do soak passa a `num_ctx = 8192` e `max_input_bytes = 16000`. Correção: a mensagem do `2319ed0` atribui o limite 3584 ao padrão do cain; ele vinha de `min(6500, 4096 - 256 - 256)` | configuração do modelo local, não parâmetro congelado; perfil, pisos e vetores iguais | `2319ed0`, #61 |
| `RAW_LOGS/runtime/run36357575208/` | soak 2, run de push no commit `2319ed0`: tolerância zero e todos os pisos do perfil V1 (tabela no `SOAK_REPORT.md`) | gate `SOAK` | #61 |
| `scripts/final_wheels_check.py`, `RAW_LOGS/final-wheels/` | as 8 `final_wheels` conferidas contra o asset da url e contra o instalado nos dois runs do Linux primário | C7.1 regra 4 | #61 |
| `scripts/render_reports.py`, `scripts/update_gates.py`, relatórios `*_REPORT.md`, `EVIDENCE_NUMBERS.json` | relatórios gerados de `RAW_LOGS/`; o `SOAK_REPORT` lista o soak anterior; ledger dos gates fechado | C20, C7 | #61 |
| `RAW_LOGS/protected/`, `RAW_LOGS/secrets/` | conjunto protegido igual; varredura de segredos refeita sobre todos os arquivos da missão, sem achados | C15.1, `SECRETS_CLEAN` | #61 |
| `FINDINGS.json` | IC-F010 (P2, `ACCEPTED_LIMITATION`): parciais C8 não gravados fase a fase depois do cleanroom-baseline | C6 | #61 |
| `ATTESTATION_PARTIAL_soak.json`, `QUALIFICATION_ATTESTATION.json` | attestation final **NOT_QUALIFIED**: `HOSTED_CI` FAIL e `BLOCKERS_ZERO` FAIL, os dois só pelo P1 IC-F004 (CI do ecosystem-predictor vermelho por atestados de harness do cripto vencidos, anterior à missão, decisão do dono pendente); os outros 28 gates PASS; WINDOWS_SMOKE no PC 2 cita a D-23 (no main) | C7.3 (gate FAIL ou P1 aberto ⇒ NOT_QUALIFIED) | #61 |

## 2026-09-27 — IC-F004 fechado (decisão do dono) e reemissão C14 (sessão no PC 2)

Decisão do dono no chat da sessão: "tenta renovar se nao coloca como expired". A renovação genuína funcionou, então as entradas não ficaram só como `EXPIRED`.

| Onde | O quê | Por quê | Commit / PR |
|---|---|---|---|
| `RAW_LOGS/harness-renewal/` | harness oficial `pipeline-power/2` do cripto rodado de novo sobre a árvore limpa `ee3d3d1`, Core 3.2.1, seeds fixos; quatro braços OK; atestados gravados fora do repo do cripto, porque os arquivos canônicos estão no `PROTECTED_SET` e fora da 7.1 | IC-F004 | #62 |
| `ecosystem-predictor` `registries/harness_registry.json`, `docs/engineering_controls/20260927/`, `.gitattributes` | entradas ALIGNED vencidas → `EXPIRED` + `reissue_required`; 2 entradas ALIGNED novas, até 2026-10-04, com `evidence_sha256` (`scripts/renew_harness_registry.py`) | check_offline exige um harness ALIGNED para o Core 3.2.1; só EXPIRED não fecharia | `61d3430`; ecosystem-predictor#31 |
| `ecosystem-predictor` `packages/research-transport` | 0.1.0rc3, só versão, publicado de `61f3ac4` com CI de push verde | C21: final_commit = commit da tag, CI verde | `61f3ac4`; ecosystem-predictor#31; pré-release `predictor-research-transport-v0.1.0rc3` |
| `cain` `pyproject.toml`, `uv.lock`, `__version__`, README | transport 0.1.0rc3 e versão 0.4.13rc6, sem código | uma só versão do transporte no stack | `10744a9`; cain#58; pré-release `v0.4.13rc6` |
| `runtime_targets.json`, `hosted_ci_final_targets.json`, `scripts/{render_reports,secrets_scan,update_gates}.py` | alvos novos; relatórios leem versões e diretórios da reemissão (sufixo `-c14`); os raw logs citados pela attestation anterior não mudam | C14, C20 | #62 |
| `RAW_LOGS/runtime/run36360075557/`, `run36360088636/`, `windows-smoke-c14/`, `hosted-ci/final-c14/`, `core-identity-c14/`, `contract-revalidation-c14/`, `protected-c14/`, `final-wheels-c14/`, `secrets-c14/` | fases refeitas com as wheels finais: cleanroom-final, C24.3, e2e, N+1, isolamento, F01–F15, soak, Windows (PC 2, mesma pasta autorizada; `logs`/`out` da rodada rc5 renomeados para `logs-rc5`/`out-rc5`, nada apagado), HOSTED_CI, core identity, conjunto protegido, final wheels, segredos | C14 (`cain`/`ecosystem-predictor` mudaram) | #62 |
| `FINDINGS.json` | IC-F004 `FIXED` | decisão do dono executada | #62 |
| `QUALIFICATION_ATTESTATION_superseded_3dce62a9d3d6.json`, `ATTESTATION_PARTIAL_c14-attestation.json`, `QUALIFICATION_ATTESTATION.json` | a attestation anterior (NOT_QUALIFIED) é preservada; a nova é **QUALIFIED**, com `supersedes_sha256` apontando para ela | C7.1 regra 8, C7.3 | #62 |

## 2026-09-28 — reemissão C14 pela integration-stocks (sessão no PC 2)

A integration-stocks mudou `cain` (configuração do domínio stocks) e `ecosystem-predictor` (entrada `stocks` na allowlist do transporte). Pela C14, as fases da integration-crypto foram refeitas com as wheels finais novas e a attestation foi reemitida. Nada do cripto mudou: o final_commit continua `ee3d3d1`, e o perfil, os vetores e o conjunto protegido são os mesmos.

| Onde | O quê | Por quê | Commit / PR |
|---|---|---|---|
| `cain` `src/cain/orchestration/data/stocks.json`, `tools/build_domain_config.py`, testes | configuração do stocks; `crypto.json` regerado byte a byte igual | integration-stocks | `581b760`; pré-release `v0.4.13rc7` (`deccaaa`, com o transporte 0.1.0rc4) |
| `ecosystem-predictor` `packages/research-transport` | entrada `stocks` na allowlist `ADAPTERS`, 0.1.0rc4 | integration-stocks | `1304b20`; pré-release `predictor-research-transport-v0.1.0rc4` |
| `runtime_targets.json`, `hosted_ci_final_targets_c14s.json`, `scripts/isolation.py` | alvos novos. No isolamento, o domínio não configurado do teste CONFIG_INVALID passa de `stocks` (agora configurado) para `brasileirao`, com a mesma conferência | C14 | integration-stocks |
| `scripts/{update_gates,render_reports,secrets_scan}.py` | ledger e relatórios leem os diretórios `-c14s`. Correção: com sufixo, o `render_reports.py` citava `core-identity/` e `windows-smoke/` sem o sufixo, embora os números viessem do diretório da reemissão (defeito desde a `-c14`; os números eram iguais). Agora cita o arquivo lido | C14, C20 | integration-stocks |
| `RAW_LOGS/runtime/run36365192302/` | run de push único, com todas as fases do runtime: cleanroom-final, C24.3 (d), e2e, N+1, isolamento, F01–F15 e soak | C14 | integration-stocks |
| `RAW_LOGS/windows-smoke-c14s/` | E2E + restart no PC 2, na mesma pasta autorizada (D-23), com o novo `stage-c14s`. `logs`/`out` da rodada anterior renomeados para `logs-rc6-final`/`out-rc6-final`; nada apagado | C14, WINDOWS_SMOKE | integration-stocks |
| `RAW_LOGS/{core-identity,contract-revalidation,protected,final-wheels,secrets}-c14s/`, `RAW_LOGS/hosted-ci/final-c14s/` | conferências refeitas com os final_commits `deccaaa`/`1304b20`, todas verdes; CI de push verde nos dois | C14 | integration-stocks |
| `QUALIFICATION_ATTESTATION_superseded_112d18a35c7b.json`, `ATTESTATION_PARTIAL_c14s-attestation.json`, `QUALIFICATION_ATTESTATION.json` | a attestation anterior (QUALIFIED, cain rc6 / transporte rc3) é preservada. A nova é **QUALIFIED**, com `supersedes_sha256` apontando para ela | C7.1 regra 8, C14 | integration-stocks |

## 2026-09-28 — ciclo 2 (C14): cain 0.4.13rc10, release única da Etapa B (sessão cripto, PC 2)

Por decisão do dono, as três integrações convergem numa só release do cain, e cada uma é requalificada nela. A política de decisão passa à v2, que é parâmetro congelado desta missão. Pela C14 isso significa a fase inteira, como novo ciclo. O dono viu o diff do ciclo 2 antes de congelar (C15) e aprovou a reemissão encadeada.

O cripto não mudou: o final_commit continua `ee3d3d1` (1.2.0rc3), e o perfil, os vetores, a matriz de falhas e o restante do conjunto protegido são os mesmos.

| Onde | O quê | Por quê | Commit / PR |
|---|---|---|---|
| `cain` | política v2 (R15, #59), custos por variante do contrato (#62), configuração do Brasileirão (#64/#66), R16 escopo lacrado (#65), tipo de pedido por hipótese (#67), R17 pedido equivalente (#68), justificativa do LLM conferida (#69); `crypto.json` com as chaves novas `proposable_request_types` e `sealed_scopes` | release única | `fb0e1dc` (#70); pré-release `v0.4.13rc10`, wheel `752de98d…`, publicada por `scripts/publish_rc.sh` (build reprodutível 2×, download anônimo conferido; `RAW_LOGS/publish-candidates/publish_cain_0.4.13rc10.log`) |
| `ecosystem-predictor` `packages/research-transport` | entrada `brasileirao` na allowlist, 0.1.0rc5 | integration-brasileirao | `b11494a`; pré-release `predictor-research-transport-v0.1.0rc5` |
| `FROZEN_PARAMETERS.json`, `FROZEN_PARAMETERS_cycle1_c428e4b769e3.json`, `scripts/freeze_cycle2.py` | ciclo 2: `decision_policy.version` 2, `rule_order` com R04 por hipótese, R16, R06 do #62, R15 e R17; `crypto_config` com as chaves novas do `crypto.json` de `fb0e1dc`; bloco `cycle` com o sha256 do ciclo 1 e a autorização. O ciclo 1 fica byte a byte (mesmo blob git) no arquivo de supersedes | C14, C15 | dono (diff mostrado antes de congelar) |
| `FINDINGS.json` (`IC-F011`, `scripts/add_finding_ic_f011.py`), `scripts/protected_check.py`, `scripts/update_gates.py`, `scripts/render_reports.py` | o FROZEN_PARAMETERS.json é item protegido: conta como alterado pela letra da C15.1, e o gate o aceita só com a supersessão conferida (ciclo 1 com os bytes protegidos e `cycle.supersedes` apontando para eles), por decisão do dono. `PROTECTED_ARTIFACT_REPORT.md` mostra o item e o encadeamento | C15.1, decisão do dono | IC-F011 |
| `scripts/isolation.py` | na rc10 os três domínios têm configuração: o domínio sem orquestração passa a ser um fora do protocolo (`forex` → `CONFIG_INVALID`, nada escrito), e a proposta do stocks é conferida na orquestração do brasileirao (BLOCK `DOMAIN_MISMATCH`, sem task). Uma conferência a mais (22) | C14 | — |
| `runtime_targets.json`, `hosted_ci_final_targets_ciclo2.json`, `scripts/secrets_scan.py` | alvos novos (cain `fb0e1dc` rc10, transporte `b11494a` rc5) | C14 | — |
| `RAW_LOGS/runtime/run36426935949/` | run de push único, com todas as fases do runtime: cleanroom-final, C24.3 (d), e2e, N+1, isolamento, F01–F15 e soak com LLM local | C14 | — |
| `RAW_LOGS/windows-smoke-ciclo2/` | E2E + restart no PC 2, na mesma pasta autorizada (D-23), com o novo `stage-ciclo2` (requisitos de `fb0e1dc` e `ee3d3d1`). `logs`/`out` da rodada anterior renomeados para `logs-rc7-c14s`/`out-rc7-c14s`; nada apagado | C14, WINDOWS_SMOKE | — |
| `RAW_LOGS/{core-identity,contract-revalidation,protected,final-wheels,secrets}-ciclo2/`, `RAW_LOGS/hosted-ci/final-ciclo2/` | conferências refeitas com os final_commits `fb0e1dc`/`b11494a`/`ee3d3d1`; CI de push verde nos três (no cain, o run do main e o da tag) | C14, C21 | — |
| `DECISION_POLICY_REPORT.md`, `ENVELOPE_V2_CONFORMANCE_REPORT.md` | tabela de regras da v2 na ordem de avaliação, campos novos da configuração, versões dos consumidores e chaves de evidência do run novo | C14, C20 | — |
| `QUALIFICATION_ATTESTATION_superseded_2d588e3df966.json`, `ATTESTATION_PARTIAL_ciclo2-attestation.json`, `QUALIFICATION_ATTESTATION.json` | a attestation anterior (QUALIFIED, cain rc7 / transporte rc4) é preservada. A nova aponta para ela por `supersedes_sha256` | C7.1 regra 8, C14 | — |

## 2026-09-28 — ciclo 3 (C14): validação prática, métricas na memória e no modelo, cain 0.4.13rc12 (sessão cripto, PC 2)

O dono pediu uma validação prática do CAIN × cripto na rc10 (`RAW_LOGS/pratica-rc10`), para ver se o CAIN tem as informações que deveria:
- auditoria da configuração contra as fontes pinadas;
- histórico do cripto no arquivo de achados;
- paráfrases de hipóteses fechadas;
- ciclo real de 21 rodadas com dados reais e o modelo local.

Decisões do dono: "Código + config"; sobre a config, "Manter e registrar"; ciclo 3 dos congelados mostrado antes de congelar, "Aprovo"; sobre o soak, "Soak conta a recusa". O cripto não mudou: o final_commit continua `ee3d3d1`.

| Onde | O quê | Por quê | Commit / PR |
|---|---|---|---|
| `RAW_LOGS/pratica-rc10/` | validação prática: config 10 OK / 3 divergências; findings check (ID qualificado e paráfrases); ciclo real de 21 rodadas; mini-ciclo com o código corrigido. 67 arquivos com SHA256SUMS | pedido do dono | — |
| `FINDINGS.json` (`scripts/add_findings_pratica.py`, `scripts/update_ic_f012_soak.py`) | IC-F012: config aceita QUAL-SHADOW-001 e datasets da Etapa A que a admissão real não aceita (ACCEPTED_LIMITATION, duas decisões do dono). IC-F013: memória e modelo sem métricas (FIXED). IC-F014: ID qualificado no findings check (FIXED). IC-F015: paráfrase não detectada (OPEN_AWAITING_OWNER, P2) | validação prática | cain#73 |
| `cain` | `result_metrics` opcional (números finitos nos fatos, no view e no contexto do LLM); ID qualificado no findings check; `crypto.json` do ciclo 3 | IC-F013, IC-F014 | cain#73 (`c3a28d9`) |
| `cain` | contexto do modo de proposta dentro do orçamento do provider (os mais antigos saem; `results_omitted`) | regressão da rc11 (o #73 levava o contexto além de 7680 bytes e o soak ficava sem propostas) | cain#75 (`2148334`); versão cain#76; pré-release `v0.4.13rc12` (`302a5c8`, wheel `988a0fb9…`) publicada por esta sessão (`RAW_LOGS/publish-candidates/publish_cain_0.4.13rc12.log`) |
| `FROZEN_PARAMETERS.json`, `FROZEN_PARAMETERS_cycle2_2ee84f572c1f.json`, `scripts/freeze_cycle3.py` | ciclo 3: só `crypto_config.result_metrics` (retorno líquido, IC 95%, amostra). O ciclo 2 fica no mesmo blob, e `cycle.chain` aponta o ciclo 1 | C14, C15 | `73cab73` |
| `scripts/protected_check.py`, `scripts/render_reports.py` | a cadeia `cycle.supersedes` + `cycle.chain` é seguida até os bytes protegidos (ciclo 1), com cada elo conferido | C15.1, IC-F011 | — |
| `scripts/soak.py` | a recusa do domínio com código fechado, registrada nos dois lados, conta como desfecho terminal. Conferência nova: hipótese recusada nunca volta (R15) | IC-F012, decisão do dono | — |
| `RAW_LOGS/runtime/run36435382707/`, `RAW_LOGS/windows-smoke-ciclo3-rc11/` | rodada da rc11, preservada. Todas as fases passaram, menos o soak (llm_proposals 0/5, contexto acima do orçamento). Windows E2E 56/56 | C14 | — |
| `RAW_LOGS/runtime/run36439656179/` | run de push único na rc12, com todas as fases: cleanroom-final, C24.3 (d), e2e, N+1, isolamento, F01–F15 e soak com LLM local (6 propostas) | C14 | — |
| `RAW_LOGS/windows-smoke-ciclo3/` | E2E + restart no PC 2 com a rc12, na mesma pasta autorizada (D-23). As rodadas anteriores ficam renomeadas (`logs-rc10-ciclo2`, `logs-rc11-ciclo3`); nada apagado | C14, WINDOWS_SMOKE | — |
| `RAW_LOGS/{core-identity,contract-revalidation,protected,final-wheels,secrets}-ciclo3/`, `RAW_LOGS/hosted-ci/final-ciclo3/` | conferências refeitas com os final_commits `302a5c8`/`b11494a`/`ee3d3d1`; CI de push verde nos três (no cain, main e tag) | C14, C21 | — |
| `runtime_targets.json`, `hosted_ci_final_targets_ciclo3.json`, `scripts/{secrets_scan,update_gates}.py`, `DECISION_POLICY_REPORT.md`, `ENVELOPE_V2_CONFORMANCE_REPORT.md` | alvos, ledger e relatórios na rc12 | C14, C20 | — |
| `QUALIFICATION_ATTESTATION_superseded_d1c76b4eedb9.json`, `ATTESTATION_PARTIAL_ciclo3-attestation.json`, `QUALIFICATION_ATTESTATION.json` | a attestation anterior (QUALIFIED, cain rc10) é preservada. A nova aponta para ela por `supersedes_sha256` | C7.1 regra 8, C14 | — |

## 2026-09-28 — achados pós-attestation: disputa da trava do Ops (teste de ecossistema, sessão cripto, PC 2)

Pedido do dono: provar o ecossistema inteiro junto, com atenção ao Core e ao Ops.

O teste: dois consumidores do cripto iniciados ao mesmo tempo sobre a mesma task, spool, ledger e estado do domínio, 20 repetições no Windows e 20 no Linux. Stack: cain 0.4.13rc12, Ops 4.2.2rc1, Core 3.2.1 e cripto 1.2.0rc3.

A trava do Ops, com a correção SHARED-005, nunca derrubou processo. Nas 40 repetições houve uma admissão, um experimento e um RESULT terminal.

Decisão do dono: "Registrar + regra". A attestation é reemitida só pelos achados, sem refazer fases.

| Onde | O quê | Por quê | Commit / PR |
|---|---|---|---|
| `RAW_LOGS/ops-disputa-windows/`, `RAW_LOGS/ops-disputa-linux/` | resumo, comandos e scripts das duas disputas, com SHA256SUMS | evidência | — |
| `FINDINGS.json` (`scripts/add_findings_disputa.py`) | IC-F016 (P2, ACCEPTED_LIMITATION): no Windows, 1/20, o perdedor morre com PermissionError em `durable_io.atomic_write`, na escrita de `reference-materialization.json` antes do `run_job` do Ops. IC-F017 (P2, ACCEPTED_LIMITATION): o perdedor publica OPS_FAILED_RETRYABLE para uma task concluída (39/40). Regra operacional nos dois: um consumidor por domínio por vez. Correção anotada para a próxima versão do cripto (C24.4) | teste de ecossistema; C6 | — |
| `scripts/update_gates.py`, `QUALIFICATION_ATTESTATION_superseded_dc4b9cf9946e.json`, `ATTESTATION_PARTIAL_achados-disputa-attestation.json`, `QUALIFICATION_ATTESTATION.json` | a attestation anterior (QUALIFIED, ciclo 3) é preservada. A nova tem os mesmos gates e evidências de fase e os achados novos na contagem | C7.1 regra 8 | — |

## 2026-09-28 — C14 na cain 0.4.13rc13 e no transporte 0.1.0rc6 (sessão cripto, PC 2)

A sessão STOCKS publicou a cain 0.4.13rc13, por decisão do dono lá: molde do LLM sem task recusada, `allowed_requests`, `refusal_mismatches`, linter e findings v2. Ela também publicou o transporte 0.1.0rc6, com a trava exclusiva por domínio no consumidor (`CONSUMER_BUSY`); é a correção dos achados da disputa, decidida pelo dono ("Só o transporte").

`policy.py` e `crypto.json` estão iguais aos da rc12, e os congelados do ciclo 3 não mudam. Pela C14, as fases foram refeitas com as wheels finais novas. O cripto não mudou (`ee3d3d1`).

| Onde | O quê | Por quê | Commit / PR |
|---|---|---|---|
| `runtime_targets.json`, `hosted_ci_final_targets_rc13.json`, `scripts/{secrets_scan,update_gates,render_reports,rc13_edits}.py`, `DECISION_POLICY_REPORT.md`, `ENVELOPE_V2_CONFORMANCE_REPORT.md` | alvos na cain `960fb25` (wheel `a1d94fd5…`) e no transporte `bac1f7b` (wheel `6c7e83c4…`), os dois conferidos por download anônimo | C14 | cain#77/#78/#79; ecosystem-predictor#36 |
| `FINDINGS.json` | IC-F016 e IC-F017 passam a FIXED pelo transporte 0.1.0rc6 | correção decidida pelo dono na sessão STOCKS | ecosystem-predictor#36 |
| `RAW_LOGS/transport-rc6-disputa/` | conferência da correção com o código do PR, que é igual ao publicado. Disputa: 20/20 no WSL e 20/20 no Windows (1 RESULT, 0 envelope falso, 0 queda). Morte do dono da trava com retomada: 6/6 | evidência do FIXED | — |
| `RAW_LOGS/runtime/run36462444590/` | run de push único, com todas as fases do runtime: cleanroom-final 48/19/65, C24.3 (d) 10/10, e2e 56/56, N+1 21/21, isolamento 22/22, F01–F15 sem falha, soak 48/48 (6 propostas do LLM, `allowed_requests` nas 6) | C14 | — |
| `RAW_LOGS/windows-smoke-rc13/` | E2E + restart no PC 2: 56/56. `logs`/`out` da rc12 renomeados para `logs-rc12-ciclo3`/`out-rc12-ciclo3`; nada apagado | C14, WINDOWS_SMOKE | — |
| `RAW_LOGS/{core-identity,contract-revalidation,protected,final-wheels,secrets}-rc13/`, `RAW_LOGS/hosted-ci/final-rc13/` | conferências com os final_commits `960fb25`/`bac1f7b`/`ee3d3d1`; CI de push verde nos três (no cain, main e tag) | C14, C21 | — |
| `QUALIFICATION_ATTESTATION_superseded_a071fe2ca22e.json`, `ATTESTATION_PARTIAL_rc13-attestation.json`, `QUALIFICATION_ATTESTATION.json` | a attestation anterior (QUALIFIED, rc12) é preservada. A nova aponta para ela | C7.1 regra 8 | — |

## 2026-09-30 — C14 na cain 0.4.13rc15 + transporte 0.1.0rc7 + cripto 1.2.0rc4 (D-27; sessão Linux na nuvem + GitHub Actions)

Por quê: as correções de 2026-09-29 foram publicadas como cain v0.4.13rc15 (`ae00017a`), transporte v0.1.0rc7 (`b0da4fd8`) e cripto v1.2.0rc4
(`21f8b182`, main; a Etapa A do crypto foi reaberta como V1.2 para esse alvo e está BLOCKED no Windows local). Pela C14 as fases que exercitam
essas wheels foram refeitas no Linux primário. `crypto.json`, `stocks.json` e `brasileirao.json` da rc15 são byte a byte os da rc13; `policy.py`
difere só por uma anotação de tipo (`found: list = []`); `service.py`/`cli.py`/`config.py`/`llm.py` trazem as correções de tipo e a memória por
domínio (`_memory_view`). O ambiente da sessão não baixa artefatos do Actions: cada job devolve a saída bruta numa branch
`integration-crypto/raw-<run>-<job>` (SHA256SUMS), copiada sem edição.

| Onde | O quê |
|---|---|
| `runtime_targets.json`, `hosted_ci_final_targets_rc15.json` | alvos rc15 / rc7 / rc4 (commits das tags); `scripts/contract_revalidation.py` lê a Etapa A vigente de `qualification/crypto/runtime_target.json` (V1.2 = 21f8b182); `scripts/secrets_scan.py` com os diffs deste ciclo |
| `.github/workflows/integration-crypto-runtime.yml` | job `static` (hosted_ci, C24.3 a/b/e/f, protegidos, segredos) e `core_identity` no runtime; saída devolvida por branch |
| `RAW_LOGS/runtime/run36648103793/` | run [36648103793](https://github.com/leonardosovienski/predictor-qualification/actions/runs/36648103793), push em `integration-crypto/runtime-…-rc15` (`2dbfb0a`), todas as fases exit 0: cleanroom-final (conformidade 48/0 falhas, transporte 20/0, cain 65/0); C24.3 (d) 10/0; e2e 56/0; N+1 21/0; isolamento 22/0; F01–F15 50 conferências, 0 falhas; soak 48/0 (24 ciclos, 18 duplicatas, 6 restarts do domínio, 10 do CAIN, 6 intercalados, 6 propostas do LLM `qwen2.5:0.5b`) |
| `RAW_LOGS/core-identity-rc15/`, `RAW_LOGS/final-wheels-rc15/` | identidade das wheels 12/0; final_wheels 17/0 (assets baixados e conferidos; instalado no run == declarado) |
| `RAW_LOGS/hosted-ci/final-rc15/` | push verde no SHA exato: cain `ae00017`, ecosystem `b0da4fd`, cripto `21f8b18` |
| `RAW_LOGS/contract-revalidation-rc15/` | C24.3 estático 6/0 (diff do domínio vazio: a Etapa A vigente já é o alvo) |
| `RAW_LOGS/protected-rc15/` | domínios intactos (crypto 1387, stocks 89, brasileirao 1884 blobs); FROZEN_PARAMETERS encadeado; **`qualification/crypto/runtime_target.json` alterado pela reabertura V1.2** (D-27): o pin do alvo da Etapa A mudou fora desta missão |
| `RAW_LOGS/secrets-rc15/` | 0 achados ({'cain 960fb2561470..ae00017ab4a2': 733, 'ecosystem-predictor bac1f7b7b3ae..b0da4fd8d0c4': 240, 'cripto-predictor ee3d3d17de0b..21f8b1822862': 32640, 'qualification/integration-crypto files': 1156}) |
| `RAW_LOGS/static-rc15/run36648103793/static.log` | log do job `static` (parou no protected_check pela regra da letra; segredos varridos localmente) |
| `scripts/rc15_gates.py`, `GATES.json`, `ATTESTATION_PARTIAL_rc15-linux-primary.json`, `ATTESTATION_PARTIAL_rc15-final-wheels.json` | ledger do ciclo; `supersedes_sha256` = attestation rc13 vigente (`69fa0393a24c…`), que **continua vigente** (QUALIFIED para rc13/rc6/rc3) |
| relatórios (`render_reports.py -rc15`), `EVIDENCE_NUMBERS.json` | seções do ciclo; a linha do Windows diz NOT_RUN em vez de inventar número |

**Estado terminal desta sessão: `BLOCKED`** (C7.3; só parciais). Gates PASS: todos menos `WINDOWS_SMOKE` (NOT_RUN: Windows do PC 2 do dono, D-23) e
`PROTECTED_ARTIFACTS_UNCHANGED` (NOT_RUN: aceitar o pin novo do crypto neste ciclo é decisão do dono, como a IC-F011 fez para o FROZEN_PARAMETERS).
Além disso, C7.1 regra 7: a attestation da Etapa A do cripto no main é a V1.1 (QUALIFIED para 341d270/rc2); a V1.2 (21f8b182/rc4, alvo deste
ciclo) só fecha depois do Windows local do dono (`qualification/crypto/REABERTURA_V1.2.md`). O que falta o dono fazer: (1) Windows do crypto V1.2;
(2) Windows do PC 2 desta integração com os alvos rc15; (3) decidir o pin do conjunto protegido. Depois: `attest.py final` supersede a rc13.

## 2026-09-30 — evidência do Windows no `windows-latest` (run 36665679329), sem mudança de gate

O runtime da missão passou a rodar também no Git Bash do `windows-latest` (`scripts/runtime_env.sh`, `scripts/ci_runtime.sh`; job
`windows` do `integration-crypto-runtime.yml`, só a fase `e2e`), como a integration-stocks já fazia. Run 36665679329 (branch
`integration-crypto/runtime-windows-rc15w`, `bd47a9d`), alvos do rc15 (cain 0.4.13rc15, transporte 0.1.0rc7, cripto 1.2.0rc4):
E2E + restart pelo `e2e.py` **56/0**, venvs limpos só com as wheels publicadas (`runtime_env run_at=2026-09-30T03:44:00Z host=runnervmfi6oq where=github_actions os=Windows_NT uname=MINGW64_NT-10.0-2610…`).
Saída bruta em `RAW_LOGS/runtime/run36665679329-windows/` (SHA256SUMS do job). O primeiro run (36664202699) falhou na montagem
do runtime por um caminho MSYS embutido em string Python (`runtime_env.sh`, função `field`), corrigido por argv.

O secundário registrado da missão continua o Windows do PC 2 (D-23): `WINDOWS_SMOKE` segue `NOT_RUN` neste ledger até uma
decisão do dono em `DECISIONS.json` dizer que este job vale como secundário (proposta D-31 na sessão de 2026-09-30, junto da
D-29 para o pin do conjunto protegido e da D-30 para o Windows do crypto); o estado do ciclo rc15 continua **BLOCKED**.

## 2026-10-07 — C14 na cain 0.4.13rc16 (D-34; lock por registro, D-32): attestation reemitida **QUALIFIED** (rc16 / rc7 / rc4)

Por quê: o programa de remediação (R01) trocou o `uv.lock` do cain de URLs de release para o registro `STACK_WHEELS.json` + índice local
(D-32); pela C14, a wheel nova exige refazer as fases que a exercitam. A cain v0.4.13rc16 (`de5db06b`, wheel `d8fca502…`, build duplo
byte-idêntico e igual ao build local) tem o código do pacote idêntico ao da rc15 (`src/cain/__init__.py` só muda a versão);
`policy.py` e `crypto.json` iguais. Transporte rc7 e cripto rc4 sem mudança; o repositório produtor do ecosystem chama-se
`ecosystem-predictor-cain` desde 2026-10-05 (mesmos assets e sha256). As decisões D-29/D-30/D-31, delegadas pelo dono em 2026-09-30 e
escritas hoje, fecham o que bloqueava o ciclo rc15: pin do crypto V1.2 aceito no conjunto protegido, `windows-latest` como secundário
do crypto (V1.2 **QUALIFIED**) e desta missão. Ambiente da sessão: Linux na nuvem; primário no GitHub Actions; saída devolvida por branch
`integration-crypto/raw-<run>-<job>` (SHA256SUMS) e copiada sem edição.

| Onde | O quê |
|---|---|
| `runtime_targets.json` (`cycle = rc16`), `hosted_ci_final_targets_rc16.json` | alvos rc16 / rc7 / rc4; transporte e protocolo no repositório renomeado |
| `scripts/runtime_env.sh`, `scripts/cleanroom_final.sh`, `scripts/transport_dev_requirements.py` | lado do CAIN instalado pelo registro: `stack_wheels.py fetch` + `check`, `requirements` (hash das wheels do stack), pip `--require-hashes --find-links .stack-wheels`; `env/stack_wheels_cain.sha256` grava o sha256 de cada wheel baixada; os requisitos de teste do transporte saem do lock rc7 por tomllib (o lock fixa o protocolo pela URL aposentada, que o `uv export` tenta resolver) |
| `scripts/core_identity.py`, `scripts/final_wheels_check.py`, `scripts/secrets_scan.py`, `scripts/rc16_gates.py`, `scripts/render_reports.py` | cadeia de identidade do registro (D-32: pyproject ↔ STACK_WHEELS.json ↔ uv.lock ↔ fetch ↔ instalado); identidade das wheels do índice pelo sha256 do fetch; download anônimo dos assets; ledger do ciclo (runs separados para as fases, o Windows e o cleanroom-final refeito); Windows pelo job `windows-latest` |
| `.github/workflows/integration-crypto-runtime.yml` | clone de `ecosystem-predictor-cain`; conferências estáticas rotuladas pelo ciclo (`RAW_LOGS/static/run<id>/`); token do job para o fetch |
| `RAW_LOGS/runtime/run37696817503/` | run [37696817503](https://github.com/leonardosovienski/predictor-qualification/actions/runs/37696817503) (push em `integration-crypto/runtime-…-rc16`, `36ac982`): C24.3 (d) 10/0; e2e 56/0; N+1 21/0; isolamento 22/0; F01–F15 50 conferências, 0 falhas; soak 48/0 (24 ciclos, 18 duplicatas, 6 restarts do domínio, 10 do CAIN, 6 intercalados, 6 propostas do LLM `qwen2.5:0.5b`); identidade das wheels 13/0 (`static/core_identity.json`). O cleanroom-final deste run falhou no passo 2 (transporte): `uv export` do lock rc7 tentou a URL aposentada do protocolo (404) — conformidade 48/0 e cain 65/0 já tinham passado; o log fica como está |
| `RAW_LOGS/runtime/run37698397521/` | run [37698397521](https://github.com/leonardosovienski/predictor-qualification/actions/runs/37698397521) (`integration-crypto/runtime-cleanroom-rc16b`, `2367e3c`): cleanroom-final refeito com `transport_dev_requirements.py`: conformidade 48/0, transporte 20/0, cain 65/0; venvs limpos só com as wheels publicadas; identidade 13/0 (`RAW_LOGS/core-identity-rc16/`) |
| `RAW_LOGS/runtime/run37696817503-windows/` | job `windows` do run 37696817503 (`windows-latest` × 3.13, D-31): E2E + restart 56/0 |
| `RAW_LOGS/static/run37696817503/` e cópias em `hosted-ci/final-rc16/`, `contract-revalidation-rc16/`, `protected-rc16/`, `secrets-rc16/` | CI de push verde nos SHAs exatos (cain `de5db06b` run 37695085002, ecosystem-predictor-cain `b0da4fd8`, cripto `21f8b182`); C24.3 estático 6/0; conjunto protegido: domínios intactos, FROZEN_PARAMETERS encadeado (IC-F011), itens do crypto V1.2 re-congelados pela D-29; segredos 0 achados (diff cain rc15→rc16 e arquivos da missão) |
| `RAW_LOGS/final-wheels-rc16/` | final_wheels 17/0: 8 assets baixados e conferidos; instalado no run == declarado (snapshot e bundle pelo registro do cain) |
| `PROTECTED_SET.json` (D-29), `GATES.json`, `EVIDENCE_NUMBERS.json`, relatórios | ledger rc16 com todos os gates PASS; números gerados de `RAW_LOGS` por script (C20) |
| `QUALIFICATION_ATTESTATION_superseded_69fa0393a24c.json` (rc13, preservada), `ATTESTATION_PARTIAL_rc16-attestation.json`, `QUALIFICATION_ATTESTATION.json` | attestation **QUALIFIED** para cain `de5db06b` / rc16, ecosystem-predictor-cain `b0da4fd8` / transporte rc7, cripto `21f8b182` / rc4, core 3.2.1, ops 4.2.2rc1; `supersedes_sha256` = rc13 (`69fa0393…`); `domain_attestations` = crypto V1.2 (`0c8589b1…`), revalidação C24.3 PASS; `attest.py check` OK; P0 = P1 = 0, P2 = 4 |

Limites (C22): vale para os `final_commits`/`final_wheels` declarados e para os vetores e perfis congelados; não garante edge nem lucro.

## 2026-10-07 (noite) — C14 refeito depois da adoção da rc16 na lock conjunta do ecosystem (rc16e): attestation reemitida **QUALIFIED**

Por quê: o `ecosystem-predictor-cain` adotou a cain 0.4.13rc16 na lock conjunta `compat/` e publicou ecosystem `v0.2.2` (`main` `6aeec475`,
PR #56; wheel `63cb1c16…`). Pela C14 ("cain, ecosystem-predictor ou envelope V2 → fases das integrações que os exercitam + reemissão"),
todas as fases foram refeitas num só run, com as mesmas wheels do ciclo rc16 (cain rc16, transporte rc7, protocolo rc2, cripto rc4, core,
ops): a mudança no ecosystem é só a lock conjunta, que o runtime desta missão não instala; `final_commits`/`final_wheels` não mudam
(o commit do ecosystem nos `final_commits` continua sendo o da tag do transporte, `b0da4fd8`); o `main` do ecosystem entra em
`hosted_ci_final_targets_rc16e.json` (CI de push verde em `6aeec475`) e em `GATES.json → cycle_rc16e.ecosystem_main_commit`.

| Onde | O quê |
|---|---|
| `runtime_targets.json` (`cycle = rc16e`), `hosted_ci_final_targets_rc16e.json`, `scripts/rc16_gates.py` (rótulo do ciclo por argumento) | alvos iguais ao rc16; conferências estáticas rotuladas rc16e |
| `RAW_LOGS/runtime/run37703318858/` e `-windows/`, `RAW_LOGS/static/run37703318858/` (cópias em `*-rc16e/`) | run [37703318858](https://github.com/leonardosovienski/predictor-qualification/actions/runs/37703318858) (push em `integration-crypto/runtime-…-rc16e`, `231e6b2`), todas as fases exit 0: cleanroom-final (conformidade 48/0, transporte 20/0, cain 65/0); C24.3 (d) 10/0; e2e 56/0; N+1 21/0; isolamento 22/0; F01–F15 50/0; soak 48/0 (24 ciclos, 18 duplicatas, 6 restarts do domínio, 10 do CAIN, 6 intercalados, 6 propostas do LLM); Windows E2E + restart 56/0; identidade 13/0; final_wheels 17/0; CI de push verde nos SHAs exatos (cain `de5db06b`, ecosystem-predictor-cain `b0da4fd8` e `6aeec475`, cripto `21f8b182`); C24.3 estático 6/0; protegidos (domínios intactos, FROZEN_PARAMETERS encadeado); segredos 0 |
| `QUALIFICATION_ATTESTATION_superseded_cc44bdf984c9.json` (rc16, preservada), `ATTESTATION_PARTIAL_rc16e-attestation.json`, `QUALIFICATION_ATTESTATION.json` | attestation **QUALIFIED** com os mesmos `final_commits`/`final_wheels` do rc16; `supersedes_sha256` = rc16 (`cc44bdf9…`); `attest.py check` OK; P0 = P1 = 0, P2 = 4 |
