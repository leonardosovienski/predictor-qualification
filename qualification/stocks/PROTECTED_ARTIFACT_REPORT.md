# PROTECTED_ARTIFACT_REPORT — missão stocks (C15.1; gate PROTECTED_ARTIFACTS_UNCHANGED)

Conjunto protegido fixado no fim do `truth-map` (`PROTECTED_SET.json`, commit `4e98a67`): 81 arquivos versionados
por hash de blob git (lista do prompt §5 + o que os documentos declaram congelado: `big_winner_shadow.py`,
`big_winner_v2.py`, `prospective_big_winner.py`, `config.yaml`, `config_rj.yaml`, veredictos em `reports/`,
`vendor/predictor_core/`, ledger H17, manifestos dos sinais congelados) e 3.698 arquivos de dados imutáveis por
sha256 (`C:\STOCKS\DADOS_STOCKS.zip*` e `C:\STOCKS\data\**`, incluindo `CATALOG.json`), lidos somente leitura.

Conferência no `final_commit` `61fc017` (C14, rc2; a mesma conferência no `9a6c09a` da rc1 deu o mesmo resultado, `RAW_LOGS/protected/protected_check_9a6c09a.json`) (`scripts/protected_check.py`, saída bruta
`RAW_LOGS/protected/protected_check_61fc017.json`; re-hash dos dados em
`RAW_LOGS/protected/immutable_data_sha256_c14.txt`):

| verificação | resultado |
|---|---|
| blobs git alterados / ausentes | 0 / 0 (de 81) |
| arquivos novos que casam com os padrões protegidos | 0 |
| dados imutáveis com sha256 diferente | 0 (de 3.698) |
| arquivos de dados novos | 0 |

A missão não altera nem cria nada em `C:\STOCKS\data`, `DADOS_STOCKS.zip*`, trials, matriz de prontidão, lacres ou
artefatos BIG_WINNER. Os recibos R8 (D-18) usaram a cópia `C:\STOCKS\work\gap-resolution-r6-20260910\raw\COTAHIST_A2026.ZIP`
somente leitura (sha256 `34b77468…`, igual antes e depois).

Checagem extra do prompt §5 (`verify_history_protected.py`, `verify_real_protected.py`): os scripts importam
`inspect_state` com caminhos de outra máquina (`C:/Users/Superleo13/...`) e gravam em `outputs/`; executados como
diagnóstico numa cópia descartável no Actions, falham com `FileNotFoundError` (ST-F003, P2;
`RAW_LOGS/cleanroom-baseline/run35943720554/*/verify_*_protected.log`). A verificação equivalente é a deste relatório.
