import study,json,sys,pathlib,ast
rows=[r for r in json.loads(study.read('cain-shared',study.ROOT/'evidencias/cain/source-index.json')) if r['path'].startswith('tests/')]
class Strip(ast.NodeTransformer):
 def visit_Expr(self,n):
  return None if isinstance(n.value,ast.Constant) and isinstance(n.value.value,str) else self.generic_visit(n)
for i,r in enumerate(rows):
 if int(sys.argv[1])<=i<=int(sys.argv[2]):
  s=study.read('cain-shared',pathlib.Path(r'C:\CAIN\projeto')/r['path'])
  print('FILE',i,r['path']);print(ast.unparse(Strip().visit(ast.parse(s))))
