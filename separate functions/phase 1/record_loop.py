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
    rs.recorder.pause(recorder)
    depth_sensor = device.first_depth_sensor()
    depth_sensor.set_option(rs.option.visual_preset, 4)
    range = depth_sensor.get_option_range(rs.option.visual_preset)
    preset_name = depth_sensor.get_option_value_description(rs.option.visual_preset, 4)
    # print preset_name

    time_1 = time.time()
    try:
        while True:
            # Get frameset of depth
            frames = pipeline.wait_for_frames()
            depth_frame = frames.get_depth_frame()
            color_frame = frames.get_color_frame()
            if not depth_frame or not color_frame:
                continue
            depth_color_frame = rs.colorizer().colorize(depth_frame)
            depth_image = np.asanyarray(depth_color_frame.get_data())
            depth_colormap_resize = cv2.resize(depth_image,(424,240))
            color_image = np.asanyarray(color_frame.get_data())
            color_cvt = cv2.cvtColor(color_image, cv2.COLOR_RGB2BGR)
            color_cvt_2 = cv2.resize(color_cvt, (424,318))
            images = np.vstack((color_cvt_2, depth_colormap_resize))
            cv2.namedWindow('Color', cv2.WINDOW_AUTOSIZE)
            cv2.imshow('Color', images)
            var = rs.frame.get_frame_number(color_frame)
            key = cv2.waitKey(1)

            time_2 = time.time()
            gap = time_2 - time_1

            if key == 27:
                print 'stopped'
                cv2.destroyAllWindows()
                break

            elif gap > 180:

                print 'done'
                cv2.destroyAllWindows()
                break
            elif key == 32:
                rs.recorder.resume(recorder)
                print 'start time: ' + str(gap)
                frames = pipeline.wait_for_frames()
                depth_frame = frames.get_depth_frame()
                color_frame = frames.get_color_frame()
                var = rs.frame.get_frame_number(color_frame)
                print 'frame number: ' + str(var)
                rs.recorder.pause(recorder)

            elif var % 300 < 1:
                rs.recorder.resume(recorder)
                print 'start time: ' + str(gap)
                frames = pipeline.wait_for_frames()
                depth_frame = frames.get_depth_frame()
                color_frame = frames.get_color_frame()
                var = rs.frame.get_frame_number(color_frame)
                print 'saved frame number: ' + str(var)
                rs.recorder.pause(recorder)
                # print 'pause time: ' + str(gap)

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
