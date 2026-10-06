# Revisão semântica dos testes Crypto — bloco 04

Leitura integral de fixtures, mocks e assertions; nenhuma execução. Os cenários demonstram contratos sintéticos ou reconciliação de artefatos, sem estabelecer lucro futuro, autorização ou execução real.

## tests/test_config_news_providers.py

Settings com envfake rejeita newsproviders desconhecido/duplicado, aceita newsapi_ai/mediastack/google_news_rss; fallbackserpapi fora da lista e tetoAPIguardnegativo inválido. Não chama provedores nem grava credenciais.

## tests/test_config_secrets_resolution.py

Initkwargs resolvidas aceitas sem os.environ, chave vazia/placeholderchangeme rejeitada; modo multi exige todas chaves resolvidas e aceita stringsfake longas. Valida presença/formato, não autenticidade de key.

## tests/test_continuity_recovery.py

Importa restore_archives físico docscontinuity; ZIPs temporários demonstram preflight sem escrita para estadosSQLite/WAL/SHM/journal/env, traversal/backslash/drive/reservednames/ambiguousWindows, collision case-insensitive e parentfile. Hashmember tampered/existingfiledif recusados e duplicate content existente igual permitido. Teste manifesto arquivos publicados verifica hashes físicos e count, sem enviar remoto. Não executado aqui.

## tests/test_core_integrity.py

Metadata importada exige core3.2.1/ops4.2.1 site-packages semvendor/packages, uv.lock URLs/hashes exatos e ausência cópias; única subpackage research-export nome correto. Não baixa wheels nem autentica remote; depende instalação disponível.

## tests/test_dependency_execution_manifest.py

Manifesto dependency_execution físico não-vazio, cada caminho confinado e bytesSHA preservados. Não reproduz execução documentada nem valida significado de logs.

## tests/test_diagnose_h6_mechanism_pit.py

SQLite sintético PIT: rawfeature published depois prediction descartada, feature passada disponível mantida com outcome futuro, normaliza ativo uppercase e calcula past25%/future10%. Não comprova proveniência/qualidade preços.

## tests/test_discovery.py

Rank fixtures verificam momentum7d dominante/24hdesempate, limite3, heurística stable por símbolo/preço/variação, wrapped/lower volume excluídos e trendingbonus não topo automático; missingcampos tolerados e missingid excluído. Não pesquisa universo real nem demonstra alpha.

## tests/test_distribution_security.py

Inspeção física dist requer sdist/wheel previamente construídos, semskip: sdist inclui buildsrc/charters/plans e exclui archives/db/env; wheel semruntime/log/db/jsonl e regexsecrets para extensões específicas. Documento incidente exige estadosBLOCKED/ROTATED-confirmed-owner e frasesaçãohumana/abuso. Regex/texto não comprova ausência universal de segredos nem rotação real.

## tests/test_divergence.py

Direções technical/LLM em fixtures, RSIoverbought neutraliza weaktrend, divergência contraditória1/alinhada0/missing0. calculate_final_score preserva88 sem penalizar divergência. Sem acurácia/modelo real.

## tests/test_dpl.py

MarketDataPoint imutável, high<low e published<timestamp rejeitados. Fakeproviders routing primary evita secondary, primaryfail secondary uma vez, allfail DataUnavailable com eventos; routerempty inválido, domínio telemetria injetado stocks preservado, facade latest_close42 delega e default sourcesbinance/coingecko configurados. Teste genérico usa símboloPETR4 mas não integraçãoStocks real; nenhum HTTP.