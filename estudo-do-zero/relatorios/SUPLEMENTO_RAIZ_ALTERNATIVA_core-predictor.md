# Suplemento: core-predictor em raiz de qualificação

Fonte alternativa `C:\QUALIFICACAO\repos\core-predictor`, identidade em linked-roots.json; fonte primária `C:\PREDICTORS\core-predictor` não foi substituída. PRELIMINAR_ALTERNATIVA_core-predictor.md salvo antes das narrativas alternativas ['README.md', 'ARCHITECTURE_IMPLEMENTATION.md', 'HANDOFF.md']. Todos rastreados foram hashados; código/config alterado lido integralmente; código byte idêntico reaproveita a inspeção primária, sem nova execução. Diferenças apenas de line ending são explicitamente separadas e não anulam hash bruto.

Código src, testes, pyproject e uv.lock são byte a byte iguais à fonte primária. As três mudanças materiais são workflows: --frozen→--locked em CI/release; consumer compatibility retirado de push/PR e mantido workflow_dispatch histórico, com alteração das actions. Portanto mecanismos de replay/trials e limitações anteriores permanecem aplicáveis a estes bytes; estado de Actions não pode ser transplantado.

Arquivos materialmente diferentes após normalizar somente quebra de linha: `.github/workflows/ci.yml`, `.github/workflows/consumer-compatibility.yml`, `.github/workflows/release.yml`.

Arquivos diferentes somente em line ending: .

Fontes: alternative-changes.json,alternative-hashes.json,alternative-difference-classes.json,alternative-material.diff e alternative-lock-*.json em evidencias/core-predictor. Declarações documentais alternativas são preservadas em alternative-narrative-*.diff. Nenhum teste da raiz alternativa original foi acionado. Não generalizar diferenças para o main remoto ou AnexoA.
