import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent));import study
p='stocks-predictor'
study.read(p,study.ROOT/'evidencias'/p/'executable-01.txt')
n=json.loads(study.read(p,study.ROOT/'evidencias'/p/'module-notes.json'))
n.update({
'stocks_predictor/backtest.py':'Revisão integral: legacy_walk_forward mensal universoestritopréasof mas sériesajustadascorrentes; retornos ausentes carteira zero vs benchmark somente disponíveis, custos cobrados primeiro registro. judge COMPROVADA significa apenas limiteinferior bootstrap diffSharpe>0, não lucro/capital; DSR aplicado nas hipóteses via trials_gate. H11 legado totalreturn; H17/18/19 abortam PAUSED. H16 seleciona universo no próprio fechamento e aplica retorno desse dia: risco seleção contemporânea. API walk_forward final delega engine simulation atual; runs H1..15 ainda legacy explícito.',
'stocks_predictor/big_winner_shadow.py':'Revisão integral: DBmodeRO; universo126sessões e252história préasof/quarentena, proxyissuer ticker[:4]. _load divide quote_factor sem validação própria e aplica splitsapproved atuais atéasof; séries completas são enviadas à geração que recorta sinais. HashDBwholebytes e freezesuppliedcommit não atestam snapshotatômico/commitreal. Ledger/artifacts escritos, default development_backfillTrue e prospective_evidence_eligibleFalse; READY_NOT_SCHEDULED é constante não execuçãoagendada.',
'stocks_predictor/config.py':'Revisão integral: miniYAML duas camadas, escalaresbool/int/float/string, comentáriosdoublequote; duplicatekeys overwrite, semschema/type/unknownkey validation/listas. frozen keys H1..19 explicitamente selecionadas e hashCore; não congela bytes externos automaticamente.',
'stocks_predictor/diagnostics.py':'Revisão integral: Python3.13..3.14 e versõesmetadata Core3.2..3/PyYAML6 estáveis, semimport/provaoperacional. DBopcional ROqueryonly quick_check timeout1; doctorcheckexitfail quando metadados/DBfalham; nenhuma criação DB.',
'stocks_predictor/disclosed_accounting.py':'Revisão integral: identifica lucrocontrolador por accountlen7/regex inequívoca; equityowner PLconsolidado menosNCIúnico; ambiguidades None+issues. Não faz validação externa/escala monetária própria.',
'stocks_predictor/cash_source_audit.py':'Revisão integral: CVMfollowup approvedissuer/category/date; duplicate reviewed exige distribuição/hash/source/reason e callbackrawrowequal. PDF suppliedtexts CREDITO atéCUSTODIA, ISINgrosspayment; missingapproval incomplete. Installments reviewed identidade/tax/hash somaDecimal ou delta≤1e-9reviewed, availableprimeirasessãopós payment. B3 divide quoteamount porquotation, cum→próxima sessão gap≤7, aprovação≤cum, completecoverageFalse. Paymentmatch exactidentity/gross tolerância1e-11/parcelas; eligibleTRfalse. Hashes declarados não verificação externa geral.',
'stocks_predictor/continuous_cash.py':'Revisão integral: RetailBookDecimal longonly com settlement/receivables/taxledger mensal; IRRF/DARF reviewcalendar, prejuízo/carry e créditoannualexternal. Corporateactions stageddeepcopy all-or-nothing; approvedsource+known<=day, lockedstocklegs/fracionários/auctiontax/rights/exactidentity. Continuous engine exige coverage_ready/noissues, calendário diário≥2plans, execução próxima sessão, sellsfirst e buys reduz delta atécashfundable; transformingaction entre sinal/execution aborta. Final liquidationrequired e clearing atépendingdates; liquidprofit vs facewithunpaid separado. full_history_executed só história fornecida, não cobertura verdadeira/ciência/capital.'})
study.save('evidencias/'+p+'/module-notes.json',n)
c=json.loads(study.read(p,study.ROOT/'evidencias'/p/'coverage.json'))
for r in c:
 if r['path'] in n:r.update(depth='revisado semanticamente',notes=n[r['path']])
study.save('evidencias/'+p+'/coverage.json',c)
study.log(p,study.ROOT,'Revisão semântica backtest/shadow/config/diagnostics/accounting/cash_source/continuous_cash',0,'7 módulos integrais',artifacts=p+'/module-notes.json;'+p+'/coverage.json')
for p in ['cain','stocks-predictor']:
 print(p,[x.name for x in (study.ROOT/'evidencias'/p).glob('*coverage*.json')])
 c=json.loads(study.read(p,study.ROOT/'evidencias'/p/'coverage.json'))
 print('pendentes', [r['path'] for r in c if r.get('depth')!='revisado semanticamente'])
