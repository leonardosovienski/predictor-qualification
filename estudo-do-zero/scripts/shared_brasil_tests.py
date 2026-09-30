import study,json,pathlib,sys,ast
p='brasileirao-predictor'
index=json.loads(study.read(p,study.ROOT/f'evidencias/{p}/applications-brazil-index.json'))
class Strip(ast.NodeTransformer):
 def visit_Expr(self,n):
  return None if isinstance(n.value,ast.Constant) and isinstance(n.value.value,str) else self.generic_visit(n)
for i in range(int(sys.argv[1]),int(sys.argv[2])+1):
 print('BLOCK',i)
 for rel in index[i]['files']:
  print('FILE',rel)
  s=study.read(p,pathlib.Path('C:/BRASILEIRAO/brasileirao-predictor')/rel)
  print(ast.unparse(Strip().visit(ast.parse(s))))
