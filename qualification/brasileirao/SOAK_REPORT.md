# SOAK_REPORT — missão brasileirao (gate `SOAK`, C10)

**Estado do gate: `NOT_RUN` — BLOCKED: D-16 pendente.** Pela regra congelada
(`FROZEN_PARAMETERS.json` → `d16_dependency_rule`), o SOAK só vira PASS com **dados reais no Linux
primário**; a D-16 (dados reais no Linux/Actions) não está decidida no `main`. O dataset real do
Brasileirão não pode ir para o Actions público sem essa decisão (D-11: sem direito de redistribuição
estabelecido).

## Diagnóstico com vetores sintéticos (Linux primário, runtime suportado)

Perfil congelado antes: `QUALIFICATION_PROFILE_BR_V1.json` (20 ciclos normais, 5 restarts, 5
duplicatas, 3 por classe de falha relevante — crash do worker, timeout do Ops, morte antes do commit
da admission, morte durante a gravação do resultado —, 5 ciclos de mesmo kickoff, 5 com dataset fora
de ordem, 5 com canário). Driver `scripts/soak.py`, cada chamada um processo novo do
`brasileirao-research` instalado da wheel v0.3.0rc2.

Números de `EVIDENCE_NUMBERS.json` → `soak.linux_synthetic_rc2` (tirados de
`RAW_LOGS/cleanroom-final/run35963501898/brasileirao-runtime-linux-primary/soak.jsonl`):

| Medida | Valor |
|---|---|
| chamadas de processo | 71 (54 sem falha injetada; 4 `before_admission_commit`, 4 `during_result_write`, 3 `ops_worker_crash`, 3 `ops_worker_hang`, e os pontos de restart) |
| pedidos com resultado | 49; resultados guardados 49 |
| perdidos / inesperados | 0 / 0 |
| efeitos de domínio | 49 (= resultados) |
| SUCCEEDED do Ops por job (máximo) | 1 |
| releitura ≠ blob autoritativo | 0 |
| `reconcile` | exit 0, sem achados |
| violações (duplicata, restart, falha, mesmo kickoff, permutação, canário, autoridade/IDs) | 0 |
| veredito de tolerância zero | `true` |

Diagnóstico adicional com **dado real** no Windows local (não é o ambiente do gate): 20 pedidos
reais + E2E real 25/25 + corroboração temporal (`TEMPORAL_INTEGRITY_REPORT.md` §4), sem violação.

## Para fechar (depois da D-16)

Rodar `scripts/soak.py` no Linux primário com o dataset real capturado no host (sha256 conferido
contra `FROZEN_PARAMETERS.json` → `windows_local_real_data.source_sha256`), sem mudar perfil nem vetores.
