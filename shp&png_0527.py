# -*- coding: utf-8 -*-
from Tkinter import *
import tkFileDialog
import os
import arcpy
from arcpy import management
import pyrealsense2 as rs
import numpy as np
import cv2
import multiprocessing as mp


def test_bag(input_file):
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
    """test if this folder exist, if not, create one"""
    in_dir = str(in_dir)
    if not os.path.exists(in_dir):
        try:
            os.makedirs(in_dir, 0o700)
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
    pool.map(test_bag,x_list)
    pool.map(frame_list, x_list)
    pool.map(match_frame_list, x_list)

    t.insert(END, 'match list fertig\n')


def pair(num):
    """match the list of _matched.txt and fotolog, with the accuracy of +-5 frames"""
    global tet, project_dir
    match = open('{}/list/{}_matched.txt'.format(project_dir, num), 'r')
    foto = open('{}/foto_log/{}.txt'.format(project_dir, num), 'r')

    match = [x.strip().split(',') for x in match]
    foto = [x.strip().split(',') for x in foto]

    for lines_m in match:
        color_m = lines_m[1]
        Depth = lines_m[2]
        for lines_l in foto:
            ID = lines_l[0]
            color_l = lines_l[1]
            Lon = lines_l[3]
            Lat = lines_l[4]
            Time = lines_l[8]
            png = '{}/png/{}-{}.png'.format(project_dir, num, color_m)
            try:
                ans = abs(int(color_l) - int(color_m))
                if ans < 5:
                    info = '{},{},{},{},{},{},{},{}\n'.format(num, ID, color_m, Depth, Lat, Lon, Time, png)
                    tet.write(info)
                else:
                    # print 'no'
                    continue
            finally:
                pass


def pair_list():
    """Tkinter Button, loop through files in fotolog and create paired matcher.txt in shp folder"""
    global project_dir, tet,t
    list_dir = dir_generate(project_dir + '/list')
    foto_log = project_dir + '/foto_log'
    shp_dir = dir_generate(project_dir + '/shp')

    tet = open(shp_dir + '/matcher.txt', 'w')
    tet.write('weg_num,foto_id,Color,Depth,Lat,Lon,Uhrzeit,png_path\n')

    for log in os.listdir(foto_log):
        num = log.split('.')[0]
        try:
            pair(num)
        except IOError:
            print 'no file {}'.format(num)
        finally:
            pass

    t.insert(END, 'match list fertig\n')


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
    foto_shp.write('weg_num,foto_id,Color,Depth,Lon,Lat,png_path,Uhrzeit\n')
    for x in os.listdir(fotolog):
        file_name = '{}/{}'.format(fotolog, x)
        with open(file_name, 'r') as log:
            for data in log:
                data = data.split(',')
                foto_id, Color, Depth, Long, Lat, time = data[0], data[1], data[2], data[4], data[3], data[8]
                weg_nummer = x[:-4]
                path = '{}/png/{}-{}.png'.format(project_dir, weg_nummer, Color)
                shp_line = '{},{},{},{},{},{},{},{}'.format(weg_nummer, foto_id, Color, Depth, Long, Lat, path, time)
                foto_shp.write(shp_line)
        t.insert(END, 'processed {}\n'.format(x))
    foto_shp.close()
    arcpy.env.overwriteOutput = True
    spRef = 'WGS 1984'
    management.MakeXYEventLayer(shp_dir + '/Fotopunkte.txt', 'Lat', 'Lon', 'Fotopunkte', spRef)
    arcpy.FeatureClassToShapefile_conversion('Fotopunkte', shp_dir)
    t.insert(END, 'Fotopunkte.shp fertig\n')


def color_to_png(input_file):
    """create png with the input file in the folder png"""
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
            png_name = '{}/png/{}-{}.png'.format(projectdir, bagname[:-4], var)
            # print png_name
            exist = os.path.isfile(png_name)
            if exist:
                # print 'png exist'
                pass
            else:
                print 'compressing {}'.format(png_name)
                cv2.imwrite((png_name), color_cvt, [cv2.IMWRITE_PNG_COMPRESSION, 1])

    except RuntimeError:
        print 'frame covert finished for ' + input_file
        cv2.destroyAllWindows()
    finally:
        pass


def test_png():
    """Loop through all the bag files until all pngs were created
    if theres unreadable bag file it will keep on looping"""
    global project_dir,t
    png_dir = dir_generate(project_dir + '/png')
    try:
        while True:
            png_list = set([x.split('-')[0] for x in os.listdir(png_dir)])
            untransformed_list = []
            print png_list
            for bag in os.listdir(project_dir + '/bag'):
                if bag[:-4] in png_list:
                    # print 'png for {} existed'.format(bag)
                    pass
                else:
                    bag_full_path = '{}/bag/{}'.format(project_dir, bag)
                    untransformed_list.append(bag_full_path)
            if untransformed_list == []:
                print 'all transformed'
                break

            for x in untransformed_list:
                print x

            pool = mp.Pool()
            pool.map(color_to_png, untransformed_list)
    finally:
        print 'png fertig'
        t.insert(END, 'PNG fertig\n')

def from_bag_to_list():
    create_list()
    pair_list()
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
    b = Button(frame, text='select folder', height=2, command=lambda: get_dir(var))
    b.pack()
    l.pack()
    frame_2 = Frame(root, height=20, bd=5)
    frame_2.pack()
    frame_b = Frame(root)
    frame_b.pack()
    t = Text(frame_b, width=40, height=10)
    t.pack()

    Button(frame_2, text='generage shp', command=from_bag_to_list).grid(row=1, column=1)
    Button(frame_2, text='generate png', command=lambda: test_png()).grid(row=1, column=2)


    root.mainloop()


if __name__ == '__main__':
    main()
