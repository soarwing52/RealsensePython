import pyrealsense2 as rs
# Import Numpy for easy array manipulation
import numpy as np
# Import OpenCV for easy image rendering
import cv2

# Configure depth and color streams
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
# Start streaming
profile = pipeline.start(config)

for x in range(5):
    pipeline.wait_for_frames()
try:
    while True:
        frame = pipeline.wait_for_frames()
        depth_frame = frame.get_depth_frame()
        color_frame = frame.get_color_frame()
        if not depth_frame or not color_frame:
            continue
        width = depth_frame.get_width()
        height = depth_frame.get_height()
        dist = depth_frame.get_distance(width / 2, height / 2)
        print 'distance is '+ str(dist)
        # Press esc or 'q' to close the image window
        key = cv2.waitKey(1)
        if key & 0xFF == ord('q') or key == 27:
            break

finally:
    # Stop streaming
    pipeline.stop()


    
