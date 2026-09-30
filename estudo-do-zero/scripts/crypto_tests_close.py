import json, pathlib, study
p='cripto-predictor'
coverage=[]; notes=[]
for i in range(1,18):
    stem=study.ROOT/f'evidencias/{p}/shared-crypto-tests-{i:02}'
    coverage+=json.loads(study.read(p,str(stem)+'-coverage.json'))
    notes+=json.loads(study.read(p,str(stem)+'-notes.json'))
print(type(coverage),len(coverage),coverage[:1])
assert len(coverage)==169 and {x['index'] for x in coverage}==set(range(169))
for rel in ['tests/conftest.py','pyproject.toml']:
    path=pathlib.Path('C:/CRIPTO/pesquisa-20260909')/rel
    if path.exists(): print('CONFIG',rel,'\n'+study.read(p,path))
study.save(f'evidencias/{p}/shared-crypto-tests-all-coverage.json',coverage)
study.save(f'evidencias/{p}/shared-crypto-tests-all-notes.json',notes)
study.save(f'evidencias/{p}/shared-crypto-tests-config-review.md','''# Revisão semântica de testes Crypto

169 arquivos pendentes integralmente revisados, índices 0..168 sem lacunas ou duplicações. Fixtures, mocks, asserts e fluxo de cada corpo foram lidos. Cobertura estática de revisão não representa cobertura de execução. Nenhum teste ou módulo original foi executado; nenhum pacote foi instalado. Notas por arquivo nos 17 blocos shared-crypto-tests-01..17 e consolidações all-notes/all-coverage; hashes dos bytes de leitura em REGISTRO.log.

tests/conftest.py foi lido integralmente. Antes da collection troca caminhos mutáveis e credenciais por fixtures sintéticas, remove variáveis cujo nome contenha API_KEY/AUTH_TOKEN/API_SECRET/SECRET_KEY. Se local_root existe, cria scratch em operacao/temporarios dessa raiz: importar conftest original produziria escrita no original, razão adicional para não executá-lo. A frase nunca chegam à rede é comentário, não mecanismo global de bloqueio HTTP. registry_attestation chama juiz real com controles sintéticos e explicitamente não autoriza registro canônico.

pyproject.toml: Python >=3.13,<3.15; pytest testpaths=tests, strict-config e strict-markers; coverage limita source=GarimpoInvestimentos e branch=true, sem mínimo de cobertura declarado. Dependências V3/science/Excel são opcionais. importorskip em numpy/hmmlearn/sklearn/scipy/openpyxl pode omitir módulos/casos; instalação ausente não é PASS. Pip/venv/subprocess/SQLite/ZIP descritos nos testes são operações previstas pelo código, não executadas neste estudo.

Limites relevantes: golden/contratos/custos sintéticos não validam lucro; calibração PERP default é rejeitada. Wheel-assets retorna normalmente quando dist está vazio, hash stable compara a si mesmo, paper position_math calcula expressão no próprio teste, purge-contract replica fórmula local (actual-slicing cobre orquestração real com SpyEngine). Configuração de caminhos e presença de secrets fictícios não provam ausência de todos efeitos laterais ou autenticação de serviços.
''')
