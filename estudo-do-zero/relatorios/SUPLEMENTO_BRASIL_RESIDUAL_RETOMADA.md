# Brasileirão: mesclagem das coberturas e residual — retomada 2026-09-30

## Mesclagem

Scripts: `root-scripts-coverage.json` (75) + `shared-brasil-scripts-coverage.json` (35) + `applications-brasil-scripts-coverage.json` (14) = 124 caminhos disjuntos, todos com sha256 igual a `hashes.json`/`untracked-hashes.json`; resultado em `evidencias/brasileirao-predictor/brasil-scripts-coverage-merged.json`. Os 119 `.py` de `brasileirao_scripts/` estão cobertos; os cinco extras são os `.ps1` de instalação de tarefas e os dois scripts de migração (estes revisados nesta retomada).

Testes: `shared-brasil-tests-coverage.json` (107) + `applications-semantic-notes.json` (103 entradas `tests/`) = 210, igual ao total de `tests/*.py`; resultado em `brasil-tests-coverage-merged.json`. .NET: 42 arquivos em `shared-dotnet-coverage.json`, hashes iguais.

`coverage.json` foi reconciliado por caminho e hash: 123 scripts, 40 linhas .NET e 24 arquivos residuais passaram a certificados com a nota da cobertura de origem. Nenhuma linha foi marcada sem nota semântica registrada.

## Residual lido nesta retomada

26 arquivos próprios que a pausa deixou fora das coberturas individuais tinham, no clone do remoto (main 1e0c6f0b), bytes idênticos aos hashes da linha de base e foram lidos integralmente: `tools/runtime_lab/*` (5), `tools/publication_validation/*` (4), `tools/integration_validation/run.py`, `tools/export_cain_*` e seus testes (4), `scripts/migration/*` (2), `poc_oddspapi.py`, `research/kimi_market05/*` (6), `compose.yaml`, `config.yaml` e `contracts/redis-protocol-v2.md`. Notas em `retomada-residual-notes.json`.

Pontos observados: os laboratórios (`runtime_lab`, `publication_validation`) usam audit hooks que negam rede, subprocess, SQLite e escrita fora da saída e bloqueiam a leitura de `.env`, `config.yaml`, `data/`, `reports/`, `research/` e dos avaliadores protegidos; `integration_validation/run.py` exercita o consumidor CAIN instalado com bundle/snapshot reais e casos negativos; os exportadores CAIN exigem pin sha256 explícito, fonte committed e escrita atômica, e declaram ausência de previsão/liquidação admissível e relógios desconhecidos; `build_data_archive.py` bloqueia código e binários por nome e audita ZIPs aninhados com limites. `research/kimi_market05` é protótipo com números sintéticos declarados como tais e testes contratuais inteiramente `skip`; a versão de pesquisa do PoC OddsPapi expõe a chave em exceções, corrigido na versão da raiz. `config.yaml` registra o desligamento do ensemble xG (trial h12) com a explicação do uso indevido de holdout.

## Residual não certificável nesta sessão

16 arquivos (workflows do GitHub, contratos JSON, `pyproject.toml`, `pytest.ini`, `global.json`, `schemas/odds_snapshot_v1.json`, `uv.lock`) têm bytes na árvore local (HEAD f8780690 com modificações preexistentes) que diferem do remoto ou não existem nele; sem acesso ao original Windows não é possível ler o mesmo conteúdo. A classificação anterior foi preservada (`aprofundado-caminho-central` para workflows/pyproject/schemas de protocolo; leitura estrutural para os demais) e a lista está em `retomada-residual-pendentes.json`. Nenhum é código Python próprio.

Limite: leitura não é execução; nenhum teste, laboratório, worker ou coleta foi acionado.
