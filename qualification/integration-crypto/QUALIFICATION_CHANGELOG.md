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
