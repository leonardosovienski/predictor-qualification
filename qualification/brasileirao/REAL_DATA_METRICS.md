# REAL_DATA_METRICS — missão brasileirao (dado real; rc2 no Windows local e no Linux do PC 2; rc3 vigente)

**Diagnóstico, não gate e não autorização de capital (C22).** Nenhum gate do braço mede edge; estas
métricas respondem "o modelo de serving congelado ganha dinheiro?" com o circuito qualificado.

> **BR-F018 corrigido na rc3 (requalificação, 2026-09-24):** as tabelas "Linux do PC 2" e as de cima (Windows local, rc2)
> mostram o defeito: mesmos pedidos, mesma wheel, mesmo snapshot, números diferentes entre SOs. Com a **rc3** (`25cdf4d`,
> `403e6a02…`; ajuste do modelo de gols com gradiente analítico, mesmo modelo) o resultado é **idêntico** no Linux e no Windows
> do PC 2 (20/20, nenhuma diferença; `RAW_LOGS/c14-rc3-20260924/crossos-real/`). **Os números vigentes são os da seção
> "rc3" no fim deste arquivo.** Nenhum estado mudou da rc2 para a rc3; a conclusão (`NO_EDGE`, sem edge demonstrável) vale.

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

### Leitura (rc3, vigente)

Das duas tabelas da rc3, acima.

* **1X2:** melhor que a climatologia PIT (significativo em 2022 e 2024; nos demais o IC cruza zero) e **pior que o
  mercado de fechamento** (significativo em 2021, 2023 e 2024), como na rc2. Ao preço de fechamento, o ROI líquido por
  aposta foi negativo em todas as temporadas (−10,6% a −23,2%). Em 2022 o IC95 fica **inteiro abaixo de zero**
  ([−43,0%, −1,8%]), então a perda é significativa. Nas demais temporadas o IC cruza zero no limite superior.
* **O/U 2.5:** sem ganho mensurável contra climatologia ou mercado (todos `INCONCLUSIVE`); ROI líquido entre −12,2% e
  +1,2% por aposta, IC cruzando zero. 2023 e 2024 continuam `INCONCLUSIVE_DATA_QUALITY` (249/380 e 246/380 jogos com
  a linha de fechamento).
* **CLV (diagnóstico com o preço de abertura):** médio negativo em todas as temporadas de 1X2 (−4,9% a −10,0%, IC95
  abaixo de zero).
* **Conclusão:** não há edge demonstrável no modelo de serving congelado; `NO_EDGE` onde avaliado; nenhuma
  recomendação de aposta sai daqui; `capital_permission = false`. Nenhum estado mudou da rc2 para a rc3; mudaram
  números (ex.: nº de apostas em 2022–2026), e o de 2022 no 1X2 ficou pior.

## Leitura (rc2, Windows local — histórico; a leitura vigente é a da rc3, no fim do arquivo)

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

## Linux do PC 2 (D-16, 2026-09-24) — mesmos pedidos, mesma wheel, mesmo snapshot

Evidência bruta (na época, a D-9 ainda não admitia o PC 2 como Linux primário; hoje admite, D-19). Fonte:
`RAW_LOGS/d16-pc2-20260924/d16/evidence_numbers_pc2.json` → `metrics.pc2_real` (tirado dos resultados
`show` do PC 2, que carregam o dado e ficam só no PC 2 — sha256 em `d16/private_manifest.sha256` — por
`scripts/evidence_numbers.py`; tabela por `scripts/render_metrics.py`, cópia em
`d16/real_metrics_pc2_table.md`). Comparação campo a campo com o Windows:
`d16/compare_real_windows_pc2.json` (métricas iguais em 4/20; estados iguais em 20/20).

| Pedido (temporada-alvo-baseline) | Estado | n | Score modelo | Score baseline | Δ médio [IC95] | Apostas | ROI bruto/aposta [IC95] | ROI líquido/aposta [IC95] | Líquido após imposto (u) |
|---|---|---|---|---|---|---|---|---|---|
| 2021-1X2-climatology | INCONCLUSIVE | 250 | +0.2097 | +0.2139 | -0.0043 [-0.0109, +0.0027] | 121 | -0.0935 [-0.3449, +0.1719] | -0.1058 [-0.3539, +0.1561] | -12.80 |
| 2021-1X2-market | REFUTED | 250 | +0.2097 | +0.1942 | +0.0154 [+0.0061, +0.0247] | 121 | -0.0935 [-0.3449, +0.1719] | -0.1058 [-0.3539, +0.1561] | -12.80 |
| 2021-OU25-climatology | INCONCLUSIVE | 250 | +0.4732 | +0.4767 | -0.0035 [-0.0082, +0.0014] | 83 | +0.0088 [-0.1886, +0.2151] | -0.0005 [-0.1960, +0.2034] | -0.05 |
| 2021-OU25-market | INCONCLUSIVE | 250 | +0.4732 | +0.4609 | +0.0123 [-0.0031, +0.0289] | 83 | +0.0088 [-0.1886, +0.2151] | -0.0005 [-0.1960, +0.2034] | -0.05 |
| 2022-1X2-climatology | NO_EDGE | 380 | +0.2094 | +0.2234 | -0.0140 [-0.0213, -0.0068] | 177 | -0.2154 [-0.4198, -0.0108] | -0.2262 [-0.4277, -0.0242] | -40.04 |
| 2022-1X2-market | INCONCLUSIVE | 380 | +0.2094 | +0.2034 | +0.0060 [-0.0006, +0.0133] | 177 | -0.2154 [-0.4198, -0.0108] | -0.2262 [-0.4277, -0.0242] | -40.04 |
| 2022-OU25-climatology | INCONCLUSIVE | 380 | +0.4896 | +0.4938 | -0.0043 [-0.0093, +0.0004] | 151 | -0.1365 [-0.2917, +0.0061] | -0.1447 [-0.2982, -0.0034] | -21.84 |
| 2022-OU25-market | INCONCLUSIVE | 379 | +0.4888 | +0.4816 | +0.0072 [-0.0062, +0.0204] | 151 | -0.1365 [-0.2917, +0.0061] | -0.1447 [-0.2982, -0.0034] | -21.84 |
| 2023-1X2-climatology | INCONCLUSIVE | 380 | +0.2176 | +0.2243 | -0.0067 [-0.0150, +0.0018] | 176 | -0.1614 [-0.4016, +0.0927] | -0.1731 [-0.4093, +0.0772] | -30.46 |
| 2023-1X2-market | REFUTED | 380 | +0.2176 | +0.2108 | +0.0068 [+0.0017, +0.0121] | 176 | -0.1614 [-0.4016, +0.0927] | -0.1731 [-0.4093, +0.0772] | -30.46 |
| 2023-OU25-climatology | INCONCLUSIVE_DATA_QUALITY | 380 | — | — | — — | — | — — | — — | — |
| 2023-OU25-market | INCONCLUSIVE_DATA_QUALITY | 249 | — | — | — — | — | — — | — — | — |
| 2024-1X2-climatology | NO_EDGE | 380 | +0.2110 | +0.2213 | -0.0103 [-0.0175, -0.0027] | 167 | -0.1403 [-0.3598, +0.0962] | -0.1521 [-0.3684, +0.0813] | -25.41 |
| 2024-1X2-market | REFUTED | 378 | +0.2111 | +0.1983 | +0.0128 [+0.0074, +0.0185] | 167 | -0.1403 [-0.3598, +0.0962] | -0.1521 [-0.3684, +0.0813] | -25.41 |
| 2024-OU25-climatology | INCONCLUSIVE_DATA_QUALITY | 380 | — | — | — — | — | — — | — — | — |
| 2024-OU25-market | INCONCLUSIVE_DATA_QUALITY | 246 | — | — | — — | — | — — | — — | — |
| 2026-1X2-climatology | INCONCLUSIVE | 256 | +0.2096 | +0.2193 | -0.0098 [-0.0213, +0.0016] | 87 | -0.1360 [-0.3999, +0.1418] | -0.1471 [-0.4078, +0.1272] | -12.79 |
| 2026-1X2-market | INCONCLUSIVE | 256 | +0.2096 | +0.2033 | +0.0063 [-0.0008, +0.0140] | 87 | -0.1360 [-0.3999, +0.1418] | -0.1471 [-0.4078, +0.1272] | -12.79 |
| 2026-OU25-climatology | INCONCLUSIVE | 256 | +0.5039 | +0.5035 | +0.0004 [-0.0068, +0.0085] | 109 | -0.0399 [-0.2443, +0.1832] | -0.0499 [-0.2521, +0.1707] | -5.44 |
| 2026-OU25-market | INCONCLUSIVE | 256 | +0.5039 | +0.5039 | +0.0000 [-0.0130, +0.0140] | 109 | -0.0399 [-0.2443, +0.1832] | -0.0499 [-0.2521, +0.1707] | -5.44 |

| Diagnóstico abertura (temporada-alvo) | Apostas na abertura | CLV médio | IC95 (normal iid) | ROI líquido na abertura |
|---|---|---|---|---|
| 2021-1X2-climatology | 130 | -0.0879 | [-0.1146, -0.0612] | +0.0447 |
| 2021-OU25-climatology | 87 | -0.0433 | [-0.0597, -0.0269] | -0.0393 |
| 2022-1X2-climatology | 169 | -0.0840 | [-0.1071, -0.0610] | +0.0290 |
| 2022-OU25-climatology | 139 | -0.0463 | [-0.0595, -0.0331] | -0.0916 |
| 2023-1X2-climatology | 164 | -0.0548 | [-0.0721, -0.0374] | -0.1131 |
| 2023-OU25-climatology | 58 | -0.0183 | [-0.0440, +0.0073] | -0.0449 |
| 2024-1X2-climatology | 155 | -0.0485 | [-0.0691, -0.0278] | -0.1045 |
| 2024-OU25-climatology | 39 | +0.0112 | [-0.0326, +0.0549] | -0.1226 |
| 2026-1X2-climatology | 100 | -0.1011 | [-0.1259, -0.0762] | +0.0196 |
| 2026-OU25-climatology | 90 | +0.0252 | [+0.0023, +0.0481] | -0.1480 |

## rc3 (requalificação do BR-F018, 2026-09-24) — números vigentes, iguais no Linux e no Windows do PC 2

Wheel 0.3.0rc3 (`25cdf4d`, `403e6a02…`), mesmos 20 pedidos (`real_env.py`), mesmo snapshot (`31f30a4d…`). Fonte:
`EVIDENCE_NUMBERS.json` → `metrics.real_pc2_owner_linux_rc3_25cdf4d` (Linux primário `owner_linux`); a chave
`metrics.real_pc2_windows_local_rc3_25cdf4d` (Windows local do PC 2) é idêntica, campo a campo
(`RAW_LOGS/c14-rc3-20260924/crossos-real/after_rc3_linuxPC2_x_winPC2.json`: 20/20, 0 diferenças). Tabela por
`scripts/render_metrics.py`.

| Pedido (temporada-alvo-baseline) | Estado | n | Score modelo | Score baseline | Δ médio [IC95] | Apostas | ROI bruto/aposta [IC95] | ROI líquido/aposta [IC95] | Líquido após imposto (u) |
|---|---|---|---|---|---|---|---|---|---|
| 2021-1X2-climatology | INCONCLUSIVE | 250 | +0.2098 | +0.2139 | -0.0041 [-0.0107, +0.0029] | 121 | -0.0935 [-0.3449, +0.1719] | -0.1058 [-0.3539, +0.1561] | -12.80 |
| 2021-1X2-market | REFUTED | 250 | +0.2098 | +0.1942 | +0.0156 [+0.0063, +0.0249] | 121 | -0.0935 [-0.3449, +0.1719] | -0.1058 [-0.3539, +0.1561] | -12.80 |
| 2021-OU25-climatology | INCONCLUSIVE | 250 | +0.4733 | +0.4767 | -0.0034 [-0.0081, +0.0014] | 82 | +0.0211 [-0.1865, +0.2296] | +0.0116 [-0.1938, +0.2177] | +0.81 |
| 2021-OU25-market | INCONCLUSIVE | 250 | +0.4733 | +0.4609 | +0.0124 [-0.0030, +0.0290] | 82 | +0.0211 [-0.1865, +0.2296] | +0.0116 [-0.1938, +0.2177] | +0.81 |
| 2022-1X2-climatology | NO_EDGE | 380 | +0.2093 | +0.2234 | -0.0140 [-0.0214, -0.0068] | 181 | -0.2217 [-0.4226, -0.0043] | -0.2324 [-0.4304, -0.0184] | -42.06 |
| 2022-1X2-market | INCONCLUSIVE | 380 | +0.2093 | +0.2034 | +0.0060 [-0.0007, +0.0133] | 181 | -0.2217 [-0.4226, -0.0043] | -0.2324 [-0.4304, -0.0184] | -42.06 |
| 2022-OU25-climatology | INCONCLUSIVE | 380 | +0.4897 | +0.4938 | -0.0042 [-0.0092, +0.0005] | 152 | -0.1134 [-0.2672, +0.0379] | -0.1218 [-0.2742, +0.0283] | -18.51 |
| 2022-OU25-market | INCONCLUSIVE | 379 | +0.4889 | +0.4816 | +0.0073 [-0.0060, +0.0206] | 152 | -0.1134 [-0.2672, +0.0379] | -0.1218 [-0.2742, +0.0283] | -18.51 |
| 2023-1X2-climatology | INCONCLUSIVE | 380 | +0.2176 | +0.2243 | -0.0067 [-0.0150, +0.0018] | 176 | -0.1614 [-0.3855, +0.0915] | -0.1731 [-0.3938, +0.0765] | -30.46 |
| 2023-1X2-market | REFUTED | 380 | +0.2176 | +0.2108 | +0.0068 [+0.0018, +0.0121] | 176 | -0.1614 [-0.3855, +0.0915] | -0.1731 [-0.3938, +0.0765] | -30.46 |
| 2023-OU25-climatology | INCONCLUSIVE_DATA_QUALITY | 380 | — | — | — — | — | — — | — — | — |
| 2023-OU25-market | INCONCLUSIVE_DATA_QUALITY | 249 | — | — | — — | — | — — | — — | — |
| 2024-1X2-climatology | NO_EDGE | 380 | +0.2110 | +0.2213 | -0.0103 [-0.0175, -0.0027] | 168 | -0.1455 [-0.3647, +0.0884] | -0.1572 [-0.3732, +0.0732] | -26.41 |
| 2024-1X2-market | REFUTED | 378 | +0.2111 | +0.1983 | +0.0128 [+0.0074, +0.0185] | 168 | -0.1455 [-0.3647, +0.0884] | -0.1572 [-0.3732, +0.0732] | -26.41 |
| 2024-OU25-climatology | INCONCLUSIVE_DATA_QUALITY | 380 | — | — | — — | — | — — | — — | — |
| 2024-OU25-market | INCONCLUSIVE_DATA_QUALITY | 246 | — | — | — — | — | — — | — — | — |
| 2026-1X2-climatology | INCONCLUSIVE | 256 | +0.2096 | +0.2193 | -0.0098 [-0.0213, +0.0016] | 87 | -0.1360 [-0.3999, +0.1418] | -0.1471 [-0.4078, +0.1272] | -12.79 |
| 2026-1X2-market | INCONCLUSIVE | 256 | +0.2096 | +0.2033 | +0.0063 [-0.0008, +0.0140] | 87 | -0.1360 [-0.3999, +0.1418] | -0.1471 [-0.4078, +0.1272] | -12.79 |
| 2026-OU25-climatology | INCONCLUSIVE | 256 | +0.5039 | +0.5035 | +0.0004 [-0.0068, +0.0084] | 109 | -0.0399 [-0.2443, +0.1832] | -0.0499 [-0.2521, +0.1707] | -5.44 |
| 2026-OU25-market | INCONCLUSIVE | 256 | +0.5039 | +0.5039 | +0.0000 [-0.0130, +0.0140] | 109 | -0.0399 [-0.2443, +0.1832] | -0.0499 [-0.2521, +0.1707] | -5.44 |

| Diagnóstico abertura (temporada-alvo) | Apostas na abertura | CLV médio | IC95 (normal iid) | ROI líquido na abertura |
|---|---|---|---|---|
| 2021-1X2-climatology | 130 | -0.0879 | [-0.1146, -0.0612] | +0.0447 |
| 2021-OU25-climatology | 87 | -0.0433 | [-0.0597, -0.0269] | -0.0393 |
| 2022-1X2-climatology | 169 | -0.0845 | [-0.1080, -0.0611] | -0.0008 |
| 2022-OU25-climatology | 137 | -0.0460 | [-0.0594, -0.0326] | -0.0902 |
| 2023-1X2-climatology | 163 | -0.0544 | [-0.0719, -0.0369] | -0.1077 |
| 2023-OU25-climatology | 57 | -0.0182 | [-0.0443, +0.0078] | -0.0612 |
| 2024-1X2-climatology | 156 | -0.0485 | [-0.0690, -0.0280] | -0.1103 |
| 2024-OU25-climatology | 38 | +0.0141 | [-0.0305, +0.0586] | -0.1464 |
| 2026-1X2-climatology | 99 | -0.1003 | [-0.1254, -0.0753] | +0.0299 |
| 2026-OU25-climatology | 90 | +0.0252 | [+0.0023, +0.0481] | -0.1480 |
