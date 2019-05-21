import pyrealsense2 as rs
import numpy as np
import cv2
import serial
import datetime
import threading
import time
import os
from math import sin, cos, sqrt, atan2, radians
import simplekml

def write_kml(lon,lat):
    myfile = open('./kml/Foto.kml', 'r')
    doc=myfile.readlines()
    myfile.close()

    doc.insert(3,"""            <Placemark id="55855">
                    <name>point</name>
                    <Point id="3">
                        <coordinates>{},{},0.0</coordinates>
                    </Point>
                </Placemark>""".format(lon,lat))

    f = open('./kml/Foto.kml', 'w')
    contents = "".join(doc)
    f.write(contents)
    f.close()

def gps_dis(location_1,location_2):
    '''
    this is the calculation of the distance between two long/lat locations
    '''
    R = 6373.0

    lat1 = radians(location_1[1])
    lon1 = radians(location_1[0])
    lat2 = radians(location_2[1])
    lon2 = radians(location_2[0])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    distance = distance*1000
    #print("Result:", distance)
    return distance

def min2decimal(in_data):
    '''transforming the data of long lat '''
    latgps = float(in_data)
    latdeg = int(latgps / 100)
    latmin = latgps - latdeg * 100
    lat = latdeg + (latmin / 60)
    return lat

def GPS():
    '''
    the main function of starting the GPS
    '''
    print('GPS start')
    global camera_on, gps_on
    camera_on = True
    gps_on = True
    serialPort = serial.Serial()
    serialPort.port = 'COM7'
    serialPort.baudrate = 4800
    serialPort.bytesize = serial.EIGHTBITS
    serialPort.parity = serial.PARITY_NONE
    serialPort.timeout = 2
    serialPort.open()
    lon,lat = 0,0
    try:
        while True:
            line = serialPort.readline()
            data = line.split(",")
            present = datetime.datetime.now()
            date = '{},{},{},{}'.format(present.day, present.month, present.year, present.time())
            global gpsmsg, current_location
            if data[0] == '$GPRMC':
                if data[2] == "A":
                    lat = min2decimal(data[3])
                    lon = min2decimal(data[5])

                else:
                    print 'searching gps'

            elif data[0] == '$GPGGA':
                if data[6] == '1':
                    lon = min2decimal(data[4])
                    lat = min2decimal(data[2])
                else:
                    print 'searching gps'

            gpsmsg = '{},{},{},{}\n'.format(i, lat, lon, date)
            if not gpsmsg:
                continue
            current_location = [lon,lat]
            print 'gps ready, current location:{}'.format(current_location)
            with open('./kml/live.kml', 'w') as pos:
                googleearth_message = '''<?xml version="1.0" encoding="UTF-8"?>
                  <kml xmlns="http://www.opengis.net/kml/2.2">
                    <Placemark>
                      <name>Live Point</name>
                      <description>hi im here</description>
                      <Point>
                        <coordinates>{},{},0</coordinates>
                      </Point>
                    </Placemark>
                  </kml>'''.format(lon, lat)
                pos.write(googleearth_message)

            if gps_on is False:
                break
    finally:

        print('GPS finish')

def Camera(num,file_name):
    print 'Camera start'
    global camera_on, camera_repeat, gps_on
    camera_on = True
    camera_repeat = False
    fotolog = open('foto_log/fotolog_{}.txt'.format(num), 'a')
    global i,gpsmsg,current_location
    foto_location = [0,0]
    current_location =[0,0]
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)
    config.enable_stream(rs.stream.color, 1920, 1080, rs.format.rgb8, 30)
    config.enable_record_to_file(file_name)
    profile = pipeline.start(config)
    device = profile.get_device()
    recorder = device.as_recorder()
    recorder.pause()
    depth_sensor = device.first_depth_sensor()
    depth_sensor.set_option(rs.option.visual_preset, 4)
    dev_range = depth_sensor.get_option_range(rs.option.visual_preset)
    preset_name = depth_sensor.get_option_value_description(rs.option.visual_preset, 4)
    print preset_name
    sensor = profile.get_device().query_sensors()
    for x in sensor:
        print x
        x.set_option(rs.option.frames_queue_size, 32)
    color_sensor = profile.get_device().query_sensors()[1]
    color_sensor.set_option(rs.option.auto_exposure_priority, False)


    try:
        while True:
            frames = pipeline.wait_for_frames()
            depth_frame = frames.get_depth_frame()
            color_frame = frames.get_color_frame()
            if not depth_frame or not color_frame:
                continue

            depth_image = np.asanyarray(depth_frame.get_data())
            depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
            depth_colormap_resize = cv2.resize(depth_colormap,(848,480))
            color_image = np.asanyarray(color_frame.get_data())
            color_cvt = cv2.cvtColor(color_image, cv2.COLOR_RGB2BGR)
            color_cvt_2 = cv2.resize(color_cvt, (640,480))
            images = np.hstack((color_cvt_2, depth_colormap_resize))
            cv2.namedWindow('Color', cv2.WINDOW_AUTOSIZE)
            cv2.imshow('Color', images)
            key = cv2.waitKey(1)

            if key == 32 or gps_dis(current_location,foto_location) > 15:
                recorder.resume()
                var = rs.frame.get_frame_number(color_frame)
                vard = rs.frame.get_frame_number(depth_frame)
                time.sleep(0.033)
                logmsg = '{},{},{},{}'.format(i, str(var), str(vard), gpsmsg)
                fotolog.write(logmsg)
                log_list = logmsg.split(',')
                foto_location = [float(log_list[5]),float(log_list[4])]
                print 'photo taken at:{}'.format(foto_location)
                recorder.pause()
                saver = rs.save_single_frameset('./frameset/{}_{}_'.format(num, i))
                saver.process(frames)
                write_kml(float(log_list[5]),float(log_list[4]))
                i += 1
                continue

            elif key & 0xFF == ord('q') or key == 27:
                cv2.destroyAllWindows()
                camera_on = False
                gps_on = False
                camera_repeat = False
                break
            elif key == 114:
                cv2.destroyAllWindows()
                camera_on = False
                camera_repeat = True
                break

    finally:
        print('Camera finish\n')

        fotolog.close()
        pipeline.stop()

def dir_generate(dir_name):
    dir_name = str(dir_name)
    if not os.path.exists(dir_name):
        try:
            os.makedirs(dir_name, 0o700)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

def camera_loop():
    global i, camera_repeat
    i = 1
    num = 1
    camera_repeat = True
    try:
        while True:
            file_name = 'bag/{}.bag'.format(num)
            exist = os.path.isfile(file_name)
            if exist:

                num+=1
            else:
                print file_name
                try:
                    while camera_repeat is True:
                        print num
                        file_name = 'bag/{}.bag'.format(num)
                        Camera(num,file_name)
                        num +=1
                finally:
                    print 'exit camera'
                break
    finally:
        print 'camera finish'


def main():
    dir_generate('bag')
    dir_generate('foto_log')
    dir_generate('gps_log')
    dir_generate('frameset')
    dir_generate('kml')

    kml = simplekml.Kml()
    kml.newpoint(name='point', coords = [(9.0,52.0)])
    kml.save('./kml/Foto.kml')

    gps_thread = threading.Thread(target=GPS, name='T1')
    camera_thread = threading.Thread(target=camera_loop, name='T2')
    gps_thread.start()
    camera_thread.start()
    camera_thread.join()
    gps_thread.join()
    print('all done\n')


if __name__ == '__main__':
    main()
