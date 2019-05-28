import pyrealsense2 as rs
import numpy as np
import cv2
import serial
import datetime
import threading
import time
import os
from math import sin, cos, sqrt, atan2, radians

def port_check():
    serialPort = serial.Serial()
    serialPort.baudrate = 4800
    serialPort.bytesize = serial.EIGHTBITS
    serialPort.parity = serial.PARITY_NONE
    serialPort.timeout = 2
    exist_port = None
    for x in range(1, 10):
        portnum = 'COM{}'.format(x)
        serialPort.port = 'COM{}'.format(x)
        try:
            serialPort.open()
            serialPort.close()
            exist_port = portnum
        except serial.SerialException:
            pass
        finally:
            pass
    if exist_port:
        return exist_port
    else:
        print 'close other programs using gps'
        raw_input('press enter to leave')
        os._exit(0)

def emptykml():
    kml = os.path.exists('./kml/Foto.kml')
    if kml:
        return
    else:
        with open('./kml/Foto.kml' , 'w') as kml:
            text = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2">
    <Document id="1">

    </Document>
</kml>
    """
            kml.write(text)


def dir_generate(dir_name):
    dir_name = str(dir_name)
    if not os.path.exists(dir_name):
        try:
            os.makedirs(dir_name, 0o700)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise


def write_kml(lon,lat):
    """
    To append a point in kml
    :param lon:
    :param lat:
    :return:
    """
    myfile = open('./kml/Foto.kml', 'r')
    doc=myfile.readlines()
    myfile.close()

    doc.insert(3,"""            <Placemark id="foto">
                    <name>P</name>
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
    global camera_on, gps_on, current_location, lon, lat
    gps_on = False
    print('GPS start')
    serialPort = serial.Serial()
    serialPort.port = port_check()
    serialPort.baudrate = 4800
    serialPort.bytesize = serial.EIGHTBITS
    serialPort.parity = serial.PARITY_NONE
    serialPort.timeout = 2
    serialPort.open()
    print 'GPS opened successfully'


    gps_on = True
    lon, lat = 0, 0
    try:
        while True:
            line = serialPort.readline()
            data = line.split(",")


            if data[0] == '$GPRMC':
                if data[2] == "A":
                    lat = min2decimal(data[3])
                    lon = min2decimal(data[5])

                else:
                    #print 'searching gps'
                    pass

            elif data[0] == '$GPGGA':
                if data[6] == '1':
                    lon = min2decimal(data[4])
                    lat = min2decimal(data[2])
                else:
                    #print 'searching gps'
                    pass

            if lon ==0 or lat == 0:
                print 'gps not ready'

            else:
                current_location = (lon,lat)
                #print 'gps ready, current location:{}'.format(current_location)

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
    except serial.SerialException:
        print 'Error opening GPS'
        gps_on = False
    finally:
        serialPort.close()
        print('GPS finish')

def Camera(file_name):
    print 'Camera start'
    global camera_on, camera_repeat, gps_on,i,gpsmsg,current_location, lon, lat
    camera_on = True
    camera_repeat = False
    foto_location = [0,0]
    current_location = [0,0]
    i = 1

    bag_name = './bag/{}.bag'.format(file_name)
    fotolog = open('foto_log/{}.txt'.format(file_name), 'w')

    # set configurations and start
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)
    config.enable_stream(rs.stream.color, 1920, 1080, rs.format.rgb8, 30)
    config.enable_record_to_file(bag_name)
    profile = pipeline.start(config)
    # get record device and pause it
    device = profile.get_device()
    recorder = device.as_recorder()
    recorder.pause()
    # get sensor and set to high density
    depth_sensor = device.first_depth_sensor()
    depth_sensor.set_option(rs.option.visual_preset, 4)
    dev_range = depth_sensor.get_option_range(rs.option.visual_preset)
    preset_name = depth_sensor.get_option_value_description(rs.option.visual_preset, 4)
    print preset_name
    # set frame queue size to max
    sensor = profile.get_device().query_sensors()
    for x in sensor:
        x.set_option(rs.option.frames_queue_size, 32)
    # set auto exposure but process data first
    color_sensor = profile.get_device().query_sensors()[1]
    color_sensor.set_option(rs.option.auto_exposure_priority, True)
    try:
        while True:
            present = datetime.datetime.now()
            date = '{},{},{},{}'.format(present.day, present.month, present.year, present.time())
            frames = pipeline.wait_for_frames()
            depth_frame = frames.get_depth_frame()
            color_frame = frames.get_color_frame()
            if not depth_frame or not color_frame:
                continue
            key = cv2.waitKey(1)
            if key == 32 or gps_dis(current_location,foto_location) > 15:
                start = time.time()
                recorder.resume()
                time.sleep(0.05)
                frames = pipeline.wait_for_frames()
                depth_frame = frames.get_depth_frame()
                color_frame = frames.get_color_frame()
                var = rs.frame.get_frame_number(color_frame)
                vard = rs.frame.get_frame_number(depth_frame)
                foto_location = (lon,lat)
                print 'photo taken at:{}'.format(foto_location)
                recorder.pause()
                logmsg = '{},{},{},{},{},{}\n'.format(i, str(var), str(vard), lon, lat, date)
                fotolog.write(logmsg)
                end = time.time()
                print end - start
                write_kml(lon,lat)
                i += 1
                continue

            elif key & 0xFF == ord('q') or key == 27:
                cv2.destroyAllWindows()
                camera_on = False
                gps_on = False
                camera_repeat = False
                print('Camera finish\n')
                break
            elif key == 114:
                cv2.destroyAllWindows()
                camera_on = False
                camera_repeat = True
                print 'camera will restart'
                break
            elif gps_on is False:
                cv2.destroyAllWindows()
                camera_repeat = False
                break

            depth_color_frame = rs.colorizer().colorize(depth_frame)
            depth_image = np.asanyarray(depth_color_frame.get_data())
            depth_colormap_resize = cv2.resize(depth_image,(424,240))
            color_image = np.asanyarray(color_frame.get_data())
            color_cvt = cv2.cvtColor(color_image, cv2.COLOR_RGB2BGR)
            color_cvt_2 = cv2.resize(color_cvt, (320,240))
            images = np.hstack((color_cvt_2, depth_colormap_resize))
            cv2.namedWindow('Color', cv2.WINDOW_AUTOSIZE)
            cv2.imshow('Color', images)

    except NameError:
        os._exit(0)

    finally:
        fotolog.close()
        pipeline.stop()



def camera_loop():
    global camera_repeat, gps_on
    num = 1
    camera_repeat = True
    now = datetime.datetime.now()
    time.sleep(1)
    try:
        while gps_on is False:
            if gps_on is True:
                break
    finally:
        print 'Starting Camera'

    try:
        while gps_on is True:
            file_name = '{:02d}{}_{:03d}'.format(now.month, now.day, num)
            bag_name = './bag/{}.bag'.format(file_name)
            exist = os.path.isfile(bag_name)
            if exist:
                num+=1
            elif camera_repeat == False:
                break
            else:
                print 'current filename:{}'.format(file_name)
                Camera(file_name)
                continue

    finally:
        pass


def main():
    folder_list = ('bag','foto_log','kml')
    for folder in folder_list:
        dir_generate(folder)

    emptykml()

    gps_thread = threading.Thread(target=GPS, name='T1')
    camera_thread = threading.Thread(target=camera_loop, name='T2')
    gps_thread.start()
    camera_thread.start()
    camera_thread.join()
    gps_thread.join()
    print('all done\n')


if __name__ == '__main__':
    main()
