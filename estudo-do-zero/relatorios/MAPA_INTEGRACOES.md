# Mapa de integrações e fluxos

Leia [Arquitetura geral](docs/ARQUITETURA_GERAL.md) para os três diagramas e [Matriz](MATRIZ_INTEGRACOES.md) para evidência por aresta. Os oito COMO_FUNCIONA detalham sequência, falhas, estados e persistência.

Não há demonstração de stack V2 ponta a ponta nesta investigação. Os mecanismos encontrados nas fontes primárias são imports Core/Ops, contratos/plugins opcionais, Snapshot/Bundle de arquivos e, em Crypto, protocolo autenticado V1. As raízes alternativas são épocas separadas.

Sobreposições observadas: vários backtests/registros/domínios persistem resultados próprios; Core fornece interfaces e utilidades sem tornar esses algoritmos idênticos. Registries Ecosystem, charters dos domínios e attestations do qualificador têm escopos diferentes; hash alinhado não equivale a decisão econômica atual.

Autenticação/grants, sincronismo, falhas/retries e obrigatoriedade estão nos artefatos integrations.json de cada projeto e reproduzidos na coluna Implementação da matriz; valores secretos não publicados. Links a outras raízes foram registrados em linked-roots.json antes de segui-los.
