Pré-release da Etapa B (auditoria adversarial de 2026-09-28; pedido do dono "publica a rc14 do cain"), publicada a partir do commit do merge do cain#81. As rc12 e rc13 continuam publicadas sem mudança.

## O que entra em relação à rc13

**cain#80, robustez da borda (auditoria adversarial; `qualification/shared/CAIN_EXTREME_20260928/` no predictor-qualification):**
- `ingest`: arquivo de resultado aninhado demais (`RecursionError` do decodificador JSON) ou com `outcome.status` lista/objeto (`TypeError` do validador do protocolo congelado) vira rejeição `SCHEMA_INVALID` gravada em `rejections`; antes derrubava o passo com traceback e nenhum resultado do domínio entrava até o arquivo ser removido.
- `cain research propose|decision-receipt`: proposta aninhada demais é `SCHEMA_INVALID` (exit 2), não traceback.
- `as_of` com a forma certa mas impossível (`2030-13-45T99:00:00Z`) é `AS_OF_INVALID` em `propose`, `decision-receipt` e no modo de proposta do LLM; antes era aceito com a memória vazia, gravado no episódio e emitido na task.
- `_payload`: payload de domínio aninhado demais não produz métricas nem exceção.
- Testes novos em `tests/integration/test_orchestration_robustness.py` (14); fixture `world` num conftest.

**cain#81:** só a versão.

## O que não muda
- `policy.py`: mesmos bytes da rc12/rc13 (sha256 `aff2f5fc…`): o `code_sha256` dos recibos é o mesmo e os vetores N+1 congelados continuam válidos.
- `crypto.json` `28e978e7…`, `stocks.json` `c514a7b0…` e `brasileirao.json` `f51ac735…`: byte a byte iguais aos da rc13.
- `predictor-research-transport` continua pinado na 0.1.0rc6 no `pyproject`/`uv.lock` (a rc7 do transporte é adotada pelas integrações, não pelo cain).

## Build e escopo
- Wheel construída 2× por `git archive` com `SOURCE_DATE_EPOCH=1758240000`, com o mesmo sha256 nas duas (`publish_rc.sh`).
- A wheel mudou, então a C14 vale para as três integrações (fases que exercitam o `cain`).
- É qualificação, não operação: sem modo operacional e sem capital.
