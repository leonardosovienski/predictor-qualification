# MISSÃO — ETAPA B: ORQUESTRAÇÃO DE PESQUISA DO BRASILEIRÃO (Rev 9)

```text
stage  = B
branch = integration-brasileirao
núcleo = qualification/COMMON_QUALIFICATION_CORE.md v2.3
sha256 = beaa5feed193356f554922439936ad401c8f177bfd18d8864ca329fae94216fc
```

Leia e siga também `prompts/prompt_etapa_b_comum_rev9.md` (vale inteiro). Este arquivo só acrescenta o que é do Brasileirão.
É a **terceira** integração (D-22): reutiliza o framework criado pela `integration-crypto`.

## 1. Pré-condições (além das comuns)

* `qualification/integration-stocks/QUALIFICATION_ATTESTATION.json` com `result = QUALIFIED` no `main`
  (e, por consequência, a `integration-crypto`).

## 2. Domínio

| Item | Valor |
|---|---|
| Repositório | `brasileirao-predictor`, commit e wheel de `qualification/brasileirao/runtime_target.json` (rc3, BR-F018 corrigido) |
| Contrato | `qualification/brasileirao/DOMAIN_RESEARCH_CONTRACT.json` (prefixo `brasileirao`) |
| `adapter_paths` | `brasileirao_predictor/adapters/` |
| Entrypoint permitido | `brasileirao-research-adapter → brasileirao_predictor.adapters.<módulo>:main` |
| Linux primário | `owner_linux`, o PC 2 (D-19): o dado real é privado |
| Windows secundário | local no PC 2 (D-3): `C:\QUALIFICACAO\runtime\integration-brasileirao\` |

## 3. Regra do dado (a mais importante desta missão)

O dado real é **privado** (D-11). Ele fica só no PC 2 e **nunca** vai para commit, PR, artefato, release, Actions, nuvem
ou log com linhas do conteúdo. Isso vale também para a **memória do CAIN**: ela guarda referências, resumos e hashes,
nunca linhas de jogos, odds ou resultados do dado. Confira isso no `no_data_rows_check` antes de cada commit.

## 4. O que só esta missão constrói

1. **Configuração do Brasileirão** para a DecisionPolicy: handlers da `handler_allowlist` e métricas e baselines próprios
   do domínio (RPS, Brier, log-loss, calibração, odds de mercado, P&L líquido, conforme o contrato). Nada de baseline de
   mercado financeiro.
2. **Adapter do Brasileirão** nos `adapter_paths`.
3. **Framework:** reutilizar sem mudar. Se precisar mudar, refaça as fases da `integration-crypto` e da
   `integration-stocks` que o exercitam e reemita as duas (C14), no mesmo ciclo.

## 5. Isolamento

`CROSS_DOMAIN_ISOLATION`, `DOMAIN_QUALIFIED_IDS` e N+1 contra Cripto e Stocks **pelos runtimes integrados**; mesmo `H9` nos três.

## 6. Cuidados conhecidos

* O **holdout 2025 é lacrado** pela política do predictor. Nenhuma proposta do CAIN o acessa sem `REQUIRE_HUMAN`, e a
  política do domínio continua podendo recusar.
* As hipóteses que o loop do PR #50 encerrou sem melhora (dois ciclos no Brasileirão) e os achados do PR #51 entram na
  memória do domínio como vieram. Proposta equivalente vira `DUPLICATE` ou `BLOCK`, com receipt.
* BR-F018 foi corrigido na rc3 (Windows e Linux 20/20 idênticos). Qualquer divergência nova entre sistemas operacionais é achado P1.
* O **BR-F019 (P2, aberto)** já registra que `event_models.fit_event_model`, `dixon_coles.fit_dixon_coles_parameters` e
  `xg_model.fit` também dependem do último bit. Os três ficam fora do worker de pesquisa, e o efeito medido é nulo no
  resultado e na operação. Não é divergência nova. Se o adapter passar a usar algum deles, meça de novo e reclassifique
  pela C6.
* O teste do pré-registro emite `ExpiredHarnessAttestationWarning` (A-04; BR-F010 `FIXED`), e isso é esperado. Renovar
  `data/trials.harness_attestation.json` é decisão do dono (artefato protegido, C15.1).
* O `README.md` e o `docs/ESTADO_ATUAL.md` do `brasileirao-predictor` estão desatualizados, e o dono decidiu deixá-los
  assim (2026-09-25). Não os atualize nesta missão: fora dos `adapter_paths`, isso quebraria a C24.3(a).
* Resultado econômico da Etapa A: `NO_EDGE` (C22).
