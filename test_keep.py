import pyrealsense2 as rs
import numpy as np
import cv2
import time
import os



pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 1920, 1080, rs.format.rgb8, 30)
profile = pipeline.start(config)


sensor = profile.get_device().query_sensors()

for x in sensor:
    x.set_option(rs.option.frames_queue_size, 32)
saver = rs.save_single_frameset()


try:
    while True:


        frames = pipeline.poll_for_frames()
        if not frames :
            continue
        saver = rs.save_single_frameset()
        saver.start()
        frame = frames.as_frameset()
        depth_frame = frame.get_depth_frame()
        color_frame = frame.get_color_frame()

        frameset = frame


        c_frame_num = rs.frame.get_frame_number(color_frame)
        color_image = np.asanyarray(color_frame.get_data())
        color_cvt = cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB)
        color_cvt = cv2.resize(color_cvt, (1680, 1050))
        cv2.rectangle(color_cvt,(540,20),(640,60),(255,255,255),-1)
        font = cv2.FONT_HERSHEY_SIMPLEX
        bottomLeftCornerOfText = (550, 50)
        fontScale = 1
        fontColor = (0, 0, 0)
        lineType = 2
        cv2.putText(color_cvt,str(c_frame_num), bottomLeftCornerOfText, font,fontScale,fontColor,lineType)
        cv2.namedWindow("Color Stream", cv2.WINDOW_FULLSCREEN)
        cv2.imshow("Color Stream", color_cvt)
        key = cv2.waitKey(1)


        # if pressed escape exit program
        if key & 0xFF == ord('q') or key == 27:
            cv2.destroyAllWindows()
            break
        elif 100 > c_frame_num > 50:
            saver.process(frameset)
        elif c_frame_num > 100:
            saver.process(frameset)
            cv2.destroyAllWindows()
            break

        """
except RuntimeError:
    print 'file ended'
    cv2.destroyAllWindows()
    """

finally:
    print 'finish'
    pipeline.stop()
