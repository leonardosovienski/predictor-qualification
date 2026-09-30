# Estudo técnico do zero — oito projetos

Estado: EM EXECUÇÃO. A análise integral de Cripto e Brasileirão continua; este documento preserva o estado e não declara conclusão global.

## Escopo e método

O estudo partiu dos arquivos locais, com inventário preliminar anterior à interpretação. As oito raízes foram identificadas por HEAD, estado Git e hashes dos arquivos. As leituras usam originais; ensaios ocorreram apenas em cópias independentes após pré-verificação. Não houve instalação pesada, execução de serviços ou alteração autorizada das raízes originais. O registro append-only está em `../evidencias/REGISTRO.log`.

OD identifica observação direta; DD declaração documental; ET-SRC implementação ou teste lido; ET-HIST registro de execução anterior; ET-RUN ensaio realizado nesta sessão; EU evidência de uso; INF inferência; NV não verificado. Leitura mecânica e análise AST não equivalem a revisão semântica integral.

## Estado das identidades

Os oito HEADs locais diferem dos oito `main` remotos observados. Portanto versões locais, releases publicadas, clones alternativos e manifests remotos são épocas separadas. A cadeia do Anexo tem assets e manifests remotos verificáveis, mas estes não demonstram integração runtime nem validação econômica. Veja [confronto do Anexo](CONFRONTO_ANEXO_REMOTO.md) e [identidades](IDENTIDADES_PACOTES_CI.md).

A arquitetura observada nas raízes primárias usa contratos V1. No `main` remoto foram observadas dependências Protocol V2 e Transport. Não se infere migração completa do conteúdo do manifest. DECISIONS remoto contém D1–D28 APPROVED, incluindo D16/D27; a ausência destes IDs em arquivo local é delimitada àquela revisão.

## Resultados técnicos preservados

CAIN e Stocks têm cobertura semântica dos executáveis próprios encerrada. Core, Ops, Ecosystem e Qualification possuem inventários e estudos técnicos; os suplementos discriminam fontes, ensaios e limites. Brasileirão .NET está revisado sem execução. Python, scripts e testes de Cripto/Brasileirão ainda têm trabalho pendente explícito nas coberturas.

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
