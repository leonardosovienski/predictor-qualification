# Estudo técnico do zero — oito projetos

Estado: PAUSADO A PEDIDO DO USUÁRIO para preservar o limite semanal. Estudo incompleto. A revisão dos executáveis ativos dos oito projetos está registrada; parte do arquivo histórico Crypto e a consolidação final permanecem pendentes. Retomar por [CONTINUIDADE.md](CONTINUIDADE.md).

## Escopo e método

O estudo partiu dos arquivos locais, com inventário preliminar anterior à interpretação. As oito raízes foram identificadas por HEAD, estado Git e hashes dos arquivos. As leituras usam originais; ensaios ocorreram apenas em cópias independentes após pré-verificação. Não houve instalação pesada, execução de serviços ou alteração autorizada das raízes originais. O registro append-only está em `../evidencias/REGISTRO.log`.

OD identifica observação direta; DD declaração documental; ET-SRC implementação ou teste lido; ET-HIST registro de execução anterior; ET-RUN ensaio realizado nesta sessão; EU evidência de uso; INF inferência; NV não verificado. Leitura mecânica e análise AST não equivalem a revisão semântica integral.

## Estado das identidades

Os oito HEADs locais diferem dos oito `main` remotos observados. Portanto versões locais, releases publicadas, clones alternativos e manifests remotos são épocas separadas. A cadeia do Anexo tem assets e manifests remotos verificáveis, mas estes não demonstram integração runtime nem validação econômica. Veja [confronto do Anexo](CONFRONTO_ANEXO_REMOTO.md) e [identidades](IDENTIDADES_PACOTES_CI.md).

A arquitetura observada nas raízes primárias usa contratos V1. No `main` remoto foram observadas dependências Protocol V2 e Transport. Não se infere migração completa do conteúdo do manifest. DECISIONS remoto contém D1–D28 APPROVED, incluindo D16/D27; a ausência destes IDs em arquivo local é delimitada àquela revisão.

## Resultados técnicos preservados

As revisões de fontes próprias ativas, scripts, testes, configurações e CI dos oito projetos foram registradas nas coberturas individuais. Isso ainda requer reconciliação global por arquivo antes de declarar cobertura integral do estudo. Brasileirão Python, seus 124 scripts e .NET estão revisados; .NET não foi executado. Crypto ativo e 169 testes estão revisados, mas há objetos históricos pendentes. A lista exata está em `../evidencias/RETOMADA_PENDENCIAS_EXATAS.json`. Inventários e matrizes consolidados ainda precisam incorporar os últimos suplementos.

Ensaios leves discriminados nos suplementos incluem contratos, smoke e unittests em cópias. A ausência de pytest/jsonschema e metadata instalada limitou algumas verificações; erros foram preservados, sem substituição por PASS. Os verificadores locais Stocks passaram no HEAD local; CI remoto em outro SHA falhou na identidade R8. Contagens históricas dos recibos não são cargas ou suites reexecutadas.

## Leitura dos resultados

- [Matriz de evidências](MATRIZ_EVIDENCIAS.md), também CSV/JSON.
- [Matriz de integrações](MATRIZ_INTEGRACOES.md), também CSV/JSON.
- [Problemas priorizados](PROBLEMAS_PRIORIZADOS.md): prioridade e certeza separadas.
- [Arquitetura geral](docs/ARQUITETURA_GERAL.md), [glossário](docs/GLOSSARIO.md), [guia de leitura](docs/GUIA_DE_LEITURA.md).
- Oito `INVENTARIO_*.md`, oito `docs/COMO_FUNCIONA_*.md` e diagramas `.mmd`.

## Limites econômicos

Não se comprovou capital autorizado, lucro real ou vantagem prospectiva. Hashes, mecanismos PIT, gates, simulações e resultados sintéticos verificam propriedades específicas. Eles não substituem dados de mercado congelados, desenho independente e observação prospectiva. Nenhum veredicto técnico deste estudo autoriza capital.

## Continuidade

[CONTINUIDADE.md](CONTINUIDADE.md) mantém pendências, responsáveis, comandos seguros e publicação. O branch de estudo é independente; nenhuma PR, merge ou alteração de main foi solicitada.
