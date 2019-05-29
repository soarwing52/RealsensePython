import pyrealsense2 as rs
# Import Numpy for easy array manipulation
import numpy as np
# Import OpenCV for easy image rendering
import cv2



def read_bag(filename):
    """a simple function for reading the input file and show in opencv window
    the current issue is that pipeline.stop still freeze while set_real_time is False"""

    pipeline = rs.pipeline()
    config = rs.config()
    # Tell config that we will use a recorded device from filem to be used by the pipeline through playback.
    config.enable_device_from_file(filename)
    # Configure the pipeline to stream the depth stream
    config.enable_all_streams()
    # Start streaming from file
    profile = pipeline.start(config)
    device = profile.get_device()
    playback = device.as_playback()
    playback.set_real_time(False)
    try:
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
            cv2.imshow("Color Stream",color_cvt)
            cv2.imshow("Depth Stream", depth_color_image)
            key = cv2.waitKey(100)
            # if pressed escape or q, exit program
            if key & 0xFF == ord('q') or key == 27:
                cv2.destroyAllWindows()
                break

    finally:
        print 'end'
        pipeline.stop()

def main():
    filename= raw_input('file full path: \n')
    read_bag(filename)

if __name__ == '__main__':
    main()