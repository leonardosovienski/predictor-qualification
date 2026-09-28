Pré-release da Etapa B (missão `integration-stocks`, decisão do dono "Só o transporte"). Muda uma coisa: **um consumidor por domínio por vez**.

- Cada passada de `Consumer.run_once()` segura uma trava exclusiva e sem espera em `<spool>/<domínio>/.consumer.lock`. No POSIX a trava é `flock`; no Windows, `msvcrt.locking`.
- Um segundo consumidor do mesmo domínio levanta `ConsumerBusy` (código `CONSUMER_BUSY`) antes de ler o ledger. Ele não chama o domínio e não publica nada.
- Nesse caso a CLI sai com código 6 e escreve uma linha `{"action": "busy", "code": "CONSUMER_BUSY", "domain": …}`.
- O sistema solta a trava quando a passada termina ou quando o processo morre. O próximo consumidor retoma a task interrompida.
- Harnesses que rodam dois consumidores do mesmo domínio precisam aceitar o exit 6.

Motivo: nos testes de disputa da Etapa B (IC-F016, IC-F017, IS-F009), o consumidor perdedor chegava ao domínio. Ele publicava um `OPS_FAILED_RETRYABLE` ou um `RECONCILIATION_REQUIRED` falso, e no Windows podia morrer num arquivo somente leitura.

Resultado da disputa na branch: stocks 20/20 com 0 envelopes falsos; Brasileirão 20/20 com exits [0, 6], F16/F08 com retomada ok.

`research-protocol` não muda (2.0.0rc2), e a allowlist de adapters é a mesma da rc5.

Base: PR ecosystem-predictor#36 (`dae4e57`), merge `bac1f7b` no main. O CI do push no main passou.

Build reprodutível: git archive, SOURCE_DATE_EPOCH=1758240000, duas vezes, mesmos bytes.
