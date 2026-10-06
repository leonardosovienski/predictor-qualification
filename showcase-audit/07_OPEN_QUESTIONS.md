# 07 — Questões abertas (Fase 1)

| Questão | Por que importa | Evidência existente | O que falta | Status |
|---|---|---|---|---|
| O proprietário confirma que `predictor-qualification` voltou a privado e quando a janela de 2026-10-06 começou/terminou? | Classificação de exposição | fato informado | confirmação explícita | EXTERNAL_VALIDATION_REQUIRED |
| O que fazer com os dumps de código em QUAL (`source-text.txt`), o zip de patches e o PII em ECO, dado que já foram públicos? | Risco residual e dever de cuidado | EVID-QUAL-008, EVID-ECO-013/015 | decisão humana (remoção, reescrita de histórico, notificação) | HIGH_PRIORITY_EXPOSURE_REVIEW |
| O nome `ecosystem-predictor` foi liberado pelo rename do privado? Está disponível para a vitrine? | Colisão de identidade/URLs | EVID-ECO-002 | consulta ao GitHub | EXTERNAL_VALIDATION_REQUIRED |
| Estado atual de `stocks-predictor`: R8 relacrado? H17 desbloqueada? `research_execution.py` em main? | Claims de lacre e duplicação | EVID-QUAL-004/007 (até 2026-10-03) | clone de stocks-predictor | BLOCKED (acesso negado) |
| `cripto-predictor`: arquivo `source_archive_20260908` ainda presente? tags existem? V1.2 fechada? | History exposure e estado | EVID-QUAL-009 (presente em 2026-09-30) | clone de cripto-predictor | BLOCKED (clone negado) |
| `predictor-ops`: achado OPS-05 (permissão de capital vem do config) e CORE-02 (concorrência V2) têm correção? | Segurança da barreira de capital | EVID-QUAL-006 | clone de predictor-ops; estado do core main | BLOCKED / NEEDS_EVIDENCE |
| As três attestations não reproduzíveis no `main` serão reemitidas ou isoladas por ciclo? | Credibilidade do pacote de evidência | EVID-QUAL-007 | decisão do dono (D-29..31 propostas) | NEEDS_EVIDENCE |
| Qual contagem de testes do Cripto é correta no audit 2026-09-20 (1580/7 ou 1614/1)? | Consistência | EVID-ECO-017 | reexecução no SHA ou errata | NEEDS_EVIDENCE |
| Existem timestamps externos (OpenTimestamps, release assets datados por terceiro) para pré-registros H17–H19 e protocolos? | Anterioridade forte | só tags/commits internos (EVID-ECO-028, EVID-CAIN-001, EVID-BRAS-001, EVID-CORE-001) | busca nos domínios; eventual carimbo externo futuro | NEEDS_EVIDENCE |
| Resultados das CI runs citadas por ID são verificáveis publicamente após privatização? | Claims "CI verde" | URLs em docs | captura/arquivamento de evidência | EXTERNAL_VALIDATION_REQUIRED |
| O commit `9d53e53a…` (exceções gitleaks) contém de fato só fixtures sintéticas? | Segurança do histórico | `.gitleaksignore` descreve como fictício; CI security-history | varredura do histórico (bloqueada nesta sessão) | NOT_TESTED |
| Suítes raiz do ECO e do CORE passam no HEAD atual? | Claims de testes | EVID-ECO-003, EVID-CORE-003 | ambiente com dependências instaláveis | BLOCKED (offline) |
| `qualification_inventory.py` será estendido para WIRED→PROVEN ou a escala fica só no ledger manual? | Reprodutibilidade da maturidade | EVID-QUAL-004/005 | decisão | NEEDS_EVIDENCE |
| H17 "PAUSED_INCONCLUSIVE_DATA_QUALITY": qual o problema de dados e está documentado para publicação como resultado negativo? | Valor científico | EVID-QUAL-006 | fonte primária em stocks-predictor | BLOCKED |
| A linha de pesquisa CAIN ("evidência não vira autoridade") tem experimento desenhado (A/B/C) ou só proposta? | Fase futura | EVID-CAIN-002/004 (contenção implementada; sem experimento comparativo encontrado) | permanece PROPOSED | NEEDS_EVIDENCE |

`DISCOVERED_OUTSIDE_ECOSYSTEM` (registrados para Fase 2, não investigados a fundo):

| Projeto | Descrição | Evidence ID | Relevância | Fase 2? |
|---|---|---|---|---|
| BRAS/CORE/OPS | Auditoria adversarial 2026-09-05 com adendos autocríticos | EVID-BRAS-002, EVID-CORE-002 | Prova de disciplina de avaliação e de correção fechada em release | Sim |
| QUAL | CAIN_EXTREME_20260928 e estudo "do zero" dos oito projetos (27 problemas priorizados) | EVID-QUAL-006/010 | Evidência de revisão independente; resultados negativos de engenharia | Sim |
| QUAL | Teste conjunto 58/58 com RAW_LOGS hash-identificados | EVID-QUAL-003 | Melhor evidência de integração real | Sim |
| CAIN | Protocolo de avaliação L0 e revisão independente com modelos locais | EVID-CAIN-004 | Linha "avaliação de agentes de pesquisa" | Sim |
| BRAS | 29 trials com só 1 comprovada; EXP-001 contrato prospectivo | EVID-BRAS-003/004 | Resultado negativo honesto; pré-registro | Sim |
| STOCKS (via QUAL) | Ledger de maturidade; H17 pausada por qualidade de dados | EVID-QUAL-004 | Caso de "componente implementado não wired" e de pausa metodológica | Sim (requer clone) |
