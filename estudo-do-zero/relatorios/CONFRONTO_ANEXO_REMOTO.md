# Confronto do Anexo com main remoto e releases

Época distinta das oito fontes locais. URLs usam SHA exato consultado por ls-remote; manifests e registro de decisão lidos somente após caracterizações preliminares. OD manifest não é execução da stack atual.

|Projeto / path|Versão main remoto|Commit|Estado|
|---|---|---|---|
|cain/pyproject.toml|0.4.13rc16|abeb1e6011537bea2d8a0d87334780f8370f1cbd|confirmado-remotamente|
|brasileirao-predictor/pyproject.toml|0.3.0rc6|1e0c6f0b31e7cdc514190f08d5d2ff9689bd905d|confirmado-remotamente|
|cripto-predictor/pyproject.toml|1.2.0rc5|74113effcec7c0cf8deb8a8a46d413b6942368ce|confirmado-remotamente|
|stocks-predictor/pyproject.toml|0.3.0rc4|3ec7e413bdcaedccfc1c2ed65c2822dddccb5cee|confirmado-remotamente|
|predictor-ops/pyproject.toml|4.2.2rc2|21cfcea55ee5c3049b406cac69998a265ea3f769|confirmado-remotamente|
|core-predictor/pyproject.toml|3.2.2|956891ea728f8e1e038cbfebb7f0148abc77f700|confirmado-remotamente|
|ecosystem-predictor/pyproject.toml|0.2.1|0b0a09c8c60e470f83bc7e735f64e2e83ab1fb6d|confirmado-remotamente|
|ecosystem-predictor/packages/research-protocol/pyproject.toml|2.0.0rc2|0b0a09c8c60e470f83bc7e735f64e2e83ab1fb6d|confirmado-remotamente|
|ecosystem-predictor/packages/research-transport/pyproject.toml|0.1.0rc7|0b0a09c8c60e470f83bc7e735f64e2e83ab1fb6d|confirmado-remotamente|
|predictor-qualification/qualification/DECISIONS.json|None|3ed750c53854573d0bab461393c67b30c52185af|confirmado-remotamente|

As versões main do AnexoA3 concordam com os manifests observados. CAIN declara protocolo2.0.0rc2 e transporte0.1.0rc7, além snapshot1.0.2rc1/bundle1.0.1rc1; isso confirma dependência declarada, sem concluir envelope funcionando. Ecosystem possui manifest de transporte; a ausência nos checkouts primáriosV1 não se aplica ao main.

|Pacote publicado do Anexo|Versão|Tag|SHA256 bytes wheel|Estado|
|---|---|---|---|---|
|predictor_core|3.2.1|v3.2.1|10ef42f34ace8bb2df5f83ff7de2ceec79b035a25ea0a690e8942bd60d2fb4e3|confirmado-remotamente|
|predictor_ops|4.2.2rc1|v4.2.2rc1|0be70bfbb2437dfb080baceb9af41043a09d03b15a358903b8bd7007f5f169b3|confirmado-remotamente|
|cain_research|0.4.13rc15|v0.4.13rc15|ff642b7271a7fcad18723b12bc7ebe29f0c2550ecfe178777b5c1481882aacf9|confirmado-remotamente|
|cripto_predictor|1.2.0rc4|v1.2.0rc4|32a4bd6d86719070e1a5d1e418c46034cfbf4ee292da11f17af2f60081fa9bf6|confirmado-remotamente|
|brasileirao_predictor|0.3.0rc5|v0.3.0rc5|be3bc5127ef64f1a3265b2e97384db3f4883d7d404030bed85aaa9fef1a078a6|confirmado-remotamente|
|stocks_predictor|0.3.0rc3|v0.3.0rc3|902f0d34efe7aef02c084e7886ef997c9b3f9bfe28e0e923c9c178361131ea00|confirmado-remotamente|
|ecosystem_predictor|0.2.1|v0.2.1|69374cf0eca60301724f07153b8a815c4807f808ace98d0188807e890ae6a80c|confirmado-remotamente|
|predictor_research_protocol|2.0.0rc2|predictor-research-protocol-v2.0.0rc2|34a1e4121e4085b901e3bd96552e2f5b4067c5e6af5e99dc1c26d6276fc7c820|confirmado-remotamente|
|predictor_research_transport|0.1.0rc7|predictor-research-transport-v0.1.0rc7|d3dfbff4b72d717ed4f655b1c97e85ca909140dcd9ebfb17e9a51a8b089c60c2|confirmado-remotamente|
|predictor_research_snapshot|1.0.2rc1|predictor-research-snapshot-v1.0.2rc1|3bd4c0414ac2d457923601e3f919f6353b5cb9370a0f420a7a3ffc013a0aafad|confirmado-remotamente|
|predictor_research_bundle|1.0.1rc1|predictor-research-bundle-v1.0.1rc1|65cf40c59c4f65d013a1134051fb94aa7c75b44f4ea6c71a54e25519143d0ea9|confirmado-remotamente|

URLs integrais/API digest/METADATA e datas em published-annex-identities.json. Sem instalação; presença de corpo METADATA não comprova README equivalente a main pós-bump. As versões não publicadas main foram distinguidas das consumidas; consultar release-identity de cada fonte e refs-tags para a busca delimitada.

DD remoto DECISIONS contém D-1..D-28 APPROVED, incluindo D-27 pós-qualificação: atestados permanecem vinculados final_commits/final_wheels antigos e novo ciclo agendado. D-29/D-30/D-31 não encontrados no campo decision_id da lista desse arquivo/commit. Aprovação no registro observada não valida execução das fases; attestations finais desse novo ciclo não foram recomputadas.

ET-HIST Stocks run36719558172 main3ec7...: dois qualityjobs3.13/3.14 falham no passo R8, tests/build subsequentes skipped; secrets success. Causa privada/religação de população não foi ensaiada. Na cópia do checkout primário5cf27... o verificador R8 PASS confirma época diferente.
