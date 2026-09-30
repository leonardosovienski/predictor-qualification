import study,json
p='brasileirao-predictor'
idx=json.loads(study.read(p,study.ROOT/f'evidencias/{p}/root-scripts-index.json'))
cov=json.loads(study.read(p,study.ROOT/f'evidencias/{p}/shared-brasil-scripts-coverage.json'))
expected={s for i in range(14,21) for s in idx[i]}
actual={s['path'] for s in cov}
r={'blocks':[14,20],'expected':len(expected),'actual':len(actual),'missing':sorted(expected-actual),'extra':sorted(actual-expected),'executed':False}
study.save(f'evidencias/{p}/shared-brasil-scripts-completeness.json',r)
print(r)
