import sys,importlib.util,json,math,pathlib
sys.stdout.reconfigure(encoding="utf-8")
p=pathlib.Path(__file__).resolve().parents[1]/"copias/brasileirao-predictor/brasileirao_predictor/a1_recommendation.py"
s=importlib.util.spec_from_file_location("a1_probe",p);m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m)
rows=[]
for stage in ["CLV_CONFIRMED","TYPO"]:
 c=m.RecommendationInput(.7,2.,0.,0.,1.,True,True,True,False,stage,float("nan"))
 r=m.assess_recommendation(c);rows.append({"stage":stage,"clv":"NaN","score":r.indication_score,"cap":r.score_cap,"action":r.action,"capital":r.capital_enabled})
print(json.dumps(rows))
