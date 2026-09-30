import study,json,pathlib,sys,ast
j=json.loads(study.read('cripto-shared',study.ROOT/'evidencias/cripto-predictor/semantic-pending-by-class.json'))
b=json.loads(study.read('cripto-shared',study.ROOT/'evidencias/cripto-predictor/baseline.json'))
rows=[r for r in j['files']['tests'] if r['state']=='pendente']
class Strip(ast.NodeTransformer):
 def visit_Expr(self,n):
  return None if isinstance(n.value,ast.Constant) and isinstance(n.value.value,str) else self.generic_visit(n)
if len(sys.argv)==1:
 print('ROOT',b['path']);print('\n'.join(str(i)+' '+str(x) for i,x in enumerate(rows)))
else:
 for i,r in enumerate(rows):
  if int(sys.argv[1])<=i<=int(sys.argv[2]):
   print('FILE',i,r['path']);s=study.read('cripto-shared',pathlib.Path(b['path'])/r['path']);print(ast.unparse(Strip().visit(ast.parse(s))))
