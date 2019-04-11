#import library needed
import pyrealsense2 as rs
import numpy as np
import cv2
import math
import sys

#message box
import ctypes
from ctypes import c_int, WINFUNCTYPE, windll
from ctypes.wintypes import HWND, LPCWSTR, UINT
prototype = WINFUNCTYPE(c_int, HWND, LPCWSTR, LPCWSTR, UINT)
paramflags = (1, "hwnd", 0), (1, "text", "Hi"), (1, "caption", "Result"), (1, "flags", 0)
MessageBox = prototype(("MessageBoxW", windll.user32), paramflags)

file_name = raw_input('name of the file: \n')+ '.bag'
print file_name
# Configure depth and color streams
pipeline = rs.pipeline()
config = rs.config()
config.enable_device_from_file(file_name)

# Start streaming from file
profile = pipeline.start(config)
profile.get_device().as_playback().set_real_time(True)
print 'profile got'
#align to color map
align_to = rs.stream.color
align = rs.align(align_to)
print 'aligned'
# Skip 5 first frames to give the Auto-Exposure time to adjust
for x in range(5):
  pipeline.wait_for_frames()

print 'waited'

# Streaming loop
try:
    while True:
        #set up sensor
        dev = profile.get_device()
        depth_sensor = dev.first_depth_sensor()
        range = depth_sensor.get_option_range(rs.option.visual_preset)
        preset_name = depth_sensor.get_option_value_description(rs.option.visual_preset, 4)
        print 'sensor set'

        # Get frameset of depth
        frames = pipeline.wait_for_frames()
        aligned_frames = align.process(frames)
        depth_frame = aligned_frames.get_depth_frame()
        color_frame = frames.get_color_frame()
        #colorize depth frame
        depth_color = rs.colorizer().colorize(depth_frame)
        print 'frame colorized'

        # get depth stream data
        depth_stream = profile.get_stream(rs.stream.depth)
        inst = rs.video_stream_profile.intrinsics
        #get intrinsics of the frames
        depth_intrin = depth_frame.profile.as_video_stream_profile().intrinsics
        color_intrin = color_frame.profile.as_video_stream_profile().intrinsics
        depth_to_color_extrin = depth_frame.profile.get_extrinsics_to(color_frame.profile)
        print 'instrincts got'

        # Convert images to numpy arrays
        depth_image = np.asanyarray(depth_color.get_data())
        color_image = np.asanyarray(color_frame.get_data())
        print 'got image'

        #set image property
        image = color_image
        print 'image property set'
        def calculate_3D (xi, yi, x0, y0):
            udist = depth_frame.get_distance(xi, yi)
            vdist = depth_frame.get_distance(x0, y0)
            print udist, vdist
            point1 = rs.rs2_deproject_pixel_to_point(color_intrin, [xi, yi], udist)
            point2 = rs.rs2_deproject_pixel_to_point(color_intrin, [x0, y0], vdist)
            print 'start(x,y,z): '+ str(point1)+'\n' + 'end(x,y,z): ' +str(point2)
            dist = math.sqrt(
            math.pow(point1[0] - point2[0], 2) + math.pow(point1[1] - point2[1],2) + math.pow(
                point1[2] - point2[2], 2))
            cm = dist * 100
            decimal2 = "%.2f" % cm
            print 'Vermessung: ' + str(decimal2)+ 'cm'
            MessageBox(text='Vermessung: ' + decimal2 + ' cm')

        def measure (event,x,y,flags,param):
            global xi,yi,x0,y0
            if event == cv2.EVENT_LBUTTONDOWN:
                xi,yi = x,y
                print 'xi,yi= ' + str(xi) + ',' + str(yi)
                return xi,yi

            elif event == cv2.EVENT_LBUTTONUP:
                x0,y0 = x,y
                print 'x0,y0= ' + str(x0) + ',' + str(y0)
                calculate_3D(xi, yi, x0, y0)
                return x0,y0

        print 'show window'
        cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
        cv2.setMouseCallback('RealSense',measure)
        cv2.imshow('RealSense', image)
        key = cv2.waitKey(0)
        # Press esc or 'q' to close the image window
        if key & 0xFF == ord('q') or key == 27:
            cv2.destroyAllWindows()
            print 'break'
            break
finally:

    pipeline.stop()
    print 'stopped'




