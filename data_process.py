# -*- coding: utf-8 -*-
from Tkinter import *
import tkFileDialog
import arcpy
from arcpy import management
import pyrealsense2 as rs
import numpy as np
import cv2
import multiprocessing as mp
import os
import piexif
from fractions import Fraction

def to_deg(value, loc):
    """convert decimal coordinates into degrees, munutes and seconds tuple
    Keyword arguments: value is float gps-value, loc is direction list ["S", "N"] or ["W", "E"]
    return: tuple like (25, 13, 48.343 ,'N')
    """
    if value < 0:
        loc_value = loc[0]
    elif value > 0:
        loc_value = loc[1]
    else:
        loc_value = ""
    abs_value = abs(value)
    deg =  int(abs_value)
    t1 = (abs_value-deg)*60
    min = int(t1)
    sec = round((t1 - min)* 60, 5)
    return (deg, min, sec, loc_value)


def change_to_rational(number):
    """convert a number to rational
    Keyword arguments: number
    return: tuple like (1, 2), (numerator, denominator)
    """
    f = Fraction(str(number))
    return (f.numerator, f.denominator)


def set_gps_location(file_name, lat, lng, altitude):
    """Adds GPS position as EXIF metadata
    Keyword arguments:
    file_name -- image file
    lat -- latitude (as float)
    lng -- longitude (as float)
    altitude -- altitude (as float)
    """
    lat_deg = to_deg(lat, ["S", "N"])
    lng_deg = to_deg(lng, ["W", "E"])

    exiv_lat = (change_to_rational(lat_deg[0]), change_to_rational(lat_deg[1]), change_to_rational(lat_deg[2]))
    exiv_lng = (change_to_rational(lng_deg[0]), change_to_rational(lng_deg[1]), change_to_rational(lng_deg[2]))

    gps_ifd = {
        piexif.GPSIFD.GPSVersionID: (2, 0, 0, 0),
        piexif.GPSIFD.GPSAltitudeRef: 1,
        piexif.GPSIFD.GPSAltitude: change_to_rational(round(altitude)),
        piexif.GPSIFD.GPSLatitudeRef: lat_deg[3],
        piexif.GPSIFD.GPSLatitude: exiv_lat,
        piexif.GPSIFD.GPSLongitudeRef: lng_deg[3],
        piexif.GPSIFD.GPSLongitude: exiv_lng,
    }

    exif_dict = {"GPS": gps_ifd}
    exif_bytes = piexif.dump(exif_dict)
    piexif.insert(exif_bytes, file_name)


def geotag():
    """
    collect gps location of matcher.txt and match to jpg
    :return:
    """
    global project_dir,t
    print 'start geotag'
    fotolog = project_dir + '/shp/matcher.txt'
    jpg_dir = project_dir + '/jpg'
    with open(fotolog, 'r') as log:
        log.readline()
        for y in log:
            data = y.split(',')
            weg_num, frame, Lat, Lon = data[0], data[2], float(data[4]), float(data[5])
            jpgname = '{}/{}-{}.jpg'.format(jpg_dir, weg_num, frame)
            try:
                set_gps_location(jpgname, Lat, Lon, 0)
            except IOError:
                print jpgname + ' not found'
                continue
            finally:
                pass
    print 'tagged'
    t.insert(END, 'geotagging fertig\n')


def dir_generate(in_dir):
    """exmaine if this folder exist, if not, create one"""
    in_dir = str(in_dir)
    if not os.path.exists(in_dir):
        try:
            os.makedirs(in_dir, 0o700)
        except WindowsError:
            print 'already exist'
        finally:
            pass
    return in_dir


def get_dir(var):
    """ Tkinter button to get the project directory"""
    global project_dir
    project_dir = tkFileDialog.askdirectory()
    var.set(project_dir)
    print project_dir
    return project_dir


def pair(num,tet,ans):
    """match fotolog and existing photos, with the accuracy of +-2 frames"""
    project_dir = ans
    photo_dir = project_dir + '/jpg'
    with open('{}/foto_log/{}.txt'.format(project_dir, num), 'r') as foto:
        foto = [x.strip().split(',') for x in foto]

    global written_lonlat
    written_lonlat = [0,0]
    for lines_l in foto:
        ID = lines_l[0]
        color_l = lines_l[1]
        Depth = lines_l[2]
        Lon = lines_l[3]
        Lat = lines_l[4]
        Time = lines_l[8]


        for i in range(-5,5):
            ans = int(color_l) + i
            if os.path.isfile('{}/jpg/{}-{}.jpg'.format(project_dir,num,ans)) and [Lat,Lon] != written_lonlat:
                jpg = '{}/jpg/{}-{}.jpg'.format(project_dir, num, ans)
                info = '{},{},{},{},{},{},{},{}\n'.format(num, ID, ans, Depth, Lat, Lon, Time, jpg)
                tet.write(info)
                written_lonlat = [Lat, Lon]
    print num + ' done'


def pair_list(ans):
    """Tkinter Button, loop through files in fotolog and create paired matcher.txt in shp folder"""
    project_dir = ans
    foto_log = project_dir + '/foto_log'
    shp_dir = dir_generate(project_dir + '/shp')

    with open(shp_dir + '/matcher.txt', 'w') as txt:
        txt.write('weg_num,foto_id,Color,Depth,Lat,Lon,Uhrzeit,jpg_path\n')
        for log in os.listdir(foto_log):
            num = log.split('.')[0]
            try:
                pair(num,txt,ans)
            except IOError:
                print 'no file {}'.format(num)
            finally:
                print 'pair list done'


def matchershp():
    """create the shp from the matcher.txt"""
    global project_dir,t
    shp_dir = dir_generate(project_dir + '/shp')
    arcpy.env.overwriteOutput = True
    spRef = 'WGS 1984'
    management.MakeXYEventLayer(shp_dir + '/matcher.txt', 'Lon', 'Lat', 'Fotopunkte', spRef)
    arcpy.FeatureClassToShapefile_conversion('Fotopunkte', shp_dir)
    t.insert(END, 'Fotopunkte.shp fertig\n')



def color_to_jpg(input_file):
    """create jpg with the input file in the folder jpg"""
    print input_file
    bagname = os.path.basename(input_file)
    bagdir = os.path.dirname(input_file)
    projectdir = os.path.dirname(bagdir)

    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_all_streams()
    config.enable_device_from_file(input_file, False)
    profile = pipeline.start(config)
    device = profile.get_device()
    playback = device.as_playback()
    playback.set_real_time(False)
    try:
        while True:
            frames = pipeline.wait_for_frames()
            color_frame = frames.get_color_frame()
            var = rs.frame.get_frame_number(color_frame)
            color_image = np.asanyarray(color_frame.get_data())
            color_cvt = cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB)
            jpg_name = '{}/jpg/{}-{}.jpg'.format(projectdir, bagname[:-4], var)
            # print jpg_name
            exist = os.path.isfile(jpg_name)
            if exist:
                # print 'jpg exist'
                pass
            else:
                print 'compressing {}'.format(jpg_name)
                kernel = np.array([[0, -1, 0],
                                   [-1, 5, -1],
                                   [0, -1, 0]])
                sharpened = cv2.filter2D(color_cvt, -1,kernel)  # applying the sharpening kernel to the input image & displaying it.
                cv2.imwrite((jpg_name), sharpened, [cv2.IMWRITE_JPEG_QUALITY,100])

    except RuntimeError:
        
        cv2.destroyAllWindows()
    finally:
        print 'frame covert finished for ' + input_file
        pipeline.stop()


def generate_jpg():
    """Loop through all the bag files until all jpgs were created
    if theres unreadable bag file it will keep on looping"""
    global project_dir,t
    jpg_dir = dir_generate(project_dir + '/jpg')
    bag_dir = dir_generate(project_dir + '/bag')

    try:
        for i in range(2):
            x = [os.path.join(bag_dir, bag) for bag in os.listdir(bag_dir)]
            pool = mp.Pool()
            pool.map(color_to_jpg, x)

    finally:
        print 'jpg fertig'
        t.insert(END, 'JPG fertig\n')


def from_bag_to_list(ans):
    project_dir = ans
    pair_list(ans)
    matchershp()


def main():
    """TKinter for data process"""
    global t
    root = Tk()
    root.title('shapefile generator')
    root.geometry('500x300')
    frame = Frame(root, bd=5)
    frame.pack()
    var = StringVar()
    l = Label(frame, textvariable=var, bg='white', bd=5, width=40)
    ans = lambda: get_dir(var)
    b = Button(frame, text='select folder', height=2, command= ans)
    b.pack()
    l.pack()
    frame_2 = Frame(root, height=20, bd=5)
    frame_2.pack()
    frame_b = Frame(root)
    frame_b.pack()
    t = Text(frame_b, width=40, height=10)
    t.pack()

    Button(frame_2, text='generate shp', command=lambda: from_bag_to_list(project_dir)).grid(row=1, column=2)
    Button(frame_2, text='generate jpg', command=lambda: generate_jpg()).grid(row=1, column=1)
    Button(frame_2, text='geotag', command=geotag).grid(row=1, column=4)

    root.mainloop()


if __name__ == '__main__':
    main()
