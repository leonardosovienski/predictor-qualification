import study, pathlib, json, hashlib, datetime, time, xml.etree.ElementTree as ET
r=study.ROOT; project='predictor-qualification'; p=r/'copias'/project; original=pathlib.Path('C:/QUALIFICACAO/predictor-qualification')
def load(rel): return json.loads(study.read(project,p/rel))
att=load('qualification/crypto/QUALIFICATION_ATTESTATION.json'); findings=load('qualification/crypto/FINDINGS.json'); gates=load('qualification/crypto/GATES.json')
counts={k:sum(x['severity']==k and x['status'] in {'OPEN','OPEN_AWAITING_VERDICT','OPEN_BLOCKED'} for x in findings['findings']) for k in ('P0','P1','P2')}
evidence=[]
for gate,entry in att['gates'].items():
 for ev in entry['evidence']:
  f=p/ev['file']; actual=hashlib.sha256(f.read_bytes()).hexdigest() if f.is_file() else None
  study.log(project,f.parent,'SHA256 evidência referida em gate '+gate,0 if actual else 1,'match='+str(actual==ev['sha256']),artifacts=project+'/recomputed-attestation.json')
  evidence.append({'gate':gate,'file':ev['file'],'match':actual==ev['sha256'],'actual_sha256':actual,'expected_sha256':ev['sha256']})
corehash=hashlib.sha256((p/'qualification/COMMON_QUALIFICATION_CORE.md').read_bytes()).hexdigest()
result={'attestation_result_DD':att['result'],'final_commits_DD':att['final_commits'],'findings_counts_recomputed':counts,'counts_match':counts==att['counts'],'gate_statuses_DD':{k:v['status'] for k,v in att['gates'].items()},'all_pass':all(v['status']=='PASS' for v in att['gates'].values()),'core_hash_actual':corehash,'core_hash_match':corehash==att['common_core_sha256'],'evidence':evidence,'evidence_hashes_all_match':all(x['match'] for x in evidence),'scope':'verificação independente parcial; schema e conteúdo científico não revalidados'}
study.save('evidencias/'+project+'/recomputed-attestation.json',result)
# Preserve recomputation generated in execution copy and compare to existing original bytes sem overwrite.
computed=load('qualification/crypto/EVIDENCE_NUMBERS.json'); old=json.loads(study.read(project,original/'qualification/crypto/EVIDENCE_NUMBERS.json'))
study.save('evidencias/'+project+'/evidence-numbers-recomputed.json',computed)
changes=[k for k in set(computed)|set(old) if computed.get(k)!=old.get(k)]
study.save('evidencias/'+project+'/evidence-numbers-comparison.json',{'equal_json':computed==old,'different_keys':changes,'historical_recomputation_only':True})
print(json.dumps({k:v for k,v in result.items() if k not in ('evidence','gate_statuses_DD','final_commits_DD')},indent=2))
print('numbers equal',computed==old,changes)
# Catalog point from schema + narrative terms, no claim of enforcement.
schema=load('qualification/ATTESTATION_SCHEMA.json')
print('schema keys', list(schema.get('properties',{})))
decisions=load('qualification/DECISIONS.json')
print('decisions',[(x.get('decision_id'),x.get('status')) for x in decisions.get('decisions',[])])
study.log(project,p,'Recomputar counts/hashs de attestation e comparar EVIDENCE_NUMBERS gerado vs original JSON',0,'counts_match='+str(result['counts_match'])+'; hashes='+str(result['evidence_hashes_all_match'])+'; números iguais='+str(computed==old),status='ET-RUN',limits='Não repete runs históricos; validação schema indisponível',artifacts=project+'/recomputed-attestation.json; '+project+'/evidence-numbers-comparison.json')
