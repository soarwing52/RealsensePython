import pyrealsense2 as rs
# Import Numpy for easy array manipulation
import numpy as np
# Import OpenCV for easy image rendering
import cv2
import sys
from matplotlib import pyplot as plt
from matplotlib.widgets2 import Ruler
import os


num = raw_input('Wegenummer:\n')
file_name = './bag/'+num+'.bag'
pipeline = rs.pipeline()
config = rs.config()
config.enable_device_from_file(file_name)
config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 1280, 720, rs.format.rgba8, 30)
profile = pipeline.start(config)
device = profile.get_device()
playback = device.as_playback()
playback.set_real_time(False)
align_to = rs.stream.color
align = rs.align(align_to)
frame_list = []

with open('./list/'+num+'_matched.txt','r') as csvfile:
    for line in csvfile:
        frame = [elt.strip() for elt in line.split(',')]
        frame_list.append(frame)
i=0
try:
    while True:
        frames = pipeline.wait_for_frames()
        aligned_frames = align.process(frames)
        depth_frame = aligned_frames.get_depth_frame()
        vard = rs.frame.get_frame_number(depth_frame)
        if int(vard) == int(frame_list[i][1]) :
            try:
                while True:
                    new_frames = pipeline.wait_for_frames()
                    color_frame = new_frames.get_color_frame()
                    var = rs.frame.get_frame_number(color_frame)
                    if int(var) ==int(frame_list[i][0]):
                        depth_color = rs.colorizer().colorize(depth_frame)
                        depth_color_image = np.asanyarray(depth_color.get_data())
                        color_image = np.asanyarray(color_frame.get_data())

                        color_intrin = color_frame.profile.as_video_stream_profile().intrinsics
                        color_cvt = cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB)
                        print var, vard
                        img_over = cv2.addWeighted(color_cvt, 1, depth_color_image, 0.3, 0.5)
                        key = cv2.waitKey(0)

                        xCoord = np.arange(0, 6, 1)
                        yCoord = [0, 1, -3, 5, -3, 0]
                        fig = plt.figure()
                        ax = fig.add_subplot(111)

                        number = 'frame number: c:' + str(var) + '/d:' + str(vard)
                        markerprops = dict(marker='o', markersize=5, markeredgecolor='red')
                        lineprops = dict(color='red', linewidth=2)
                        plt.imshow(img_over)
                        ax.grid(False)
                        plt.text(500, -20, number, fontsize=15)
                        figManager = plt.get_current_fig_manager().window.state('zoomed')

                        ruler = Ruler(ax=ax,
                                      depth_frame=depth_frame,
                                      color_intrin=color_intrin,
                                      useblit=True,
                                      markerprops=markerprops,
                                      lineprops=lineprops,
                                      )

                        #print 'show image'
                        plt.show()
                        # if pressed escape exit program
                        if key == 27:
                            cv2.destroyAllWindows()
                            break
                        else:
                            cv2.destroyAllWindows()
                            i+= 1
                            break

            finally:
                pass

        else:
            pass

except IndexError:
    print 'file ended'


finally:
    print 'finish'


