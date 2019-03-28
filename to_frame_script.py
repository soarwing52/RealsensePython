# First import library
import pyrealsense2 as rs
# Import Numpy for easy array manipulation
import numpy as np
# Import OpenCV for easy image rendering
import cv2
# Import os.path for file path manipulation
import os.path


file_name = '0327.bag'
print file_name
# Configure depth and color streams
pipeline = rs.pipeline()
config = rs.config()
config.enable_device_from_file(file_name)

# Start streaming from file
profile = pipeline.start(config)
device = profile.get_device()
playback = device.as_playback()
playback.set_real_time(False)
print 'profile got'
#align to color map
align_to = rs.stream.color
align = rs.align(align_to)
print 'aligned'
# Skip 5 first frames to give the Auto-Exposure time to adjust
for x in range(5):
  pipeline.wait_for_frames()
i = 1

frame_number = input('no.? \n')


for x in range(frame_number):
            pipeline.wait_for_frames()
frames = pipeline.wait_for_frames()
depth_frame = frames.get_depth_frame()
color_frame = frames.get_color_frame()
playback.pause()
# Colorize depth frame to jet colormap
depth_color_frame = rs.colorizer().colorize(depth_frame)
# Convert depth_frame to numpy array to render image in opencv
depth_color_image = np.asanyarray(depth_color_frame.get_data())
color_image = np.asanyarray(color_frame.get_data())
cv2.namedWindow("Color Stream", cv2.WINDOW_AUTOSIZE)
cv2.imshow('Color Stream', color_image)
cv2.waitKey(0)

playback.resume()
pipeline.stop()
pipeline.start(config)






