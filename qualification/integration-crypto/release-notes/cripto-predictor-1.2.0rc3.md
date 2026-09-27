Pré-release da missão `integration-crypto` (Etapa B). Commit `ee3d3d17de0b76cf731808243ffa838a0f5ee8cc`
(branch `integration-crypto/adapter-20260927`, a partir de `174573d`, mesma árvore de `341d270` = v1.2.0rc2).

Muda só:
- `GarimpoInvestimentos/adapters/research_v2.py`: adapter V2 (stdlib + `adapter_api`), carregado pelo nome do
  módulo pelo consumidor do transporte (`predictor-research-transport`);
- a versão pré-release `1.2.0rc3` (`pyproject.toml`, `__version__` e a linha da versão no `uv.lock`), exceção C24.3(a).

Nada fora de `GarimpoInvestimentos/adapters/` muda além da versão. O `main` pós-merge conterá #128–#134 + adapter
e **não** será o commit qualificado: o `final_commit` é o desta tag.
Wheel e sdist construídos 2× por `git archive` com `SOURCE_DATE_EPOCH=1758240000` (mesmos sha256).
Qualificação, não operação: sem capital, sem conexão com exchange.
