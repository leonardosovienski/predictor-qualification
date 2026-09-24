# MISSÃO — ETAPA B: ORQUESTRAÇÃO DE PESQUISA DO CRIPTO (Rev 9)

```text
stage  = B
branch = integration-crypto
núcleo = qualification/COMMON_QUALIFICATION_CORE.md v2.3
sha256 = beaa5feed193356f554922439936ad401c8f177bfd18d8864ca329fae94216fc
```

Leia e siga também `prompts/prompt_etapa_b_comum_rev9.md` (vale inteiro). Este arquivo só acrescenta o que é do Cripto.
É a **primeira** das três integrações (D-22): além da orquestração do Cripto, ela cria no `cain` o framework que as
outras duas vão reutilizar.

## 1. Pré-condições (além das comuns)

* Nenhuma integração anterior: esta é a primeira.

## 2. Domínio

| Item | Valor |
|---|---|
| Repositório | `cripto-predictor`, commit e wheel de `qualification/crypto/runtime_target.json` |
| Contrato | `qualification/crypto/DOMAIN_RESEARCH_CONTRACT.json` (prefixo `crypto`) |
| `adapter_paths` | `GarimpoInvestimentos/adapters/` |
| Entrypoint permitido | `cripto-research-adapter → GarimpoInvestimentos.adapters.<módulo>:main` |
| Linux primário | GitHub Actions (dados públicos Binance data.vision, baixados no job e conferidos pelo `.CHECKSUM`; D-16) |
| Windows secundário | local (D-3): CAIN e a parte Cripto em `C:\Cripto\qualificacao\runtime\integration-crypto\` |

## 3. O que só esta missão constrói

1. **Framework genérico da orquestração** no `cain`, pensado para três domínios desde o início, mas exercitado só com o Cripto:
   composition root real, `TaskOutbox`/`ResultInbox` V2, memória com namespace obrigatório por domínio (sobre a memória
   bitemporal do PR #45), episódios numerados por domínio, DecisionPolicy genérica e o formato da **configuração de
   domínio**. Critério: acrescentar Stocks e Brasileirão deve exigir só uma configuração nova e um adapter, sem mudar o
   framework. Registre em `DECISION_POLICY_REPORT.md` a interface da configuração de domínio.
2. **Configuração do Cripto** para a DecisionPolicy: handlers da `handler_allowlist`, custos, baselines e as hipóteses
   já encerradas no estado científico do Cripto (H1..H9 e a família congelada), que **nunca** são reabertas: proposta
   equivalente vira `DUPLICATE` ou `BLOCK`, com receipt.
3. **Resolver o conflito do PR #50** (comum, seção 4). Como é a primeira missão, a escolha vale para as três e fica
   documentada no `DECISION_POLICY_REPORT.md`.
4. **Adapter do Cripto** nos `adapter_paths`.

## 4. Isolamento

Stocks e Brasileirão ainda não estão integrados: `CROSS_DOMAIN_ISOLATION`, `DOMAIN_QUALIFIED_IDS` e o N+1 usam fixtures
V2 congeladas dos dois (geradas pelos vetores da Etapa A deles, sem rodar os predictors), com o mesmo `H9` nos três.

## 5. Cuidados conhecidos

* `QUALIFIED` na Etapa A não é edge: o resultado econômico real do Cripto foi `INCONCLUSIVE`/`NO_EDGE` (C22). A policy
  não pode tratar `QUALIFIED` como sinal econômico.
* O plugin cripto devolve `version: null` no `health()` (A-06, P2): resolver no adapter ou registrar.
* Depois desta missão, qualquer mudança no framework feita pelas missões seguintes refaz as fases desta que o exercitam (C14).
