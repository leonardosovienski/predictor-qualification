# 02 — Inventário (Fase 1)

Projetos: ECO = `ecosystem-predictor-cain`; QUAL = `predictor-qualification`; CAIN; BRAS; CORE. STOCKS/CRIPTO/OPS só via QUAL (secundário). Destinos: REUSE só para conteúdo conceitual; nunca cópia literal.

| Projeto | Item | Camada | Destino | Evidence maturity | Verif. | Reconstr. | Evidence ID | Observação |
|---|---|---|---|---|---|---|---|---|
| ECO | `ECOSYSTEM_CHARTER.md` (4 eixos de estado, capital fail-closed, precedência de fontes, taxonomia de inconsistências) | PUBLIC (conceitual) | REUSE | DECLARED + IMPLEMENTED (contrato) | HIGH | LOW | EVID-ECO-007 | Reescrever; não copiar texto |
| ECO | `GLOSSARIO_STATUS.md` | PUBLIC (conceitual) | REBUILD_PUBLIC | DECLARED | HIGH | LOW | EVID-ECO-024 | Retirar exemplos internos |
| ECO | `src/ecosystem/contracts`, `registry` | PRIVATE | PRIVATE_ONLY | IMPLEMENTED (não reproduzido: pydantic offline) | MEDIUM | HIGH | EVID-ECO-003 | |
| ECO | `packages/research-*` (4 pacotes) | PRIVATE | PRIVATE_ONLY | REPRODUCED (310 testes) | HIGH | HIGH | EVID-ECO-003 | Publicar só o número + SHA |
| ECO | `SPEC_V2.md` + README do transporte (princípio: envelope não decide handler/budget/capital) | ILLUSTRATIVE | SANITIZE | IMPLEMENTED + REPRODUCED | HIGH | MEDIUM | EVID-ECO-020 | Revisão humana |
| ECO | 8 workflows CI | PUBLIC (fatos de definição) | SANITIZE | DECLARED | MEDIUM | LOW | EVID-ECO-006 | Runs: EXTERNAL_VALIDATION_REQUIRED |
| ECO | `ETAPA_B_INTEGRATED_STACK_20260928.md` | PUBLIC (agregado) | SANITIZE | EXERCISED (hashes conferidos em QUAL) | HIGH | MEDIUM | EVID-ECO-008, EVID-QUAL-002/003 | |
| ECO | `registries/harness_registry.json` + `docs/engineering_controls/**` | PUBLIC (agregado) | SANITIZE | EXERCISED (10/10 hashes) | HIGH | MEDIUM | EVID-ECO-009/027 | Escopo: controle sintético dos julgadores |
| ECO | `evidence_registry.json`, `decision_log.json` (20 decisões datadas) | PUBLIC (seleção) | SANITIZE | DECLARED | HIGH | LOW–MEDIUM | EVID-ECO-011/018 | Números exigem fonte primária |
| ECO | zip `docs/audit-2026-08-31` → FALSIFIED_HYPOTHESES, PORTFOLIO_DECISION, KILL_CRITERIA | PUBLIC (agregado) | SANITIZE | DECLARED | HIGH | LOW | EVID-ECO-011/015 | |
| ECO | mesmo zip → 6 `.patch` | PRIVATE | PRIVATE_ONLY | N/A | LOW | HIGH | EVID-ECO-015 | Exposto publicamente até 2026-10-05 |
| ECO | `registries/commercial_discovery.json` (PII de 10 terceiros) | PRIVATE | PRIVATE_ONLY | N/A | LOW | N/A | EVID-ECO-013 | Exposto publicamente até 2026-10-05 |
| ECO | `economics_registry.json`, `canonical_checkpoints.json`, `commercial_discovery` (gates B0/E0, receita 0) | PUBLIC (agregado, sem contatos) | SANITIZE | DECLARED | MEDIUM | LOW | EVID-ECO-018 | |
| ECO | `VEREDITOS_2026-07-26.md` | PUBLIC (agregado) | SANITIZE | DECLARED | HIGH | LOW | EVID-ECO-023 | Inclui repos fora do escopo |
| ECO | `TCC_EVIDENCE_CLOSURE.md` | PUBLIC (trajetória) | SANITIZE | DECLARED | MEDIUM | LOW | EVID-ECO-025 | |
| ECO | `audits/cain-cripto-20260920/**` | PUBLIC agregado / PRIVATE mecanismos | SANITIZE | DECLARED (recibos) | HIGH | MEDIUM–HIGH | EVID-ECO-017 | Discrepância de contagem |
| ECO | `evidence/**`, `docs/core_integration_20260913/**` | PUBLIC (agregado) | SANITIZE | EXERCISED (recibos) | MEDIUM | LOW–MEDIUM | EVID-ECO-019 | Caminhos locais |
| ECO | `SECURITY_INCIDENT_SECRET_ROTATION.md`, `.gitleaksignore`, `RUNBOOK_SECRET_INCIDENT.md` | PRIVATE | PRIVATE_ONLY | HISTORICAL | LOW | LOW | EVID-ECO-012 | Lição pública genérica possível |
| ECO | histórico Git: `src/ecosystem/{gateway,scheduler,db,storage,cache,telemetry}`, `migrations`, `docker`, `compose.yaml` (34 arquivos removidos) | PRIVATE | OBSOLETE | HISTORICAL | LOW | MEDIUM | EVID-ECO-021 | Público até 2026-10-05 |
| ECO | `PREDICTOR_CORE_BLUEPRINT.md`, `FINAL_*`, `FECHAMENTO_*`, `CODEX_*`, `HANDOFF*`, `HEALTH_TASKS.json`, `ecosystem_health.ps1`, `.env.example` | PRIVATE | OBSOLETE | DECLARED | LOW | LOW–MEDIUM | EVID-ECO-010/014 | |
| ECO | `.ci/cain-supply/overlay.zip` | PRIVATE | PRIVATE_ONLY | N/A | LOW | HIGH | EVID-ECO-016 | |
| ECO | `LICENSE` proprietário (2026-09-29) | PUBLIC (fato) | REUSE | PROVEN | MEDIUM | LOW | EVID-ECO-022 | |
| ECO | `compat/` lock conjunta (12 pacotes do stack) | PRIVATE | PRIVATE_ONLY | DECLARED | MEDIUM | MEDIUM | EVID-ECO-006 | |
| QUAL | `qualification/*/QUALIFICATION_ATTESTATION.json` (6 vigentes, 19 superseded) | PUBLIC (agregado: resultado, contagens, hashes) | SANITIZE | EXERCISED (hashes conferidos) | HIGH | MEDIUM | EVID-QUAL-002 | Campos de ambiente/caminhos: privados |
| QUAL | `RAW_LOGS/**` (2.435 logs; 238 MB) | PRIVATE | PRIVATE_ONLY | EXERCISED | HIGH | HIGH | EVID-QUAL-003 | Base dos números; nunca publicar bruto |
| QUAL | `ledger/stocks-predictor.yaml` (escala DECLARED→PROVEN) | PUBLIC (conceito da escala) / PRIVATE (conteúdo) | SANITIZE | DECLARED | HIGH | MEDIUM | EVID-QUAL-004 | Confirma hipóteses do protocolo |
| QUAL | `qualification_inventory.py` | PRIVATE | PRIVATE_ONLY | IMPLEMENTED | LOW | LOW | EVID-QUAL-005 | Cobre só DECLARED→IMPLEMENTED por heurística |
| QUAL | `estudo-do-zero/relatorios/*` (inventários, matrizes, problemas priorizados) | PUBLIC (achados agregados) | SANITIZE | DECLARED/EXERCISED | HIGH | MEDIUM | EVID-QUAL-006/007 | |
| QUAL | `estudo-do-zero/evidencias/{cain,stocks-predictor}/source-text.txt` + `source-index.json` | PRIVATE (código integral) | PRIVATE_ONLY | N/A | LOW | HIGH | EVID-QUAL-008 | **HIGH_PRIORITY_EXPOSURE_REVIEW** |
| QUAL | `estudo-do-zero/evidencias/cripto-predictor/shared-archive-*-review.md` (revisão de 773 objetos do arquivo histórico) | PRIVATE | PRIVATE_ONLY | N/A | LOW | MEDIUM–HIGH | EVID-QUAL-009 | |
| QUAL | `qualification/shared/CAIN_EXTREME_20260928/REPORT.md` | PUBLIC (agregado) | SANITIZE | EXERCISED | HIGH | MEDIUM | EVID-QUAL-010 | |
| QUAL | `qualification/COMMON_QUALIFICATION_CORE.md`, `ATTESTATION_SCHEMA.json`, `DECISIONS.json` (28 APPROVED) | PRIVATE (mecanismo) | PRIVATE_ONLY | DECLARED | MEDIUM | HIGH | EVID-QUAL-011 | Princípios podem virar texto ilustrativo |
| QUAL | `CLAUDE.md` ("repos públicos"; caminhos Windows) | PRIVATE | PRIVATE_ONLY | DECLARED | LOW | LOW | EVID-QUAL-001 | Pressupõe repos públicos: revisar |
| CAIN | `docs/ORCHESTRATION_V2.md` (proposta → DecisionPolicy determinística → task → spool → resultado → memória bitemporal) | ILLUSTRATIVE | SANITIZE | IMPLEMENTED (não reproduzido aqui) | HIGH | MEDIUM–HIGH | EVID-CAIN-002 | Só fluxo abstrato; sem comandos, decisões, regras |
| CAIN | `src/cain/orchestration/*` (política, outbox, inbox, egress/sandbox policy) | PRIVATE | PRIVATE_ONLY | IMPLEMENTED | MEDIUM | HIGH | EVID-CAIN-003 | |
| CAIN | `evaluation/*` (protocolo L0 com parâmetros fixados antes, revisão independente, orçamento de evidência, abstenção) | PUBLIC (conceito) | SANITIZE | EXERCISED (recibos JSON) | HIGH | MEDIUM | EVID-CAIN-004 | |
| CAIN | `docs/ESTADO_2026-09-30.md`, `ESTADO_DO_PROJETO.md` | PRIVATE | OBSOLETE/SANITIZE | DECLARED | MEDIUM | MEDIUM | EVID-CAIN-001 | Caminhos locais |
| BRAS | `docs/AUDITORIA_ADVERSARIAL_2026-09-05.md` (7 achados; "engenharia > ciência"; adendos) | PUBLIC (agregado) | SANITIZE | EXERCISED | HIGH | LOW–MEDIUM | EVID-BRAS-002 | Alto valor de autocrítica |
| BRAS | `data/trials.json` (29 trials, statuses) | PUBLIC (contagens) | SANITIZE | EXERCISED | HIGH | MEDIUM | EVID-BRAS-003 | Sem parâmetros |
| BRAS | `docs/EVIDENCE_REGISTRY.md` (CLAIM-BR-MARKET-001/002/003 BLOCKED_PENDING_PIT_FEATURES) | PUBLIC (agregado) | SANITIZE | DECLARED | HIGH | LOW | EVID-BRAS-004 | |
| BRAS | `research_runtime/execution.py` (ResearchExecutor) | PRIVATE | PRIVATE_ONLY | IMPLEMENTED | LOW | HIGH | EVID-BRAS-005 | Fato: duplicado em 3 domínios |
| CORE | `CHANGELOG.md` (3.2.0 fecha achados da auditoria adversarial; mudança de contrato documentada) | PUBLIC (agregado) | SANITIZE | DECLARED | HIGH | LOW | EVID-CORE-002 | |
| CORE | tags `v3.2.1`=`7bb212c` (2026-09-11) e demais | PUBLIC (fato) | REUSE | PROVEN | HIGH | LOW | EVID-CORE-001 | |
| CORE | `src/predictor_core/*`, `tests` (255 funções) | PRIVATE | PRIVATE_ONLY | IMPLEMENTED (não reproduzido: metadata ausente offline) | MEDIUM | HIGH | EVID-CORE-003 | |
| STOCKS (via QUAL) | lacres H17–H19, EconomicRebalanceGate, R8 | ver 05/07 | SANITIZE/NEEDS_EVIDENCE | DECLARED (secundário) | MEDIUM | MEDIUM | EVID-QUAL-004/007 | BLOCKED_LOCAL_REPO_MISSING |
| CRIPTO (via QUAL) | arquivo histórico 773 objetos; H1–H6; V1.2 reabertura | ver 05/06 | NEEDS_EVIDENCE | DECLARED (secundário) | MEDIUM | — | EVID-QUAL-006/009 | BLOCKED (clone negado) |
| OPS (via QUAL/ECO) | runner, provenance, kill-switch; CORE-02/OPS-05 achados | ver 05 | NEEDS_EVIDENCE | DECLARED (secundário) | MEDIUM | — | EVID-QUAL-007 | BLOCKED_LOCAL_REPO_MISSING |
