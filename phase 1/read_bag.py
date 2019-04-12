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
    pipeline = rs.pipeline()
    config = rs.config()
    # Tell config that we will use a recorded device from filem to be used by the pipeline through playback.
    rs.config.enable_device_from_file(config, '1515.bag')
    config.enable_all_streams()

    # Configure the pipeline to stream the depth stream
    # Start streaming from file
    profile = pipeline.start(config)
    device = profile.get_device()
    playback = device.as_playback()
    playback.set_real_time(False)

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
        color_cvt = cv2.cvtColor(color_image,cv2.COLOR_BGR2RGB)

        # Render image in opencv window
        # Create opencv window to render image in
        cv2.namedWindow("Color Stream", cv2.WINDOW_AUTOSIZE)
        cv2.imshow("Color Stream",color_image)
        cv2.imshow("Depth Stream", depth_color_image)
        key = cv2.waitKey(1)
        # if pressed escape exit program
        if key == 27:
            cv2.destroyAllWindows()
            break

finally:
    pipeline.stop()
    print 'end'
    pass