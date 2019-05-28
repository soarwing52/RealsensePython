import os
import re

with open('match.txt', 'w') as ttt:
    ttt.write('title')
    for x in os.listdir(r'X:\Mittelweser\0528\png'):
        q = re.split('[_ . -]',x)
        print q
        ans = int(q[1] + q[2])
        print ans
        k = '{},{}\n'.format(x,ans)
        ttt.write(k)
