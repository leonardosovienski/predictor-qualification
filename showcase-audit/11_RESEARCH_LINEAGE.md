# 11 — Linhagem de pesquisa (Fase 2)

Hipótese testada (do protocolo): prediction systems → evaluation problems → leakage/overfitting/false positives → qualification → reproducibility → research infrastructure → governance/evaluation of research agents → CAIN. Cada elo abaixo tem data e fonte; onde a ordem não é sustentada, está dito.

## Cronologia datada (INTERNAL_TIMESTAMP_ONLY: commits, tags e datas em documentos)

| Data | Marco | Fonte | Elo da hipótese |
|---|---|---|---|
| ≤2026-06-16 | Auditoria interna de três projetos de previsão (Copa, ações, cripto) motiva o blueprint de um "core" compartilhado | `PREDICTOR_CORE_BLUEPRINT.md` (ECO); primeiro commit do core 2026-06-16 | prediction systems → evaluation problems |
| 2026-06-27 | Diagnóstico do viés pró-zebra: +44% de ROI explicado como variância; modelo perde do mercado em walk-forward | `VIES_ZEBRA.md`, `CONCLUSOES.md` (BRAS) | evaluation problems / false positives |
| 2026-07-02 | Famílias HMM funding/OI encerradas NO-GO após custos; Kelly-sweep pré-custos descartado | VEREDITOS (ECO) | false positives (artefato de varredura) |
| 2026-07-10 | `brasileirao-predictor` nasce do `wc-predictor-v2`; H1 OU2.5 refutada no mesmo dia | primeiro commit BRAS; trials.json | prediction systems → evaluation |
| 2026-07-11→17 | Reintegração do ecossistema (Ondas 1–6), contrato temporal conceitual, auditoria hostil final; ECO nasce em 2026-07-17 como governança documental | SINERGIAS, FINAL_FORENSIC_REVIEW, primeiro commit ECO | research infrastructure (1ª tentativa) |
| 2026-07-13→18 | Incidente de credencial em logs; redação em código; rotação só em 2026-09-03 | SECURITY_INCIDENT (ECO) | (operacional) |
| 2026-07-26/28 | 42 hipóteses com veredito formal; H5 cripto (score LLM) refutada com direção oposta; "capital aprovado: zero" | VEREDITOS (ECO) | leakage/overfitting/false positives → disciplina de veredito |
| 2026-07-28 → 2026-08-17 | Core 1.0.0 → 2.3.0 (tags) | tags CORE | research infrastructure |
| 2026-08-02 | ADRs do ECO (protocolo de plugins; propriedade de dados); arquitetura de agregador com gateway/db | `docs/adr` (ECO) | infrastructure (depois invalidada) |
| 2026-08-08 | ADR-001 do core: runs operacionais e evidência científica são contratos separados; dataset freeze com hash | `ADR-001` (CORE) | reproducibility |
| 2026-08-11 | Fechamento de evidência para monografia: "maturidade inclui rejeitar abstrações" | TCC_EVIDENCE_CLOSURE (ECO) | research infrastructure → reflexão |
| 2026-08-21→26 | H11 refutada; auditoria matemática acha baseline contaminado (H13→H14); dossiê modelo vs mercado | trials.json, docs (BRAS) | evaluation problems / leakage |
| 2026-08-24 | Gate L0 live: HOLD; MARKET-02/03/04/06 encerrados; MARKET-05/A1 pré-registrado | docs e trials (BRAS) | false positives → caminho estrutural |
| 2026-08-31 | Core 3.0.0: 9 primitivas removidas por falta de 2º consumidor; auditoria estratégica dos 6 projetos: 17 hipóteses falsificadas, "ecosystem = maior ilusão de progresso" | tags CORE; zip 2026-08-31 (ECO) | reproducibility → disciplina de portfólio |
| 2026-09-03 | 20 decisões datadas (freeze cripto/stocks; EXP-001 histórico inviável; ecosystem não é produto); rotação concluída | decision_log (ECO) | governance |
| 2026-09-04→06 | H17–H19 pré-registradas; Core 3.2.0 (atestado exigido ao atualizar veredito) invalida atestado do Stocks; auditoria adversarial 2026-09-05 (7 achados; "engenharia > ciência") | harness_registry; CHANGELOG core; AUDITORIA_ADVERSARIAL | qualification (nasce da falha de reprodutibilidade) |
| 2026-09-07 | `cain` nasce (documentos recebidos e ADRs) | primeiro commit CAIN | research agents |
| 2026-09-11 | Core 3.2.1, ECO 0.2.0, BRAS 0.2.0, CAIN 0.4.5 publicados; revisão independente do CAIN ("síntese livre sem confiabilidade"); protocolo L0 | tags; REVISAO_INDEPENDENTE | evaluation of research agents |
| 2026-09-12/13 | Integrações Cripto/Brasileirão/Stocks/Core/Ops → CAIN com recibos; charter reconciliado para sete repositórios | *_INTEGRATION_*.md (ECO) | research infrastructure (2ª forma: artefatos, não serviço) |
| 2026-09-20 | Audit CAIN↔CRIPTO: 50 checks; HMAC fora do SQLite; três taxonomias (SUCCEEDED≠SUPPORTED≠edge) | audits/ (ECO) | governance of research agents |
| 2026-09-23 | `predictor-qualification` nasce (núcleo v2.0, prompts Rev 8) | primeiro commit QUAL | qualification (formal) |
| 2026-09-24→28 | Etapa A QUALIFIED nos três domínios; Envelope V2 (2.0.0rc2) e transporte (rc1→rc6); Etapa B QUALIFIED ×3; teste conjunto 47/57 → 58/58; CAIN_EXTREME adversarial | tags ECO/CAIN; attestations; RAW_LOGS | qualification + reproducibility + research agents |
| 2026-09-29/30 | Licenças proprietárias; versões rc novas; estudo "do zero" dos oito projetos (27 problemas); 3 attestations deixam de revalidar no main | commits; estudo-do-zero | reflexão/auditoria |
| 2026-10-02/03 | Renovação automática de atestados do cripto; ledger de maturidade do Stocks (H17–H19 reconferidos) | bot commit ECO; ledger QUAL | reproducibility |
| 2026-10-05/06 | Repositórios tornam-se privados; QUAL reaberto para provisionamento | fato informado | (exposição) |

## Veredito sobre a hipótese de linhagem

- **Sustentado:** prediction systems (jun/jul) → evaluation problems e false positives (jun–ago: viés pró-zebra, Kelly pré-custos, H5 direção oposta, baseline contaminado) → reproducibility/governance no core (ago–set: ADR-001, Trial Registry V2, atestado de poder, auditoria adversarial) → qualification formal (set 23+) → research agents e sua avaliação (CAIN, set 7+; L0; PROPOSE_ONLY; CAIN_EXTREME).
- **Ordem corrigida:** "research infrastructure" aparece **duas vezes**: uma primeira tentativa (agregador com gateway/db, jul–ago) foi invalidada e removida; a forma vigente (artefatos com hash, contratos, transporte por arquivos) só se consolida em set/2026. A linhagem não é linear: infraestrutura precede e sucede a qualificação.
- **Em paralelo, não em sequência:** CAIN (2026-09-07) começa **antes** da qualificação formal (2026-09-23); a qualificação nasce da falha de reprodutibilidade apontada em 2026-09-05 e passa a ter o CAIN como alvo das integrações.
- **Não sustentado como fato:** que o CAIN "decorre" das lições de avaliação. É plausível (os documentos do CAIN citam PROPOSE_ONLY, admissão do domínio, taxonomias separadas), mas é INFERENCE_ONLY sem um documento de motivação datado que ligue explicitamente os achados de avaliação ao desenho do CAIN. Registrar como pergunta para o proprietário.
- **Fora do escopo canônico, mas parte da história:** wc-predictor, cs, lol, f1, nba (jun–jul/2026) são a origem dos problemas de avaliação e do contrato temporal; só podem aparecer como "trabalhos anteriores" sem detalhe.

## Anterioridade

Toda a cronologia é `INTERNAL_TIMESTAMP_ONLY` (commits, tags, datas em texto). Tags com data: core 10 (2026-07-28 → 09-11), eco 14 (09-11 → 09-29), cain 10 (09-11 → 09-29), bras 6 (09-11 → 09-29). Nenhum `EXTERNAL_TIMESTAMP` encontrado. Para claims de anterioridade de pré-registros (H17–H19 em 2026-09-04; H14/H15 em 2026-08-26; MARKET-05 em 2026-08-24), a evidência atual é o commit que os registra; um carimbo externo futuro não altera o passado, mas pode ancorar o presente.
