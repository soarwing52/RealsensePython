import pyrealsense2 as rs
# Import Numpy for easy array manipulation
import numpy as np
# Import OpenCV for easy image rendering
import cv2

file_name = '18frame.bag'
print file_name
# Configure depth and color streams
pipeline = rs.pipeline()
config = rs.config()
config.enable_device_from_file(file_name,True)
config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 1920, 1080, rs.format.rgba8, 30)
# Start streaming from file
profile = pipeline.start(config)
device = profile.get_device()
playback = device.as_playback()
playback.set_real_time(False)
# print 'profile got'
# align to color map
align_to = rs.stream.color
align = rs.align(align_to)
fold = open('colorlist.txt','w')
depth_list = []
i=0
try:
    while True:
        frames = pipeline.wait_for_frames()
        aligned_frames = align.process(frames)
        color_frame = aligned_frames.get_color_frame()
        vard = rs.frame.get_frame_number(color_frame)
        time_depth = rs.frame.get_timestamp(color_frame)
        fold.write(str(vard)+',')
        fold.write(str(time_depth)+'\n')
        depth_list.append([])
        depth_list[i].append(vard)
        depth_list[i].append(time_depth)
        i +=1

except RuntimeError:
    print 'file ended'
finally:
    print depth_list

    pipeline.stop()