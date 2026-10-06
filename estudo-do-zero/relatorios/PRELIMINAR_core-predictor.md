# Caracterização preliminar — core-predictor



Base local: `C:\PREDICTORS\core-predictor`; HEAD `9bf43efe92459a0b484cac00f51170b2c70d420f`.



Biblioteca Python predictor_core, pacote predictor-core 3.2.1 >=3.13, dependências runtime obrigatórias vazias e extras HTTP/scraping. A API pública lazy exporta contratos de pontos e observações, aquisição/freezes, replay temporal, métricas probabilísticas e financeiras, bootstrap, registros de tentativas e controles sintéticos. Não se encontrou project.scripts no manifest examinado. Kernel oferece SQLite WAL/migrações, JSONL, logging e downloads opcionais. Replay materializa apenas prefixo na PastView, mas mantém referência aos objetos dos eventos; key/available_at são opcionais. TrialRegistry V1 protege novas tentativas e mudanças de veredito por atestado métrica/fingerprint/versão/validade, lock e tmp+replace; TrialRegistryV2 valida proveniência explícita e rejeita trial_id duplicado, porém usa read-modify-write sem o lock/harness V1. Contratos científicos implementam estados e dataset seal, não demonstram edge em dados reais. Testes presentes e inventariados por AST; nenhum resultado de execução inferido. CI local fixa uv 0.12.1 e exige teste/coverage/import-linter/wheel externo. Fontes: pyproject.toml; src/predictor_core/{contracts,data,kernel,measurement,testing}; .github/workflows/ci.yml.



Categorias: OD para código/manifests; ET-SRC para testes. Hashs e leituras no REGISTRO.log e evidencias/core-predictor/hashes.json.



Limitação metodológica: o pedido integral foi exibido incluindo o Anexo A antes deste salvamento. Nenhuma narrativa do repositório foi usada na caracterização acima; a independência absoluta frente ao Anexo A não pode ser afirmada. Confronto documental ainda não realizado.

