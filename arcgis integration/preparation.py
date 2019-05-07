import os
import arcpy
from arcpy import management


def foto_shp(project_name):
    project_name = project_name
    project_path = r'X:/' + project_name
    bag_dir = project_path + '/bag'
    foto_dir = project_path + '/foto_log'
    foto_shp = open(project_path + '/Foto.txt', 'w')
    foto_shp.write('weg_num,foto_id,Color,Depth,X,Y,png_path,time\n')
    for f_log in os.listdir(foto_dir):
        file_name = foto_dir + '/' + f_log
        print file_name
        with open(file_name, 'r') as logs:
            for lines in logs:
                data = lines.split(',')
                Long = data[7]
                Lat = data[5]
                weg_nummer = f_log[8:-4]
                path = '{}/png/{}-{}.png'.format(project_path, weg_nummer, data[1])
                shp_line = '{},{},{},{},{},{},{},{}'.format(weg_nummer, data[0], data[1], data[2], Long, Lat, path,data[11])
                #print shp_line
                foto_shp.write(shp_line)
    foto_shp.close()
    arcpy.env.overwriteOutput = True
    a = management.MakeXYEventLayer(project_path + '/Foto.txt', 'X', 'Y', 'Fotopunkte')
    print a
    arcpy.FeatureClassToShapefile_conversion('Fotopunkte', project_path)
    print 'Fotopunkte.shp fertig'

def gps_shp(project_name):
    project_name = project_name
    project_path = r'X:/' + project_name
    bag_dir = project_path + '/bag'
    gps_dir = project_path + '/gps_log'
    gps_shp = open(project_path + '/gps.txt', 'w')
    gps_shp.write('X,Y\n')
    for g_log in os.listdir(gps_dir):
        file_name = gps_dir + '/' + g_log
        print file_name
        with open(file_name, 'r') as logs:
            for lines in logs:
                data = lines.split(',')
                Long = data[4]
                Lat = data[2]
                print data
                shp_line = '{},{}\n'.format(Long, Lat)
                print shp_line
                gps_shp.write(shp_line)
    gps_shp.close()
    arcpy.env.overwriteOutput = True
    a = management.MakeXYEventLayer(project_path + '/gps.txt', 'X', 'Y', 'GPSpunkte')
    print a
    arcpy.FeatureClassToShapefile_conversion('GPSpunkte', project_path)
    print 'GPSpunkte.shp fertig'

def main():
    project_name = raw_input('Projekt name(ex.Loehne): \n')
    foto_shp(project_name)
    gps_shp(project_name)
    print 'done'
    raw_input('press enter to leave')

if __name__ == '__main__':
    main()

