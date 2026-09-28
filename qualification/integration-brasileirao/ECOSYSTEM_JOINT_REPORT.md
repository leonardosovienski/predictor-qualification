# Teste conjunto do ecossistema — cain 0.4.13rc12

> Gerado por `scripts/ecosystem_joint_report.py` a partir de `RAW_LOGS/runtime/run-20260928T183300Z-br13/ecosystem-joint/SUMMARY.json`.
> Não é gate da integration-brasileirao (QUALIFIED, attestation inalterada). Pedido do dono no chat da sessão cripto;
> lista de conferências combinada com as sessões cripto e STOCKS; rodado no PC 2 (WSL) pelo runtime integrado.

Resultado da tentativa publicada: **58 de 58** conferências.

| Item | Passaram | Falharam |
|---|---|---|
| 1 | 9 | 0 |
| 2 | 9 | 0 |
| 3 | 6 | 0 |
| 4 | 2 | 0 |
| 5 | 2 | 0 |
| 6 | 1 | 0 |
| 7 | 1 | 0 |
| 8 | 7 | 0 |
| 9 | 4 | 0 |
| 10 | 1 | 0 |
| 11 | 1 | 0 |
| 12 | 12 | 0 |
| 13 | 3 | 0 |

Falhas: nenhuma.

## Disputa da trava do Ops (item 13): dois consumidores do mesmo domínio na mesma task

| Domínio | Repetições | 1 experimento | O perdedor publicou | Quedas | Repetições com RECONCILIATION_REQUIRED |
|---|---|---|---|---|---|
| brasileirao | 20 | 20 | none 20 | 0 | — |
| crypto | 20 | 20 | none 20 | 0 | — |
| stocks | 20 | 20 | none 20 | 0 | — |

`OPS_FAILED_RETRYABLE` do perdedor não é terminal e não tem efeito. `RECONCILIATION_REQUIRED` falso tem efeito: o
CAIN trava o domínio (R09 DOMAIN_RECONCILIATION_PENDING) até um humano. No stocks isso vem de uma materialização de
referência fora da trava do Ops (achado da sessão STOCKS, confirmado aqui). Fica em aberto para o dono.

LLM (item 10): {"brasileirao": {"exit": 2, "decision": null, "error": "NO_ELIGIBLE_HYPOTHESIS: the policy holds every proposable hy"}, "crypto": {"exit": 0, "decision": "ALLOW", "error": ""}, "stocks": {"exit": 0, "decision": "ALLOW", "error": ""}}

## Arquivos (sha256)
- `SUMMARY.json` `964f014d413ed6ed4db246d2ec9e97097776f3014afcf0e10f91a3abcc5e6e5a`
- `commands.log` `338fad3c321399d3f287edf86512540c7a0dd5490277c92f8225e1551d2ed01b`
- `lock-contention/commands.log` `77eb7ee70906ba1a235525fd7a24239bd613935c43f6424e2b4f1be8a270e3b3`
- `no_data_rows_check.json` `f0a2ad5d1e3c8362a58b698392643e058723f5af45c93c5c601b5415376fb339`

## Tentativas anteriores (privadas, não publicadas)
- tentativa 1: 58/58, no_data_rows_check limpo; run anterior na mesma pilha (run-20260928T180538Z-br13), retirado do RAW_LOGS inteiro pelo falso positivo IB-F003 no policy.sha256 do operador (E2E) (sha256 `9788814956577e88defbd71b81022a3ff5d81e20fdde897824378b8d867c118c`)
- tentativa 2: 58/58, no_data_rows_check limpo; execução concorrente com um git stash/pop do agente na árvore de trabalho (commands.log possivelmente incompleto); refeito sozinho (sha256 `18bdf078d4565b5b5bf71d357e289871f560a00ac50693b9ca2b300eaa7b6dc8`)
