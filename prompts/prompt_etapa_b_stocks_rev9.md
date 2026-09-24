# MISSÃO — ETAPA B: ORQUESTRAÇÃO DE PESQUISA DO STOCKS (Rev 9)

```text
stage  = B
branch = integration-stocks
núcleo = qualification/COMMON_QUALIFICATION_CORE.md v2.3
sha256 = beaa5feed193356f554922439936ad401c8f177bfd18d8864ca329fae94216fc
```

Leia e siga também `prompts/prompt_etapa_b_comum_rev9.md` (vale inteiro). Este arquivo só acrescenta o que é do Stocks.
É a **segunda** integração (D-22): reutiliza o framework criado pela `integration-crypto`.

## 1. Pré-condições (além das comuns)

* `qualification/integration-crypto/QUALIFICATION_ATTESTATION.json` com `result = QUALIFIED` no `main`.

## 2. Domínio

| Item | Valor |
|---|---|
| Repositório | `stocks-predictor`, commit e wheel de `qualification/stocks/runtime_target.json` |
| Contrato | `qualification/stocks/DOMAIN_RESEARCH_CONTRACT.json` (prefixo `stocks`) |
| `adapter_paths` | `stocks_predictor/adapters/` |
| Entrypoint permitido | **nenhum** (`adapter_entrypoints` vazio): o adapter é biblioteca, chamado pelo transporte do ecosystem. Se um script for inevitável, pare (C24.4) |
| Linux primário | GitHub Actions (D-9) |
| Windows secundário | `windows-latest` no GitHub Actions (D-1: nada é instalado no Windows local para o Stocks) |
| Dados reais | só públicos (B3/CVM), por URL + sha256 fixados antes de cada execução (D-16, D-21). As fontes mudam: todo run novo precisa de pin novo (`build_real_panel.py pin`), como no PR #21 |

## 3. O que só esta missão constrói

1. **Configuração do Stocks** para a DecisionPolicy: handlers da `handler_allowlist`, famílias de sinal existentes
   (momentum, máxima de 52 semanas, baixa volatilidade, volume, external intelligence, conforme o contrato), baselines
   e custos do próprio Stocks. Regras do Cripto **não** são transportadas.
2. **Adapter do Stocks** nos `adapter_paths`.
3. **Framework:** reutilizar sem mudar. Se precisar mudar, a mudança vale para o Cripto também: refaça as fases da
   `integration-crypto` que o exercitam (E2E, N+1, isolamento) e reemita a attestation dela (C14), no mesmo ciclo.

## 4. Isolamento

`CROSS_DOMAIN_ISOLATION`, `DOMAIN_QUALIFIED_IDS` e N+1: contra o Cripto **pelo runtime integrado** e contra o Brasileirão
por fixtures V2 congeladas; mesmo `H9` nos três.

## 5. Cuidados conhecidos

* ST-F007 (D-21): o rebalance é "a cada 21 pregões", não "fim de mês". A configuração do domínio usa o que o handler aceita.
* ST-F008 (D-21): painel público com retorno só-preço e lacunas de eventos. A policy não pode tratar métricas desse painel
  como mais fortes do que são.
* Resultado econômico da Etapa A: sem edge demonstrado (C22).
