# -*- coding: utf-8 -*-
from  Tkinter import *
import tkFileDialog
import os
import arcpy
from arcpy import management
import pyrealsense2 as rs
import numpy as np
import cv2
import multiprocessing as mp


class trans:
    def __init__(self,root):
        frame = Frame(root, bd= 5)
        frame.pack()
        s_var = StringVar()
        l = Label(frame, textvariable=s_var,bg='white', bd=5, width=40)
        b = Button(frame, text='select folder',height= 2, command= lambda: self.get_dir(s_var))
        b.pack()
        l.pack()
        frame_2 = Frame(root,height= 20,bd=5)
        frame_2.pack()
        frame_b =Frame(root)
        frame_b.pack()
        t = Text(frame_b,width= 40, height=10)
        t.pack()

        Fotorun = Button(frame_2, text='generate Foto shp', command=lambda: self.foto_txt(t)).grid(row=1, column=1)
        GPSrun = Button(frame_2, text='generate Gps shp', command=lambda: self.gps_txt(t)).grid(row=1, column=2)
        png = Button(frame_2, text='generate png', command= lambda: self.loop_png(t)).grid(row=1, column=3)


    def get_dir(self,var):
        self.dir_name = tkFileDialog.askdirectory()
        var.set(self.dir_name)
        print self.dir_name
        self.project_path =str(self.dir_name)
        self.bag_path = self.project_path + '/bag'
        self.foto_path = self.project_path + '/foto_log'
        self.gps_path = self.project_path + '/gps_log'
        self.png_path = self.project_path + '/png'
        self.shp_path = self.project_path + '/shp'
        self.dir_generate(self.shp_path)
        self.dir_generate(self.png_path)
        return self.project_path

    def dir_generate(self,dir_name):
        dir_name = str(dir_name)
        if not os.path.exists(dir_name):
            try:
                os.makedirs(dir_name, 0o700)

            finally:
                return

    def foto_txt(self,t):
        foto_txt =open(self.shp_path+'/Foto.txt','w')
        foto_txt.write('weg_num,foto_id,Color,Depth,X,Y,png_path,time\n')
        for f_logs in os.listdir(self.foto_path):
            filename = self.foto_path + '/' + f_logs
            print f_logs
            with open(filename, 'r') as logs:
                for lines in logs:
                    data = lines.split(',')
                    Long = data[7]
                    Lat = data[5]
                    weg_nummer = f_logs[8:-4]
                    path = '{}/png/{}-{}.png'.format(self.project_path, weg_nummer, data[1])
                    shp_line = '{},{},{},{},{},{},{},{}'.format(weg_nummer, data[0], data[1], data[2], Long, Lat, path,
                                                                data[11])
                    foto_txt.write(shp_line)
        foto_txt.close()
        print 'foto.txt fertig\n'
        t.insert(END,'foto.txt fetig\n' )
        arcpy.env.overwriteOutput = True
        spRef = 'WGS 1984'
        a = management.MakeXYEventLayer(self.project_path + '/shp/Foto.txt', 'X', 'Y', 'Fotopunkte', spRef)
        print a
        arcpy.FeatureClassToShapefile_conversion('Fotopunkte', self.project_path + '/shp')
        print 'Fotopunkte.shp fertig\n'
        t.insert(END, 'Fotopunkte.shp fertig\n')


    def gps_txt(self,t):
        gps_txt = open(self.shp_path + '/gps.txt', 'w')
        gps_txt.write('X,Y\n')
        for g_log in os.listdir(self.gps_path):
            file_name = self.gps_path + '/' + g_log
            print file_name

            with open(file_name, 'r') as logs:
                for lines in logs:
                    data = lines.split(',')
                    Long = data[4]
                    Lat = data[2]
                    print data
                    shp_line = '{},{}\n'.format(Long, Lat)
                    print shp_line
                    gps_txt.write(shp_line)
        gps_txt.close()
        print 'gps.txt fetig'
        t.insert(END,'gps.txt fetig\n' )
        arcpy.env.workspace = self.project_path + '/shp'
        arcpy.env.overwriteOutput = True
        spRef = 'WGS 1984'
        a = management.MakeXYEventLayer(self.project_path + '/shp/gps.txt', 'X', 'Y', 'GPSpunkte', spRef)
        print a
        arcpy.FeatureClassToShapefile_conversion('GPSpunkte', self.project_path + '/shp')
        print 'GPSpunkte.shp fertig\n'
        t.insert(END, 'GPSpunkte.shp fertig\n')

    def loop_png(self,t):
        processes = []
        project_path = str(self.project_path)
        bag_dir = project_path + '/bag'
        for bags in os.listdir(bag_dir):
            path = bag_dir + '/' + bags
            p = mp.Process(target=self.color_to_png, args=(path,))
            processes.append(p)
            p.start()

        for process in processes:
            process.join()
            print 'joined {}'.format(process)

        print 'png done'
        t.insert(END, 'png fertig\n')

    def color_to_png(self,input_file):
        print 'start color to png'
        print input_file
        bagname = os.path.basename(input_file)
        bagdir = os.path.dirname(input_file)
        projectdir = os.path.dirname(bagdir)
        print bagname, bagdir, projectdir
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
                print 'compressing {}-{}.png'.format(bagname[:-4], str(var))
                cv2.imwrite('{}/png/{}-{}.png'.format(projectdir, bagname[:-4], str(var)), color_cvt,
                            [cv2.IMWRITE_PNG_COMPRESSION, 1])
                key = cv2.waitKey(100)
                # if pressed escape exit program
                if key == 27:
                    cv2.destroyAllWindows()
                    break

        except RuntimeError:
            print 'frame covert finished for ' + input_file
            cv2.destroyAllWindows()
        finally:
            pass


def main():
    root = Tk()
    root.title('shapefile generator')
    root.geometry('470x305')
    trans(root)
    root.mainloop()

if __name__ == '__main__':
    main()