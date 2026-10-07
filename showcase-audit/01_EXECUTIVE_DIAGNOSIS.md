# 01 — Diagnóstico executivo (Fase 1)

**Auditoria:** 2026-10-06 (UTC). **Canônico:** `ecosystem-predictor-cain` @ `602f369d7a8f2f91bf7b5e26d237908badc1dd02` (branch de trabalho = `main` = `origin/main`, árvore limpa). **Repositórios locais usados para verificação cruzada:** `predictor-qualification` @ `d9f0216`, `cain` @ `abeb1e6`, `brasileirao-predictor` @ `1e0c6f0`, `core-predictor` @ `956891e`. **Ausentes:** `stocks-predictor`, `predictor-ops` (acesso negado pelo controle de permissões da sessão), `cripto-predictor` (clone negado). Para esses três, só evidência secundária registrada em `predictor-qualification`.

## O que existe

Um repositório de **governança, contratos e transporte de evidência**, não um predictor: biblioteca de contratos de estado e permissão de capital (fail-closed), registry opcional de plugins, quatro pacotes stdlib de transporte (snapshot, bundle, protocolo V2, transporte com trava por domínio), 12 registries JSON datados, 8 workflows de CI (matriz Python 3.11–3.14, cobertura mínima, varredura de segredos no histórico completo com controle sintético, release reprodutível por `git archive` + `SOURCE_DATE_EPOCH`), recibos com hashes e índice explícito de autoridade documental. Histórico completo: 267 commits (2026-07-17 → 2026-10-05), 14 tags.

## Maior valor científico/técnico

1. **Disciplina de evidência codificada**, não só declarada: quatro eixos de estado (científico/preditivo/econômico/operacional), capital `FORBIDDEN` por padrão no contrato, testes que impedem regressões de registry (ex.: "atestado invalidado nunca passa por não precisa reemitir").
2. **Resultados negativos abundantes e pré-registrados** nos três domínios (17 hipóteses falsificadas documentadas; 29 trials do Brasileirão com 6 refutadas, 6 inconclusivas, 1 comprovada; H6 cripto inconclusiva com poder medido; EXP-001 histórico declarado inviável; auditoria adversarial de 2026-09-05 com 7 achados, 2 críticos, registrada e respondida).
3. **Qualificação por protocolo com attestations hash-identificadas**: seis attestations `QUALIFIED` vigentes (3 de domínio, 3 de integração), todas com `capital_permission=false`; teste conjunto dos três domínios 58/58 com hashes **conferidos localmente** nesta auditoria contra o que o canônico cita.
4. **Princípio arquitetural "modelo propõe; política determinística decide"** implementado no CAIN (política de decisão versionada por hash, sem LLM e sem relógio; CAIN `PROPOSE_ONLY`) e no envelope/transporte (não escolhe handler, budget nem capital). Transporte: 310 testes reproduzidos nesta auditoria.

## Maiores problemas

- As evidências mais fortes citadas pelo canônico vivem em `predictor-qualification` e no GitHub; no canônico são `DECLARED`. Agora verificadas em parte (hashes das attestations e do teste conjunto conferem).
- **Attestations não reproduzíveis no `main` atual** da qualificação: três `QUALIFIED` (crypto V1.1, integration-crypto, integration-stocks) só validam no commit de emissão porque o ciclo D-27 regravou relatórios no mesmo diretório (achado EPOCA-QUAL-1, P1, do próprio estudo interno).
- Lacre operacional R8 do Stocks **quebrado no `main`** desde a mudança de licença (CI vermelho só nesse gate; não relacrado por decisão fundamentada). Distinto dos lacres de configuração H17–H19, que estão intactos (hashes recalculados em 2026-10-03). Ver 05/07.
- Inconsistência interna de contagem (1580/7 vs 1614/1 testes do Cripto) no audit CAIN↔CRIPTO de 2026-09-20.
- Identidade: `pyproject`, docs e URLs chamam o canônico de `ecosystem-predictor`; o remoto é `-cain`. O nome planejado para a vitrine coincide com o nome histórico do privado.

## Maior risco de exposição

**Os oito repositórios foram públicos até 2026-10-05 (fato informado pelo proprietário)** e `predictor-qualification` foi reaberto em 2026-10-06. Esse repositório contém **dumps integrais de código** de `cain` (1,2 MB) e `stocks-predictor` (1,8 MB) em texto plano, índices AST de vários repositórios, e revisões objeto a objeto do arquivo histórico do Cripto. O canônico contém PII de 10 terceiros reais (registro comercial), 6 patches de código dos seis repositórios num zip de auditoria, overlay com código, e caminhos/usuário/porta locais em 18 arquivos. Tudo isso deve ser tratado como **exposição pública passada confirmada** (conteúdo até 2026-10-05). `HIGH_PRIORITY_EXPOSURE_REVIEW`.

## Maior oportunidade para o showcase

Narrativa verificável sem código: sistemas de previsão → problemas de avaliação (PIT, leakage, DSR) → resultados negativos disciplinados → qualificação com attestations e teste conjunto → governança de agente de pesquisa (proposta ≠ autoridade). Sustentada por números agregados com fonte (hashes já conferidos), taxonomias públicas (glossário de vereditos, quatro eixos), e pela auditoria adversarial de 2026-09-05 como prova de autocrítica.

## Principais incertezas

Estado atual de `stocks-predictor`, `predictor-ops` e `cripto-predictor` (sem clone); exposição efetiva (acessos/clones externos: não determinável); se o nome `ecosystem-predictor` está livre; publicabilidade dos números dos domínios até verificação primária na Fase 2.
