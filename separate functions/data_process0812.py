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
    """convert a number to rantional
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


def examine_bag(input_file):
    try:
        pipeline = rs.pipeline()
        config = rs.config()
        config.enable_device_from_file(input_file, False)
        config.enable_all_streams()
        profile = pipeline.start(config)
        device = profile.get_device()
        playback = device.as_playback()
        playback.set_real_time(False)
        pipeline.stop()
    except RuntimeError:
        print '{} unindexed'.format(input_file)
    finally:
        pass


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


def frame_list(input_file):
    """write the frame list of the bag file
    input: abspath"""
    input_num = os.path.basename(input_file)[:-4]
    project_dir = os.path.dirname(os.path.dirname(input_file))
    list_dir = dir_generate(project_dir + '/list')

    if os.path.isfile('{}/{}_color.txt'.format(list_dir, input_num)) and os.path.isfile('{}/{}_depth.txt'.format(list_dir, input_num)):
        print 'list {} already exist'.format(input_num)
        return

    c_fold = open('{}/{}_color.txt'.format(list_dir, input_num), 'w')
    d_fold = open('{}/{}_depth.txt'.format(list_dir, input_num), 'w')

    try:
        pipeline = rs.pipeline()
        config = rs.config()
        config.enable_device_from_file(input_file, False)
        config.enable_all_streams()
        profile = pipeline.start(config)
        device = profile.get_device()
        playback = device.as_playback()
        playback.set_real_time(False)
        align_to = rs.stream.color
        align = rs.align(align_to)
        while True:
            frames = pipeline.wait_for_frames()
            aligned_frames = align.process(frames)
            color_frame = aligned_frames.get_color_frame()
            depth_frame = aligned_frames.get_depth_frame()
            num_d = rs.frame.get_frame_number(depth_frame)
            num_c = rs.frame.get_frame_number(color_frame)
            time_c = rs.frame.get_timestamp(color_frame)
            time_d = rs.frame.get_timestamp(depth_frame)

            c_fold.write('{},{}\n'.format(str(num_c), str(time_c)))
            d_fold.write('{},{}\n'.format(str(num_d), str(time_d)))

    except RuntimeError:
        print '{} frame list ended'.format(input_num)
    finally:
        c_fold.close()
        d_fold.close()


def match_frame_list(input_file):
    """match color and depth within the time of 25ms"""
    input_num = os.path.basename(input_file)[:-4]
    project_dir = os.path.dirname(os.path.dirname(input_file))
    list_dir = dir_generate(project_dir + '/list')

    with open('{}/{}_color.txt'.format(list_dir, input_num), 'r') as color:
        color_frame_list = [x.strip().split(',') for x in color]

    with open('{}/{}_depth.txt'.format(list_dir, input_num), 'r') as depth:
        depth_frame_list = [x.strip().split(',') for x in depth]

    f_list = []
    for t_c in color_frame_list:
        for t_d in depth_frame_list:
            gap = float(t_c[1]) - float(t_d[1])
            gap = abs(gap)
            if gap < 25:
                f_list.append(str(t_c[0]) + ',' + str(t_d[0]) + '\n')

    unique_list = []

    for elem in f_list:
        if elem not in unique_list:
            unique_list.append(elem)

    i = 1
    if os.path.isfile('{}/{}_matched.txt'.format(list_dir, input_num)):
        return
    with open('{}/{}_matched.txt'.format(list_dir, input_num), 'w') as matched:
        for x in unique_list:
            x = '{},{}'.format(i, x)
            matched.write(x)
            i += 1
    matched.close()
    print 'finished match list ' + input_file


def create_list():
    """TKinter Button, loop through the bag folder and create color,depth,match list"""
    global project_dir,t
    bag_dir = project_dir + '/bag'

    x_list = ['{}/{}'.format(bag_dir,x) for x in os.listdir(bag_dir) ]
    pool = mp.Pool()
    pool.map(examine_bag, x_list)
    pool.map(frame_list, x_list)
    pool.map(match_frame_list, x_list)

    t.insert(END, 'match list fertig\n')


def pair(num,tet,ans):
    """match the list of _matched.txt and fotolog, with the accuracy of +-5 frames"""
    project_dir = ans
    match = open('{}/list/{}_matched.txt'.format(project_dir, num), 'r')
    foto = open('{}/foto_log/{}.txt'.format(project_dir, num), 'r')

    match = [x.strip().split(',') for x in match]
    foto = [x.strip().split(',') for x in foto]
    written_lonlat = [0,0]
    for lines_m in match:
        color_m = lines_m[1]
        Depth = lines_m[2]
        for lines_l in foto:
            ID = lines_l[0]
            color_l = lines_l[1]
            Lon = lines_l[3]
            Lat = lines_l[4]
            Time = lines_l[8]
            jpg = '{}/jpg/{}-{}.jpg'.format(project_dir, num, color_m)

            ans = abs(int(color_l) - int(color_m))
            if ans < 5 and written_lonlat != [Lat,Lon] and os.path.isfile(project_dir + '/jpg/{}-{}.jpg'.format(num,color_m)):
                info = '{},{},{},{},{},{},{},{}\n'.format(num, ID, color_m, Depth, Lat, Lon, Time, jpg)
                tet.write(info)
                written_lonlat = [Lat, Lon]

    print num + ' done'


def pair_list(ans):
    """Tkinter Button, loop through files in fotolog and create paired matcher.txt in shp folder"""
    project_dir = ans

    list_dir = dir_generate(project_dir + '/list')
    foto_log = project_dir + '/foto_log'
    shp_dir = dir_generate(project_dir + '/shp')

    tet = open(shp_dir + '/matcher.txt', 'w')
    tet.write('weg_num,foto_id,Color,Depth,Lat,Lon,Uhrzeit,jpg_path\n')

    for log in os.listdir(foto_log):
        num = log.split('.')[0]
        try:
            pair(num,tet,ans)
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


def Fotopunkte():
    """create Fotopunkte.txt and shp from all fotologs, the lost frames and the small latency caused frame number not
    match can't be detected """
    global project_dir,t
    shp_dir = dir_generate(project_dir + '/shp')
    fotolog = project_dir + '/foto_log'
    foto_shp = open(project_dir + '/shp/Fotopunkte.txt', 'w')
    foto_shp.write('weg_num,foto_id,Color,Depth,Lon,Lat,jpg_path,Uhrzeit\n')
    for x in os.listdir(fotolog):
        file_name = '{}/{}'.format(fotolog, x)
        with open(file_name, 'r') as log:
            for data in log:
                data = data.split(',')
                foto_id, Color, Depth, Long, Lat, time = data[0], data[1], data[2], data[4], data[3], data[8]
                weg_nummer = x[:-4]
                path = '{}/jpg/{}-{}.jpg'.format(project_dir, weg_nummer, Color)
                shp_line = '{},{},{},{},{},{},{},{}'.format(weg_nummer, foto_id, Color, Depth, Long, Lat, path, time)
                foto_shp.write(shp_line)
        t.insert(END, 'processed {}\n'.format(x))
    foto_shp.close()
    arcpy.env.overwriteOutput = True
    spRef = 'WGS 1984'
    management.MakeXYEventLayer(shp_dir + '/Fotopunkte.txt', 'Lat', 'Lon', 'Fotopunkte', spRef)
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
    align_to = rs.stream.color
    align = rs.align(align_to)
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
                kernel = np.array([[-1, -1, -1],
                                   [-1, 9, -1],
                                   [-1, -1, -1]])
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

    Button(frame_2, text='generate list', command=lambda: create_list()).grid(row=1, column=1)
    Button(frame_2, text='generate shp', command=lambda: from_bag_to_list(project_dir)).grid(row=1, column=2)
    Button(frame_2, text='generate jpg', command=lambda: generate_jpg()).grid(row=1, column=3)
    Button(frame_2, text='geotag', command=geotag).grid(row=1, column=4)

    root.mainloop()


if __name__ == '__main__':
    main()
