# Linha de base — época `main` remoto (2026-09-30)

Segunda época do estudo, separada da [linha de base original](LINHA_DE_BASE.md) (raízes Windows, HEADs locais). As duas épocas **nunca se misturam**: cada conclusão do estudo cita a época e o SHA a que se refere. Esta linha de base foi tirada no clone Linux do `main` remoto de cada projeto presente no container de execução (`<EXEC_ROOT>/<projeto>`), com `.venv` de sessões anteriores. Esse clone é **cópia de execução**, não raiz forense: nenhuma afirmação aqui vale para os originais Windows.

Inspeção em 30/09/2026 (UTC nos registros). `origin/main` conferido por `git ls-remote` (estado `confirmado-remotamente`) e igual ao HEAD local em todos os oito projetos; árvores limpas (`git status --porcelain` vazio); sha256 de todos os arquivos rastreados em `../evidencias/epoca-main-20260930/baseline/<projeto>-hashes.json`.

## Identidades

| Projeto | HEAD = `main` remoto | HEAD da época original | Original é ancestral | HEAD == remoto | Versão `pyproject` | Rastreados | `git diff --shortstat` original→main |
|---|---|---|---|---|---|---|---|
| cain | abeb1e6011537bea2d8a0d87334780f8370f1cbd | 24f784c5dde1fa66c262ad5899f4fd8d02526adf | sim | sim | 0.4.13rc16 | 756 | 357 files changed, 61453 insertions(+), 1115 deletions(-) |
| brasileirao-predictor | 1e0c6f0b31e7cdc514190f08d5d2ff9689bd905d | f87806900d2aa3c5e267259a67f27ce56e18dc03 | sim | sim | 0.3.0rc6 | 2622 | 113 files changed, 13984 insertions(+), 207 deletions(-) |
| core-predictor | 956891ea728f8e1e038cbfebb7f0148abc77f700 | 9bf43efe92459a0b484cac00f51170b2c70d420f | sim | sim | 3.2.2 | 114 | 10 files changed, 105 insertions(+), 15 deletions(-) |
| cripto-predictor | 74113effcec7c0cf8deb8a8a46d413b6942368ce | 88158f25ab067ed34a845a52f3816e215addf486 | sim | sim | 1.2.0rc5 | 3417 | 132 files changed, 36747 insertions(+), 1179 deletions(-) |
| ecosystem-predictor | 0b0a09c8c60e470f83bc7e735f64e2e83ab1fb6d | a879525c49f1b3ac2050a3a70b10a322501b1e56 | sim | sim | 0.2.1 | 233 | 61 files changed, 7499 insertions(+), 281 deletions(-) |
| predictor-ops | 21cfcea55ee5c3049b406cac69998a265ea3f769 | b19e69527c0fda5cb1f96281d3a984fea1431768 | sim | sim | 4.2.2rc2 | 75 | 14 files changed, 217 insertions(+), 45 deletions(-) |
| predictor-qualification | 3ed750c53854573d0bab461393c67b30c52185af | f21bbbcccb06252cd5bc156c4093d571d03f0933 | sim | sim | (sem pyproject) | 7044 | 5763 files changed, 1128312 insertions(+), 689 deletions(-) |
| stocks-predictor | 3ec7e413bdcaedccfc1c2ed65c2822dddccb5cee | 5cf27f44f579cb40d8b873c0f10005360427a2d0 | sim | sim | 0.3.0rc4 | 1987 | 127 files changed, 27812 insertions(+), 25 deletions(-) |

Leitura: os oito HEADs estudados na época original são ancestrais diretos dos `main` atuais, logo o delta é só "o que entrou depois" (nenhuma reescrita de histórico observada). Isso **não** transfere as conclusões da época original para o `main`: cada arquivo do delta é uma leitura nova, e o estado de revisão de cada um está em `../evidencias/epoca-main-20260930/delta/<projeto>-delta-inventory.json` (campo `semantic_review`).

## Delta por classe de arquivo (original → main)

| Projeto | Arquivos | py-src/scripts | py-tests | qual-scripts | raw_logs | docs/md | data/text | ci/config | manifest/lock | other | A / M / D / R | Linhas (main) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| cain | 357 | 110 | 87 | 0 | 0 | 44 | 59 | 6 | 6 | 45 | A 279 / M 73 / D 4 / R 1 | 75834 |
| brasileirao-predictor | 113 | 25 | 28 | 0 | 0 | 20 | 19 | 5 | 2 | 14 | A 85 / M 28 / D 0 / R 0 | 20493 |
| core-predictor | 10 | 0 | 0 | 0 | 0 | 3 | 0 | 4 | 2 | 1 | A 3 / M 7 / D 0 / R 0 | 2025 |
| cripto-predictor | 132 | 28 | 21 | 10 | 0 | 20 | 25 | 4 | 2 | 22 | A 104 / M 24 / D 0 / R 4 | 43291 |
| ecosystem-predictor | 61 | 11 | 10 | 0 | 0 | 8 | 11 | 6 | 12 | 3 | A 42 / M 19 / D 0 / R 0 | 9439 |
| predictor-ops | 14 | 1 | 2 | 0 | 0 | 3 | 0 | 4 | 2 | 2 | A 4 / M 10 / D 0 / R 0 | 1812 |
| predictor-qualification | 5763 | 0 | 2 | 198 | 4956 | 106 | 425 | 13 | 6 | 57 | A 5733 / M 29 / D 0 / R 1 | 1229813 |
| stocks-predictor | 127 | 41 | 21 | 0 | 0 | 17 | 40 | 4 | 2 | 2 | A 113 / M 14 / D 0 / R 0 | 29913 |

A/M/D/R = adicionado / modificado / apagado / renomeado segundo `git diff --name-status`. "Linhas (main)" soma as linhas dos arquivos no `main` (arquivos apagados contam 0).

## O que foi feito nesta época

- Baseline: HEAD, branch, estado, remoto, versão, contagem e hashes de rastreados por projeto (`baseline/`).
- Delta: inventário com classe, sha256 no `main` e linhas para cada um dos arquivos do `git diff --name-status` (`delta/`).
- Verificadores do Anexo A6 executados onde o container permite (`runs/`, índice em `runs/INDEX.txt`); resultado e limites no [suplemento da época](SUPLEMENTO_EPOCA_MAIN_20260930.md).
- Wheels: 11 assets publicados baixados e conferidos por sha256 (`wheel-files-sha256.json`; bytes não versionados), METADATA confrontada com o README da tag e do `main` (`wheel-readme-metadata-check.json`), wheels construídas do `main` comparadas membro a membro com as publicadas (`built-vs-published-wheels.json`), registro `released_architecture.json` do ecosystem conferido contra os assets (`released-architecture-vs-assets.json`).
- Attestations da qualificação: `attest.py check` no commit de emissão e no `main` atual (`attestation-issuance-commits.json`, `runs/attest-check-*.log`).
- Revisão semântica: só nos deltas pequenos (ops, core, ecosystem V2/transport, adapters e contratos de pesquisa dos três domínios); o resto inventariado como `pendente-nova-epoca` — ver [cobertura por projeto](COBERTURA_POR_PROJETO.md).

## O que esta época não é

Não é preservação (os originais Windows não foram tocados nem reverificados), não é cleanroom (os `.venv` são de sessões anteriores e alguns editable), não é execução de suítes completas, harness econômicos, serviços, coleta, treino ou capital. Números de qualificação citados nos documentos de estado dos projetos (`docs/ESTADO_2026-09-30.md`) são ET-HIST: registrados por outra sessão, não reexecutados aqui.
