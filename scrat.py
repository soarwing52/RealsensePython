
with open(r'X:\Mittelweser\0626\shp/matcher.txt', 'r') as txtfile:

    title = [elt.strip() for elt in txtfile.readline().split(',')]
    frame_list = [[elt.strip() for elt in line.split(',')] for line in txtfile  if line.split(',')[0] == '0626_003']
    frame_list.insert(0,title)


print frame_list[0]