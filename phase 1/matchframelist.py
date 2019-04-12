
depth_frame_list = []
color_frame_list = []
match_frame_list = []
with open('colorlist.txt','r') as csvfile:
    for line in csvfile:
        frame = [elt.strip() for elt in line.split(',')]
        color_frame_list.append(frame)

with open('depthlist.txt','r') as depcsv:
    for dline in depcsv:
        frame_d = [dd.strip() for dd in dline.split(',')]
        depth_frame_list.append(frame_d)
print depth_frame_list
csvfile.close()
depcsv.close()
f_list = []

for t_c in color_frame_list:
    for t_d in depth_frame_list:
        gap = float(t_c[1]) - float(t_d[1])
        gap = abs(gap)
        if gap <20:
            #print gap
            frame_match = t_c[0],t_d[0]
            #print frame_match
            f_list.append(str(t_c[0]) + ','+str(t_d[0]) + '\n')


print f_list
unique_list = []
with open('matched.txt','w') as matched:
    for elem in f_list:
        if elem not in unique_list:
            print elem
            unique_list.append(elem)
            matched.write(elem)

matched.close()
print unique_list


