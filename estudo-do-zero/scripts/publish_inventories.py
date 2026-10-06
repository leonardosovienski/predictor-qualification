import study,subprocess,sys
r=study.ROOT
for p in ['predictor-ops','ecosystem-predictor','cain','stocks-predictor','cripto-predictor','brasileirao-predictor']:
 code,out=study.run('PUBLICACAO',r,[sys.executable,str(r/'scripts/publish.py'),'inventario-'+p,p],f'publication-milestone-{p}.txt',timeout=60)
 print(p,code,out.strip()[-100:],flush=True)
 if code:raise SystemExit(code)
