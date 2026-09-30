import sys,pathlib,ast,json
import study
class Strip(ast.NodeTransformer):
 def visit_Expr(self,node):
  if isinstance(node.value,ast.Constant) and isinstance(node.value.value,str):return None
  return self.generic_visit(node)
p=sys.argv[1];lo=int(sys.argv[2]);hi=int(sys.argv[3]);root={'core-predictor':r'C:\PREDICTORS\core-predictor','predictor-ops':r'C:\PREDICTORS\predictor-ops','ecosystem-predictor':r'C:\CAIN\contrato'}[p]
for i,row in enumerate(json.loads(study.read(p,study.ROOT/'evidencias'/p/'source-catalog.json'))):
 rel=row['path']
 if lo<=i<=hi and rel.endswith('.py'):
  s=study.read(p,pathlib.Path(root)/rel);print('\nFILE '+rel+'\n'+ast.unparse(Strip().visit(ast.parse(s))))
