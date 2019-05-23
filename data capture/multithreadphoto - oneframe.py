import pyrealsense2 as rs
import numpy as np
import cv2
import serial
import datetime
import threading
import time
import os
from math import sin, cos, sqrt, atan2, radians


def gps_dis(location_1,location_2):
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
    latgps = float(in_data)
    latdeg = int(latgps / 100)
    latmin = latgps - latdeg * 100
    lat = latdeg + (latmin / 60)
    return lat

def GPS(num):
    print('GPS start')
    global camera_on
    camera_on = True
    gpslog = open('gps_log/gpslog_{}.txt'.format(num), 'a')
    serialPort = serial.Serial()
    serialPort.port = 'COM7'
    serialPort.baudrate = 4800
    serialPort.bytesize = serial.EIGHTBITS
    serialPort.parity = serial.PARITY_NONE
    serialPort.timeout = 2
    serialPort.open()
    try:
        while True:
            line = serialPort.readline()
            data = line.split(",")
            present = datetime.datetime.now()
            date = '{},{},{},{}'.format(present.day, present.month, present.year, present.time())
            if data[0] == '$GPRMC':
                if data[2] == "A":
                    lat = min2decimal(data[3])
                    lon = min2decimal(data[5])
                    global gpsmsg,current_location
                    gpsmsg = '{},{},{},{},{},{}\n'.format(i, data[4], lat, data[6], lon, date)
                    if not gpsmsg:
                        continue
                    current_location = [lon,lat ]
                    print 'gps ready, current location:{}'.format(current_location)
                    gpslog.write(gpsmsg)
                    with open('live.kml', 'w') as pos:
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
            elif camera_on==False:
                break
    finally:
        gpslog.close()
        print('GPS finish')

def Camera(num,file_name):
    print 'Camera start'
    global camera_on
    camera_on = True
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
    rs.recorder.pause(recorder)
    depth_sensor = device.first_depth_sensor()
    depth_sensor.set_option(rs.option.visual_preset, 4)
    dev_range = depth_sensor.get_option_range(rs.option.visual_preset)
    preset_name = depth_sensor.get_option_value_description(rs.option.visual_preset, 4)
    print preset_name
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

            if key == 32:
                rs.recorder.resume(recorder)
                var = rs.frame.get_frame_number(color_frame)
                vard = rs.frame.get_frame_number(depth_frame)
                time.sleep(0.02)
                logmsg = '{},{},{},{}'.format(i, str(var), str(vard), gpsmsg)
                fotolog.write(logmsg)
                log_list = logmsg.split(',')
                foto_location = [float(log_list[7]),float(log_list[5])]
                print 'photo taken at:{}'.format(foto_location)
                rs.recorder.pause(recorder)
                saver = rs.save_single_frameset('./frameset/{}_{}_'.format(num, i))
                saver.process(frames)
                i += 1
                continue
            elif gps_dis(current_location,foto_location) > 15:
                print 'auto picture taken,distance:{}'.format(gps_dis(current_location,foto_location))
                rs.recorder.resume(recorder)
                var = rs.frame.get_frame_number(color_frame)
                vard = rs.frame.get_frame_number(depth_frame)
                time.sleep(0.02)
                logmsg = '{},{},{},{}'.format(i, str(var), str(vard), gpsmsg)
                fotolog.write(logmsg)
                log_list = logmsg.split(',')
                foto_location = [float(log_list[7]),float(log_list[5])]
                print 'photo taken at:{}'.format(foto_location)
                rs.recorder.pause(recorder)
                saver = rs.save_single_frameset('./frameset/{}_{}_'.format(num,i))
                saver.process(frames)
                i += 1
                continue

            elif key & 0xFF == ord('q') or key == 27:
                cv2.destroyAllWindows()
                camera_on = False
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


def main():
    num = 1
    dir_generate('bag')
    dir_generate('foto_log')
    dir_generate('gps_log')
    dir_generate('frameset')

    try:
        while True:
            file_name = 'bag/{}.bag'.format(num)
            exist = os.path.isfile(file_name)
            if exist:
                num+=1
            else:
                print file_name
                break

    finally:
        global i
        i=1
        gps_thread = threading.Thread(target=GPS, name='T1',args=(num,))
        camera_thread = threading.Thread(target=Camera, name='T2',args=(num,file_name,))
        gps_thread.start()
        camera_thread.start()
        camera_thread.join()
        gps_thread.join()
        print('all done\n')


if __name__ == '__main__':
    main()
