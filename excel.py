import pandas as pd


file = open('0527_10_depth.txt','r')

x = [[x.split(',')[0],x.split(',')[1]] for x in file]
print x
file.close()
file2 = open('0527_10_color.txt','r')
y = [[x.split(',')[0],x.split(',')[1]] for x in file2]
print y
file2.close()

d = dict(enumerate(x))
print d

d2 = dict(enumerate(y))

df = pd.DataFrame(data=d)
df2 = pd.DataFrame(data=d2)
print df
print df2