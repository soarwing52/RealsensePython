#import library needed
import pyrealsense2 as rs
import numpy as np
import cv2
import math
import sys
from matplotlib import pyplot as plt
from matplotlib.widgets2 import Ruler

def main():
    question()

def measure(input):
    file_name = input+'.bag'
    print file_name
    # Configure depth and color streams
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_device_from_file(file_name)
    # Start streaming from file
    profile = pipeline.start(config)
    device = profile.get_device()
    playback = device.as_playback()
    playback.set_real_time(False)
    print 'profile got'
    # align to color map
    # Define filters
    dec = rs.decimation_filter(1)
    to_dasparity = rs.disparity_transform(True)
    dasparity_to = rs.disparity_transform(False)
    spat = rs.spatial_filter()
    hole = rs.hole_filling_filter(2)
    temp = rs.temporal_filter()


    i = 1

    while i < 10:
            align_to = rs.stream.color
            align = rs.align(align_to)
            print 'aligned'
            playback.resume()
            frames = pipeline.wait_for_frames()
            aligned_frames = align.process(frames)
            playback.pause()

            depth_frame = aligned_frames.get_depth_frame()
            depth_frame = frames.get_depth_frame()
            color_frame = frames.get_color_frame()
            depth = dec.process(depth_frame)
            depth_dis = to_dasparity.process(depth)
            depth_spat = spat.process(depth_dis)
            depth_temp = temp.process(depth_spat)
            depth_hole = hole.process(depth_temp)
            depth_final = dasparity_to.process(depth_hole)
            depth_color = rs.colorizer().colorize(depth_final)
            depth_stream = profile.get_stream(rs.stream.depth)
            inst = rs.video_stream_profile.intrinsics
            # get intrinsics of the frames
            depth_intrin = depth_frame.profile.as_video_stream_profile().intrinsics
            color_intrin = color_frame.profile.as_video_stream_profile().intrinsics
            depth_to_color_extrin = depth_frame.profile.get_extrinsics_to(color_frame.profile)
            print 'instrincts got'
            var = rs.frame.get_frame_number(color_frame)
            print 'frame number: ' + str(var)


            # turn into numpy array
            depth_image = np.asanyarray(depth_color.get_data())
            color_image = np.asanyarray(color_frame.get_data())
            print 'got image'



            #cv2.namedWindow('Depth', cv2.WINDOW_FULLSCREEN)
            #cv2.imshow('Depth', depth_image)
            #key = cv2.waitKey(0)

            #if key == 27:
                #print 'stop'
                #cv2.destroyAllWindows()
                #break

            xCoord = np.arange(0, 6, 1)
            yCoord = [0, 1, -3, 5, -3, 0]
            fig = plt.figure()
            ax = fig.add_subplot(111)

            markerprops = dict(marker='o', markersize=5, markeredgecolor='red')
            lineprops = dict(color='red', linewidth=2)
            plt.imshow(depth_image)
            ax.grid(True)
            figManager = plt.get_current_fig_manager().window.state('zoomed')

            ruler = Ruler(ax=ax,
                          depth_frame=depth_frame,
                          color_intrin=color_intrin,
                          useblit=True,
                          markerprops=markerprops,
                          lineprops=lineprops,
                          )

            plt.show()
            print 'show image'
            decision = raw_input('next move: \n')
            if decision == '+':
                continue
            elif decision == 'x':
                i = 100
                print 'stop'
                break
    question()

def question():

    x = raw_input('haben Sie noch bilder?(y/n) \n')
    #x= 'y'
    if str(x) == 'y':
        file_name = raw_input('filename: \n')
        return file_name

    elif str(x) == 'n':
            print 'exit'
            return
    else :
            print 'Falsche Antwort'

if __name__ == '__main__':
    in_file = question()
    measure(in_file)

