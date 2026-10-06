import study,pathlib
s=study.read('cain-shared',study.ROOT/'evidencias/cain/baseline-status.txt')
for line in s.splitlines():
 if line.startswith('?? ') and 'test_' in line:
  p=line[3:];print('FILE',p);print(study.read('cain-shared',pathlib.Path('C:/CAIN/projeto')/p))
