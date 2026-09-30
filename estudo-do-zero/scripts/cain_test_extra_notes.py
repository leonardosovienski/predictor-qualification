import study,json,pathlib,hashlib,ast
notes={
'tests/integration/test_br_audit_instructions.py':'Capture.generate_json valida instrução Explicitlylabel/features=inputvariables e recorte BLOCKED/featureunproven intacto; entrega gerada semantic_support not_certified uma chamada; fonte ausente modelo proibido zero inferência. Não demonstra entendimento modelo real.',
'tests/integration/test_literal_claim_tables.py':'Dois orders identities QA001..003 com três horizontes; NoGeneration exige literal_claim_table zero calls; resposta preserva todos state/limits/horizons e disclaimer não resultado demonstrado, inclui header em source_quotes.',
'tests/integration/test_review_provider_budget.py':'Provider effectivebudget1000 insuficiente abstained_context_budget antes modelo; falha RuntimeError mantem last_metadata HTTP500 no envelope. Context contract apenas.',
'tests/unit/test_llm_failure_diagnostics.py':'Ollama effectivebudget3190 antes generate; HTTP404/500 synthetic monkeypatch com bounded JSON error preserva diagnostic uma chamada sem retry; nonJSONprivatebody não exposto, status mantido/servererrorNone.'}
out=[]
for p,n in notes.items():
 s=study.read('cain-shared',pathlib.Path('C:/CAIN/projeto')/p)
 out.append(dict(path=p,sha256=hashlib.sha256(s.encode()).hexdigest(),review='integral-semantic-read',notes=n,execution='not-executed-in-this-study',source_state='untracked-local-tree',tests=[x.name for x in ast.walk(ast.parse(s)) if isinstance(x,ast.FunctionDef) and x.name.startswith('test_')]))
study.save('evidencias/cain/shared-untracked-test-notes.json',out)
study.save('evidencias/cain/shared-untracked-test-coverage.json',[{k:r[k] for k in ('path','sha256','review','execution','source_state')} for r in out])
study.save('evidencias/cain/shared-untracked-test-review.md','# Suplemento testes locais não rastreados\n\nQuatro arquivos lidos integralmente, nenhum executado. Não pertencem ao HEAD remoto ou tracked.\n\n'+'\n\n'.join('## '+r['path']+'\n\n'+r['notes'] for r in out))
print(study.read('cain-shared',pathlib.Path('C:/CAIN/projeto/tests/integration/qa_br_fixture.py')))
