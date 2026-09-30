# Caracterização preliminar — predictor-ops



Base local: `C:\PREDICTORS\predictor-ops`; HEAD `b19e69527c0fda5cb1f96281d3a984fea1431768`.



Pacote Python predictor-ops 4.2.1 >=3.13, Pydantic/pydantic-settings, CLI run/validate/provenance. JobConfig determina command argv, cwd, ambiente, timeout, heartbeat, truncamento de saída e runtime root. Runner adquire lock por identidade econômica (ou id), observa idempotency, kill switch e proveniência, inicia subprocesso e persiste heartbeat/events/idempotency. Windows cria processo suspenso e Job Object antes de resumir; POSIX usa process group. Schema permite EXECUTION somente com capital_permission=true e snapshot de risco completo/atual/limites; isso não fornece broker nem prova autorização humana. Scientific state é string opaca. retry_action é recomendação determinística por OrderState; retry_count é metadado. Backend implementado local, agendamento Windows é adapter somente inspeção de tarefas. Docker e CI declarados. Fonte implementa execução genérica arbitrária autorizada por configuração, não motor econômico de domínio. Testes presentes/AST não equivalem execução. Fontes: pyproject.toml; src/predictor_ops; tests_v2; workflows; Dockerfile.



Categorias: OD para código/manifests; ET-SRC para testes. Hashs e leituras no REGISTRO.log e evidencias/predictor-ops/hashes.json.



Limitação metodológica: o pedido integral foi exibido incluindo o Anexo A antes deste salvamento. Nenhuma narrativa do repositório foi usada na caracterização acima; a independência absoluta frente ao Anexo A não pode ser afirmada. Confronto documental ainda não realizado.

