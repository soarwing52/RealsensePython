import pyrealsense2 as rs
# Import Numpy for easy array manipulation
import numpy as np
# Import OpenCV for easy image rendering
import cv2
# Import argparse for command-line options
import argparse
# Import os.path for file path manipulation
import os.path


try:
    file_name = raw_input('file name: \n')
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)
    config.enable_stream(rs.stream.color,1920,1080,rs.format.rgba8,30)
    config.enable_device_from_file(file_name + '.bag')
    profile = pipeline.start(config)
    i = 0
    align = rs.stream.color
    align_to = rs.align(align)
    # Streaming loop
    while True:
        frames = pipeline.wait_for_frames()
        frames = align_to.process(frames)
        if frames:
            depth_frame = frames.get_depth_frame()
            var_d = rs.frame.get_frame_number(depth_frame)
            print 'frame number d: '+ str(var_d)
            depth_color_frame = rs.colorizer().colorize(depth_frame)
            depth_color_image = np.asanyarray(depth_color_frame.get_data())
            cv2.imwrite(file_name +'_d_'+ str(var_d)+'.png',depth_color_image)
            cv2.imshow("Depth Stream", depth_color_image)
            key = cv2.waitKey(1)
            # if pressed escape exit program
            if key == 27:
                cv2.destroyAllWindows()
                break
except RuntimeError:
    print "No more frames arrived, reached end of BAG file!"
finally:
    pass
