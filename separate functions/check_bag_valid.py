import os
# -*- coding: utf-8 -*-
from Tkinter import *
import tkFileDialog
import os
import arcpy
from arcpy import management
import pyrealsense2 as rs
import numpy as np
import cv2
import multiprocessing as mp
import time

def test_bag(input_file):
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_device_from_file(input_file, False)
    config.enable_all_streams()
    profile = pipeline.start(config)
    device = profile.get_device()
    playback = device.as_playback()
    playback.set_real_time(False)
    try:
        while True:
            frames = pipeline.wait_for_frames()
            print 'Xx'
            depth_frame = frames.get_depth_frame()
            color_frame = frames.get_color_frame()
            if not depth_frame or not color_frame:
                continue
            depth_color_frame = rs.colorizer().colorize(depth_frame)
            depth_image = np.asanyarray(depth_color_frame.get_data())
            depth_colormap_resize = cv2.resize(depth_image,(424,240))
            color_image = np.asanyarray(color_frame.get_data())
            color_cvt = cv2.cvtColor(color_image, cv2.COLOR_RGB2BGR)
            color_cvt_2 = cv2.resize(color_cvt, (320,240))
            images = np.hstack((color_cvt_2, depth_colormap_resize))
            cv2.namedWindow('Color', cv2.WINDOW_AUTOSIZE)
            cv2.imshow('Color', images)
        time.sleep(1)
        pipeline.stop()
    except RuntimeError:
        print '{} unindexed'.format(input_file)
    finally:
        print 'tested'
        pass

if __name__ == '__main__':
    test_bag(r'C:\Users\cyh\Desktop\test\bag\0529_002.bag')