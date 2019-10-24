# -*- coding: utf-8 -*-
import sys, time
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QTimer, QThread, pyqtSignal
from PyQt5.QtWidgets import QFileDialog
from gui2 import Ui_MainWindow

import sys
import numpy as np
import cv2
import multiprocessing as mp
import threading
import os
import piexif
from fractions import Fraction
from queue import Queue


RUNNING = False


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
    deg = int(abs_value)
    t1 = (abs_value - deg) * 60
    min = int(t1)
    sec = round((t1 - min) * 60, 5)
    return deg, min, sec, loc_value


def change_to_rational(number):
    """convert a number to rational
    Keyword arguments: number
    return: tuple like (1, 2), (numerator, denominator)
    """
    f = Fraction(str(number))
    return f.numerator, f.denominator


def generate_jpg(project_dir, q):
    """Loop through all the bag files until all jpgs were created
    if theres unreadable bag file it will keep on looping"""
    bag_dir = project_dir + '/bag'
    global RUNNING
    RUNNING = True
    try:
        for i in range(2):
            x = [os.path.join(bag_dir, bag) for bag in os.listdir(bag_dir)]
            pool = mp.Pool()
            count = 0
            for result in pool.imap_unordered(color_to_jpg, x):
                count += 1
                q.put(count * 100 / len(x))


            #pool.map(color_to_jpg, x)

    finally:
        print('jpg fertig')
        RUNNING = False


def color_to_jpg(input_file):
    """create jpg with the input file in the folder jpg"""
    import pyrealsense2 as rs
    try:
        #print(input_file)
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
                #print('compressing {}'.format(jpg_name))
                kernel = np.array([[0, -1, 0],
                                   [-1, 5, -1],
                                   [0, -1, 0]])
                sharpened = cv2.filter2D(color_cvt, -1,kernel)  # applying the sharpening kernel to the input image & displaying it.
                cv2.imwrite((jpg_name), sharpened, [cv2.IMWRITE_JPEG_QUALITY,100])
    except RuntimeError:
        pass
    finally:
        print('frame covert finished for ' + input_file)
        pipeline.stop()



class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent=parent)
        self.setupUi(self)
        self.dir_button.clicked.connect(lambda: self.get_prjdir_dialog())
        self.make_jpg.clicked.connect(lambda: self.generate_jpg_button())
        self.make_list.clicked.connect(lambda: self.pair_list())
        self.geotag.clicked.connect(lambda: self.geotag_thread())

        self.msg = QtWidgets.QMessageBox()
        self.msg.setWindowTitle('Warning')
        self.msg.setIcon(QtWidgets.QMessageBox.Information)

    def get_prjdir_dialog(self):
        self.prj_dir = QFileDialog.getExistingDirectory()
        self.project_lable.setText(self.prj_dir)
        self.project_lable.adjustSize()

    def dir_generate(self, in_dir):
        """exmaine if this folder exist, if not, create one"""
        in_dir = str(in_dir)
        if not os.path.exists(in_dir):
            try:
                os.makedirs(in_dir, 0o700)
            except WindowsError:
                print('already exist')
            finally:
                pass
        return in_dir

    def generate_jpg_button(self):
        self.dir_generate(self.prj_dir+'/jpg')
        if not RUNNING:
            self.t_jpg = JPGThread()
            self.t_jpg.set_dir(self.prj_dir)
            self.t_jpg.start()
            self.t_jpg.update_progressbar.connect(self.update_progressbar)
            self.t_jpg.msg.connect(self.message_reciever)
        else:
            self.msg.setText('still creating JPG')
            self.msg.exec_()

    def pair(self, num):
        """match fotolog and existing photos, with the accuracy of +-5 frames"""
        project_dir = self.prj_dir
        with open('{}/foto_log/{}.txt'.format(project_dir, num), 'r') as foto:
            foto = [x.strip().split(',') for x in foto]

        self.written_lonlat = [0, 0]
        for lines_l in foto:
            ID = lines_l[0]
            color_l = lines_l[1]
            Depth = lines_l[2]
            Lon = lines_l[3]
            Lat = lines_l[4]
            Time = lines_l[8]

            for i in range(-5, 5):
                ans = int(color_l) + i
                if os.path.isfile('{}/jpg/{}-{}.jpg'.format(project_dir, num, ans)) and [Lat, Lon] != self.written_lonlat:
                    jpg = '{}/jpg/{}-{}.jpg'.format(project_dir, num, ans)
                    info = '{},{},{},{},{},{},{},{}\n'.format(num, ID, ans, Depth, Lat, Lon, Time, jpg)
                    with open(project_dir + '/shp/matcher.txt', 'a') as txt:
                        txt.write(info)
                    self.written_lonlat = [Lat, Lon]
        #print(num + ' done')

    def pair_list(self):
        """Tkinter Button, loop through files in fotolog and create paired matcher.txt in shp folder"""
        global RUNNING
        project_dir = self.prj_dir
        foto_log = project_dir + '/foto_log'
        shp_dir = self.dir_generate(project_dir + '/shp')
        RUNNING = True
        with open(shp_dir + '/matcher.txt', 'w') as txt:
            txt.write('weg_num,foto_id,Color,Depth,Lat,Lon,Uhrzeit,jpg_path\n')
        source = os.listdir(foto_log)
        total = len(source)
        for i, log in enumerate(source):
            num = log.split('.')[0]
            try:
                self.pair(num)
                self.update_progressbar(i*100/total)
                self.statusbar.showMessage(num)
            except IOError:
                print('no file {}'.format(num))
            finally:
                pass
        print('pair list done')
        RUNNING = False
        self.update_progressbar(100)
        self.textBrowser.append('List fertig')

    def geotag_thread(self):
        if not RUNNING:
            self.t_geotag = GeotagThread()
            self.t_geotag.prj(self.prj_dir)
            self.t_geotag.start()
            self.t_geotag.update_progressbar.connect(self.update_progressbar)
            self.t_geotag.msg.connect(self.message_reciever)
        else:
            self.msg.setText('still geotagging')
            self.msg.exec_()

    def update_progressbar(self, val):
        self.progressBar.setValue(val)

    def message_reciever(self, msg):
        if 'Error' in msg or 'fertig' in msg:
            self.textBrowser.append(msg)
        self.statusbar.showMessage(msg)

class JPGThread(QThread):
    update_progressbar = pyqtSignal(float)
    msg = pyqtSignal(str)
    def __int__(self, parent=None):
        super(JPGThread, self).__init__(parent)

    def run(self):
        q = Queue()
        t1 = threading.Thread(target=generate_jpg, args=(self.prj_dir,q))
        t1.start()
        while RUNNING:
            x = q.get()
            self.update_progressbar.emit(x)
        self.update_progressbar.emit(100)
        self.msg.emit('JPG fertig')

    def set_dir(self,stt):
        self.prj_dir = stt

class GeotagThread(QThread):
    update_progressbar = pyqtSignal(float)
    msg = pyqtSignal(str)
    def __int__(self, parent=None):
        super(GeotagThread, self).__init__(parent)

    def run(self):
        global RUNNING
        RUNNING = True
        project_dir = self.prj_dir
        print('start geotag')
        fotolog = project_dir + '/shp/matcher.txt'
        jpg_dir = project_dir + '/jpg'
        total = len(os.listdir(jpg_dir))
        current = 0

        with open(fotolog, 'r') as log:
            log.readline()
            for y in log:
                data = y.split(',')
                weg_num, frame, Lat, Lon = data[0], data[2], float(data[4]), float(data[5])
                jpgname = '{}/{}-{}.jpg'.format(jpg_dir, weg_num, frame)
                self.msg.emit(jpgname)
                try:
                    set_gps_location(jpgname, Lat, Lon, 0)
                    current += 1
                    self.update_progressbar.emit(current*100/total)
                except:
                    print(jpgname + ' not found')
                    self.msg.emit('Error: {} broken image'.format(jpgname))
                finally:
                    pass
        print('tagged')
        self.update_progressbar.emit(100)
        self.msg.emit('Geotag fertig')
        RUNNING = False

    def prj(self, stt):
        self.prj_dir = stt



if __name__ == "__main__":
    mp.freeze_support()
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())