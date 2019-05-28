import os

def pair(num):
    global tet
    match = open('./list/{}_matched.txt'.format(num),'r')
    foto = open('./foto_log/{}.txt'.format(num), 'r')

    match =[x.strip().split(',') for x in match]
    foto = [x.strip().split(',') for x in foto]
    #print match


    for lines_m in match:
        color_m = lines_m[1]
        Depth = lines_m[2]
        for lines_l in foto:
            ID = lines_l[0]
            color_l = lines_l[1]
            Lon = lines_l[3]
            Lat = lines_l[4]
            Time = lines_l[8]
            png = r'X:\Mittelweser\0528\png/{}-{}.png'.format(num,color_m)
            try:
                ans = abs(int(color_l) - int(color_m))
                if ans <5:

                    info = '{},{},{},{},{},{},{},{}\n'.format(num,ID,color_m,Depth,Lon,Lat,Time,png)
                    print info
                    tet.write(info)
                else:
                    #print 'no'
                    continue
            finally:
                pass


def main():
    global tet
    tet = open('matcher.txt','w')
    tet.write('weg_num,foto_id,Color,Depth,Lon,Lat,Uhrzeit,png_path\n')
    for x in os.listdir('foto_log'):
        num = x.split('.')[0]
        try:
            pair(num)
        except IOError:
            pass
        finally:
            pass

if __name__ == '__main__':
    main()

