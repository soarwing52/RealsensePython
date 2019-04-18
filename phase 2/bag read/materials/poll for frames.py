import argparse
import pyrealsense2 as rs
import numpy as np
import cv2
import os


def main():

    try:
        config = rs.config()
        rs.config.enable_device_from_file(config, '18frame.bag')
        pipeline = rs.pipeline()
        config.enable_all_streams()
        pipeline.start(config)
        i = 0
        while True:
            frames = pipeline.poll_for_frames()
            depth_frame= frames.get_depth_frame()
            color_frame = frames.get_color_frame()
            if not depth_frame or not color_frame:
                continue

            n_var = rs.frame.get_frame_number(color_frame)
            n_vard = rs.frame.get_frame_number(depth_frame)
            print 'frame number: {},{}'.format(n_var, n_vard)
            # Colorize depth frame to jet colormap
            depth_color_frame = rs.colorizer().colorize(depth_frame)

            # Convert depth_frame to numpy array to render image in opencv
            depth_color_image = np.asanyarray(depth_color_frame.get_data())
            color_image = np.asanyarray(color_frame.get_data())
            color_cvt = cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB)

            # Render image in opencv window
            # Create opencv window to render image in
            cv2.namedWindow("Color Stream", cv2.WINDOW_AUTOSIZE)
            cv2.imshow("Color Stream", color_cvt)
            cv2.imshow("Depth Stream", depth_color_image)
            key = cv2.waitKey(100)
            # if pressed escape exit program
            if key == 27:
                cv2.destroyAllWindows()
                break
            else:
                continue
    finally:
        pass


if __name__ == "__main__":

    main()