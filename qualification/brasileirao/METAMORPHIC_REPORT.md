# METAMORPHIC_REPORT — missão brasileirao (gate `BR_METAMORPHIC`)

> **Requalificação rc3 (C14 do BR-F018, 2026-09-24):** final_commit `25cdf4d` / wheel 0.3.0rc3 `403e6a02…`. 5 permutações congeladas verdes nos 4 ambientes; soak com o dado real: 5 permutações idênticas à referência; corroboração real: `permuted_identical`. Detalhes: `BR_F018_REQUALIFICATION_REPORT.md`; saída bruta: `RAW_LOGS/c14-rc3-20260924/`. O texto abaixo descreve a rc2 (Etapa A).

Relação metamórfica: permutar a ordem física das linhas do dataset (mesmo conteúdo) não muda o
resultado.

* Permutações congeladas: 5, seeds `[11, 23, 37, 41, 53]` (`FROZEN_PARAMETERS.json` → `metamorphic`),
  aplicadas à ordem de inserção de **todas** as linhas de `sofascore_matches`, `matches` e
  `match_kickoff_versions` (`tests/conformance/fixtures.py`, sha256 em `FROZEN_VECTORS.json`).
* Comparador congelado: igualdade exata do JSON de `harness.comparable()` — estados
  (resultado/científico/econômico), previsões por evento (cutoff, refit, Elo, parâmetros,
  probabilidades, nº de informações), avaliação (scores, Δ, IC) e economia (ROI bruto/líquido, IC).
  Fica de fora só o fingerprint da informação (que por construção não depende da ordem física, mas
  é identidade e não resultado).
* Por que passa: o handler ordena a informação pelo conteúdo (`available_at`, kickoff, event_id,
  times) antes de qualquer cálculo; o SQL nunca depende da ordem física.

| Teste | Onde |
|---|---|
| `test_metamorphic_row_order_permutations_do_not_change_results` (5 permutações × pedido completo pelo entrypoint) | Linux primário, windows-latest, Windows local |
| soak: 5 ciclos com dataset fora de ordem | Linux primário (diagnóstico) |
| dado real: 1 permutação (seed 11) de uma cópia do snapshot | Windows local (`REAL_CORROBORATION.json` → `permuted_identical`) |

Diferença sem explicação = não passa. Nenhuma diferença foi observada.
