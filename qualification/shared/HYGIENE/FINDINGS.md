# Fase 0 — achados fora do escopo dos itens

Severidade conforme C6 do núcleo. Nenhum destes achados vale como veredito de qualificação.

| ID | Sev. | Status | Achado | Evidência |
|---|---|---|---|---|
| HF-001 | P2 | OPEN | Os hashes de `predictor-research-{protocol,snapshot,bundle}` registrados em `ecosystem-predictor/audits/cain-cripto-20260920/STACK_MANIFEST.json` (e fixados em `.github/workflows/cain-crypto-integration.yml`) vêm de builds feitos em árvore de trabalho Windows com fim de linha misto e não se reproduzem a partir do git. As releases rc publicadas usam o build LF canônico (D-14). O conteúdo com EOL normalizado é idêntico, mas os hashes diferem do manifesto auditado. Causa de fundo: o Ecosystem não força `eol=lf` para `packages/**`, então qualquer build num checkout Windows com `autocrlf=true` gera outro hash. | `HYG-001.md`, `RAW_LOGS/HYG-001_repro_investigation.log` |
| HF-002 | P2 | OPEN | As releases rc foram criadas com `immutable=false`. A imutabilidade nativa de releases do GitHub é uma configuração do repositório, que fica a critério do dono. Até lá, a imutabilidade é procedimental (C5: nunca sobrescrever asset). | `RAW_LOGS/HYG-001_download_verify.log` |
| HF-003 | P2 | OPEN | O `brasileirao-predictor` não faz checkout no Windows sem `core.longpaths=true`: há caminhos longos em `docs/continuation/publication_2026-09-10/evidence/ci-*/extracted/...`. Contorno aplicado só na config local do clone de qualificação. | `RAW_LOGS/HYG-011_006_clone.log` |
| HF-004 | P2 | OPEN — decisão do dono | 17 objetos git soltos e não referenciados (os blobs dos próprios arquivos sujos + 2 trees) apareceram em `C:\CAIN\projeto\.git\objects` às 03:41:42Z, durante a preservação. Causa provável: o harness da sessão do agente depois de um `cd` para o diretório. Não apagados. Refs, index, HEAD e arquivos inalterados. | `HYG-005.md`, `RAW_LOGS/HYG-005_preserve.log` |
| HF-005 | P2 | OPEN | O `HYGIENE.json` descreve o checkout do CAIN como "`24f784c` + 14 caminhos"; o estado observado tem 17 (10 modificados + 7 não rastreados). Os 17 foram preservados. | `HYG-005.md` |
