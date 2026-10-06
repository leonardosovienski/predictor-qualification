import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent));import study
texts={'cain':'''# Caracterização preliminar — cain

OD, árvore local: pacote `cain-research` 0.4.12, Python >=3.11, setuptools; dependências snapshot 1.0.1 e bundle 1.0.0. CLI cain, cain-mcp, cain-stream; API FastAPI opcional. `runtime.build_cain` compõe SQLiteIdentityStore, SQLiteDecisionLog, índice lexical, agentes conversação/resumo/código/busca e RuleRouter. `Cain.run` encadeia oito passos sequenciais, registra eventos mediated/completed/failed e hash da resposta; identidade explícita é atualizada separadamente. Falhas não têm retry implícito.

`research.service`, `bundles`, `inspection`, `analysis`, `workflows` recebem e consultam pesquisas com políticas distintas de leitura/divulgação/geração. LLM Ollama POST /api/generate e FakeLLM teste; review exige provedor local, trechos/citações e validação JSON, devolve semantic_support=not_certified e não promove memória. Workflow inspect/search/entities/support/challenge/synthesis tem aprovação geração, fingerprint do corpus, lease 600s e tentativas duráveis SQLite. Arquivo não rastreado claim_tables.py é consumido pelo analysis.py modificado, logo árvore executável não coincide com HEAD.

Escopo antes de confronto narrativo: 169 arquivos rastreados executáveis/configuração/testes, 25.175 linhas mecanicamente lidas/indexadas; módulos centrais acima revisados semanticamente. Arquivos não rastreados precisam complementar cobertura. Não há ET-RUN nem observação de modelo/serviço/instalação. Hashes e comandos em evidencias/cain e REGISTRO.log. Esta caracterização descreve a árvore local, não versão remota.
''','stocks-predictor':'''# Caracterização preliminar — stocks-predictor

OD: pacote stocks-predictor 0.2.0, Python >=3.13,<3.15, Hatchling 1.32.0, PyYAML e predictor-core >=3.2,<4; tool.uv.sources fixa wheel core 3.2.1. Plugin predictor.plugins stocks tem health WAITING e capabilities pesquisa, sem previsão/settlement/coleta; capital FORBIDDEN, econômico NO_GO, científico DISCOVERY_INCONCLUSIVE. Arquitetura inclui CLI legado main.py e operacional `python -m stocks_predictor`, ingestão COTAHIST/CVM, hipóteses/backtests, RJ, paper, integração bundle e catálogo versionado.

operational_store valida schema/application_id/user_version exatos, WAL local, BEGIN IMMEDIATE, triggers append-only, ingestão arquivo local com hash, backup consistente e restore em diretório novo. Não transforma observação de catálogo em disponibilidade histórica. economic_gate usa média menos z*erro-padrão e custo para HOLD/REBALANCE, capital_enabled=False; caller é responsável pela maturidade. trials_gate usa controles positivos/sintéticos sobre judge, registro de tentativas e DSR estrito, evitando deflation_applied=False virar COMPROVADA.

235 arquivos executáveis/configuração/testes selecionados, 36.308 linhas mecanicamente lidas/indexadas; lógica central selecionada revisada semanticamente. Código vendorizado e scripts históricos research catalogados, não integralmente revisados. Não há ET-RUN, banco real, backtest recalculado nem instalação/serviço observado. Identidade e hashes em evidencias/stocks-predictor. Sem inferência de capacidade lucrativa.
'''}
for project,text in texts.items():
 study.save('relatorios/PRELIMINAR_'+project+'.md',text);study.log(project,study.ROOT,'Caracterização preliminar salva ANTES confronto narrativo',0,'Caracterização por código/configuração e cobertura limitada',artifacts='relatorios/PRELIMINAR_'+project+'.md')
