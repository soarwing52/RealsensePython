import multiprocessing as mp
import pyrealsense2 as rs
import numpy as np
import cv2
import serial
import datetime
import time
import os, sys
from math import sin, cos, sqrt, atan2, radians
import threading


def dir_generate(dir_name):
    """
    :param dir_name: input complete path of the desired directory
    :return: None
    """
    dir_name = str(dir_name)
    if not os.path.exists(dir_name):
        try:
            os.mkdir(dir_name)
        finally:
            pass


def port_check(gps_on):
    """
    :param gps_on: when started it is False
    :return: when gps started correctly, return True, if error return 3, which will shut down the program
    """
    serialPort = serial.Serial()
    serialPort.baudrate = 4800
    serialPort.bytesize = serial.EIGHTBITS
    serialPort.parity = serial.PARITY_NONE
    serialPort.timeout = 2
    exist_port = None
    win = ['COM{}'.format(x) for x in range(10)]
    linux = ['/dev/ttyUSB{}'.format(x) for x in range(5)]
    for x in (win + linux):
        serialPort.port = x
        try:
            serialPort.open()
            serialPort.close()
            exist_port = x
        except serial.SerialException:
            pass
        finally:
            pass
    if exist_port:
        return exist_port
    else:
        print('close other programs using gps or check if the gps is correctly connected')
        gps_on.value = 3


def gps_dis(location_1, location_2):
    """
    this is the calculation of the distance between two long/lat locations
    input tuple/list
    :param location_1: [Lon, Lat]
    :param location_2: [Lon, Lat]
    :return: distance in meter
    """
    R = 6373.0

    lat1 = radians(location_1[1])
    lon1 = radians(location_1[0])
    lat2 = radians(location_2[1])
    lon2 = radians(location_2[0])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    distance = distance * 1000
    # print("Result:", distance)
    return distance


def min2decimal(in_data):
    """
    transform lon,lat from 00'00" to decimal
    :param in_data: lon / lat
    :return: in decimal poiints
    """
    latgps = float(in_data)
    latdeg = int(latgps / 100)
    latmin = latgps - latdeg * 100
    lat = latdeg + (latmin / 60)
    return lat


def gps_information(port):
    lon, lat = 0, 0
    try:
        while lon == 0 or lat == 0:
            line = port.readline()
            data = line.split(b',')
            data = [x.decode("UTF-8") for x in data]
            if data[0] == '$GPRMC':
                if data[2] == "A":
                    lat = min2decimal(data[3])
                    lon = min2decimal(data[5])
            elif data[0] == '$GPGGA':
                if data[6] == '1':
                    lon = min2decimal(data[4])
                    lat = min2decimal(data[2])
            time.sleep(1)
            #import random
            #if lon == 0 or lat == 0:
            #    lon, lat = random.random(), random.random()
        # print("return", lon, lat)
    except:
        print('decode error')

    return lon, lat


def GPS(Location, gps_on, root):
    """

    :param Location: mp.Array fot longitude, latitude
    :param gps_on: gps status 0 for resting, 1 for looking for signal, 2 for signal got, 3 for error
    :param root: root dir for linux at /home/pi
    :return:
    """
    print('GPS thread start')
    # Set port
    serialPort = serial.Serial()
    serialPort.port = port_check(gps_on)  # Check the available ports, return the valid one
    serialPort.baudrate = 4800
    serialPort.bytesize = serial.EIGHTBITS
    serialPort.parity = serial.PARITY_NONE
    serialPort.timeout = 2
    serialPort.open()
    print('GPS opened successfully')
    gps_on.value = 2
    lon, lat = gps_information(serialPort)
    gps_on.value = 1
    try:
        while gps_on.value != 99:
            lon, lat = gps_information(serialPort)
            Location[:] = [lon, lat]
            with open('{}location.csv'.format(root), 'w') as gps:
                gps.write('Lat,Lon\n')
                gps.write('{},{}'.format(lat, lon))
        # print(lon, lat)

    except serial.SerialException:
        print('Error opening GPS')
        gps_on.value = 3
    finally:
        serialPort.close()
        print('GPS finish')
        gps_on.value = 0


def Camera(child_conn, take_pic, frame_num, camera_status, bag):
    """

    :param child_conn: mp.Pipe for image
    :param take_pic: take pic command, 0 for rest, 1 for take one pic, after taken is 2, log file will turn back to 0
    :param frame_num: mp.Array for frame number
    :param camera_status: 0 for rest, 1 for running, 99 for end
    :param bag: bag path /home/pi/bag
    :return:
    """
    print('camera start')
    try:
        pipeline = rs.pipeline()
        config = rs.config()
        config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 15)
        config.enable_stream(rs.stream.color, 1920, 1080, rs.format.rgb8, 15)
        config.enable_record_to_file(bag)
        profile = pipeline.start(config)

        device = profile.get_device()  # get record device
        recorder = device.as_recorder()
        recorder.pause()  # and pause it

        # set frame queue size to max
        sensor = profile.get_device().query_sensors()
        for x in sensor:
            x.set_option(rs.option.frames_queue_size, 32)
        # set auto exposure but process data first
        color_sensor = profile.get_device().query_sensors()[1]
        color_sensor.set_option(rs.option.auto_exposure_priority, True)
        camera_status.value = 1
        while camera_status.value != 99:
            frames = pipeline.wait_for_frames()
            depth_frame = frames.get_depth_frame()
            color_frame = frames.get_color_frame()
            depth_color_frame = rs.colorizer().colorize(depth_frame)
            depth_image = np.asanyarray(depth_color_frame.get_data())
            color_image = np.asanyarray(color_frame.get_data())
            depth_colormap_resize = cv2.resize(depth_image, (400, 250))
            color_cvt = cv2.cvtColor(color_image, cv2.COLOR_RGB2BGR)
            color_cvt_2 = cv2.resize(color_cvt, (400, 250))
            img = np.vstack((color_cvt_2, depth_colormap_resize))
            child_conn.send(img)

            if take_pic.value == 1:
                recorder.resume()
                frames = pipeline.wait_for_frames()
                depth_frame = frames.get_depth_frame()
                color_frame = frames.get_color_frame()
                var = rs.frame.get_frame_number(color_frame)
                vard = rs.frame.get_frame_number(depth_frame)
                frame_num[:] = [var, vard]
                time.sleep(0.05)
                recorder.pause()
                print('taken', frame_num[:])
                take_pic.value = 2

        #child_conn.close()
        pipeline.stop()

    except RuntimeError:
        print('run')

    finally:
        print('pipeline closed')
        camera_status.value = 98
        print('camera value', camera_status.value)


def bag_num():
    """
    Generate the number of record file MMDD001
    :return:
    """
    num = 1
    now = datetime.datetime.now()
    time.sleep(1)

    try:
        while True:
            file_name = '{:02d}{:02d}_{:03d}'.format(now.month, now.day, num)
            bag_name = 'bag/{}.bag'.format(file_name)
            if sys.platform == 'linux':
                bag_name = "/home/pi/RR/" + bag_name
            exist = os.path.isfile(bag_name)
            if exist:
                num += 1
            else:
                print('current filename:{}'.format(file_name))
                break
        return file_name
    finally:
        pass


class RScam:
    def __init__(self):
        # Create Folders for Data
        if sys.platform == "linux":
            self.root_dir = '/home/pi/RR/'
        else:
            self.root_dir = ''

        folder_list = ('bag', 'foto_log')

        for folder in folder_list:
            dir_generate(self.root_dir + folder)
        # Create Variables between Processes
        self.Location = mp.Array('d', [0, 0])
        self.Frame_num = mp.Array('i', [0, 0])

        self.take_pic = mp.Value('i', 0)
        self.camera_command = mp.Value('i', 0)
        self.gps_status = mp.Value('i', 0)
        jpg_path = "/home/pi/RR/jpg.jpeg"
        if os.path.isfile(jpg_path):
            self.img = cv2.imread(jpg_path)
        else:
            self.img = cv2.imread('img/1.jpg')

        self.auto = False
        self.restart = True
        self.command = None
        self.distance = 15
        self.msg = 'waiting'

    def start_gps(self):
        # Start GPS process
        gps_process = mp.Process(target=GPS, args=(self.Location, self.gps_status, self.root_dir,))
        gps_process.start()

    def main_loop(self):
        parent_conn, child_conn = mp.Pipe()
        self.img_thread_status = True
        image_thread = threading.Thread(target=self.image_receiver, args=(parent_conn,))
        image_thread.start()
        while self.restart:
            self.msg = 'gps status: {}'.format(self.gps_status.value)
            if self.gps_status.value == 3:
                self.msg = 'error with gps'
                break
            elif self.gps_status.value == 2:
                time.sleep(1)
            elif self.gps_status.value == 1 and self.camera_command.value == 0:
                bag = bag_num()
                bag_name = "{}bag/{}.bag".format(self.root_dir, bag)
                cam_process = mp.Process(target=Camera, args=(child_conn, self.take_pic,
                                                              self.Frame_num, self.camera_command, bag_name))
                cam_process.start()
                self.command_receiver(bag)
                self.msg = 'end one round'
                #print('end one round')
        self.camera_command.value = 0
        self.gps_status.value = 99
        self.img_thread_status = False
        self.msg = "waiting"

    def image_receiver(self, parent_conn):
        while self.img_thread_status:
            try:
                self.img = parent_conn.recv()
            except EOFError:
                print('EOF')

        self.img = cv2.imread("img/1.jpg")
        print("img thread closed")

    def command_receiver(self, bag):
        i = 1
        foto_location = (0, 0)
        while self.camera_command.value != 98:
            #print('msg', self.msg)
            (lon, lat) = self.Location[:]
            current_location = (lon, lat)
            present = datetime.datetime.now()
            date = '{},{},{},{}'.format(present.day, present.month, present.year, present.time())
            local_take_pic = False

            if self.take_pic.value == 2:
                color_frame_num, depth_frame_num = self.Frame_num[:]
                print(color_frame_num, depth_frame_num)
                logmsg = '{},{},{},{},{},{}\n'.format(i, color_frame_num, depth_frame_num, lon, lat, date)
                #print('Foto {} gemacht um {:.03},{:.04}'.format(i, lon, lat))
                self.msg = 'Foto {} gemacht um {:.03},{:.04}'.format(i, lon, lat)
                with open('{}foto_log/{}.txt'.format(self.root_dir, bag), 'a') as logfile:
                    logfile.write(logmsg)
                with open('{}foto_location.csv'.format(self.root_dir), 'a') as record:
                    record.write(logmsg)
                foto_location = (lon, lat)
                i += 1
                self.take_pic.value = 0

            if self.take_pic.value in (1, 2) or current_location == foto_location:
                continue

            cmd = self.command

            if cmd == 'auto':
                self.auto = True
            elif cmd == "pause":
                self.auto = False
            elif cmd == "shot":
                print('take manual')
                local_take_pic = True
            elif cmd == "restart" or cmd == "quit":
                self.camera_command.value = 99
                self.msg = cmd
                print("close main", self.msg)

            self.command = None

            if self.auto and gps_dis(current_location, foto_location) > self.distance:
                local_take_pic = True

            if local_take_pic:
                self.take_pic.value = 1

        self.msg = 'main closed'
        print("main closed")
        self.camera_command.value = 0


if __name__ == '__main__':
    pass