# PROTECTED_ARTIFACT_REPORT — missão brasileirao (gate `PROTECTED_ARTIFACTS_UNCHANGED`, C15.1)

* Conjunto: `PROTECTED_SET.json`, fechado em `truth-map` no commit `e14f3394c1908fae6d2f25754e6ab3a6792dbf1e`
  **antes de qualquer mudança**: 1877 arquivos, identidade = blob git. Composição: as 172 linhas de
  `docs/open_source_research/OSR-20260911-01/PROTECTED_PATHS.txt` (H9, H14, H15, A1, coleta de odds,
  trials), `contracts/h8-ou25-frozen-candidate.json`, `reports/**/frozen_candidate.json`,
  `reports/benchmark_h9_frozen_*.json` (prompt §3/§5), mais o declarado congelado pelo próprio repo:
  bytes congelados do ruff (`prospective_protocol_v2.py` e dois testes, com os recibos
  `RECIBO_*.json`), contratos com `frozen_at` (inclui o calendário `season-2026-turn-split-paper.json`),
  `config.yaml` (hiperparâmetros congelados), `data/trials*.json`, `reports/**` (artefatos de
  avaliação), `docs/continuation/**` (evidência datada), o pacote OSR e a política científica
  (`docs/PREDICTION_PROTOCOL.md`, `docs/PROJECT_LOGIC_REGISTER.md`).
* Verificação no commit final `04b42c9245e6ec75d72ec6a27d151ee2afef5e70` (`scripts/protected_check.py`):
  **1877/1877 blobs iguais, 0 alterados** → `RAW_LOGS/attestation/protected_check_04b42c9.json`.
* O conjunto só cresceu; nenhum item foi descoberto depois já alterado.
* Nada foi retunado: o modelo avaliado usa os valores de `config.yaml` do commit (lidos por
  `git show`, sem cópia editada); `brasileirao:H8/H9/H14/H15/A1` são recusadas pela admission
  (`PROTECTED_HYPOTHESIS`); 2025 (holdout selado) é recusado como alvo (`HOLDOUT_SEALED`, dupla trava
  na admission e no handler) e nunca foi pedido nos runs reais (`scripts/real_env.py` recusa 2025).
* Nota (BR-F004): os relatórios protegidos `reports/benchmark_*` foram produzidos pelo motor de
  benchmark que tinha o vazamento de jogo em andamento; continuam intocados, como exige a C15.1. Os
  números deles devem ser lidos com essa ressalva.
