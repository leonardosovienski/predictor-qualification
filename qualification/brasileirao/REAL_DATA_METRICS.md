# REAL_DATA_METRICS — missão brasileirao (dado real, Windows local, wheel v0.3.0rc2)

**Diagnóstico, não gate e não autorização de capital (C22).** Nenhum gate do braço mede edge; estas
métricas respondem "o modelo de serving congelado ganha dinheiro?" com o circuito qualificado.

* Dados: cópia do snapshot preservado `matches__20260908T193132732597Z__787a29d9a12e.sqlite3`
  (sha256 da fonte `53fe7350…`, cópia `31f30a4d…`, capturada por `sqlite3.backup` só leitura),
  `as_of` 2026-09-08T19:31:32Z. Não versionado (D-11).
* Modelo: `nbdc-normalized-elo-horizon-v2` com os valores de `config.yaml` do commit (Elo + Binomial
  Negativa com Dixon-Coles, ensemble xG desligado), refit mensal, previsão 60 min antes do kickoff,
  só informação com `available_at < cutoff`. **Nada foi retunado.**
* Temporadas: 2021–2023 (desenvolvimento), 2024 (validação), 2026 (exploratória, até o `as_of`).
  **2025 (holdout selado) nunca foi alvo.**
* Score: RPS (1X2) e Brier (O/U 2.5); Δ = score do modelo − score do baseline (negativo = modelo
  melhor); IC95 por `bootstrap_ci` do Core, cluster por kickoff, 1000 reamostras, seed 13.
* Economia: aposta de 1 u quando `p_modelo × odd − 1 ∈ [0.02, 0.15]`, ao preço de **fechamento**;
  líquido com 2% de slippage sobre o ganho; imposto de 15% sobre o ganho líquido positivo por
  ano-calendário. O resultado econômico é o mesmo nas duas linhas de baseline (depende só do modelo e
  das odds).
* Fonte dos números: `EVIDENCE_NUMBERS.json` → `metrics.real_windows_rc2_04b42c9` (tirado de
  `RAW_LOGS/windows-smoke/rc2/real/result_*.json` por `scripts/evidence_numbers.py`; tabelas por
  `scripts/render_metrics.py`).

| Pedido (temporada-alvo-baseline) | Estado | n | Score modelo | Score baseline | Δ médio [IC95] | Apostas | ROI bruto/aposta [IC95] | ROI líquido/aposta [IC95] | Líquido após imposto (u) |
|---|---|---|---|---|---|---|---|---|---|
| 2021-1X2-climatology | INCONCLUSIVE | 250 | +0.2099 | +0.2139 | -0.0041 [-0.0107, +0.0029] | 121 | -0.0935 [-0.3449, +0.1719] | -0.1058 [-0.3539, +0.1561] | -12.80 |
| 2021-1X2-market | REFUTED | 250 | +0.2099 | +0.1942 | +0.0156 [+0.0063, +0.0249] | 121 | -0.0935 [-0.3449, +0.1719] | -0.1058 [-0.3539, +0.1561] | -12.80 |
| 2021-OU25-climatology | INCONCLUSIVE | 250 | +0.4733 | +0.4767 | -0.0034 [-0.0080, +0.0014] | 82 | +0.0211 [-0.1865, +0.2296] | +0.0116 [-0.1938, +0.2177] | +0.81 |
| 2021-OU25-market | INCONCLUSIVE | 250 | +0.4733 | +0.4609 | +0.0124 [-0.0030, +0.0290] | 82 | +0.0211 [-0.1865, +0.2296] | +0.0116 [-0.1938, +0.2177] | +0.81 |
| 2022-1X2-climatology | NO_EDGE | 380 | +0.2093 | +0.2234 | -0.0140 [-0.0214, -0.0068] | 182 | -0.1905 [-0.3891, +0.0378] | -0.2017 [-0.3973, +0.0235] | -36.70 |
| 2022-1X2-market | INCONCLUSIVE | 380 | +0.2093 | +0.2034 | +0.0060 [-0.0007, +0.0133] | 182 | -0.1905 [-0.3891, +0.0378] | -0.2017 [-0.3973, +0.0235] | -36.70 |
| 2022-OU25-climatology | INCONCLUSIVE | 380 | +0.4898 | +0.4938 | -0.0040 [-0.0093, +0.0006] | 152 | -0.1037 [-0.2527, +0.0437] | -0.1122 [-0.2595, +0.0335] | -17.05 |
| 2022-OU25-market | INCONCLUSIVE | 379 | +0.4891 | +0.4816 | +0.0074 [-0.0059, +0.0207] | 152 | -0.1037 [-0.2527, +0.0437] | -0.1122 [-0.2595, +0.0335] | -17.05 |
| 2023-1X2-climatology | INCONCLUSIVE | 380 | +0.2176 | +0.2243 | -0.0067 [-0.0150, +0.0017] | 180 | -0.1600 [-0.3897, +0.0733] | -0.1717 [-0.3979, +0.0576] | -30.91 |
| 2023-1X2-market | REFUTED | 380 | +0.2176 | +0.2108 | +0.0067 [+0.0017, +0.0120] | 180 | -0.1600 [-0.3897, +0.0733] | -0.1717 [-0.3979, +0.0576] | -30.91 |
| 2023-OU25-climatology | INCONCLUSIVE_DATA_QUALITY | 380 | — | — | — — | — | — — | — — | — |
| 2023-OU25-market | INCONCLUSIVE_DATA_QUALITY | 249 | — | — | — — | — | — — | — — | — |
| 2024-1X2-climatology | NO_EDGE | 380 | +0.2110 | +0.2213 | -0.0103 [-0.0176, -0.0027] | 166 | -0.1490 [-0.3753, +0.0801] | -0.1607 [-0.3838, +0.0650] | -26.68 |
| 2024-1X2-market | REFUTED | 378 | +0.2110 | +0.1983 | +0.0128 [+0.0074, +0.0185] | 166 | -0.1490 [-0.3753, +0.0801] | -0.1607 [-0.3838, +0.0650] | -26.68 |
| 2024-OU25-climatology | INCONCLUSIVE_DATA_QUALITY | 380 | — | — | — — | — | — — | — — | — |
| 2024-OU25-market | INCONCLUSIVE_DATA_QUALITY | 246 | — | — | — — | — | — — | — — | — |
| 2026-1X2-climatology | INCONCLUSIVE | 256 | +0.2096 | +0.2193 | -0.0098 [-0.0213, +0.0016] | 88 | -0.1117 [-0.3636, +0.1735] | -0.1231 [-0.3714, +0.1584] | -10.83 |
| 2026-1X2-market | INCONCLUSIVE | 256 | +0.2096 | +0.2033 | +0.0063 [-0.0008, +0.0141] | 88 | -0.1117 [-0.3636, +0.1735] | -0.1231 [-0.3714, +0.1584] | -10.83 |
| 2026-OU25-climatology | INCONCLUSIVE | 256 | +0.5038 | +0.5035 | +0.0004 [-0.0068, +0.0084] | 110 | -0.0486 [-0.2349, +0.1600] | -0.0586 [-0.2430, +0.1481] | -6.44 |
| 2026-OU25-market | INCONCLUSIVE | 256 | +0.5038 | +0.5039 | -0.0000 [-0.0130, +0.0139] | 110 | -0.0486 [-0.2349, +0.1600] | -0.0586 [-0.2430, +0.1481] | -6.44 |

| Diagnóstico abertura (temporada-alvo) | Apostas na abertura | CLV médio | IC95 (normal iid) | ROI líquido na abertura |
|---|---|---|---|---|
| 2021-1X2-climatology | 130 | -0.0879 | [-0.1146, -0.0612] | +0.0447 |
| 2021-OU25-climatology | 87 | -0.0433 | [-0.0597, -0.0269] | -0.0393 |
| 2022-1X2-climatology | 170 | -0.0838 | [-0.1071, -0.0605] | +0.0308 |
| 2022-OU25-climatology | 139 | -0.0461 | [-0.0593, -0.0329] | -0.0797 |
| 2023-1X2-climatology | 164 | -0.0555 | [-0.0729, -0.0382] | -0.1131 |
| 2023-OU25-climatology | 57 | -0.0182 | [-0.0443, +0.0078] | -0.0612 |
| 2024-1X2-climatology | 157 | -0.0476 | [-0.0681, -0.0272] | -0.1160 |
| 2024-OU25-climatology | 38 | +0.0141 | [-0.0305, +0.0586] | -0.1464 |
| 2026-1X2-climatology | 101 | -0.1006 | [-0.1252, -0.0760] | +0.0095 |
| 2026-OU25-climatology | 90 | +0.0252 | [+0.0023, +0.0481] | -0.1480 |

## Leitura

* **1X2:** o modelo é melhor que a climatologia PIT (significativo em 2022 e 2024; nos demais o IC
  cruza zero) e **pior que o mercado de fechamento** (significativo em 2021, 2023 e 2024). Ao preço
  de fechamento, o ROI líquido por aposta foi negativo em todas as temporadas (−10,6% a −20,2%), com
  o IC cruzando zero no limite superior.
* **O/U 2.5:** sem ganho mensurável contra climatologia ou mercado (todos INCONCLUSIVE); ROI líquido
  entre −11,2% e +1,2% por aposta, IC cruzando zero. 2023 e 2024 ficam `INCONCLUSIVE_DATA_QUALITY`:
  a linha O/U 2.5 de fechamento existe só para 249/380 e 246/380 jogos (regra congelada: >10% sem odds).
* **CLV:** não mensurável no resultado (a base histórica não tem preço pré-jogo com horário). O
  diagnóstico com o preço de abertura (horário desconhecido; viés otimista possível) dá CLV médio
  negativo em todas as temporadas de 1X2 (−4,8% a −10,1%, IC95 abaixo de zero).
* **Conclusão:** não há edge demonstrável no modelo de serving congelado. Estado econômico `NO_EDGE`
  onde avaliado; nenhuma recomendação de aposta sai daqui. `capital_permission = false`.
