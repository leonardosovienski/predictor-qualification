# Continuidade — revisão histórica Crypto, partição1

Interrompida por solicitação do usuário transmitida pelo root: salvar ponto de retomada e encerrar com5% semanal restante. Não realizar novas leituras nesta sessão.

153 dos193 objetos efetivamente revisados e persistidos em shared-archive-1-notes.json e shared-archive-1-coverage.json. Índices **40 a192 inclusive completos**, por leitura integral de todas diferenças frente às bases atuais já revisadas, ou corpo integral quando sem base. Trechos truncados foram relidos em chamadas menores antes marcar cobertura. Nenhum original executado.

**Pendentes exatos: índices0 a39 inclusive (40 objetos)** de archive-derivation-assignment-1.json. Nenhum desses40 foi marcado como revisado. Apenas nomes/índice foram inventariados; não houve leitura semântica de seus corpos/diffs nesta partição.

Retomar com scripts/archive_display.py1 0 1 para o primeiro objeto (959 linhas modificadas), dividir impressão se necessário. Demais objetos1..39 incluem integration-audit validate, corpos sem base e versões antigas de backtest/harness/feature-store/collectors/contracts. O índice assignment1 é a fonte autoritativa dos caminhos.

Persistência: scripts/shared_archive_record.py; scripts/shared_archive_notes_tail.py e shared_archive_notes_mid1.py..mid7.py contêm notas manuais já salvas. Stem exclusivo shared-archive-1; não editar coberturas de outros agentes.

Os objetos são **históricos**, separados da implementação atual. Não transformar ausência de guards nas versões antigas em achado presente. Cobertura atual principal e respectivos testes foram entregues anteriormente. Achados históricos anotados incluem publicação macro inferida por lag, budget reset que apagava SQLite, redaction incompleta, cache sem TTL, validação permissiva de contratos e pipeline fit de toda série descrito causal. Bases atuais adicionaram diversas proteções.

Também concluídos antes da pausa: Brasil testes042–059 (107 arquivos), Brasil scripts14–20 (35 arquivos), Crypto169 testes atuais, CAIN testes próprios/untracked, .NET Brasil e Core/Ops/Eco. Cada conjunto possui cobertura/notas próprias já comunicadas ao root.
