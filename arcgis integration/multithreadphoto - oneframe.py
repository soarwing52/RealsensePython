import pyrealsense2 as rs
import numpy as np
import cv2
import serial
import datetime
import threading
import time


def min2decimal(in_data):
  latgps = float(in_data)
  latdeg = int(latgps / 100)
  latmin = latgps - latdeg * 100
  lat = latdeg + (latmin / 60)
  return lat

def GPS():
    print('GPS start')
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
                  global gpsmsg
                  gpsmsg = '{},{},{},{},{},{}\n'.format(i, data[4], lat, data[6], lon, date)
                  if not gpsmsg:
                      continue
                  print gpsmsg
                  gpslog.write(gpsmsg)
          elif i == 800:
              break
    finally:
      gpslog.close()
      print('GPS finish')

def Camera():
    print 'Camera start'
    global i,gpsmsg
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
            color_image = np.asanyarray(color_frame.get_data())
            color_cvt = cv2.cvtColor(color_image, cv2.COLOR_RGB2BGR)
            color_cvt_2 = cv2.resize(color_cvt, (960, 540))
            cv2.namedWindow('Color', cv2.WINDOW_AUTOSIZE)
            cv2.imshow('Color', color_cvt_2)
            key = cv2.waitKey(1)
            if key == 32:
                rs.recorder.resume(recorder)
                time.sleep(0.01)
                
                r_frames = pipeline.wait_for_frames()
                r_depth_frame = r_frames.get_depth_frame()
                r_color_frame = r_frames.get_color_frame()
                var = rs.frame.get_frame_number(r_color_frame)
                vard = rs.frame.get_frame_number(r_depth_frame)
                msg = '{}.c:{}/d:{}\n{}'.format(i, str(var), str(vard), gpsmsg)
                print msg
                logmsg = '{},{},{},{}'.format(i, str(var), str(vard), gpsmsg)
                fotolog.write(logmsg)
                rs.recorder.pause(recorder)
                i += 1
                continue
            elif key & 0xFF == ord('q') or key == 27:
                cv2.destroyAllWindows()
                i = 800
                break
    finally:
        print('Camera finish\n')

        fotolog.close()
        pipeline.stop()

def main():
    global i
    i=1
    gps_thread = threading.Thread(target=GPS, name='T1')
    camera_thread = threading.Thread(target=Camera, name='T2')
    gps_thread.start()
    camera_thread.start()
    camera_thread.join()
    gps_thread.join()
    print threading.active_count()
    print('all done\n')


if __name__ == '__main__':
    num = raw_input('Wegnummer: \n')
    file_name = num + '.bag'
    gpslog = open('gpslog_{}.txt'.format(num), 'a')
    fotolog = open('fotolog_{}.txt'.format(num), 'a')
    main()
