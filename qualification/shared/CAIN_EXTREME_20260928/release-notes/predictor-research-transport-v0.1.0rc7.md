Pré-release da Etapa B (auditoria adversarial de 2026-09-28; pedido do dono "publica a rc7 do transporte"). Muda uma coisa: **um arquivo de task ilegível nunca derruba a passada do consumidor**.

- `Consumer._load` trata `RecursionError` (aninhamento absurdo no decodificador JSON) e `TypeError` (valor não hasheável onde o protocolo congelado espera texto) como qualquer envelope malformado: rejeição `SCHEMA_INVALID` publicada em `rejected/` e gravada no ledger; a passada segue para as outras tasks.
- Antes, um arquivo com 100 000 níveis de aninhamento matava `run_once()` inteiro com traceback, e nenhuma task do domínio era entregue até o arquivo ser removido. As 433 mutações de campo único de uma task válida já eram todas rejeitadas sem chamar o domínio.
- Teste novo: arquivo aninhado demais ao lado de uma task válida → 1 rejeição, 1 entrega; passada seguinte `skipped`×2.

`research-protocol` não muda (2.0.0rc2); a allowlist de adapters e a trava por domínio são as mesmas da rc6. Nenhum domínio muda.

Base: PR ecosystem-predictor#38 (`8ce2a64`), merge `21ae791`; tag no `main` `f0cc041` (merge do #39, só registro), com o CI do push verde nas 21 conferências.

Build reprodutível: git archive, SOURCE_DATE_EPOCH=1758240000, duas vezes, mesmos bytes (`d3dfbff4…`). Evidência da auditoria: `qualification/shared/CAIN_EXTREME_20260928/` no predictor-qualification.

Adotar esta release nas integrações da Etapa B dispara a C14 (fases que exercitam o transporte) nas três.
