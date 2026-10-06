# Identidades de pacotes e CI

Estas são identidades das fontes primárias locais da linha de base. Versões instaladas/serviços ativos são NV. Releases e main remoto são consultas independentes.

| Projeto | Manifest | Python | Lock | Release local correspondente | README da wheel igual ao local |
|---|---|---|---|---|---|
| brasileirao-predictor | 0.2.0 | >=3.13,<3.15 | observado | tag/release observada; asset observado | False |
| cain | 0.4.12 | >=3.11 | não encontrado na raiz examinada | não publicada (sem tag correspondente na consulta) | NV sem asset |
| core-predictor | 3.2.1 | >=3.13 | observado | tag/release observada; asset observado | False |
| cripto-predictor | 1.1.1rc4 | >=3.13,<3.15 | observado | não publicada (sem tag correspondente na consulta) | NV sem asset |
| ecosystem-predictor | 0.2.0 | >=3.13,<3.15 | observado | tag/release observada; asset observado | False |
| predictor-ops | 4.2.1 | >=3.13 | observado | tag/release observada; asset observado | False |
| stocks-predictor | 0.2.0 | >=3.13,<3.15 | observado | tag/release observada; asset observado | False |

Cada asset possui URL, digest API, SHA256 calculado do download e versão METADATA em release-identity.json. Comparação README normaliza LF/CRLF e rstrip; divergência remanescente é conteúdo textual. Manifest do protocolo local não declara readme: igualdade NV, mesmo com asset existente. A ausência de uma tag/asset é limitada à consulta das refs e primeiras 100 releases.

Dependências do stack: veja package-chain.json (requirement, uv_source, lock_version, lock_source e URL/hash de cada wheel). Caminho declarado não prova biblioteca instalada. Crypto tem protocol declarado sem pacote correspondente no lock; CAIN não tem uv.lock na raiz rastreada. Estes são bloqueios de reprodutibilidade dos checkouts estudados.

Pins de terceiros diferentes: third-party-different-pins.json. Essa comparação não considera resolução de markers/extras e não prova insatisfatibilidade. compat/ remoto descrito no anexo não foi executado.

## CI consultado remotamente

| Projeto | Época | Run | Commit | Status | Conclusão | URL |
|---|---|---|---|---|---|---|
| brasileirao-predictor | ci-head-local | 34818565665 | f87806900d2aa3c5e267259a67f27ce56e18dc03 | completed | success | https://github.com/leonardosovienski/brasileirao-predictor/actions/runs/34818565665 |
| brasileirao-predictor | ci-head-local | 34817074000 | f87806900d2aa3c5e267259a67f27ce56e18dc03 | completed | success | https://github.com/leonardosovienski/brasileirao-predictor/actions/runs/34817074000 |
| brasileirao-predictor | ci-head-local | 34816773315 | f87806900d2aa3c5e267259a67f27ce56e18dc03 | completed | success | https://github.com/leonardosovienski/brasileirao-predictor/actions/runs/34816773315 |
| brasileirao-predictor | ci-head-local | 34739909356 | f87806900d2aa3c5e267259a67f27ce56e18dc03 | completed | success | https://github.com/leonardosovienski/brasileirao-predictor/actions/runs/34739909356 |
| brasileirao-predictor | ci-head-local | 34739909340 | f87806900d2aa3c5e267259a67f27ce56e18dc03 | completed | success | https://github.com/leonardosovienski/brasileirao-predictor/actions/runs/34739909340 |
| brasileirao-predictor | ci-head-local | 34739909348 | f87806900d2aa3c5e267259a67f27ce56e18dc03 | completed | success | https://github.com/leonardosovienski/brasileirao-predictor/actions/runs/34739909348 |
| brasileirao-predictor | ci-main-remoto | 36723785428 | 1e0c6f0b31e7cdc514190f08d5d2ff9689bd905d | completed | success | https://github.com/leonardosovienski/brasileirao-predictor/actions/runs/36723785428 |
| brasileirao-predictor | ci-main-remoto | 36722537039 | 1e0c6f0b31e7cdc514190f08d5d2ff9689bd905d | completed | success | https://github.com/leonardosovienski/brasileirao-predictor/actions/runs/36722537039 |
| brasileirao-predictor | ci-main-remoto | 36722537026 | 1e0c6f0b31e7cdc514190f08d5d2ff9689bd905d | completed | success | https://github.com/leonardosovienski/brasileirao-predictor/actions/runs/36722537026 |
| cain | ci-head-local | 34909056885 | 24f784c5dde1fa66c262ad5899f4fd8d02526adf | completed | success | https://github.com/leonardosovienski/cain/actions/runs/34909056885 |
| cain | ci-head-local | 34895204883 | 24f784c5dde1fa66c262ad5899f4fd8d02526adf | completed | success | https://github.com/leonardosovienski/cain/actions/runs/34895204883 |
| cain | ci-main-remoto | 36723814637 | abeb1e6011537bea2d8a0d87334780f8370f1cbd | completed | success | https://github.com/leonardosovienski/cain/actions/runs/36723814637 |
| cain | ci-main-remoto | 36723777371 | abeb1e6011537bea2d8a0d87334780f8370f1cbd | completed | success | https://github.com/leonardosovienski/cain/actions/runs/36723777371 |
| cain | ci-main-remoto | 36723776989 | abeb1e6011537bea2d8a0d87334780f8370f1cbd | completed | success | https://github.com/leonardosovienski/cain/actions/runs/36723776989 |
| core-predictor | ci-head-local | 35645909672 | 9bf43efe92459a0b484cac00f51170b2c70d420f | completed | success | https://github.com/leonardosovienski/core-predictor/actions/runs/35645909672 |
| core-predictor | ci-head-local | 35598622376 | 9bf43efe92459a0b484cac00f51170b2c70d420f | completed | success | https://github.com/leonardosovienski/core-predictor/actions/runs/35598622376 |
| core-predictor | ci-head-local | 35597963425 | 9bf43efe92459a0b484cac00f51170b2c70d420f | completed | success | https://github.com/leonardosovienski/core-predictor/actions/runs/35597963425 |
| core-predictor | ci-head-local | 34887852941 | 9bf43efe92459a0b484cac00f51170b2c70d420f | completed | success | https://github.com/leonardosovienski/core-predictor/actions/runs/34887852941 |
| core-predictor | ci-head-local | 34842561269 | 9bf43efe92459a0b484cac00f51170b2c70d420f | completed | success | https://github.com/leonardosovienski/core-predictor/actions/runs/34842561269 |
| core-predictor | ci-head-local | 34841990230 | 9bf43efe92459a0b484cac00f51170b2c70d420f | completed | success | https://github.com/leonardosovienski/core-predictor/actions/runs/34841990230 |
| core-predictor | ci-head-local | 34740848667 | 9bf43efe92459a0b484cac00f51170b2c70d420f | completed | success | https://github.com/leonardosovienski/core-predictor/actions/runs/34740848667 |
| core-predictor | ci-head-local | 34740848668 | 9bf43efe92459a0b484cac00f51170b2c70d420f | completed | success | https://github.com/leonardosovienski/core-predictor/actions/runs/34740848668 |
| core-predictor | ci-head-local | 34740848559 | 9bf43efe92459a0b484cac00f51170b2c70d420f | completed | success | https://github.com/leonardosovienski/core-predictor/actions/runs/34740848559 |
| core-predictor | ci-main-remoto | 36723794389 | 956891ea728f8e1e038cbfebb7f0148abc77f700 | completed | success | https://github.com/leonardosovienski/core-predictor/actions/runs/36723794389 |
| core-predictor | ci-main-remoto | 36722552556 | 956891ea728f8e1e038cbfebb7f0148abc77f700 | completed | success | https://github.com/leonardosovienski/core-predictor/actions/runs/36722552556 |
| core-predictor | ci-main-remoto | 36722547831 | 956891ea728f8e1e038cbfebb7f0148abc77f700 | completed | success | https://github.com/leonardosovienski/core-predictor/actions/runs/36722547831 |
| core-predictor | ci-main-remoto | 36722547756 | 956891ea728f8e1e038cbfebb7f0148abc77f700 | completed | success | https://github.com/leonardosovienski/core-predictor/actions/runs/36722547756 |
| cripto-predictor | ci-head-local | 35600509755 | 88158f25ab067ed34a845a52f3816e215addf486 | completed | success | https://github.com/leonardosovienski/cripto-predictor/actions/runs/35600509755 |
| cripto-predictor | ci-head-local | 35598623427 | 88158f25ab067ed34a845a52f3816e215addf486 | completed | success | https://github.com/leonardosovienski/cripto-predictor/actions/runs/35598623427 |
| cripto-predictor | ci-head-local | 35598184706 | 88158f25ab067ed34a845a52f3816e215addf486 | completed | failure | https://github.com/leonardosovienski/cripto-predictor/actions/runs/35598184706 |
| cripto-predictor | ci-head-local | 35565341264 | 88158f25ab067ed34a845a52f3816e215addf486 | completed | failure | https://github.com/leonardosovienski/cripto-predictor/actions/runs/35565341264 |
| cripto-predictor | ci-head-local | 35565341315 | 88158f25ab067ed34a845a52f3816e215addf486 | completed | failure | https://github.com/leonardosovienski/cripto-predictor/actions/runs/35565341315 |
| cripto-predictor | ci-main-remoto | 36723810026 | 74113effcec7c0cf8deb8a8a46d413b6942368ce | completed | success | https://github.com/leonardosovienski/cripto-predictor/actions/runs/36723810026 |
| cripto-predictor | ci-main-remoto | 36723770475 | 74113effcec7c0cf8deb8a8a46d413b6942368ce | completed | success | https://github.com/leonardosovienski/cripto-predictor/actions/runs/36723770475 |
| ecosystem-predictor | ci-head-local | 35817818948 | a879525c49f1b3ac2050a3a70b10a322501b1e56 | completed | success | https://github.com/leonardosovienski/ecosystem-predictor/actions/runs/35817818948 |
| ecosystem-predictor | ci-head-local | 35817814007 | a879525c49f1b3ac2050a3a70b10a322501b1e56 | completed | success | https://github.com/leonardosovienski/ecosystem-predictor/actions/runs/35817814007 |
| ecosystem-predictor | ci-head-local | 35817811133 | a879525c49f1b3ac2050a3a70b10a322501b1e56 | completed | success | https://github.com/leonardosovienski/ecosystem-predictor/actions/runs/35817811133 |
| ecosystem-predictor | ci-head-local | 35722286775 | a879525c49f1b3ac2050a3a70b10a322501b1e56 | completed | success | https://github.com/leonardosovienski/ecosystem-predictor/actions/runs/35722286775 |
| ecosystem-predictor | ci-head-local | 35601356940 | a879525c49f1b3ac2050a3a70b10a322501b1e56 | completed | success | https://github.com/leonardosovienski/ecosystem-predictor/actions/runs/35601356940 |
| ecosystem-predictor | ci-head-local | 35555412836 | a879525c49f1b3ac2050a3a70b10a322501b1e56 | completed | success | https://github.com/leonardosovienski/ecosystem-predictor/actions/runs/35555412836 |
| ecosystem-predictor | ci-head-local | 35555412792 | a879525c49f1b3ac2050a3a70b10a322501b1e56 | completed | success | https://github.com/leonardosovienski/ecosystem-predictor/actions/runs/35555412792 |
| ecosystem-predictor | ci-main-remoto | 36723789504 | 0b0a09c8c60e470f83bc7e735f64e2e83ab1fb6d | completed | success | https://github.com/leonardosovienski/ecosystem-predictor/actions/runs/36723789504 |
| ecosystem-predictor | ci-main-remoto | 36722543322 | 0b0a09c8c60e470f83bc7e735f64e2e83ab1fb6d | completed | success | https://github.com/leonardosovienski/ecosystem-predictor/actions/runs/36722543322 |
| ecosystem-predictor | ci-main-remoto | 36722542990 | 0b0a09c8c60e470f83bc7e735f64e2e83ab1fb6d | completed | success | https://github.com/leonardosovienski/ecosystem-predictor/actions/runs/36722542990 |
| predictor-ops | ci-head-local | 35821939095 | b19e69527c0fda5cb1f96281d3a984fea1431768 | completed | success | https://github.com/leonardosovienski/predictor-ops/actions/runs/35821939095 |
| predictor-ops | ci-head-local | 35600509978 | b19e69527c0fda5cb1f96281d3a984fea1431768 | completed | success | https://github.com/leonardosovienski/predictor-ops/actions/runs/35600509978 |
| predictor-ops | ci-head-local | 35598623442 | b19e69527c0fda5cb1f96281d3a984fea1431768 | completed | success | https://github.com/leonardosovienski/predictor-ops/actions/runs/35598623442 |
| predictor-ops | ci-head-local | 35597947578 | b19e69527c0fda5cb1f96281d3a984fea1431768 | completed | success | https://github.com/leonardosovienski/predictor-ops/actions/runs/35597947578 |
| predictor-ops | ci-head-local | 35307402645 | b19e69527c0fda5cb1f96281d3a984fea1431768 | completed | success | https://github.com/leonardosovienski/predictor-ops/actions/runs/35307402645 |
| predictor-ops | ci-head-local | 34844358155 | b19e69527c0fda5cb1f96281d3a984fea1431768 | completed | success | https://github.com/leonardosovienski/predictor-ops/actions/runs/34844358155 |
| predictor-ops | ci-head-local | 34842537432 | b19e69527c0fda5cb1f96281d3a984fea1431768 | completed | success | https://github.com/leonardosovienski/predictor-ops/actions/runs/34842537432 |
| predictor-ops | ci-head-local | 34842040310 | b19e69527c0fda5cb1f96281d3a984fea1431768 | completed | success | https://github.com/leonardosovienski/predictor-ops/actions/runs/34842040310 |
| predictor-ops | ci-head-local | 34740109319 | b19e69527c0fda5cb1f96281d3a984fea1431768 | completed | success | https://github.com/leonardosovienski/predictor-ops/actions/runs/34740109319 |
| predictor-ops | ci-head-local | 34740108765 | b19e69527c0fda5cb1f96281d3a984fea1431768 | completed | success | https://github.com/leonardosovienski/predictor-ops/actions/runs/34740108765 |
| predictor-ops | ci-main-remoto | 36723776858 | 21cfcea55ee5c3049b406cac69998a265ea3f769 | completed | success | https://github.com/leonardosovienski/predictor-ops/actions/runs/36723776858 |
| predictor-ops | ci-main-remoto | 36722537408 | 21cfcea55ee5c3049b406cac69998a265ea3f769 | completed | success | https://github.com/leonardosovienski/predictor-ops/actions/runs/36722537408 |
| predictor-ops | ci-main-remoto | 36722531151 | 21cfcea55ee5c3049b406cac69998a265ea3f769 | completed | success | https://github.com/leonardosovienski/predictor-ops/actions/runs/36722531151 |
| predictor-ops | ci-main-remoto | 36722530507 | 21cfcea55ee5c3049b406cac69998a265ea3f769 | completed | success | https://github.com/leonardosovienski/predictor-ops/actions/runs/36722530507 |
| predictor-qualification | ci-head-local | 35942817475 | f21bbbcccb06252cd5bc156c4093d571d03f0933 | completed | success | https://github.com/leonardosovienski/predictor-qualification/actions/runs/35942817475 |
| predictor-qualification | ci-main-remoto | 36667788172 | 3ed750c53854573d0bab461393c67b30c52185af | completed | success | https://github.com/leonardosovienski/predictor-qualification/actions/runs/36667788172 |
| stocks-predictor | ci-head-local | 35566993442 | 5cf27f44f579cb40d8b873c0f10005360427a2d0 | completed | success | https://github.com/leonardosovienski/stocks-predictor/actions/runs/35566993442 |
| stocks-predictor | ci-head-local | 35566993464 | 5cf27f44f579cb40d8b873c0f10005360427a2d0 | completed | success | https://github.com/leonardosovienski/stocks-predictor/actions/runs/35566993464 |
| stocks-predictor | ci-main-remoto | 36719558172 | 3ec7e413bdcaedccfc1c2ed65c2822dddccb5cee | completed | failure | https://github.com/leonardosovienski/stocks-predictor/actions/runs/36719558172 |

Estado confirmado-remotamente na consulta. Run de CI é ET-HIST remoto, não teste rodado por esta investigação; listagem não oferece logs nem semântica das asserções. Runs podem ser de eventos diferentes sobre o mesmo commit. Nenhum workflow foi acionado.
