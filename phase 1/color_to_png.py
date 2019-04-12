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


try:
    file_name = raw_input('file name: \n')
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.color, 1920,1080, rs.format.rgba8, 30)
    config.enable_device_from_file(file_name + '.bag')
    profile = pipeline.start(config)
    while True:
        frames = pipeline.wait_for_frames()
        frames.keep()
        if frames:
            color_frame = frames.get_color_frame()
            var = rs.frame.get_frame_number(color_frame)
            print 'frame number: ' + str(var)
            time_color = rs.frame.get_timestamp(color_frame)
            color_image = np.asanyarray(color_frame.get_data())
            color_cvt = cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB)

            cv2.namedWindow("Color Stream", cv2.WINDOW_AUTOSIZE)
            cv2.imshow("Color Stream",color_cvt)
            cv2.imwrite(file_name +'_c_'+ str(var)+'.png',color_cvt)
            key = cv2.waitKey(1)
            # if pressed escape exit program
            if key == 27:
                cv2.destroyAllWindows()
                break
except RuntimeError:
    print("No more frames arrived, reached end of BAG file!")
    cv2.destroyAllWindows()
finally:
    pass
