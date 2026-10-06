# Caracterização preliminar — ecosystem-predictor



Base local: `C:\CAIN\contrato`; HEAD `a879525c49f1b3ac2050a3a70b10a322501b1e56`.



Distribuição ecosystem-predictor 0.2.0 >=3.13,<3.15 com Pydantic; src/ecosystem.__version__ literal 0.1.0. Contratos PluginV1 e registry descobrem predictor.plugins, carregam health/capabilities e degradam falhas; diagnóstico preserva namespace/status nativo sem traduzir significado nem autorizar capital. Há três subpacotes rastreados: snapshot (ResearchSnapshotV1), bundle (ResearchBundleV1 com perfis local-research/1 e /2) e protocol (ResearchTaskV1/ResearchResultV1/AuthenticatedEnvelopeV1 HMAC). Protocolo local restringe tarefas a crypto/BACKTEST_EXISTING_HYPOTHESIS e parâmetros inteiros limitados; JSON canônico NFC e HMAC >=32 bytes. HmacKeyStore guarda metadata.sqlite e vault de arquivos ACL, suporta rotação/revogação/backup. Bundle representa entidades, evidências, artefatos recebidos/referências e relações; publicação exige fontes admitidas por hash e não altera produtor. Snapshot publica por staging/link e conflito/idempotência. CI inclui plugins reais/released wheels e auditorias de registries. Não se encontrou pacote transporte ou compat/ no inventário rastreado; busca estrutural restante pendente. Não há CLI project.scripts no manifest raiz. Fontes: pyproject.toml; src/ecosystem; packages/*/src; CI; locks. Nenhum serviço central foi executado.



Categorias: OD para código/manifests; ET-SRC para testes. Hashs e leituras no REGISTRO.log e evidencias/ecosystem-predictor/hashes.json.



Limitação metodológica: o pedido integral foi exibido incluindo o Anexo A antes deste salvamento. Nenhuma narrativa do repositório foi usada na caracterização acima; a independência absoluta frente ao Anexo A não pode ser afirmada. Confronto documental ainda não realizado.

