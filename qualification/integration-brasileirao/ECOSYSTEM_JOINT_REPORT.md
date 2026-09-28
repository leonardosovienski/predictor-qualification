# Teste conjunto do ecossistema — cain 0.4.13rc12

> Gerado por `scripts/ecosystem_joint_report.py` a partir de `RAW_LOGS/runtime/run-20260928T153733Z-eco/ecosystem-joint/SUMMARY.json`.
> Não é gate da integration-brasileirao (QUALIFIED, attestation inalterada). Pedido do dono no chat da sessão cripto;
> lista de conferências combinada com as sessões cripto e STOCKS; rodado no PC 2 (WSL) pelo runtime integrado.

Resultado da tentativa publicada: **57 de 58** conferências.

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
| 13 | 2 | 1 |

Falhas: 13: stocks: 20 races of two consumers on the same spool/ledger/state: no process dies (exit 0, no PermissionError), exactly one experiment and exactly one RESULT per task (an extra non-terminal OPS_FAILED_RETRYABLE of the loser is recorded, not counted as a failure).

## Disputa da trava do Ops (item 13): dois consumidores do mesmo domínio na mesma task

| Domínio | Repetições | 1 experimento | O perdedor publicou | Quedas | Repetições com RECONCILIATION_REQUIRED |
|---|---|---|---|---|---|
| brasileirao | 20 | 20 | OPS_FAILED_RETRYABLE 20 | 0 | — |
| crypto | 20 | 20 | OPS_FAILED_RETRYABLE 20 | 0 | — |
| stocks | 20 | 20 | OPS_FAILED_RETRYABLE 18, RECONCILIATION_REQUIRED 2 | 0 | 4, 12 |

`OPS_FAILED_RETRYABLE` do perdedor não é terminal e não tem efeito. `RECONCILIATION_REQUIRED` falso tem efeito: o
CAIN trava o domínio (R09 DOMAIN_RECONCILIATION_PENDING) até um humano. No stocks isso vem de uma materialização de
referência fora da trava do Ops (achado da sessão STOCKS, confirmado aqui). Fica em aberto para o dono.

LLM (item 10): {"brasileirao": {"exit": 2, "decision": null, "error": "NO_ELIGIBLE_HYPOTHESIS: the policy holds every proposable hy"}, "crypto": {"exit": 0, "decision": "ALLOW", "error": ""}, "stocks": {"exit": 0, "decision": "ALLOW", "error": ""}}

## Arquivos (sha256)
- `SUMMARY.json` `39adaafe13cfe6c5e163d5371a2529ba71149e5b7a0c48d57eeef4deae627002`
- `commands.log` `d30c0a86c3534ddcc3b82068a3b36ef978990f328b0cedf46eb5e10e205a04ec`
- `lock-contention/commands.log` `fba4944d4b43777528697af196a285b9ecb817d798a069b019e843e926ede32b`
- `no_data_rows_check.json` `f0a2ad5d1e3c8362a58b698392643e058723f5af45c93c5c601b5415376fb339`

## Tentativas anteriores (privadas, não publicadas)
- tentativa 1: 47/57, no_data_rows_check não limpo; falso positivo IB-F003 no commands.log da disputa (7 dígitos dentro de um sha256; arquivo mantido privado) e 10 falhas de script: regex do pin Core/Ops (uv exporta '@ url'), freeze via pip inexistente no venv do uv (a checagem 'CAIN sem domínio' passava no vazio), proposal_id repetido na 2ª proposta do brasileirao, item 9 conferido pelo texto do consumidor, janelas jan–abr no brasileirao (o domínio recusa) (sha256 `1adef1eb1bd58b1ada26c2a7a82b2346ef9673ff73c4dcee12178a9f46f1099a`)
- tentativa 2: 56/58; limiar do freeze estrito demais (o venv do CAIN tem 5 pacotes; script) e stocks 2/20 RECONCILIATION_REQUIRED falso (o mesmo achado) (sha256 `9de4a58016bc5ad7d7a32f06f2969207425708b2993b4ba8bb7f45c0e21d5253`)
