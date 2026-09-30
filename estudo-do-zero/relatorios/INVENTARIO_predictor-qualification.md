# Inventário — predictor-qualification

Fonte: C:\QUALIFICACAO\predictor-qualification, HEAD f21bbbcccb06252cd5bc156c4093d571d03f0933. Branch main, árvore limpa na linha de base. main remoto é outra identidade; conferir LINHA_DE_BASE. Toda caracterização preliminar está congelada em PRELIMINAR_predictor-qualification.md. Este inventário não transfere seus atestados para os sete checkouts locais examinados.

## A–D. Propósito, estrutura, tecnologia e interfaces

OD: coleção de executores de investigação/qualificação e registros públicos. Sem manifest raiz installável na listagem rastreada. Seus entrypoints são arquivos scripts: coleta baseline, truth_map, check/build attestation, cleanroom, E2E/science/soak e sondas Ops. Python stdlib, jsonschema no validador, bibliotecas dos domínios/Core/Ops no runtime; Git, gh, curl, uv e Bash nos executores. PowerShell keep_awake mantém execução Windows acordada por processo. O diretório qualification/<domínio> é organização de evidência, não serviço de pesquisa.

Pontos de leitura: qualification/shared/scripts/collect_stack_baseline.py (collect_repo e verify_stack_wheels), cleanroom_baseline.py (Log/main/wheel_digest), qualification/crypto/scripts/attest.py (build/check/write), evidence_numbers.py (main/junit), runtime_cleanroom.sh e d16_linux.sh; outros scripts têm índice de símbolos em source-index.json. Não foram invocados comandos encontrados nesses documentos.

## E–F. Configuração e persistência

OD: cleanroom usa plano JSON com repo/sha/wheels/hashes/suites/limits; usa CLEANROOM_UV, RUNNER_TEMP, UV_* e CLEANROOM_GUARD_*. Scripts Windows usam caminhos absolutos C:/QUALIFICACAO/tools, C:/Cripto/qualificacao, inclusive caches fora de cwd. Não devem ser executados indiscriminadamente nem mesmo após clone. d16_linux lê DECISIONS e runtime_target; exige APPROVED. build_real_dataset baixa publicamente data.binance.vision, confere checksum e grava raw/MANIFEST/datasets fora do repo. Não houve download de datasets nesta investigação.

Persistência de evidência: JSON/JSONL/XML/log, hashes, Git e artefatos do Actions. DDL próprio não encontrado no espaço de 22 Python, 13 shell/PowerShell e 6 workflows; scripts E2E/soak abrem SQLite do domínio produzido em ambiente de teste. Nenhum banco original foi aberto nesta investigação. real_env preserva bytes dos datasets mediante MANIFEST e CAS e deriva vetores de futuro, disponibilidade inválida e direção aleatória.

## G–H. Lógica e fluxos

Fluxo baseline: configuração de raízes → Git/manifests/lock → API CI/releases → cruzamento lock/hash asset → JSON/log. A coleta usa refs locais e deve ser distinguida da consulta main remota; o script original não faz essa distinção do modo exigido por este estudo.

Fluxo cleanroom: plano congelado → clone do commit → lock/export → download de wheel → duas instalações independentes published/head_build → introspecção módulos/plugin/script → testes em árvore sem diretório pacote → fatos/JUnit/guard → comparação da wheel. Observação: guard apenas grava origens, não torna a suíte vermelha ao achar módulo externo; o consumidor precisa aplicar gate. clone, instalações, rmtree e git clean fazem deste executor mutável. Não o executamos integralmente.

Fluxo atestado: GATES e FINDINGS → hashes e contagens → schema + regras parciais → JSON novo. check reconta P0/P1/P2 atuais e hashes dos gates; não confirma sozinho releases, todos ambientes, contratos domínio, supersession ou semântica científica. Relação hash correta prova identidade, não verdade do conteúdo.

Fluxo Crypto runtime: runtime_target → wheel/hash/deps → CLI instalada → request → admission/journal/Core/Ops/effect/result → reinício/show → conferência de hashes e IDs. science_real usa controles negativos; separated_with_ci só verifica dois limites inferiores não nulos. A presença de limites superiores coerentes não está testada por esse predicado. d16_finalize confere strings de identidade em env.log e valores de JSON; não torna os JSONs prova independente de experimento. Conformance JUnit considera só primeira suite quando testsuites, não exige explicitamente tests>0; risco de aceitar fixture vazia/multissuíte não ensaiado nesta sessão.

soak.py implementa 20 ciclos normais, 5 duplicatas, 5 restarts e falhas/retries, mas o perfil JSON lista morte do host Ops e corrupção de resultado como classes próprias. A leitura do harness examinado não encontrou execução explícita dessas duas classes no soak.py; elas podem existir em suítes separadas. Isso é divergência de cobertura do harness, não prova de ausência no stack. Ver stdout/exit do domínio e logs: shells set -uo pipefail sem -e continuam após alguns erros e podem concluir com exit0 mesmo com evidência de subcomando falho.

## I–J. Testes e operação

ET-RUN: em clone --no-hardlinks independente, evidence_numbers.py terminou exit0 e gerou JSON semanticamente igual ao original. É recomputação de logs antigos; não executou as milhares de asserções históricas que resumiu. Falhas históricas anteriores permanecem no arquivo gerado (ex.: baseline com quatro falhas e execução de método corrigida). attest.py check terminou exit1 por ModuleNotFoundError jsonschema; checagem oficial NV. Sem instalação de dependências.

ET-RUN: a comparação inicial contra a árvore atual encontrou 12 referências divergentes, sem transformação da cópia. A investigação de proveniência verificou Git blobs nos commits de emissão: final em 800d4d1211b439144d48138bed629a826ef21295 tem 94/94 referências corretas; parcial V1.1 em ed5375d57984cae44f052775d4a525d11c9704b1 tem 100/100. O final primário é NOT_QUALIFIED; o parcial é IN_PROGRESS. As diferenças posteriores são de época e não invalidam a emissão por si mesmas. Não foi reexecutado o validador oficial completo, limitado por dependências. Evidências: attestation-issuance-check.json, issuance-ATTESTATION_PARTIAL_v1-1-attestation.json, hash-mismatch-original-check.json.

OD workflows: contents:read; runtime e matriz usam uv0.12.1 e Python3.13; provision script fixa uv0.12.18. cleanroom lê uv do plano. CI inclui upload-artifact, triggers por paths e workflow_dispatch, matrizes Linux/Windows, limites de duração. Metadados atuais consultados anonimamente em ci-head-local.json e ci-main-remoto.json; não confundir execução API remota com ET-RUN. Não acionamos Actions.

## K–L. Confronto e artefatos em uso

DD README declara evidência pré-treinamento e ausência de código de produção: concorda com scripts diagnósticos observados. Núcleo promete qualificação confiável e enums/regras de autoridade: existe implementação parcial nos scripts, mas a validade financeira e científica não decorre dos gates. DD núcleo C7.1 possui oito regras; attest.check implementa subconjunto, como docstring admite. C24/Etapa B/V2 são narrativa nesta fonte local, sem diretório integration executável examinado. GATES/FINDINGS/atestado/RAW_LOGS são registros a contextualizar, não oráculo.

Anexo A: papel geral é compatível; datas/versões/requalificações atuais não podem ser confirmadas por esta árvore anterior. DECISIONS local contém D-1..D-15 e D-17, sem D-16 aprovada e sem D-27/D-29/30/31 na lista lida. Busca delimitada a campo decision_id dos registros atuais deste arquivo; main remoto não foi baixado nem estudado em conteúdo. Não atribuir ausência ao servidor remoto. Fontes instaladas e serviços ativos NV: não importados nem consultados.

## Cobertura e limites

Código próprio executável: 22 Python, 12 shell e 1 PowerShell, seis workflows lidos integralmente e revisados por responsabilidade/efeitos/configuração/erros. Índice e coverage por arquivo estão em evidencias/predictor-qualification. Schema, core de governança, DECISIONS, GATES/FINDINGS, final e parcial selecionado, parâmetros/perfil/matriz de autoridade lidos. Histórico repetitivo catalogado, aprofundado apenas quando sustenta recomputação. Não há teste de domínio real, instalação cleanroom, Linux primário, acesso dados privados, prova financeira, ou implantação observada. Integração V2 remota e ciclo D27 permanecem fora do conteúdo local estudado.


## Épocas remotas observadas

Os manifests do main remoto e os assets do Anexo foram verificados separadamente, por SHA/versão. Veja [confronto do Anexo](CONFRONTO_ANEXO_REMOTO.md). Essas identidades não ampliam automaticamente a cobertura semântica da raiz primária nem provam integração runtime.
