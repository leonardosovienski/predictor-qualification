# Suplemento: predictor-ops em raiz de qualificação

Fonte alternativa `C:\QUALIFICACAO\repos\predictor-ops`, identidade em linked-roots.json; fonte primária `C:\PREDICTORS\predictor-ops` não foi substituída. PRELIMINAR_ALTERNATIVA_predictor-ops.md salvo antes das narrativas alternativas ['README.md', 'ARCHITECTURE_IMPLEMENTATION.md', 'HANDOFF.md']. Todos rastreados foram hashados; código/config alterado lido integralmente; código byte idêntico reaproveita a inspeção primária, sem nova execução. Diferenças apenas de line ending são explicitamente separadas e não anulam hash bruto.

Versão sobe4.2.1→4.2.2rc1. Única mudança de src é _mutation_guard: inicialização de byte usa descriptor não buffered, captura PermissionError e espera a trava em vez de repropagar no seek/close Windows. Teste novo multiprocessos segura byte vazio e verifica espera>=0.3s; ET-SRC somente. Teste version aceita PEP440rc. CI/release passam a --locked; consumer contracts movido para workflow_dispatch histórico, fora push/PR. Runner/modelos/risco/provenance/processes continuam byte idênticos. Sem execução alternativa.

Arquivos materialmente diferentes após normalizar somente quebra de linha: `.github/workflows/ci.yml`, `.github/workflows/consumer-contracts.yml`, `.github/workflows/release.yml`, `pyproject.toml`, `src/predictor_ops/runtime.py`, `tests_v2/test_runtime.py`, `tests_v2/test_version_contract.py`, `uv.lock`.

Arquivos diferentes somente em line ending: .

Fontes: alternative-changes.json,alternative-hashes.json,alternative-difference-classes.json,alternative-material.diff e alternative-lock-*.json em evidencias/predictor-ops. Declarações documentais alternativas são preservadas em alternative-narrative-*.diff. Nenhum teste da raiz alternativa original foi acionado. Não generalizar diferenças para o main remoto ou AnexoA.
