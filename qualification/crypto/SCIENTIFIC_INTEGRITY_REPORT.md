# SCIENTIFIC_INTEGRITY_REPORT — missão crypto (§13)

Os números vêm de `EVIDENCE_NUMBERS.json`, gerado por `scripts/evidence_numbers.py` a partir
de `RAW_LOGS/windows-smoke/local/science/SCIENCE_REAL.json` e dos junit dos runtimes. O
runtime é suportado: wheel publicada 1.2.0rc1 `1f76b8c4…` instalada em
`C:\Cripto\qualificacao\runtime\f0923T1540`. Os dados são reais e públicos (Binance
data.vision, BTCUSDT USDⓈ-M, semanal, 2025-09-01 → 2026-08-31), com sha256 da cópia conferido
contra o `.CHECKSUM` publicado (`MANIFEST.json`, fora do repo, D-11). Os limiares estão
congelados em `FROZEN_PARAMETERS.json`.

**Nada aqui é edge, lucro ou autorização de capital.** O experimento é uma sonda de
qualificação (sinal fixo long), e não uma hipótese científica do Cripto (`crypto:H1..H9`
seguem como estão no `charters/scientific_state.json`).

## Integridade temporal (gate `TEMPORAL_INTEGRITY`)

- `tests/test_dpl*.py`, `test_v3_wfa_purge_contract.py`, `test_permutation_placebo_control.py`,
  `test_pbo.py` e `test_gate_power.py` pela wheel instalada no Windows: **120/120**
  (`RAW_LOGS/windows-smoke/local/temporal_suites.junit.xml`). No Linux entram na suíte completa
  pela wheel: 1647 passed, e nenhuma das 17 falhas é desses arquivos (CR-F016).
- No circuito, o `replay` do Core impõe `observed_at ≤ available_at ≤ data_cutoff` e a ordem
  temporal **antes** de qualquer estatística. O sinal só recebe `PastView`.

## Future canary (gate `FUTURE_CANARY`)

- Sintético (conformidade, Linux, windows-latest e Windows): o pedido com o canário
  `FUTURE_CANARY_CRYPTO_001` falha com `TEMPORAL_INTEGRITY_VIOLATION` (`LookaheadError`), sem
  efeito, sem trial e sem resultado. Um pedido legítimo não carrega o token nem o valor do
  canário em efeito, trial, resultado, `results.sqlite` ou outcomes.
- Real (Windows): as linhas de 07, 14 e 21/set/2026 falham na linha 52 com `LookaheadError`.
  Vazamentos nos artefatos dos pedidos legítimos: **0**.

## Métricas econômicas (gate `CRYPTO_ECONOMIC_METRICS`)

Pedido real `crypto:REQ-REAL-E2E-001`, 52 observações. Custos congelados: `CostModel` V3,
10 + 5 bps por perna, 2 pernas, funding vigente.

| | Média (bps/semana) | IC 95% bootstrap (iid, 500, seed 17) |
|---|---|---|
| bruto | −45 | [−214, 112] |
| líquido | −83 | [−253, 76] |

- Custo médio total: 38 bps (30 de fricção de round-trip + 8 de funding).
- Decisão do gate econômico: `NO_TRADE`. Estado científico (Core): `INCONCLUSIVE`.
  Econômico: `NO_EDGE`.
- **Gate `NOT_RUN` — BLOCKED: D-16 pendente.** A regra congelada exige dados reais no Linux
  primário. As métricas acima são do Windows (secundário) e servem de evidência adicional.

## Controles negativos (gate `CRYPTO_NEGATIVE_CONTROLS`)

| Controle | Resultado esperado (congelado) | Observado |
|---|---|---|
| injeção de futuro | 0 resultados aceitos | 0 (`TEMPORAL_INTEGRITY_VIOLATION`) |
| ablação temporal (ordem trocada; disponível antes de observado) | 0 resultados aceitos | 0 e 0 |
| labels embaralhados (100 seeds) | `SUPPORTED` em ≤ 10 | **3** (`INCONCLUSIVE` 94, `REFUTED` 3) |

**Gate `NOT_RUN` — BLOCKED: D-16 pendente** (mesma regra). Resultado no Windows: todos dentro
dos limiares.

## Correção científica feita nesta missão

CR-F004: o handler reportava o líquido com uma perna e sem funding. Com bruto de +15 bps, o
líquido aparecia como 0 bps, quando o `CostModel` congelado dá −36 bps. E não havia IC do
líquido. O resultado econômico estava errado a favor do edge. Foi corrigido (`33fed6b`), com
regressão em `test_net_return_uses_the_frozen_cost_model_and_has_its_own_interval`.

## V1.1 (cripto 1.2.0rc2 + Ops 4.2.2rc1)

Refeito no runtime Windows (`RAW_LOGS/v1.1/windows-local/`): suítes temporais 120/120; canário e ablações falham fechado (0 aceitos); placebo SUPPORTED 3/100; métricas reais idênticas (bruto −45, líquido −83 bps; mesmos ICs). Gates econômico, controles negativos e casos desconfortáveis seguem **NOT_RUN — BLOCKED: D-16 pendente**.
