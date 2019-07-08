import pyrealsense2 as rs
import numpy as np
import cv2
import serial
import datetime
import time
import os
from math import sin, cos, sqrt, atan2, radians
from getch import pause_exit
from multiprocessing import Process,Value, Array, Pipe


def dir_generate(dir_name):
    dir_name = str(dir_name)
    if not os.path.exists(dir_name):
        try:
            os.makedirs(dir_name, 0o700)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise


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
        print ('close other programs using gps')
        pause_exit(status=0, message='Press any key to leave')
        os._exit(0)


def emptykml():
    kml = os.path.exists('./kml/Foto.kml')
    if kml:
        return
    else:
        with open('./kml/Foto.kml' , 'w') as kml:
            text = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2" xmlns:kml="http://www.opengis.net/kml/2.2" xmlns:atom="http://www.w3.org/2005/Atom">
<Document id="1">
	<name>Foto.kml</name>
	<open>1</open>
	<Style id="s_ylw-pushpin">
		<IconStyle>
			<color>ff00ffff</color>
			<scale>0.8</scale>
			<Icon>
				<href>http://maps.google.com/mapfiles/kml/shapes/target.png</href>
			</Icon>
		</IconStyle>
		<ListStyle>
		</ListStyle>
	</Style>
	<Style id="s_ylw-pushpin_hl">
		<IconStyle>
			<color>ff00ffff</color>
			<scale>0.945455</scale>
			<Icon>
				<href>http://maps.google.com/mapfiles/kml/shapes/target.png</href>
			</Icon>
		</IconStyle>
		<ListStyle>
		</ListStyle>
	</Style>
	<StyleMap id="m_ylw-pushpin">
		<Pair>
			<key>normal</key>
			<styleUrl>#s_ylw-pushpin</styleUrl>
		</Pair>
		<Pair>
			<key>highlight</key>
			<styleUrl>#s_ylw-pushpin_hl</styleUrl>
		</Pair>
	</StyleMap>
	</Document>
	</kml>
    """
            kml.write(text)


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

    doc.insert(37,"""            <Placemark id="foto">
                    <name>P</name>
                    <styleUrl>#m_ylw-pushpin</styleUrl>
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
    input tuple/list
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


def GPS(Location,gps_on):
    '''
    the main function of starting the GPS
    '''
    print('GPS start')
    serialPort = serial.Serial()
    serialPort.port = port_check()
    serialPort.baudrate = 4800
    serialPort.bytesize = serial.EIGHTBITS
    serialPort.parity = serial.PARITY_NONE
    serialPort.timeout = 2
    serialPort.open()
    print ('GPS opened successfully')
    gps_on.value = True
    lon, lat = 0, 0
    try:
        while True:
            line = serialPort.readline()
            data = line.split(b',')
            data = [x.decode("UTF-8") for x in data]

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
                print ('gps signal not ready')

            else:
                #print ('gps ready, current location:{},{}'.format(lon,lat))
                Location[:] = [lon,lat]

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

            if gps_on.value is False:
                break
    except serial.SerialException:
        print ('Error opening GPS')
        gps_on.value = False
    finally:
        serialPort.close()
        print('GPS finish')


def Camera(child_conn, pic, Frame_num, camera_on, bag):
    print('camera start')
    bag_name = './bag/{}.bag'.format(bag)
    camera_on.value = True
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)
    config.enable_stream(rs.stream.color, 1920, 1080, rs.format.rgb8, 30)
    config.enable_record_to_file(bag_name)
    profile = pipeline.start(config)

    device = profile.get_device() # get record device
    recorder = device.as_recorder()
    recorder.pause() # and pause it

    # get sensor and set to high density
    depth_sensor = device.first_depth_sensor()
    depth_sensor.set_option(rs.option.visual_preset, 4)
    # dev_range = depth_sensor.get_option_range(rs.option.visual_preset)
    preset_name = depth_sensor.get_option_value_description(rs.option.visual_preset, 4)
    print (preset_name)
    # set frame queue size to max
    sensor = profile.get_device().query_sensors()
    for x in sensor:
        x.set_option(rs.option.frames_queue_size, 32)
    # set auto exposure but process data first
    color_sensor = profile.get_device().query_sensors()[1]
    color_sensor.set_option(rs.option.auto_exposure_priority, True)

    try:
        while True:
            frames = pipeline.wait_for_frames()
            depth_frame = frames.get_depth_frame()
            color_frame = frames.get_color_frame()
            depth_color_frame = rs.colorizer().colorize(depth_frame)
            depth_image = np.asanyarray(depth_color_frame.get_data())
            color_image = np.asanyarray(color_frame.get_data())
            child_conn.send((color_image, depth_image))

            take_pic = pic.value
            if take_pic == 1:
                recorder.resume()
                frames = pipeline.wait_for_frames()
                depth_frame = frames.get_depth_frame()
                color_frame = frames.get_color_frame()
                var = rs.frame.get_frame_number(color_frame)
                vard = rs.frame.get_frame_number(depth_frame)
                Frame_num[:] = [var,vard]
                time.sleep(0.05)
                #print ('photo taken')
                recorder.pause()

                pic.value = False
                continue

            elif camera_on.value == 0:
                child_conn.close()
                break

    except RuntimeError:
        print ('run')

    finally:
        print('pipeline stop')
        pipeline.stop()


def Show_Image(bag, parent_conn, take_pic, Frame_num, camera_on, camera_repeat, gps_on, Location):
    Pause = False
    i = 1
    foto_location = (0, 0)
    foto_frame = Frame_num[0]
    logfile = open('./foto_log/{}.txt'.format(bag),'w')
    try:
        while True:
            (lon, lat) = Location[:]
            current_location = (lon, lat)
            present = datetime.datetime.now()
            date = '{},{},{},{}'.format(present.day, present.month, present.year, present.time())

            color_image,depth_image = parent_conn.recv()
            depth_colormap_resize = cv2.resize(depth_image, (424, 240))
            color_cvt = cv2.cvtColor(color_image, cv2.COLOR_RGB2BGR)
            color_cvt_2 = cv2.resize(color_cvt, (320, 240))
            images = np.hstack((color_cvt_2, depth_colormap_resize))
            cv2.namedWindow('Color', cv2.WINDOW_AUTOSIZE)

            if Pause is True:
                cv2.rectangle(images, (420, 40), (220, 160), (0, 0, 255), -1)
                font = cv2.FONT_HERSHEY_SIMPLEX
                bottomLeftCornerOfText = (220, 110)
                fontScale = 2
                fontColor = (0, 0, 0)
                lineType = 4
                cv2.putText(images, 'Pause', bottomLeftCornerOfText, font, fontScale, fontColor, lineType)

            cv2.imshow('Color', images)
            key = cv2.waitKeyEx(1)

            if Pause is True:
                if key == 98 or key == 32:
                    take_pic.value = True
            elif Pause is False:
                if gps_dis(current_location, foto_location) > 15 or key == 98 or key == 32:
                    take_pic.value = True

            if take_pic.value == True:
                (color_frame_num, depth_frame_num) = Frame_num[:]

                if color_frame_num == foto_frame:
                    pass
                else:
                    foto_location = (lon, lat)
                    foto_frame = color_frame_num
                    logmsg = '{},{},{},{},{},{}\n'.format(i, color_frame_num, depth_frame_num, lon, lat,date)
                    print(logmsg)
                    #print('Foto {} gemacht um {:.03},{:.04}'.format(i,lon,lat))
                    logfile.write(logmsg)
                    write_kml(lon,lat)
                    #time.sleep(0.4)
                    i += 1

            if key & 0xFF == ord('q') or key == 27:
                camera_on.value = False
                gps_on.value = False
                camera_repeat.value = False
                print('Camera finish\n')
            elif key == 114 or key == 2228224:
                camera_on.value = False
                camera_repeat.value = True
                print ('camera will restart')
            elif gps_on is False:
                camera_repeat.value = False
            elif cv2.waitKey(1) & 0xFF == ord('p') or key == 2162688:
                if Pause is False:
                    print ('pause pressed')
                    Pause = True
                elif Pause is True:
                    print ('restart')
                    Pause = False
    except EOFError:
        pass
    finally:
        logfile.close()
        print ('end showing image')


def bag_num():
    num = 1
    now = datetime.datetime.now()
    time.sleep(1)

    try:
        while True:
            file_name = '{:02d}{:02d}_{:03d}'.format(now.month, now.day, num)
            bag_name = './bag/{}.bag'.format(file_name)
            exist = os.path.isfile(bag_name)
            if exist:
                num+=1
            else:
                print ('current filename:{}'.format(file_name))
                break

    finally:
        return file_name



def main():
    folder_list = ('bag','foto_log','kml')
    for folder in folder_list:
        dir_generate(folder)

    emptykml()

    Location = Array('d',[0,0])
    Frame_num = Array('i',[0,0])

    take_pic = Value('i',False)
    camera_on = Value('i',True)
    camera_repeat = Value('i',True)
    gps_on = Value('i',False)

    gps_process = Process(target=GPS, args=(Location,gps_on,))
    gps_process.start()

    print('Program Start')
    while camera_repeat.value:
        parent_conn, child_conn = Pipe()
        bag = bag_num()
        img_process = Process(target=Show_Image,
                              args=(bag,parent_conn, take_pic, Frame_num, camera_on, camera_repeat, gps_on, Location,))
        img_process.start()
        Camera(child_conn,take_pic,Frame_num,camera_on,bag)

        print ('terminated')

    gps_process.terminate()

    print ('all end')

if __name__ == '__main__':
    main()