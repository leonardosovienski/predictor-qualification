import sys,pathlib,ast
import study
class Strip(ast.NodeTransformer):
 def visit_Expr(self,node):
  if isinstance(node.value,ast.Constant) and isinstance(node.value.value,str):return None
  return self.generic_visit(node)
p=sys.argv[1];prefix=sys.argv[2];root={'core-predictor':r'C:\PREDICTORS\core-predictor','predictor-ops':r'C:\PREDICTORS\predictor-ops','ecosystem-predictor':r'C:\CAIN\contrato'}[p]
for rel in study.read(p,study.ROOT/'evidencias'/p/'tracked-files.txt').splitlines():
 rel=rel.strip()
 if rel.startswith(prefix) and rel.endswith('.py'):
  content=study.read(p,pathlib.Path(root)/rel);tree=ast.parse(content)
  print('\nFILE '+rel+'\n'+ast.unparse(Strip().visit(tree)))
