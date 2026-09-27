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
