import pyrealsense2 as rs
import numpy as np
from matplotlib import pyplot as plt
import cv2
import time
import sys

def main():
    question()

def record():
    global time_name
    time_name = time.strftime('%d_%m_%H_%M')
    file_name = str(time_name) + '.bag'
    print file_name
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)
    config.enable_stream(rs.stream.color, 1280, 720, rs.format.rgba8, 30)
    config.enable_record_to_file(file_name)
    profile = pipeline.start(config)
    # get device and recorder
    device = profile.get_device()
    recorder = device.as_recorder()
    depth_sensor = device.first_depth_sensor()
    depth_sensor.set_option(rs.option.visual_preset, 4)
    range = depth_sensor.get_option_range(rs.option.visual_preset)
    preset_name = depth_sensor.get_option_value_description(rs.option.visual_preset, 4)
    #print preset_name

    time_1 = time.time()
    try:
        while True:
            # Get frameset of depth
            frames = pipeline.wait_for_frames()
            depth_frame = frames.get_depth_frame()
            color_frame = frames.get_color_frame()
            depth_image = np.asanyarray(depth_frame.get_data())
            color_image = np.asanyarray(color_frame.get_data())
            cv2.namedWindow('Color', cv2.WINDOW_AUTOSIZE)
            # cv2.namedWindow('Depth', cv2.WINDOW_AUTOSIZE)
            # cv2.imshow('Depth', depth_image)
            cv2.imshow('Color', color_image)
            key = cv2.waitKey(1)

            time_2 = time.time()
            gap = time_2 - time_1

            if key == 27:
                print 'done'
                break

            elif gap > 60:
                print 'done'
                break

            elif gap % 20 < 1:
                rs.recorder.resume(recorder)
                #print 'start time: ' + str(gap)
            elif gap % 5 < 1:
                rs.recorder.pause(recorder)
                #print 'pause time: ' + str(gap)
    finally:
        pipeline.stop()

    pass

def question():
    x = raw_input('next file? \n')
    if str(x) == 'no':
        sys.exit('fertig')
    else:
        record()
        question()

if __name__ == '__main__':
    question()
