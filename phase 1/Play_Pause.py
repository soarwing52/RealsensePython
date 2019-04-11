# First import library
import pyrealsense2 as rs
# Import Numpy for easy array manipulation
import numpy as np
# Import OpenCV for easy image rendering
import cv2
# Import argparse for command-line options
import argparse
# Import os.path for file path manipulation
import os.path

from pyrealsense2.pyrealsense2 import pipeline

try:
    # Create pipeline

    cfg = rs.config()
    # Tell config that we will use a recorded device from filem to be used by the pipeline through playback.
    rs.config.enable_device_from_file(cfg, '0327.bag')
    # Start streaming from file
    pipeline = rs.pipeline()  # type: pipeline
    profile = pipeline.start(cfg)
    device = profile.get_device()
    playback = device.as_playback()
    playback.set_real_time(False)
    clr = rs.colorizer()
    clr.set_option(rs.option.color_scheme,3.0)

    # set up sensor
    dev = profile.get_device()
    depth_sensor = dev.first_depth_sensor()
    range = depth_sensor.get_option_range(rs.option.visual_preset)
    preset_name = depth_sensor.get_option_value_description(rs.option.visual_preset, 4)
    print 'sensor set'

    def play_pause(event,x,y,flags,param):
        if flags == cv2.EVENT_FLAG_CTRLKEY:
            rs.playback.pause(playback)
        elif flags == cv2.EVENT_FLAG_SHIFTKEY:
            rs.playback.resume(playback)

    # Streaming loop
    while True:
        # Get frameset of depth
        frames = pipeline.wait_for_frames()

        # Get depth frame
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()
        # Colorize depth frame to jet colormap
        depth_color_frame = rs.colorizer().colorize(depth_frame)
        # Convert depth_frame to numpy array to render image in opencv
        depth_color_image = np.asanyarray(depth_color_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        cv2.namedWindow("Color Stream", cv2.WINDOW_AUTOSIZE)
        # Render image in opencv window
        #cv2.imshow("Depth Stream", depth_color_image)
        cv2.imshow('Color Stream', color_image)
        cv2.setMouseCallback('Color Stream',play_pause)

        key = cv2.waitKey(1)
        # if pressed escape exit program
        if key == 27:
            cv2.destroyAllWindows()
            break
finally:
    pass