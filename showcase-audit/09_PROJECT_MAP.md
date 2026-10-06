# 09 — Mapa real dos oito projetos (Fase 2)

Base: cinco clones completos (ECO `602f369`, QUAL `d9f0216`, CAIN `abeb1e6`, BRAS `1e0c6f0`, CORE `956891e`) e, para STOCKS/CRIPTO/OPS, os registros de QUAL (estudo "do zero" de 2026-09-30, attestations, RAW_LOGS). Base de cada relação classificada conforme seção 22 do protocolo. "Estado" é o observado nesta auditoria, não o declarado.

## Projetos

| Projeto | Papel observado | Primeiro commit | Último commit / tag | Tamanho (arquivos / funções de teste) | Maturidade dominante | Base |
|---|---|---|---|---|---|---|
| core-predictor | Biblioteca científica neutra: contratos temporais (`PredictionPoint`, replay anti-lookahead), medição (bootstrap, DSR), registro de trials V2 com proveniência, harness de controle positivo (atestado de poder). Sem dependências de runtime. | 2026-06-16 ("canonical core v0.4.0") | 2026-09-30 / `v3.2.1` = `7bb212c` (2026-09-11) | 114 / 255 | IMPLEMENTED + EXERCISED (278 testes em 2026-09-28 por QUAL); REPRODUCED não (offline) | DIRECT_REFERENCE (clone) |
| predictor-ops | Supervisor local de jobs: subprocesso, locks/leases, heartbeat, idempotência, proveniência de instalação, kill-switch; permissão de capital é dado de config, não autorização. | — (não clonado) | 4.2.2rc1 (`9831b0d`) | — | DECLARED aqui; EXERCISED em QUAL (88+1 testes, 80,9%) | DOCUMENTED_RELATION (QUAL) |
| cripto-predictor | Domínio cripto: ingestão/feature store, diagnóstico por LLM, pesquisa quantitativa (HMM funding/OI, score LLM), governança com charter científico fail-closed, adapter V2, exportador de evidência. | — (não clonado) | 1.2.0rc4 (`21f8b18`) | — | DECLARED aqui; EXERCISED em QUAL (Etapa A QUALIFIED V1.1; V1.2 30/31) | DOCUMENTED_RELATION (QUAL) |
| brasileirao-predictor | Domínio futebol: Elo + Binomial Negativa/Dixon-Coles, protocolo de previsão com classes PRE_MATCH/LIVE/RETROSPECTIVE, ledger prospectivo, worker .NET de escalações, runtime de pesquisa V2. Bootstrap a partir do `wc-predictor-v2` (Copa 2026). | 2026-07-10 | 2026-09-30 / `v0.3.0rc5` (2026-09-29) | 2.622 / 1.490 | IMPLEMENTED + EXERCISED (QUAL QUALIFIED 32 gates; 2.090 testes em recibo de 2026-09-12) | DIRECT_REFERENCE |
| stocks-predictor | Domínio ações B3: ingestão COTAHIST/CVM com catálogo versionado e PIT, fatores, backtest causal D+1, judge com DSR/bootstrap, linha RJ (recuperação judicial), armazenamento operacional append-only; gate econômico implementado e não conectado. | — (não clonado) | 0.3.0rc3 (`6f857b2`); `main` à frente (rc4 não publicada) | 812 funções de teste (QUAL) | DECLARED aqui; EXERCISED em QUAL (QUALIFIED 31 gates; sonda D-16 real) | DOCUMENTED_RELATION (QUAL) |
| ecosystem-predictor(-cain) | Governança/contratos: 4 eixos de estado, registry opcional, 12 registries datados, 4 pacotes de transporte (snapshot, bundle, protocolo V2, transporte), lock conjunta, CI com drift e varredura de histórico. Arquitetura antiga (gateway/db) removida. | 2026-07-17 | 2026-10-05 / `v0.2.1` (2026-09-29) | 235 / 180 | IMPLEMENTED + REPRODUCED (310 testes de pacotes) | DIRECT_REFERENCE |
| cain | Assistente/orquestrador de pesquisa: admite evidência (snapshot/bundle) com grants, memória bitemporal por domínio, política de decisão determinística versionada (sem LLM/relógio), outbox/inbox do envelope V2, propostas por LLM local opcionais, protocolo de avaliação L0. | 2026-09-07 | 2026-09-30 / `v0.4.13rc15` (2026-09-29) | 756 / 854 | IMPLEMENTED + EXERCISED (1.446 testes em QUAL; 787 em 2026-09-29) | DIRECT_REFERENCE |
| predictor-qualification | Protocolo de qualificação pré-treinamento: núcleo com regras C-numeradas, schema de attestation, 6 missões (3 Etapa A, 3 Etapa B), RAW_LOGS hash-identificados, estudo "do zero" dos oito projetos, auditoria adversarial do CAIN. | 2026-09-23 | 2026-10-05 | 7.923 / — | EXERCISED (attestations, 58/58); REPRODUCED (identidade dos arquivos) | DIRECT_REFERENCE |

## Relações (base de conclusão)

| De → Para | Mecanismo observado | Base | Evidence ID |
|---|---|---|---|
| cripto, brasileirão, stocks → core | import da biblioteca; wheel 3.2.1 fixada por URL + sha256 nos locks dos três | SHARED_ARTIFACT (lock/hash) + DIRECT_REFERENCE (BRAS) | EVID-QUAL-018, EVID-ECO-008 |
| cripto, brasileirão → ops | execução de jobs via runner; wheel 4.2.x fixada | SHARED_ARTIFACT | EVID-QUAL-018 |
| stocks → ops | declarado no stack V2 (adapter) | DOCUMENTED_RELATION | EVID-QUAL-002 |
| ecosystem → {cripto, stocks, brasileirão} | registry descobre plugins (health/capabilities); opcional, não obrigatório | SHARED_INTERFACE (`PluginV1`) | EVID-ECO-007, EVID-QUAL-018 |
| ecosystem → cain | contratos snapshot/bundle/protocolo V2/transporte distribuídos como wheels; CAIN depende do transporte pelo lock | SHARED_ARTIFACT | EVID-ECO-020, EVID-CAIN-002 |
| cain ↔ {cripto, stocks, brasileirão} | envelope V2 via spool: task → adapter do domínio → resultado; domínios não dependem do envelope | SHARED_INTERFACE (envelope) + EXERCISED (58/58) | EVID-QUAL-003 |
| {cripto, stocks, brasileirão} → cain | exportação de evidência admitida (snapshot/bundle) por hash; grants no receptor | SHARED_INTERFACE + EXERCISED (recibos) | EVID-ECO-019, EVID-CAIN-006 |
| qualification → todos | clona/instala wheels por hash, roda cleanroom, E2E, soak, matriz de falhas; emite attestations | SHARED_ARTIFACT (final_commits + wheels) | EVID-QUAL-002 |
| brasileirão ← wc-predictor (histórico, fora do escopo) | bootstrap do repositório a partir do `wc-predictor-v2` pós-Copa | HISTORICAL_EVIDENCE (mensagem do primeiro commit) | EVID-BRAS-008 |
| core ← previsao-cripto (histórico) | template de pré-registro "promovido do previsao-cripto" | HISTORICAL_EVIDENCE (doc do core) | EVID-CORE-004 |
| ecosystem ← {cs, lol, f1, wc, nba} (históricos) | documentos de fechamento e vereditos de 2026-07 cobrem esses repositórios | HISTORICAL_EVIDENCE | EVID-ECO-023/030 |

Não há banco central nem serviço compartilhado em execução; a integração é por artefatos (wheels com hash), arquivos (spool, publicações) e contratos. "Sete repositórios" no charter do ECO exclui `predictor-qualification`, que o protocolo desta auditoria inclui como oitavo.

## Estado por eixo (observado, sem promoção)

| Projeto | Científico | Preditivo | Econômico | Operacional | Capital |
|---|---|---|---|---|---|
| cripto | famílias H1–H5 CLOSED_NO_GO; H6 INCONCLUSIVE; sonda real V1.x INCONCLUSIVE | sem edge demonstrado | NO_EDGE (−45 bruto / −83 bps líquido por semana, n=52, IC cruza zero) | QUALIFIED (Etapa A V1.1); V1.2 BLOCKED (Windows) | FORBIDDEN em todo artefato |
| stocks | H1–H16 encerradas; H17 pausada (qualidade de dados); H18/H19 pausadas; RJ sem dado real | sonda momentum PIT INCONCLUSIVE (excesso +38 bps, IC [−33; +104]) | NO_EDGE | QUALIFIED (31 gates); lacre R8 quebrado no main (decisão de não relacrar) | FORBIDDEN |
| brasileirão | 29 trials: 1 comprovada (qualidade de previsão), 6 refutadas, 6 inconclusivas, 8 pré-registradas | modelo perde do mercado (2021–2024); sem edge demonstrável no circuito qualificado | NO_EDGE | QUALIFIED (32 gates); BR-F018 (não determinismo entre SOs) corrigido na rc3 | FORBIDDEN |
| core | N/A (biblioteca) | N/A | N/A | 3.2.1 publicada e pinada por todos | N/A |
| ops | N/A | N/A | N/A | 4.2.2rc1 publicada | capital é config, não autorização |
| ecosystem | N/A | N/A | hipótese comercial B0/E0 | registry/contratos/transporte; 0.2.1 | FORBIDDEN por contrato |
| cain | N/A (orquestra; não julga ciência) | N/A | N/A | rc15 publicada; PROPOSE_ONLY; contenção verificada por QUAL | false em todo receipt |
| qualification | N/A | N/A | N/A | 6 attestations QUALIFIED; 3 não revalidam no main | false em todas |
