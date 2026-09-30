# Estudo técnico do zero — oito projetos

Estado: CONCLUÍDO DENTRO DOS LIMITES DECLARADOS (retomada de 2026-09-30, em Linux). A revisão dos executáveis ativos dos oito projetos e do arquivo histórico Crypto está registrada e reconciliada nas coberturas; o residual exato está em [PROBLEMAS_PRIORIZADOS](PROBLEMAS_PRIORIZADOS.md) (`G-COBERTURA-RESIDUAL`). A preservação byte a byte dos originais Windows não pôde ser repetida nesta retomada (sem acesso às raízes locais); a última verificação registrada é a do checkpoint anterior. Histórico da retomada em [CONTINUIDADE.md](CONTINUIDADE.md). Na mesma sessão foi aberta uma **segunda época**, o `main` remoto de 2026-09-30 ([linha de base da época main](LINHA_DE_BASE_EPOCA_MAIN.md), [suplemento](SUPLEMENTO_EPOCA_MAIN_20260930.md), [cobertura por projeto](COBERTURA_POR_PROJETO.md)): baseline e delta inventariados por arquivo, verificadores do Anexo A6 executados onde o container permite, wheels publicadas confrontadas com README/METADATA e com wheels construídas do `main`, attestations da qualificação checadas na emissão e no `main`; revisão semântica só nos deltas pequenos (ops, core, ecosystem V2/transport) e nos adapters/contratos V2 dos domínios. As duas épocas nunca se misturam: toda conclusão cita o SHA.

Estado: PAUSADO A PEDIDO DO USUÁRIO para preservar o limite semanal. Estudo incompleto. A revisão dos executáveis ativos dos oito projetos está registrada; parte do arquivo histórico Crypto e a consolidação final permanecem pendentes. Retomar por [CONTINUIDADE.md](CONTINUIDADE.md).

## Escopo e método

O estudo partiu dos arquivos locais, com inventário preliminar anterior à interpretação. As oito raízes foram identificadas por HEAD, estado Git e hashes dos arquivos. As leituras usam originais; ensaios ocorreram apenas em cópias independentes após pré-verificação. Não houve instalação pesada, execução de serviços ou alteração autorizada das raízes originais. O registro append-only está em `../evidencias/REGISTRO.log`.

OD identifica observação direta; DD declaração documental; ET-SRC implementação ou teste lido; ET-HIST registro de execução anterior; ET-RUN ensaio realizado nesta sessão; EU evidência de uso; INF inferência; NV não verificado. Leitura mecânica e análise AST não equivalem a revisão semântica integral.

## Estado das identidades

Os oito HEADs locais diferem dos oito `main` remotos observados; na época `main` (2026-09-30) verificou-se que cada HEAD local é ancestral direto do `main` atual, com deltas de 10 (core) a 5.763 (qualificação) arquivos. Portanto versões locais, releases publicadas, clones alternativos e manifests remotos são épocas separadas. A cadeia do Anexo tem assets e manifests remotos verificáveis, mas estes não demonstram integração runtime nem validação econômica. Veja [confronto do Anexo](CONFRONTO_ANEXO_REMOTO.md) e [identidades](IDENTIDADES_PACOTES_CI.md).

A arquitetura observada nas raízes primárias usa contratos V1. No `main` remoto foram observadas dependências Protocol V2 e Transport. Não se infere migração completa do conteúdo do manifest. DECISIONS remoto contém D1–D28 APPROVED, incluindo D16/D27; a ausência destes IDs em arquivo local é delimitada àquela revisão.

## Resultados técnicos preservados

As revisões de fontes próprias ativas, scripts, testes, configurações e CI dos oito projetos foram registradas nas coberturas individuais e, na retomada, reconciliadas por caminho e hash em `evidencias/<projeto>/coverage.json` (Crypto e Brasileirão) — as marcações só ocorreram onde existe nota semântica registrada. Brasileirão Python, seus 124 scripts, 210 testes e .NET estão revisados e reconciliados em coverage.json; .NET não foi executado; 26 arquivos residuais foram lidos no clone do remoto com hash idêntico à linha de base e 16 (configuração/contratos/lock) permanecem não certificados por divergirem do remoto ([suplemento](SUPLEMENTO_BRASIL_RESIDUAL_RETOMADA.md)). Crypto ativo (440 arquivos) e o arquivo histórico completo (773 objetos em quatro partições) estão revisados sem execução ([suplemento](SUPLEMENTO_CRIPTO_HISTORICO_RETOMADA.md)); `../evidencias/RETOMADA_PENDENCIAS_EXATAS.json` registra 0 pendentes. Stocks: `research/` (301 arquivos históricos separados), `vendor/` e protótipos OSS ficaram catalogados sem leitura semântica, por decisão de escopo do inventário.

Ensaios leves discriminados nos suplementos incluem contratos, smoke e unittests em cópias. A ausência de pytest/jsonschema e metadata instalada limitou algumas verificações; erros foram preservados, sem substituição por PASS. Os verificadores locais Stocks passaram no HEAD local; CI remoto em outro SHA falhou na identidade R8. Contagens históricas dos recibos não são cargas ou suites reexecutadas.

## Leitura dos resultados

- [Matriz de evidências](MATRIZ_EVIDENCIAS.md), também CSV/JSON.
- [Matriz de integrações](MATRIZ_INTEGRACOES.md), também CSV/JSON.
- [Problemas priorizados](PROBLEMAS_PRIORIZADOS.md): prioridade e certeza separadas.
- [Arquitetura geral](docs/ARQUITETURA_GERAL.md), [glossário](docs/GLOSSARIO.md), [guia de leitura](docs/GUIA_DE_LEITURA.md).
- Oito `INVENTARIO_*.md`, oito `docs/COMO_FUNCIONA_*.md` e 27 diagramas `.mmd` (índice no [guia de leitura](docs/GUIA_DE_LEITURA.md)).
- Suplementos da retomada: [Crypto histórico](SUPLEMENTO_CRIPTO_HISTORICO_RETOMADA.md) e [Brasil residual](SUPLEMENTO_BRASIL_RESIDUAL_RETOMADA.md).
- Época `main` (2026-09-30): [linha de base](LINHA_DE_BASE_EPOCA_MAIN.md), [suplemento](SUPLEMENTO_EPOCA_MAIN_20260930.md) (confronto A3/A4, verificadores A6, wheels, attestations, revisão dos deltas pequenos, inventário dos grandes), [cobertura por projeto](COBERTURA_POR_PROJETO.md) em cinco categorias. Achados novos `EPOCA-*` (2 P1: attestations não reproduzíveis no `main` da qualificação; lacre R8 do Stocks quebrado por três arquivos).

## Limites econômicos

Não se comprovou capital autorizado, lucro real ou vantagem prospectiva. Hashes, mecanismos PIT, gates, simulações e resultados sintéticos verificam propriedades específicas. Eles não substituem dados de mercado congelados, desenho independente e observação prospectiva. Nenhum veredicto técnico deste estudo autoriza capital.

## Continuidade

[CONTINUIDADE.md](CONTINUIDADE.md) mantém o histórico da pausa, o que a retomada fechou, o residual e a publicação. O branch de estudo é independente; nenhuma PR, merge ou alteração de main foi solicitada.
