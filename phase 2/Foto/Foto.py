import pyrealsense2 as rs
import numpy as np
from matplotlib import pyplot as plt
import cv2
import time
import sys

file_name = raw_input('Wegnummer: \n') + '.bag'
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 1280, 720, rs.format.rgba8, 30)
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

i=1
try:
    while True :
        frames = pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()
        if not depth_frame or not color_frame:
            continue

        # Convert images to numpy arrays
        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())
        color_cvt = cv2.cvtColor(color_image,cv2.COLOR_RGB2BGR)

        # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
        # Show images
        #cv2.namedWindow('depth',cv2.WINDOW_FULLSCREEN)
        cv2.namedWindow('Color', cv2.WINDOW_FULLSCREEN)
        #cv2.imshow('depth',depth_colormap)
        cv2.imshow('Color', color_cvt)
        
        key = cv2.waitKey(1)
        
        # Press esc or 'q' to close the image window
        if key == 32:
            print i
            i +=1
            rs.recorder.resume(recorder)
            frames = pipeline.wait_for_frames()
            depth_frame = frames.get_depth_frame()
            color_frame = frames.get_color_frame()
            var = rs.frame.get_frame_number(color_frame)
            vard = rs.frame.get_frame_number(depth_frame)
            print 'frame number: ' + str(var)+'/d:' + str(vard)
            rs.recorder.pause(recorder)
            continue
        elif key == 27:
            cv2.destroyAllWindows()
            break

finally:

    # Stop streaming
    pipeline.stop()
