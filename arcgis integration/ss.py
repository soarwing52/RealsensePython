
with open('all.csv', 'r') as csvfile:
    frame = [[elt.strip() for elt in line.split(';')] for line in csvfile]

print(frame[0])
print(frame[5])