import os
import pyrealsense2 as rs
import numpy as np
import cv2

def color_to_png(input_file):
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_all_streams()
    config.enable_device_from_file('./bag/'+input_file,False)
    profile = pipeline.start(config)
    device = profile.get_device()
    playback = device.as_playback()
    playback.set_real_time(False)
    align_to = rs.stream.color
    align = rs.align(align_to)
    try:
        while True:
            frames = pipeline.wait_for_frames()
            aligned_frames = align.process(frames)
            depth_frame = aligned_frames.get_depth_frame()
            color_frame = frames.get_color_frame()
            depth_color = rs.colorizer().colorize(depth_frame)
            depth_color_image = np.asanyarray(depth_color.get_data())
            var = rs.frame.get_frame_number(color_frame)
            color_image = np.asanyarray(color_frame.get_data())
            color_cvt = cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB)
            cv2.namedWindow("Color Stream", cv2.WINDOW_AUTOSIZE)
            cv2.imshow("Color Stream", depth_color_image)
            print 'compressing {}-{}.png'.format(input_file[:-4],str(var))
            cv2.imwrite('./png/D-{}-{}.png'.format(input_file[:-4],str(var)), depth_color_image,[cv2.IMWRITE_PNG_COMPRESSION,1])
            key = cv2.waitKey(100)
            # if pressed escape exit program
            if key == 27:
                cv2.destroyAllWindows()
                break

    except RuntimeError:
        print 'frame covert finished for '+input_file
        cv2.destroyAllWindows()
    finally:
        pass


dir_name = 'bag'
for filename in os.listdir(dir_name):
    print filename
    color_to_png(filename)
