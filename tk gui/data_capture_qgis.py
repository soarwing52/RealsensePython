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
        print ('close other programs using gps or check if the gps is correctly connected')
        gps_on.value = 3
        os._exit(0)



def gps_dis(location_1,location_2):
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

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    distance = distance*1000
    #print("Result:", distance)
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


def GPS(Location,gps_on):
    """
    the main function of starting the GPS
    :param Location: mp.Array
    :param gps_on: mp.Value
    :return:
    """

    print('GPS thread start')

    # Set port
    serialPort = serial.Serial()
    serialPort.port = port_check(gps_on) # Check the available ports, return the valid one
    serialPort.baudrate = 4800
    serialPort.bytesize = serial.EIGHTBITS
    serialPort.parity = serial.PARITY_NONE
    serialPort.timeout = 2
    serialPort.open()
    print ('GPS opened successfully')
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
            elif data[0] == '$GPGGA':
                if data[6] == '1':
                    lon = min2decimal(data[4])
                    lat = min2decimal(data[2])


            if lon ==0 or lat == 0:
                time.sleep(1)

            else:
                #print ('gps ready, current location:{},{}'.format(lon,lat))
                gps_on.value = True
                Location[:] = [lon,lat]
                with open('location.csv', 'w') as gps:
                    gps.write('Lat,Lon\n')
                    gps.write('{},{}'.format(lat,lon))


    except serial.SerialException:
        print ('Error opening GPS')
        gps_on.value = 3
    finally:
        serialPort.close()
        print('GPS finish')


def Camera(child_conn, take_pic, Frame_num, camera_on, bag):
    """
    Main camera running
    :param child_conn: source of image, sending to openCV
    :param take_pic: mp.Value, receive True will take one picture, and send back False when done
    :param Frame_num: mp.Array, frame number of the picture taken
    :param camera_on: mp.Value, the status of camera
    :param bag: the number of the current recorded file
    :return:
    """
    print('camera start')
    bag_name = './bag/{}.bag'.format(bag)
    camera_on.value = True
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 15)
    config.enable_stream(rs.stream.color, 1920, 1080, rs.format.rgb8, 15)
    config.enable_record_to_file(bag_name)
    profile = pipeline.start(config)

    device = profile.get_device() # get record device
    recorder = device.as_recorder()
    recorder.pause() # and pause it

    # get sensor and set to high density
    depth_sensor = device.first_depth_sensor()
    #depth_sensor.set_option(rs.option.visual_preset, 4)
    # dev_range = depth_sensor.get_option_range(rs.option.visual_preset)
    #preset_name = depth_sensor.get_option_value_description(rs.option.visual_preset, 4)
    #print (preset_name)
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

            if take_pic.value == 1:
                recorder.resume()
                frames = pipeline.wait_for_frames()
                depth_frame = frames.get_depth_frame()
                color_frame = frames.get_color_frame()
                var = rs.frame.get_frame_number(color_frame)
                vard = rs.frame.get_frame_number(depth_frame)
                Frame_num[:] = [var,vard]
                time.sleep(0.05)
                recorder.pause()
                take_pic.value = False

            elif camera_on.value == 0:
                child_conn.close()
                break

    except RuntimeError:
        print ('run')

    finally:
        print('pipeline closed')
        pipeline.stop()


def Show_Image(bag, parent_conn, take_pic, Frame_num, camera_on, camera_repeat, gps_on, Location):
    """
    The GUI for the program, using openCV to send and receive instructions
    :param bag: number of the recorded file
    :param parent_conn: receiver side of image, to show on openCV, the recorded bag will still in Camera
    :param take_pic: send True to let Camera take picture
    :param Frame_num: receive frame number
    :param camera_on: receive camera situation
    :param camera_repeat: mp.Value, determine if automatic start the next record
    :param gps_on: receive the status of gps
    :param Location: the current Lon, Lat
    :return:
    """
    Pause = False
    i = 1
    foto_location = (0, 0)
    foto_frame = Frame_num[0]

    try:
        while True:
            (lon, lat) = Location[:]
            current_location = (lon, lat)
            present = datetime.datetime.now()
            date = '{},{},{},{}'.format(present.day, present.month, present.year, present.time())
            local_take_pic = False

            color_image, depth_image = parent_conn.recv()
            depth_colormap_resize = cv2.resize(depth_image, (424, 240))
            color_cvt = cv2.cvtColor(color_image, cv2.COLOR_RGB2BGR)
            color_cvt_2 = cv2.resize(color_cvt, (424, 318))
            images = np.vstack((color_cvt_2, depth_colormap_resize))
            cv2.namedWindow('Color', cv2.WINDOW_AUTOSIZE)
            cv2.setWindowProperty('Color', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            cv2.setWindowProperty('Color', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)

            if Pause is True:
                cv2.rectangle(images, (111,219), (339,311), (0, 0, 255), -1)
                font = cv2.FONT_HERSHEY_SIMPLEX
                bottomLeftCornerOfText = (125,290)
                fontScale = 2
                fontColor = (0, 0, 0)
                lineType = 4
                cv2.putText(images, 'Pause', bottomLeftCornerOfText, font, fontScale, fontColor, lineType)

            cv2.imshow('Color', images)
            key = cv2.waitKeyEx(1)
            if take_pic.value == 1 or current_location == foto_location:
                continue

            if Pause is False:
                if gps_dis(current_location, foto_location) > 15:
                    local_take_pic = True

            if key == 98 or key == 32:
                local_take_pic = True

            if local_take_pic == True:
                take_pic.value = True
                time.sleep(0.1)
                (color_frame_num, depth_frame_num) = Frame_num[:]
                logmsg = '{},{},{},{},{},{}\n'.format(i, color_frame_num, depth_frame_num, lon, lat,date)
                print('Foto {} gemacht um {:.03},{:.04}'.format(i,lon,lat))
                with open('./foto_log/{}.txt'.format(bag), 'a') as logfile:
                    logfile.write(logmsg)
                with open('foto_location.csv', 'a') as record:
                    record.write(logmsg)
                foto_location = (lon, lat)
                i += 1
            if key & 0xFF == ord('q') or key == 27:
                camera_on.value = False
                gps_on.value = False
                camera_repeat.value = False
                print('Camera finish\n')
            elif key == 114 or key == 2228224:
                camera_on.value = False
                camera_repeat.value = True
                print ('Camera restart')
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
        print ('Image thread ended')


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
            bag_name = './bag/{}.bag'.format(file_name)
            exist = os.path.isfile(bag_name)
            if exist:
                num+=1
            else:
                print ('current filename:{}'.format(file_name))
                break
        return file_name
    finally:
        pass


def main():
    # Create Folders for Data
    folder_list = ('bag','foto_log')
    for folder in folder_list:
        dir_generate(folder)
    # Create Variables between Processes
    Location = Array('d',[0,0])
    Frame_num = Array('i',[0,0])

    take_pic = Value('i',False)
    camera_on = Value('i',True)
    camera_repeat = Value('i',True)
    gps_on = Value('i',False)

    # Start GPS process
    gps_process = Process(target=GPS, args=(Location,gps_on,))
    gps_process.start()

    print('Program Start')
    while camera_repeat.value:
        if gps_on.value == 0:
            time.sleep(1)
            continue
        elif gps_on.value == 3:
            pause_exit()
            break

        else:
            parent_conn, child_conn = Pipe()
            bag = bag_num()
            img_process = Process(target=Show_Image,
                                  args=(bag,parent_conn, take_pic, Frame_num, camera_on, camera_repeat, gps_on, Location,))
            img_process.start()
            Camera(child_conn,take_pic,Frame_num,camera_on,bag)

    gps_process.terminate()

if __name__ == '__main__':
    main()